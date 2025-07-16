import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MuteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def get_or_create_mute_role(self, guild):
        """Get or create the mute role for a guild"""
        # Check if guild has a custom mute role set
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT mute_role FROM guild_settings WHERE guild_id = ?', (guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            mute_role = guild.get_role(result[0])
            if mute_role:
                return mute_role
        
        # Try to find existing mute role
        mute_role = discord.utils.get(guild.roles, name="Muted")
        if mute_role:
            return mute_role
        
        # Create new mute role
        try:
            mute_role = await guild.create_role(
                name="Muted",
                permissions=discord.Permissions.none(),
                color=discord.Color.dark_gray(),
                reason="Auto-created mute role"
            )
            
            # Set up channel overrides
            for channel in guild.channels:
                try:
                    await channel.set_permissions(mute_role, send_messages=False, speak=False)
                except discord.Forbidden:
                    pass
            
            return mute_role
        except discord.Forbidden:
            return None
    
    @app_commands.command(name='mute', description='Mute a member in the server')
    @app_commands.describe(
        member='The member to mute',
        reason='The reason for the mute'
    )
    async def mute(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Mute a member in the server"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_roles:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to mute members.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member == interaction.user:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot mute yourself.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot mute someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get or create mute role
        mute_role = await self.get_or_create_mute_role(interaction.guild)
        if not mute_role:
            embed = discord.Embed(
                title="❌ Error",
                description="Could not find or create a mute role.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if already muted
        if mute_role in member.roles:
            embed = discord.Embed(
                title="❌ Error",
                description="This member is already muted.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Add mute role
            await member.add_roles(mute_role, reason=f"Muted by {interaction.user}: {reason}")
            
            # Log the mute
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO mutes (guild_id, user_id, moderator_id, reason)
                VALUES (?, ?, ?, ?)
            ''', (interaction.guild.id, member.id, interaction.user.id, reason))
            conn.commit()
            conn.close()
            
            # Try to DM the user
            try:
                dm_embed = discord.Embed(
                    title="🔇 You have been muted",
                    description=f"**Server:** {interaction.guild.name}\n**Reason:** {reason}\n**Moderator:** {interaction.user}",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            # Send confirmation
            embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"**Member:** {member} (`{member.id}`)\n**Reason:** {reason}\n**Moderator:** {interaction.user}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"User {member} muted in {interaction.guild.name} by {interaction.user}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to mute this member.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error muting member: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while trying to mute the member.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(MuteCog(bot))