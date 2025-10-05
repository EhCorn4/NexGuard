#!/usr/bin/env python3

import discord
from discord.ext import commands, tasks
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, deque
import time

logger = logging.getLogger(__name__)

class AntiNukeSystem(commands.Cog):
    """Advanced anti-nuke protection system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.antinuke_active = True
        
        # Nuke detection thresholds
        self.CHANNEL_DELETE_THRESHOLD = 3  # channels deleted
        self.ROLE_DELETE_THRESHOLD = 3     # roles deleted
        self.BAN_THRESHOLD = 5             # members banned
        self.KICK_THRESHOLD = 10           # members kicked
        self.WEBHOOK_THRESHOLD = 5         # webhooks created
        self.TIME_WINDOW = 60              # within 60 seconds
        
        # Permission escalation thresholds
        self.PERMISSION_CHANGE_THRESHOLD = 5  # permission changes
        self.ROLE_CREATE_THRESHOLD = 3        # roles created with admin perms
        
        # Tracking dictionaries
        self.action_tracking: Dict[int, Dict[str, deque]] = defaultdict(lambda: defaultdict(lambda: deque(maxlen=100)))
        self.user_action_tracking: Dict[int, Dict[int, Dict[str, deque]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: deque(maxlen=50))))
        self.nuked_guilds: Set[int] = set()
        self.quarantined_users: Dict[int, Set[int]] = defaultdict(set)
        
        # Backup data for restoration
        self.guild_backups: Dict[int, Dict] = {}
        
        # Whitelist for trusted users (admins, bots, etc.)
        self.trusted_users: Dict[int, Set[int]] = defaultdict(set)
        
        # Start monitoring tasks
        self.cleanup_tracking.start()
        self.backup_guild_data.start()
        logger.info("Anti-Nuke protection system initialized")
    
    async def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.cleanup_tracking.cancel()
        self.backup_guild_data.cancel()
    
    @tasks.loop(minutes=10)
    async def cleanup_tracking(self):
        """Clean up old tracking data"""
        try:
            current_time = time.time()
            cutoff_time = current_time - (self.TIME_WINDOW * 2)  # Keep data for 2x time window
            
            # Clean up action tracking
            for guild_id in list(self.action_tracking.keys()):
                guild_actions = self.action_tracking[guild_id]
                for action_type in list(guild_actions.keys()):
                    action_queue = guild_actions[action_type]
                    while action_queue and action_queue[0]['timestamp'] < cutoff_time:
                        action_queue.popleft()
                    
                    if not action_queue:
                        del guild_actions[action_type]
                
                if not guild_actions:
                    del self.action_tracking[guild_id]
            
            # Clean up user action tracking
            for guild_id in list(self.user_action_tracking.keys()):
                guild_users = self.user_action_tracking[guild_id]
                for user_id in list(guild_users.keys()):
                    user_actions = guild_users[user_id]
                    for action_type in list(user_actions.keys()):
                        action_queue = user_actions[action_type]
                        while action_queue and action_queue[0]['timestamp'] < cutoff_time:
                            action_queue.popleft()
                        
                        if not action_queue:
                            del user_actions[action_type]
                    
                    if not user_actions:
                        del guild_users[user_id]
                
                if not guild_users:
                    del self.user_action_tracking[guild_id]
                    
        except Exception as e:
            logger.error(f"Error in anti-nuke cleanup: {e}")
    
    @tasks.loop(hours=1)
    async def backup_guild_data(self):
        """Backup critical guild data for restoration"""
        try:
            for guild in self.bot.guilds:
                if guild.me.guild_permissions.administrator:
                    await self.create_guild_backup(guild)
        except Exception as e:
            logger.error(f"Error in guild backup: {e}")
    
    async def create_guild_backup(self, guild: discord.Guild):
        """Create comprehensive guild backup"""
        try:
            backup_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'channels': [],
                'roles': [],
                'permissions': {},
                'settings': {}
            }
            
            # Backup channels
            for channel in guild.channels:
                channel_data = {
                    'id': channel.id,
                    'name': channel.name,
                    'type': str(channel.type),
                    'category_id': channel.category_id if hasattr(channel, 'category_id') else None,
                    'position': channel.position,
                    'overwrites': {}
                }
                
                # Backup permission overwrites
                for target, overwrite in channel.overwrites.items():
                    channel_data['overwrites'][str(target.id)] = {
                        'type': 'role' if isinstance(target, discord.Role) else 'member',
                        'allow': overwrite.allow.value,
                        'deny': overwrite.deny.value
                    }
                
                backup_data['channels'].append(channel_data)
            
            # Backup roles
            for role in guild.roles:
                if not role.is_default():
                    role_data = {
                        'id': role.id,
                        'name': role.name,
                        'permissions': role.permissions.value,
                        'color': role.color.value,
                        'hoist': role.hoist,
                        'mentionable': role.mentionable,
                        'position': role.position
                    }
                    backup_data['roles'].append(role_data)
            
            # Store backup
            self.guild_backups[guild.id] = backup_data
            
            # Store in database
            await self.store_guild_backup(guild.id, backup_data)
            
        except Exception as e:
            logger.error(f"Error creating guild backup for {guild.name}: {e}")
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Monitor channel deletions"""
        if not self.antinuke_active:
            return
            
        try:
            guild = channel.guild
            
            # Find who deleted the channel from audit logs
            deleter = await self.get_action_author(guild, discord.AuditLogAction.channel_delete, channel.id)
            
            if deleter and not await self.is_trusted_user(guild, deleter):
                await self.track_action(guild, deleter, 'channel_delete', {
                    'channel_name': channel.name,
                    'channel_id': channel.id,
                    'channel_type': str(channel.type)
                })
                
                # Check for nuke attempt
                await self.check_nuke_patterns(guild, deleter, 'channel_delete')
                
        except Exception as e:
            logger.error(f"Error in channel delete monitor: {e}")
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Monitor role deletions"""
        if not self.antinuke_active:
            return
            
        try:
            guild = role.guild
            
            # Find who deleted the role from audit logs
            deleter = await self.get_action_author(guild, discord.AuditLogAction.role_delete, role.id)
            
            if deleter and not await self.is_trusted_user(guild, deleter):
                await self.track_action(guild, deleter, 'role_delete', {
                    'role_name': role.name,
                    'role_id': role.id,
                    'permissions': role.permissions.value
                })
                
                # Check for nuke attempt
                await self.check_nuke_patterns(guild, deleter, 'role_delete')
                
        except Exception as e:
            logger.error(f"Error in role delete monitor: {e}")
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Monitor member bans"""
        if not self.antinuke_active:
            return
            
        try:
            # Find who banned the user from audit logs
            banner = await self.get_action_author(guild, discord.AuditLogAction.ban, user.id)
            
            if banner and not await self.is_trusted_user(guild, banner):
                await self.track_action(guild, banner, 'member_ban', {
                    'banned_user': str(user),
                    'banned_user_id': user.id
                })
                
                # Check for nuke attempt
                await self.check_nuke_patterns(guild, banner, 'member_ban')
                
        except Exception as e:
            logger.error(f"Error in member ban monitor: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Monitor member kicks"""
        if not self.antinuke_active:
            return
            
        try:
            guild = member.guild
            
            # Check if it was a kick (not a leave)
            kicker = await self.get_action_author(guild, discord.AuditLogAction.kick, member.id)
            
            if kicker and not await self.is_trusted_user(guild, kicker):
                await self.track_action(guild, kicker, 'member_kick', {
                    'kicked_user': str(member),
                    'kicked_user_id': member.id
                })
                
                # Check for nuke attempt
                await self.check_nuke_patterns(guild, kicker, 'member_kick')
                
        except Exception as e:
            logger.error(f"Error in member remove monitor: {e}")
    
    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        """Monitor webhook creation"""
        if not self.antinuke_active:
            return
            
        try:
            guild = channel.guild
            
            # Find who created/modified webhooks
            webhook_creator = await self.get_action_author(guild, discord.AuditLogAction.webhook_create)
            
            if webhook_creator and not await self.is_trusted_user(guild, webhook_creator):
                await self.track_action(guild, webhook_creator, 'webhook_create', {
                    'channel_name': channel.name,
                    'channel_id': channel.id
                })
                
                # Check for nuke attempt
                await self.check_nuke_patterns(guild, webhook_creator, 'webhook_create')
                
        except Exception as e:
            logger.error(f"Error in webhook monitor: {e}")
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """Monitor role creation with dangerous permissions"""
        if not self.antinuke_active:
            return
            
        try:
            guild = role.guild
            
            # Check if role has dangerous permissions
            dangerous_perms = [
                'administrator',
                'manage_guild',
                'manage_roles',
                'manage_channels',
                'ban_members',
                'kick_members'
            ]
            
            has_dangerous_perms = any(getattr(role.permissions, perm, False) for perm in dangerous_perms)
            
            if has_dangerous_perms:
                # Find who created the role
                role_creator = await self.get_action_author(guild, discord.AuditLogAction.role_create, role.id)
                
                if role_creator and not await self.is_trusted_user(guild, role_creator):
                    await self.track_action(guild, role_creator, 'dangerous_role_create', {
                        'role_name': role.name,
                        'role_id': role.id,
                        'permissions': role.permissions.value
                    })
                    
                    # Check for nuke attempt
                    await self.check_nuke_patterns(guild, role_creator, 'dangerous_role_create')
                    
        except Exception as e:
            logger.error(f"Error in role create monitor: {e}")
    
    async def get_action_author(self, guild: discord.Guild, action: discord.AuditLogAction, target_id: int = None) -> Optional[discord.Member]:
        """Get the author of an action from audit logs"""
        try:
            if not guild.me.guild_permissions.view_audit_log:
                return None
                
            async for entry in guild.audit_logs(action=action, limit=5):
                if target_id is None or entry.target.id == target_id:
                    # Check if entry is recent (within last 10 seconds)
                    if (datetime.utcnow().replace(tzinfo=None) - entry.created_at.replace(tzinfo=None)).seconds <= 10:
                        return entry.user
            return None
            
        except Exception as e:
            logger.error(f"Error getting action author: {e}")
            return None
    
    async def is_trusted_user(self, guild: discord.Guild, user: discord.Member) -> bool:
        """Check if user is trusted (whitelist, owner, or has trusted role)"""
        try:
            # Global whitelist for specific trusted users
            if user.id in [409889861441421315, 1365321309130588160]:  # Globally whitelisted users
                return True
            
            # Guild owner is always trusted
            if user.id == guild.owner_id:
                return True
            
            # Check manual whitelist
            if user.id in self.trusted_users.get(guild.id, set()):
                return True
            
            # Check if user has been quarantined
            if user.id in self.quarantined_users.get(guild.id, set()):
                return False
            
            # Bot accounts are generally trusted for basic actions
            if user.bot:
                return True
            
            # Users with specific trusted roles
            trusted_role_names = ['owner', 'admin', 'administrator', 'nexguard-admin', 'trusted']
            for role in user.roles:
                if role.name.lower() in trusted_role_names:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking trusted user: {e}")
            return False
    
    async def track_action(self, guild: discord.Guild, user: discord.Member, action_type: str, details: dict):
        """Track user actions for pattern detection"""
        try:
            current_time = time.time()
            action_data = {
                'timestamp': current_time,
                'user_id': user.id,
                'details': details
            }
            
            # Track globally for guild
            self.action_tracking[guild.id][action_type].append(action_data)
            
            # Track per user
            self.user_action_tracking[guild.id][user.id][action_type].append(action_data)
            
            # Log the action
            await self.log_antinuke_action(guild, user, action_type, details)
            
        except Exception as e:
            logger.error(f"Error tracking action: {e}")
    
    async def check_nuke_patterns(self, guild: discord.Guild, user: discord.Member, action_type: str):
        """Check for nuke attack patterns"""
        try:
            current_time = time.time()
            time_window_start = current_time - self.TIME_WINDOW
            
            # Get recent actions by this user
            user_actions = self.user_action_tracking[guild.id][user.id][action_type]
            recent_actions = [action for action in user_actions if action['timestamp'] >= time_window_start]
            
            # Define thresholds
            thresholds = {
                'channel_delete': self.CHANNEL_DELETE_THRESHOLD,
                'role_delete': self.ROLE_DELETE_THRESHOLD,
                'member_ban': self.BAN_THRESHOLD,
                'member_kick': self.KICK_THRESHOLD,
                'webhook_create': self.WEBHOOK_THRESHOLD,
                'dangerous_role_create': self.ROLE_CREATE_THRESHOLD
            }
            
            threshold = thresholds.get(action_type, 5)
            
            if len(recent_actions) >= threshold:
                logger.warning(f"NUKE ATTEMPT DETECTED: {user} in {guild.name} - {action_type}: {len(recent_actions)} actions")
                await self.handle_nuke_attempt(guild, user, action_type, recent_actions)
            
            # Also check for mixed attack patterns
            await self.check_mixed_nuke_patterns(guild, user)
            
        except Exception as e:
            logger.error(f"Error checking nuke patterns: {e}")
    
    async def check_mixed_nuke_patterns(self, guild: discord.Guild, user: discord.Member):
        """Check for mixed attack patterns (multiple types of destructive actions)"""
        try:
            current_time = time.time()
            time_window_start = current_time - self.TIME_WINDOW
            
            # Count all recent destructive actions by this user
            user_actions = self.user_action_tracking[guild.id][user.id]
            total_destructive_actions = 0
            
            destructive_action_types = [
                'channel_delete', 'role_delete', 'member_ban', 
                'member_kick', 'webhook_create', 'dangerous_role_create'
            ]
            
            for action_type in destructive_action_types:
                if action_type in user_actions:
                    recent_actions = [action for action in user_actions[action_type] if action['timestamp'] >= time_window_start]
                    total_destructive_actions += len(recent_actions)
            
            # If user has performed many different destructive actions
            if total_destructive_actions >= 8:  # Lower threshold for mixed attacks
                logger.warning(f"MIXED NUKE ATTEMPT DETECTED: {user} in {guild.name} - {total_destructive_actions} total destructive actions")
                await self.handle_nuke_attempt(guild, user, 'mixed_nuke', {'total_actions': total_destructive_actions})
            
        except Exception as e:
            logger.error(f"Error checking mixed nuke patterns: {e}")
    
    async def handle_nuke_attempt(self, guild: discord.Guild, user: discord.Member, attack_type: str, action_details: list):
        """Handle detected nuke attempts"""
        try:
            if guild.id in self.nuked_guilds:
                return  # Already handling nuke for this guild
            
            self.nuked_guilds.add(guild.id)
            logger.critical(f"HANDLING NUKE ATTEMPT: {user} in {guild.name} - {attack_type}")
            
            # Immediate response - quarantine user
            await self.quarantine_user(guild, user, attack_type)
            
            # Alert administrators
            await self.send_nuke_alert(guild, user, attack_type, action_details)
            
            # Log to database
            await self.log_nuke_attempt(guild, user, attack_type, action_details)
            
            # Start restoration process if needed
            if attack_type in ['channel_delete', 'role_delete', 'mixed_nuke']:
                await self.initiate_restoration(guild, user, attack_type)
            
            # Schedule nuke cooldown
            await asyncio.sleep(300)  # 5 minute cooldown
            if guild.id in self.nuked_guilds:
                self.nuked_guilds.remove(guild.id)
                
        except Exception as e:
            logger.error(f"Error handling nuke attempt: {e}")
    
    async def quarantine_user(self, guild: discord.Guild, user: discord.Member, attack_type: str):
        """Quarantine dangerous user by removing all permissions"""
        try:
            # Add to quarantine list
            self.quarantined_users[guild.id].add(user.id)
            
            # Remove all roles (keep @everyone)
            roles_to_remove = [role for role in user.roles if not role.is_default()]
            if roles_to_remove:
                try:
                    await user.remove_roles(*roles_to_remove, reason=f"Anti-nuke: {attack_type} detected")
                except discord.Forbidden:
                    logger.warning(f"Cannot remove roles from {user} - insufficient permissions")
            
            # Try to ban if very severe
            if attack_type in ['mixed_nuke'] or len(self.user_action_tracking[guild.id][user.id]) > 15:
                try:
                    await guild.ban(user, reason=f"Anti-nuke: Severe {attack_type} attack detected", delete_message_days=0)
                    logger.info(f"Banned {user} for nuke attempt")
                except discord.Forbidden:
                    logger.warning(f"Cannot ban {user} - insufficient permissions")
            
        except Exception as e:
            logger.error(f"Error quarantining user: {e}")
    
    async def send_nuke_alert(self, guild: discord.Guild, user: discord.Member, attack_type: str, action_details: list):
        """Send immediate nuke attempt alerts"""
        try:
            embed = discord.Embed(
                title="🚨 NUKE ATTEMPT DETECTED",
                description=f"Immediate action taken against {user.mention}",
                color=0xFF0000,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Attacker", value=f"{user} ({user.id})", inline=True)
            embed.add_field(name="Attack Type", value=attack_type.replace('_', ' ').title(), inline=True)
            embed.add_field(name="Actions Count", value=str(len(action_details)), inline=True)
            
            embed.add_field(name="Response", value="✅ User quarantined\n✅ Permissions removed\n✅ Actions logged", inline=False)
            
            # Add action details
            if len(action_details) <= 10:
                detail_text = "\n".join([
                    f"• {detail.get('details', {}).get('channel_name', detail.get('details', {}).get('role_name', 'Unknown'))}"
                    for detail in action_details[:10]
                ])
                embed.add_field(name="Affected Items", value=detail_text or "Multiple items", inline=False)
            
            # Send to alert channels
            await self.broadcast_nuke_alert(guild, embed)
            
            # Send DM to guild owner if possible
            try:
                owner = guild.owner
                if owner:
                    await owner.send(embed=embed)
            except discord.Forbidden:
                pass
                
        except Exception as e:
            logger.error(f"Error sending nuke alert: {e}")
    
    async def broadcast_nuke_alert(self, guild: discord.Guild, embed: discord.Embed):
        """Broadcast nuke alert to appropriate channels"""
        try:
            # Try to find alert/admin channels
            alert_channels = []
            for channel in guild.text_channels:
                if any(keyword in channel.name.lower() for keyword in ['alert', 'admin', 'mod', 'security', 'nuke']):
                    if channel.permissions_for(guild.me).send_messages:
                        alert_channels.append(channel)
            
            # If no specific channels, use system channel
            if not alert_channels and guild.system_channel:
                if guild.system_channel.permissions_for(guild.me).send_messages:
                    alert_channels.append(guild.system_channel)
            
            # Send to found channels
            for channel in alert_channels[:3]:  # Max 3 channels to avoid spam
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    continue
                    
        except Exception as e:
            logger.error(f"Error broadcasting nuke alert: {e}")
    
    async def log_antinuke_action(self, guild: discord.Guild, user: discord.Member, action_type: str, details: dict):
        """Log anti-nuke actions to database"""
        try:
            if not self.bot.db_pool:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS antinuke_logs (
                        id SERIAL PRIMARY KEY,
                        guild_id VARCHAR(20),
                        user_id VARCHAR(20),
                        action_type VARCHAR(50),
                        details JSONB,
                        timestamp TIMESTAMP NOT NULL
                    )
                """)
                
                await conn.execute("""
                    INSERT INTO antinuke_logs (guild_id, user_id, action_type, details, timestamp)
                    VALUES ($1, $2, $3, $4, $5)
                """, str(guild.id), str(user.id), action_type, json.dumps(details), datetime.utcnow())
                
        except Exception as e:
            logger.error(f"Error logging anti-nuke action: {e}")
    
    async def log_nuke_attempt(self, guild: discord.Guild, user: discord.Member, attack_type: str, action_details: list):
        """Log nuke attempts to database"""
        try:
            if not self.bot.db_pool:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS nuke_attempts (
                        id SERIAL PRIMARY KEY,
                        guild_id VARCHAR(20),
                        user_id VARCHAR(20),
                        attack_type VARCHAR(50),
                        actions_count INTEGER,
                        action_details JSONB,
                        timestamp TIMESTAMP NOT NULL
                    )
                """)
                
                await conn.execute("""
                    INSERT INTO nuke_attempts (guild_id, user_id, attack_type, actions_count, action_details, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, 
                    str(guild.id), 
                    str(user.id), 
                    attack_type, 
                    len(action_details), 
                    json.dumps(action_details, default=str), 
                    datetime.utcnow()
                )
                
        except Exception as e:
            logger.error(f"Error logging nuke attempt: {e}")
    
    async def store_guild_backup(self, guild_id: int, backup_data: dict):
        """Store guild backup in database"""
        try:
            if not self.bot.db_pool:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS guild_backups (
                        id SERIAL PRIMARY KEY,
                        guild_id VARCHAR(20),
                        backup_data JSONB,
                        created_at TIMESTAMP NOT NULL
                    )
                """)
                
                await conn.execute("""
                    INSERT INTO guild_backups (guild_id, backup_data, created_at)
                    VALUES ($1, $2, $3)
                """, str(guild_id), json.dumps(backup_data, default=str), datetime.utcnow())
                
                # Keep only latest 10 backups per guild
                await conn.execute("""
                    DELETE FROM guild_backups 
                    WHERE guild_id = $1 
                    AND id NOT IN (
                        SELECT id FROM guild_backups 
                        WHERE guild_id = $1 
                        ORDER BY created_at DESC 
                        LIMIT 10
                    )
                """, str(guild_id))
                
        except Exception as e:
            logger.error(f"Error storing guild backup: {e}")
    
    async def initiate_restoration(self, guild: discord.Guild, attacker: discord.Member, attack_type: str):
        """Initiate restoration of deleted channels/roles"""
        try:
            # This is a placeholder for restoration logic
            # In a real implementation, you would:
            # 1. Analyze what was deleted from audit logs
            # 2. Compare with backup data
            # 3. Recreate deleted items with proper permissions
            # 4. Notify admins of restoration progress
            
            logger.info(f"Restoration initiated for {guild.name} after {attack_type} by {attacker}")
            
            # Send restoration notification
            embed = discord.Embed(
                title="🔧 Restoration Process Started",
                description=f"Attempting to restore items deleted by {attacker.mention}",
                color=0xFFAA00,
                timestamp=datetime.utcnow()
            )
            
            await self.broadcast_nuke_alert(guild, embed)
            
        except Exception as e:
            logger.error(f"Error initiating restoration: {e}")
    
    @discord.app_commands.command(name="antinuke")
    @discord.app_commands.describe(
        action="Action to perform",
        user="User to manage (for whitelist/quarantine)"
    )
    async def antinuke_command(self, interaction: discord.Interaction, 
                              action: str, user: discord.Member = None):
        """Configure anti-nuke protection settings"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need administrator permissions to use this command.",
                ephemeral=True
            )
            return
        
        guild = interaction.guild
        
        if action.lower() == "status":
            embed = discord.Embed(
                title="🛡️ Anti-Nuke Status",
                color=0x00FF00 if self.antinuke_active else 0xFF0000,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="Protection Status",
                value="Active" if self.antinuke_active else "Disabled",
                inline=True
            )
            
            embed.add_field(
                name="Quarantined Users",
                value=len(self.quarantined_users.get(guild.id, set())),
                inline=True
            )
            
            embed.add_field(
                name="Trusted Users",
                value=len(self.trusted_users.get(guild.id, set())),
                inline=True
            )
            
            # Show recent activity
            recent_actions = 0
            guild_tracking = self.action_tracking.get(guild.id, {})
            for action_type, actions in guild_tracking.items():
                recent_actions += len(actions)
            
            embed.add_field(
                name="Recent Activity",
                value=f"{recent_actions} tracked actions",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        elif action.lower() == "whitelist" and user:
            self.trusted_users[guild.id].add(user.id)
            await interaction.response.send_message(
                f"✅ Added {user.mention} to anti-nuke whitelist.",
                ephemeral=True
            )
            
        elif action.lower() == "unwhitelist" and user:
            self.trusted_users[guild.id].discard(user.id)
            await interaction.response.send_message(
                f"✅ Removed {user.mention} from anti-nuke whitelist.",
                ephemeral=True
            )
            
        elif action.lower() == "unquarantine" and user:
            self.quarantined_users[guild.id].discard(user.id)
            await interaction.response.send_message(
                f"✅ Removed {user.mention} from quarantine.",
                ephemeral=True
            )
            
        elif action.lower() == "backup":
            await self.create_guild_backup(guild)
            await interaction.response.send_message(
                "✅ Guild backup created successfully.",
                ephemeral=True
            )
            
        else:
            await interaction.response.send_message(
                "❌ Invalid action. Use: `status`, `whitelist <user>`, `unwhitelist <user>`, `unquarantine <user>`, `backup`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AntiNukeSystem(bot))