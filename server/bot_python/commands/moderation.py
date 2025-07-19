import discord
from discord.ext import commands, tasks
from discord import app_commands
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class ModerationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_expired_bans.start()
    
    def cog_unload(self):
        self.check_expired_bans.cancel()
    
    @tasks.loop(minutes=5)  # Check every 5 minutes
    async def check_expired_bans(self):
        """Check for expired temporary bans and automatically unban users"""
        try:
            if not self.bot.db_pool:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                # Get expired bans
                expired_bans = await conn.fetch("""
                    SELECT guild_id, user_id, username 
                    FROM ban_list 
                    WHERE ban_type = 'temporary' 
                    AND expires_at <= $1 
                    AND is_active = TRUE
                """, datetime.utcnow())
                
                for ban_record in expired_bans:
                    try:
                        guild = self.bot.get_guild(int(ban_record['guild_id']))
                        if not guild:
                            continue
                            
                        # Unban the user
                        user = await self.bot.fetch_user(int(ban_record['user_id']))
                        await guild.unban(user, reason="Temporary ban expired")
                        
                        # Update ban record as inactive
                        await conn.execute("""
                            UPDATE ban_list SET is_active = FALSE, updated_at = $1
                            WHERE guild_id = $2 AND user_id = $3 AND is_active = TRUE
                        """, datetime.utcnow(), ban_record['guild_id'], ban_record['user_id'])
                        
                        # Log the automatic unban
                        await conn.execute("""
                            INSERT INTO moderation_logs (guild_id, user_id, moderator_id, action, reason)
                            VALUES ($1, $2, $3, $4, $5)
                        """, ban_record['guild_id'], ban_record['user_id'], str(self.bot.user.id), 
                            "auto_unban", "Temporary ban expired")
                        
                        logger.info(f"Automatically unbanned {ban_record['username']} (ID: {ban_record['user_id']}) from guild {ban_record['guild_id']}")
                        
                    except Exception as e:
                        logger.error(f"Failed to auto-unban user {ban_record['user_id']}: {e}")
                        
        except Exception as e:
            logger.error(f"Error checking expired bans: {e}")
    
    @check_expired_bans.before_loop
    async def before_check_expired_bans(self):
        await self.bot.wait_until_ready()
    
    async def log_moderation_action(self, guild_id: str, user_id: str, moderator_id: str, action: str, reason: str = None, duration: str = None):
        """Log moderation action to database"""
        try:
            if not self.bot.db_pool:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO moderation_logs (guild_id, user_id, moderator_id, action, reason, duration)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, guild_id, user_id, moderator_id, action, reason, duration)
        except Exception as e:
            logger.error(f"Failed to log moderation action: {e}")
    
    def parse_duration(self, duration_str: str) -> timedelta:
        """Parse duration string like '7d', '2h', '30m' into timedelta"""
        import re
        if not duration_str:
            return None
            
        # Match pattern like '7d', '2h', '30m', '1w'
        match = re.match(r'^(\d+)([dhwm])$', duration_str.lower())
        if not match:
            return None
            
        amount = int(match.group(1))
        unit = match.group(2)
        
        if unit == 'm':  # minutes
            return timedelta(minutes=amount)
        elif unit == 'h':  # hours
            return timedelta(hours=amount)
        elif unit == 'd':  # days
            return timedelta(days=amount)
        elif unit == 'w':  # weeks
            return timedelta(weeks=amount)
        
        return None

    async def add_to_banlist(self, guild_id: str, user_id: str, username: str, moderator_id: str, moderator_name: str, reason: str = None, ban_type: str = "permanent", duration: str = None):
        """Add user to banlist"""
        try:
            if not self.bot.db_pool:
                return
                
            expires_at = None
            if ban_type == "temporary" and duration:
                duration_delta = self.parse_duration(duration)
                if duration_delta:
                    expires_at = datetime.utcnow() + duration_delta
                
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO ban_list (guild_id, user_id, username, moderator_id, moderator_name, reason, ban_type, duration, expires_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, guild_id, user_id, username, moderator_id, moderator_name, reason, ban_type, duration, expires_at)
        except Exception as e:
            logger.error(f"Failed to add to banlist: {e}")
    
    async def add_warning(self, guild_id: str, user_id: str, username: str, moderator_id: str, moderator_name: str, reason: str, severity: str = "medium"):
        """Add warning to user"""
        try:
            if not self.bot.db_pool:
                return
                
            # Calculate points based on severity
            points = {"low": 1, "medium": 2, "high": 3, "severe": 5}.get(severity, 2)
            
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO warn_history (guild_id, user_id, username, moderator_id, moderator_name, reason, severity, points)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, guild_id, user_id, username, moderator_id, moderator_name, reason, severity, points)
        except Exception as e:
            logger.error(f"Failed to add warning: {e}")
    
    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(
        user="The user to ban",
        reason="Reason for the ban",
        duration="Duration for temporary ban (e.g., 7d, 2h, 30m) - leave empty for permanent",
        delete_days="Number of days of messages to delete (0-7)"
    )
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided", duration: str = None, delete_days: int = 0):
        """Ban a user from the server"""
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ You don't have permission to ban members.", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You cannot ban this user due to role hierarchy.", ephemeral=True)
            return
        
        # Validate duration if provided
        duration_delta = None
        expires_at = None
        ban_type = "permanent"
        
        if duration:
            duration_delta = self.parse_duration(duration)
            if not duration_delta:
                await interaction.response.send_message("❌ Invalid duration format. Use formats like: 7d, 2h, 30m, 1w", ephemeral=True)
                return
            expires_at = datetime.utcnow() + duration_delta
            ban_type = "temporary"
        
        try:
            # Send DM to user
            try:
                if ban_type == "temporary":
                    embed = discord.Embed(
                        title="You have been temporarily banned",
                        description=f"You have been temporarily banned from **{interaction.guild.name}**",
                        color=0xFF6600,
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Duration", value=duration, inline=True)
                    embed.add_field(name="Expires", value=f"<t:{int(expires_at.timestamp())}:F>", inline=True)
                    embed.add_field(name="Reason", value=reason, inline=False)
                    embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                else:
                    embed = discord.Embed(
                        title="You have been banned",
                        description=f"You have been permanently banned from **{interaction.guild.name}**",
                        color=0xFF0000,
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Reason", value=reason, inline=False)
                    embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                await user.send(embed=embed)
            except:
                pass  # User has DMs disabled
            
            # Ban the user
            ban_reason = f"{'Temporary ban' if ban_type == 'temporary' else 'Permanent ban'}: {reason}"
            await user.ban(reason=ban_reason, delete_message_days=max(0, min(7, delete_days)))
            
            # Log the action
            action_type = "tempban" if ban_type == "temporary" else "ban"
            await self.log_moderation_action(
                str(interaction.guild.id), str(user.id), str(interaction.user.id), 
                action_type, reason, duration
            )
            
            # Add to banlist
            await self.add_to_banlist(
                str(interaction.guild.id), str(user.id), user.name,
                str(interaction.user.id), interaction.user.name, reason, ban_type, duration
            )
            
            # Create response embed
            if ban_type == "temporary":
                embed = discord.Embed(
                    title="User Temporarily Banned",
                    description=f"**{user.name}** has been temporarily banned from the server.",
                    color=0xFF6600,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Duration", value=duration, inline=True)
                embed.add_field(name="Expires", value=f"<t:{int(expires_at.timestamp())}:F>", inline=True)
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            else:
                embed = discord.Embed(
                    title="User Banned",
                    description=f"**{user.name}** has been permanently banned from the server.",
                    color=0xFF0000,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Log command usage
            parameters = {"user": user.mention, "reason": reason}
            if duration:
                parameters["duration"] = duration
            await self.bot.log_command_usage(interaction, "ban", parameters)
            
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            await interaction.response.send_message("❌ Failed to ban user. Please try again.", ephemeral=True)
    
    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(
        user="The user to kick",
        reason="Reason for the kick"
    )
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Kick a user from the server"""
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("❌ You don't have permission to kick members.", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You cannot kick this user due to role hierarchy.", ephemeral=True)
            return
        
        try:
            # Send DM to user
            try:
                embed = discord.Embed(
                    title="You have been kicked",
                    description=f"You have been kicked from **{interaction.guild.name}**",
                    color=0xFF8000,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                await user.send(embed=embed)
            except:
                pass  # User has DMs disabled
            
            # Kick the user
            await user.kick(reason=reason)
            
            # Log the action
            await self.log_moderation_action(
                str(interaction.guild.id), str(user.id), str(interaction.user.id), 
                "kick", reason
            )
            
            embed = discord.Embed(
                title="User Kicked",
                description=f"**{user.name}** has been kicked from the server.",
                color=0xFF8000,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Log command usage
            parameters = {"user": user.mention, "reason": reason}
            await self.bot.log_command_usage(interaction, "kick", parameters)
            
        except Exception as e:
            logger.error(f"Error kicking user: {e}")
            await interaction.response.send_message("❌ Failed to kick user. Please try again.", ephemeral=True)
    
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.describe(
        user="The user to warn",
        reason="Reason for the warning",
        severity="Warning severity level"
    )
    @app_commands.choices(severity=[
        app_commands.Choice(name="Low", value="low"),
        app_commands.Choice(name="Medium", value="medium"),
        app_commands.Choice(name="High", value="high"),
        app_commands.Choice(name="Severe", value="severe")
    ])
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str, severity: str = "medium"):
        """Warn a user"""
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ You don't have permission to warn members.", ephemeral=True)
            return
        
        try:
            # Send DM to user
            try:
                embed = discord.Embed(
                    title="You have been warned",
                    description=f"You have been warned in **{interaction.guild.name}**",
                    color=0xFFFF00,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Severity", value=severity.capitalize(), inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                await user.send(embed=embed)
            except:
                pass  # User has DMs disabled
            
            # Log the action
            await self.log_moderation_action(
                str(interaction.guild.id), str(user.id), str(interaction.user.id), 
                "warn", reason
            )
            
            # Add to warning history
            await self.add_warning(
                str(interaction.guild.id), str(user.id), user.name,
                str(interaction.user.id), interaction.user.name, reason, severity
            )
            
            embed = discord.Embed(
                title="User Warned",
                description=f"**{user.name}** has been warned.",
                color=0xFFFF00,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Severity", value=severity.capitalize(), inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Log command usage
            parameters = {"user": user.mention, "reason": reason, "severity": severity}
            await self.bot.log_command_usage(interaction, "warn", parameters)
            
        except Exception as e:
            logger.error(f"Error warning user: {e}")
            await interaction.response.send_message("❌ Failed to warn user. Please try again.", ephemeral=True)
    
    @app_commands.command(name="timeout", description="Timeout a user")
    @app_commands.describe(
        user="The user to timeout",
        duration="Duration in minutes",
        reason="Reason for the timeout"
    )
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: int, reason: str = "No reason provided"):
        """Timeout a user"""
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ You don't have permission to timeout members.", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You cannot timeout this user due to role hierarchy.", ephemeral=True)
            return
        
        if duration < 1 or duration > 40320:  # Discord limit: 28 days
            await interaction.response.send_message("❌ Duration must be between 1 minute and 28 days (40320 minutes).", ephemeral=True)
            return
        
        try:
            timeout_until = datetime.utcnow() + timedelta(minutes=duration)
            
            # Send DM to user
            try:
                embed = discord.Embed(
                    title="You have been timed out",
                    description=f"You have been timed out in **{interaction.guild.name}**",
                    color=0xFF8000,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                await user.send(embed=embed)
            except:
                pass  # User has DMs disabled
            
            # Timeout the user
            await user.timeout(timeout_until, reason=reason)
            
            # Log the action
            await self.log_moderation_action(
                str(interaction.guild.id), str(user.id), str(interaction.user.id), 
                "timeout", reason, f"{duration}m"
            )
            
            embed = discord.Embed(
                title="User Timed Out",
                description=f"**{user.name}** has been timed out for {duration} minutes.",
                color=0xFF8000,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Log command usage
            parameters = {"user": user.mention, "duration": f"{duration} minutes", "reason": reason}
            await self.bot.log_command_usage(interaction, "timeout", parameters)
            
        except Exception as e:
            logger.error(f"Error timing out user: {e}")
            await interaction.response.send_message("❌ Failed to timeout user. Please try again.", ephemeral=True)
    
    @app_commands.command(name="untimeout", description="Remove timeout from a user")
    @app_commands.describe(
        user="The user to remove timeout from",
        reason="Reason for removing the timeout"
    )
    async def untimeout(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Remove timeout from a user"""
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ You don't have permission to manage member timeouts.", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You cannot manage timeouts for this user due to role hierarchy.", ephemeral=True)
            return
        
        # Check if user is actually timed out
        if not user.is_timed_out():
            await interaction.response.send_message("❌ This user is not currently timed out.", ephemeral=True)
            return
        
        try:
            # Remove timeout from user
            await user.timeout(None, reason=reason)
            
            # Send DM to user
            try:
                embed = discord.Embed(
                    title="Timeout Removed",
                    description=f"Your timeout has been removed in **{interaction.guild.name}**",
                    color=0x00FF00,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                await user.send(embed=embed)
            except:
                pass  # User has DMs disabled
            
            # Log the action
            await self.log_moderation_action(
                str(interaction.guild.id), str(user.id), str(interaction.user.id), 
                "untimeout", reason
            )
            
            embed = discord.Embed(
                title="Timeout Removed",
                description=f"**{user.name}**'s timeout has been removed.",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Log command usage
            parameters = {"user": user.mention, "reason": reason}
            await self.bot.log_command_usage(interaction, "untimeout", parameters)
            
        except Exception as e:
            logger.error(f"Error removing timeout from user: {e}")
            await interaction.response.send_message("❌ Failed to remove timeout from user. Please try again.", ephemeral=True)
    
    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.describe(
        user_id="The ID of the user to unban",
        reason="Reason for the unban"
    )
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        """Unban a user"""
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ You don't have permission to unban members.", ephemeral=True)
            return
        
        try:
            # Get user object
            user = await self.bot.fetch_user(int(user_id))
            
            # Unban the user
            await interaction.guild.unban(user, reason=reason)
            
            # Log the action
            await self.log_moderation_action(
                str(interaction.guild.id), str(user.id), str(interaction.user.id), 
                "unban", reason
            )
            
            # Update banlist
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE ban_list SET is_active = FALSE, updated_at = $1
                        WHERE guild_id = $2 AND user_id = $3 AND is_active = TRUE
                    """, datetime.utcnow(), str(interaction.guild.id), str(user.id))
            
            embed = discord.Embed(
                title="User Unbanned",
                description=f"**{user.name}** has been unbanned.",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Log command usage
            parameters = {"user_id": user_id, "reason": reason}
            await self.bot.log_command_usage(interaction, "unban", parameters)
            
        except discord.NotFound:
            await interaction.response.send_message("❌ User not found or not banned.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            await interaction.response.send_message("❌ Failed to unban user. Please try again.", ephemeral=True)
    
    @app_commands.command(name="purge", description="Delete multiple messages")
    @app_commands.describe(
        amount="Number of messages to delete (1-100)",
        user="Only delete messages from this user"
    )
    async def purge(self, interaction: discord.Interaction, amount: int, user: discord.Member = None):
        """Delete multiple messages"""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You don't have permission to manage messages.", ephemeral=True)
            return
        
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Amount must be between 1 and 100.", ephemeral=True)
            return
        
        try:
            await interaction.response.defer()
            
            def check(message):
                if user:
                    return message.author == user
                return True
            
            deleted = await interaction.channel.purge(limit=amount, check=check)
            
            # Log the action
            await self.log_moderation_action(
                str(interaction.guild.id), str(user.id) if user else "N/A", 
                str(interaction.user.id), "purge", f"Deleted {len(deleted)} messages"
            )
            
            embed = discord.Embed(
                title="Messages Purged",
                description=f"Successfully deleted {len(deleted)} messages.",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            if user:
                embed.add_field(name="User", value=user.mention, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Log command usage
            parameters = {"amount": amount}
            if user:
                parameters["user"] = user.mention
            await self.bot.log_command_usage(interaction, "purge", parameters)
            
        except Exception as e:
            logger.error(f"Error purging messages: {e}")
            await interaction.followup.send("❌ Failed to purge messages. Please try again.", ephemeral=True)
    
    @app_commands.command(name="mute", description="Mute a user by adding the configured mute role")
    @app_commands.describe(
        user="The user to mute",
        reason="Reason for the mute"
    )
    async def mute(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Mute a user by adding the configured mute role"""
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ You don't have permission to mute members.", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You cannot mute this user due to role hierarchy.", ephemeral=True)
            return
        
        try:
            # Get mute role from guild settings
            mute_role = None
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    result = await conn.fetchrow("SELECT mute_role_id FROM guilds WHERE id = $1", str(interaction.guild.id))
                    if result and result['mute_role_id']:
                        mute_role = interaction.guild.get_role(int(result['mute_role_id']))
            
            # If no mute role configured, try to find one named "Muted"
            if not mute_role:
                mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
                
            # If still no mute role, create one
            if not mute_role:
                try:
                    mute_role = await interaction.guild.create_role(
                        name="Muted",
                        color=discord.Color.dark_grey(),
                        reason="Auto-created mute role for moderation"
                    )
                    
                    # Set up channel permissions for the mute role
                    for channel in interaction.guild.channels:
                        try:
                            if isinstance(channel, discord.TextChannel):
                                await channel.set_permissions(mute_role, send_messages=False, add_reactions=False)
                            elif isinstance(channel, discord.VoiceChannel):
                                await channel.set_permissions(mute_role, speak=False, stream=False)
                        except discord.Forbidden:
                            continue  # Skip channels we can't modify
                    
                    # Save mute role to database
                    if self.bot.db_pool:
                        async with self.bot.db_pool.acquire() as conn:
                            await conn.execute(
                                "UPDATE guilds SET mute_role_id = $1 WHERE id = $2",
                                str(mute_role.id), str(interaction.guild.id)
                            )
                            
                except discord.Forbidden:
                    await interaction.response.send_message("❌ I don't have permission to create roles. Please create a 'Muted' role manually or set one using admin commands.", ephemeral=True)
                    return
            
            # Check if user is already muted
            if mute_role in user.roles:
                await interaction.response.send_message(f"❌ {user.mention} is already muted.", ephemeral=True)
                return
            
            # Add mute role to user
            await user.add_roles(mute_role, reason=reason)
            
            # Send DM to user
            try:
                embed = discord.Embed(
                    title="You have been muted",
                    description=f"You have been muted in **{interaction.guild.name}**",
                    color=0xFF8000,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                await user.send(embed=embed)
            except:
                pass  # User has DMs disabled
            
            # Log the action
            await self.log_moderation_action(
                str(interaction.guild.id), str(user.id), str(interaction.user.id), 
                "mute", reason
            )
            
            embed = discord.Embed(
                title="User Muted",
                description=f"**{user.name}** has been muted.",
                color=0xFF8000,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            embed.add_field(name="Mute Role", value=mute_role.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Log command usage
            parameters = {"user": user.mention, "reason": reason}
            await self.bot.log_command_usage(interaction, "mute", parameters)
            
        except Exception as e:
            logger.error(f"Error muting user: {e}")
            await interaction.response.send_message("❌ Failed to mute user. Please try again.", ephemeral=True)
    
    @app_commands.command(name="unmute", description="Unmute a user by removing the configured mute role")
    @app_commands.describe(
        user="The user to unmute",
        reason="Reason for the unmute"
    )
    async def unmute(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Unmute a user by removing the configured mute role"""
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ You don't have permission to unmute members.", ephemeral=True)
            return
        
        try:
            # Get mute role from guild settings
            mute_role = None
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    result = await conn.fetchrow("SELECT mute_role_id FROM guilds WHERE id = $1", str(interaction.guild.id))
                    if result and result['mute_role_id']:
                        mute_role = interaction.guild.get_role(int(result['mute_role_id']))
            
            # If no mute role configured, try to find one named "Muted"
            if not mute_role:
                mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
                
            if not mute_role:
                await interaction.response.send_message("❌ No mute role found. Please configure a mute role first.", ephemeral=True)
                return
            
            # Check if user is actually muted
            if mute_role not in user.roles:
                await interaction.response.send_message(f"❌ {user.mention} is not currently muted.", ephemeral=True)
                return
            
            # Remove mute role from user
            await user.remove_roles(mute_role, reason=reason)
            
            # Send DM to user
            try:
                embed = discord.Embed(
                    title="You have been unmuted",
                    description=f"You have been unmuted in **{interaction.guild.name}**",
                    color=0x00FF00,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                await user.send(embed=embed)
            except:
                pass  # User has DMs disabled
            
            # Log the action
            await self.log_moderation_action(
                str(interaction.guild.id), str(user.id), str(interaction.user.id), 
                "unmute", reason
            )
            
            embed = discord.Embed(
                title="User Unmuted",
                description=f"**{user.name}** has been unmuted.",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Log command usage
            parameters = {"user": user.mention, "reason": reason}
            await self.bot.log_command_usage(interaction, "unmute", parameters)
            
        except Exception as e:
            logger.error(f"Error unmuting user: {e}")
            await interaction.response.send_message("❌ Failed to unmute user. Please try again.", ephemeral=True)

    @app_commands.command(name="lock", description="Lock a channel to prevent members from sending messages")
    @app_commands.describe(
        channel="The channel to lock (defaults to current channel)",
        reason="Reason for locking the channel"
    )
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel = None, reason: str = "No reason provided"):
        """Lock a channel"""
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You don't have permission to manage channels.", ephemeral=True)
            return
        
        if channel is None:
            channel = interaction.channel
        
        try:
            # Get @everyone role
            everyone_role = interaction.guild.default_role
            
            # Check if channel is already locked
            current_perms = channel.overwrites_for(everyone_role)
            if current_perms.send_messages is False:
                await interaction.response.send_message(f"❌ {channel.mention} is already locked.", ephemeral=True)
                return
            
            # Lock the channel by denying send_messages
            await channel.set_permissions(everyone_role, send_messages=False, reason=f"Channel locked by {interaction.user}: {reason}")
            
            # Log the action
            await self.log_moderation_action(
                str(interaction.guild.id), str(channel.id), str(interaction.user.id), 
                "lock", f"Locked #{channel.name}: {reason}"
            )
            
            # Create response embed
            embed = discord.Embed(
                title="🔒 Channel Locked",
                description=f"**{channel.mention}** has been locked.",
                color=0xFF6600,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Send lock notification to the channel
            lock_embed = discord.Embed(
                title="🔒 Channel Locked",
                description=f"This channel has been locked by {interaction.user.mention}",
                color=0xFF6600,
                timestamp=datetime.utcnow()
            )
            lock_embed.add_field(name="Reason", value=reason, inline=False)
            
            await channel.send(embed=lock_embed)
            
            # Log command usage
            parameters = {"channel": channel.mention, "reason": reason}
            await self.bot.log_command_usage(interaction, "lock", parameters)
            
        except Exception as e:
            logger.error(f"Error locking channel: {e}")
            await interaction.response.send_message("❌ Failed to lock channel. Please try again.", ephemeral=True)
    
    @app_commands.command(name="unlock", description="Unlock a channel to allow members to send messages")
    @app_commands.describe(
        channel="The channel to unlock (defaults to current channel)",
        reason="Reason for unlocking the channel"
    )
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel = None, reason: str = "No reason provided"):
        """Unlock a channel"""
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You don't have permission to manage channels.", ephemeral=True)
            return
        
        if channel is None:
            channel = interaction.channel
        
        try:
            # Get @everyone role
            everyone_role = interaction.guild.default_role
            
            # Check if channel is already unlocked
            current_perms = channel.overwrites_for(everyone_role)
            if current_perms.send_messages is not False:
                await interaction.response.send_message(f"❌ {channel.mention} is not locked.", ephemeral=True)
                return
            
            # Unlock the channel by removing the send_messages override
            await channel.set_permissions(everyone_role, send_messages=None, reason=f"Channel unlocked by {interaction.user}: {reason}")
            
            # Log the action
            await self.log_moderation_action(
                str(interaction.guild.id), str(channel.id), str(interaction.user.id), 
                "unlock", f"Unlocked #{channel.name}: {reason}"
            )
            
            # Create response embed
            embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description=f"**{channel.mention}** has been unlocked.",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Send unlock notification to the channel
            unlock_embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description=f"This channel has been unlocked by {interaction.user.mention}",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            unlock_embed.add_field(name="Reason", value=reason, inline=False)
            
            await channel.send(embed=unlock_embed)
            
            # Log command usage
            parameters = {"channel": channel.mention, "reason": reason}
            await self.bot.log_command_usage(interaction, "unlock", parameters)
            
        except Exception as e:
            logger.error(f"Error unlocking channel: {e}")
            await interaction.response.send_message("❌ Failed to unlock channel. Please try again.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationCommands(bot))