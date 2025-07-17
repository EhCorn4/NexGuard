import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TimeoutCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def parse_duration(self, duration_str):
        """Parse duration string like '1h', '30m', '2d' into seconds"""
        duration_str = duration_str.lower()
        
        # Extract number and unit
        if duration_str[-1] in ['s', 'm', 'h', 'd']:
            try:
                number = int(duration_str[:-1])
                unit = duration_str[-1]
                
                if unit == 's':
                    return number
                elif unit == 'm':
                    return number * 60
                elif unit == 'h':
                    return number * 3600
                elif unit == 'd':
                    return number * 86400
            except ValueError:
                return None
        
        return None
    
    @app_commands.command(name='timeout', description='Timeout a member for a specified duration')
    @app_commands.describe(
        member='The member to timeout',
        duration='Duration (e.g., 1h, 30m, 2d)',
        reason='The reason for the timeout'
    )
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
        """Timeout a member for a specified duration"""
        # Check permissions
        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to timeout members.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member == interaction.user:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot timeout yourself.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot timeout someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Parse duration
        duration_seconds = self.parse_duration(duration)
        if not duration_seconds:
            embed = discord.Embed(
                title="❌ Invalid Duration",
                description="Please use format like: 1h, 30m, 2d, 60s",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Discord timeout limit is 28 days
        if duration_seconds > 2419200:  # 28 days in seconds
            embed = discord.Embed(
                title="❌ Duration Too Long",
                description="Maximum timeout duration is 28 days.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Apply timeout
            timeout_until = datetime.utcnow() + timedelta(seconds=duration_seconds)
            await member.timeout(timeout_until, reason=f"Timed out by {interaction.user}: {reason}")
            
            # Log the timeout
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interaction.guild.id, interaction.channel.id, member.id, interaction.id, 
                  f"Timeout {duration} - {reason}", 'TIMEOUT'))
            conn.commit()
            conn.close()
            
            # Try to DM the user
            try:
                dm_embed = discord.Embed(
                    title="⏰ You have been timed out",
                    description=f"**Server:** {interaction.guild.name}\n**Duration:** {duration}\n**Reason:** {reason}\n**Moderator:** {interaction.user}",
                    color=discord.Color.orange(),
                    timestamp=datetime.utcnow()
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            # Send confirmation
            embed = discord.Embed(
                title="⏰ Member Timed Out",
                description=f"**Member:** {member} (`{member.id}`)\n**Duration:** {duration}\n**Reason:** {reason}\n**Moderator:** {interaction.user}",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(
                name="Timeout Expires",
                value=f"<t:{int(timeout_until.timestamp())}:F>",
                inline=False
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"User {member} timed out for {duration} in {interaction.guild.name} by {interaction.user}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to timeout this member.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error timing out member: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while trying to timeout the member.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='untimeout', description='Remove timeout from a member')
    @app_commands.describe(member='The member to remove timeout from')
    async def untimeout(self, interaction: discord.Interaction, member: discord.Member):
        """Remove timeout from a member"""
        # Check permissions
        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to remove timeouts.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if member is timed out
        if not member.timed_out:
            embed = discord.Embed(
                title="❌ Error",
                description="This member is not timed out.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Remove timeout
            await member.timeout(None, reason=f"Timeout removed by {interaction.user}")
            
            # Log the action
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interaction.guild.id, interaction.channel.id, member.id, interaction.id, 
                  f"Timeout removed by {interaction.user}", 'UNTIMEOUT'))
            conn.commit()
            conn.close()
            
            # Try to DM the user
            try:
                dm_embed = discord.Embed(
                    title="✅ Your timeout has been removed",
                    description=f"**Server:** {interaction.guild.name}\n**Moderator:** {interaction.user}",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            # Send confirmation
            embed = discord.Embed(
                title="✅ Timeout Removed",
                description=f"**Member:** {member} (`{member.id}`)\n**Moderator:** {interaction.user}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"Timeout removed for {member} in {interaction.guild.name} by {interaction.user}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to remove timeouts for this member.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error removing timeout: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while trying to remove the timeout.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TimeoutCog(bot))