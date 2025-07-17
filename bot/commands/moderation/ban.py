import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='ban', description='Ban a member from the server')
    @app_commands.describe(
        member='The member to ban',
        reason='The reason for the ban'
    )
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Ban a member from the server"""
        # Check permissions
        if not interaction.user.guild_permissions.ban_members:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to ban members.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member == interaction.user:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot ban yourself.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot ban someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member.top_role >= interaction.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Error",
                description="I cannot ban someone with a higher or equal role than me.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Try to DM the user before banning
            try:
                dm_embed = discord.Embed(
                    title="🔨 You have been banned",
                    description=f"**Server:** {interaction.guild.name}\n**Reason:** {reason}\n**Moderator:** {interaction.user}",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            # Ban the member
            await member.ban(reason=f"Banned by {interaction.user}: {reason}")
            
            # Log the ban
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interaction.guild.id, interaction.channel.id, member.id, interaction.id, reason, 'BAN'))
            conn.commit()
            conn.close()
            
            # Send confirmation
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**Member:** {member} (`{member.id}`)\n**Reason:** {reason}\n**Moderator:** {interaction.user}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"User {member} banned from {interaction.guild.name} by {interaction.user}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to ban this member.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error banning member: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while trying to ban the member.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(BanCog(bot))