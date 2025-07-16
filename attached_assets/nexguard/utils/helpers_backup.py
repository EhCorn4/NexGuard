import discord
from discord.ext import commands
import sqlite3
import re
import asyncio
import logging
from typing import Optional, List, Union, Dict, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class EmbedBuilder:
    """Helper class for building Discord embeds"""
    
    @staticmethod
    def success(title: str, description: str = None) -> discord.Embed:
        """Create a success embed"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def error(title: str, description: str = None) -> discord.Embed:
        """Create an error embed"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def warning(title: str, description: str = None) -> discord.Embed:
        """Create a warning embed"""
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def info(title: str, description: str = None) -> discord.Embed:
        """Create an info embed"""
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def moderation(action: str, target: Union[discord.Member, discord.User], 
                   moderator: discord.Member, reason: str = None) -> discord.Embed:
        """Create a moderation embed"""
        embed = discord.Embed(
            title=f"🔨 {action.title()}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Target",
            value=f"{target} (`{target.id}`)",
            inline=True
        )
        
        embed.add_field(
            name="Moderator",
            value=f"{moderator} (`{moderator.id}`)",
            inline=True
        )
        
        if reason:
            embed.add_field(
                name="Reason",
                value=reason,
                inline=False
            )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        return embed

class DatabaseHelper:
    """Helper class for database operations"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.bot.db_path)
    
    def execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """Execute a SELECT query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            return results
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def get_guild_prefix(self, guild_id: int) -> str:
        """Get guild prefix"""
        query = 'SELECT prefix FROM guild_settings WHERE guild_id = ?'
        result = self.execute_query(query, (guild_id,))
        return result[0][0] if result else '!'
    
    def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get all guild settings"""
        query = '''
            SELECT prefix, log_channel, mute_role, welcome_channel, auto_role
            FROM guild_settings WHERE guild_id = ?
        '''
        result = self.execute_query(query, (guild_id,))
        
        if result:
            return {
                'prefix': result[0][0],
                'log_channel': result[0][1],
                'mute_role': result[0][2],
                'welcome_channel': result[0][3],
                'auto_role': result[0][4]
            }
        return {}

class UserLookup:
    """Helper class for user lookups"""
    
    @staticmethod
    async def get_user(ctx, user_input: str) -> Optional[Union[discord.Member, discord.User]]:
        """Get user from various input formats"""
        # Try to get member by mention
        if user_input.startswith('<@') and user_input.endswith('>'):
            user_id = int(user_input[2:-1].replace('!', ''))
            member = ctx.guild.get_member(user_id)
            if member:
                return member
            
            # Try to get user by ID
            try:
                user = await ctx.bot.fetch_user(user_id)
                return user
            except discord.NotFound:
                pass
        
        # Try to get member by ID
        if user_input.isdigit():
            user_id = int(user_input)
            member = ctx.guild.get_member(user_id)
            if member:
                return member
            
            # Try to get user by ID
            try:
                user = await ctx.bot.fetch_user(user_id)
                return user
            except discord.NotFound:
                pass
        
        # Try to get member by name
        member = discord.utils.get(ctx.guild.members, name=user_input)
        if member:
            return member
        
        # Try to get member by display name
        member = discord.utils.get(ctx.guild.members, display_name=user_input)
        if member:
            return member
        
        # Try to get member by name (case insensitive)
        member = discord.utils.find(
            lambda m: m.name.lower() == user_input.lower(),
            ctx.guild.members
        )
        if member:
            return member
        
        # Try to get member by display name (case insensitive)
        member = discord.utils.find(
            lambda m: m.display_name.lower() == user_input.lower(),
            ctx.guild.members
        )
        if member:
            return member
        
        return None

class TimeHelper:
    """Helper class for time operations"""
    
    @staticmethod
    def parse_time(time_str: str) -> Optional[int]:
        """Parse time string to seconds"""
        if not time_str:
            return None
        
        pattern = r'^(\d+)([smhd])$'
        match = re.match(pattern, time_str.lower())
        
        if not match:
            return None
        
        amount = int(match.group(1))
        unit = match.group(2)
        
        multipliers = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400
        }
        
        return amount * multipliers.get(unit, 0)
    
    @staticmethod
    def format_time(seconds: int) -> str:
        """Format seconds to human readable time"""
        if seconds < 60:
            return f"{seconds} second{'s' if seconds != 1 else ''}"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            days = seconds // 86400
            return f"{days} day{'s' if days != 1 else ''}"
    
    @staticmethod
    def get_relative_time(dt: datetime) -> str:
        """Get relative time string"""
        now = datetime.utcnow()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"

class PaginationHelper:
    """Helper class for paginated embeds"""
    
    @staticmethod
    async def paginate(ctx, embeds: List[discord.Embed], timeout: int = 300):
        """Create paginated embed with reactions"""
        if not embeds:
            return
        
        if len(embeds) == 1:
            await ctx.send(embed=embeds[0])
            return
        
        current_page = 0
        message = await ctx.send(embed=embeds[current_page])
        
        # Add reactions
        await message.add_reaction('⏮️')
        await message.add_reaction('◀️')
        await message.add_reaction('▶️')
        await message.add_reaction('⏭️')
        await message.add_reaction('❌')
        
        def check(reaction, user):
            return (
                user == ctx.author and
                reaction.message.id == message.id and
                str(reaction.emoji) in ['⏮️', '◀️', '▶️', '⏭️', '❌']
            )
        
        while True:
            try:
                reaction, user = await ctx.bot.wait_for('reaction_add', timeout=timeout, check=check)
                
                if str(reaction.emoji) == '⏮️':
                    current_page = 0
                elif str(reaction.emoji) == '◀️':
                    current_page = max(0, current_page - 1)
                elif str(reaction.emoji) == '▶️':
                    current_page = min(len(embeds) - 1, current_page + 1)
                elif str(reaction.emoji) == '⏭️':
                    current_page = len(embeds) - 1
                elif str(reaction.emoji) == '❌':
                    await message.delete()
                    return
                
                await message.edit(embed=embeds[current_page])
                await message.remove_reaction(reaction, user)
                
            except asyncio.TimeoutError:
                try:
                    await message.clear_reactions()
                except discord.Forbidden:
                    pass
                break

class ModerationHelper:
    """Helper class for moderation operations"""
    
    @staticmethod
    async def log_action(bot, guild: discord.Guild, action: str, target: Union[discord.Member, discord.User],
                        moderator: discord.Member, reason: str = None, additional_info: Dict = None):
        """Log moderation action to database and log channel"""
        try:
            # Log to database
            conn = sqlite3.connect(bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action, additional_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                guild.id,
                0,  # No specific channel for moderation actions
                target.id,
                0,  # No specific message
                reason or "No reason provided",
                action,
                json.dumps(additional_info) if additional_info else None
            ))
            conn.commit()
            
            # Get log channel
            cursor.execute('SELECT log_channel FROM guild_settings WHERE guild_id = ?', (guild.id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                log_channel = guild.get_channel(result[0])
                if log_channel:
                    embed = EmbedBuilder.moderation(action, target, moderator, reason)
                    await log_channel.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Error logging moderation action: {e}")
    
    @staticmethod
    async def dm_user(user: Union[discord.Member, discord.User], embed: discord.Embed) -> bool:
        """Try to DM a user with embed"""
        try:
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            return False
        except Exception as e:
            logger.error(f"Error sending DM: {e}")
            return False

class ValidationHelper:
    """Helper class for input validation"""
    
    @staticmethod
    def is_valid_hex_color(color: str) -> bool:
        """Check if string is valid hex color"""
        return bool(re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color))
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if string is valid URL"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    @staticmethod
    def clean_content(content: str, max_length: int = 2000) -> str:
        """Clean and truncate content"""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Truncate if too long
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        return content

class ConfirmationHelper:
    """Helper class for confirmation dialogs"""
    
    @staticmethod
    async def confirm(ctx, message: str, timeout: int = 30) -> bool:
        """Ask for confirmation from user"""
        embed = discord.Embed(
            title="🤔 Confirmation Required",
            description=f"{message}\n\nReact with ✅ to confirm or ❌ to cancel.",
            color=discord.Color.orange()
        )
        
        confirmation_message = await ctx.send(embed=embed)
        await confirmation_message.add_reaction('✅')
        await confirmation_message.add_reaction('❌')
        
        def check(reaction, user):
            return (
                user == ctx.author and
                reaction.message.id == confirmation_message.id and
                str(reaction.emoji) in ['✅', '❌']
            )
        
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=timeout, check=check)
            await confirmation_message.delete()
            return str(reaction.emoji) == '✅'
        except asyncio.TimeoutError:
            await confirmation_message.delete()
            return False

class LogHelper:
    """Helper class for logging operations"""
    
    @staticmethod
    async def send_log(bot, guild: discord.Guild, embed: discord.Embed) -> bool:
        """Send log message to guild's log channel"""
        try:
            conn = sqlite3.connect(bot.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT log_channel FROM guild_settings WHERE guild_id = ?', (guild.id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                log_channel = guild.get_channel(result[0])
                if log_channel:
                    await log_channel.send(embed=embed)
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error sending log: {e}")
            return False
    
    @staticmethod
    def format_permissions(permissions: discord.Permissions) -> List[str]:
        """Format permissions object to readable list"""
        perm_list = []
        for perm, value in permissions:
            if value:
                perm_list.append(perm.replace('_', ' ').title())
        return perm_list

# Global helper functions
def get_bot_color(bot: commands.Bot) -> discord.Color:
    """Get the bot's color"""
    return discord.Color.blue()

def format_list(items: List[str], max_items: int = 10) -> str:
    """Format a list of items for display"""
    if not items:
        return "None"
    
    if len(items) <= max_items:
        return ", ".join(items)
    else:
        return ", ".join(items[:max_items]) + f" and {len(items) - max_items} more..."

def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def parse_mention(mention: str) -> Optional[int]:
    """Parse mention string to ID"""
    if mention.startswith('<@') and mention.endswith('>'):
        return int(mention[2:-1].replace('!', ''))
    return None

def is_mention(text: str) -> bool:
    """Check if text is a mention"""
    return text.startswith('<@') and text.endswith('>')

def format_seconds(seconds: int) -> str:
    """Format seconds to human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"
