import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
import asyncio
from datetime import datetime
from io import StringIO, BytesIO
from typing import Optional, Union
import uuid

logger = logging.getLogger(__name__)

def replace_placeholders(text: Optional[str], interaction: discord.Interaction, ticket_id: Optional[str] = None) -> str:
    """Replace placeholder variables in text and handle newlines properly"""
    if not text:
        return ""
    
    replacements = {
        '{user.mention}': interaction.user.mention,
        '{user.name}': interaction.user.name,
        '{user.display_name}': interaction.user.display_name,
        '{guild.name}': interaction.guild.name if interaction.guild else 'Unknown Server',
        '{channel.name}': getattr(interaction.channel, 'name', 'Unknown Channel'),
        '{ticket.id}': ticket_id or 'Unknown',
        '{newline}': '\n',
        '\\\\n': '\n',  # Handle escaped newlines
        '\\n': '\n'     # Handle literal \n
    }
    
    result = text
    for placeholder, replacement in replacements.items():
        result = result.replace(placeholder, replacement)
    
    # Additional newline processing for better embed support
    # Convert common newline representations to actual newlines
    result = result.replace('\\n', '\n')  # \n literal
    result = result.replace('\\r\\n', '\n')  # Windows line endings
    result = result.replace('\\r', '\n')  # Mac line endings
    result = result.replace('\r\n', '\n')  # Normalize Windows endings
    result = result.replace('\r', '\n')   # Normalize Mac endings
    
    return result

class TicketPanelView(discord.ui.View):
    """Permanent panel buttons to open tickets"""
    def __init__(self, panels: list):
        super().__init__(timeout=None)  # Permanent view - never times out
        for panel in panels[:5]:
            button = TicketButton(panel['panel_id'], panel['title'])
            self.add_item(button)

class TicketButton(discord.ui.Button):
    """Permanent button to open a ticket"""
    def __init__(self, panel_id: str, title: str):
        # Use consistent custom_id format for persistence
        super().__init__(
            label="Open a Ticket",
            emoji='📄',
            style=discord.ButtonStyle.secondary,
            custom_id=f"nexguard_ticket_{panel_id}"  # Unique prefix for identification
        )
        self.panel_id = panel_id
        self.title = title

    async def callback(self, interaction: discord.Interaction):
        """Create ticket when button pressed"""
        try:
            # Immediate response to prevent timeout
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)
            
            if not interaction.guild:
                await interaction.followup.send("❌ This can only be used in a server.", ephemeral=True)
                return
            
            # Get panel configuration from database
            bot = interaction.client
            if not hasattr(bot, 'db_pool') or not getattr(bot, 'db_pool', None):
                await interaction.followup.send("❌ Database not available.", ephemeral=True)
                return
                
            async with getattr(bot, 'db_pool').acquire() as conn:
                panel = await conn.fetchrow("""
                    SELECT * FROM ticket_panels 
                    WHERE guild_id = $1 AND panel_id = $2
                """, str(interaction.guild.id), self.panel_id)
                
                if not panel:
                    await interaction.followup.send("❌ Panel configuration not found.", ephemeral=True)
                    return
            
            # Create ticket channel with {panel}-{username} format
            channel_name = f"{self.panel_id}-{interaction.user.name}".lower()
            channel_name = "".join(c for c in channel_name if c.isalnum() or c in '-_')[:50]
            
            # Get category if specified
            category = None
            if panel.get('category_id') and interaction.guild:
                category_channel = interaction.guild.get_channel(int(panel['category_id']))
                if isinstance(category_channel, discord.CategoryChannel):
                    category = category_channel
            
            overwrites = {}
            if interaction.guild:
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                # Add user permissions for Member type
                if isinstance(interaction.user, discord.Member):
                    overwrites[interaction.user] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            # Add support team permissions
            if panel.get('support_team_ids'):
                try:
                    team_ids = json.loads(panel['support_team_ids'])
                    for team_id in team_ids:
                        if team_id.startswith('role:') and interaction.guild:
                            role_id = team_id[5:]  # Remove 'role:' prefix
                            role = interaction.guild.get_role(int(role_id))
                            if role:
                                overwrites[role] = discord.PermissionOverwrite(
                                    read_messages=True, 
                                    send_messages=True,
                                    attach_files=True,
                                    embed_links=True,
                                    read_message_history=True
                                )
                        elif team_id.startswith('user:') and interaction.guild:
                            user_id = team_id[5:]  # Remove 'user:' prefix
                            user = interaction.guild.get_member(int(user_id))
                            if user:
                                overwrites[user] = discord.PermissionOverwrite(
                                    read_messages=True, 
                                    send_messages=True,
                                    attach_files=True,
                                    embed_links=True,
                                    read_message_history=True
                                )
                except Exception as e:
                    logger.error(f"Error setting support team permissions: {e}")
            
            if not interaction.guild:
                await interaction.followup.send("❌ This can only be used in a server.", ephemeral=True)
                return
                
            channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                reason=f"Ticket by {interaction.user}"
            )
            
            # Prepare role/user pings (permissions already set above)
            ping_content = ""
            if panel.get('support_team_ids'):
                try:
                    team_ids = json.loads(panel['support_team_ids'])
                    pings = []
                    for team_id in team_ids:
                        if team_id.startswith('role:') and interaction.guild:
                            role_id = team_id[5:]  # Remove 'role:' prefix
                            role = interaction.guild.get_role(int(role_id))
                            if role:
                                pings.append(role.mention)
                        elif team_id.startswith('user:') and interaction.guild:
                            user_id = team_id[5:]  # Remove 'user:' prefix
                            user = interaction.guild.get_member(int(user_id))
                            if user:
                                pings.append(user.mention)
                    if pings:
                        ping_content = " ".join(pings)
                except Exception as e:
                    logger.error(f"Error parsing support team pings: {e}")
            
            # Create ticket channel embed with separate customization and placeholder support
            embed = discord.Embed(color=0x5865F2)
            
            # Generate unique ticket ID for placeholders
            ticket_id = f"{panel['panel_id']}-{interaction.user.name.lower()}"
            
            # Set ticket embed header (author field) with placeholder replacement
            if panel.get('ticket_embed_header'):
                embed.set_author(name=replace_placeholders(panel['ticket_embed_header'], interaction, ticket_id))
            
            # Set ticket embed title with placeholder replacement
            if panel.get('ticket_embed_title'):
                embed.title = replace_placeholders(panel['ticket_embed_title'], interaction, ticket_id)
            else:
                embed.title = f"🎫 New Ticket"
            
            # Set ticket embed description with placeholder replacement
            if panel.get('ticket_embed_description'):
                embed.description = replace_placeholders(panel['ticket_embed_description'], interaction, ticket_id)
            else:
                embed.description = f"Hello {interaction.user.mention}! Please describe your issue and we'll help you."
            
            embed.set_footer(text="NexGuard |")
            
            # Send message with pings and embed
            control_view = TicketControlView(channel.name)
            # Register the control view as persistent
            interaction.client.add_view(control_view)
            
            if ping_content:
                await channel.send(content=ping_content, embed=embed, view=control_view)
            else:
                await channel.send(embed=embed, view=control_view)
            
            await interaction.followup.send(
                f"✅ Ticket created! Continue in {channel.mention}",
                ephemeral=True
            )
                
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Failed to create ticket.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Failed to create ticket.", ephemeral=True)
            except:
                pass

