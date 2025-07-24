import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
import asyncio
from datetime import datetime
from typing import Optional, List

logger = logging.getLogger(__name__)

class TicketPanelView(discord.ui.View):
    def __init__(self, panels_config: dict):
        super().__init__(timeout=None)
        self.panels_config = panels_config
        
        # Create buttons dynamically from panel configuration
        for panel_id, panel_data in panels_config.items():
            button = TicketButton(
                panel_id=panel_id,
                label=panel_data.get('title', 'Create Ticket'),
                emoji=panel_data.get('emoji'),
                style=discord.ButtonStyle.primary,
                custom_id=f"ticket_panel_{panel_id}"
            )
            self.add_item(button)

class TicketButton(discord.ui.Button):
    def __init__(self, panel_id: str, label: str, emoji: Optional[str] = None, **kwargs):
        super().__init__(label=label, emoji=emoji, **kwargs)
        self.panel_id = panel_id
    
    async def callback(self, interaction: discord.Interaction):
        # Check if user already has an open ticket
        if not hasattr(interaction.client, 'db_pool') or not interaction.client.db_pool:
            await interaction.response.send_message("❌ Database connection unavailable.", ephemeral=True)
            return
            
        try:
            async with interaction.client.db_pool.acquire() as conn:
                existing_ticket = await conn.fetchrow("""
                    SELECT id FROM tickets 
                    WHERE guild_id = $1 AND user_id = $2 AND status = 'open'
                    LIMIT 1
                """, str(interaction.guild.id), str(interaction.user.id))
                
                if existing_ticket:
                    await interaction.response.send_message(
                        "❌ You already have an open ticket. Please close your current ticket before creating a new one.",
                        ephemeral=True
                    )
                    return
                
                # Get panel configuration
                panel_config = await conn.fetchrow("""
                    SELECT * FROM ticket_panels 
                    WHERE guild_id = $1 AND panel_id = $2 AND is_active = TRUE
                """, str(interaction.guild.id), self.panel_id)
                
                if not panel_config:
                    await interaction.response.send_message("❌ This ticket panel is no longer active.", ephemeral=True)
                    return
                
                # Check if panel has forms - if so, show form modal
                if panel_config['has_forms'] and panel_config['form_questions']:
                    modal = TicketFormModal(panel_config, self.panel_id)
                    await interaction.response.send_modal(modal)
                else:
                    # Create ticket directly without form
                    await self.create_ticket_directly(interaction, panel_config)
                    
        except Exception as e:
            logger.error(f"Error in ticket panel callback: {e}")
            await interaction.response.send_message("❌ An error occurred. Please try again.", ephemeral=True)
    
    async def create_ticket_directly(self, interaction: discord.Interaction, panel_config):
        """Create a ticket without form questions"""
        try:
            ticket_id = f"ticket-{interaction.user.id}-{int(datetime.utcnow().timestamp())}"
            
            # Create ticket channel
            category = interaction.guild.get_channel(int(panel_config['category_id'])) if panel_config['category_id'] else None
            
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(
                    view_channel=True, 
                    send_messages=True, 
                    read_message_history=True
                ),
                interaction.guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_channels=True,
                    read_message_history=True
                )
            }
            
            # Add support team permissions
            if panel_config['support_team_ids']:
                team_ids = json.loads(panel_config['support_team_ids'])
                for role_id in team_ids:
                    role = interaction.guild.get_role(int(role_id))
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True,
                            read_message_history=True
                        )
            
            channel = await interaction.guild.create_text_channel(
                name=f"ticket-{interaction.user.name}",
                category=category,
                overwrites=overwrites
            )
            
            # Store ticket in database
            async with interaction.client.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO tickets (
                        ticket_id, guild_id, channel_id, user_id, username,
                        panel_id, subject, status, priority, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, 
                    ticket_id, str(interaction.guild.id), str(channel.id), 
                    str(interaction.user.id), interaction.user.display_name,
                    self.panel_id, panel_config['title'], 'open', 'medium', datetime.utcnow()
                )
            
            # Send welcome message with ticket controls
            embed = discord.Embed(
                title=f"🎫 {panel_config['title']}",
                description=panel_config.get('welcome_message', f"Hello {interaction.user.mention}! Thank you for creating a ticket."),
                color=0x00ff00
            )
            embed.add_field(name="User", value=interaction.user.mention, inline=True)
            embed.add_field(name="Created", value=f"<t:{int(datetime.utcnow().timestamp())}:R>", inline=True)
            embed.set_footer(text=f"Ticket ID: {ticket_id}")
            
            view = TicketControlView(ticket_id)
            await channel.send(embed=embed, view=view)
            
            await interaction.response.send_message(
                f"✅ Ticket created! Please continue in {channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await interaction.response.send_message("❌ Failed to create ticket. Please try again.", ephemeral=True)

class TicketFormModal(discord.ui.Modal):
    def __init__(self, panel_config, panel_id: str):
        super().__init__(title=f"{panel_config['title']} - Information Required")
        self.panel_config = panel_config
        self.panel_id = panel_id
        
        # Parse form questions and create input fields
        questions = json.loads(panel_config['form_questions']) if panel_config['form_questions'] else []
        
        for i, question in enumerate(questions[:5]):  # Discord modal limit of 5 fields
            field = discord.ui.TextInput(
                label=question.get('label', f'Question {i+1}'),
                placeholder=question.get('placeholder', 'Your answer...'),
                required=question.get('required', True),
                max_length=question.get('max_length', 1000),
                style=discord.TextStyle.paragraph if question.get('multiline', False) else discord.TextStyle.short
            )
            self.add_item(field)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Collect form responses
            responses = {}
            for i, item in enumerate(self.children):
                if isinstance(item, discord.ui.TextInput):
                    responses[f'question_{i}'] = item.value
            
            # Create ticket with form data
            await self.create_ticket_with_form(interaction, responses)
            
        except Exception as e:
            logger.error(f"Error submitting ticket form: {e}")
            await interaction.response.send_message("❌ An error occurred. Please try again.", ephemeral=True)
    
    async def create_ticket_with_form(self, interaction: discord.Interaction, form_responses: dict):
        """Create ticket with form responses"""
        try:
            ticket_id = f"ticket-{interaction.user.id}-{int(datetime.utcnow().timestamp())}"
            
            # Create ticket channel (similar to create_ticket_directly but with form data)
            category = interaction.guild.get_channel(int(self.panel_config['category_id'])) if self.panel_config['category_id'] else None
            
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(
                    view_channel=True, 
                    send_messages=True, 
                    read_message_history=True
                ),
                interaction.guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_channels=True,
                    read_message_history=True
                )
            }
            
            # Add support team permissions
            if self.panel_config['support_team_ids']:
                team_ids = json.loads(self.panel_config['support_team_ids'])
                for role_id in team_ids:
                    role = interaction.guild.get_role(int(role_id))
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True,
                            read_message_history=True
                        )
            
            channel = await interaction.guild.create_text_channel(
                name=f"ticket-{interaction.user.name}",
                category=category,
                overwrites=overwrites
            )
            
            # Store ticket with form data
            async with interaction.client.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO tickets (
                        ticket_id, guild_id, channel_id, user_id, username,
                        panel_id, subject, status, priority, form_responses, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """, 
                    ticket_id, str(interaction.guild.id), str(channel.id), 
                    str(interaction.user.id), interaction.user.display_name,
                    self.panel_id, self.panel_config['title'], 'open', 'medium',
                    json.dumps(form_responses), datetime.utcnow()
                )
            
            # Send welcome message with form responses
            embed = discord.Embed(
                title=f"🎫 {self.panel_config['title']}",
                description=self.panel_config.get('welcome_message', f"Hello {interaction.user.mention}! Thank you for creating a ticket."),
                color=0x00ff00
            )
            embed.add_field(name="User", value=interaction.user.mention, inline=True)
            embed.add_field(name="Created", value=f"<t:{int(datetime.utcnow().timestamp())}:R>", inline=True)
            
            # Add form responses to embed
            if form_responses:
                questions = json.loads(self.panel_config['form_questions']) if self.panel_config['form_questions'] else []
                for i, question in enumerate(questions):
                    if f'question_{i}' in form_responses:
                        embed.add_field(
                            name=question.get('label', f'Question {i+1}'),
                            value=form_responses[f'question_{i}'][:1000] + ('...' if len(form_responses[f'question_{i}']) > 1000 else ''),
                            inline=False
                        )
            
            embed.set_footer(text=f"Ticket ID: {ticket_id}")
            
            view = TicketControlView(ticket_id)
            await channel.send(embed=embed, view=view)
            
            await interaction.response.send_message(
                f"✅ Ticket created! Please continue in {channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error creating ticket with form: {e}")
            await interaction.response.send_message("❌ Failed to create ticket. Please try again.", ephemeral=True)

class TicketControlView(discord.ui.View):
    def __init__(self, ticket_id: str):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
    
    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Show confirmation and close ticket
        modal = CloseTicketModal(self.ticket_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Claim Ticket", style=discord.ButtonStyle.secondary, custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            async with interaction.client.db_pool.acquire() as conn:
                # Check if ticket exists and is not already claimed
                ticket = await conn.fetchrow("""
                    SELECT * FROM tickets WHERE ticket_id = $1 AND guild_id = $2
                """, self.ticket_id, str(interaction.guild.id))
                
                if not ticket:
                    await interaction.response.send_message("❌ Ticket not found.", ephemeral=True)
                    return
                
                if ticket['claimed_by']:
                    claimer = interaction.guild.get_member(int(ticket['claimed_by']))
                    claimer_name = claimer.display_name if claimer else "Unknown User"
                    await interaction.response.send_message(
                        f"❌ This ticket is already claimed by {claimer_name}.", 
                        ephemeral=True
                    )
                    return
                
                # Claim the ticket
                await conn.execute("""
                    UPDATE tickets 
                    SET claimed_by = $1, claimed_at = $2, status = 'claimed'
                    WHERE ticket_id = $3
                """, str(interaction.user.id), datetime.utcnow(), self.ticket_id)
                
                embed = discord.Embed(
                    title="🎯 Ticket Claimed",
                    description=f"{interaction.user.mention} has claimed this ticket and will be handling your request.",
                    color=0xff9900
                )
                embed.set_footer(text=f"Claimed at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
                
                await interaction.response.send_message(embed=embed)
                
        except Exception as e:
            logger.error(f"Error claiming ticket: {e}")
            await interaction.response.send_message("❌ Failed to claim ticket.", ephemeral=True)

class CloseTicketModal(discord.ui.Modal):
    def __init__(self, ticket_id: str):
        super().__init__(title="Close Ticket")
        self.ticket_id = ticket_id
        
        self.reason = discord.ui.TextInput(
            label="Reason for closing (optional)",
            placeholder="Why is this ticket being closed?",
            required=False,
            max_length=1000,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Generate transcript before closing
            transcript_url = await self.generate_transcript(interaction)
            
            # Update ticket status
            async with interaction.client.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE tickets 
                    SET status = 'closed', closed_by = $1, closed_at = $2, 
                        close_reason = $3, transcript_url = $4
                    WHERE ticket_id = $5
                """, 
                    str(interaction.user.id), datetime.utcnow(), 
                    self.reason.value or "No reason provided", 
                    transcript_url, self.ticket_id
                )
                
                # Get ticket info for user feedback
                ticket = await conn.fetchrow("""
                    SELECT user_id FROM tickets WHERE ticket_id = $1
                """, self.ticket_id)
            
            embed = discord.Embed(
                title="🔒 Ticket Closed",
                description=f"This ticket has been closed by {interaction.user.mention}",
                color=0xff0000
            )
            embed.add_field(name="Reason", value=self.reason.value or "No reason provided", inline=False)
            if transcript_url:
                embed.add_field(name="Transcript", value=f"[View Transcript]({transcript_url})", inline=False)
            embed.set_footer(text="This channel will be deleted in 30 seconds.")
            
            await interaction.response.send_message(embed=embed)
            
            # Send feedback request to user
            if ticket:
                user = interaction.client.get_user(int(ticket['user_id']))
                if user:
                    try:
                        feedback_embed = discord.Embed(
                            title="📝 Rate Your Support Experience",
                            description=f"Your ticket `{self.ticket_id}` has been resolved. How was our support?",
                            color=0x00ff00
                        )
                        view = FeedbackView(self.ticket_id)
                        await user.send(embed=feedback_embed, view=view)
                    except:
                        pass  # User might have DMs disabled
            
            # Delete channel after delay
            await asyncio.sleep(30)
            await interaction.channel.delete()
            
        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
            await interaction.response.send_message("❌ Failed to close ticket.", ephemeral=True)
    
    async def generate_transcript(self, interaction: discord.Interaction) -> Optional[str]:
        """Generate and store ticket transcript"""
        try:
            messages = []
            async for message in interaction.channel.history(limit=None, oldest_first=True):
                messages.append({
                    'author': message.author.display_name,
                    'content': message.content,
                    'timestamp': message.created_at.isoformat(),
                    'attachments': [att.url for att in message.attachments]
                })
            
            # Store transcript in database
            transcript_data = json.dumps(messages)
            async with interaction.client.db_pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO ticket_transcripts (ticket_id, guild_id, transcript_data, created_at)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                """, self.ticket_id, str(interaction.guild.id), transcript_data, datetime.utcnow())
                
                # Return transcript URL (would be implemented in web dashboard)
                return f"https://nexguard.com/transcripts/{result['id']}"
                
        except Exception as e:
            logger.error(f"Error generating transcript: {e}")
            return None

class FeedbackView(discord.ui.View):
    def __init__(self, ticket_id: str):
        super().__init__(timeout=300)  # 5 minute timeout
        self.ticket_id = ticket_id
        
        # Star rating buttons
        for i in range(1, 6):
            button = discord.ui.Button(
                label=f"{i} ⭐",
                style=discord.ButtonStyle.secondary,
                custom_id=f"rating_{i}"
            )
            button.callback = self.create_rating_callback(i)
            self.add_item(button)
    
    def create_rating_callback(self, rating: int):
        async def rating_callback(interaction: discord.Interaction):
            modal = FeedbackModal(self.ticket_id, rating)
            await interaction.response.send_modal(modal)
        return rating_callback

class FeedbackModal(discord.ui.Modal):
    def __init__(self, ticket_id: str, rating: int):
        super().__init__(title=f"Feedback - {rating} Star{'s' if rating != 1 else ''}")
        self.ticket_id = ticket_id
        self.rating = rating
        
        self.comment = discord.ui.TextInput(
            label="Additional comments (optional)",
            placeholder="Tell us about your support experience...",
            required=False,
            max_length=1000,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.comment)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Store feedback
            async with interaction.client.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE tickets 
                    SET satisfaction = $1, satisfaction_comment = $2, feedback_at = $3
                    WHERE ticket_id = $4
                """, self.rating, self.comment.value, datetime.utcnow(), self.ticket_id)
            
            embed = discord.Embed(
                title="✅ Thank You for Your Feedback!",
                description=f"Your {self.rating}-star rating has been recorded. We appreciate your feedback!",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            await interaction.response.send_message("❌ Failed to submit feedback.", ephemeral=True)

class TicketPanelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ticket-panel", description="Create or manage ticket panels")
    @app_commands.describe(
        action="Action to perform",
        panel_name="Name of the panel",
        title="Display title for the panel",
        description="Description of what this panel is for",
        category="Discord category to create tickets in",
        emoji="Emoji for the button",
        support_team="Role that will handle tickets from this panel"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Create", value="create"),
        app_commands.Choice(name="Edit", value="edit"),
        app_commands.Choice(name="Delete", value="delete"),
        app_commands.Choice(name="List", value="list"),
        app_commands.Choice(name="Deploy", value="deploy")
    ])
    async def ticket_panel(
        self, 
        interaction: discord.Interaction, 
        action: str,
        panel_name: str = None,
        title: str = None,
        description: str = None,
        category: discord.CategoryChannel = None,
        emoji: str = None,
        support_team: discord.Role = None
    ):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need Manage Server permissions to use this command.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            if action == "create":
                await self.create_panel(interaction, panel_name, title, description, category, emoji, support_team)
            elif action == "edit":
                await self.edit_panel(interaction, panel_name, title, description, category, emoji, support_team)
            elif action == "delete":
                await self.delete_panel(interaction, panel_name)
            elif action == "list":
                await self.list_panels(interaction)
            elif action == "deploy":
                await self.deploy_panels(interaction)
                
        except Exception as e:
            logger.error(f"Error in ticket panel command: {e}")
            await interaction.followup.send("❌ An error occurred. Please try again.", ephemeral=True)
    
    async def create_panel(self, interaction, panel_name, title, description, category, emoji, support_team):
        if not all([panel_name, title]):
            await interaction.followup.send("❌ Panel name and title are required.", ephemeral=True)
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO ticket_panels (
                        guild_id, panel_id, title, description, category_id, 
                        emoji, support_team_ids, is_active, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (guild_id, panel_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        category_id = EXCLUDED.category_id,
                        emoji = EXCLUDED.emoji,
                        support_team_ids = EXCLUDED.support_team_ids,
                        is_active = TRUE
                """, 
                    str(interaction.guild.id), panel_name.lower().replace(' ', '_'), 
                    title, description or "Support ticket panel", 
                    str(category.id) if category else None,
                    emoji, json.dumps([str(support_team.id)]) if support_team else None,
                    True, datetime.utcnow()
                )
            
            embed = discord.Embed(
                title="✅ Ticket Panel Created",
                description=f"Panel `{panel_name}` has been created successfully!",
                color=0x00ff00
            )
            embed.add_field(name="Title", value=title, inline=False)
            if description:
                embed.add_field(name="Description", value=description, inline=False)
            if category:
                embed.add_field(name="Category", value=category.mention, inline=True)
            if support_team:
                embed.add_field(name="Support Team", value=support_team.mention, inline=True)
            embed.add_field(name="Next Step", value="Use `/ticket-panel deploy` to deploy all panels to a channel", inline=False)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creating ticket panel: {e}")
            await interaction.followup.send("❌ Failed to create panel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketPanelCommands(bot))
    logger.info("Ticket panel system loaded")