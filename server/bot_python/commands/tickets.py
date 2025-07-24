import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
import asyncio
from datetime import datetime
from io import StringIO

logger = logging.getLogger(__name__)

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
            if not interaction.guild:
                await interaction.response.send_message("❌ This can only be used in a server.", ephemeral=True)
                return
            
            # Get panel configuration from database
            if not hasattr(interaction.client, 'db_pool') or not interaction.client.db_pool:
                await interaction.response.send_message("❌ Database not available.", ephemeral=True)
                return
                
            async with interaction.client.db_pool.acquire() as conn:
                panel = await conn.fetchrow("""
                    SELECT * FROM ticket_panels 
                    WHERE guild_id = $1 AND panel_id = $2
                """, str(interaction.guild.id), self.panel_id)
                
                if not panel:
                    await interaction.response.send_message("❌ Panel configuration not found.", ephemeral=True)
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
            
            channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                reason=f"Ticket by {interaction.user}"
            )
            
            # Prepare role/user pings
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
            
            # Create ticket channel embed with separate customization
            embed = discord.Embed(color=0x5865F2)
            
            # Set ticket embed header (author field)
            if panel.get('ticket_embed_header'):
                embed.set_author(name=panel['ticket_embed_header'])
            
            # Set ticket embed title
            if panel.get('ticket_embed_title'):
                embed.title = panel['ticket_embed_title']
            else:
                embed.title = f"🎫 New Ticket"
            
            # Set ticket embed description
            if panel.get('ticket_embed_description'):
                embed.description = panel['ticket_embed_description']
            else:
                embed.description = f"Hello {interaction.user.mention}! Please describe your issue and we'll help you."
            
            embed.set_footer(text="NexGuard | :nexguard:")
            
            # Send message with pings and embed
            control_view = TicketControlView(channel.name)
            
            if ping_content:
                await channel.send(content=ping_content, embed=embed, view=control_view)
            else:
                await channel.send(embed=embed, view=control_view)
            
            await interaction.response.send_message(
                f"✅ Ticket created! Continue in {channel.mention}",
                ephemeral=True
            )
                
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await interaction.response.send_message("❌ Failed to create ticket.", ephemeral=True)

class TicketControlView(discord.ui.View):
    """Close and claim buttons"""
    def __init__(self, ticket_id: str):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
    
    @discord.ui.button(label="Close", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close ticket with transcript"""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You need Manage Messages permissions.", ephemeral=True)
            return
        
        modal = CloseTicketModal(self.ticket_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Claim", emoji="🙌", style=discord.ButtonStyle.primary, custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Claim ticket"""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You need Manage Messages permissions.", ephemeral=True)
            return
        
        # Disable claim button
        self.claim_ticket.disabled = True
        self.claim_ticket.label = f"Claimed by {interaction.user.display_name}"
        
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"🙌 Ticket claimed by {interaction.user.mention}")

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
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            
            # Generate transcript and get participants
            transcript_data, participants = await self.generate_transcript(interaction.channel)
            
            # Send closing message
            embed = discord.Embed(
                description=f"🔒 **Ticket Closed**\n\nClosed by {interaction.user.mention}",
                color=0x5865F2
            )
            if self.reason.value:
                embed.description += f"\n\n**Reason:** {self.reason.value}"
            
            await interaction.followup.send(embed=embed)
            
            # Send transcript to all participants
            if participants and transcript_data:
                await self.send_transcripts_to_participants(interaction.client, participants, transcript_data)
            
            # Delete channel after delay
            await asyncio.sleep(30)
            try:
                await interaction.channel.delete(reason="Ticket closed")
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
            await interaction.followup.send("❌ Failed to close ticket.", ephemeral=True)
    
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
        panel_embed_header="Panel message embed header",
        panel_embed_title="Panel message embed title", 
        panel_embed_description="Panel message embed description",
        ticket_embed_header="Ticket channel embed header",
        ticket_embed_title="Ticket channel embed title",
        ticket_embed_description="Ticket channel embed description"
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
        panel_embed_header: str = None,
        panel_embed_title: str = None,
        panel_embed_description: str = None,
        ticket_embed_header: str = None,
        ticket_embed_title: str = None,
        ticket_embed_description: str = None
    ):
        """Manage ticket panels"""
        
        # Check permissions
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You need Manage Channels permissions to manage ticket panels.", ephemeral=True)
            return
        
        if not hasattr(interaction.client, 'db_pool') or not interaction.client.db_pool:
            await interaction.response.send_message("❌ Database not available.", ephemeral=True)
            return
        
        try:
            async with interaction.client.db_pool.acquire() as conn:
                if action == "create":
                    if not panel_id or not title:
                        await interaction.response.send_message("❌ Panel ID and title are required for creation.", ephemeral=True)
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
                    
                    await interaction.response.send_message(embed=embed)
                
                elif action == "deploy":
                    if not panel_id:
                        await interaction.response.send_message("❌ Panel ID required for deployment.", ephemeral=True)
                        return
                    
                    # Get panel data
                    panel = await conn.fetchrow("""
                        SELECT * FROM ticket_panels 
                        WHERE guild_id = $1 AND panel_id = $2
                    """, str(interaction.guild.id), panel_id)
                    
                    if not panel:
                        await interaction.response.send_message("❌ Panel not found.", ephemeral=True)
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
                    
                    panel_embed.set_footer(text="NexGuard | :nexguard:")
                    
                    # Prepare role/user pings for panel message too
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
                            logger.error(f"Error parsing panel support team pings: {e}")
                    
                    # Create panel view
                    panel_view = TicketPanelView([{
                        'panel_id': panel['panel_id'],
                        'title': panel['title']
                    }])
                    
                    # Send panel message with same embed and pings as ticket channel
                    if ping_content:
                        await interaction.response.send_message(content=ping_content, embed=panel_embed, view=panel_view)
                    else:
                        await interaction.response.send_message(embed=panel_embed, view=panel_view)
                
                elif action == "list":
                    panels = await conn.fetch("""
                        SELECT * FROM ticket_panels 
                        WHERE guild_id = $1
                        ORDER BY created_at DESC
                    """, str(interaction.guild.id))
                    
                    if not panels:
                        await interaction.response.send_message("❌ No ticket panels found.", ephemeral=True)
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
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                
                elif action == "delete":
                    if not panel_id:
                        await interaction.response.send_message("❌ Panel ID required for deletion.", ephemeral=True)
                        return
                    
                    # Check if panel exists
                    panel = await conn.fetchrow("""
                        SELECT * FROM ticket_panels 
                        WHERE guild_id = $1 AND panel_id = $2
                    """, str(interaction.guild.id), panel_id)
                    
                    if not panel:
                        await interaction.response.send_message("❌ Panel not found.", ephemeral=True)
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
                    
                    await interaction.response.send_message(embed=embed)
                
                else:
                    await interaction.response.send_message("❌ Invalid action.", ephemeral=True)
                    
        except Exception as e:
            logger.error(f"Error managing ticket panel: {e}")
            await interaction.response.send_message("❌ Failed to manage ticket panel.", ephemeral=True)
    
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