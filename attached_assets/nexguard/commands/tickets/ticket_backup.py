import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        
    @discord.ui.button(label='📩 Create Ticket', style=discord.ButtonStyle.primary, custom_id='create_ticket')
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal(self.bot))

class TicketSetupView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.selected_roles = []
        self.config = {
            'title': '🎫 Support Ticket System',
            'description': 'Welcome to our support ticket system! Click the button below to create a new support ticket.',
            'support_hours': 'Monday - Friday: 9 AM - 6 PM',
            'response_time': 'Within 24 hours'
        }
        
    @discord.ui.button(label='📝 Configure Text', style=discord.ButtonStyle.primary, row=0)
    async def configure_text(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketSetupModal(self.bot, self))
    
    @discord.ui.button(label='👥 Select Roles', style=discord.ButtonStyle.secondary, row=0)
    async def select_roles_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Create a new view for role selection
        role_view = RoleSelectionView(self.bot, self)
        
        # Get ALL roles in the guild (including @everyone if desired, but excluding it for practical reasons)
        all_roles = [role for role in interaction.guild.roles if not role.is_default()]
        
        if not all_roles:
            embed = discord.Embed(
                title="❌ No Roles Available",
                description="This server has no roles available for selection.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Sort roles by position (higher roles first)
        all_roles.sort(key=lambda r: r.position, reverse=True)
        
        # Add ALL role options to the dropdown (up to 25 due to Discord limit)
        role_view.role_select.options = [
            discord.SelectOption(
                label=role.name,
                description=f"Members: {len(role.members)} | {'Bot' if role.managed else 'User'} Role",
                value=str(role.id),
                emoji="🤖" if role.managed else "👤"
            ) for role in all_roles[:25]
        ]
        
        embed = discord.Embed(
            title="👥 Select Support Roles",
            description="Choose which roles should be pinged when tickets are created.\nAll server roles are available for selection:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 Available Roles:",
            value=f"Showing {len(role_view.role_select.options)} of {len(all_roles)} total roles",
            inline=False
        )
        
        if self.selected_roles:
            embed.add_field(
                name="✅ Currently Selected:",
                value=", ".join([role.mention for role in self.selected_roles]),
                inline=False
            )
        else:
            embed.add_field(
                name="✅ Currently Selected:",
                value="*No roles selected*",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, view=role_view, ephemeral=True)
    
    @discord.ui.button(label='✅ Create Ticket Panel', style=discord.ButtonStyle.success, row=2)
    async def create_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Save configuration
        role_names = [role.name for role in self.selected_roles]
        await self.save_ticket_config(
            interaction.guild.id,
            self.config['title'],
            self.config['description'],
            ','.join(role_names),
            self.config['support_hours'],
            self.config['response_time']
        )
        
        # Create the ticket panel
        embed = discord.Embed(
            title=self.config['title'],
            description=self.config['description'],
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📋 How it works:",
            value="1. Click the **Create Ticket** button\n2. Fill out the form with your issue\n3. A private channel will be created for you\n4. Support staff will assist you there\n5. The ticket will be closed when resolved",
            inline=False
        )
        
        if self.config['support_hours']:
            embed.add_field(
                name="🔧 Support Hours:",
                value=self.config['support_hours'],
                inline=True
            )
        
        if self.config['response_time']:
            embed.add_field(
                name="⏱️ Response Time:",
                value=self.config['response_time'],
                inline=True
            )
        
        if self.selected_roles:
            embed.add_field(
                name="👥 Support Roles:",
                value=", ".join([role.mention for role in self.selected_roles]),
                inline=False
            )
        
        embed.set_footer(text="NexGuard Ticket System")
        
        view = TicketView(self.bot)
        
        await interaction.response.edit_message(embed=embed, view=view)
        
        logger.info(f"Ticket system configured in {interaction.guild.name} by {interaction.user}")
    
    @discord.ui.button(label='❌ Cancel', style=discord.ButtonStyle.danger, row=2)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Setup Cancelled",
            description="Ticket system setup has been cancelled.",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    def create_preview_embed(self, guild):
        embed = discord.Embed(
            title="🎫 Ticket System Setup",
            description="Configure your ticket system settings below",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📝 Panel Title:",
            value=self.config['title'],
            inline=False
        )
        
        embed.add_field(
            name="📄 Panel Description:",
            value=self.config['description'][:100] + ("..." if len(self.config['description']) > 100 else ""),
            inline=False
        )
        
        if self.selected_roles:
            embed.add_field(
                name="👥 Selected Roles:",
                value=", ".join([role.mention for role in self.selected_roles]),
                inline=False
            )
        else:
            # Check total roles in guild (excluding @everyone)
            total_roles = len([role for role in guild.roles if not role.is_default()])
            if total_roles > 0:
                embed.add_field(
                    name="👥 Selected Roles:",
                    value=f"*No roles selected - {total_roles} roles available*",
                    inline=False
                )
            else:
                embed.add_field(
                    name="👥 Selected Roles:",
                    value="*No roles available in this server*",
                    inline=False
                )
        
        embed.add_field(
            name="🔧 Support Hours:",
            value=self.config['support_hours'],
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Response Time:",
            value=self.config['response_time'],
            inline=True
        )
        
        embed.set_footer(text="Use the buttons to configure your ticket system")
        
        return embed
    
    async def save_ticket_config(self, guild_id, title, description, ping_roles, support_hours, response_time):
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        
        # Create ticket config table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_config (
                guild_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                ping_roles TEXT,
                support_hours TEXT,
                response_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            INSERT OR REPLACE INTO ticket_config 
            (guild_id, title, description, ping_roles, support_hours, response_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (guild_id, title, description, ping_roles, support_hours, response_time))
        
        conn.commit()
        conn.close()

class TicketSetupModal(discord.ui.Modal):
    def __init__(self, bot, setup_view):
        super().__init__(title="Configure Ticket Text")
        self.bot = bot
        self.setup_view = setup_view
        
        self.title_input = discord.ui.TextInput(
            label="Panel Title",
            placeholder="Support Ticket System",
            max_length=100,
            required=True,
            default=setup_view.config['title']
        )
        
        self.description_input = discord.ui.TextInput(
            label="Panel Description",
            placeholder="Welcome message and instructions...",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True,
            default=setup_view.config['description']
        )
        
        self.support_hours = discord.ui.TextInput(
            label="Support Hours",
            placeholder="Monday - Friday: 9 AM - 6 PM",
            max_length=100,
            required=False,
            default=setup_view.config['support_hours']
        )
        
        self.response_time = discord.ui.TextInput(
            label="Response Time",
            placeholder="Within 24 hours",
            max_length=50,
            required=False,
            default=setup_view.config['response_time']
        )
        
        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.add_item(self.support_hours)
        self.add_item(self.response_time)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Update the setup view's config
        self.setup_view.config['title'] = self.title_input.value
        self.setup_view.config['description'] = self.description_input.value
        self.setup_view.config['support_hours'] = self.support_hours.value
        self.setup_view.config['response_time'] = self.response_time.value
        
        # Update the preview embed
        embed = self.setup_view.create_preview_embed(interaction.guild)
        await interaction.response.edit_message(embed=embed, view=self.setup_view)

class RoleSelectionView(discord.ui.View):
    def __init__(self, bot, setup_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.setup_view = setup_view
        
    @discord.ui.select(
        placeholder="Select roles to ping when tickets are created...",
        min_values=0,
        max_values=10,
        row=0,
        options=[discord.SelectOption(label="Loading...", value="loading")]  # Default option
    )
    async def role_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        # Don't process if it's the loading option
        if select.values and select.values[0] == "loading":
            await interaction.response.defer()
            return
        
        # Update selected roles
        self.setup_view.selected_roles = []
        for role_id in select.values:
            role = interaction.guild.get_role(int(role_id))
            if role:
                self.setup_view.selected_roles.append(role)
        
        # Update the embed to show selected roles
        embed = discord.Embed(
            title="👥 Roles Selected",
            description="Selected roles will be pinged when tickets are created:",
            color=discord.Color.green()
        )
        
        if self.setup_view.selected_roles:
            embed.add_field(
                name="Selected Roles:",
                value=", ".join([role.mention for role in self.setup_view.selected_roles]),
                inline=False
            )
        else:
            embed.add_field(
                name="Selected Roles:",
                value="*No roles selected*",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label='✅ Confirm Selection', style=discord.ButtonStyle.success, row=1)
    async def confirm_selection(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Update the main setup view
        embed = self.setup_view.create_preview_embed(interaction.guild)
        
        success_embed = discord.Embed(
            title="✅ Roles Updated",
            description="Return to the main setup to continue configuration.",
            color=discord.Color.green()
        )
        
        if self.setup_view.selected_roles:
            success_embed.add_field(
                name="Selected Roles:",
                value=", ".join([role.mention for role in self.setup_view.selected_roles]),
                inline=False
            )
        
        await interaction.response.edit_message(embed=success_embed, view=None)

class TicketModal(discord.ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Create Support Ticket")
        self.bot = bot
        
        self.subject = discord.ui.TextInput(
            label="Subject",
            placeholder="Brief description of your issue...",
            max_length=100,
            required=True
        )
        
        self.description = discord.ui.TextInput(
            label="Description",
            placeholder="Detailed description of your issue...",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True
        )
        
        self.add_item(self.subject)
        self.add_item(self.description)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Get ticket category
        category = discord.utils.get(interaction.guild.categories, name="🎫 Support Tickets")
        
        if not category:
            # Create category if it doesn't exist
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True),
            }
            category = await interaction.guild.create_category("🎫 Support Tickets", overwrites=overwrites)
        
        # Create ticket channel
        ticket_number = await self.get_next_ticket_number(interaction.guild.id)
        channel_name = f"ticket-{ticket_number:04d}"
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True),
        }
        
        # Add configured support roles
        config = await self.get_ticket_config(interaction.guild.id)
        if config and config.get('ping_roles'):
            role_names = [role.strip() for role in config['ping_roles'].split(',')]
            for role_name in role_names:
                support_role = discord.utils.get(interaction.guild.roles, name=role_name)
                if support_role:
                    overwrites[support_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        
        ticket_channel = await interaction.guild.create_text_channel(
            channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"Support ticket by {interaction.user} | Subject: {self.subject.value}"
        )
        
        # Save to database
        await self.save_ticket_to_db(
            interaction.guild.id,
            ticket_channel.id,
            interaction.user.id,
            ticket_number,
            self.subject.value,
            self.description.value
        )
        
        # Create ticket embed
        embed = discord.Embed(
            title=f"🎫 Support Ticket #{ticket_number:04d}",
            description=f"**Subject:** {self.subject.value}\n\n**Description:**\n{self.description.value}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="Status", value="🟢 Open", inline=True)
        embed.add_field(name="Created by", value=interaction.user.mention, inline=True)
        
        # Add control buttons
        view = TicketControlView(self.bot, ticket_number)
        
        # Create ping message with configured roles
        ping_message = interaction.user.mention
        config = await self.get_ticket_config(interaction.guild.id)
        if config and config.get('ping_roles'):
            role_names = [role.strip() for role in config['ping_roles'].split(',')]
            for role_name in role_names:
                support_role = discord.utils.get(interaction.guild.roles, name=role_name)
                if support_role:
                    ping_message += f" {support_role.mention}"
        
        await ticket_channel.send(ping_message, embed=embed, view=view)
        
        # Send confirmation
        await interaction.response.send_message(
            f"✅ Ticket created successfully! Please check {ticket_channel.mention}",
            ephemeral=True
        )
        
        # Log ticket creation
        await self.log_ticket_action(interaction.guild, f"Ticket #{ticket_number:04d} created by {interaction.user}", ticket_channel)
    
    async def get_next_ticket_number(self, guild_id):
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        
        # Create tickets table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                ticket_number INTEGER NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                closed_by INTEGER
            )
        ''')
        
        cursor.execute('SELECT MAX(ticket_number) FROM tickets WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        next_number = (result[0] or 0) + 1
        
        conn.close()
        return next_number
    
    async def get_ticket_config(self, guild_id):
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ticket_config WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'title': result[1],
                'description': result[2],
                'ping_roles': result[3],
                'support_hours': result[4],
                'response_time': result[5]
            }
        return None
    
    async def save_ticket_to_db(self, guild_id, channel_id, user_id, ticket_number, subject, description):
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tickets (guild_id, channel_id, user_id, ticket_number, subject, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (guild_id, channel_id, user_id, ticket_number, subject, description))
        
        conn.commit()
        conn.close()
    
    async def log_ticket_action(self, guild, message, channel=None):
        # Get log channel
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT log_channel FROM guild_settings WHERE guild_id = ?', (guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            log_channel = guild.get_channel(result[0])
            if log_channel:
                embed = discord.Embed(
                    title="🎫 Ticket System",
                    description=message,
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                if channel:
                    embed.add_field(name="Channel", value=channel.mention, inline=True)
                
                try:
                    await log_channel.send(embed=embed)
                except discord.Forbidden:
                    pass

class TicketControlView(discord.ui.View):
    def __init__(self, bot, ticket_number):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_number = ticket_number
        
    @discord.ui.button(label='🔒 Close Ticket', style=discord.ButtonStyle.danger, custom_id='close_ticket')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has permission to close tickets
        has_permission = await self.check_ticket_permissions(interaction.user, interaction.guild)
        if not (has_permission or await self.is_ticket_owner(interaction.user.id, interaction.channel.id)):
            await interaction.response.send_message("❌ You don't have permission to close this ticket.", ephemeral=True)
            return
        
        await interaction.response.send_modal(CloseTicketModal(self.bot, self.ticket_number))
    
    @discord.ui.button(label='📋 Ticket Info', style=discord.ButtonStyle.secondary, custom_id='ticket_info')
    async def ticket_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket_info = await self.get_ticket_info(interaction.channel.id)
        
        if not ticket_info:
            await interaction.response.send_message("❌ Ticket information not found.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🎫 Ticket #{self.ticket_number:04d} Information",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        user = interaction.guild.get_member(ticket_info['user_id'])
        embed.add_field(name="Created by", value=user.mention if user else "Unknown User", inline=True)
        embed.add_field(name="Subject", value=ticket_info['subject'], inline=True)
        embed.add_field(name="Status", value=f"🟢 {ticket_info['status'].title()}", inline=True)
        embed.add_field(name="Created", value=f"<t:{int(datetime.fromisoformat(ticket_info['created_at']).timestamp())}:F>", inline=True)
        embed.add_field(name="Description", value=ticket_info['description'], inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def is_ticket_owner(self, user_id, channel_id):
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM tickets WHERE channel_id = ?', (channel_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result and result[0] == user_id
    
    async def check_ticket_permissions(self, user, guild):
        """Check if user has ticket management permissions"""
        if user.guild_permissions.manage_channels:
            return True
        
        # Check configured support roles
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT ping_roles FROM ticket_config WHERE guild_id = ?', (guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            role_names = [role.strip() for role in result[0].split(',')]
            for role_name in role_names:
                if discord.utils.get(user.roles, name=role_name):
                    return True
        
        return False
    
    async def get_ticket_info(self, channel_id):
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tickets WHERE channel_id = ?', (channel_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'user_id': result[3],
                'ticket_number': result[4],
                'subject': result[5],
                'description': result[6],
                'status': result[7],
                'created_at': result[8]
            }
        return None

class CloseTicketModal(discord.ui.Modal):
    def __init__(self, bot, ticket_number):
        super().__init__(title="Close Ticket")
        self.bot = bot
        self.ticket_number = ticket_number
        
        self.reason = discord.ui.TextInput(
            label="Reason for closing",
            placeholder="Optional reason for closing this ticket...",
            style=discord.TextStyle.paragraph,
            max_length=500,
            required=False
        )
        
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Update database
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tickets 
            SET status = 'closed', closed_at = CURRENT_TIMESTAMP, closed_by = ?
            WHERE channel_id = ?
        ''', (interaction.user.id, interaction.channel.id))
        conn.commit()
        conn.close()
        
        # Create closure embed
        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"Ticket #{self.ticket_number:04d} has been closed by {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        if self.reason.value:
            embed.add_field(name="Reason", value=self.reason.value, inline=False)
        
        embed.add_field(name="Closed by", value=interaction.user.mention, inline=True)
        embed.add_field(name="Closed at", value=f"<t:{int(datetime.utcnow().timestamp())}:F>", inline=True)
        
        await interaction.response.send_message(embed=embed)
        
        # Log closure
        await self.log_ticket_action(interaction.guild, f"Ticket #{self.ticket_number:04d} closed by {interaction.user}", interaction.channel)
        
        # Delete channel after 5 seconds
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete(reason=f"Ticket #{self.ticket_number:04d} closed")
        except discord.NotFound:
            pass
    
    async def log_ticket_action(self, guild, message, channel=None):
        # Get log channel
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT log_channel FROM guild_settings WHERE guild_id = ?', (guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            log_channel = guild.get_channel(result[0])
            if log_channel:
                embed = discord.Embed(
                    title="🎫 Ticket System",
                    description=message,
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                if channel:
                    embed.add_field(name="Channel", value=channel.mention, inline=True)
                
                try:
                    await log_channel.send(embed=embed)
                except discord.Forbidden:
                    pass

class EnhancedTicketSelectionView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.selected_category = "General Support"
        self.selected_priority = "Medium"
    
    @discord.ui.select(
        placeholder="Select ticket category...",
        options=[
            discord.SelectOption(label="Bug Report", description="Report software bugs", emoji="🐛"),
            discord.SelectOption(label="Feature Request", description="Suggest new features", emoji="💡"),
            discord.SelectOption(label="General Support", description="General help and questions", emoji="❓"),
            discord.SelectOption(label="Account Issues", description="Account-related problems", emoji="👤"),
            discord.SelectOption(label="Technical Support", description="Technical assistance", emoji="🔧"),
            discord.SelectOption(label="Billing", description="Payment and billing issues", emoji="💰")
        ],
        row=0
    )
    async def category_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_category = select.values[0]
        await interaction.response.defer()
    
    @discord.ui.select(
        placeholder="Select priority level...",
        options=[
            discord.SelectOption(label="Low", description="Non-urgent issues", emoji="🟢"),
            discord.SelectOption(label="Medium", description="Standard priority", emoji="🟡"),
            discord.SelectOption(label="High", description="Important issues", emoji="🟠"),
            discord.SelectOption(label="Critical", description="Urgent attention required", emoji="🔴")
        ],
        row=1
    )
    async def priority_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_priority = select.values[0]
        await interaction.response.defer()
    
    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary, emoji="🎫", row=2)
    async def create_enhanced_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Use the enhanced modal from the enhanced_ticket.py file
        from .enhanced_ticket import EnhancedTicketModal
        
        modal = EnhancedTicketModal(self.bot, self.selected_category, self.selected_priority)
        await interaction.response.send_modal(modal)

