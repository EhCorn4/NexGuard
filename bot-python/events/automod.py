import discord
from discord.ext import commands
import sqlite3
import json
import re
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AutoModEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_message_history = {}  # Track user message history for spam detection
        self.user_violations = {}  # Track user violations for escalation
        
        # Common bad words list (basic implementation)
        self.default_bad_words = [
            # Add common inappropriate words here
            "spam", "scam", "hack", "cheat", "bot", "fake"
        ]
        
        # URL patterns
        self.url_patterns = [
            r'https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?',
            r'www\.(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?',
            r'(?:[-\w.])+\.(?:com|org|net|edu|gov|mil|int|co|io|me|tv|cc|tk|ml|cf|ga|xyz|top|click|link|download|zip|rar|exe|scr|bat|cmd|pif|com|scr|vbs|js|jar|app|deb|rpm|dmg|pkg|msi|run|bin|sh|pl|py|rb|php|asp|jsp|html|htm|xml|css|js|json|txt|doc|docx|pdf|xls|xlsx|ppt|pptx|zip|rar|tar|gz|7z|bz2|xz|iso|img|dmg|toast|vcd|cue|mds|mdx|bin|nrg|cdi|b5t|bwt|ccd|sub|img|udf|gho|tib|vhd|vmdk|vdi|qcow|qcow2|vbox|ova|ovf|vmx|vmdk|vhd|vhdx|avhd|avhdx|vdi|qcow|qcow2|vmdk|vhd|vhdx|avhd|avhdx|vdi|qcow|qcow2)(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?'
        ]
        
        # Discord invite patterns
        self.invite_patterns = [
            r'discord\.gg/[a-zA-Z0-9]+',
            r'discordapp\.com/invite/[a-zA-Z0-9]+',
            r'discord\.com/invite/[a-zA-Z0-9]+',
            r'dsc\.gg/[a-zA-Z0-9]+',
            r'invite\.gg/[a-zA-Z0-9]+',
        ]
        
    @commands.Cog.listener()
    async def on_message(self, message):
        """Enhanced message monitoring with automod"""
        if message.author.bot:
            return
            
        if not message.guild:
            return
            
        # Skip messages from mods/admins
        if message.author.guild_permissions.manage_messages:
            return
            
        try:
            # Get automod settings for this guild
            settings = await self.get_automod_settings(message.guild.id)
            
            if not settings:
                return
                
            # Check each automod feature
            await self.check_spam(message, settings)
            await self.check_links(message, settings)
            await self.check_bad_words(message, settings)
            await self.check_caps(message, settings)
            await self.check_mentions(message, settings)
            
        except Exception as e:
            logger.error(f"Error in automod engine: {e}")
            
    async def get_automod_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get automod settings for a guild"""
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT automod_settings FROM guild_settings WHERE guild_id = ?', (guild_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return json.loads(result[0])
            return {}
            
        except Exception as e:
            logger.error(f"Error getting automod settings: {e}")
            return {}
            
    async def check_spam(self, message: discord.Message, settings: Dict[str, Any]):
        """Check for spam messages"""
        spam_settings = settings.get('spam', {})
        if not spam_settings.get('enabled', False):
            return
            
        user_id = message.author.id
        current_time = time.time()
        
        # Initialize user history if not exists
        if user_id not in self.user_message_history:
            self.user_message_history[user_id] = []
            
        # Add current message to history
        self.user_message_history[user_id].append({
            'content': message.content,
            'timestamp': current_time,
            'channel_id': message.channel.id,
            'message_id': message.id
        })
        
        # Clean old messages from history
        time_window = spam_settings.get('time_window', 5)
        self.user_message_history[user_id] = [
            msg for msg in self.user_message_history[user_id] 
            if current_time - msg['timestamp'] <= time_window
        ]
        
        # Check if user exceeded message limit
        max_messages = spam_settings.get('max_messages', 5)
        if len(self.user_message_history[user_id]) > max_messages:
            await self.handle_violation(message, "Spam detected", spam_settings.get('action', 'delete'))
            
    async def check_links(self, message: discord.Message, settings: Dict[str, Any]):
        """Check for unwanted links"""
        link_settings = settings.get('links', {})
        if not link_settings.get('enabled', False):
            return
            
        content = message.content.lower()
        
        # Check for Discord invites
        if link_settings.get('block_invites', True):
            for pattern in self.invite_patterns:
                if re.search(pattern, content):
                    await self.handle_violation(message, "Discord invite detected", link_settings.get('action', 'delete'))
                    return
                    
        # Check for URLs
        if link_settings.get('block_urls', False):
            for pattern in self.url_patterns:
                if re.search(pattern, content):
                    await self.handle_violation(message, "URL detected", link_settings.get('action', 'delete'))
                    return
                    
    async def check_bad_words(self, message: discord.Message, settings: Dict[str, Any]):
        """Check for inappropriate language"""
        badword_settings = settings.get('badwords', {})
        if not badword_settings.get('enabled', False):
            return
            
        content = message.content.lower()
        
        # Get word list (default + custom)
        word_list = self.default_bad_words.copy()
        custom_words = badword_settings.get('custom_words', [])
        word_list.extend(custom_words)
        
        # Check for bad words
        for word in word_list:
            if badword_settings.get('strict', False):
                # Exact word match
                if re.search(r'\b' + re.escape(word.lower()) + r'\b', content):
                    await self.handle_violation(message, f"Inappropriate language: {word}", badword_settings.get('action', 'delete'))
                    return
            else:
                # Substring match
                if word.lower() in content:
                    await self.handle_violation(message, f"Inappropriate language: {word}", badword_settings.get('action', 'delete'))
                    return
                    
    async def check_caps(self, message: discord.Message, settings: Dict[str, Any]):
        """Check for excessive caps lock"""
        caps_settings = settings.get('caps', {})
        if not caps_settings.get('enabled', False):
            return
            
        content = message.content
        min_length = caps_settings.get('min_length', 10)
        
        # Skip short messages
        if len(content) < min_length:
            return
            
        # Calculate caps percentage
        caps_count = sum(1 for c in content if c.isupper())
        caps_percentage = (caps_count / len(content)) * 100
        
        threshold = caps_settings.get('threshold', 70)
        if caps_percentage > threshold:
            await self.handle_violation(message, f"Excessive caps lock ({caps_percentage:.1f}%)", caps_settings.get('action', 'delete'))
            
    async def check_mentions(self, message: discord.Message, settings: Dict[str, Any]):
        """Check for excessive mentions"""
        mention_settings = settings.get('mentions', {})
        if not mention_settings.get('enabled', False):
            return
            
        # Check user mentions
        max_mentions = mention_settings.get('max_mentions', 5)
        if len(message.mentions) > max_mentions:
            await self.handle_violation(message, f"Too many mentions ({len(message.mentions)})", mention_settings.get('action', 'delete'))
            return
            
        # Check role mentions
        max_role_mentions = mention_settings.get('max_role_mentions', 2)
        if len(message.role_mentions) > max_role_mentions:
            await self.handle_violation(message, f"Too many role mentions ({len(message.role_mentions)})", mention_settings.get('action', 'delete'))
            return
            
    async def handle_violation(self, message: discord.Message, reason: str, action: str):
        """Handle automod violations"""
        try:
            # Log the violation
            await self.log_violation(message, reason, action)
            
            # Delete the message
            await message.delete()
            
            # Take action based on settings
            if action == "delete":
                # Just delete (already done)
                pass
            elif action == "warn":
                # Delete and warn user
                await self.warn_user(message, reason)
            elif action == "timeout":
                # Delete and timeout user
                await self.timeout_user(message, reason)
                
            # Send notification to log channel
            await self.send_log_notification(message, reason, action)
            
        except Exception as e:
            logger.error(f"Error handling automod violation: {e}")
            
    async def log_violation(self, message: discord.Message, reason: str, action: str):
        """Log violation to database"""
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action, additional_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                message.guild.id,
                message.channel.id,
                message.author.id,
                message.id,
                message.content,
                'AUTOMOD_VIOLATION',
                json.dumps({
                    'reason': reason,
                    'action': action,
                    'timestamp': datetime.utcnow().isoformat()
                })
            ))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging automod violation: {e}")
            
    async def warn_user(self, message: discord.Message, reason: str):
        """Issue a warning to the user"""
        try:
            # Add warning to database
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO warnings (guild_id, user_id, moderator_id, reason)
                VALUES (?, ?, ?, ?)
            ''', (
                message.guild.id,
                message.author.id,
                self.bot.user.id,  # Bot as moderator
                f"AutoMod: {reason}"
            ))
            conn.commit()
            conn.close()
            
            # Send DM to user
            embed = discord.Embed(
                title="⚠️ AutoMod Warning",
                description=f"You have been warned in **{message.guild.name}** for: {reason}",
                color=discord.Color.orange()
            )
            
            try:
                await message.author.send(embed=embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
                
        except Exception as e:
            logger.error(f"Error warning user: {e}")
            
    async def timeout_user(self, message: discord.Message, reason: str):
        """Timeout the user"""
        try:
            # Timeout for 5 minutes
            timeout_duration = timedelta(minutes=5)
            
            await message.author.timeout(timeout_duration, reason=f"AutoMod: {reason}")
            
            # Send DM to user
            embed = discord.Embed(
                title="⏰ AutoMod Timeout",
                description=f"You have been timed out in **{message.guild.name}** for 5 minutes.\n**Reason:** {reason}",
                color=discord.Color.red()
            )
            
            try:
                await message.author.send(embed=embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
                
        except Exception as e:
            logger.error(f"Error timing out user: {e}")
            
    async def send_log_notification(self, message: discord.Message, reason: str, action: str):
        """Send notification to log channel"""
        try:
            # Get log channel
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT log_channel FROM guild_settings WHERE guild_id = ?', (message.guild.id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result or not result[0]:
                return
                
            log_channel = message.guild.get_channel(result[0])
            if not log_channel:
                return
                
            # Create log embed
            embed = discord.Embed(
                title="🤖 AutoMod Action",
                description=f"Automatic moderation action taken",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="User",
                value=f"{message.author} (`{message.author.id}`)",
                inline=True
            )
            
            embed.add_field(
                name="Channel",
                value=message.channel.mention,
                inline=True
            )
            
            embed.add_field(
                name="Action",
                value=action.capitalize(),
                inline=True
            )
            
            embed.add_field(
                name="Reason",
                value=reason,
                inline=False
            )
            
            if len(message.content) > 0:
                embed.add_field(
                    name="Message Content",
                    value=message.content[:1000] + ("..." if len(message.content) > 1000 else ""),
                    inline=False
                )
            
            embed.set_footer(text=f"Message ID: {message.id}")
            
            await log_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending log notification: {e}")

async def setup(bot):
    await bot.add_cog(AutoModEngine(bot))