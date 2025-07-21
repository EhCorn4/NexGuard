"""
NexGuard Moderation Role System
Advanced role-based permission management for moderation commands
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

# Constants
COLORS = {
    'SUCCESS': 0x00FF00,
    'ERROR': 0xFF0000,
    'INFO': 0x00FFFF,
    'WARNING': 0xFFFF00,
    'BLUE': 0x0000FF
}

EMOJIS = {
    'SUCCESS': '✅',
    'ERROR': '❌',
    'INFO': 'ℹ️',
    'WARNING': '⚠️',
    'SHIELD': '🛡️',
    'STATS': '📊'
}

class ModRoleCog(commands.Cog):
    """Moderation role management system for custom permission control"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("ModRole system initialized")
    
    async def get_mod_role_id(self, guild_id: str) -> int:
        """Get the moderation role ID for a guild"""
        if not self.bot.db_pool:
            return None
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                result = await conn.fetchrow('''
                    SELECT moderator_role_id FROM guilds WHERE id = $1
                ''', guild_id)
                
                return int(result['moderator_role_id']) if result and result['moderator_role_id'] else None
        except Exception as e:
            logger.error(f"Error getting mod role ID: {e}")
            return None
    
    async def get_admin_role_id(self, guild_id: str) -> int:
        """Get the admin role ID for a guild"""
        if not self.bot.db_pool:
            return None
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                result = await conn.fetchrow('''
                    SELECT admin_role_id FROM guilds WHERE id = $1
                ''', guild_id)
                
                return int(result['admin_role_id']) if result and result['admin_role_id'] else None
        except Exception as e:
            logger.error(f"Error getting admin role ID: {e}")
            return None
    
    async def set_mod_role_id(self, guild_id: str, role_id: int = None):
        """Set the moderation role ID for a guild"""
        if not self.bot.db_pool:
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO guilds (id, name, moderator_role_id, joined_at, updated_at)
                    VALUES ($1, 'Unknown', $2, NOW(), NOW())
                    ON CONFLICT (id) 
                    DO UPDATE SET moderator_role_id = $2, updated_at = NOW()
                ''', guild_id, str(role_id) if role_id else None)
        except Exception as e:
            logger.error(f"Error setting mod role ID: {e}")
    
    async def set_admin_role_id(self, guild_id: str, role_id: int = None):
        """Set the admin role ID for a guild"""
        if not self.bot.db_pool:
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO guilds (id, name, admin_role_id, joined_at, updated_at)
                    VALUES ($1, 'Unknown', $2, NOW(), NOW())
                    ON CONFLICT (id) 
                    DO UPDATE SET admin_role_id = $2, updated_at = NOW()
                ''', guild_id, str(role_id) if role_id else None)
        except Exception as e:
            logger.error(f"Error setting admin role ID: {e}")
    
    async def has_mod_permissions(self, user: discord.Member, guild_id: str) -> bool:
        """Check if user has moderator permissions (for mute, unmute, timeout, warn)"""
        # Check Discord permissions first
        if user.guild_permissions.administrator or user.guild_permissions.moderate_members:
            return True
        
        # Check custom mod role
        mod_role_id = await self.get_mod_role_id(guild_id)
        admin_role_id = await self.get_admin_role_id(guild_id)
        
        user_role_ids = [role.id for role in user.roles]
        
        # Check if user has mod role or admin role (admin can do everything mod can)
        if mod_role_id and mod_role_id in user_role_ids:
            return True
        if admin_role_id and admin_role_id in user_role_ids:
            return True
        
        return False
    
    async def has_admin_permissions(self, user: discord.Member, guild_id: str) -> bool:
        """Check if user has admin permissions (for ban, unban, slowmode, lock, unlock)"""
        # Check Discord permissions first
        if user.guild_permissions.administrator or user.guild_permissions.ban_members or user.guild_permissions.manage_channels:
            return True
        
        # Check custom admin role
        admin_role_id = await self.get_admin_role_id(guild_id)
        
        user_role_ids = [role.id for role in user.roles]
        
        # Check if user has admin role
        if admin_role_id and admin_role_id in user_role_ids:
            return True
        
        return False
    
    @app_commands.command(name='modrole', description='Set the role for basic moderation commands (mute, timeout, warn)')
    @app_commands.describe(
        role="The role that will be able to use basic moderation commands"
    )
    async def modrole(self, interaction: discord.Interaction, role: discord.Role = None):
        """Set or view the role required for basic moderation commands"""
        
        # Check if user is administrator
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title=f"{EMOJIS['ERROR']} Permission Denied",
                description="You need Administrator permission to use this command.",
                color=COLORS['ERROR']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if role is None:
            # Show current mod role
            current_role_id = await self.get_mod_role_id(str(interaction.guild.id))
            
            if current_role_id:
                current_role = interaction.guild.get_role(current_role_id)
                if current_role:
                    embed = discord.Embed(
                        title=f"{EMOJIS['SHIELD']} Current Moderation Role",
                        description=f"The current moderation role is {current_role.mention}",
                        color=COLORS['BLUE']
                    )
                    embed.add_field(
                        name=f"{EMOJIS['STATS']} Role Information",
                        value=f"**Role:** {current_role.name}\n**Members:** {len(current_role.members)}\n**Position:** {current_role.position}",
                        inline=False
                    )
                    embed.add_field(
                        name=f"{EMOJIS['INFO']} How It Works",
                        value="Users with this role or admin role can use basic moderation commands.",
                        inline=False
                    )
                    embed.add_field(
                        name="🛠️ Moderation Commands",
                        value="`/mute`, `/unmute`, `/timeout`, `/untimeout`, `/warn`",
                        inline=False
                    )
                else:
                    embed = discord.Embed(
                        title=f"{EMOJIS['WARNING']} Moderation Role Not Found",
                        description="The configured moderation role no longer exists.\nUse `/modrole <role>` to set a new one.",
                        color=COLORS['WARNING']
                    )
            else:
                embed = discord.Embed(
                    title=f"{EMOJIS['ERROR']} No Moderation Role Set",
                    description="No moderation role has been configured.\nUse `/modrole <role>` to set one.",
                    color=COLORS['ERROR']
                )
                embed.add_field(
                    name="📝 Default Behavior",
                    value="Currently, users with 'Moderate Members' permission can use moderation commands.",
                    inline=False
                )
                embed.add_field(
                    name="💡 Tip",
                    value="Setting a custom mod role gives you more precise control over who can moderate your server.",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate role hierarchy - bot's role position
        if role.position >= interaction.guild.me.top_role.position:
            embed = discord.Embed(
                title=f"{EMOJIS['ERROR']} Role Hierarchy Error",
                description="I cannot manage roles that are higher than or equal to my highest role.",
                color=COLORS['ERROR']
            )
            embed.add_field(
                name="💡 Solution",
                value="Move my role higher in the server settings or choose a lower role.",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate role hierarchy - user's role position (except server owner)
        if role.position >= interaction.user.top_role.position and interaction.user != interaction.guild.owner:
            embed = discord.Embed(
                title=f"{EMOJIS['ERROR']} Role Hierarchy Error",
                description="You cannot set a role that is higher than or equal to your highest role.",
                color=COLORS['ERROR']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Set the mod role
        await self.set_mod_role_id(str(interaction.guild.id), role.id)
        
        embed = discord.Embed(
            title=f"{EMOJIS['SUCCESS']} Moderation Role Set",
            description=f"Moderation role has been set to {role.mention}",
            color=COLORS['SUCCESS']
        )
        embed.add_field(
            name="🛠️ Moderation Commands",
            value="`/mute`, `/unmute`, `/timeout`, `/untimeout`, `/warn`",
            inline=False
        )
        embed.add_field(
            name="💡 Note",
            value="Users with this role or admin role can use basic moderation commands.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Moderation role set to {role.name} by {interaction.user.name} in {interaction.guild.name}")
    
    @app_commands.command(name='adminrole', description='Set the role for advanced admin commands (ban, lock, slowmode)')
    @app_commands.describe(
        role="The role that will be able to use advanced admin commands"
    )
    async def adminrole(self, interaction: discord.Interaction, role: discord.Role = None):
        """Set or view the role required for advanced admin commands"""
        
        # Check if user is administrator
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title=f"{EMOJIS['ERROR']} Permission Denied",
                description="You need Administrator permission to use this command.",
                color=COLORS['ERROR']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if role is None:
            # Show current admin role
            current_role_id = await self.get_admin_role_id(str(interaction.guild.id))
            
            if current_role_id:
                current_role = interaction.guild.get_role(current_role_id)
                if current_role:
                    embed = discord.Embed(
                        title=f"{EMOJIS['SHIELD']} Current Admin Role",
                        description=f"The current admin role is {current_role.mention}",
                        color=COLORS['BLUE']
                    )
                    embed.add_field(
                        name=f"{EMOJIS['STATS']} Role Information",
                        value=f"**Role:** {current_role.name}\n**Members:** {len(current_role.members)}\n**Position:** {current_role.position}",
                        inline=False
                    )
                    embed.add_field(
                        name=f"{EMOJIS['INFO']} How It Works",
                        value="Users with this role can use all moderation commands including advanced admin commands.",
                        inline=False
                    )
                    embed.add_field(
                        name="🛠️ Admin Commands",
                        value="`/ban`, `/unban`, `/slowmode`, `/lock`, `/unlock`\n**Plus all moderation commands**",
                        inline=False
                    )
                else:
                    embed = discord.Embed(
                        title=f"{EMOJIS['WARNING']} Admin Role Not Found",
                        description="The configured admin role no longer exists.\nUse `/adminrole <role>` to set a new one.",
                        color=COLORS['WARNING']
                    )
            else:
                embed = discord.Embed(
                    title=f"{EMOJIS['ERROR']} No Admin Role Set",
                    description="No admin role has been configured.\nUse `/adminrole <role>` to set one.",
                    color=COLORS['ERROR']
                )
                embed.add_field(
                    name="📝 Default Behavior",
                    value="Currently, users with 'Ban Members' or 'Manage Channels' permissions can use admin commands.",
                    inline=False
                )
                embed.add_field(
                    name="💡 Tip",
                    value="Setting a custom admin role gives you more precise control over who can use advanced commands.",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate role hierarchy - bot's role position
        if role.position >= interaction.guild.me.top_role.position:
            embed = discord.Embed(
                title=f"{EMOJIS['ERROR']} Role Hierarchy Error",
                description="I cannot manage roles that are higher than or equal to my highest role.",
                color=COLORS['ERROR']
            )
            embed.add_field(
                name="💡 Solution",
                value="Move my role higher in the server settings or choose a lower role.",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate role hierarchy - user's role position (except server owner)
        if role.position >= interaction.user.top_role.position and interaction.user != interaction.guild.owner:
            embed = discord.Embed(
                title=f"{EMOJIS['ERROR']} Role Hierarchy Error",
                description="You cannot set a role that is higher than or equal to your highest role.",
                color=COLORS['ERROR']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Set the admin role
        await self.set_admin_role_id(str(interaction.guild.id), role.id)
        
        embed = discord.Embed(
            title=f"{EMOJIS['SUCCESS']} Admin Role Set",
            description=f"Admin role has been set to {role.mention}",
            color=COLORS['SUCCESS']
        )
        embed.add_field(
            name="🛠️ Admin Commands",
            value="`/ban`, `/unban`, `/slowmode`, `/lock`, `/unlock`",
            inline=False
        )
        embed.add_field(
            name="🔧 Additional Access",
            value="This role can also use all moderation commands: `/mute`, `/unmute`, `/timeout`, `/untimeout`, `/warn`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Admin role set to {role.name} by {interaction.user.name} in {interaction.guild.name}")
    
    @app_commands.command(name='resetmodrole', description='Reset moderation role to default Discord permissions')
    async def resetmodrole(self, interaction: discord.Interaction):
        """Reset moderation role to default Discord permissions"""
        
        # Check if user is administrator
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title=f"{EMOJIS['ERROR']} Permission Denied",
                description="You need Administrator permission to use this command.",
                color=COLORS['ERROR']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Reset both roles to None
        await self.set_mod_role_id(str(interaction.guild.id), None)
        await self.set_admin_role_id(str(interaction.guild.id), None)
        
        embed = discord.Embed(
            title=f"{EMOJIS['SUCCESS']} Roles Reset",
            description="Both moderation and admin roles have been reset to default Discord permissions.",
            color=COLORS['SUCCESS']
        )
        embed.add_field(
            name="📝 Default Permissions",
            value="**Moderation Commands:** Users with 'Moderate Members' permission\n**Admin Commands:** Users with 'Ban Members', 'Manage Channels', or 'Administrator' permissions",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Mod and admin roles reset by {interaction.user.name} in {interaction.guild.name}")

async def setup(bot):
    await bot.add_cog(ModRoleCog(bot))