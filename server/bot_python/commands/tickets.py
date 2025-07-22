import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class TicketPanelView(discord.ui.View):
    """Main view for ticket creation panels - TicketsBot.net style"""
    def __init__(self, panels: List[Dict[str, Any]]):
        super().__init__(timeout=None)
        self.panels = panels
        
        # Create buttons dynamically from panels
        for panel in panels[:5]:  # Discord max 5 buttons per row
            button = TicketButton(
                panel_id=panel['panel_id'],
                title=panel['title'],
                emoji='📄',  # Document icon like in reference
                custom_id=f"ticket_panel_{panel['panel_id']}"
            )
            self.add_item(button)

class TicketButton(discord.ui.Button):
    """Individual ticket creation button"""
    def __init__(self, panel_id: str, title: str, emoji: Optional[str] = None, **kwargs):
        super().__init__(
            label="Open a Ticket",  # Consistent label like in reference
            emoji='📄',  # Document icon like in reference
            style=discord.ButtonStyle.secondary,  # Gray button style
            **kwargs
        )
        self.panel_id = panel_id
        self.title = title
    
    async def callback(self, interaction: discord.Interaction):
        try:
            bot = interaction.client
            
            # Get panel configuration
            if bot.db_pool:
                async with bot.db_pool.acquire() as conn:
                    panel = await conn.fetchrow("""
                        SELECT * FROM ticket_panels 
                        WHERE guild_id = $1 AND panel_id = $2 AND is_active = TRUE
                    """, str(interaction.guild.id), self.panel_id)
                    
                    if not panel:
                        await interaction.response.send_message("❌ This ticket panel is no longer active.", ephemeral=True)
                        return
                    
                    # Check if panel has forms
                    if panel['has_form'] and panel['form_questions']:
                        modal = TicketFormModal(panel, self.panel_id)
                        await interaction.response.send_modal(modal)
                    else:
                        # Create ticket directly
                        await self.create_ticket_direct(interaction, panel)
            else:
                await interaction.response.send_message("❌ Database unavailable.", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error in ticket button callback: {e}")
            await interaction.response.send_message("❌ An error occurred. Please try again.", ephemeral=True)
    
    async def create_ticket_direct(self, interaction: discord.Interaction, panel):
        """Create ticket without form"""
        try:
            # Generate unique ticket ID
            ticket_count = await self.get_ticket_count(interaction, interaction.client.db_pool)
            ticket_id = f"ticket-{ticket_count + 1:04d}"
            
            # Create ticket channel and store in database
            channel = await self.setup_ticket_channel(interaction, panel, ticket_id)
            
            # Send only ephemeral success message (no public notification in panel channel)
            await interaction.response.send_message(
                f"✅ Ticket created! Continue in {channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error creating direct ticket: {e}")
            try:
                await interaction.response.send_message("❌ Failed to create ticket.", ephemeral=True)
            except:
                logger.error("Could not send error response to user")
    
    def process_placeholders(self, text: str, context: dict) -> str:
        """Process placeholder variables like {user.mention}"""
        if not text or not isinstance(text, str):
            return text or ""
            
        try:
            # Replace user placeholders
            if 'user' in context:
                user = context['user']
                text = text.replace('{user.mention}', str(user.get('mention', '')))
                text = text.replace('{user.name}', str(user.get('name', '')))
                text = text.replace('{user.display_name}', str(user.get('display_name', '')))
                text = text.replace('{user.id}', str(user.get('id', '')))
            
            # Replace guild placeholders  
            if 'guild' in context:
                guild = context['guild']
                text = text.replace('{guild.name}', str(guild.get('name', '')))
                text = text.replace('{guild.member_count}', str(guild.get('member_count', '')))
            
            # Replace ticket placeholders
            if 'ticket' in context:
                ticket = context['ticket']
                text = text.replace('{ticket.id}', str(ticket.get('id', '')))
                text = text.replace('{ticket.category}', str(ticket.get('category', '')))
            
            return text
        except Exception as e:
            logger.error(f"Error processing placeholders: {e}")
            return text
    
    async def setup_ticket_channel(self, interaction, panel, ticket_id, form_data=None):
        """Setup the ticket channel with proper permissions and embeds"""
        # Get category if specified
        category = None
        if panel['category_id']:
            category = interaction.guild.get_channel(int(panel['category_id']))
        
        # Set up permissions
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            ),
            interaction.guild.me: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, manage_channels=True, 
                read_message_history=True, manage_messages=True
            )
        }
        
        # Add support team permissions - enhanced debugging
        logger.info(f"🔍 Checking support team IDs for panel: {panel.get('support_team_ids')}")
        
        if panel.get('support_team_ids'):
            try:
                team_ids = json.loads(panel['support_team_ids'])
                logger.info(f"🔍 Parsed support team IDs: {team_ids}")
                support_roles_added = []
                
                for role_id in team_ids:
                    logger.info(f"🔍 Looking for role ID: {role_id}")
                    role = interaction.guild.get_role(int(role_id))
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(
                            view_channel=True, send_messages=True, read_message_history=True, 
                            manage_messages=True  # Allow support staff to manage messages
                        )
                        support_roles_added.append(role.name)
                        logger.info(f"✅ Added channel access for support role: {role.name} (ID: {role.id})")
                    else:
                        logger.warning(f"❌ Could not find role with ID: {role_id}")
                
                if support_roles_added:
                    logger.info(f"🎫 Support team with access: {', '.join(support_roles_added)}")
                else:
                    logger.warning(f"❌ No support roles were added to channel permissions")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"❌ Error parsing support team IDs: {e}")
        else:
            logger.info(f"ℹ️ No support team configured for this panel")
        
        # Create channel
        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name}".lower(),
            category=category,
            overwrites=overwrites,
            topic=f"Ticket {ticket_id} | {panel['title']} | {interaction.user.display_name}"
        )
        
        # Store in database with category field populated
        async with interaction.client.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO tickets (
                    ticket_id, guild_id, channel_id, user_id, username,
                    category, panel_id, subject, status, priority, 
                    form_responses, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """, 
                ticket_id, str(interaction.guild.id), str(channel.id),
                str(interaction.user.id), interaction.user.display_name,
                panel.get('title', 'General'), self.panel_id, panel['title'], 
                'open', 'medium', json.dumps(form_data) if form_data else None, 
                datetime.utcnow()
            )
        
        # Process welcome message placeholders
        welcome_msg = panel.get('welcome_message', "Thank you for creating a ticket, {user.mention}. Our team will assist you shortly.")
        welcome_context = {
            'user': {
                'mention': interaction.user.mention,
                'name': interaction.user.name,
                'display_name': interaction.user.display_name,
                'id': interaction.user.id
            },
            'guild': {
                'name': interaction.guild.name,
                'member_count': interaction.guild.member_count
            },
            'ticket': {
                'id': ticket_id,
                'category': panel['title']
            }
        }
        
        processed_welcome = self.process_placeholders(welcome_msg, welcome_context)
        
        # Send welcome embed with controls - styled like the reference image  
        embed = discord.Embed(
            description=processed_welcome,
            color=0x5865F2  # Discord blue color like in the image
        )
        
        # Add form responses in a clean format like the reference
        form_display_text = ""
        
        # Add form responses in a clean list format like the reference
        if form_data:
            try:
                questions = json.loads(panel['form_questions'])
                form_display_text += "\n\n**Please list the following:**\n"
                for i, question in enumerate(questions):
                    if f'question_{i}' in form_data:
                        form_display_text += f"\n**{question.get('label', f'Question {i+1}')}**\n{form_data[f'question_{i}']}\n"
            except (json.JSONDecodeError, KeyError):
                pass
        
        if form_display_text:
            embed.description += form_display_text
        
        embed.set_footer(text=f"NexGuard | :nexguard: • Ticket ID: {ticket_id}")
        
        # Add ticket control buttons and send welcome embed
        view = TicketControlView(ticket_id)
        try:
            welcome_msg = await channel.send(f"{interaction.user.mention}", embed=embed, view=view)
            logger.info(f"✅ Welcome embed sent to ticket channel {channel.id}")
            
            # Pin the welcome message for easy access
            try:
                await welcome_msg.pin()
                logger.info(f"📌 Pinned welcome message in ticket {ticket_id}")
            except Exception as e:
                logger.warning(f"Could not pin welcome message: {e}")
                
        except Exception as e:
            logger.error(f"❌ Failed to send welcome embed to ticket channel: {e}")
            # Send a simple fallback message if embed fails
            try:
                await channel.send(f"{interaction.user.mention} Welcome to your ticket! Our team will assist you shortly.")
            except Exception as fallback_error:
                logger.error(f"❌ Even fallback message failed: {fallback_error}")
        
        # Ping support team if configured
        if panel.get('support_team_ids'):
            try:
                team_ids = json.loads(panel['support_team_ids'])
                mentions = []
                for role_id in team_ids:
                    role = interaction.guild.get_role(int(role_id))
                    if role:
                        mentions.append(role.mention)
                if mentions:
                    await channel.send(f"🔔 Support team: {' '.join(mentions)}", delete_after=5)
                    logger.info(f"Pinged support team: {', '.join([role.name for role in [interaction.guild.get_role(int(rid)) for rid in team_ids] if role])}")
            except Exception as e:
                logger.error(f"Error pinging support team: {e}")
        
        return channel
    
    async def get_ticket_count(self, interaction, db_pool):
        """Get current ticket count for ID generation"""
        try:
            async with db_pool.acquire() as conn:
                result = await conn.fetchval("""
                    SELECT COUNT(*) FROM tickets WHERE guild_id = $1
                """, str(interaction.guild.id))
                return result or 0
        except:
            return 0

class TicketFormModal(discord.ui.Modal):
    """Modal for collecting pre-ticket information"""
    def __init__(self, panel, panel_id: str):
        super().__init__(title=f"{panel['title']} - Information Required")
        self.panel = panel
        self.panel_id = panel_id
        
        # Parse form questions
        try:
            questions = json.loads(panel['form_questions']) if panel['form_questions'] else []
            
            for i, question in enumerate(questions[:5]):  # Discord limit
                # Process placeholder text and ensure it fits Discord's 100 char limit
                base_placeholder = self.process_placeholders(
                    question.get('placeholder', 'Your answer here...'),
                    {'user': {'mention': 'you'}}  # Sample for placeholder display
                )
                
                # Reserve space for the suffix and ensure total doesn't exceed 100 chars
                suffix = " (Shift+Enter for new lines)"
                max_base_length = 100 - len(suffix)
                if len(base_placeholder) > max_base_length:
                    base_placeholder = base_placeholder[:max_base_length-3] + "..."
                
                final_placeholder = base_placeholder + suffix
                
                field = discord.ui.TextInput(
                    label=question.get('label', f'Question {i+1}')[:45],  # Discord limit  
                    placeholder=final_placeholder,
                    required=question.get('required', True),
                    max_length=min(question.get('max_length', 2000), 4000),  # Discord limit
                    style=discord.TextStyle.paragraph  # Always multiline for Shift+Enter support
                )
                self.add_item(field)
                
        except (json.JSONDecodeError, KeyError):
            # Fallback single question
            field = discord.ui.TextInput(
                label="Please describe your issue",
                placeholder="Tell us how we can help you... (Shift+Enter for new lines)",
                required=True,
                max_length=2000,
                style=discord.TextStyle.paragraph
            )
            self.add_item(field)
    
    def process_placeholders(self, text: str, context: dict) -> str:
        """Process placeholder variables like {user.mention}"""
        if not text or not isinstance(text, str):
            return text or ""
            
        try:
            # Replace user placeholders
            if 'user' in context:
                user = context['user']
                text = text.replace('{user.mention}', user.get('mention', '@user'))
                text = text.replace('{user.name}', user.get('name', 'User'))
                text = text.replace('{user.display_name}', user.get('display_name', 'User'))
                text = text.replace('{user.id}', str(user.get('id', '000000')))
            
            # Replace guild placeholders
            if 'guild' in context:
                guild = context['guild']
                text = text.replace('{guild.name}', guild.get('name', 'Server'))
                text = text.replace('{guild.member_count}', str(guild.get('member_count', '0')))
            
            # Replace ticket placeholders
            if 'ticket' in context:
                ticket = context['ticket']
                text = text.replace('{ticket.id}', ticket.get('id', 'ticket-0000'))
                text = text.replace('{ticket.category}', ticket.get('category', 'General'))
                
        except Exception as e:
            logger.error(f"Error processing placeholders: {e}")
            
        return text
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Collect form responses
            form_data = {}
            for i, item in enumerate(self.children):
                if isinstance(item, discord.ui.TextInput):
                    form_data[f'question_{i}'] = item.value
            
            # Process form data placeholders
            processed_form_data = {}
            user_context = {
                'user': {
                    'mention': interaction.user.mention,
                    'name': interaction.user.name,
                    'display_name': interaction.user.display_name,
                    'id': interaction.user.id
                }
            }
            
            for key, value in form_data.items():
                processed_form_data[key] = self.process_placeholders(str(value), user_context)
            
            # Create ticket with processed form data
            button = TicketButton(self.panel_id, self.panel['title'])
            ticket_count = await button.get_ticket_count(interaction, interaction.client.db_pool)
            ticket_id = f"ticket-{ticket_count + 1:04d}"
            channel = await button.setup_ticket_channel(interaction, self.panel, ticket_id, processed_form_data)
            
            # Send only ephemeral success message (no public notification in panel channel)
            await interaction.response.send_message(
                f"✅ Ticket created with your information! Continue in {channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            await interaction.response.send_message("❌ Failed to create ticket.", ephemeral=True)

class TicketStaffView(discord.ui.View):
    """Staff management buttons for ticket notifications"""
    def __init__(self, ticket_id: str, channel_id: int):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
        self.channel_id = channel_id
    
    @discord.ui.button(label="Claim 🙌", style=discord.ButtonStyle.primary)
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check permissions
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You need Manage Messages permissions to claim tickets.", ephemeral=True)
            return
        
        # Get ticket channel
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Ticket channel not found.", ephemeral=True)
            return
        
        # Update database
        try:
            async with interaction.client.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE tickets SET 
                        claimed_by = $1, 
                        claimed_at = $2,
                        status = 'claimed'
                    WHERE ticket_id = $3 AND guild_id = $4
                """, str(interaction.user.id), datetime.utcnow(), self.ticket_id, str(interaction.guild.id))
            
            # Update embed to show claimed status
            if interaction.message.embeds:
                embed = interaction.message.embeds[0]
                embed.color = 0xffa500  # Orange for claimed
                embed.description = embed.description.replace("🎫 **New Ticket Created**", "🙌 **Ticket Claimed**")
                embed.add_field(name="Claimed by", value=interaction.user.mention, inline=True)
            
            # Disable claim button
            self.claim_ticket.disabled = True
            self.claim_ticket.label = f"Claimed by {interaction.user.display_name}"
            
            await interaction.response.edit_message(embed=embed, view=self)
            
            # Notify in ticket channel
            await channel.send(f"🙌 This ticket has been claimed by {interaction.user.mention}")
            
        except Exception as e:
            logger.error(f"Error claiming ticket: {e}")
            await interaction.response.send_message("❌ Failed to claim ticket.", ephemeral=True)
    
    @discord.ui.button(label="Close 🔒", style=discord.ButtonStyle.danger)
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check permissions
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You need Manage Messages permissions to close tickets.", ephemeral=True)
            return
        
        # Show close modal
        modal = CloseTicketModal(self.ticket_id)
        await interaction.response.send_modal(modal)


