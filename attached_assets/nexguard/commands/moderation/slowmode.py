import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SlowmodeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='slowmode', description='Set slowmode for the current channel')
    @app_commands.describe(
        seconds='Slowmode duration in seconds (0 to disable, max 21600)',
        channel='Channel to apply slowmode to (current channel if not specified)'
    )
    async def slowmode(self, interaction: discord.Interaction, seconds: int, channel: discord.TextChannel = None):
        """Set slowmode for a channel"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to manage channels.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if channel is None:
            channel = interaction.channel
        
        # Validate seconds
        if seconds < 0 or seconds > 21600:  # Discord's max slowmode is 6 hours
            embed = discord.Embed(
                title="❌ Invalid Duration",
                description="Slowmode duration must be between 0 and 21600 seconds (6 hours).",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Set slowmode
            await channel.edit(slowmode_delay=seconds, reason=f"Slowmode set by {interaction.user}")
            
            # Log the action
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interaction.guild.id, channel.id, interaction.user.id, interaction.id, 
                  f"Slowmode set to {seconds}s", 'SLOWMODE'))
            conn.commit()
            conn.close()
            
            # Send confirmation
            if seconds == 0:
                embed = discord.Embed(
                    title="✅ Slowmode Disabled",
                    description=f"Slowmode has been disabled for {channel.mention}",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
            else:
                embed = discord.Embed(
                    title="⏳ Slowmode Enabled",
                    description=f"Slowmode set to **{seconds} seconds** for {channel.mention}",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                
                # Convert seconds to readable format
                if seconds >= 3600:
                    hours = seconds // 3600
                    minutes = (seconds % 3600) // 60
                    remaining_seconds = seconds % 60
                    readable_time = f"{hours}h {minutes}m {remaining_seconds}s"
                elif seconds >= 60:
                    minutes = seconds // 60
                    remaining_seconds = seconds % 60
                    readable_time = f"{minutes}m {remaining_seconds}s"
                else:
                    readable_time = f"{seconds}s"
                
                embed.add_field(
                    name="Duration",
                    value=readable_time,
                    inline=True
                )
            
            embed.set_footer(text=f"Set by {interaction.user}")
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"Slowmode set to {seconds}s for {channel.name} by {interaction.user}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to edit this channel.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error setting slowmode: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while setting slowmode.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(SlowmodeCog(bot))