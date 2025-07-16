import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='lock', description='Lock a channel to prevent messages')
    @app_commands.describe(
        channel='Channel to lock (current channel if not specified)',
        reason='Reason for locking the channel'
    )
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel = None, reason: str = "No reason provided"):
        """Lock a channel to prevent messages"""
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
        
        try:
            # Get @everyone role
            everyone_role = interaction.guild.default_role
            
            # Check if channel is already locked
            overwrites = channel.overwrites_for(everyone_role)
            if overwrites.send_messages is False:
                embed = discord.Embed(
                    title="❌ Channel Already Locked",
                    description=f"{channel.mention} is already locked.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Lock the channel
            overwrites.send_messages = False
            await channel.set_permissions(everyone_role, overwrite=overwrites, reason=f"Channel locked by {interaction.user}: {reason}")
            
            # Log the action
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interaction.guild.id, channel.id, interaction.user.id, interaction.id, 
                  f"Channel locked - {reason}", 'LOCK'))
            conn.commit()
            conn.close()
            
            # Send confirmation
            embed = discord.Embed(
                title="🔒 Channel Locked",
                description=f"{channel.mention} has been locked.\n\n**Reason:** {reason}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"Locked by {interaction.user}")
            await interaction.response.send_message(embed=embed)
            
            # Send lock message in the channel if it's different from current
            if channel != interaction.channel:
                lock_embed = discord.Embed(
                    title="🔒 Channel Locked",
                    description=f"This channel has been locked by {interaction.user.mention}.\n\n**Reason:** {reason}",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                await channel.send(embed=lock_embed)
            
            logger.info(f"Channel {channel.name} locked by {interaction.user}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to lock this channel.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error locking channel: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while locking the channel.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='unlock', description='Unlock a channel to allow messages')
    @app_commands.describe(
        channel='Channel to unlock (current channel if not specified)',
        reason='Reason for unlocking the channel'
    )
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel = None, reason: str = "No reason provided"):
        """Unlock a channel to allow messages"""
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
        
        try:
            # Get @everyone role
            everyone_role = interaction.guild.default_role
            
            # Check if channel is locked
            overwrites = channel.overwrites_for(everyone_role)
            if overwrites.send_messages is not False:
                embed = discord.Embed(
                    title="❌ Channel Not Locked",
                    description=f"{channel.mention} is not locked.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Unlock the channel
            overwrites.send_messages = None  # Reset to default
            await channel.set_permissions(everyone_role, overwrite=overwrites, reason=f"Channel unlocked by {interaction.user}: {reason}")
            
            # Log the action
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interaction.guild.id, channel.id, interaction.user.id, interaction.id, 
                  f"Channel unlocked - {reason}", 'UNLOCK'))
            conn.commit()
            conn.close()
            
            # Send confirmation
            embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description=f"{channel.mention} has been unlocked.\n\n**Reason:** {reason}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"Unlocked by {interaction.user}")
            await interaction.response.send_message(embed=embed)
            
            # Send unlock message in the channel if it's different from current
            if channel != interaction.channel:
                unlock_embed = discord.Embed(
                    title="🔓 Channel Unlocked",
                    description=f"This channel has been unlocked by {interaction.user.mention}.\n\n**Reason:** {reason}",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                await channel.send(embed=unlock_embed)
            
            logger.info(f"Channel {channel.name} unlocked by {interaction.user}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to unlock this channel.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error unlocking channel: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while unlocking the channel.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(LockCog(bot))