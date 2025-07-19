import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import logging

logger = logging.getLogger(__name__)

class ModRoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='modrole', description='Set the minimum role required for moderation commands')
    @app_commands.describe(
        role="The role that will be able to use moderation commands (and roles above it)"
    )
    async def modrole(self, interaction: discord.Interaction, role: discord.Role = None):
        """Set the minimum role required for moderation commands"""
        
        # Check if user is administrator
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need Administrator permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if role is None:
            # Show current mod role
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT mod_role_id FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
            result = cursor.fetchone()
            conn.close()
            
            current_role_id = result[0] if result and result[0] else None
            
            if current_role_id:
                current_role = interaction.guild.get_role(current_role_id)
                if current_role:
                    embed = discord.Embed(
                        title="🛡️ Current Moderation Role",
                        description=f"The current moderation role is {current_role.mention}",
                        color=discord.Color.blue()
                    )
                    embed.add_field(
                        name="📊 Role Information",
                        value=f"**Role:** {current_role.name}\n**Members:** {len(current_role.members)}\n**Position:** {current_role.position}",
                        inline=False
                    )
                    embed.add_field(
                        name="ℹ️ How It Works",
                        value="Users with this role or any role above it can use moderation commands.",
                        inline=False
                    )
                else:
                    embed = discord.Embed(
                        title="⚠️ Moderation Role Not Found",
                        description="The configured moderation role no longer exists.",
                        color=discord.Color.orange()
                    )
            else:
                embed = discord.Embed(
                    title="❌ No Moderation Role Set",
                    description="No moderation role has been configured.\nUse `/modrole <role>` to set one.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="📝 Default Behavior",
                    value="Currently, users with 'Moderate Members' permission can use moderation commands.",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate role hierarchy
        if role.position >= interaction.guild.me.top_role.position:
            embed = discord.Embed(
                title="❌ Role Hierarchy Error",
                description="I cannot manage roles that are higher than or equal to my highest role.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if role.position >= interaction.user.top_role.position and interaction.user != interaction.guild.owner:
            embed = discord.Embed(
                title="❌ Role Hierarchy Error", 
                description="You cannot set a moderation role that is higher than or equal to your highest role.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Save the mod role
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO guild_settings (guild_id, mod_role_id)
            VALUES (?, ?)
        ''', (interaction.guild.id, role.id))
        conn.commit()
        conn.close()
        
        # Create success embed
        embed = discord.Embed(
            title="✅ Moderation Role Set",
            description=f"Successfully set {role.mention} as the moderation role!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📊 Role Information",
            value=f"**Role:** {role.name}\n**Members:** {len(role.members)}\n**Position:** {role.position}",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ Affected Commands",
            value="Ban, Kick, Mute, Unmute, Timeout, Warn, Purge, Slowmode, Lock, Unlock",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ How It Works",
            value="Users with this role or any role above it can now use moderation commands.",
            inline=False
        )
        
        embed.set_footer(text="Use /modrole with no arguments to view the current setting")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        logger.info(f"Moderation role set to {role.name} by {interaction.user} in {interaction.guild.name}")
    
    @app_commands.command(name='resetmodrole', description='Reset moderation role to default (Moderate Members permission)')
    async def resetmodrole(self, interaction: discord.Interaction):
        """Reset moderation role to default"""
        
        # Check if user is administrator
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need Administrator permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Remove the mod role setting
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO guild_settings (guild_id, mod_role_id)
            VALUES (?, ?)
        ''', (interaction.guild.id, None))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="✅ Moderation Role Reset",
            description="Successfully reset the moderation role to default!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 Default Behavior",
            value="Users with 'Moderate Members' permission can now use moderation commands.",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ Affected Commands",
            value="Ban, Kick, Mute, Unmute, Timeout, Warn, Purge, Slowmode, Lock, Unlock",
            inline=False
        )
        
        embed.set_footer(text="Use /modrole <role> to set a custom moderation role")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        logger.info(f"Moderation role reset by {interaction.user} in {interaction.guild.name}")

async def setup(bot):
    await bot.add_cog(ModRoleCog(bot))