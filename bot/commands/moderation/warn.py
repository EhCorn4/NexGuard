import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WarnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='warn', description='Warn a member')
    @app_commands.describe(
        member='The member to warn',
        reason='The reason for the warning'
    )
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Warn a member"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_messages:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to warn members.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member == interaction.user:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot warn yourself.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot warn someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Add warning to database
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO warnings (guild_id, user_id, moderator_id, reason)
                VALUES (?, ?, ?, ?)
            ''', (interaction.guild.id, member.id, interaction.user.id, reason))
            
            # Get warning count
            cursor.execute('''
                SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?
            ''', (interaction.guild.id, member.id))
            warning_count = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            # Try to DM the user
            try:
                dm_embed = discord.Embed(
                    title="⚠️ You have been warned",
                    description=f"**Server:** {interaction.guild.name}\n**Reason:** {reason}\n**Moderator:** {interaction.user}\n**Warning Count:** {warning_count}",
                    color=discord.Color.orange(),
                    timestamp=datetime.utcnow()
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            # Send confirmation
            embed = discord.Embed(
                title="⚠️ Member Warned",
                description=f"**Member:** {member} (`{member.id}`)\n**Reason:** {reason}\n**Moderator:** {interaction.user}\n**Total Warnings:** {warning_count}",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"User {member} warned in {interaction.guild.name} by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error warning member: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while trying to warn the member.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='warnings', description='View warnings for a member')
    @app_commands.describe(member='The member to check warnings for')
    async def warnings(self, interaction: discord.Interaction, member: discord.Member = None):
        """View warnings for a member"""
        if member is None:
            member = interaction.user
        
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT moderator_id, reason, timestamp FROM warnings 
                WHERE guild_id = ? AND user_id = ?
                ORDER BY timestamp DESC
            ''', (interaction.guild.id, member.id))
            warnings = cursor.fetchall()
            conn.close()
            
            if not warnings:
                embed = discord.Embed(
                    title="📋 No Warnings",
                    description=f"{member.mention} has no warnings.",
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=embed)
                return
            
            embed = discord.Embed(
                title="⚠️ Member Warnings",
                description=f"**Member:** {member.mention}\n**Total Warnings:** {len(warnings)}",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            
            for i, (moderator_id, reason, timestamp) in enumerate(warnings[:10], 1):
                moderator = interaction.guild.get_member(moderator_id)
                moderator_name = moderator.mention if moderator else f"<@{moderator_id}>"
                
                embed.add_field(
                    name=f"Warning #{i}",
                    value=f"**Moderator:** {moderator_name}\n**Reason:** {reason}\n**Date:** <t:{int(datetime.fromisoformat(timestamp).timestamp())}:R>",
                    inline=False
                )
            
            if len(warnings) > 10:
                embed.add_field(
                    name="Note",
                    value=f"Showing 10 most recent warnings out of {len(warnings)} total.",
                    inline=False
                )
            
            embed.set_thumbnail(url=member.display_avatar.url)
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting warnings: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while retrieving warnings.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(WarnCog(bot))