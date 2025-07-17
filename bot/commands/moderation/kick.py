import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class KickCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='kick', description='Kick a member from the server')
    @app_commands.describe(
        member='The member to kick',
        reason='The reason for the kick'
    )
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Kick a member from the server"""
        # Check permissions
        if not interaction.user.guild_permissions.kick_members:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to kick members.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member == interaction.user:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot kick yourself.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot kick someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member.top_role >= interaction.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Error",
                description="I cannot kick someone with a higher or equal role than me.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Try to DM the user before kicking
            try:
                dm_embed = discord.Embed(
                    title="🦵 You have been kicked",
                    description=f"**Server:** {interaction.guild.name}\n**Reason:** {reason}\n**Moderator:** {interaction.user}",
                    color=discord.Color.orange(),
                    timestamp=datetime.utcnow()
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            # Kick the member
            await member.kick(reason=f"Kicked by {interaction.user}: {reason}")
            
            # Log the kick
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interaction.guild.id, interaction.channel.id, member.id, interaction.id, reason, 'KICK'))
            conn.commit()
            conn.close()
            
            # Send confirmation
            embed = discord.Embed(
                title="🦵 Member Kicked",
                description=f"**Member:** {member} (`{member.id}`)\n**Reason:** {reason}\n**Moderator:** {interaction.user}",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"User {member} kicked from {interaction.guild.name} by {interaction.user}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to kick this member.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error kicking member: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while trying to kick the member.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(KickCog(bot))