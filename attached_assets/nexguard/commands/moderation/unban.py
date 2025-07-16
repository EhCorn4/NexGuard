import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UnbanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='unban', description='Unban a user from the server')
    @app_commands.describe(user_id='The ID of the user to unban')
    async def unban(self, interaction: discord.Interaction, user_id: str):
        """Unban a user from the server"""
        # Check permissions
        if not interaction.user.guild_permissions.ban_members:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to unban members.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate user ID
        try:
            user_id = int(user_id)
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid User ID",
                description="Please provide a valid user ID.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Get banned users
            banned_users = [entry async for entry in interaction.guild.bans()]
            banned_user = None
            
            for ban_entry in banned_users:
                if ban_entry.user.id == user_id:
                    banned_user = ban_entry.user
                    break
            
            if not banned_user:
                embed = discord.Embed(
                    title="❌ User Not Found",
                    description="This user is not banned from the server.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Unban the user
            await interaction.guild.unban(banned_user, reason=f"Unbanned by {interaction.user}")
            
            # Log the unban
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interaction.guild.id, interaction.channel.id, banned_user.id, interaction.id, 
                  f"Unbanned by {interaction.user}", 'UNBAN'))
            conn.commit()
            conn.close()
            
            # Send confirmation
            embed = discord.Embed(
                title="✅ User Unbanned",
                description=f"**User:** {banned_user} (`{banned_user.id}`)\n**Moderator:** {interaction.user}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=banned_user.display_avatar.url)
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"User {banned_user} unbanned from {interaction.guild.name} by {interaction.user}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to unban users.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while trying to unban the user.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='banlist', description='Show the list of banned users')
    async def banlist(self, interaction: discord.Interaction):
        """Show the list of banned users"""
        # Check permissions
        if not interaction.user.guild_permissions.ban_members:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to view banned users.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Defer response as this might take time
            await interaction.response.defer()
            
            # Get banned users
            banned_users = [entry async for entry in interaction.guild.bans()]
            
            if not banned_users:
                embed = discord.Embed(
                    title="📋 No Banned Users",
                    description="There are no banned users in this server.",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🔨 Banned Users",
                description=f"**Total Banned Users:** {len(banned_users)}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            
            # Show first 10 banned users
            for i, ban_entry in enumerate(banned_users[:10], 1):
                user = ban_entry.user
                reason = ban_entry.reason or "No reason provided"
                
                embed.add_field(
                    name=f"{i}. {user}",
                    value=f"**ID:** `{user.id}`\n**Reason:** {reason}",
                    inline=False
                )
            
            if len(banned_users) > 10:
                embed.add_field(
                    name="Note",
                    value=f"Showing 10 most recent bans out of {len(banned_users)} total.\nUse `/unban <user_id>` to unban a user.",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to view banned users.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error getting ban list: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while retrieving the ban list.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnbanCog(bot))