import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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
        
        self.additional_info = discord.ui.TextInput(
            label="Additional Information",
            placeholder="Any additional details (optional)...",
            style=discord.TextStyle.paragraph,
            max_length=500,
            required=False
        )
        
        self.add_item(self.subject)
        self.add_item(self.description)
        self.add_item(self.additional_info)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            # Get next ticket number
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(ticket_number) FROM tickets WHERE guild_id = ?', (interaction.guild.id,))
            result = cursor.fetchone()
            ticket_number = (result[0] or 0) + 1
            
            # Get ticket configuration
            cursor.execute('SELECT ping_roles FROM ticket_config WHERE guild_id = ?', (interaction.guild.id,))
            config_result = cursor.fetchone()
            ping_roles = []
            if config_result and config_result[0]:
                try:
                    ping_roles = json.loads(config_result[0])
                except (json.JSONDecodeError, TypeError):
                    ping_roles = []
            
            # Create ticket category
            guild = interaction.guild
            category_name = "Support Tickets"
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                category = await guild.create_category(name=category_name)
            
            # Create ticket channel
            channel_name = f"🎫ticket-{ticket_number:04d}"
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            
            # Add ping roles permissions
            for role_id in ping_roles:
                role = guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            channel = await category.create_text_channel(name=channel_name, overwrites=overwrites)
            
            # Create additional info text
            additional_text = f"\n\n**Additional Information:**\n{self.additional_info.value}" if self.additional_info.value else ""
            
            # Save ticket to database
            cursor.execute('''
                INSERT INTO tickets (guild_id, channel_id, user_id, ticket_number, subject, description, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                guild.id, channel.id, interaction.user.id, ticket_number, 
                self.subject.value, self.description.value + additional_text, 
                "open", datetime.utcnow().isoformat()
            ))
            conn.commit()
            conn.close()
            
            # Create ticket embed
            embed = discord.Embed(
                title=f"🎫 Support Ticket #{ticket_number:04d}",
                description=f"**Subject:** {self.subject.value}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="📝 Description", value=self.description.value, inline=False)
            if self.additional_info.value:
                embed.add_field(name="ℹ️ Additional Information", value=self.additional_info.value, inline=False)
            
            embed.add_field(name="👤 Created by", value=interaction.user.mention, inline=True)
            embed.add_field(name="🕒 Created at", value=f"<t:{int(datetime.utcnow().timestamp())}:F>", inline=True)
            embed.set_footer(text=f"Ticket ID: {ticket_number:04d}")
            
            # Create control buttons
            view = TicketControlView(self.bot, ticket_number)
            
            # Send ticket message
            ping_text = ""
            if ping_roles:
                role_mentions = [guild.get_role(role_id).mention for role_id in ping_roles if guild.get_role(role_id)]
                if role_mentions:
                    ping_text = f"📢 {' '.join(role_mentions)}"
            
            await channel.send(content=ping_text, embed=embed, view=view)
            
            # Send confirmation
            confirmation_embed = discord.Embed(
                title="✅ Ticket Created Successfully",
                description=f"Your support ticket has been created in {channel.mention}",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=confirmation_embed, ephemeral=True)
            
            logger.info(f"Ticket #{ticket_number:04d} created by {interaction.user} in {guild.name}")
            
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}", exc_info=True)
            error_embed = discord.Embed(
                title="❌ Error Creating Ticket",
                description=f"An error occurred while creating your ticket: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

class TicketControlView(discord.ui.View):
    def __init__(self, bot, ticket_number):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_number = ticket_number
    
    @discord.ui.button(label='Close Ticket', style=discord.ButtonStyle.danger, custom_id='close_ticket')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
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
        
        # Send closure message
        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"Ticket #{self.ticket_number:04d} has been closed by {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Delete channel after 5 seconds
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete(reason=f"Ticket #{self.ticket_number:04d} closed")
        except discord.NotFound:
            pass

class TicketCreationPanelView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label='Create Ticket', style=discord.ButtonStyle.success, custom_id='create_ticket', row=0)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            from .enhanced_ticket import EnhancedTicketModal
            modal = EnhancedTicketModal(self.bot)
            await interaction.response.send_modal(modal)
        except Exception as e:
            logger.error(f"Error in create_ticket button: {str(e)}", exc_info=True)
            error_embed = discord.Embed(
                title="❌ Button Error",
                description=f"An error occurred while opening the ticket form: {str(e)}",
                color=discord.Color.red()
            )
            try:
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
            except discord.InteractionResponded:
                # Interaction was already responded to
                pass

class TicketSetupModal(discord.ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Configure Ticket System")
        self.bot = bot
        
        self.title_input = discord.ui.TextInput(
            label="Panel Title",
            placeholder="Support Ticket System",
            max_length=100,
            required=True
        )
        
        self.description_input = discord.ui.TextInput(
            label="Panel Description",
            placeholder="Welcome message and instructions...",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True
        )
        
        self.ping_roles_input = discord.ui.TextInput(
            label="Ping Roles (comma-separated)",
            placeholder="Staff, Moderator, Admin",
            max_length=200,
            required=False
        )
        
        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.add_item(self.ping_roles_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Save configuration
        ping_roles = []
        if self.ping_roles_input.value:
            role_names = [name.strip() for name in self.ping_roles_input.value.split(',')]
            for role_name in role_names:
                role = discord.utils.get(interaction.guild.roles, name=role_name)
                if role:
                    ping_roles.append(role.id)
        
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_config (
                guild_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                ping_roles TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            INSERT OR REPLACE INTO ticket_config (guild_id, title, description, ping_roles)
            VALUES (?, ?, ?, ?)
        ''', (interaction.guild.id, self.title_input.value, self.description_input.value, json.dumps(ping_roles)))
        
        conn.commit()
        conn.close()
        
        # Create the ticket panel
        embed = discord.Embed(
            title=self.title_input.value,
            description=self.description_input.value,
            color=discord.Color.blue()
        )
        
        view = TicketCreationPanelView(self.bot)
        await interaction.response.send_message(embed=embed, view=view)

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = bot.db_path
    
    @app_commands.command(name='ticket', description='Create a support ticket')
    async def ticket(self, interaction: discord.Interaction):
        modal = TicketModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name='ticket-setup', description='Setup the ticket system')
    async def ticket_setup(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need the `Manage Channels` permission to setup tickets.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        modal = TicketSetupModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name='ticket-panel', description='Create a ticket panel')
    @app_commands.describe(
        channel='Channel to send the panel to',
        title='Custom title for the panel',
        description='Custom description for the panel'
    )
    async def ticket_panel(self, interaction: discord.Interaction, channel: discord.TextChannel = None, title: str = None, description: str = None):
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need the `Manage Channels` permission to create ticket panels.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        target_channel = channel or interaction.channel
        
        panel_embed = discord.Embed(
            title=title or "🎫 Support Ticket System",
            description=description or "Need help? Create a support ticket and our team will assist you!",
            color=discord.Color.blue()
        )
        
        view = TicketCreationPanelView(self.bot)
        
        try:
            await target_channel.send(embed=panel_embed, view=view)
            embed = discord.Embed(
                title="✅ Ticket Panel Created",
                description=f"Ticket panel sent to {target_channel.mention}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description=f"I don't have permission to send messages in {target_channel.mention}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketCog(bot))