#!/usr/bin/env python3

import discord
from discord.ext import commands, tasks
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Set, Optional
import json
from collections import defaultdict, deque
import time

logger = logging.getLogger(__name__)

class AntiRaidSystem(commands.Cog):
    """Advanced anti-raid protection system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.raid_detection_active = True
        
        # Raid detection thresholds
        self.JOIN_THRESHOLD = 10  # users joining
        self.JOIN_TIMEFRAME = 60  # within 60 seconds
        self.MESSAGE_SPAM_THRESHOLD = 15  # messages
        self.MESSAGE_SPAM_TIMEFRAME = 30  # within 30 seconds
        self.MENTION_SPAM_THRESHOLD = 10  # mentions in a message
        
        # Tracking dictionaries
        self.recent_joins: Dict[int, deque] = defaultdict(lambda: deque(maxlen=50))
        self.message_tracking: Dict[int, Dict[int, deque]] = defaultdict(lambda: defaultdict(lambda: deque(maxlen=100)))
        self.raid_guilds: Set[int] = set()
        self.lockdown_guilds: Set[int] = set()
        
        # Start background tasks
        self.cleanup_tracking.start()
        logger.info("Anti-Raid system initialized")
    
    async def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.cleanup_tracking.cancel()
    
    @tasks.loop(minutes=5)
    async def cleanup_tracking(self):
        """Clean up old tracking data"""
        try:
            current_time = time.time()
            cutoff_time = current_time - 300  # 5 minutes ago
            
            # Clean up join tracking
            for guild_id in list(self.recent_joins.keys()):
                join_queue = self.recent_joins[guild_id]
                while join_queue and join_queue[0] < cutoff_time:
                    join_queue.popleft()
                
                if not join_queue:
                    del self.recent_joins[guild_id]
            
            # Clean up message tracking
            for guild_id in list(self.message_tracking.keys()):
                guild_messages = self.message_tracking[guild_id]
                for user_id in list(guild_messages.keys()):
                    message_queue = guild_messages[user_id]
                    while message_queue and message_queue[0] < cutoff_time:
                        message_queue.popleft()
                    
                    if not message_queue:
                        del guild_messages[user_id]
                
                if not guild_messages:
                    del self.message_tracking[guild_id]
                    
        except Exception as e:
            logger.error(f"Error in anti-raid cleanup: {e}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Monitor member joins for raid detection"""
        if not self.raid_detection_active:
            return
        
        # Global whitelist - skip anti-raid checks for trusted users
        if member.id in [409889861441421315, 1365321309130588160, 904858290461241375]:
            return
        
        # Server owner bypass - owners are always trusted
        if member.id == member.guild.owner_id:
            return
            
        try:
            guild = member.guild
            current_time = time.time()
            
            # Add join to tracking
            self.recent_joins[guild.id].append(current_time)
            
            # Check for raid pattern
            recent_join_count = len([
                join_time for join_time in self.recent_joins[guild.id]
                if current_time - join_time <= self.JOIN_TIMEFRAME
            ])
            
            if recent_join_count >= self.JOIN_THRESHOLD:
                await self.handle_potential_raid(guild, "mass_joins", {
                    'join_count': recent_join_count,
                    'timeframe': self.JOIN_TIMEFRAME
                })
                
            # Check suspicious account patterns
            await self.check_suspicious_account(member)
            
        except Exception as e:
            logger.error(f"Error in anti-raid member join handler: {e}")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Monitor messages for spam and raid patterns"""
        if not message.guild or message.author.bot:
            return
            
        if not self.raid_detection_active:
            return
        
        # Global whitelist - skip anti-raid checks for trusted users  
        if message.author.id in [409889861441421315, 1365321309130588160, 904858290461241375]:
            return
        
        # Server owner bypass - owners are always trusted
        if message.author.id == message.guild.owner_id:
            return
            
        try:
            guild = message.guild
            user = message.author
            current_time = time.time()
            
            # Track message frequency
            self.message_tracking[guild.id][user.id].append(current_time)
            
            # Check for message spam
            recent_messages = len([
                msg_time for msg_time in self.message_tracking[guild.id][user.id]
                if current_time - msg_time <= self.MESSAGE_SPAM_TIMEFRAME
            ])
            
            if recent_messages >= self.MESSAGE_SPAM_THRESHOLD:
                await self.handle_spam_user(user, message.channel, "message_spam", {
                    'message_count': recent_messages,
                    'timeframe': self.MESSAGE_SPAM_TIMEFRAME
                })
            
            # Check for mention spam
            if len(message.mentions) >= self.MENTION_SPAM_THRESHOLD:
                await self.handle_spam_user(user, message.channel, "mention_spam", {
                    'mention_count': len(message.mentions)
                })
            
            # Check for invite spam
            if "discord.gg/" in message.content.lower() or "discordapp.com/invite/" in message.content.lower():
                await self.handle_spam_user(user, message.channel, "invite_spam", {
                    'message_content': message.content[:100]
                })
                
        except Exception as e:
            logger.error(f"Error in anti-raid message handler: {e}")
    
    async def handle_potential_raid(self, guild: discord.Guild, raid_type: str, details: dict):
        """Handle detected raid attempts"""
        try:
            if guild.id in self.raid_guilds:
                return  # Already handling raid for this guild
                
            self.raid_guilds.add(guild.id)
            logger.warning(f"RAID DETECTED in {guild.name}: {raid_type} - {details}")
            
            # Get anti-raid settings from database
            settings = await self.get_antiraid_settings(guild.id)
            
            if settings.get('auto_lockdown', True):
                await self.activate_lockdown(guild)
            
            if settings.get('notify_moderators', True):
                await self.notify_moderators(guild, raid_type, details)
            
            if settings.get('auto_ban_recent_joins', False) and raid_type == "mass_joins":
                await self.ban_recent_suspicious_joins(guild)
            
            # Schedule raid cooldown
            await asyncio.sleep(300)  # 5 minute cooldown
            if guild.id in self.raid_guilds:
                self.raid_guilds.remove(guild.id)
                
        except Exception as e:
            logger.error(f"Error handling potential raid: {e}")
    
    async def handle_spam_user(self, user: discord.Member, channel: discord.TextChannel, spam_type: str, details: dict):
        """Handle individual spam users"""
        try:
            logger.warning(f"SPAM DETECTED: {user} in {channel.guild.name} - {spam_type}")
            
            # Delete recent messages
            try:
                async for message in channel.history(limit=50):
                    if message.author == user and (datetime.now(timezone.utc) - message.created_at.replace(tzinfo=timezone.utc)).seconds < 60:
                        await message.delete()
            except discord.Forbidden:
                pass
            
            # Timeout user
            try:
                await user.timeout(timedelta(minutes=10), reason=f"Anti-raid: {spam_type}")
            except discord.Forbidden:
                pass
            
            # Log the action
            await self.log_antiraid_action(channel.guild, "spam_timeout", {
                'user': str(user),
                'spam_type': spam_type,
                'details': details
            })
            
        except Exception as e:
            logger.error(f"Error handling spam user: {e}")
    
    async def activate_lockdown(self, guild: discord.Guild):
        """Activate server lockdown"""
        try:
            if guild.id in self.lockdown_guilds:
                return
                
            self.lockdown_guilds.add(guild.id)
            logger.info(f"Activating lockdown for {guild.name}")
            
            # Create lockdown role with no permissions
            lockdown_role = None
            for role in guild.roles:
                if role.name == "NexGuard-Lockdown":
                    lockdown_role = role
                    break
            
            if not lockdown_role:
                lockdown_role = await guild.create_role(
                    name="NexGuard-Lockdown",
                    permissions=discord.Permissions.none(),
                    reason="Anti-raid lockdown role"
                )
            
            # Restrict @everyone permissions in all channels
            overwrites_backup = {}
            for channel in guild.channels:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                    overwrites_backup[channel.id] = channel.overwrites
                    
                    await channel.set_permissions(
                        guild.default_role,
                        send_messages=False,
                        connect=False,
                        reason="Anti-raid lockdown"
                    )
            
            # Store backup for restoration
            await self.store_lockdown_backup(guild.id, overwrites_backup)
            
            # Send lockdown notification
            embed = discord.Embed(
                title="🔒 Server Lockdown Activated",
                description="Anti-raid protection has been activated due to suspicious activity.",
                color=0xFF0000,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Duration", value="Manual or automatic restoration", inline=True)
            embed.add_field(name="Reason", value="Potential raid detected", inline=True)
            
            # Try to send to system channel or first available channel
            notification_channel = guild.system_channel
            if not notification_channel:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        notification_channel = channel
                        break
            
            if notification_channel:
                await notification_channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error activating lockdown: {e}")
    
    async def check_suspicious_account(self, member: discord.Member):
        """Check if joining account is suspicious"""
        try:
            now = datetime.now(timezone.utc)
            created_at = member.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            
            account_age = now - created_at
            
            # Flag accounts created within last 24 hours
            if account_age < timedelta(hours=24):
                logger.info(f"Suspicious new account: {member} (age: {account_age})")
                
                # Add to monitoring list
                if not hasattr(self, 'suspicious_users'):
                    self.suspicious_users = set()
                self.suspicious_users.add(member.id)
                
        except Exception as e:
            logger.error(f"Error checking suspicious account: {e}")
    
    async def get_antiraid_settings(self, guild_id: int) -> dict:
        """Get anti-raid settings from database"""
        try:
            if not self.bot.db_pool:
                return {
                    'auto_lockdown': True,
                    'notify_moderators': True,
                    'auto_ban_recent_joins': False
                }
                
            async with self.bot.db_pool.acquire() as conn:
                result = await conn.fetchrow(
                    "SELECT settings FROM antiraid_config WHERE guild_id = $1",
                    str(guild_id)
                )
                
                if result:
                    return json.loads(result['settings'])
                else:
                    return {
                        'auto_lockdown': True,
                        'notify_moderators': True,
                        'auto_ban_recent_joins': False
                    }
                    
        except Exception as e:
            logger.error(f"Error getting anti-raid settings: {e}")
            return {
                'auto_lockdown': True,
                'notify_moderators': True,
                'auto_ban_recent_joins': False
            }
    
    async def notify_moderators(self, guild: discord.Guild, raid_type: str, details: dict):
        """Notify moderators of raid detection"""
        try:
            embed = discord.Embed(
                title="⚠️ Raid Detection Alert",
                description=f"Anti-raid system detected suspicious activity",
                color=0xFF6600,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Type", value=raid_type.replace("_", " ").title(), inline=True)
            embed.add_field(name="Server", value=guild.name, inline=True)
            embed.add_field(name="Time", value=f"<t:{int(datetime.utcnow().timestamp())}:f>", inline=True)
            
            for key, value in details.items():
                embed.add_field(name=key.replace("_", " ").title(), value=str(value), inline=True)
            
            # Send to logging channel or system channel
            for channel in guild.text_channels:
                if "log" in channel.name.lower() or "mod" in channel.name.lower():
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send(embed=embed)
                        break
                        
        except Exception as e:
            logger.error(f"Error notifying moderators: {e}")
    
    async def log_antiraid_action(self, guild: discord.Guild, action: str, details: dict):
        """Log anti-raid actions to database"""
        try:
            if not self.bot.db_pool:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO antiraid_logs (guild_id, action, details, timestamp)
                    VALUES ($1, $2, $3, $4)
                """, str(guild.id), action, json.dumps(details), datetime.utcnow())
                
        except Exception as e:
            logger.error(f"Error logging anti-raid action: {e}")
    
    async def store_lockdown_backup(self, guild_id: int, overwrites_backup: dict):
        """Store channel overwrites backup for lockdown restoration"""
        try:
            if not self.bot.db_pool:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO lockdown_backups (guild_id, overwrites_data, created_at)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (guild_id) DO UPDATE SET
                        overwrites_data = EXCLUDED.overwrites_data,
                        created_at = EXCLUDED.created_at
                """, str(guild_id), json.dumps(overwrites_backup, default=str), datetime.utcnow())
                
        except Exception as e:
            logger.error(f"Error storing lockdown backup: {e}")
    
    @discord.app_commands.command(name="antiraid")
    @discord.app_commands.describe(
        action="Action to perform",
        setting="Setting to configure"
    )
    async def antiraid_command(self, interaction: discord.Interaction, 
                              action: str, setting: str = None):
        """Configure anti-raid protection settings"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need administrator permissions to use this command.",
                ephemeral=True
            )
            return
        
        if action.lower() == "status":
            embed = discord.Embed(
                title="🛡️ Anti-Raid Status",
                color=0x00FF00 if self.raid_detection_active else 0xFF0000,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="Detection Status",
                value="Active" if self.raid_detection_active else "Disabled",
                inline=True
            )
            
            embed.add_field(
                name="Lockdown Status", 
                value="Active" if interaction.guild.id in self.lockdown_guilds else "None",
                inline=True
            )
            
            embed.add_field(
                name="Recent Joins Tracked",
                value=len(self.recent_joins.get(interaction.guild.id, [])),
                inline=True
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        elif action.lower() == "unlock":
            if interaction.guild.id in self.lockdown_guilds:
                # TODO: Implement lockdown restoration
                self.lockdown_guilds.remove(interaction.guild.id)
                await interaction.response.send_message(
                    "🔓 Server lockdown has been lifted.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Server is not currently in lockdown.",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                "❌ Invalid action. Use: `status`, `unlock`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AntiRaidSystem(bot))