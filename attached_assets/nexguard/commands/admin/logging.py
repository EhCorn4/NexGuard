import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='logging', description='Configure server logging settings')
    @app_commands.describe(
        log_type='Type of logging to configure',
        channel='Channel to send logs to (leave empty to disable)',
        action='Action to perform'
    )
    @app_commands.choices(log_type=[
        app_commands.Choice(name='Message Events (edits, deletes)', value='message'),
        app_commands.Choice(name='Member Events (joins, leaves)', value='member'),
        app_commands.Choice(name='Moderation Actions', value='moderation'),
        app_commands.Choice(name='Channel Changes', value='channel'),
        app_commands.Choice(name='Role Changes', value='role'),
        app_commands.Choice(name='Server Changes', value='server'),
        app_commands.Choice(name='Voice Activity', value='voice'),
        app_commands.Choice(name='All Events', value='all')
    ])
    @app_commands.choices(action=[
        app_commands.Choice(name='Enable', value='enable'),
        app_commands.Choice(name='Disable', value='disable'),
        app_commands.Choice(name='View Current Settings', value='view')
    ])
    async def logging(self, interaction: discord.Interaction, 
                     log_type: str, 
                     action: str,
                     channel: discord.TextChannel = None):
        """Configure server logging settings"""
        
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need the 'Manage Server' permission to configure logging.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if action == 'view':
            await self.show_logging_settings(interaction)
            return
        
        if action == 'enable' and not channel:
            embed = discord.Embed(
                title="❌ Channel Required",
                description="You must specify a channel when enabling logging.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Update logging settings
        await self.update_logging_settings(interaction, log_type, action, channel)
    
    async def show_logging_settings(self, interaction: discord.Interaction):
        """Show current logging settings"""
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        
        # Get current settings
        cursor.execute('''
            SELECT log_channel, message_logs, member_logs, moderation_logs, 
                   channel_logs, role_logs, server_logs, voice_logs
            FROM guild_settings WHERE guild_id = ?
        ''', (interaction.guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            embed = discord.Embed(
                title="📋 Logging Settings",
                description="No logging settings configured yet.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        log_channel_id, msg_logs, member_logs, mod_logs, channel_logs, role_logs, server_logs, voice_logs = result
        
        embed = discord.Embed(
            title="📋 Current Logging Settings",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Main log channel
        if log_channel_id:
            log_channel = interaction.guild.get_channel(log_channel_id)
            embed.add_field(
                name="Main Log Channel",
                value=log_channel.mention if log_channel else "Channel not found",
                inline=False
            )
        else:
            embed.add_field(
                name="Main Log Channel",
                value="❌ Not configured",
                inline=False
            )
        
        # Individual log settings
        log_status = {
            "📝 Message Events": "✅ Enabled" if msg_logs else "❌ Disabled",
            "👥 Member Events": "✅ Enabled" if member_logs else "❌ Disabled",
            "🔨 Moderation Actions": "✅ Enabled" if mod_logs else "❌ Disabled",
            "📁 Channel Changes": "✅ Enabled" if channel_logs else "❌ Disabled",
            "🎭 Role Changes": "✅ Enabled" if role_logs else "❌ Disabled",
            "🏠 Server Changes": "✅ Enabled" if server_logs else "❌ Disabled",
            "🎙️ Voice Activity": "✅ Enabled" if voice_logs else "❌ Disabled"
        }
        
        for log_type, status in log_status.items():
            embed.add_field(
                name=log_type,
                value=status,
                inline=True
            )
        
        embed.set_footer(text=f"Requested by {interaction.user}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def update_logging_settings(self, interaction: discord.Interaction, 
                                    log_type: str, action: str, channel: discord.TextChannel):
        """Update logging settings in database"""
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        
        # Ensure guild settings exist
        cursor.execute('INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)', (interaction.guild.id,))
        
        if log_type == 'all':
            # Enable/disable all logging types
            enabled = 1 if action == 'enable' else 0
            cursor.execute('''
                UPDATE guild_settings SET 
                    log_channel = ?,
                    message_logs = ?,
                    member_logs = ?,
                    moderation_logs = ?,
                    channel_logs = ?,
                    role_logs = ?,
                    server_logs = ?,
                    voice_logs = ?
                WHERE guild_id = ?
            ''', (
                channel.id if channel else None,
                enabled, enabled, enabled, enabled, enabled, enabled, enabled,
                interaction.guild.id
            ))
        else:
            # Update specific log type
            column_map = {
                'message': 'message_logs',
                'member': 'member_logs', 
                'moderation': 'moderation_logs',
                'channel': 'channel_logs',
                'role': 'role_logs',
                'server': 'server_logs',
                'voice': 'voice_logs'
            }
            
            column = column_map.get(log_type)
            if column:
                enabled = 1 if action == 'enable' else 0
                
                # Update the specific column and set log channel if enabling
                if action == 'enable':
                    cursor.execute(f'''
                        UPDATE guild_settings SET 
                            log_channel = ?,
                            {column} = ?
                        WHERE guild_id = ?
                    ''', (channel.id, enabled, interaction.guild.id))
                else:
                    cursor.execute(f'''
                        UPDATE guild_settings SET 
                            {column} = ?
                        WHERE guild_id = ?
                    ''', (enabled, interaction.guild.id))
        
        conn.commit()
        conn.close()
        
        # Create success embed
        log_type_names = {
            'message': 'Message Events',
            'member': 'Member Events',
            'moderation': 'Moderation Actions',
            'channel': 'Channel Changes',
            'role': 'Role Changes',
            'server': 'Server Changes',
            'voice': 'Voice Activity',
            'all': 'All Events'
        }
        
        embed = discord.Embed(
            title="✅ Logging Settings Updated",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        if action == 'enable':
            embed.description = f"**{log_type_names.get(log_type, log_type)}** logging has been enabled.\nLogs will be sent to {channel.mention}."
        else:
            embed.description = f"**{log_type_names.get(log_type, log_type)}** logging has been disabled."
        
        embed.set_footer(text=f"Updated by {interaction.user}")
        await interaction.response.send_message(embed=embed)
        
        # Log the action
        logger.info(f"Logging settings updated in {interaction.guild.name}: {log_type} {action} by {interaction.user}")

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))