import discord
from discord.ext import commands
import sqlite3
import logging

logger = logging.getLogger(__name__)

class SettingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(name='settings', aliases=['config'])
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx):
        """Manage server settings"""
        if ctx.invoked_subcommand is None:
            try:
                conn = sqlite3.connect(self.bot.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT prefix, log_channel, mute_role, welcome_channel, auto_role
                    FROM guild_settings WHERE guild_id = ?
                ''', (ctx.guild.id,))
                
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    prefix, log_channel_id, mute_role_id, welcome_channel_id, auto_role_id = result
                else:
                    prefix = "!"
                    log_channel_id = mute_role_id = welcome_channel_id = auto_role_id = None
                
                embed = discord.Embed(
                    title="⚙️ Server Settings",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="🔧 Basic Settings",
                    value=f"**Prefix:** `{prefix}`\n"
                          f"**Log Channel:** {f'<#{log_channel_id}>' if log_channel_id else 'Not set'}\n"
                          f"**Mute Role:** {ctx.guild.get_role(mute_role_id).mention if mute_role_id and ctx.guild.get_role(mute_role_id) else 'Not set'}",
                    inline=False
                )
                
                embed.add_field(
                    name="👋 Welcome Settings",
                    value=f"**Welcome Channel:** {f'<#{welcome_channel_id}>' if welcome_channel_id else 'Not set'}\n"
                          f"**Auto Role:** {ctx.guild.get_role(auto_role_id).mention if auto_role_id and ctx.guild.get_role(auto_role_id) else 'Not set'}",
                    inline=False
                )
                
                embed.add_field(
                    name="📋 Available Commands",
                    value="`settings logchannel <channel>` - Set log channel\n"
                          "`settings muterole <role>` - Set mute role\n"
                          "`settings welcome <channel>` - Set welcome channel\n"
                          "`settings autorole <role>` - Set auto role\n"
                          "`settings reset` - Reset all settings",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"An error occurred while fetching settings: {str(e)}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                logger.error(f"Error fetching settings: {e}")
    
    @settings.command(name='logchannel', aliases=['logs'])
    async def set_log_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the log channel for the server"""
        if channel is None:
            embed = discord.Embed(
                title="❌ Error",
                description="Please specify a channel to set as the log channel.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)
            ''', (ctx.guild.id,))
            
            cursor.execute('''
                UPDATE guild_settings SET log_channel = ? WHERE guild_id = ?
            ''', (channel.id, ctx.guild.id))
            
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="✅ Log Channel Set",
                description=f"Log channel has been set to {channel.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
            # Send test message to log channel
            log_embed = discord.Embed(
                title="📝 Log Channel Configured",
                description=f"This channel has been set as the log channel by {ctx.author.mention}",
                color=discord.Color.blue()
            )
            await channel.send(embed=log_embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred while setting the log channel: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error(f"Error setting log channel: {e}")
    
    @settings.command(name='muterole')
    async def set_mute_role(self, ctx, role: discord.Role = None):
        """Set the mute role for the server"""
        if role is None:
            embed = discord.Embed(
                title="❌ Error",
                description="Please specify a role to set as the mute role.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)
            ''', (ctx.guild.id,))
            
            cursor.execute('''
                UPDATE guild_settings SET mute_role = ? WHERE guild_id = ?
            ''', (role.id, ctx.guild.id))
            
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="✅ Mute Role Set",
                description=f"Mute role has been set to {role.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred while setting the mute role: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error(f"Error setting mute role: {e}")
    
    @settings.command(name='welcome')
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the welcome channel for the server"""
        if channel is None:
            embed = discord.Embed(
                title="❌ Error",
                description="Please specify a channel to set as the welcome channel.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)
            ''', (ctx.guild.id,))
            
            cursor.execute('''
                UPDATE guild_settings SET welcome_channel = ? WHERE guild_id = ?
            ''', (channel.id, ctx.guild.id))
            
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="✅ Welcome Channel Set",
                description=f"Welcome channel has been set to {channel.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred while setting the welcome channel: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error(f"Error setting welcome channel: {e}")
    
    @settings.command(name='autorole')
    async def set_auto_role(self, ctx, role: discord.Role = None):
        """Set the auto role for new members"""
        if role is None:
            embed = discord.Embed(
                title="❌ Error",
                description="Please specify a role to set as the auto role.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if role.position >= ctx.guild.me.top_role.position:
            embed = discord.Embed(
                title="❌ Error",
                description="I cannot assign a role that is higher than or equal to my highest role.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)
            ''', (ctx.guild.id,))
            
            cursor.execute('''
                UPDATE guild_settings SET auto_role = ? WHERE guild_id = ?
            ''', (role.id, ctx.guild.id))
            
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="✅ Auto Role Set",
                description=f"Auto role has been set to {role.mention}\n"
                           f"New members will automatically receive this role.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred while setting the auto role: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error(f"Error setting auto role: {e}")
    
    @settings.command(name='reset')
    async def reset_settings(self, ctx):
        """Reset all server settings to default"""
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE guild_settings 
                SET prefix = '!', log_channel = NULL, mute_role = NULL, 
                    welcome_channel = NULL, auto_role = NULL
                WHERE guild_id = ?
            ''', (ctx.guild.id,))
            
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="✅ Settings Reset",
                description="All server settings have been reset to default values.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred while resetting settings: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error(f"Error resetting settings: {e}")
    
    @settings.error
    async def settings_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You need the `Manage Server` permission to manage server settings.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SettingsCog(bot))
