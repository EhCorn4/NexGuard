import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
import asyncio
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from io import StringIO

logger = logging.getLogger(__name__)

class TicketPanelView(discord.ui.View):
    """Panel with buttons to open tickets"""
    def __init__(self, panels: List[Dict[str, Any]]):
        super().__init__(timeout=None)
        self.panels = panels
        
        # Create buttons for each panel
        for panel in panels[:5]:
            button = TicketButton(
                panel_id=panel['panel_id'],
                title=panel['title'],
                custom_id=f"ticket_panel_{panel['panel_id']}"
            )
            self.add_item(button)

class TicketButton(discord.ui.Button):
    """Button to open a ticket"""
    def __init__(self, panel_id: str, title: str, **kwargs):
        super().__init__(
            label="Open a Ticket",
            emoji='📄',
            style=discord.ButtonStyle.secondary,
            **kwargs
        )
        self.panel_id = panel_id
        self.title = title

    async def callback(self, interaction: discord.Interaction):
        """Create a new ticket when button is pressed"""
        try:
            # Get panel data
            if not hasattr(interaction.client, 'db_pool') or not interaction.client.db_pool:
                await interaction.response.send_message("❌ Database not available.", ephemeral=True)
                return
                
            async with interaction.client.db_pool.acquire() as conn:
                panel = await conn.fetchrow("""
                    SELECT * FROM ticket_panels 
                    WHERE guild_id = $1 AND panel_id = $2
                """, str(interaction.guild.id), self.panel_id)
                
                if not panel:
                    await interaction.response.send_message("❌ Panel not found.", ephemeral=True)
                    return
                
                # Get ticket count for naming
                ticket_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM tickets WHERE guild_id = $1
                """, str(interaction.guild.id))
                
                ticket_id = f"ticket-{ticket_count + 1:04d}"
                
                # Create ticket channel
                channel_name = f"{panel['panel_id']}-{interaction.user.name}".lower()
                channel_name = "".join(c for c in channel_name if c.isalnum() or c in '-_')[:50]
                
                category = interaction.guild.get_channel(int(panel['category_id'])) if panel['category_id'] else None
                
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                
                channel = await interaction.guild.create_text_channel(
                    name=channel_name,
                    category=category,
                    overwrites=overwrites,
                    reason=f"Ticket created by {interaction.user}"
                )
                
                # Store ticket in database
                await conn.execute("""
                    INSERT INTO tickets (
                        ticket_id, guild_id, user_id, channel_id, panel_id, 
                        subject, status, priority, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, 
                    ticket_id, str(interaction.guild.id), str(interaction.user.id), 
                    str(channel.id), self.panel_id, panel['title'], 
                    'open', 'normal', datetime.utcnow()
                )
                
                # Send welcome message with control buttons
                embed = discord.Embed(
                    title=f"🎫 New Ticket - {ticket_id}",
                    description=f"Hello {interaction.user.mention}! Please describe your issue and we'll help you.",
                    color=0x5865F2
                )
                embed.set_footer(text="NexGuard | :nexguard:")
                
                control_view = TicketControlView(ticket_id)
                await channel.send(embed=embed, view=control_view)
                
                await interaction.response.send_message(
                    f"✅ Ticket created! Continue in {channel.mention}",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await interaction.response.send_message("❌ Failed to create ticket.", ephemeral=True)

class TicketControlView(discord.ui.View):
    """Simple control buttons - Close and Claim only"""
    def __init__(self, ticket_id: str):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
    
    @discord.ui.button(label="Close", emoji="🔒", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close ticket with transcript generation"""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You need Manage Messages permissions to close tickets.", ephemeral=True)
            return
        
        modal = CloseTicketModal(self.ticket_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Claim", emoji="🙌", style=discord.ButtonStyle.primary)
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Claim ticket for support staff"""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You need Manage Messages permissions to claim tickets.", ephemeral=True)
            return
        
        try:
            if not hasattr(interaction.client, 'db_pool') or not interaction.client.db_pool:
                await interaction.response.send_message("❌ Database not available.", ephemeral=True)
                return
                
            async with interaction.client.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE tickets SET 
                        claimed_by = $1, 
                        claimed_at = $2,
                        status = 'claimed'
                    WHERE ticket_id = $3 AND guild_id = $4
                """, str(interaction.user.id), datetime.utcnow(), self.ticket_id, str(interaction.guild.id))
            
            # Disable claim button and update
            self.claim_ticket.disabled = True
            self.claim_ticket.label = f"Claimed by {interaction.user.display_name}"
            
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f"🙌 Ticket claimed by {interaction.user.mention}")
            
        except Exception as e:
            logger.error(f"Error claiming ticket: {e}")
            await interaction.response.send_message("❌ Failed to claim ticket.", ephemeral=True)

class CloseTicketModal(discord.ui.Modal):
    """Modal for closing tickets with transcript generation"""
    def __init__(self, ticket_id: str):
        super().__init__(title="Close Ticket")
        self.ticket_id = ticket_id
        
        self.reason = discord.ui.TextInput(
            label="Reason for closing (optional)",
            placeholder="Why is this ticket being closed?",
            required=False,
            max_length=2000,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            
            # Generate transcript and get participants
            transcript_data, participants = await self.generate_transcript(interaction.channel)
            
            # Update ticket status
            if hasattr(interaction.client, 'db_pool') and interaction.client.db_pool:
                async with interaction.client.db_pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE tickets 
                        SET status = 'closed', closed_by = $1, closed_at = $2, close_reason = $3
                        WHERE ticket_id = $4
                    """, 
                        str(interaction.user.id), datetime.utcnow(),
                        self.reason.value or "No reason provided", self.ticket_id
                    )
            
            # Send closing message
            embed = discord.Embed(
                description=f"🔒 **Ticket Closed**\n\nThis ticket has been closed by {interaction.user.mention}",
                color=0x5865F2
            )
            if self.reason.value:
                embed.description += f"\n\n**Reason:** {self.reason.value}"
            embed.set_footer(text="NexGuard | :nexguard: • This channel will be deleted in 30 seconds.")
            
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
    
    async def generate_transcript(self, channel) -> tuple[Optional[str], set[int]]:
        """Generate transcript and return participants"""
        try:
            messages = []
            participants = set()
            
            async for message in channel.history(limit=1000, oldest_first=True):
                if not message.author.bot or message.embeds:
                    msg_data = {
                        'timestamp': message.created_at.isoformat(),
                        'author': message.author.display_name,
                        'author_id': str(message.author.id),
                        'content': message.content,
                        'attachments': [att.url for att in message.attachments],
                        'embeds': len(message.embeds) > 0
                    }
                    messages.append(msg_data)
                    
                    # Track human participants only
                    if not message.author.bot:
                        participants.add(message.author.id)
            
            transcript_json = json.dumps(messages, indent=2)
            return transcript_json, participants
            
        except Exception as e:
            logger.error(f"Error generating transcript: {e}")
            return None, set()
    
    async def send_transcripts_to_participants(self, bot, participants: set[int], transcript_data: str):
        """Send transcript to all participants who typed in the ticket"""
        try:
            messages = json.loads(transcript_data)
            
            # Create readable transcript
            readable_transcript = f"# Ticket Transcript - {self.ticket_id}\n\n"
            for msg in messages:
                timestamp = datetime.fromisoformat(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S UTC")
                author = msg['author']
                content = msg['content']
                
                if content:
                    readable_transcript += f"**[{timestamp}] {author}:**\n{content}\n\n"
                elif msg['embeds']:
                    readable_transcript += f"**[{timestamp}] {author}:** [Sent an embed message]\n\n"
                
                if msg['attachments']:
                    readable_transcript += f"**Attachments:** {', '.join(msg['attachments'])}\n\n"
            
            # Send to all participants
            logger.info(f"📋 Sending transcript to {len(participants)} participants")
            
            for user_id in participants:
                try:
                    user = bot.get_user(user_id)
                    if user:
                        embed = discord.Embed(
                            title=f"📋 Ticket Transcript - {self.ticket_id}",
                            description=f"Here's a complete transcript of your ticket conversation.",
                            color=0x5865F2,
                            timestamp=datetime.utcnow()
                        )
                        
                        embed.add_field(
                            name="Ticket Details",
                            value=f"**Ticket ID:** {self.ticket_id}\n**Closed:** <t:{int(datetime.utcnow().timestamp())}:F>",
                            inline=False
                        )
                        
                        # Send as file if too long
                        if len(readable_transcript) > 2000:
                            transcript_file = discord.File(
                                fp=StringIO(readable_transcript),
                                filename=f"ticket_{self.ticket_id}_transcript.txt"
                            )
                            await user.send(embed=embed, file=transcript_file)
                            logger.info(f"✅ Sent transcript file to {user.display_name}")
                        else:
                            embed.description += f"\n\n```\n{readable_transcript[:1800]}{'...' if len(readable_transcript) > 1800 else ''}\n```"
                            await user.send(embed=embed)
                            logger.info(f"✅ Sent transcript embed to {user.display_name}")
                            
                except Exception as e:
                    logger.warning(f"Could not send transcript to user {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending transcripts to participants: {e}")

class TicketsCog(commands.Cog):
    """Simple ticket system with panel buttons, close/claim buttons, and transcript functionality"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Ensure persistent views are registered"""
        try:
            # Add views for persistence
            self.bot.add_view(TicketPanelView([]))
            self.bot.add_view(TicketControlView(""))
            logger.info("Ticket system initialized")
        except Exception as e:
            logger.error(f"Error initializing ticket system: {e}")

async def setup(bot):
    await bot.add_cog(TicketsCog(bot))