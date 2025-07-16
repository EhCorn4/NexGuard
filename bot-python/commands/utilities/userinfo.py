import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='userinfo', description='Get information about a user')
    @app_commands.describe(member='The member to get info about (yourself if not specified)')
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        """Get information about a user"""
        if member is None:
            member = interaction.user
        
        # Get user information
        embed = discord.Embed(
            title="👤 User Information",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Basic info
        embed.add_field(
            name="📋 Basic Info",
            value=f"**Username:** {member.name}\n**Display Name:** {member.display_name}\n**ID:** `{member.id}`\n**Bot:** {'Yes' if member.bot else 'No'}",
            inline=False
        )
        
        # Account creation
        account_created = member.created_at
        embed.add_field(
            name="📅 Account Created",
            value=f"<t:{int(account_created.timestamp())}:F>\n<t:{int(account_created.timestamp())}:R>",
            inline=True
        )
        
        # Server join date
        if member.joined_at:
            embed.add_field(
                name="📥 Joined Server",
                value=f"<t:{int(member.joined_at.timestamp())}:F>\n<t:{int(member.joined_at.timestamp())}:R>",
                inline=True
            )
        
        # Status
        status_emojis = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🟡 Idle",
            discord.Status.dnd: "🔴 Do Not Disturb",
            discord.Status.offline: "⚫ Offline"
        }
        
        embed.add_field(
            name="🔍 Status",
            value=status_emojis.get(member.status, "❓ Unknown"),
            inline=True
        )
        
        # Roles
        if len(member.roles) > 1:  # Exclude @everyone
            roles = [role.mention for role in member.roles[1:]]  # Skip @everyone
            roles_text = ", ".join(roles[:10])  # Show first 10 roles
            if len(member.roles) > 11:
                roles_text += f" and {len(member.roles) - 11} more..."
            
            embed.add_field(
                name=f"🎭 Roles ({len(member.roles) - 1})",
                value=roles_text,
                inline=False
            )
        
        # Permissions
        key_permissions = []
        perms = member.guild_permissions
        
        if perms.administrator:
            key_permissions.append("Administrator")
        if perms.manage_guild:
            key_permissions.append("Manage Server")
        if perms.manage_roles:
            key_permissions.append("Manage Roles")
        if perms.manage_channels:
            key_permissions.append("Manage Channels")
        if perms.ban_members:
            key_permissions.append("Ban Members")
        if perms.kick_members:
            key_permissions.append("Kick Members")
        if perms.manage_messages:
            key_permissions.append("Manage Messages")
        
        if key_permissions:
            embed.add_field(
                name="🔑 Key Permissions",
                value=", ".join(key_permissions),
                inline=False
            )
        
        # Activity
        if member.activities:
            activity = member.activities[0]  # Get the first activity
            activity_text = f"**Type:** {activity.type.name.title()}\n**Name:** {activity.name}"
            
            if hasattr(activity, 'details') and activity.details:
                activity_text += f"\n**Details:** {activity.details}"
            
            embed.add_field(
                name="🎮 Activity",
                value=activity_text,
                inline=False
            )
        
        # Boost info
        if member.premium_since:
            embed.add_field(
                name="💎 Server Boost",
                value=f"Boosting since <t:{int(member.premium_since.timestamp())}:F>",
                inline=False
            )
        
        embed.set_footer(text=f"Requested by {interaction.user}")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='avatar', description='Get a user\'s avatar')
    @app_commands.describe(member='The member to get avatar of (yourself if not specified)')
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        """Get a user's avatar"""
        if member is None:
            member = interaction.user
        
        embed = discord.Embed(
            title=f"🖼️ Avatar - {member.display_name}",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_image(url=member.display_avatar.url)
        
        # Add download links
        avatar_urls = []
        avatar_urls.append(f"[PNG]({member.display_avatar.with_format('png').url})")
        avatar_urls.append(f"[JPG]({member.display_avatar.with_format('jpg').url})")
        avatar_urls.append(f"[WEBP]({member.display_avatar.with_format('webp').url})")
        
        if member.display_avatar.is_animated():
            avatar_urls.append(f"[GIF]({member.display_avatar.with_format('gif').url})")
        
        embed.add_field(
            name="🔗 Download Links",
            value=" • ".join(avatar_urls),
            inline=False
        )
        
        embed.set_footer(text=f"Requested by {interaction.user}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfoCog(bot))