class TicketControlView(discord.ui.View):
    """Close and claim buttons - persistent across restarts"""
    def __init__(self, ticket_id: str):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
    
    @discord.ui.button(label="Close", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="nexguard_close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close ticket with transcript - accessible to all ticket participants"""
        try:
            # Basic server check only - anyone in the ticket channel can close it
            if not interaction.guild:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
                return
            
            modal = CloseTicketModal(self.ticket_id)
            if not interaction.response.is_done():
                await interaction.response.send_modal(modal)
            else:
                await interaction.followup.send("❌ Interaction expired. Please try again.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in close_ticket: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Failed to open close dialog. Please try again.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Failed to open close dialog. Please try again.", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(label="Claim", emoji="🙌", style=discord.ButtonStyle.primary, custom_id="nexguard_claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Claim ticket - staff action only"""
        try:
            # Check if user has manage messages permission for claiming
            if interaction.guild and isinstance(interaction.user, discord.Member):
                if not interaction.user.guild_permissions.manage_messages:
                    if not interaction.response.is_done():
                        await interaction.response.send_message("❌ You need Manage Messages permissions to claim tickets.", ephemeral=True)
                    return
            else:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
                return
            
            # Disable claim button
            self.claim_ticket.disabled = True
            self.claim_ticket.label = f"Claimed by {interaction.user.display_name}"
            
            if not interaction.response.is_done():
                await interaction.response.edit_message(view=self)
                await interaction.followup.send(f"🙌 Ticket claimed by {interaction.user.mention}")
            else:
                await interaction.followup.send("❌ Interaction expired. Please try again.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in claim_ticket: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Failed to claim ticket. Please try again.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Failed to claim ticket. Please try again.", ephemeral=True)
            except:
                pass

class CloseTicketModal(discord.ui.Modal):
    """Modal to close ticket"""
    def __init__(self, ticket_id: str):
        super().__init__(title="Close Ticket")
        self.ticket_id = ticket_id
        
        self.reason = discord.ui.TextInput(
            label="Reason (optional)",
            placeholder="Why is this ticket being closed?",
            required=False,
            max_length=1000,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.reason)
        
        self.delete_delay = discord.ui.TextInput(
            label="Delete channel in (seconds)",
            placeholder="Enter 0 for immediate deletion or 30 for default",
            required=False,
            default="5",
            max_length=3
        )
        self.add_item(self.delete_delay)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            
            # Parse deletion delay
            try:
                delay = int(self.delete_delay.value) if self.delete_delay.value else 5
                delay = max(0, min(300, delay))  # Between 0 and 300 seconds
            except:
                delay = 5
            
            # Generate transcript and get participants
            transcript_data, participants = await self.generate_transcript(interaction.channel)
            
            # Send closing message
            embed_desc = f"🔒 **Ticket Closed**\n\nClosed by {interaction.user.mention}"
            if self.reason.value:
                embed_desc += f"\n\n**Reason:** {self.reason.value}"
            
            if delay > 0:
                embed_desc += f"\n\n⏰ Channel will be deleted in {delay} seconds."
            else:
                embed_desc += f"\n\n⏰ Channel will be deleted immediately."
                
            embed = discord.Embed(description=embed_desc, color=0x5865F2)
            
            await interaction.followup.send(embed=embed)
            
            # Send transcript to all participants in background
            if participants and transcript_data:
                asyncio.create_task(self.send_transcripts_to_participants(interaction.client, participants, transcript_data))
            
            # Delete channel after delay
            if delay > 0:
                await asyncio.sleep(delay)
                
            try:
                if isinstance(interaction.channel, discord.TextChannel):
                    channel_name = interaction.channel.name
                    await interaction.channel.delete(reason=f"Ticket closed by {interaction.user.display_name}")
                    logger.info(f"Ticket channel '{channel_name}' deleted successfully")
            except Exception as delete_error:
                logger.error(f"Failed to delete ticket channel: {delete_error}")
                
        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
            try:
                await interaction.followup.send("❌ Failed to close ticket.", ephemeral=True)
            except:
                pass
    
    async def generate_transcript(self, channel):
        """Generate transcript and return participants"""
        try:
            messages = []
            participants = set()
            
            async for message in channel.history(limit=1000, oldest_first=True):
                if not message.author.bot or message.embeds:
                    messages.append({
                        'timestamp': message.created_at.isoformat(),
                        'author': message.author.display_name,
                        'content': message.content,
                        'attachments': [att.url for att in message.attachments]
                    })
                    
                    # Track human participants
                    if not message.author.bot:
                        participants.add(message.author.id)
            
            return json.dumps(messages, indent=2), participants
            
        except Exception as e:
            logger.error(f"Error generating transcript: {e}")
            return None, set()
    
    async def send_transcripts_to_participants(self, bot, participants: set, transcript_data: str):
        """Send transcript to all participants"""
        try:
            messages = json.loads(transcript_data)
            
            # Create readable transcript
            readable_transcript = f"# Ticket Transcript - {self.ticket_id}\n\n"
            for msg in messages:
                timestamp = datetime.fromisoformat(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S UTC")
                author = msg['author']
                content = msg['content']
                
                if content:
                    readable_transcript += f"[{timestamp}] {author}: {content}\n"
                
                if msg['attachments']:
                    for att in msg['attachments']:
                        readable_transcript += f"[{timestamp}] {author} uploaded: {att}\n"
            
            # Send to all participants
            for user_id in participants:
                try:
                    user = bot.get_user(user_id)
                    if user:
                        embed = discord.Embed(
                            title=f"📋 Ticket Transcript - {self.ticket_id}",
                            description="Complete transcript of your ticket conversation.",
                            color=0x5865F2
                        )
                        
                        # Send as file if too long
                        if len(readable_transcript) > 2000:
                            file = discord.File(
                                fp=BytesIO(readable_transcript.encode('utf-8')),
                                filename=f"ticket_{self.ticket_id}_transcript.txt"
                            )
                            await user.send(embed=embed, file=file)
                        else:
                            current_desc = embed.description or ""
                            embed.description = current_desc + f"\n\n```\n{readable_transcript[:1800]}\n```"
                            await user.send(embed=embed)
                            
                except Exception as e:
                    logger.warning(f"Could not send transcript to user {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending transcripts: {e}")

class TicketsCog(commands.Cog):
    """Revamped ticket system with custom embeds and pings"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ticket-panel", description="Create or manage a ticket panel")
    @app_commands.describe(
        action="Action to perform",
        panel_id="Unique ID for the panel",
        title="Panel title",
        category="Category for ticket channels",
        roles="Support roles to ping (mention them)",
        channel="Channel to deploy panel to (for deploy action)",
        panel_embed_header="Panel message embed header",
        panel_embed_title="Panel message embed title", 
        panel_embed_description="Panel message embed description",
        ticket_embed_header="Ticket channel embed header (supports {user.mention}, {user.name}, {guild.name}, \\n for new lines)",
        ticket_embed_title="Ticket channel embed title (supports {user.mention}, {user.name}, {guild.name}, \\n for new lines)",
        ticket_embed_description="Ticket channel embed description (supports {user.mention}, {user.name}, {guild.name}, \\n for new lines)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="create", value="create"),
        app_commands.Choice(name="edit", value="edit"),
        app_commands.Choice(name="deploy", value="deploy"),
        app_commands.Choice(name="list", value="list"),
        app_commands.Choice(name="delete", value="delete")
    ])
    async def ticket_panel(
        self, 
        interaction: discord.Interaction,
        action: str,
        panel_id: Optional[str] = None,
        title: Optional[str] = None,
        category: Optional[discord.CategoryChannel] = None,
        roles: Optional[str] = None,
        channel: Optional[discord.TextChannel] = None,
        panel_embed_header: Optional[str] = None,
        panel_embed_title: Optional[str] = None,
        panel_embed_description: Optional[str] = None,
        ticket_embed_header: Optional[str] = None,
        ticket_embed_title: Optional[str] = None,
        ticket_embed_description: Optional[str] = None
    ):
        """Manage ticket panels"""
        
        try:
            # Defer immediately to prevent timeouts
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)
        except discord.errors.NotFound:
            # Interaction already timed out
            return
        except Exception as e:
            logger.error(f"Error deferring interaction: {e}")
            return
        
        # Check permissions
        if interaction.guild and isinstance(interaction.user, discord.Member):
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.followup.send("❌ You need Manage Channels permissions to manage ticket panels.", ephemeral=True)
                return
        else:
            await interaction.followup.send("❌ This command can only be used in a server.", ephemeral=True)
            return
        
        if not hasattr(interaction.client, 'db_pool') or not getattr(interaction.client, 'db_pool', None):
            await interaction.followup.send("❌ Database not available.", ephemeral=True)
            return
        
        try:
            async with getattr(interaction.client, 'db_pool').acquire() as conn:
                if action == "create":
                    if not panel_id or not title:
                        await interaction.followup.send("❌ Panel ID and title are required for creation.", ephemeral=True)
                        return
                    
                    # Parse role mentions and user mentions
                    support_team_ids = []
                    if roles:
                        # Handle both @role mentions and @user mentions
                        import re
                        # Find all role mentions <@&123456789>
                        role_matches = re.findall(r'<@&(\d+)>', roles)
                        # Find all user mentions <@123456789>
                        user_matches = re.findall(r'<@!?(\d+)>', roles)
                        
                        # Store both with prefixes to distinguish
                        for role_id in role_matches:
                            support_team_ids.append(f"role:{role_id}")
                        for user_id in user_matches:
                            support_team_ids.append(f"user:{user_id}")
                    
                    # Insert panel with separate embed settings
                    await conn.execute("""
                        INSERT INTO ticket_panels (
                            guild_id, panel_id, title, category_id, support_team_ids,
                            panel_embed_header, panel_embed_title, panel_embed_description,
                            ticket_embed_header, ticket_embed_title, ticket_embed_description
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        ON CONFLICT (guild_id, panel_id) 
                        DO UPDATE SET 
                            title = $3,
                            category_id = $4,
                            support_team_ids = $5,
                            panel_embed_header = $6,
                            panel_embed_title = $7,
                            panel_embed_description = $8,
                            ticket_embed_header = $9,
                            ticket_embed_title = $10,
                            ticket_embed_description = $11
                    """, 
                        str(interaction.guild.id), panel_id, title,
                        str(category.id) if category else None,
                        json.dumps(support_team_ids) if support_team_ids else None,
                        panel_embed_header, panel_embed_title, panel_embed_description,
                        ticket_embed_header, ticket_embed_title, ticket_embed_description
                    )
                    
                    embed = discord.Embed(
                        title="✅ Ticket Panel Created",
                        description=f"Panel `{panel_id}` has been created with title: **{title}**",
                        color=0x00ff00
                    )
                    
                    if category:
                        embed.add_field(name="Category", value=category.mention, inline=True)
                    if support_team_ids:
                        mentions = []
                        for team_id in support_team_ids:
                            if team_id.startswith('role:'):
                                role_id = team_id[5:]
                                role = interaction.guild.get_role(int(role_id))
                                if role:
                                    mentions.append(role.mention)
                            elif team_id.startswith('user:'):
                                user_id = team_id[5:]
                                user = interaction.guild.get_member(int(user_id))
                                if user:
                                    mentions.append(user.mention)
                        if mentions:
                            embed.add_field(name="Support Team", value=" ".join(mentions), inline=True)
                    
                    await interaction.followup.send(embed=embed)
                
                elif action == "edit":
                    if not panel_id:
                        await interaction.followup.send("❌ Panel ID required for editing.", ephemeral=True)
                        return
                    
                    # Check if panel exists first
                    existing_panel = await conn.fetchrow("""
                        SELECT * FROM ticket_panels 
                        WHERE guild_id = $1 AND panel_id = $2
                    """, str(interaction.guild.id), panel_id)
                    
                    if not existing_panel:
                        await interaction.followup.send("❌ Panel not found. Use 'create' action to create a new panel.", ephemeral=True)
                        return
                    
                    # Parse role mentions and user mentions for editing
                    support_team_ids = []
                    if roles:
                        import re
                        role_matches = re.findall(r'<@&(\d+)>', roles)
                        user_matches = re.findall(r'<@!?(\d+)>', roles)
                        
                        for role_id in role_matches:
                            support_team_ids.append(f"role:{role_id}")
                        for user_id in user_matches:
                            support_team_ids.append(f"user:{user_id}")
                    
                    # Update only provided fields, keep existing values for others
                    update_title = title if title is not None else existing_panel['title']
                    update_category_id = str(category.id) if category is not None else existing_panel['category_id']
                    update_support_team_ids = json.dumps(support_team_ids) if roles is not None else existing_panel['support_team_ids']
                    update_panel_embed_header = panel_embed_header if panel_embed_header is not None else existing_panel['panel_embed_header']
                    update_panel_embed_title = panel_embed_title if panel_embed_title is not None else existing_panel['panel_embed_title']
                    update_panel_embed_description = panel_embed_description if panel_embed_description is not None else existing_panel['panel_embed_description']
                    update_ticket_embed_header = ticket_embed_header if ticket_embed_header is not None else existing_panel['ticket_embed_header']
                    update_ticket_embed_title = ticket_embed_title if ticket_embed_title is not None else existing_panel['ticket_embed_title']
                    update_ticket_embed_description = ticket_embed_description if ticket_embed_description is not None else existing_panel['ticket_embed_description']
                    
                    # Update the panel
                    await conn.execute("""
                        UPDATE ticket_panels SET 
                            title = $3,
                            category_id = $4,
                            support_team_ids = $5,
                            panel_embed_header = $6,
                            panel_embed_title = $7,
                            panel_embed_description = $8,
                            ticket_embed_header = $9,
                            ticket_embed_title = $10,
                            ticket_embed_description = $11
                        WHERE guild_id = $1 AND panel_id = $2
                    """, 
                        str(interaction.guild.id), panel_id,
                        update_title, update_category_id, update_support_team_ids,
                        update_panel_embed_header, update_panel_embed_title, update_panel_embed_description,
                        update_ticket_embed_header, update_ticket_embed_title, update_ticket_embed_description
                    )
                    
                    embed = discord.Embed(
                        title="✅ Ticket Panel Updated",
                        description=f"Panel `{panel_id}` has been successfully updated.",
                        color=0x00ff00
                    )
                    embed.add_field(name="Updated Title", value=update_title, inline=True)
                    
                    if category:
                        embed.add_field(name="Category", value=category.mention, inline=True)
                    if support_team_ids:
                        mentions = []
                        for team_id in support_team_ids:
                            if team_id.startswith('role:'):
                                role_id = team_id[5:]
                                role = interaction.guild.get_role(int(role_id))
                                if role:
                                    mentions.append(role.mention)
                            elif team_id.startswith('user:'):
                                user_id = team_id[5:]
                                user = interaction.guild.get_member(int(user_id))
                                if user:
                                    mentions.append(user.mention)
                        if mentions:
                            embed.add_field(name="Support Team", value=" ".join(mentions), inline=True)
                    
                    await interaction.followup.send(embed=embed)
                
                elif action == "deploy":
                    if not panel_id:
                        await interaction.followup.send("❌ Panel ID required for deployment.", ephemeral=True)
                        return
                    
                    # Get panel data
                    panel = await conn.fetchrow("""
                        SELECT * FROM ticket_panels 
                        WHERE guild_id = $1 AND panel_id = $2
                    """, str(interaction.guild.id), panel_id)
                    
                    if not panel:
                        await interaction.followup.send("❌ Panel not found.", ephemeral=True)
                        return
                    
                    # Create panel embed with separate customization
                    panel_embed = discord.Embed(color=0x5865F2)
                    
                    # Set panel embed header (author field) with placeholder replacement
                    if panel.get('panel_embed_header'):
                        panel_embed.set_author(name=replace_placeholders(panel['panel_embed_header'], interaction, panel['panel_id']))
                    
                    # Set panel embed title with placeholder replacement
                    if panel.get('panel_embed_title'):
                        panel_embed.title = replace_placeholders(panel['panel_embed_title'], interaction, panel['panel_id'])
                    else:
                        panel_embed.title = panel['title']
                    
                    # Set panel embed description with placeholder replacement
                    if panel.get('panel_embed_description'):
                        panel_embed.description = replace_placeholders(panel['panel_embed_description'], interaction, panel['panel_id'])
                    else:
                        panel_embed.description = "Click the button below to open a support ticket."
                    
                    panel_embed.set_footer(text="NexGuard |")
                    
                    # Create permanent panel view
                    panel_view = TicketPanelView([{
                        'panel_id': panel['panel_id'],
                        'title': panel['title']
                    }])
                    
                    # Register the view permanently with the bot
                    self.bot.add_view(panel_view)
                    
                    # Deploy to specified channel or current channel
                    if channel:
                        await channel.send(embed=panel_embed, view=panel_view)
                        await interaction.followup.send(f"✅ Permanent panel `{panel_id}` deployed to {channel.mention}", ephemeral=True)
                    else:
                        await interaction.followup.send(embed=panel_embed, view=panel_view)
                
                elif action == "list":
                    panels = await conn.fetch("""
                        SELECT * FROM ticket_panels 
                        WHERE guild_id = $1
                        ORDER BY created_at DESC
                    """, str(interaction.guild.id))
                    
                    if not panels:
                        await interaction.followup.send("❌ No ticket panels found.", ephemeral=True)
                        return
                    
                    embed = discord.Embed(
                        title="📋 Ticket Panels",
                        description=f"Found {len(panels)} panel(s)",
                        color=0x5865F2
                    )
                    
                    for panel in panels[:10]:  # Limit to 10 for embed limits
                        value = f"**Title:** {panel['title']}\n"
                        if panel['category_id']:
                            category = interaction.guild.get_channel(int(panel['category_id']))
                            value += f"**Category:** {category.mention if category else 'Deleted'}\n"
                        
                        embed.add_field(
                            name=f"Panel: {panel['panel_id']}",
                            value=value,
                            inline=True
                        )
                    
                    await interaction.followup.send(embed=embed, ephemeral=True)
                
                elif action == "delete":
                    if not panel_id:
                        await interaction.followup.send("❌ Panel ID required for deletion.", ephemeral=True)
                        return
                    
                    # Check if panel exists
                    panel = await conn.fetchrow("""
                        SELECT * FROM ticket_panels 
                        WHERE guild_id = $1 AND panel_id = $2
                    """, str(interaction.guild.id), panel_id)
                    
                    if not panel:
                        await interaction.followup.send("❌ Panel not found.", ephemeral=True)
                        return
                    
                    # Delete the panel
                    await conn.execute("""
                        DELETE FROM ticket_panels 
                        WHERE guild_id = $1 AND panel_id = $2
                    """, str(interaction.guild.id), panel_id)
                    
                    embed = discord.Embed(
                        title="🗑️ Panel Deleted",
                        description=f"Panel `{panel_id}` has been successfully deleted.",
                        color=0xff0000
                    )
                    embed.add_field(name="Panel Title", value=panel['title'], inline=True)
                    
                    await interaction.followup.send(embed=embed)
                
                else:
                    await interaction.followup.send("❌ Invalid action.", ephemeral=True)
                    
        except discord.errors.NotFound:
            # Interaction already expired
            logger.warning("Ticket panel interaction expired")
            return
        except Exception as e:
            logger.error(f"Error managing ticket panel: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Failed to manage ticket panel.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Failed to manage ticket panel.", ephemeral=True)
            except:
                pass
    

    @commands.Cog.listener()
    async def on_ready(self):
        """Register persistent views and ensure ticket tables"""
        try:
            await self.ensure_ticket_tables()
            await self.restore_persistent_views()
            await self.restore_control_views()
            logger.info("Revamped ticket system initialized")
        except Exception as e:
            logger.error(f"Error initializing tickets: {e}")
    
    async def restore_persistent_views(self):
        """Restore all permanent persistent views from database"""
        if not hasattr(self.bot, 'db_pool') or not self.bot.db_pool:
            return
            
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Get all deployed panels from all guilds
                panels = await conn.fetch("""
                    SELECT DISTINCT panel_id, title, guild_id 
                    FROM ticket_panels
                """)
                
                # Group panels by guild for organized view registration
                guild_panels = {}
                for panel in panels:
                    guild_id = panel['guild_id']
                    if guild_id not in guild_panels:
                        guild_panels[guild_id] = []
                    guild_panels[guild_id].append({
                        'panel_id': panel['panel_id'],
                        'title': panel['title']
                    })
                
                # Register permanent views for each unique panel combination
                total_views = 0
                for guild_id, guild_panel_list in guild_panels.items():
                    # Create view for each individual panel (for unique interactions)
                    for panel in guild_panel_list:
                        panel_view = TicketPanelView([panel])
                        self.bot.add_view(panel_view)
                        total_views += 1
                
                # Control views will be restored separately for individual ticket channels
                
                logger.info(f"Restored {total_views} permanent ticket panel views across {len(guild_panels)} guilds")
                
        except Exception as e:
            logger.error(f"Error restoring persistent views: {e}")
    
    async def restore_control_views(self):
        """Restore control views for existing ticket channels on startup"""
        try:
            restored_count = 0
            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    # Check if this looks like a ticket channel with dash format or common prefixes
                    if ('-' in channel.name and 
                        (channel.name.count('-') == 1 or  # panel-username format
                         channel.name.startswith(tuple(["support-", "billing-", "general-", "admin-", "technical-", "lspdapplication-", "civapplication-"])))):
                        
                        # Check if channel has recent messages with NexGuard ticket control buttons
                        try:
                            async for message in channel.history(limit=20):
                                if (message.author == self.bot.user and 
                                    message.components):
                                    # Check for NexGuard-specific button custom IDs
                                    for action_row in message.components:
                                        for component in action_row.children:
                                            if hasattr(component, 'custom_id') and component.custom_id in ['nexguard_close_ticket', 'nexguard_claim_ticket']:
                                                # This is a ticket channel with our control buttons
                                                control_view = TicketControlView(channel.name)
                                                self.bot.add_view(control_view)
                                                restored_count += 1
                                                break
                                        else:
                                            continue
                                        break
                                    else:
                                        continue
                                    break
                        except Exception as e:
                            logger.warning(f"Could not check channel {channel.name}: {e}")
                            continue
            
            if restored_count > 0:
                logger.info(f"Restored {restored_count} ticket control views")
            
        except Exception as e:
            logger.error(f"Error restoring control views: {e}")
    
    @app_commands.command(name="close", description="Close a ticket")
    @app_commands.describe(
        reason="Reason for closing the ticket"
    )
    async def close_ticket(self, interaction: discord.Interaction, reason: str = "No reason provided"):
        """Close the current ticket"""
        await interaction.response.defer()
        
        try:
            if not interaction.guild:
                await interaction.followup.send("❌ This command can only be used in a server.", ephemeral=True)
                return
            
            if not isinstance(interaction.channel, discord.TextChannel):
                await interaction.followup.send("❌ This command can only be used in text channels.", ephemeral=True)
                return
                
            # Enhanced ticket channel detection - very flexible approach
            channel_name = interaction.channel.name
            is_ticket_channel = False
            
            # Primary detection: Check for any dash pattern (most tickets use panel-username format)
            if "-" in channel_name:
                is_ticket_channel = True
            
            # Secondary detection: Known ticket prefixes
            if not is_ticket_channel:
                ticket_prefixes = ["support-", "billing-", "general-", "admin-", "technical-", "lspdapplication-", "ticket-", "help-"]
                if any(channel_name.startswith(prefix) for prefix in ticket_prefixes):
                    is_ticket_channel = True
            
            # Tertiary detection: "ticket" in name
            if not is_ticket_channel and "ticket" in channel_name.lower():
                is_ticket_channel = True
            
            # Final fallback: Check for NexGuard ticket control buttons in recent messages
            if not is_ticket_channel:
                try:
                    async for message in interaction.channel.history(limit=30):
                        if (message.author == interaction.client.user and 
                            message.components):
                            # Look for NexGuard-specific button IDs
                            message_content = str(message.components)
                            if ("nexguard_close_ticket" in message_content or 
                                "nexguard_claim_ticket" in message_content or
                                ("Close" in message_content and "Claim" in message_content)):
                                is_ticket_channel = True
                                break
                except:
                    pass
            
            # If still not detected, be more permissive - allow in any channel with "ticket" context
            if not is_ticket_channel:
                try:
                    # Check channel topic or pins for ticket-related content
                    if (interaction.channel.topic and 
                        any(word in interaction.channel.topic.lower() for word in ["ticket", "support", "help"])):
                        is_ticket_channel = True
                except:
                    pass
            
            if not is_ticket_channel:
                await interaction.followup.send("❌ This command can only be used in ticket channels.", ephemeral=True)
                return
            
            # Anyone in the ticket channel can close it - no permission check needed
            
            # Create transcript
            transcript = StringIO()
            transcript.write(f"Ticket Transcript - {channel_name}\n")
            transcript.write(f"Closed by: {interaction.user} ({interaction.user.id})\n")
            transcript.write(f"Closed at: {datetime.now()}\n")
            transcript.write(f"Reason: {reason}\n")
            transcript.write("-" * 50 + "\n\n")
            
            # Get recent messages for transcript
            messages = [message async for message in interaction.channel.history(limit=100)]
            messages.reverse()
            
            for message in messages:
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                author = f"{message.author} ({message.author.id})"
                content = message.content or "[No text content]"
                transcript.write(f"[{timestamp}] {author}: {content}\n")
                
                # Include attachments
                if message.attachments:
                    for attachment in message.attachments:
                        transcript.write(f"    📎 Attachment: {attachment.filename} ({attachment.url})\n")
            
            transcript.seek(0)
            transcript_bytes = BytesIO(transcript.getvalue().encode('utf-8'))
            transcript_file = discord.File(transcript_bytes, filename=f"transcript-{channel_name}.txt")
            
            # Update database
            if hasattr(self.bot, 'db_pool') and getattr(self.bot, 'db_pool', None):
                async with self.bot.db_pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE tickets 
                        SET status = 'closed', closed_by = $1, closed_at = NOW(), close_reason = $2
                        WHERE channel_id = $3 AND status = 'open'
                    """, str(interaction.user.id), reason, str(interaction.channel.id))
            
            # Create close embed
            close_embed = discord.Embed(
                title="🔒 Ticket Closed",
                description=f"This ticket has been closed by {interaction.user.mention}",
                color=0xff0000
            )
            close_embed.add_field(name="Reason", value=reason, inline=False)
            close_embed.add_field(name="Closed by", value=f"{interaction.user} ({interaction.user.id})", inline=True)
            close_embed.add_field(name="Closed at", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
            close_embed.set_footer(text="Transcript will be sent to participants")
            
            await interaction.followup.send(embed=close_embed)
            
            # Send transcript to all participants via DM
            try:
                participants = set()
                
                # Find all human participants 
                async for message in interaction.channel.history(limit=1000):
                    if not message.author.bot:
                        participants.add(message.author.id)
                
                # Send transcript file to each participant via DM
                for user_id in participants:
                    try:
                        user = interaction.client.get_user(user_id)
                        if user:
                            transcript.seek(0)
                            user_transcript_bytes = BytesIO(transcript.getvalue().encode('utf-8'))
                            user_transcript = discord.File(user_transcript_bytes, filename=f"transcript-{channel_name}.txt")
                            
                            embed = discord.Embed(
                                title=f"📋 Ticket Transcript - {channel_name}",
                                description="Complete transcript of your ticket conversation.",
                                color=0x5865F2
                            )
                            
                            await user.send(embed=embed, file=user_transcript)
                    except Exception as e:
                        logger.warning(f"Could not send transcript to user {user_id}: {e}")
                        
            except Exception as e:
                logger.error(f"Error sending transcripts via DM: {e}")
            
            # Delete channel after delay
            await asyncio.sleep(5)
            await interaction.channel.send("🗑️ This channel will be deleted in 5 seconds...")
            await asyncio.sleep(5)
            await interaction.channel.delete()
            
        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
            await interaction.followup.send("❌ Failed to close ticket.", ephemeral=True)

    @app_commands.command(name="close-request", description="Request ticket closure (for ticket owners)")
    @app_commands.describe(
        reason="Reason for requesting closure"
    )
    async def close_request(self, interaction: discord.Interaction, reason: str = "Issue resolved"):
        """Request ticket closure from staff"""
        await interaction.response.defer()
        
        try:
            if not interaction.guild:
                await interaction.followup.send("❌ This command can only be used in a server.", ephemeral=True)
                return
            
            if not isinstance(interaction.channel, discord.TextChannel):
                await interaction.followup.send("❌ This command can only be used in text channels.", ephemeral=True)
                return
                
            # Enhanced ticket channel detection - very flexible approach
            channel_name = interaction.channel.name
            is_ticket_channel = False
            
            # Primary detection: Check for any dash pattern (most tickets use panel-username format)
            if "-" in channel_name:
                is_ticket_channel = True
            
            # Secondary detection: Known ticket prefixes
            if not is_ticket_channel:
                ticket_prefixes = ["support-", "billing-", "general-", "admin-", "technical-", "lspdapplication-", "ticket-", "help-"]
                if any(channel_name.startswith(prefix) for prefix in ticket_prefixes):
                    is_ticket_channel = True
            
            # Tertiary detection: "ticket" in name
            if not is_ticket_channel and "ticket" in channel_name.lower():
                is_ticket_channel = True
            
            # Final fallback: Check for NexGuard ticket control buttons in recent messages
            if not is_ticket_channel:
                try:
                    async for message in interaction.channel.history(limit=30):
                        if (message.author == interaction.client.user and 
                            message.components):
                            # Look for NexGuard-specific button IDs
                            message_content = str(message.components)
                            if ("nexguard_close_ticket" in message_content or 
                                "nexguard_claim_ticket" in message_content or
                                ("Close" in message_content and "Claim" in message_content)):
                                is_ticket_channel = True
                                break
                except:
                    pass
            
            # If still not detected, be more permissive - allow in any channel with "ticket" context
            if not is_ticket_channel:
                try:
                    # Check channel topic or pins for ticket-related content
                    if (interaction.channel.topic and 
                        any(word in interaction.channel.topic.lower() for word in ["ticket", "support", "help"])):
                        is_ticket_channel = True
                except:
                    pass
            
            if not is_ticket_channel:
                await interaction.followup.send("❌ This command can only be used in ticket channels. If this is a ticket channel, ask staff to use `/close` instead.", ephemeral=True)
                return
            
            # Create close request embed
            request_embed = discord.Embed(
                title="🔄 Ticket Closure Requested",
                description=f"{interaction.user.mention} has requested this ticket to be closed.",
                color=0xffa500
            )
            request_embed.add_field(name="Reason", value=reason, inline=False)
            request_embed.add_field(name="Request Type", value="New Ticket Panel", inline=True)
            request_embed.add_field(name="Requested at", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
            request_embed.set_footer(text="Staff can use /close to close this ticket")
            
            # Create approval buttons for staff
            class CloseRequestView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=3600)  # 1 hour timeout
                
                @discord.ui.button(label="Approve & Close", style=discord.ButtonStyle.red, emoji="✅")
                async def approve_close(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                    # Allow anyone to close the ticket (matching the /close command behavior)
                    await button_interaction.response.defer()
                    
                    try:
                        # Create transcript
                        transcript = StringIO()
                        if not isinstance(button_interaction.channel, discord.TextChannel):
                            await button_interaction.followup.send("❌ Cannot generate transcript for this channel type.", ephemeral=True)
                            return
                        channel_name = button_interaction.channel.name
                        transcript.write(f"Ticket Transcript - {channel_name}\n")
                        transcript.write(f"Closed by: {button_interaction.user} ({button_interaction.user.id})\n")
                        transcript.write(f"Closed at: {datetime.now()}\n")
                        transcript.write(f"Reason: Ticket closure request approved\n")
                        transcript.write("-" * 50 + "\n\n")
                        
                        # Get recent messages for transcript
                        messages = [message async for message in button_interaction.channel.history(limit=100)]
                        messages.reverse()
                        
                        for message in messages:
                            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                            author = f"{message.author} ({message.author.id})"
                            content = message.content or "[No text content]"
                            transcript.write(f"[{timestamp}] {author}: {content}\n")
                            
                            # Include attachments
                            if message.attachments:
                                for attachment in message.attachments:
                                    transcript.write(f"    📎 Attachment: {attachment.filename} ({attachment.url})\n")
                        
                        transcript.seek(0)
                        transcript_bytes = BytesIO(transcript.getvalue().encode('utf-8'))
                        transcript_file = discord.File(transcript_bytes, filename=f"transcript-{channel_name}.txt")
                        
                        # Update database if available
                        bot = button_interaction.client
                        if hasattr(bot, 'db_pool') and getattr(bot, 'db_pool', None):
                            async with bot.db_pool.acquire() as conn:
                                await conn.execute("""
                                    UPDATE tickets 
                                    SET status = 'closed', closed_by = $1, closed_at = NOW(), close_reason = $2
                                    WHERE channel_id = $3 AND status = 'open'
                                """, str(button_interaction.user.id), "Ticket closure request approved", str(button_interaction.channel.id))
                        
                        # Create close embed
                        close_embed = discord.Embed(
                            title="🔒 Ticket Closed",
                            description=f"✅ Ticket closure approved and closed by {button_interaction.user.mention}",
                            color=0xff0000
                        )
                        close_embed.add_field(name="Reason", value="Ticket closure request approved", inline=False)
                        close_embed.add_field(name="Closed by", value=f"{button_interaction.user} ({button_interaction.user.id})", inline=True)
                        close_embed.add_field(name="Closed at", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
                        close_embed.set_footer(text="Transcript will be sent to participants")
                        
                        await button_interaction.followup.send(embed=close_embed)
                        
                        # Send transcript to all participants via DM
                        try:
                            participants = set()
                            
                            # Find all human participants 
                            if isinstance(button_interaction.channel, discord.TextChannel):
                                async for message in button_interaction.channel.history(limit=1000):
                                    if not message.author.bot:
                                        participants.add(message.author.id)
                            
                            # Send transcript file to each participant via DM
                            for user_id in participants:
                                try:
                                    user = button_interaction.client.get_user(user_id)
                                    if user:
                                        transcript.seek(0)
                                        user_transcript_bytes = BytesIO(transcript.getvalue().encode('utf-8'))
                                        user_transcript = discord.File(user_transcript_bytes, filename=f"transcript-{channel_name}.txt")
                                        
                                        embed = discord.Embed(
                                            title=f"📋 Ticket Transcript - {channel_name}",
                                            description="Complete transcript of your ticket conversation.",
                                            color=0x5865F2
                                        )
                                        
                                        await user.send(embed=embed, file=user_transcript)
                                except Exception as e:
                                    logger.warning(f"Could not send transcript to user {user_id}: {e}")
                                    
                        except Exception as e:
                            logger.error(f"Error sending transcripts via DM: {e}")
                        
                        # Delete channel after delay
                        if isinstance(button_interaction.channel, discord.TextChannel):
                            await button_interaction.channel.send("🗑️ This channel will be deleted in 10 seconds...")
                            await asyncio.sleep(10)
                            await button_interaction.channel.delete()
                        
                    except Exception as e:
                        logger.error(f"Error approving and closing ticket: {e}")
                        await button_interaction.followup.send("❌ Failed to close ticket.", ephemeral=True)
                    
                @discord.ui.button(label="Deny Request", style=discord.ButtonStyle.gray, emoji="❌")
                async def deny_close(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                    if isinstance(button_interaction.user, discord.Member):
                        has_permission = (button_interaction.user.guild_permissions.manage_messages or 
                                       any(role.name.lower() in ['support', 'staff', 'moderator', 'admin'] for role in button_interaction.user.roles))
                    else:
                        has_permission = False
                        
                    if not has_permission:
                        await button_interaction.response.send_message("❌ You don't have permission to manage tickets.", ephemeral=True)
                        return
                    
                    await button_interaction.response.send_message(f"❌ Ticket closure request denied by {button_interaction.user.mention}")
                    self.clear_items()
                    await button_interaction.edit_original_response(view=self)
            
            # Ping support roles
            support_mentions = []
            for role in interaction.guild.roles:
                if role.name.lower() in ['support', 'staff', 'moderator', 'admin']:
                    support_mentions.append(role.mention)
            
            mention_text = " ".join(support_mentions) if support_mentions else "@here"
            
            await interaction.followup.send(f"{mention_text}", embed=request_embed, view=CloseRequestView())
            
        except Exception as e:
            logger.error(f"Error requesting ticket closure: {e}")
            await interaction.followup.send("❌ Failed to request ticket closure.", ephemeral=True)

    @app_commands.command(name="add", description="Add a user to the current ticket")
    @app_commands.describe(
        user="User to add to the ticket"
    )
    async def add_user(self, interaction: discord.Interaction, user: discord.Member):
        """Add a user to the current ticket channel"""
        await interaction.response.defer()
        
        try:
            if not interaction.guild:
                await interaction.followup.send("❌ This command can only be used in a server.", ephemeral=True)
                return
            
            if not isinstance(interaction.channel, discord.TextChannel):
                await interaction.followup.send("❌ This command can only be used in text channels.", ephemeral=True)
                return
                
            # Enhanced ticket channel detection - very flexible approach
            channel_name = interaction.channel.name
            is_ticket_channel = False
            
            # Primary detection: Check for any dash pattern (most tickets use panel-username format)
            if "-" in channel_name:
                is_ticket_channel = True
            
            # Secondary detection: Known ticket prefixes
            if not is_ticket_channel:
                ticket_prefixes = ["support-", "billing-", "general-", "admin-", "technical-", "lspdapplication-", "ticket-", "help-"]
                if any(channel_name.startswith(prefix) for prefix in ticket_prefixes):
                    is_ticket_channel = True
            
            # Tertiary detection: "ticket" in name
            if not is_ticket_channel and "ticket" in channel_name.lower():
                is_ticket_channel = True
            
            # Final fallback: Check for NexGuard ticket control buttons in recent messages
            if not is_ticket_channel:
                try:
                    async for message in interaction.channel.history(limit=30):
                        if (message.author == interaction.client.user and 
                            message.components):
                            # Look for NexGuard-specific button IDs
                            message_content = str(message.components)
                            if ("nexguard_close_ticket" in message_content or 
                                "nexguard_claim_ticket" in message_content or
                                ("Close" in message_content and "Claim" in message_content)):
                                is_ticket_channel = True
                                break
                except:
                    pass
            
            # If still not detected, be more permissive - allow in any channel with "ticket" context
            if not is_ticket_channel:
                try:
                    # Check channel topic or pins for ticket-related content
                    if (interaction.channel.topic and 
                        any(word in interaction.channel.topic.lower() for word in ["ticket", "support", "help"])):
                        is_ticket_channel = True
                except:
                    pass
            
            if not is_ticket_channel:
                await interaction.followup.send("❌ This command can only be used in ticket channels.", ephemeral=True)
                return
            
            # Check permissions
            if isinstance(interaction.user, discord.Member):
                has_permission = (interaction.user.guild_permissions.manage_messages or 
                               any(role.name.lower() in ['support', 'staff', 'moderator', 'admin'] for role in interaction.user.roles))
            else:
                has_permission = False
                
            if not has_permission:
                await interaction.followup.send("❌ You don't have permission to add users to tickets.", ephemeral=True)
                return
            
            # Check if user is already in the channel
            if user in interaction.channel.members:
                await interaction.followup.send(f"❌ {user.mention} is already in this ticket.", ephemeral=True)
                return
            
            # Add permissions for the user
            overwrites = {
                user: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                )
            }
            
            await interaction.channel.edit(overwrites={**interaction.channel.overwrites, **overwrites})
            
            # Create notification embed
            add_embed = discord.Embed(
                title="✅ User Added to Ticket",
                description=f"{user.mention} has been added to this ticket.",
                color=0x00ff00
            )
            add_embed.add_field(name="Added User", value=f"{user} ({user.id})", inline=True)
            add_embed.add_field(name="Added at", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
            
            await interaction.followup.send(embed=add_embed)
            
            # Welcome message for the added user
            welcome_embed = discord.Embed(
                title="🎫 Welcome to the Ticket",
                description=f"Hello {user.mention}! You have been added to this support ticket.",
                color=0x5865F2
            )
            welcome_embed.add_field(
                name="What you can do:", 
                value="• View the conversation history\n• Send messages and attachments\n• Provide additional information\n• Collaborate on resolving the issue", 
                inline=False
            )
            welcome_embed.set_footer(text="Use /close-request if you want to request ticket closure")
            
            await interaction.channel.send(f"{user.mention}", embed=welcome_embed)
            
        except Exception as e:
            logger.error(f"Error adding user to ticket: {e}")
            await interaction.followup.send("❌ Failed to add user to ticket.", ephemeral=True)

    @app_commands.command(name="rename", description="Rename the current ticket channel")
    @app_commands.describe(
        new_name="New name for the ticket channel (without spaces or special characters)"
    )
    async def rename_ticket(self, interaction: discord.Interaction, new_name: str):
        """Rename the current ticket channel"""
        await interaction.response.defer()
        
        try:
            if not interaction.guild:
                await interaction.followup.send("❌ This command can only be used in a server.", ephemeral=True)
                return
            
            # Enhanced ticket channel detection - very flexible approach
            channel_name = interaction.channel.name
            is_ticket_channel = False
            
            # Primary detection: Check for any dash pattern (most tickets use panel-username format)
            if "-" in channel_name:
                is_ticket_channel = True
            
            # Secondary detection: Known ticket prefixes
            if not is_ticket_channel:
                ticket_prefixes = ["support-", "billing-", "general-", "admin-", "technical-", "lspdapplication-", "ticket-", "help-"]
                if any(channel_name.startswith(prefix) for prefix in ticket_prefixes):
                    is_ticket_channel = True
            
            # Tertiary detection: "ticket" in name
            if not is_ticket_channel and "ticket" in channel_name.lower():
                is_ticket_channel = True
            
            # Final fallback: Check for NexGuard ticket control buttons in recent messages
            if not is_ticket_channel:
                try:
                    async for message in interaction.channel.history(limit=30):
                        if (message.author == interaction.client.user and 
                            message.components):
                            # Look for NexGuard-specific button IDs
                            message_content = str(message.components)
                            if ("nexguard_close_ticket" in message_content or 
                                "nexguard_claim_ticket" in message_content or
                                ("Close" in message_content and "Claim" in message_content)):
                                is_ticket_channel = True
                                break
                except:
                    pass
            
            # If still not detected, be more permissive - allow in any channel with "ticket" context
            if not is_ticket_channel:
                try:
                    # Check channel topic or pins for ticket-related content
                    if (interaction.channel.topic and 
                        any(word in interaction.channel.topic.lower() for word in ["ticket", "support", "help"])):
                        is_ticket_channel = True
                except:
                    pass
            
            if not is_ticket_channel:
                await interaction.followup.send("❌ This command can only be used in ticket channels.", ephemeral=True)
                return
            
            # Check permissions - staff or ticket creator can rename
            has_permission = False
            
            # Staff permissions
            if (interaction.user.guild_permissions.manage_messages or 
                any(role.name.lower() in ['support', 'staff', 'moderator', 'admin'] for role in interaction.user.roles)):
                has_permission = True
            
            # Check if user is the ticket creator (from channel name pattern)
            if not has_permission and "-" in channel_name:
                try:
                    username_part = channel_name.split("-", 1)[1]
                    if (interaction.user.name.lower() == username_part.lower() or 
                        interaction.user.display_name.lower() == username_part.lower()):
                        has_permission = True
                except:
                    pass
            
            if not has_permission:
                await interaction.followup.send("❌ You don't have permission to rename this ticket. Only staff or the ticket creator can rename tickets.", ephemeral=True)
                return
            
            # Validate new name
            new_name = new_name.lower().strip()
            
            # Remove invalid characters
            import re
            new_name = re.sub(r'[^a-z0-9\-]', '', new_name)
            
            if not new_name:
                await interaction.followup.send("❌ Invalid channel name. Please use only letters, numbers, and hyphens.", ephemeral=True)
                return
            
            if len(new_name) > 100:
                await interaction.followup.send("❌ Channel name is too long. Please use 100 characters or less.", ephemeral=True)
                return
            
            # Preserve format if it exists (panel-username becomes panel-newname)
            old_name = channel_name
            final_name = new_name
            
            # If current name has a dash pattern, try to preserve the prefix
            if "-" in old_name:
                parts = old_name.split("-", 1)
                if len(parts) == 2:
                    prefix = parts[0]
                    # Check if it's a known ticket prefix
                    ticket_prefixes = ["support", "billing", "general", "admin", "technical", "lspdapplication", "ticket", "help"]
                    if prefix in ticket_prefixes:
                        final_name = f"{prefix}-{new_name}"
            
            # Check if name already exists
            existing_channels = [channel.name for channel in interaction.guild.channels]
            if final_name in existing_channels:
                await interaction.followup.send(f"❌ A channel named `{final_name}` already exists. Please choose a different name.", ephemeral=True)
                return
            
            # Rename the channel
            try:
                await interaction.channel.edit(name=final_name)
                
                # Log the rename action
                rename_embed = discord.Embed(
                    title="📝 Ticket Renamed",
                    description=f"Ticket channel has been renamed by {interaction.user.mention}",
                    color=0x00ff00
                )
                rename_embed.add_field(name="Old Name", value=f"`{old_name}`", inline=True)
                rename_embed.add_field(name="New Name", value=f"`{final_name}`", inline=True)
                rename_embed.add_field(name="Renamed by", value=f"{interaction.user} ({interaction.user.id})", inline=False)
                rename_embed.timestamp = datetime.now()
                
                await interaction.followup.send(embed=rename_embed)
                
            except discord.Forbidden:
                await interaction.followup.send("❌ I don't have permission to rename this channel.", ephemeral=True)
            except discord.HTTPException as e:
                await interaction.followup.send(f"❌ Failed to rename channel: {str(e)}", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error renaming ticket: {e}")
            await interaction.followup.send("❌ Failed to rename ticket.", ephemeral=True)

    async def ensure_ticket_tables(self):
        """Ensure ticket database tables exist"""
        if not hasattr(self.bot, 'db_pool') or not self.bot.db_pool:
            return
            
        try:
            async with self.bot.db_pool.acquire() as conn:
                # First, ensure the basic table exists
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS ticket_panels (
                        id SERIAL PRIMARY KEY,
                        guild_id TEXT NOT NULL,
                        panel_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        category_id TEXT,
                        support_team_ids TEXT,
                        created_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(guild_id, panel_id)
                    )
                """)
                
                # Add new embed columns if they don't exist
                try:
                    await conn.execute("ALTER TABLE ticket_panels ADD COLUMN IF NOT EXISTS panel_embed_header TEXT")
                    await conn.execute("ALTER TABLE ticket_panels ADD COLUMN IF NOT EXISTS panel_embed_title TEXT")
                    await conn.execute("ALTER TABLE ticket_panels ADD COLUMN IF NOT EXISTS panel_embed_description TEXT")
                    await conn.execute("ALTER TABLE ticket_panels ADD COLUMN IF NOT EXISTS ticket_embed_header TEXT")
                    await conn.execute("ALTER TABLE ticket_panels ADD COLUMN IF NOT EXISTS ticket_embed_title TEXT")
                    await conn.execute("ALTER TABLE ticket_panels ADD COLUMN IF NOT EXISTS ticket_embed_description TEXT")
                except Exception as e:
                    logger.warning(f"Could not add embed columns (they may already exist): {e}")
                
                # Ensure tickets table exists
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS tickets (
                        id SERIAL PRIMARY KEY,
                        ticket_id TEXT NOT NULL,
                        guild_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        channel_id TEXT,
                        panel_id TEXT,
                        subject TEXT,
                        status TEXT DEFAULT 'open',
                        priority TEXT DEFAULT 'normal',
                        claimed_by TEXT,
                        claimed_at TIMESTAMP,
                        closed_by TEXT,
                        closed_at TIMESTAMP,
                        close_reason TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                logger.info("Ticket tables ensured")
        except Exception as e:
            logger.error(f"Error ensuring ticket tables: {e}")
    
    async def restore_control_views(self):
        """Restore control views for existing ticket channels on startup"""
        await self.bot.wait_until_ready()
        
        try:
            restored_count = 0
            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    # Check if this looks like a ticket channel
                    if (channel.name.startswith(tuple(["support-", "billing-", "general-", "admin-", "technical-"])) or 
                        "ticket" in channel.name.lower()):
                        
                        # Check if channel has recent messages with ticket control buttons
                        try:
                            async for message in channel.history(limit=10):
                                if (message.author == self.bot.user and 
                                    message.components and 
                                    any("Close" in str(component) for component in message.components)):
                                    
                                    # Register a new control view for this ticket
                                    control_view = TicketControlView(channel.name)
                                    self.bot.add_view(control_view)
                                    restored_count += 1
                                    break
                        except Exception as e:
                            logger.warning(f"Could not check channel {channel.name}: {e}")
                            continue
            
            if restored_count > 0:
                logger.info(f"Restored {restored_count} ticket control views")
            
        except Exception as e:
            logger.error(f"Error restoring control views: {e}")

async def setup(bot):
    await bot.add_cog(TicketsCog(bot))