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
    def create_embed(title: str, description: str = None, color: discord.Color = None, embed_type: str = "info") -> discord.Embed:
        """Create a generic embed with common styling"""
        colors = {
            "success": discord.Color.green(),
            "error": discord.Color.red(),
            "warning": discord.Color.orange(),
            "info": discord.Color.blue()
        }
        
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        embed = discord.Embed(
            title=f"{icons.get(embed_type, '')} {title}",
            description=description,
            color=color or colors.get(embed_type, discord.Color.blue()),
            timestamp=datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def success(title: str, description: str = None) -> discord.Embed:
        return EmbedBuilder.create_embed(title, description, None, "success")
    
    @staticmethod
    def error(title: str, description: str = None) -> discord.Embed:
        return EmbedBuilder.create_embed(title, description, None, "error")
    
    @staticmethod
    def warning(title: str, description: str = None) -> discord.Embed:
        return EmbedBuilder.create_embed(title, description, None, "warning")
    
    @staticmethod
    def info(title: str, description: str = None) -> discord.Embed:
        return EmbedBuilder.create_embed(title, description, None, "info")
    
    @staticmethod
    def moderation(action: str, target: Union[discord.Member, discord.User], 
                   moderator: discord.Member, reason: str = None) -> discord.Embed:
        """Create a moderation embed"""
        embed = discord.Embed(
            title=f"🔨 {action.title()}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Target", value=f"{target} (`{target.id}`)", inline=True)
        embed.add_field(name="Moderator", value=f"{moderator} (`{moderator.id}`)", inline=True)
        
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        
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
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get guild settings"""
        result = self.execute_query(
            'SELECT * FROM guild_settings WHERE guild_id = ?',
            (guild_id,)
        )
        
        if result:
            return {
                'prefix': result[0][1],
                'log_channel': result[0][2],
                'welcome_channel': result[0][3],
                'autorole_enabled': result[0][4],
                'autorole_roles': result[0][5]
            }
        return {}

class MessageHelper:
    """Helper class for message operations"""
    
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
    
    @staticmethod
    def format_list(items: List[str], max_items: int = 10) -> str:
        """Format a list of items for display"""
        if not items:
            return "None"
        
        if len(items) <= max_items:
            return ", ".join(items)
        else:
            return ", ".join(items[:max_items]) + f" and {len(items) - max_items} more..."
    
    @staticmethod
    def parse_mention(mention: str) -> Optional[int]:
        """Parse mention string to ID"""
        if mention.startswith('<@') and mention.endswith('>'):
            return int(mention[2:-1].replace('!', ''))
        return None
    
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

# Utility functions
def get_bot_color(bot: commands.Bot) -> discord.Color:
    """Get the bot's color"""
    return discord.Color.blue()

def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

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

def is_mention(text: str) -> bool:
    """Check if text is a mention"""
    return text.startswith('<@') and text.endswith('>')