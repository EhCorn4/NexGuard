import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
import asyncio
from datetime import datetime
from io import StringIO

logger = logging.getLogger(__name__)

def replace_placeholders(text: str, interaction: discord.Interaction) -> str:
    """Replace placeholder variables in text"""
    if not text:
        return text
    
    replacements = {
        '{user.mention}': interaction.user.mention,
        '{user.name}': interaction.user.name,
        '{user.display_name}': interaction.user.display_name,
        '{guild.name}': interaction.guild.name if interaction.guild else 'Unknown Server',
        '{channel.name}': interaction.channel.name if hasattr(interaction.channel, 'name') else 'Unknown Channel',
        '{newline}': '\n',
        '\\n': '\n'
    }
    
    result = text
    for placeholder, replacement in replacements.items():
        result = result.replace(placeholder, replacement)
    
    return result

class TicketPanelView(discord.ui.View):
    """Panel buttons to open tickets"""
    def __init__(self, panels: list):
        super().__init__(timeout=None)
        for panel in panels[:5]:
            button = TicketButton(panel['panel_id'], panel['title'])
            self.add_item(button)

class TicketButton(discord.ui.Button):
    """Button to open a ticket"""
    def __init__(self, panel_id: str, title: str):
        super().__init__(
            label="Open a Ticket",
            emoji='📄',
            style=discord.ButtonStyle.secondary,
            custom_id=f"ticket_{panel_id}"
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
            if not hasattr(interaction.client, 'db_pool') or not interaction.client.db_pool:
                await interaction.followup.send("❌ Database not available.", ephemeral=True)
                return
                
            async with interaction.client.db_pool.acquire() as conn:
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
            if panel.get('category_id'):
                category = interaction.guild.get_channel(int(panel['category_id']))
            
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            # Add support team permissions
            if panel.get('support_team_ids'):
                try:
                    team_ids = json.loads(panel['support_team_ids'])
                    for team_id in team_ids:
                        if team_id.startswith('role:'):
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
                        elif team_id.startswith('user:'):
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
                        if team_id.startswith('role:'):
                            role_id = team_id[5:]  # Remove 'role:' prefix
                            role = interaction.guild.get_role(int(role_id))
                            if role:
                                pings.append(role.mention)
                        elif team_id.startswith('user:'):
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
            
            # Set ticket embed header (author field) with placeholder replacement
            if panel.get('ticket_embed_header'):
                embed.set_author(name=replace_placeholders(panel['ticket_embed_header'], interaction))
            
            # Set ticket embed title with placeholder replacement
            if panel.get('ticket_embed_title'):
                embed.title = replace_placeholders(panel['ticket_embed_title'], interaction)
            else:
                embed.title = f"🎫 New Ticket"
            
            # Set ticket embed description with placeholder replacement
            if panel.get('ticket_embed_description'):
                embed.description = replace_placeholders(panel['ticket_embed_description'], interaction)
            else:
                embed.description = f"Hello {interaction.user.mention}! Please describe your issue and we'll help you."
            
            embed.set_footer(text="NexGuard |")
            
            # Send message with pings and embed
            control_view = TicketControlView(channel.name)
            
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
    """Close and claim buttons"""
    def __init__(self, ticket_id: str):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
    
    @discord.ui.button(label="Close", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close ticket with transcript"""
        try:
            if not interaction.user.guild_permissions.manage_messages:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ You need Manage Messages permissions.", ephemeral=True)
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
    
    @discord.ui.button(label="Claim", emoji="🙌", style=discord.ButtonStyle.primary, custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Claim ticket"""
        try:
            if not interaction.user.guild_permissions.manage_messages:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ You need Manage Messages permissions.", ephemeral=True)
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
            embed = discord.Embed(
                description=f"🔒 **Ticket Closed**\n\nClosed by {interaction.user.mention}",
                color=0x5865F2
            )
            if self.reason.value:
                embed.description += f"\n\n**Reason:** {self.reason.value}"
            
            if delay > 0:
                embed.description += f"\n\n⏰ Channel will be deleted in {delay} seconds."
            else:
                embed.description += f"\n\n⏰ Channel will be deleted immediately."
            
            await interaction.followup.send(embed=embed)
            
            # Send transcript to all participants in background
            if participants and transcript_data:
                asyncio.create_task(self.send_transcripts_to_participants(interaction.client, participants, transcript_data))
            
            # Delete channel after delay
            if delay > 0:
                await asyncio.sleep(delay)
                
            try:
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
                                fp=StringIO(readable_transcript),
                                filename=f"ticket_{self.ticket_id}_transcript.txt"
                            )
                            await user.send(embed=embed, file=file)
                        else:
                            embed.description += f"\n\n```\n{readable_transcript[:1800]}\n```"
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
        panel_id: str = None,
        title: str = None,
        category: discord.CategoryChannel = None,
        roles: str = None,
        channel: discord.TextChannel = None,
        panel_embed_header: str = None,
        panel_embed_title: str = None,
        panel_embed_description: str = None,
        ticket_embed_header: str = None,
        ticket_embed_title: str = None,
        ticket_embed_description: str = None
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
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.followup.send("❌ You need Manage Channels permissions to manage ticket panels.", ephemeral=True)
            return
        
        if not hasattr(interaction.client, 'db_pool') or not interaction.client.db_pool:
            await interaction.followup.send("❌ Database not available.", ephemeral=True)
            return
        
        try:
            async with interaction.client.db_pool.acquire() as conn:
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
                    
                    # Set panel embed header (author field)
                    if panel.get('panel_embed_header'):
                        panel_embed.set_author(name=panel['panel_embed_header'])
                    
                    # Set panel embed title
                    if panel.get('panel_embed_title'):
                        panel_embed.title = panel['panel_embed_title']
                    else:
                        panel_embed.title = panel['title']
                    
                    # Set panel embed description
                    if panel.get('panel_embed_description'):
                        panel_embed.description = panel['panel_embed_description']
                    else:
                        panel_embed.description = "Click the button below to open a support ticket."
                    
                    panel_embed.set_footer(text="NexGuard |")
                    
                    # Create panel view
                    panel_view = TicketPanelView([{
                        'panel_id': panel['panel_id'],
                        'title': panel['title']
                    }])
                    
                    # Deploy to specified channel or current channel
                    if channel:
                        await channel.send(embed=panel_embed, view=panel_view)
                        await interaction.followup.send(f"✅ Panel `{panel_id}` deployed to {channel.mention}", ephemeral=True)
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
            self.bot.add_view(TicketPanelView([]))
            self.bot.add_view(TicketControlView(""))
            await self.ensure_ticket_tables()
            logger.info("Revamped ticket system initialized")
        except Exception as e:
            logger.error(f"Error initializing tickets: {e}")
    
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

async def setup(bot):
    await bot.add_cog(TicketsCog(bot))