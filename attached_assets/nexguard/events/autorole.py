"""
AutoRole Event Handler for NexGuard Discord Bot
Automatically assigns configured roles to new members when they join
"""

import discord
from discord.ext import commands
import logging
import asyncio

logger = logging.getLogger(__name__)

class AutoRoleEventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle autorole assignment when members join"""
        try:
            # Get database connection
            from ..database.persistent_db import DatabaseManager
            db_path = "nexguard/database/nexguard.db"
            db = DatabaseManager(db_path)
            
            # Get autorole settings
            settings = db.get_guild_settings(member.guild.id)
            autorole_settings = eval(settings.get("autorole_settings", "{'enabled': False, 'roles': []}"))
            
            # Check if autorole is enabled
            if not autorole_settings.get("enabled", False):
                return
            
            # Get role IDs to assign
            role_ids = autorole_settings.get("roles", [])
            if not role_ids:
                return
            
            # Get actual role objects
            roles_to_assign = []
            for role_id in role_ids:
                role = member.guild.get_role(role_id)
                if role:
                    # Check if bot can assign this role
                    if role.position < member.guild.me.top_role.position and not role.managed:
                        roles_to_assign.append(role)
                    else:
                        logger.warning(f"Cannot assign role {role.name} in {member.guild.name} - insufficient permissions")
            
            if not roles_to_assign:
                logger.info(f"No valid roles to assign to {member.display_name} in {member.guild.name}")
                return
            
            # Add a small delay to avoid rate limits
            await asyncio.sleep(1)
            
            # Assign roles
            try:
                await member.add_roles(*roles_to_assign, reason="AutoRole - Automatic role assignment")
                
                # Log success
                role_names = [role.name for role in roles_to_assign]
                logger.info(f"AutoRole: Assigned roles {role_names} to {member.display_name} in {member.guild.name}")
                
                # Log to database
                db.log_member_event(
                    member.guild.id,
                    member.id,
                    "autorole_assigned",
                    f"Assigned roles: {', '.join(role_names)}"
                )
                
                # Send log to autorole log channel if configured
                await self.send_autorole_log(member, roles_to_assign)
                
            except discord.Forbidden:
                logger.error(f"AutoRole: Missing permissions to assign roles to {member.display_name} in {member.guild.name}")
            except discord.HTTPException as e:
                logger.error(f"AutoRole: HTTP error assigning roles to {member.display_name} in {member.guild.name}: {e}")
            except Exception as e:
                logger.error(f"AutoRole: Unexpected error assigning roles to {member.display_name} in {member.guild.name}: {e}")
                
        except Exception as e:
            logger.error(f"AutoRole: Error in on_member_join handler: {e}")
    
    async def send_autorole_log(self, member, assigned_roles):
        """Send autorole log message to configured channel"""
        try:
            # Get database connection
            from ..database.persistent_db import DatabaseManager
            db_path = "nexguard/database/nexguard.db"
            db = DatabaseManager(db_path)
            
            # Get log channel settings
            settings = db.get_guild_settings(member.guild.id)
            log_settings = eval(settings.get("log_settings", "{}"))
            
            # Check if member logs are enabled and channel is configured
            if not log_settings.get("member_logs", {}).get("enabled", False):
                return
            
            channel_id = log_settings.get("member_logs", {}).get("channel_id")
            if not channel_id:
                return
            
            # Get log channel
            log_channel = member.guild.get_channel(channel_id)
            if not log_channel:
                return
            
            # Create log embed
            embed = discord.Embed(
                title="🤖 AutoRole Assignment",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(
                name="Member",
                value=f"{member.mention} ({member.display_name})",
                inline=True
            )
            
            embed.add_field(
                name="Assigned Roles",
                value="\n".join([f"• {role.mention}" for role in assigned_roles]),
                inline=False
            )
            
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"User ID: {member.id}")
            
            await log_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"AutoRole: Error sending log message: {e}")

async def setup(bot):
    await bot.add_cog(AutoRoleEventsCog(bot))