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
                    SELECT mod_role_id FROM guilds WHERE id = $1
                ''', guild_id)
                
                return int(result['mod_role_id']) if result and result['mod_role_id'] else None
        except Exception as e:
            logger.error(f"Error getting mod role ID: {e}")
            return None
    
    async def set_mod_role_id(self, guild_id: str, role_id: int = None):
        """Set the moderation role ID for a guild"""
        if not self.bot.db_pool:
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO guilds (id, name, mod_role_id, joined_at, updated_at)
                    VALUES ($1, 'Unknown', $2, NOW(), NOW())
                    ON CONFLICT (id) 
                    DO UPDATE SET mod_role_id = $2, updated_at = NOW()
                ''', guild_id, str(role_id) if role_id else None)
        except Exception as e:
            logger.error(f"Error setting mod role ID: {e}")
    
    @app_commands.command(name='modrole', description='Set the minimum role required for moderation commands')
    @app_commands.describe(
        role="The role that will be able to use moderation commands (and roles above it)"
    )
    async def modrole(self, interaction: discord.Interaction, role: discord.Role = None):
        """Set or view the minimum role required for moderation commands"""
        
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
                        value="Users with this role or any role above it can use moderation commands.",
                        inline=False
                    )
                    embed.add_field(
                        name="🛠️ Affected Commands",
                        value="`/ban`, `/kick`, `/mute`, `/unmute`, `/timeout`, `/warn`, `/purge`, `/slowmode`, `/lock`, `/unlock`",
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
                description="You cannot set a moderation role that is higher than or equal to your highest role.",
                color=COLORS['ERROR']
            )
            embed.add_field(
                name="💡 Solution",
                value="Choose a role that is below your highest role in the hierarchy.",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Save the mod role
        await self.set_mod_role_id(str(interaction.guild.id), role.id)
        
        # Create success embed
        embed = discord.Embed(
            title=f"{EMOJIS['SUCCESS']} Moderation Role Set",
            description=f"Successfully set {role.mention} as the moderation role!",
            color=COLORS['SUCCESS']
        )
        
        embed.add_field(
            name=f"{EMOJIS['STATS']} Role Information",
            value=f"**Role:** {role.name}\n**Members:** {len(role.members)}\n**Position:** {role.position}",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Affected Commands",
            value="`/ban`, `/kick`, `/mute`, `/unmute`, `/timeout`, `/warn`, `/purge`, `/slowmode`, `/lock`, `/unlock`",
            inline=False
        )
        
        embed.add_field(
            name=f"{EMOJIS['INFO']} How It Works",
            value="Users with this role or any role above it can now use moderation commands.",
            inline=False
        )
        
        embed.set_footer(text="Use /modrole with no arguments to view the current setting")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        logger.info(f"Moderation role set to {role.name} by {interaction.user} in {interaction.guild.name}")
    
    @app_commands.command(name='resetmodrole', description='Reset moderation role to default (Moderate Members permission)')
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
        
        # Remove the mod role setting
        await self.set_mod_role_id(str(interaction.guild.id), None)
        
        embed = discord.Embed(
            title=f"{EMOJIS['SUCCESS']} Moderation Role Reset",
            description="Successfully reset the moderation role to default!",
            color=COLORS['SUCCESS']
        )
        
        embed.add_field(
            name="📝 Default Behavior",
            value="Users with 'Moderate Members' permission can now use moderation commands.",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Affected Commands",
            value="`/ban`, `/kick`, `/mute`, `/unmute`, `/timeout`, `/warn`, `/purge`, `/slowmode`, `/lock`, `/unlock`",
            inline=False
        )
        
        embed.add_field(
            name="💡 Next Steps",
            value="To set a custom moderation role again, use `/modrole <role>`.",
            inline=False
        )
        
        embed.set_footer(text="Moderation commands now use Discord's default permissions")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        logger.info(f"Moderation role reset by {interaction.user} in {interaction.guild.name}")
    
    @app_commands.command(name='modpermissions', description='Check moderation permissions for a user')
    @app_commands.describe(
        user="The user to check moderation permissions for"
    )
    async def modpermissions(self, interaction: discord.Interaction, user: discord.Member = None):
        """Check if a user has moderation permissions"""
        
        # Default to the command user if no user specified
        if user is None:
            user = interaction.user
        
        # Check if command user has permissions to view this
        if not (interaction.user.guild_permissions.administrator or 
                interaction.user.guild_permissions.manage_guild or
                user == interaction.user):
            embed = discord.Embed(
                title=f"{EMOJIS['ERROR']} Permission Denied",
                description="You can only check your own permissions unless you have Administrator or Manage Server permission.",
                color=COLORS['ERROR']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check moderation permissions
        has_default_perms = user.guild_permissions.moderate_members
        has_admin_perms = user.guild_permissions.administrator
        
        # Check custom mod role
        current_role_id = await self.get_mod_role_id(str(interaction.guild.id))
        has_custom_role = False
        custom_role_name = None
        
        if current_role_id:
            custom_role = interaction.guild.get_role(current_role_id)
            if custom_role:
                custom_role_name = custom_role.name
                # Check if user has the mod role or a higher role
                user_top_role_position = user.top_role.position
                has_custom_role = (custom_role in user.roles or 
                                 user_top_role_position >= custom_role.position)
        
        # Determine overall permission status
        can_moderate = has_admin_perms or has_default_perms or has_custom_role
        
        embed = discord.Embed(
            title=f"{EMOJIS['SHIELD']} Moderation Permissions",
            description=f"Permission check for {user.mention}",
            color=COLORS['SUCCESS'] if can_moderate else COLORS['ERROR']
        )
        
        # Permission breakdown
        permissions_text = ""
        if has_admin_perms:
            permissions_text += f"{EMOJIS['SUCCESS']} Administrator\n"
        else:
            permissions_text += f"{EMOJIS['ERROR']} Administrator\n"
        
        if has_default_perms:
            permissions_text += f"{EMOJIS['SUCCESS']} Moderate Members\n"
        else:
            permissions_text += f"{EMOJIS['ERROR']} Moderate Members\n"
        
        if current_role_id and custom_role_name:
            if has_custom_role:
                permissions_text += f"{EMOJIS['SUCCESS']} Custom Mod Role ({custom_role_name})\n"
            else:
                permissions_text += f"{EMOJIS['ERROR']} Custom Mod Role ({custom_role_name})\n"
        else:
            permissions_text += f"{EMOJIS['INFO']} No custom mod role set\n"
        
        embed.add_field(
            name="Permission Sources",
            value=permissions_text,
            inline=False
        )
        
        embed.add_field(
            name="Overall Status",
            value=f"{'✅ Can use moderation commands' if can_moderate else '❌ Cannot use moderation commands'}",
            inline=False
        )
        
        if user.top_role:
            embed.add_field(
                name="User Information",
                value=f"**Highest Role:** {user.top_role.mention}\n**Role Position:** {user.top_role.position}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModRoleCog(bot))