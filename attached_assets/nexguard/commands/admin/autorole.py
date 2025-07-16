import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
from ...utils.helpers import EmbedBuilder

logger = logging.getLogger(__name__)

class AutoRoleView(discord.ui.View):
    def __init__(self, roles):
        super().__init__(timeout=300)
        self.roles = roles
        self.add_item(RoleSelectDropdown(roles))

class RoleSelectDropdown(discord.ui.Select):
    def __init__(self, roles):
        options = []
        for role in roles[:25]:  # Discord limit
            role_type = "🤖" if role.managed else "👤"
            options.append(discord.SelectOption(
                label=role.name,
                description=f"{role_type} {len(role.members)} members",
                value=str(role.id)
            ))
        
        super().__init__(
            placeholder="Select roles to auto-assign to new members...",
            min_values=0,
            max_values=len(options),
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        selected_role_ids = [int(role_id) for role_id in self.values]
        selected_roles = [interaction.guild.get_role(role_id) for role_id in selected_role_ids]
        selected_roles = [role for role in selected_roles if role]
        
        # Save to database
        from ...database.persistent_db import DatabaseManager
        db = DatabaseManager("nexguard/database/nexguard.db")
        
        autorole_data = {
            "enabled": len(selected_roles) > 0,
            "roles": selected_role_ids
        }
        
        db.update_guild_setting(interaction.guild.id, "autorole_settings", json.dumps(autorole_data))
        
        embed = EmbedBuilder.success(
            "AutoRole Configuration Updated",
            f"{'✅ Enabled' if selected_roles else '❌ Disabled'} - {len(selected_roles)} role(s) configured"
        )
        
        if selected_roles:
            embed.add_field(
                name="Auto-Assigned Roles",
                value="\n".join([f"• {role.mention}" for role in selected_roles]),
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=None)

class AutoRoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="autorole", description="Configure automatic role assignment for new members")
    @app_commands.describe(
        action="Action to perform",
        roles="Roles to assign (for quick setup)"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Configure", value="configure"),
            app_commands.Choice(name="Status", value="status"),
            app_commands.Choice(name="Disable", value="disable")
        ]
    )
    async def autorole(self, interaction: discord.Interaction, action: str = "configure", roles: str = None):
        """Configure automatic role assignment"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                embed=EmbedBuilder.error("Permission Denied", "You need Administrator permissions to configure AutoRole."),
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        from ...database.persistent_db import DatabaseManager
        db = DatabaseManager("nexguard/database/nexguard.db")
        
        if action == "status":
            settings = db.get_guild_settings(interaction.guild.id)
            autorole_settings = json.loads(settings.get("autorole_settings", '{"enabled": false, "roles": []}'))
            
            embed = EmbedBuilder.info("AutoRole Status")
            embed.add_field(
                name="Status",
                value="✅ Enabled" if autorole_settings.get("enabled", False) else "❌ Disabled",
                inline=True
            )
            
            if autorole_settings.get("enabled", False):
                role_ids = autorole_settings.get("roles", [])
                roles = [interaction.guild.get_role(role_id) for role_id in role_ids]
                valid_roles = [role for role in roles if role]
                
                if valid_roles:
                    embed.add_field(
                        name="Configured Roles",
                        value="\n".join([f"• {role.mention}" for role in valid_roles]),
                        inline=False
                    )
            
            await interaction.followup.send(embed=embed)
        
        elif action == "disable":
            autorole_data = {"enabled": False, "roles": []}
            db.update_guild_setting(interaction.guild.id, "autorole_settings", json.dumps(autorole_data))
            
            embed = EmbedBuilder.success("AutoRole Disabled", "AutoRole has been disabled for this server.")
            await interaction.followup.send(embed=embed)
        
        else:  # configure
            assignable_roles = [
                role for role in interaction.guild.roles
                if role != interaction.guild.default_role and 
                role.position < interaction.guild.me.top_role.position and
                not role.managed
            ]
            
            if not assignable_roles:
                embed = EmbedBuilder.error(
                    "No Assignable Roles",
                    "There are no roles available that can be auto-assigned to new members."
                )
                await interaction.followup.send(embed=embed)
                return
            
            assignable_roles.sort(key=lambda r: r.position, reverse=True)
            
            embed = EmbedBuilder.info(
                "AutoRole Configuration",
                "Select the roles that should be automatically assigned to new members."
            )
            
            view = AutoRoleView(assignable_roles)
            await interaction.followup.send(embed=embed, view=view)
    
    @app_commands.command(name="autorole-stats", description="View autorole statistics")
    async def autorole_stats(self, interaction: discord.Interaction):
        """View autorole statistics"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                embed=EmbedBuilder.error("Permission Denied", "You need Administrator permissions to view autorole statistics."),
                ephemeral=True
            )
            return
        
        from ...database.persistent_db import DatabaseManager
        db = DatabaseManager("nexguard/database/nexguard.db")
        
        settings = db.get_guild_settings(interaction.guild.id)
        autorole_settings = json.loads(settings.get("autorole_settings", '{"enabled": false, "roles": []}'))
        
        embed = EmbedBuilder.info("AutoRole Statistics")
        
        if autorole_settings.get("enabled", False):
            role_ids = autorole_settings.get("roles", [])
            roles = [interaction.guild.get_role(role_id) for role_id in role_ids]
            valid_roles = [role for role in roles if role]
            
            embed.add_field(name="Status", value="✅ Enabled", inline=True)
            embed.add_field(name="Configured Roles", value=str(len(valid_roles)), inline=True)
        else:
            embed.add_field(name="Status", value="❌ Disabled", inline=True)
            embed.add_field(name="Configured Roles", value="0", inline=True)
        
        # Get recent activity
        recent_autoroles = db.execute_query(
            "SELECT user_id, additional_info FROM member_logs WHERE guild_id = ? AND action = 'autorole_assigned' ORDER BY timestamp DESC LIMIT 5",
            (interaction.guild.id,)
        )
        
        if recent_autoroles:
            activity = []
            for user_id, info in recent_autoroles:
                user = interaction.guild.get_member(user_id)
                user_name = user.display_name if user else f"User {user_id}"
                activity.append(f"• {user_name}")
            
            embed.add_field(
                name="Recent Activity",
                value="\n".join(activity),
                inline=False
            )
        else:
            embed.add_field(name="Recent Activity", value="No recent activity", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoRoleCog(bot))