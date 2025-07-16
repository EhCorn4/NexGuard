import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TicketManageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='ticket-list', description='List all tickets in the server')
    @app_commands.describe(status='Filter by ticket status (open/closed/all)')
    async def ticket_list(self, interaction: discord.Interaction, status: str = "all"):
        """List all tickets in the server"""
        # Check permissions
        if not await self.check_ticket_permissions(interaction.user, interaction.guild):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to view tickets.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate status
        valid_statuses = ["open", "closed", "all"]
        if status.lower() not in valid_statuses:
            embed = discord.Embed(
                title="❌ Invalid Status",
                description=f"Status must be one of: {', '.join(valid_statuses)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get tickets from database
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        
        if status.lower() == "all":
            cursor.execute('''
                SELECT ticket_number, user_id, subject, status, created_at, channel_id
                FROM tickets WHERE guild_id = ? 
                ORDER BY created_at DESC LIMIT 20
            ''', (interaction.guild.id,))
        else:
            cursor.execute('''
                SELECT ticket_number, user_id, subject, status, created_at, channel_id
                FROM tickets WHERE guild_id = ? AND status = ?
                ORDER BY created_at DESC LIMIT 20
            ''', (interaction.guild.id, status.lower()))
        
        tickets = cursor.fetchall()
        conn.close()
        
        if not tickets:
            embed = discord.Embed(
                title="📋 No Tickets Found",
                description=f"No {status.lower()} tickets found in this server.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Create tickets list embed
        embed = discord.Embed(
            title=f"🎫 {status.title()} Tickets",
            description=f"Showing {len(tickets)} most recent tickets",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        for ticket_number, user_id, subject, ticket_status, created_at, channel_id in tickets:
            user = interaction.guild.get_member(user_id)
            user_name = user.display_name if user else "Unknown User"
            
            status_emoji = "🟢" if ticket_status == "open" else "🔴"
            
            # Check if channel still exists
            channel = interaction.guild.get_channel(channel_id)
            channel_info = channel.mention if channel else "*(deleted)*"
            
            embed.add_field(
                name=f"#{ticket_number:04d} - {subject[:30]}{'...' if len(subject) > 30 else ''}",
                value=f"{status_emoji} **{ticket_status.title()}** | {user_name}\n{channel_info} | <t:{int(datetime.fromisoformat(created_at).timestamp())}:R>",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='ticket-close', description='Close a ticket by number')
    @app_commands.describe(ticket_number='The ticket number to close')
    async def ticket_close(self, interaction: discord.Interaction, ticket_number: int):
        """Close a ticket by number"""
        # Check permissions
        if not await self.check_ticket_permissions(interaction.user, interaction.guild):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to close tickets.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get ticket info
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT channel_id, user_id, subject, status FROM tickets 
            WHERE guild_id = ? AND ticket_number = ?
        ''', (interaction.guild.id, ticket_number))
        result = cursor.fetchone()
        
        if not result:
            embed = discord.Embed(
                title="❌ Ticket Not Found",
                description=f"No ticket found with number #{ticket_number:04d}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        channel_id, user_id, subject, status = result
        
        if status == "closed":
            embed = discord.Embed(
                title="❌ Ticket Already Closed",
                description=f"Ticket #{ticket_number:04d} is already closed.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Update ticket status
        cursor.execute('''
            UPDATE tickets 
            SET status = 'closed', closed_at = CURRENT_TIMESTAMP, closed_by = ?
            WHERE guild_id = ? AND ticket_number = ?
        ''', (interaction.user.id, interaction.guild.id, ticket_number))
        conn.commit()
        conn.close()
        
        # Try to delete the channel
        channel = interaction.guild.get_channel(channel_id)
        if channel:
            try:
                await channel.delete(reason=f"Ticket #{ticket_number:04d} closed by {interaction.user}")
                channel_status = "Channel deleted"
            except discord.Forbidden:
                channel_status = "Channel exists but couldn't be deleted"
            except discord.NotFound:
                channel_status = "Channel already deleted"
        else:
            channel_status = "Channel not found"
        
        # Send confirmation
        embed = discord.Embed(
            title="✅ Ticket Closed",
            description=f"Ticket #{ticket_number:04d} has been closed successfully.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Subject", value=subject, inline=False)
        embed.add_field(name="Closed by", value=interaction.user.mention, inline=True)
        embed.add_field(name="Channel Status", value=channel_status, inline=True)
        
        await interaction.response.send_message(embed=embed)
        
        # Log the closure
        await self.log_ticket_action(interaction.guild, f"Ticket #{ticket_number:04d} closed by {interaction.user}")
        
        logger.info(f"Ticket #{ticket_number:04d} closed by {interaction.user} in {interaction.guild.name}")
    
    @app_commands.command(name='ticket-info', description='Get detailed information about a ticket')
    @app_commands.describe(ticket_number='The ticket number to get info about')
    async def ticket_info(self, interaction: discord.Interaction, ticket_number: int):
        """Get detailed information about a ticket"""
        # Check permissions
        if not await self.check_ticket_permissions(interaction.user, interaction.guild):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to view ticket information.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get ticket info
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM tickets 
            WHERE guild_id = ? AND ticket_number = ?
        ''', (interaction.guild.id, ticket_number))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            embed = discord.Embed(
                title="❌ Ticket Not Found",
                description=f"No ticket found with number #{ticket_number:04d}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Parse ticket data
        (ticket_id, guild_id, channel_id, user_id, ticket_num, subject, 
         description, status, created_at, closed_at, closed_by) = result
        
        # Create info embed
        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket_number:04d} Information",
            color=discord.Color.blue() if status == "open" else discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        # Basic info
        user = interaction.guild.get_member(user_id)
        embed.add_field(name="Subject", value=subject, inline=False)
        embed.add_field(name="Description", value=description[:500] + ("..." if len(description) > 500 else ""), inline=False)
        embed.add_field(name="Created by", value=user.mention if user else "Unknown User", inline=True)
        embed.add_field(name="Status", value=f"{'🟢' if status == 'open' else '🔴'} {status.title()}", inline=True)
        embed.add_field(name="Created", value=f"<t:{int(datetime.fromisoformat(created_at).timestamp())}:F>", inline=True)
        
        # Channel info
        channel = interaction.guild.get_channel(channel_id)
        embed.add_field(name="Channel", value=channel.mention if channel else "*(deleted)*", inline=True)
        
        # Closed info
        if status == "closed" and closed_at:
            embed.add_field(name="Closed", value=f"<t:{int(datetime.fromisoformat(closed_at).timestamp())}:F>", inline=True)
            if closed_by:
                closer = interaction.guild.get_member(closed_by)
                embed.add_field(name="Closed by", value=closer.mention if closer else "Unknown User", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='ticket-cleanup', description='Clean up deleted ticket channels from database')
    async def ticket_cleanup(self, interaction: discord.Interaction):
        """Clean up deleted ticket channels from database"""
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need administrator permissions to clean up tickets.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Get all open tickets
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ticket_number, channel_id FROM tickets 
            WHERE guild_id = ? AND status = 'open'
        ''', (interaction.guild.id,))
        tickets = cursor.fetchall()
        
        cleaned_count = 0
        for ticket_number, channel_id in tickets:
            channel = interaction.guild.get_channel(channel_id)
            if not channel:
                # Channel doesn't exist, mark ticket as closed
                cursor.execute('''
                    UPDATE tickets 
                    SET status = 'closed', closed_at = CURRENT_TIMESTAMP, closed_by = ?
                    WHERE guild_id = ? AND ticket_number = ?
                ''', (interaction.user.id, interaction.guild.id, ticket_number))
                cleaned_count += 1
        
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="🧹 Ticket Cleanup Complete",
            description=f"Cleaned up {cleaned_count} tickets with deleted channels.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Action Taken", value="Marked tickets as closed where channels no longer exist", inline=False)
        
        await interaction.followup.send(embed=embed)
        
        logger.info(f"Ticket cleanup performed by {interaction.user} in {interaction.guild.name} - {cleaned_count} tickets cleaned")
    
    async def log_ticket_action(self, guild, message):
        """Log ticket action to the guild's log channel"""
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
                
                try:
                    await log_channel.send(embed=embed)
                except discord.Forbidden:
                    pass
    
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

async def setup(bot):
    await bot.add_cog(TicketManageCog(bot))