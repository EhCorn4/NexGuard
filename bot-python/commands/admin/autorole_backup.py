"""
AutoRole System for NexGuard Discord Bot
Automatically assigns roles to new members when they join the server
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from ...utils.checks import is_admin
from ...utils.helpers import EmbedBuilder

logger = logging.getLogger(__name__)

class AutoRoleView(discord.ui.View):
    def __init__(self, ctx, roles):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.roles = roles
        self.selected_roles = []
        
        # Create dropdown with roles
        self.add_item(RoleSelectDropdown(roles))
        
    async def on_timeout(self):
        """Handle timeout"""
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass

class RoleSelectDropdown(discord.ui.Select):
    def __init__(self, roles):
        # Create options for dropdown (max 25 roles)
        options = []
        for role in roles[:25]:  # Discord limit of 25 options
            # Show role type and member count
            role_type = "🤖" if role.managed else "👤"
            member_count = len(role.members)
            
            options.append(discord.SelectOption(
                label=f"{role.name}",
                description=f"{role_type} {member_count} members",
                value=str(role.id)
            ))
        
        super().__init__(
            placeholder="Select roles to auto-assign to new members...",
            min_values=0,
            max_values=len(options),
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle role selection"""
        try:
            selected_role_ids = [int(role_id) for role_id in self.values]
            selected_roles = [interaction.guild.get_role(role_id) for role_id in selected_role_ids]
            selected_roles = [role for role in selected_roles if role]  # Remove None values
            
            # Get database connection
            from ...database.persistent_db import DatabaseManager
            db_path = "nexguard/database/nexguard.db"
            db = DatabaseManager(db_path)
            
            # Update autorole settings
            autorole_data = {
                "enabled": len(selected_roles) > 0,
                "roles": selected_role_ids
            }
            
            # Use direct database update to avoid column issues
            conn = db.get_connection()
            cursor = conn.cursor()
            try:
                # Check if guild exists
                cursor.execute('SELECT guild_id FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
                exists = cursor.fetchone()
                
                if exists:
                    # Update existing guild
                    cursor.execute('''
                        UPDATE guild_settings SET autorole_settings = ? WHERE guild_id = ?
                    ''', (str(autorole_data), interaction.guild.id))
                else:
                    # Insert new guild
                    cursor.execute('''
                        INSERT INTO guild_settings (guild_id, autorole_settings) VALUES (?, ?)
                    ''', (interaction.guild.id, str(autorole_data)))
                
                conn.commit()
            finally:
                conn.close()
            
            # Create response embed
            embed = discord.Embed(
                title="✅ AutoRole Configuration Updated",
                color=discord.Color.green()
            )
            
            if selected_roles:
                embed.add_field(
                    name="Auto-Assigned Roles",
                    value="\n".join([f"• {role.mention}" for role in selected_roles]),
                    inline=False
                )
                embed.add_field(
                    name="Status",
                    value="✅ AutoRole is now **enabled**",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Status",
                    value="❌ AutoRole is now **disabled**",
                    inline=False
                )
            
            embed.add_field(
                name="How it works",
                value="New members will automatically receive the selected roles when they join the server.",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            logger.error(f"Error in autorole callback: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while updating autorole settings.",
                ephemeral=True
            )

class AutoRoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="autorole-setup", description="Configure automatic role assignment for new members")
    @app_commands.describe(
        action="Choose to enable/disable or view current autorole settings"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Configure Roles", value="configure"),
        app_commands.Choice(name="View Settings", value="view"),
        app_commands.Choice(name="Test AutoRole", value="test"),
        app_commands.Choice(name="Disable AutoRole", value="disable")
    ])
    async def autorole_setup(self, interaction: discord.Interaction, action: str):
        """Configure autorole settings"""
        await interaction.response.defer()
        
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send(
                embed=await send_error_embed("❌ You need Administrator permissions to configure autorole settings."),
                ephemeral=True
            )
            return
        
        try:
            # Get database connection
            from ...database.persistent_db import DatabaseManager
            db_path = "nexguard/database/nexguard.db"
            db = DatabaseManager(db_path)
            
            if action == "test":
                # Test autorole functionality
                conn = db.get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute('SELECT autorole_settings FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
                    result = cursor.fetchone()
                    autorole_settings = {"enabled": False, "roles": []}
                    if result and result[0]:
                        try:
                            autorole_settings = eval(result[0])
                        except:
                            pass
                finally:
                    conn.close()
                
                embed = discord.Embed(
                    title="🧪 AutoRole Test",
                    color=discord.Color.blue()
                )
                
                if not autorole_settings.get("enabled", False):
                    embed.add_field(
                        name="Status",
                        value="❌ AutoRole is disabled",
                        inline=False
                    )
                    embed.add_field(
                        name="Action Required",
                        value="Configure autorole settings first using the 'Configure Roles' option",
                        inline=False
                    )
                else:
                    role_ids = autorole_settings.get("roles", [])
                    roles = [interaction.guild.get_role(role_id) for role_id in role_ids]
                    valid_roles = [role for role in roles if role]
                    
                    if valid_roles:
                        embed.add_field(
                            name="✅ AutoRole is Active",
                            value=f"New members will receive {len(valid_roles)} role(s):",
                            inline=False
                        )
                        embed.add_field(
                            name="Roles to Assign",
                            value="\n".join([f"• {role.mention}" for role in valid_roles]),
                            inline=False
                        )
                        embed.add_field(
                            name="Test Instructions",
                            value="When a new member joins, they will automatically receive these roles.",
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name="⚠️ Configuration Issue",
                            value="AutoRole is enabled but no valid roles are configured",
                            inline=False
                        )
                
                await interaction.followup.send(embed=embed)
                
            elif action == "view":
                # Show current settings
                settings = db.get_guild_settings(interaction.guild.id)
                autorole_settings = eval(settings.get("autorole_settings", "{'enabled': False, 'roles': []}"))
                
                embed = discord.Embed(
                    title="🔧 AutoRole Settings",
                    color=discord.Color.blue()
                )
                
                if autorole_settings.get("enabled", False):
                    role_ids = autorole_settings.get("roles", [])
                    roles = [interaction.guild.get_role(role_id) for role_id in role_ids]
                    valid_roles = [role for role in roles if role]
                    
                    if valid_roles:
                        embed.add_field(
                            name="Status",
                            value="✅ **Enabled**",
                            inline=True
                        )
                        embed.add_field(
                            name="Auto-Assigned Roles",
                            value="\n".join([f"• {role.mention}" for role in valid_roles]),
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name="Status",
                            value="❌ **Disabled** (no valid roles)",
                            inline=True
                        )
                else:
                    embed.add_field(
                        name="Status",
                        value="❌ **Disabled**",
                        inline=True
                    )
                
                await interaction.followup.send(embed=embed)
                
            elif action == "disable":
                # Disable autorole
                autorole_data = {
                    "enabled": False,
                    "roles": []
                }
                
                db.update_guild_setting(interaction.guild.id, "autorole_settings", str(autorole_data))
                
                embed = discord.Embed(
                    title="✅ AutoRole Disabled",
                    description="AutoRole has been disabled for this server.",
                    color=discord.Color.green()
                )
                
                await interaction.followup.send(embed=embed)
                
            else:  # configure
                # Get all roles (excluding @everyone and managed roles that can't be assigned)
                assignable_roles = [
                    role for role in interaction.guild.roles
                    if role != interaction.guild.default_role and 
                    role.position < interaction.guild.me.top_role.position and
                    not role.managed
                ]
                
                if not assignable_roles:
                    embed = discord.Embed(
                        title="❌ No Assignable Roles",
                        description="There are no roles available that can be auto-assigned to new members.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed)
                    return
                
                # Sort roles by position (highest first)
                assignable_roles.sort(key=lambda r: r.position, reverse=True)
                
                # Create configuration embed
                embed = discord.Embed(
                    title="🔧 AutoRole Configuration",
                    description="Select the roles that should be automatically assigned to new members when they join the server.",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="Instructions",
                    value="• Select multiple roles from the dropdown menu below\n"
                          "• Only roles the bot can assign will be shown\n"
                          "• Selected roles will be given to all new members\n"
                          "• Leave empty to disable autorole",
                    inline=False
                )
                
                # Create view with dropdown
                view = AutoRoleView(interaction, assignable_roles)
                message = await interaction.followup.send(embed=embed, view=view)
                view.message = message
                
        except Exception as e:
            logger.error(f"Error in autorole setup: {e}")
            await interaction.followup.send(
                embed=await send_error_embed(f"❌ An error occurred: {str(e)}"),
                ephemeral=True
            )
    
    @app_commands.command(name="autorole-stats", description="View autorole statistics and recent activity")
    async def autorole_stats(self, interaction: discord.Interaction):
        """View autorole statistics"""
        await interaction.response.defer()
        
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send(
                embed=await send_error_embed("❌ You need Administrator permissions to view autorole statistics."),
                ephemeral=True
            )
            return
        
        try:
            # Get database connection
            from ...database.persistent_db import DatabaseManager
            db_path = "nexguard/database/nexguard.db"
            db = DatabaseManager(db_path)
            
            # Get autorole settings
            settings = db.get_guild_settings(interaction.guild.id)
            autorole_settings = eval(settings.get("autorole_settings", "{'enabled': False, 'roles': []}"))
            
            # Get recent autorole events from member logs
            recent_autoroles = db.execute_query(
                "SELECT user_id, additional_info, timestamp FROM member_logs WHERE guild_id = ? AND action = 'autorole_assigned' ORDER BY timestamp DESC LIMIT 10",
                (interaction.guild.id,)
            )
            
            embed = discord.Embed(
                title="📊 AutoRole Statistics",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            # Current status
            if autorole_settings.get("enabled", False):
                role_ids = autorole_settings.get("roles", [])
                roles = [interaction.guild.get_role(role_id) for role_id in role_ids]
                valid_roles = [role for role in roles if role]
                
                embed.add_field(
                    name="Status",
                    value="✅ **Enabled**",
                    inline=True
                )
                embed.add_field(
                    name="Configured Roles",
                    value=f"{len(valid_roles)} role(s)",
                    inline=True
                )
            else:
                embed.add_field(
                    name="Status",
                    value="❌ **Disabled**",
                    inline=True
                )
                embed.add_field(
                    name="Configured Roles",
                    value="0 roles",
                    inline=True
                )
            
            # Recent activity
            if recent_autoroles:
                recent_activity = []
                for user_id, additional_info, timestamp in recent_autoroles[:5]:
                    user = interaction.guild.get_member(user_id)
                    user_name = user.display_name if user else f"User {user_id}"
                    recent_activity.append(f"• {user_name} - {additional_info}")
                
                embed.add_field(
                    name="Recent AutoRole Activity",
                    value="\n".join(recent_activity) if recent_activity else "No recent activity",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Recent AutoRole Activity",
                    value="No recent activity",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in autorole stats: {e}")
            await interaction.followup.send(
                embed=await send_error_embed(f"❌ An error occurred: {str(e)}"),
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AutoRoleCog(bot))