class TicketControlView(discord.ui.View):
    """Control buttons for managing tickets"""
    def __init__(self, ticket_id: str):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
    
    @discord.ui.button(label="Close", emoji="🔒", style=discord.ButtonStyle.secondary, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close ticket with feedback collection"""
        try:
            # Check permissions
            if not (interaction.user.guild_permissions.manage_channels or 
                   await self.is_ticket_owner(interaction) or 
                   await self.is_support_staff(interaction)):
                await interaction.response.send_message("❌ You don't have permission to close this ticket.", ephemeral=True)
                return
            
            modal = CloseTicketModal(self.ticket_id)
            await interaction.response.send_modal(modal)
            
        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
            await interaction.response.send_message("❌ Failed to close ticket.", ephemeral=True)
    
    @discord.ui.button(label="Claim", emoji="🙌", style=discord.ButtonStyle.secondary, custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Claim ticket for dedicated support"""
        try:
            # Check if user is support staff
            if not await self.is_support_staff(interaction):
                await interaction.response.send_message("❌ Only support staff can claim tickets.", ephemeral=True)
                return
            
            async with interaction.client.db_pool.acquire() as conn:
                # Check current claim status
                ticket = await conn.fetchrow("""
                    SELECT claimed_by, status FROM tickets 
                    WHERE ticket_id = $1 AND guild_id = $2
                """, self.ticket_id, str(interaction.guild.id))
                
                if not ticket:
                    await interaction.response.send_message("❌ Ticket not found.", ephemeral=True)
                    return
                
                if ticket['claimed_by']:
                    claimer = interaction.guild.get_member(int(ticket['claimed_by']))
                    name = claimer.display_name if claimer else "Unknown User"
                    await interaction.response.send_message(f"❌ Already claimed by {name}.", ephemeral=True)
                    return
                
                # Claim the ticket
                await conn.execute("""
                    UPDATE tickets 
                    SET claimed_by = $1, claimed_at = $2, status = 'claimed'
                    WHERE ticket_id = $3
                """, str(interaction.user.id), datetime.utcnow(), self.ticket_id)
                
                embed = discord.Embed(
                    description=f"🙌 **Ticket Claimed**\n\n{interaction.user.mention} has claimed this ticket and will provide dedicated support.",
                    color=0x5865F2
                )
                embed.set_footer(text="NexGuard | :nexguard: • You now have dedicated support!")
                
                await interaction.response.send_message(embed=embed)
                
        except Exception as e:
            logger.error(f"Error claiming ticket: {e}")
            await interaction.response.send_message("❌ Failed to claim ticket.", ephemeral=True)
    
    @discord.ui.button(label="Info", emoji="📋", style=discord.ButtonStyle.secondary, custom_id="ticket_info")
    async def ticket_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show ticket information"""
        try:
            async with interaction.client.db_pool.acquire() as conn:
                ticket = await conn.fetchrow("""
                    SELECT * FROM tickets 
                    WHERE ticket_id = $1 AND guild_id = $2
                """, self.ticket_id, str(interaction.guild.id))
                
                if not ticket:
                    await interaction.response.send_message("❌ Ticket not found.", ephemeral=True)
                    return
                
                embed = discord.Embed(
                    description=f"📋 **Ticket Information**\n\n**Ticket ID:** {self.ticket_id}",
                    color=0x5865F2
                )
                
                info_text = f"\n**Subject:** {ticket['subject']}"
                info_text += f"\n**Status:** {ticket['status'].title()}"
                info_text += f"\n**Priority:** {ticket['priority'].title()}" 
                info_text += f"\n**Created:** <t:{int(ticket['created_at'].timestamp())}:F>"
                
                if ticket['claimed_by']:
                    claimer = interaction.guild.get_member(int(ticket['claimed_by']))
                    info_text += f"\n**Claimed by:** {claimer.mention if claimer else 'Unknown User'}"
                
                embed.description += info_text
                embed.set_footer(text="NexGuard | :nexguard: • Ticket Information")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error showing ticket info: {e}")
            await interaction.response.send_message("❌ Failed to get ticket info.", ephemeral=True)
    
    async def is_ticket_owner(self, interaction: discord.Interaction) -> bool:
        """Check if user owns this ticket"""
        try:
            async with interaction.client.db_pool.acquire() as conn:
                result = await conn.fetchval("""
                    SELECT user_id FROM tickets 
                    WHERE ticket_id = $1 AND guild_id = $2
                """, self.ticket_id, str(interaction.guild.id))
                return result == str(interaction.user.id)
        except:
            return False
    
    async def is_support_staff(self, interaction: discord.Interaction) -> bool:
        """Check if user is support staff"""
        if interaction.user.guild_permissions.manage_channels:
            return True
        
        try:
            async with interaction.client.db_pool.acquire() as conn:
                # Get panel for this ticket
                ticket = await conn.fetchrow("""
                    SELECT panel_id FROM tickets 
                    WHERE ticket_id = $1 AND guild_id = $2
                """, self.ticket_id, str(interaction.guild.id))
                
                if not ticket:
                    return False
                
                # Get support team roles for this panel
                panel = await conn.fetchrow("""
                    SELECT support_team_ids FROM ticket_panels 
                    WHERE guild_id = $1 AND panel_id = $2
                """, str(interaction.guild.id), ticket['panel_id'])
                
                if panel and panel['support_team_ids']:
                    team_ids = json.loads(panel['support_team_ids'])
                    user_role_ids = [role.id for role in interaction.user.roles]
                    return any(int(role_id) in user_role_ids for role_id in team_ids)
                    
        except:
            pass
        
        return False

class CloseTicketModal(discord.ui.Modal):
    """Modal for closing tickets with transcript generation"""
    def __init__(self, ticket_id: str):
        super().__init__(title="Close Ticket")
        self.ticket_id = ticket_id
        
        self.reason = discord.ui.TextInput(
            label="Reason for closing (optional)",
            placeholder="Why is this ticket being closed? (Use Shift+Enter for new lines)",
            required=False,
            max_length=2000,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            
            # Generate transcript
            transcript_data = await self.generate_transcript(interaction.channel)
            
            # Get ticket info for user feedback
            async with interaction.client.db_pool.acquire() as conn:
                ticket = await conn.fetchrow("""
                    SELECT user_id FROM tickets 
                    WHERE ticket_id = $1 AND guild_id = $2
                """, self.ticket_id, str(interaction.guild.id))
                
                # Update ticket status with transcript
                await conn.execute("""
                    UPDATE tickets 
                    SET status = 'closed', closed_by = $1, closed_at = $2, 
                        close_reason = $3, transcript_url = $4
                    WHERE ticket_id = $5
                """, 
                    str(interaction.user.id), datetime.utcnow(),
                    self.reason.value or "No reason provided",
                    f"transcript_{self.ticket_id}", self.ticket_id
                )
                
                # Store transcript
                if transcript_data:
                    await conn.execute("""
                        INSERT INTO ticket_transcripts (ticket_id, guild_id, transcript_data, created_at)
                        VALUES ($1, $2, $3, $4)
                    """, self.ticket_id, str(interaction.guild.id), transcript_data, datetime.utcnow())
            
            # Send closing message
            embed = discord.Embed(
                description=f"🔒 **Ticket Closed**\n\nThis ticket has been closed by {interaction.user.mention}",
                color=0x5865F2
            )
            if self.reason.value:
                embed.description += f"\n\n**Reason:** {self.reason.value}"
            embed.set_footer(text="NexGuard | :nexguard: • This channel will be deleted in 30 seconds.")
            
            await interaction.followup.send(embed=embed)
            
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
            try:
                await interaction.channel.delete(reason="Ticket closed")
            except:
                pass  # Channel might already be deleted
                
        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
            await interaction.followup.send("❌ Failed to close ticket.", ephemeral=True)
    
    async def generate_transcript(self, channel) -> Optional[str]:
        """Generate transcript of ticket conversation"""
        try:
            messages = []
            async for message in channel.history(limit=1000, oldest_first=True):
                if not message.author.bot or message.embeds:  # Include bot messages with embeds
                    msg_data = {
                        'timestamp': message.created_at.isoformat(),
                        'author': message.author.display_name,
                        'author_id': str(message.author.id),
                        'content': message.content,
                        'attachments': [att.url for att in message.attachments],
                        'embeds': len(message.embeds) > 0
                    }
                    messages.append(msg_data)
            
            return json.dumps(messages, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating transcript: {e}")
            return None

class FeedbackView(discord.ui.View):
    """User feedback collection after ticket closure"""
    def __init__(self, ticket_id: str):
        super().__init__(timeout=300)  # 5 minutes
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
    """Modal for detailed feedback submission"""
    def __init__(self, ticket_id: str, rating: int):
        super().__init__(title=f"Feedback - {rating} Star{'s' if rating != 1 else ''}")
        self.ticket_id = ticket_id
        self.rating = rating
        
        self.comment = discord.ui.TextInput(
            label="Additional comments (optional)",
            placeholder="Tell us about your support experience... (Use Shift+Enter for new lines)",
            required=False,
            max_length=2000,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.comment)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Find the ticket (it might be in any guild the bot is in)
            bot = interaction.client
            if bot.db_pool:
                async with bot.db_pool.acquire() as conn:
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
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            await interaction.response.send_message("❌ Failed to submit feedback.", ephemeral=True)

class TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Ensure tables exist
        self.bot.loop.create_task(self.ensure_tables())
    
    async def ensure_tables(self):
        """Ensure all necessary tables exist"""
        if not self.bot.db_pool:
            return
            
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Create ticket_panels table if not exists
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS ticket_panels (
                        id SERIAL PRIMARY KEY,
                        guild_id TEXT NOT NULL,
                        panel_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        emoji TEXT,
                        category_id TEXT,
                        support_team_ids TEXT,
                        welcome_message TEXT DEFAULT 'Thank you for creating a ticket. Our team will assist you shortly.',
                        has_form BOOLEAN DEFAULT FALSE,
                        form_questions TEXT,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(guild_id, panel_id)
                    )
                """)
                
                # Create ticket_transcripts table if not exists
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS ticket_transcripts (
                        id SERIAL PRIMARY KEY,
                        ticket_id TEXT NOT NULL,
                        guild_id TEXT NOT NULL,
                        transcript_data TEXT NOT NULL,
                        message_count INTEGER DEFAULT 0,
                        participant_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Add new columns to tickets table if they don't exist
                columns_to_add = [
                    "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS claimed_by TEXT",
                    "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS claimed_at TIMESTAMP",
                    "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS panel_id TEXT",
                    "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS form_responses TEXT",
                    "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS transcript_url TEXT",
                    "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS close_reason TEXT",
                    "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS closed_by TEXT",
                    "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS feedback_at TIMESTAMP"
                ]
                
                for column_query in columns_to_add:
                    try:
                        await conn.execute(column_query)
                    except:
                        pass  # Column might already exist
                        
                logger.info("Ticket tables ensured")
                
        except Exception as e:
            logger.error(f"Error ensuring ticket tables: {e}")
    
    @app_commands.command(name="ticket-panel", description="Create and manage ticket panels - TicketsBot.net style")
    @app_commands.describe(
        action="Action to perform",
        name="Panel identifier (unique name for this panel)",
        title="Display title for the panel button",
        description="Description of what this panel is for", 
        category="Discord category to create tickets in",
        emoji="Emoji for the button (optional)",
        support_roles="Roles that handle tickets from this panel (comma-separated)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Create Panel", value="create"),
        app_commands.Choice(name="Edit Panel", value="edit"), 
        app_commands.Choice(name="Delete Panel", value="delete"),
        app_commands.Choice(name="List Panels", value="list"),
        app_commands.Choice(name="Deploy Panels", value="deploy")
    ])
    async def ticket_panel(
        self,
        interaction: discord.Interaction,
        action: str,
        name: str = None,
        title: str = None,
        description: str = None,
        category: discord.CategoryChannel = None,
        emoji: str = None,
        support_roles: str = None
    ):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need Manage Server permissions to use this command.", ephemeral=True)
            return
            
        # Immediate response to prevent timeout
        try:
            await interaction.response.send_message("⏳ Creating ticket panel...", ephemeral=True)
        except:
            return
        
        try:
            if action == "create":
                await self.create_panel(interaction, name, title, description, category, emoji, support_roles)
            elif action == "edit":
                await self.edit_panel(interaction, name, title, description, category, emoji, support_roles)
            elif action == "delete":
                await self.delete_panel(interaction, name)
            elif action == "list":
                await self.list_panels(interaction)
            elif action == "deploy":
                await self.deploy_panels(interaction)
                
        except Exception as e:
            logger.error(f"Error in ticket panel command: {e}")
            await interaction.edit_original_response(content="❌ An error occurred. Please try again.")
    
    async def create_panel(self, interaction, name, title, description, category, emoji, support_roles):
        if not name or not title:
            await interaction.edit_original_response(content="❌ Panel name and title are required.")
            return
        
        # Parse support roles - accept both names and mentions
        support_role_ids = []
        if support_roles:
            for role_ref in support_roles.split(','):
                role_ref = role_ref.strip()
                role = None
                
                # Check if it's a role mention (like <@&1234567890>)
                if role_ref.startswith('<@&') and role_ref.endswith('>'):
                    role_id = role_ref[3:-1]
                    try:
                        role = interaction.guild.get_role(int(role_id))
                    except ValueError:
                        pass
                # Check if it's a raw ID
                elif role_ref.isdigit():
                    try:
                        role = interaction.guild.get_role(int(role_ref))
                    except ValueError:
                        pass
                # Otherwise treat as role name
                else:
                    role = discord.utils.get(interaction.guild.roles, name=role_ref)
                
                if role:
                    support_role_ids.append(str(role.id))
                    logger.info(f"✅ Added support role to panel: {role.name} (ID: {role.id})")
                else:
                    logger.warning(f"❌ Could not find role: {role_ref}")
        
        logger.info(f"🔍 Final support role IDs for panel: {support_role_ids}")
        
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
                        is_active = TRUE,
                        updated_at = NOW()
                """,
                    str(interaction.guild.id), name.lower().replace(' ', '_'),
                    title, description or f"Support tickets for {title}",
                    str(category.id) if category else None,
                    emoji, json.dumps(support_role_ids) if support_role_ids else None,
                    True, datetime.utcnow()
                )
            
            embed = discord.Embed(
                title="✅ Ticket Panel Created",
                description=f"Panel `{name}` has been created successfully!",
                color=0x00ff00
            )
            embed.add_field(name="Title", value=title, inline=False)
            embed.add_field(name="Panel ID", value=name, inline=True)
            if description:
                embed.add_field(name="Description", value=description[:1000], inline=False)
            if category:
                embed.add_field(name="Category", value=category.mention, inline=True)
            if support_role_ids:
                role_names = []
                for rid in support_role_ids:
                    role = interaction.guild.get_role(int(rid))
                    if role:
                        role_names.append(role.name)
                if role_names:
                    embed.add_field(name="Support Team", value=", ".join(role_names), inline=True)
            embed.add_field(
                name="Next Step", 
                value="Use `/ticket-panel deploy` to deploy all panels to a channel", 
                inline=False
            )
            
            await interaction.edit_original_response(content="✅ Panel created! Use `/ticket-panel deploy` to deploy it.")
            
        except Exception as e:
            logger.error(f"Error creating panel: {e}")
            await interaction.edit_original_response(content="❌ Failed to create panel.")
    
    async def edit_panel(self, interaction, name, title, description, category, emoji, support_roles):
        if not name:
            await interaction.edit_original_response(content="❌ Panel name is required for editing.")
            return
        
        # Parse support roles - accept both names and mentions
        support_role_ids = []
        if support_roles:
            for role_ref in support_roles.split(','):
                role_ref = role_ref.strip()
                role = None
                
                # Check if it's a role mention (like <@&1234567890>)
                if role_ref.startswith('<@&') and role_ref.endswith('>'):
                    role_id = role_ref[3:-1]
                    try:
                        role = interaction.guild.get_role(int(role_id))
                    except ValueError:
                        pass
                # Check if it's a raw ID
                elif role_ref.isdigit():
                    try:
                        role = interaction.guild.get_role(int(role_ref))
                    except ValueError:
                        pass
                # Otherwise treat as role name
                else:
                    role = discord.utils.get(interaction.guild.roles, name=role_ref)
                
                if role:
                    support_role_ids.append(str(role.id))
                    logger.info(f"✅ Added support role to panel: {role.name} (ID: {role.id})")
                else:
                    logger.warning(f"❌ Could not find role: {role_ref}")
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Check if panel exists
                existing = await conn.fetchrow("""
                    SELECT * FROM ticket_panels 
                    WHERE guild_id = $1 AND panel_id = $2 AND is_active = TRUE
                """, str(interaction.guild.id), name.lower().replace(' ', '_'))
                
                if not existing:
                    await interaction.edit_original_response(content=f"❌ Panel `{name}` not found.")
                    return
                
                # Update panel
                await conn.execute("""
                    UPDATE ticket_panels SET
                        title = COALESCE($3, title),
                        description = COALESCE($4, description),
                        category_id = COALESCE($5, category_id),
                        emoji = COALESCE($6, emoji),
                        support_team_ids = COALESCE($7, support_team_ids),
                        updated_at = NOW()
                    WHERE guild_id = $1 AND panel_id = $2
                """,
                    str(interaction.guild.id), name.lower().replace(' ', '_'),
                    title, description, str(category.id) if category else None,
                    emoji, json.dumps(support_role_ids) if support_role_ids else None
                )
            
            embed = discord.Embed(
                title="✅ Ticket Panel Updated",
                description=f"Panel `{name}` has been updated successfully!",
                color=0x00ff00
            )
            if title:
                embed.add_field(name="New Title", value=title, inline=False)
            if description:
                embed.add_field(name="New Description", value=description[:1000], inline=False)
            if category:
                embed.add_field(name="New Category", value=category.mention, inline=True)
            if support_role_ids:
                role_names = []
                for rid in support_role_ids:
                    role = interaction.guild.get_role(int(rid))
                    if role:
                        role_names.append(role.name)
                if role_names:
                    embed.add_field(name="Support Team", value=", ".join(role_names), inline=True)
            
            await interaction.edit_original_response(content="✅ Panel updated!", embed=embed)
            
        except Exception as e:
            logger.error(f"Error editing panel: {e}")
            await interaction.edit_original_response(content="❌ Failed to edit panel.")
    
    async def list_panels(self, interaction):
        try:
            async with self.bot.db_pool.acquire() as conn:
                panels = await conn.fetch("""
                    SELECT * FROM ticket_panels 
                    WHERE guild_id = $1 AND is_active = TRUE
                    ORDER BY created_at DESC
                """, str(interaction.guild.id))
            
            if not panels:
                await interaction.followup.send("📋 No ticket panels found. Create one with `/ticket-panel create`.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🎫 Ticket Panels",
                description=f"Found {len(panels)} active panel(s)",
                color=0x00ff00
            )
            
            for panel in panels:
                value_parts = [f"**Title:** {panel['title']}"]
                if panel['description']:
                    value_parts.append(f"**Description:** {panel['description']}")
                if panel['category_id']:
                    category = interaction.guild.get_channel(int(panel['category_id']))
                    if category:
                        value_parts.append(f"**Category:** {category.mention}")
                if panel['support_team_ids']:
                    try:
                        team_ids = json.loads(panel['support_team_ids'])
                        roles = [interaction.guild.get_role(int(rid)) for rid in team_ids]
                        valid_roles = [f"<@&{r.id}>" for r in roles if r]
                        if valid_roles:
                            value_parts.append(f"**Support Team:** {' '.join(valid_roles)}")
                    except:
                        pass
                
                embed.add_field(
                    name=f"{panel['emoji'] or '🎫'} {panel['panel_id']}",
                    value="\n".join(value_parts),
                    inline=False
                )
            
            embed.set_footer(text="Use `/ticket-panel deploy` to deploy panels to a channel")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing panels: {e}")
            await interaction.followup.send("❌ Failed to list panels.", ephemeral=True)
    
    async def deploy_panels(self, interaction):
        try:
            async with self.bot.db_pool.acquire() as conn:
                panels = await conn.fetch("""
                    SELECT * FROM ticket_panels 
                    WHERE guild_id = $1 AND is_active = TRUE
                    ORDER BY created_at ASC
                """, str(interaction.guild.id))
            
            if not panels:
                await interaction.followup.send("❌ No ticket panels to deploy. Create one first.", ephemeral=True)
                return
            
            # Convert to list of dicts for the view
            panel_data = []
            for panel in panels:
                panel_data.append({
                    'panel_id': panel['panel_id'],
                    'title': panel['title'],
                    'emoji': panel['emoji']
                })
            
            # Create separate embed for each panel matching the reference image
            for panel in panels:
                embed = discord.Embed(
                    title=f"Please open a {panel['title']} Today!",
                    description=f"Please click on the button below to create a {panel['title']}",
                    color=0x2F3136  # Dark gray like in the reference image
                )
            
                # Create individual view for this panel
                view = TicketPanelView([{
                    'panel_id': panel['panel_id'],
                    'title': panel['title'],
                    'emoji': '📄'  # Document icon like in the reference
                }])
                
                # Send this panel
                await interaction.followup.send(embed=embed, view=view)
            
            # Send success message
            await interaction.followup.send(
                f"✅ Deployed {len(panels)} ticket panel(s)! Users can now create tickets using the buttons above.",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error deploying panels: {e}")
            await interaction.followup.send("❌ Failed to deploy panels.", ephemeral=True)
    
    async def delete_panel(self, interaction, name):
        if not name:
            await interaction.followup.send("❌ Panel name is required.", ephemeral=True)
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                result = await conn.execute("""
                    UPDATE ticket_panels 
                    SET is_active = FALSE 
                    WHERE guild_id = $1 AND panel_id = $2
                """, str(interaction.guild.id), name.lower().replace(' ', '_'))
            
            if result == "UPDATE 1":
                await interaction.followup.send(f"✅ Panel `{name}` has been deleted.", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Panel `{name}` not found.", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error deleting panel: {e}")
            await interaction.followup.send("❌ Failed to delete panel.", ephemeral=True)
    
    @app_commands.command(name="ticket-form", description="Create custom forms for ticket panels")
    @app_commands.describe(
        panel_name="Name of the panel to add the form to",
        form_title="Title shown to users when filling the form",
        questions="Questions separated by semicolons (e.g., 'RP Name;Age;Experience')"
    )
    async def ticket_form(
        self,
        interaction: discord.Interaction,
        panel_name: str,
        form_title: str,
        questions: str
    ):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need Manage Server permissions to use this command.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        try:
            # Parse questions
            question_list = [q.strip() for q in questions.split(';') if q.strip()]
            
            if not question_list:
                await interaction.followup.send("❌ Please provide at least one question.", ephemeral=True)
                return
            
            # Format questions for database storage
            form_questions = []
            for question in question_list:
                form_questions.append({
                    'label': question,
                    'placeholder': f'Please provide your {question.lower()}... (Shift+Enter for new line)',
                    'required': True,
                    'multiline': True,
                    'max_length': 1000
                })
            
            async with self.bot.db_pool.acquire() as conn:
                # Update panel with form
                result = await conn.execute("""
                    UPDATE ticket_panels 
                    SET has_form = TRUE, 
                        form_questions = $1,
                        updated_at = NOW()
                    WHERE guild_id = $2 AND panel_id = $3 AND is_active = TRUE
                """, json.dumps(form_questions), str(interaction.guild.id), panel_name.lower().replace(' ', '_'))
                
                if result == "UPDATE 1":
                    embed = discord.Embed(
                        description=f"✅ **Form Created Successfully**\n\nForm has been added to panel `{panel_name}` with {len(question_list)} questions.",
                        color=0x5865F2
                    )
                    
                    questions_text = ""
                    for i, question in enumerate(question_list, 1):
                        questions_text += f"\n**{i}.** {question}"
                    
                    embed.description += f"\n\n**Questions:{questions_text}"
                    embed.set_footer(text="NexGuard | :nexguard: • Form will be shown when users create tickets from this panel")
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f"❌ Panel `{panel_name}` not found.", ephemeral=True)
                    
        except Exception as e:
            logger.error(f"Error creating ticket form: {e}")
            await interaction.followup.send("❌ Failed to create form.", ephemeral=True)
    
    @app_commands.command(name="ticket-stats", description="View ticket statistics and analytics")
    @app_commands.describe(
        timeframe="Time period to analyze"
    )
    @app_commands.choices(timeframe=[
        app_commands.Choice(name="Last 7 days", value="7d"),
        app_commands.Choice(name="Last 30 days", value="30d"), 
        app_commands.Choice(name="All time", value="all")
    ])
    async def ticket_stats(self, interaction: discord.Interaction, timeframe: str = "30d"):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need Manage Server permissions to use this command.", ephemeral=True)
            return
            
        await interaction.response.send_message("⏳ Generating ticket statistics...", ephemeral=True)
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Base stats
                total_tickets = await conn.fetchval("""
                    SELECT COUNT(*) FROM tickets WHERE guild_id = $1
                """, str(interaction.guild.id))
                
                open_tickets = await conn.fetchval("""
                    SELECT COUNT(*) FROM tickets 
                    WHERE guild_id = $1 AND status IN ('open', 'claimed', 'in-progress')
                """, str(interaction.guild.id))
                
                closed_tickets = await conn.fetchval("""
                    SELECT COUNT(*) FROM tickets 
                    WHERE guild_id = $1 AND status = 'closed'
                """, str(interaction.guild.id))
                
                # Skip satisfaction stats - column doesn't exist yet
                avg_satisfaction = None
                
                # Panel breakdown
                panel_stats = await conn.fetch("""
                    SELECT panel_id, COUNT(*) as count
                    FROM tickets 
                    WHERE guild_id = $1 
                    GROUP BY panel_id 
                    ORDER BY count DESC
                """, str(interaction.guild.id))
                
                embed = discord.Embed(
                    title="📊 Ticket Statistics",
                    color=0x00ff00
                )
                
                embed.add_field(name="📈 Total Tickets", value=str(total_tickets or 0), inline=True)
                embed.add_field(name="🟢 Open Tickets", value=str(open_tickets or 0), inline=True)  
                embed.add_field(name="🔴 Closed Tickets", value=str(closed_tickets or 0), inline=True)
                
                # Skip satisfaction display for now
                embed.add_field(name="💯 Average Rating", value="Not available", inline=True)
                
                if total_tickets and closed_tickets:
                    resolution_rate = (closed_tickets / total_tickets) * 100
                    embed.add_field(name="✅ Resolution Rate", value=f"{resolution_rate:.1f}%", inline=True)
                
                # Panel breakdown
                if panel_stats:
                    panel_text = []
                    for panel in panel_stats[:5]:  # Top 5 panels
                        panel_text.append(f"• {panel['panel_id']}: {panel['count']} tickets")
                    embed.add_field(
                        name="📋 Top Panels", 
                        value="\n".join(panel_text) or "No data",
                        inline=False
                    )
                
                embed.set_footer(text="NexGuard | :nexguard: • Ticket Analytics")
                embed.timestamp = datetime.utcnow()
                
                await interaction.edit_original_response(content="📊 **Ticket Statistics**", embed=embed)
                
        except Exception as e:
            logger.error(f"Error getting ticket stats: {e}")
            await interaction.edit_original_response(content="❌ Failed to get ticket statistics.")

async def setup(bot):
    await bot.add_cog(TicketCommands(bot))
    logger.info("TicketsBot.net-style ticket system loaded")
    
    async def get_ticket_categories(self, guild_id: str):
        """Get all ticket categories for a guild"""
        if not self.bot.db_pool:
            return []
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                categories = await conn.fetch("""
                    SELECT * FROM ticket_categories 
                    WHERE guild_id = $1 AND is_active = TRUE
                    ORDER BY category_name
                """, guild_id)
                return categories
        except Exception as e:
            logger.error(f"Error getting ticket categories: {e}")
            return []
    
    async def create_ticket_category(self, guild_id: str, category_name: str, category_id: str, description: str = None):
        """Create a new ticket category"""
        if not self.bot.db_pool:
            return False
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO ticket_categories (guild_id, category_name, category_id, description)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (guild_id, category_name) DO UPDATE SET
                        category_id = EXCLUDED.category_id,
                        description = EXCLUDED.description,
                        is_active = TRUE
                """, guild_id, category_name, category_id, description)
                return True
        except Exception as e:
            logger.error(f"Error creating ticket category: {e}")
            return False
    
    @app_commands.command(name="ticket", description="Create a support ticket")
    @app_commands.describe(
        subject="Subject of the ticket",
        description="Detailed description of the issue",
        category="Category of the ticket",
        priority="Priority level",
        ticket_category="Discord category to create the ticket in"
    )
    @app_commands.choices(
        category=[
            app_commands.Choice(name="General Support", value="general"),
            app_commands.Choice(name="Technical Issue", value="technical"),
            app_commands.Choice(name="Bug Report", value="bug"),
            app_commands.Choice(name="Feature Request", value="feature"),
            app_commands.Choice(name="Account Issue", value="account"),
            app_commands.Choice(name="Billing Issue", value="billing"),
            app_commands.Choice(name="Partnership", value="partnership"),
            app_commands.Choice(name="Other", value="other")
        ],
        priority=[
            app_commands.Choice(name="Low", value="low"),
            app_commands.Choice(name="Medium", value="medium"),
            app_commands.Choice(name="High", value="high"),
            app_commands.Choice(name="Urgent", value="urgent")
        ]
    )
    async def ticket(self, interaction: discord.Interaction, subject: str, description: str, category: str = "general", priority: str = "medium", ticket_category: discord.CategoryChannel = None):
        """Create a support ticket"""
        try:
            # Generate unique ticket ID
            ticket_id = str(uuid.uuid4())[:8]
            
            # Create ticket channel
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            # Add staff role permissions if configured
            config = await self.bot.get_guild_config(str(interaction.guild.id))
            if config.get('mod_role_id'):
                try:
                    mod_role = interaction.guild.get_role(int(config['mod_role_id']))
                    if mod_role:
                        overwrites[mod_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                except:
                    pass
            
            # Determine the Discord category to create the ticket in
            target_category = None
            if ticket_category:
                target_category = ticket_category
            else:
                # Try to find a category based on the ticket category type
                categories = await self.get_ticket_categories(str(interaction.guild.id))
                for cat in categories:
                    if cat['category_name'].lower() == category.lower():
                        target_category = interaction.guild.get_channel(int(cat['category_id']))
                        break
            
            # Create the channel with appropriate naming
            channel_name = f"{category}-{ticket_id}"
            if target_category:
                channel_name = f"{target_category.name.lower()}-{ticket_id}"
            
            channel = await interaction.guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                category=target_category,
                reason=f"Support ticket created by {interaction.user.name}"
            )
            
            # Store ticket in database
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO tickets (ticket_id, guild_id, channel_id, discord_category_id, user_id, username, category, subject, description, priority, status)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    """, ticket_id, str(interaction.guild.id), str(channel.id), str(target_category.id) if target_category else None,
                    str(interaction.user.id), interaction.user.name, category, subject, description, priority, "open")
            
            # Create ticket embed
            embed = discord.Embed(
                title=f"🎫 Support Ticket - {ticket_id}",
                description=f"**Subject:** {subject}\n**Description:** {description}",
                color=0x00FFFF,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Category", value=category.title(), inline=True)
            embed.add_field(name="Priority", value=priority.title(), inline=True)
            embed.add_field(name="Status", value="Open", inline=True)
            
            embed.add_field(name="Created by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Created at", value=discord.utils.format_dt(datetime.utcnow(), "F"), inline=True)
            embed.add_field(name="Ticket ID", value=ticket_id, inline=True)
            
            if target_category:
                embed.add_field(name="Category Location", value=target_category.name, inline=True)
            
            embed.set_footer(text="Support staff will be with you shortly. Please provide any additional information that might help.")
            
            # Send embed to ticket channel
            await channel.send(f"{interaction.user.mention}", embed=embed)
            
            # Send confirmation to user
            category_info = f" in {target_category.name}" if target_category else ""
            await interaction.response.send_message(
                f"✅ Support ticket created{category_info}! Please check {channel.mention} for further assistance.",
                ephemeral=True
            )
            
            logger.info(f"Created ticket {ticket_id} for user {interaction.user.name} in guild {interaction.guild.name}")
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await interaction.response.send_message("❌ Failed to create ticket. Please try again.", ephemeral=True)
    
    @app_commands.command(name="ticketinfo", description="Get information about a ticket")
    @app_commands.describe(ticket_id="The ID of the ticket to get information about")
    async def ticketinfo(self, interaction: discord.Interaction, ticket_id: str):
        """Get information about a ticket"""
        try:
            if not self.bot.db_pool:
                await interaction.response.send_message("❌ Database not available.", ephemeral=True)
                return
            
            async with self.bot.db_pool.acquire() as conn:
                ticket = await conn.fetchrow("""
                    SELECT * FROM tickets WHERE ticket_id = $1 AND guild_id = $2
                """, ticket_id, str(interaction.guild.id))
                
                if not ticket:
                    await interaction.response.send_message("❌ Ticket not found.", ephemeral=True)
                    return
                
                embed = discord.Embed(
                    title=f"🎫 Ticket Information - {ticket_id}",
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(name="Subject", value=ticket['subject'], inline=False)
                embed.add_field(name="Description", value=ticket['description'] or "No description", inline=False)
                
                embed.add_field(name="Category", value=ticket['category'].title(), inline=True)
                embed.add_field(name="Priority", value=ticket['priority'].title(), inline=True)
                embed.add_field(name="Status", value=ticket['status'].title(), inline=True)
                
                embed.add_field(name="Created by", value=f"<@{ticket['user_id']}>", inline=True)
                embed.add_field(name="Created at", value=discord.utils.format_dt(ticket['created_at'], "F"), inline=True)
                
                if ticket['assigned_to']:
                    embed.add_field(name="Assigned to", value=f"<@{ticket['assigned_to']}>", inline=True)
                
                if ticket['closed_at']:
                    embed.add_field(name="Closed at", value=discord.utils.format_dt(ticket['closed_at'], "F"), inline=True)
                
                channel = self.bot.get_channel(int(ticket['channel_id']))
                if channel:
                    embed.add_field(name="Channel", value=channel.mention, inline=True)
                
                await interaction.response.send_message(embed=embed)
                
        except Exception as e:
            logger.error(f"Error getting ticket info: {e}")
            await interaction.response.send_message("❌ Failed to get ticket information.", ephemeral=True)
    
    @app_commands.command(name="ticketmanage", description="Manage tickets (staff only)")
    @app_commands.describe(
        action="Action to perform",
        ticket_id="The ID of the ticket",
        user="User to assign ticket to (for assign action)",
        reason="Reason for the action"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Close", value="close"),
        app_commands.Choice(name="Assign", value="assign"),
        app_commands.Choice(name="Escalate", value="escalate"),
        app_commands.Choice(name="Archive", value="archive")
    ])
    async def ticketmanage(self, interaction: discord.Interaction, action: str, ticket_id: str, user: discord.Member = None, reason: str = None):
        """Manage tickets (staff only)"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You don't have permission to manage tickets.", ephemeral=True)
            return
        
        try:
            if not self.bot.db_pool:
                await interaction.response.send_message("❌ Database not available.", ephemeral=True)
                return
            
            async with self.bot.db_pool.acquire() as conn:
                ticket = await conn.fetchrow("""
                    SELECT * FROM tickets WHERE ticket_id = $1 AND guild_id = $2
                """, ticket_id, str(interaction.guild.id))
                
                if not ticket:
                    await interaction.response.send_message("❌ Ticket not found.", ephemeral=True)
                    return
                
                if action == "close":
                    # Close the ticket
                    await conn.execute("""
                        UPDATE tickets SET status = 'closed', closed_at = $1, updated_at = $2
                        WHERE ticket_id = $3 AND guild_id = $4
                    """, datetime.utcnow(), datetime.utcnow(), ticket_id, str(interaction.guild.id))
                    
                    # Archive the channel
                    channel = self.bot.get_channel(int(ticket['channel_id']))
                    if channel:
                        await channel.edit(name=f"closed-{ticket_id}")
                        
                        embed = discord.Embed(
                            title="🔒 Ticket Closed",
                            description=f"This ticket has been closed by {interaction.user.mention}.",
                            color=0xFF0000,
                            timestamp=datetime.utcnow()
                        )
                        
                        if reason:
                            embed.add_field(name="Reason", value=reason, inline=False)
                        
                        embed.add_field(name="Closed by", value=interaction.user.mention, inline=True)
                        embed.add_field(name="Closed at", value=discord.utils.format_dt(datetime.utcnow(), "F"), inline=True)
                        
                        await channel.send(embed=embed)
                    
                    await interaction.response.send_message(f"✅ Ticket {ticket_id} has been closed.", ephemeral=True)
                    
                elif action == "assign":
                    if not user:
                        await interaction.response.send_message("❌ Please specify a user to assign the ticket to.", ephemeral=True)
                        return
                    
                    # Assign the ticket
                    await conn.execute("""
                        UPDATE tickets SET assigned_to = $1, assigned_by = $2, updated_at = $3
                        WHERE ticket_id = $4 AND guild_id = $5
                    """, str(user.id), str(interaction.user.id), datetime.utcnow(), ticket_id, str(interaction.guild.id))
                    
                    # Add user to channel permissions
                    channel = self.bot.get_channel(int(ticket['channel_id']))
                    if channel:
                        await channel.set_permissions(user, read_messages=True, send_messages=True)
                        
                        embed = discord.Embed(
                            title="👤 Ticket Assigned",
                            description=f"This ticket has been assigned to {user.mention}.",
                            color=0x00FF00,
                            timestamp=datetime.utcnow()
                        )
                        
                        embed.add_field(name="Assigned by", value=interaction.user.mention, inline=True)
                        embed.add_field(name="Assigned at", value=discord.utils.format_dt(datetime.utcnow(), "F"), inline=True)
                        
                        await channel.send(f"{user.mention}", embed=embed)
                    
                    await interaction.response.send_message(f"✅ Ticket {ticket_id} has been assigned to {user.mention}.", ephemeral=True)
                    
                elif action == "escalate":
                    # Escalate the ticket
                    new_escalation = (ticket.get('escalation_level', 0) or 0) + 1
                    await conn.execute("""
                        UPDATE tickets SET escalation_level = $1, updated_at = $2
                        WHERE ticket_id = $3 AND guild_id = $4
                    """, new_escalation, datetime.utcnow(), ticket_id, str(interaction.guild.id))
                    
                    channel = self.bot.get_channel(int(ticket['channel_id']))
                    if channel:
                        embed = discord.Embed(
                            title="⚠️ Ticket Escalated",
                            description=f"This ticket has been escalated to level {new_escalation}.",
                            color=0xFFFF00,
                            timestamp=datetime.utcnow()
                        )
                        
                        embed.add_field(name="Escalated by", value=interaction.user.mention, inline=True)
                        embed.add_field(name="Escalation Level", value=f"Level {new_escalation}", inline=True)
                        
                        if reason:
                            embed.add_field(name="Reason", value=reason, inline=False)
                        
                        await channel.send(embed=embed)
                    
                    await interaction.response.send_message(f"✅ Ticket {ticket_id} has been escalated to level {new_escalation}.", ephemeral=True)
                    
                elif action == "archive":
                    # Archive the ticket
                    await conn.execute("""
                        UPDATE tickets SET is_archived = TRUE, updated_at = $1
                        WHERE ticket_id = $2 AND guild_id = $3
                    """, datetime.utcnow(), ticket_id, str(interaction.guild.id))
                    
                    # Delete the channel
                    channel = self.bot.get_channel(int(ticket['channel_id']))
                    if channel:
                        await channel.delete(reason=f"Ticket {ticket_id} archived by {interaction.user.name}")
                    
                    await interaction.response.send_message(f"✅ Ticket {ticket_id} has been archived and the channel deleted.", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error managing ticket: {e}")
            await interaction.response.send_message("❌ Failed to manage ticket. Please try again.", ephemeral=True)

    @app_commands.command(name="ticketcategory", description="Manage ticket categories (Admin only)")
    @app_commands.describe(
        action="Action to perform",
        category_name="Name of the ticket category",
        discord_category="Discord category channel",
        description="Description of the ticket category"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove"),
        app_commands.Choice(name="List", value="list"),
        app_commands.Choice(name="Update", value="update")
    ])
    async def ticketcategory(self, interaction: discord.Interaction, action: str, category_name: str = None, discord_category: discord.CategoryChannel = None, description: str = None):
        """Manage ticket categories (Admin only)"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to manage ticket categories.", ephemeral=True)
            return
        
        try:
            guild_id = str(interaction.guild.id)
            
            if action == "add":
                if not category_name or not discord_category:
                    await interaction.response.send_message("❌ Please provide both category name and Discord category.", ephemeral=True)
                    return
                
                success = await self.create_ticket_category(guild_id, category_name, str(discord_category.id), description)
                if success:
                    await interaction.response.send_message(f"✅ Ticket category '{category_name}' added for {discord_category.mention}.", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Failed to add ticket category.", ephemeral=True)
            
            elif action == "remove":
                if not category_name:
                    await interaction.response.send_message("❌ Please provide a category name to remove.", ephemeral=True)
                    return
                
                if self.bot.db_pool:
                    async with self.bot.db_pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE ticket_categories SET is_active = FALSE
                            WHERE guild_id = $1 AND category_name = $2
                        """, guild_id, category_name)
                        await interaction.response.send_message(f"✅ Ticket category '{category_name}' removed.", ephemeral=True)
            
            elif action == "list":
                categories = await self.get_ticket_categories(guild_id)
                if not categories:
                    await interaction.response.send_message("❌ No ticket categories configured.", ephemeral=True)
                    return
                
                embed = discord.Embed(
                    title="🎫 Ticket Categories",
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                
                for category in categories:
                    discord_cat = interaction.guild.get_channel(int(category['category_id']))
                    cat_name = discord_cat.name if discord_cat else "Unknown Category"
                    
                    embed.add_field(
                        name=f"📁 {category['category_name']}",
                        value=f"**Discord Category:** {cat_name}\n**Description:** {category['description'] or 'No description'}\n**Created:** {discord.utils.format_dt(category['created_at'], 'R')}",
                        inline=False
                    )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            elif action == "update":
                if not category_name:
                    await interaction.response.send_message("❌ Please provide a category name to update.", ephemeral=True)
                    return
                
                if self.bot.db_pool:
                    async with self.bot.db_pool.acquire() as conn:
                        update_fields = []
                        params = [guild_id, category_name]
                        param_count = 2
                        
                        if discord_category:
                            param_count += 1
                            update_fields.append(f"category_id = ${param_count}")
                            params.append(str(discord_category.id))
                        
                        if description:
                            param_count += 1
                            update_fields.append(f"description = ${param_count}")
                            params.append(description)
                        
                        if update_fields:
                            query = f"""
                                UPDATE ticket_categories SET {', '.join(update_fields)}
                                WHERE guild_id = $1 AND category_name = $2
                            """
                            await conn.execute(query, *params)
                            await interaction.response.send_message(f"✅ Ticket category '{category_name}' updated.", ephemeral=True)
                        else:
                            await interaction.response.send_message("❌ No fields to update.", ephemeral=True)
                            
        except Exception as e:
            logger.error(f"Error managing ticket categories: {e}")
            await interaction.response.send_message("❌ Failed to manage ticket categories.", ephemeral=True)

    @app_commands.command(name="tickets", description="List all tickets with filtering options")
    @app_commands.describe(
        status="Filter by status",
        category="Filter by category",
        user="Filter by user",
        show_closed="Show closed tickets"
    )
    @app_commands.choices(
        status=[
            app_commands.Choice(name="Open", value="open"),
            app_commands.Choice(name="In Progress", value="in-progress"),
            app_commands.Choice(name="Pending", value="pending"),
            app_commands.Choice(name="Resolved", value="resolved"),
            app_commands.Choice(name="Closed", value="closed")
        ],
        category=[
            app_commands.Choice(name="General Support", value="general"),
            app_commands.Choice(name="Technical Issue", value="technical"),
            app_commands.Choice(name="Bug Report", value="bug"),
            app_commands.Choice(name="Feature Request", value="feature"),
            app_commands.Choice(name="Account Issue", value="account"),
            app_commands.Choice(name="Billing Issue", value="billing"),
            app_commands.Choice(name="Partnership", value="partnership"),
            app_commands.Choice(name="Other", value="other")
        ]
    )
    async def tickets(self, interaction: discord.Interaction, status: str = None, category: str = None, user: discord.Member = None, show_closed: bool = False):
        """List all tickets with filtering options"""
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You need Manage Channels permission to view tickets.", ephemeral=True)
            return
        
        try:
            if not self.bot.db_pool:
                await interaction.response.send_message("❌ Database not available.", ephemeral=True)
                return
            
            # Build query with filters
            query = "SELECT * FROM tickets WHERE guild_id = $1"
            params = [str(interaction.guild.id)]
            param_count = 1
            
            if status:
                param_count += 1
                query += f" AND status = ${param_count}"
                params.append(status)
            
            if category:
                param_count += 1
                query += f" AND category = ${param_count}"
                params.append(category)
            
            if user:
                param_count += 1
                query += f" AND user_id = ${param_count}"
                params.append(str(user.id))
            
            if not show_closed:
                query += " AND status != 'closed'"
            
            query += " ORDER BY created_at DESC LIMIT 10"
            
            async with self.bot.db_pool.acquire() as conn:
                tickets = await conn.fetch(query, *params)
                
                if not tickets:
                    await interaction.response.send_message("❌ No tickets found matching your criteria.", ephemeral=True)
                    return
                
                embed = discord.Embed(
                    title="🎫 Tickets Overview",
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                
                for ticket in tickets:
                    status_emoji = {
                        "open": "🔓",
                        "in-progress": "⏳",
                        "pending": "⏸️",
                        "resolved": "✅",
                        "closed": "🔒"
                    }.get(ticket['status'], "❓")
                    
                    priority_emoji = {
                        "low": "🟢",
                        "medium": "🟡",
                        "high": "🟠",
                        "urgent": "🔴"
                    }.get(ticket['priority'], "⚪")
                    
                    channel = self.bot.get_channel(int(ticket['channel_id']))
                    channel_info = channel.mention if channel else "Channel Deleted"
                    
                    embed.add_field(
                        name=f"{status_emoji} {ticket['ticket_id']} - {ticket['subject']}",
                        value=f"**User:** <@{ticket['user_id']}>\n**Category:** {ticket['category'].title()}\n**Priority:** {priority_emoji} {ticket['priority'].title()}\n**Status:** {ticket['status'].title()}\n**Channel:** {channel_info}\n**Created:** {discord.utils.format_dt(ticket['created_at'], 'R')}",
                        inline=False
                    )
                
                embed.set_footer(text=f"Showing {len(tickets)} tickets")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error listing tickets: {e}")
            await interaction.response.send_message("❌ Failed to list tickets.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketCommands(bot))