import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UnmuteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='unmute', description='Unmute a member in the server')
    @app_commands.describe(member='The member to unmute')
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        """Unmute a member in the server"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_roles:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to unmute members.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Find mute role
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not mute_role:
            # Check database for custom mute role
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT mute_role FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                mute_role = interaction.guild.get_role(result[0])
        
        if not mute_role:
            embed = discord.Embed(
                title="❌ Error",
                description="No mute role found. Please set up a mute role first.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if user is muted
        if mute_role not in member.roles:
            embed = discord.Embed(
                title="❌ Error",
                description="This member is not muted.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Remove mute role
            await member.remove_roles(mute_role, reason=f"Unmuted by {interaction.user}")
            
            # Remove from database
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM mutes WHERE guild_id = ? AND user_id = ?', 
                          (interaction.guild.id, member.id))
            conn.commit()
            conn.close()
            
            # Try to DM the user
            try:
                dm_embed = discord.Embed(
                    title="🔊 You have been unmuted",
                    description=f"**Server:** {interaction.guild.name}\n**Moderator:** {interaction.user}",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            # Send confirmation
            embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f"**Member:** {member} (`{member.id}`)\n**Moderator:** {interaction.user}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"User {member} unmuted in {interaction.guild.name} by {interaction.user}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to unmute this member.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error unmuting member: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while trying to unmute the member.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='mutelist', description='Show the list of muted users')
    async def mutelist(self, interaction: discord.Interaction):
        """Show the list of muted users"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_roles:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to view muted users.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Get muted users from database
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, moderator_id, reason, timestamp FROM mutes 
                WHERE guild_id = ? 
                ORDER BY timestamp DESC
            ''', (interaction.guild.id,))
            muted_users = cursor.fetchall()
            conn.close()
            
            if not muted_users:
                embed = discord.Embed(
                    title="📋 No Muted Users",
                    description="There are no muted users in this server.",
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=embed)
                return
            
            embed = discord.Embed(
                title="🔇 Muted Users",
                description=f"**Total Muted Users:** {len(muted_users)}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            
            # Show first 10 muted users
            for i, (user_id, moderator_id, reason, timestamp) in enumerate(muted_users[:10], 1):
                user = interaction.guild.get_member(user_id)
                moderator = interaction.guild.get_member(moderator_id)
                
                user_name = user.mention if user else f"<@{user_id}>"
                moderator_name = moderator.mention if moderator else f"<@{moderator_id}>"
                
                embed.add_field(
                    name=f"{i}. {user_name}",
                    value=f"**Moderator:** {moderator_name}\n**Reason:** {reason}\n**Date:** <t:{int(datetime.fromisoformat(timestamp).timestamp())}:R>",
                    inline=False
                )
            
            if len(muted_users) > 10:
                embed.add_field(
                    name="Note",
                    value=f"Showing 10 most recent mutes out of {len(muted_users)} total.\nUse `/unmute @member` to unmute a user.",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting mute list: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while retrieving the mute list.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnmuteCog(bot))