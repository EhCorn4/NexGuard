import discord
from discord.ext import commands
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
            
            # Create ticket channel
            channel_name = f"{self.panel_id}-{interaction.user.name}".lower()
            channel_name = "".join(c for c in channel_name if c.isalnum() or c in '-_')[:50]
            
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            channel = await interaction.guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                reason=f"Ticket by {interaction.user}"
            )
            
            # Send welcome message with control buttons
            embed = discord.Embed(
                title=f"🎫 New Ticket",
                description=f"Hello {interaction.user.mention}! Please describe your issue.",
                color=0x5865F2
            )
            
            control_view = TicketControlView(channel.name)
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
    """Minimal ticket system - 3 core features only"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Register persistent views"""
        try:
            self.bot.add_view(TicketPanelView([]))
            self.bot.add_view(TicketControlView(""))
            logger.info("Minimal ticket system initialized")
        except Exception as e:
            logger.error(f"Error initializing tickets: {e}")

async def setup(bot):
    await bot.add_cog(TicketsCog(bot))