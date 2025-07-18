import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class ModerationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
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
    
    async def add_to_banlist(self, guild_id: str, user_id: str, username: str, moderator_id: str, moderator_name: str, reason: str = None, ban_type: str = "permanent", duration: str = None):
        """Add user to banlist"""
        try:
            if not self.bot.db_pool:
                return
                
            expires_at = None
            if ban_type == "temporary" and duration:
                # Parse duration (e.g., "7d", "1h", "30m")
                expires_at = datetime.utcnow() + timedelta(days=7)  # Default 7 days
                
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
        delete_days="Number of days of messages to delete (0-7)"
    )
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided", delete_days: int = 0):
        """Ban a user from the server"""
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ You don't have permission to ban members.", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You cannot ban this user due to role hierarchy.", ephemeral=True)
            return
        
        try:
            # Send DM to user
            try:
                embed = discord.Embed(
                    title="You have been banned",
                    description=f"You have been banned from **{interaction.guild.name}**",
                    color=0xFF0000,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                await user.send(embed=embed)
            except:
                pass  # User has DMs disabled
            
            # Ban the user
            await user.ban(reason=reason, delete_message_days=max(0, min(7, delete_days)))
            
            # Log the action
            await self.log_moderation_action(
                str(interaction.guild.id), str(user.id), str(interaction.user.id), 
                "ban", reason
            )
            
            # Add to banlist
            await self.add_to_banlist(
                str(interaction.guild.id), str(user.id), user.name,
                str(interaction.user.id), interaction.user.name, reason
            )
            
            embed = discord.Embed(
                title="User Banned",
                description=f"**{user.name}** has been banned from the server.",
                color=0xFF0000,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
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
            
        except Exception as e:
            logger.error(f"Error timing out user: {e}")
            await interaction.response.send_message("❌ Failed to timeout user. Please try again.", ephemeral=True)
    
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
            
        except Exception as e:
            logger.error(f"Error purging messages: {e}")
            await interaction.followup.send("❌ Failed to purge messages. Please try again.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationCommands(bot))