class TicketCreationPanelView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label='Create Ticket', style=discord.ButtonStyle.success, custom_id='create_ticket', row=0)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Create a support ticket"""
        try:
            logger.info(f"Create ticket button pressed by {interaction.user} in {interaction.guild.name}")
            
            from .enhanced_ticket import EnhancedTicketModal
            
            modal = EnhancedTicketModal(self.bot)
            await interaction.response.send_modal(modal)
            
            logger.info(f"Modal sent successfully to {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in create_ticket button: {str(e)}", exc_info=True)
            
            # Send error message to user
            error_embed = discord.Embed(
                title="❌ Button Error",
                description=f"An error occurred while opening the ticket form. Please try again.\n\nError: {str(e)}",
                color=discord.Color.red()
            )
            
            try:
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
            except:
                pass

class TicketEmbedCustomizationModal(discord.ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Customize Ticket Embed", timeout=300)
        self.bot = bot
        
        self.embed_title = discord.ui.TextInput(
            label="Embed Title",
            placeholder="🎫 Support Ticket System",
            max_length=100,
            required=True
        )
        
        self.embed_description = discord.ui.TextInput(
            label="Embed Description",
            placeholder="Need help? Create a support ticket and our team will assist you!",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True
        )
        
        self.embed_color = discord.ui.TextInput(
            label="Embed Color (hex code)",
            placeholder="#0099FF or blue",
            max_length=20,
            required=False
        )
        
        self.target_channel = discord.ui.TextInput(
            label="Channel Name (optional)",
            placeholder="Leave empty to use current channel",
            max_length=100,
            required=False
        )
        
        self.embed_footer = discord.ui.TextInput(
            label="Footer Text (optional)",
            placeholder="Custom footer message",
            max_length=100,
            required=False
        )
        
        self.add_item(self.embed_title)
        self.add_item(self.embed_description)
        self.add_item(self.embed_color)
        self.add_item(self.target_channel)
        self.add_item(self.embed_footer)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Parse color
        embed_color = discord.Color.blue()  # Default color
        if self.embed_color.value:
            try:
                if self.embed_color.value.startswith('#'):
                    embed_color = discord.Color(int(self.embed_color.value[1:], 16))
                else:
                    # Try to parse named colors
                    color_map = {
                        'red': discord.Color.red(),
                        'green': discord.Color.green(),
                        'blue': discord.Color.blue(),
                        'orange': discord.Color.orange(),
                        'purple': discord.Color.purple(),
                        'yellow': discord.Color.yellow(),
                        'pink': discord.Color.magenta(),
                        'teal': discord.Color.teal(),
                        'gold': discord.Color.gold(),
                        'dark_blue': discord.Color.dark_blue(),
                        'dark_green': discord.Color.dark_green(),
                        'dark_red': discord.Color.dark_red()
                    }
                    embed_color = color_map.get(self.embed_color.value.lower(), discord.Color.blue())
            except ValueError:
                embed_color = discord.Color.blue()
        
        # Find target channel
        target_channel = interaction.channel
        if self.target_channel.value:
            for channel in interaction.guild.text_channels:
                if channel.name.lower() == self.target_channel.value.lower():
                    target_channel = channel
                    break
        
        # Create the custom embed
        embed = discord.Embed(
            title=self.embed_title.value,
            description=self.embed_description.value,
            color=embed_color
        )
        

        
        # Set footer
        footer_text = self.embed_footer.value or f"Ticket System • {interaction.guild.name}"
        embed.set_footer(text=footer_text)
        
        # Create the view
        view = TicketCreationPanelView(self.bot)
        
        # Send the embed
        try:
            await target_channel.send(embed=embed, view=view)
            
            # Send confirmation
            confirm_embed = discord.Embed(
                title="✅ Custom Ticket Embed Created",
                description=f"Your custom ticket embed has been sent to {target_channel.mention}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=confirm_embed, ephemeral=True)
            
        except discord.Forbidden:
            error_embed = discord.Embed(
                title="❌ Permission Error",
                description=f"I don't have permission to send messages in {target_channel.mention}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='ticket-setup', description='Setup the ticket system with role selection and custom settings')
    async def ticket_setup(self, interaction: discord.Interaction):
        """Setup the ticket system with configuration options"""
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need administrator permissions to setup the ticket system.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create the setup view
        setup_view = TicketSetupView(self.bot)
        
        # Get all roles except @everyone and managed roles
        roles = [role for role in interaction.guild.roles 
                if not role.is_default() and not role.managed and not role.is_bot_managed()]
        
        # Sort roles by position (higher roles first)
        roles.sort(key=lambda r: r.position, reverse=True)
        
        # No need to populate dropdown options here anymore
        
        # Create initial embed
        embed = setup_view.create_preview_embed(interaction.guild)
        
        await interaction.response.send_message(embed=embed, view=setup_view, ephemeral=True)
        
        logger.info(f"Ticket setup initiated in {interaction.guild.name} by {interaction.user}")
    
    @app_commands.command(name='ticket', description='Create a new support ticket')
    async def ticket(self, interaction: discord.Interaction):
        """Create a new support ticket"""
        await interaction.response.send_modal(TicketModal(self.bot))
        
        logger.info(f"Ticket creation initiated by {interaction.user} in {interaction.guild.name}")
    
    @app_commands.command(name='ticket-enhanced', description='Create an enhanced ticket with priority and category selection')
    async def ticket_enhanced(self, interaction: discord.Interaction):
        """Create an enhanced ticket with priority and category selection"""
        view = EnhancedTicketSelectionView(self.bot)
        
        embed = discord.Embed(
            title="🎫 Create Enhanced Ticket",
            description="Select the category and priority for your ticket, then click 'Create Ticket':",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📋 Available Categories",
            value="• 🐛 Bug Report - Report software bugs\n• 💡 Feature Request - Suggest new features\n• ❓ General Support - General help and questions\n• 👤 Account Issues - Account-related problems\n• 🔧 Technical Support - Technical assistance\n• 💰 Billing - Payment and billing issues",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Priority Levels",
            value="• 🟢 Low - Non-urgent issues\n• 🟡 Medium - Standard priority\n• 🟠 High - Important issues\n• 🔴 Critical - Urgent attention required",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        logger.info(f"Enhanced ticket creation initiated by {interaction.user} in {interaction.guild.name}")
    
    @app_commands.command(name='ticket-panel', description='Create a ticket creation panel with buttons')
    @app_commands.describe(
        channel='Channel to send the ticket panel to (optional, defaults to current channel)',
        title='Custom title for the ticket panel',
        description='Custom description for the ticket panel'
    )
    async def ticket_panel(self, interaction: discord.Interaction, channel: discord.TextChannel = None, title: str = None, description: str = None):
        """Create a ticket creation panel with interactive buttons"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need the `Manage Channels` permission to create ticket panels.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Use current channel if none specified
        target_channel = channel or interaction.channel
        
        # Create the ticket panel embed
        panel_embed = discord.Embed(
            title=title or "🎫 Support Ticket System",
            description=description or "Need help? Create a support ticket and our team will assist you!",
            color=discord.Color.blue()
        )
        

        
        panel_embed.set_footer(text=f"Ticket System • {interaction.guild.name}")
        
        # Create the interactive view with buttons
        view = TicketCreationPanelView(self.bot)
        
        # Send the panel to the target channel
        try:
            await target_channel.send(embed=panel_embed, view=view)
            
            # Send confirmation
            embed = discord.Embed(
                title="✅ Ticket Panel Created",
                description=f"Ticket creation panel has been sent to {target_channel.mention}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            logger.info(f"Ticket panel created by {interaction.user} in {target_channel.name}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description=f"I don't have permission to send messages in {target_channel.mention}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name='ticket-embed', description='Create a custom ticket embed with your own design')
    async def ticket_embed(self, interaction: discord.Interaction):
        """Create a custom ticket embed with personalized design"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need the `Manage Channels` permission to create ticket embeds.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Send the custom embed creation modal
        modal = TicketEmbedCustomizationModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name='ticket-stats', description='View ticket statistics')
    async def ticket_stats(self, interaction: discord.Interaction):
        """View ticket statistics"""
        # Check permissions
        if not (interaction.user.guild_permissions.manage_channels or 
                discord.utils.get(interaction.user.roles, name="Support")):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to view ticket statistics.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get statistics
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        
        # Total tickets
        cursor.execute('SELECT COUNT(*) FROM tickets WHERE guild_id = ?', (interaction.guild.id,))
        total_tickets = cursor.fetchone()[0]
        
        # Open tickets
        cursor.execute('SELECT COUNT(*) FROM tickets WHERE guild_id = ? AND status = "open"', (interaction.guild.id,))
        open_tickets = cursor.fetchone()[0]
        
        # Closed tickets
        cursor.execute('SELECT COUNT(*) FROM tickets WHERE guild_id = ? AND status = "closed"', (interaction.guild.id,))
        closed_tickets = cursor.fetchone()[0]
        
        # Recent tickets (last 7 days)
        cursor.execute('''
            SELECT COUNT(*) FROM tickets 
            WHERE guild_id = ? AND datetime(created_at) >= datetime('now', '-7 days')
        ''', (interaction.guild.id,))
        recent_tickets = cursor.fetchone()[0]
        
        conn.close()
        
        embed = discord.Embed(
            title="📊 Ticket Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="📋 Total Tickets", value=str(total_tickets), inline=True)
        embed.add_field(name="🟢 Open Tickets", value=str(open_tickets), inline=True)
        embed.add_field(name="🔴 Closed Tickets", value=str(closed_tickets), inline=True)
        embed.add_field(name="📅 Recent (7 days)", value=str(recent_tickets), inline=True)
        
        if total_tickets > 0:
            resolution_rate = (closed_tickets / total_tickets) * 100
            embed.add_field(name="✅ Resolution Rate", value=f"{resolution_rate:.1f}%", inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(TicketCog(bot))