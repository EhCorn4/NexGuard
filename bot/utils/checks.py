import discord
from discord.ext import commands
import sqlite3
import logging
from typing import Union

logger = logging.getLogger(__name__)

def is_moderator():
    """Check if user has moderator permissions"""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        
        # Check if user is guild owner
        if ctx.author.id == ctx.guild.owner_id:
            return True
        
        # Check if user has administrator permission
        if ctx.author.guild_permissions.administrator:
            return True
        
        # Check for custom mod role
        if hasattr(ctx.bot, 'db_path'):
            try:
                conn = sqlite3.connect(ctx.bot.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT mod_role_id FROM guild_settings WHERE guild_id = ?', (ctx.guild.id,))
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0]:
                    mod_role_id = result[0]
                    mod_role = ctx.guild.get_role(mod_role_id)
                    if mod_role:
                        # Check if user has the mod role or any role above it
                        user_top_role = ctx.author.top_role
                        if user_top_role.position >= mod_role.position:
                            return True
                        return False
            except Exception:
                pass
        
        # Check if user has specific moderation permissions (fallback)
        perms = ctx.author.guild_permissions
        if perms.manage_guild or perms.manage_roles or perms.manage_messages:
            return True
        
        return False
    
    return commands.check(predicate)

def is_admin():
    """Check if user has admin permissions"""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        
        # Check if user is guild owner
        if ctx.author.id == ctx.guild.owner_id:
            return True
        
        # Check if user has administrator permission
        if ctx.author.guild_permissions.administrator:
            return True
        
        return False
    
    return commands.check(predicate)

def has_custom_permissions(command_name: str):
    """Check if user has custom permissions for a command"""
    async def predicate(ctx):
        if not ctx.guild:
            return True  # Allow in DMs by default
        
        # Check if user is guild owner (always allowed)
        if ctx.author.id == ctx.guild.owner_id:
            return True
        
        # Check if user has administrator permission (always allowed)
        if ctx.author.guild_permissions.administrator:
            return True
        
        try:
            # Check custom permissions from database
            conn = sqlite3.connect(ctx.bot.db_path)
            cursor = conn.cursor()
            
            # Check user-specific permissions
            cursor.execute('''
                SELECT allowed FROM command_permissions
                WHERE guild_id = ? AND command_name = ? AND entity_id = ? AND entity_type = 'user'
            ''', (ctx.guild.id, command_name, ctx.author.id))
            
            result = cursor.fetchone()
            if result:
                conn.close()
                return bool(result[0])
            
            # Check role-based permissions
            user_role_ids = [role.id for role in ctx.author.roles]
            if user_role_ids:
                placeholders = ','.join(['?'] * len(user_role_ids))
                cursor.execute(f'''
                    SELECT allowed FROM command_permissions
                    WHERE guild_id = ? AND command_name = ? AND entity_id IN ({placeholders}) AND entity_type = 'role'
                    ORDER BY allowed DESC
                ''', [ctx.guild.id, command_name] + user_role_ids)
                
                result = cursor.fetchone()
                if result:
                    conn.close()
                    return bool(result[0])
            
            conn.close()
            
            # No custom permissions found, use default Discord permissions
            return True
            
        except Exception as e:
            logger.error(f"Error checking custom permissions: {e}")
            return True  # Default to allowing if there's an error
    
    return commands.check(predicate)

def bot_has_permissions(**permissions):
    """Check if bot has required permissions"""
    async def predicate(ctx):
        if not ctx.guild:
            return True
        
        bot_permissions = ctx.guild.me.guild_permissions
        
        for perm, value in permissions.items():
            if getattr(bot_permissions, perm) != value:
                return False
        
        return True
    
    return commands.check(predicate)

def is_higher_role(member1: discord.Member, member2: discord.Member) -> bool:
    """Check if member1 has a higher role than member2"""
    return member1.top_role > member2.top_role

def can_moderate(moderator: discord.Member, target: discord.Member) -> bool:
    """Check if moderator can moderate target"""
    # Guild owner can moderate anyone
    if moderator.id == moderator.guild.owner_id:
        return True
    
    # Can't moderate guild owner
    if target.id == target.guild.owner_id:
        return False
    
    # Can't moderate someone with higher or equal role
    if target.top_role >= moderator.top_role:
        return False
    
    return True

def can_bot_moderate(bot_member: discord.Member, target: discord.Member) -> bool:
    """Check if bot can moderate target"""
    # Can't moderate guild owner
    if target.id == target.guild.owner_id:
        return False
    
    # Can't moderate someone with higher or equal role
    if target.top_role >= bot_member.top_role:
        return False
    
    return True

async def check_hierarchy(ctx, target: Union[discord.Member, discord.User], action: str) -> bool:
    """Check role hierarchy for moderation actions"""
    if isinstance(target, discord.User):
        # If it's a User object, try to get Member object
        target = ctx.guild.get_member(target.id)
        if not target:
            return True  # User not in guild, probably safe to moderate
    
    # Check if author can moderate target
    if not can_moderate(ctx.author, target):
        embed = discord.Embed(
            title="❌ Error",
            description=f"You cannot {action} someone with a higher or equal role.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return False
    
    # Check if bot can moderate target
    if not can_bot_moderate(ctx.guild.me, target):
        embed = discord.Embed(
            title="❌ Error",
            description=f"I cannot {action} someone with a higher or equal role than me.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return False
    
    return True

def is_valid_duration(duration: str) -> bool:
    """Check if duration string is valid (e.g., '1h', '30m', '1d')"""
    import re
    pattern = r'^(\d+)([smhd])$'
    return bool(re.match(pattern, duration.lower()))

def parse_duration(duration: str) -> int:
    """Parse duration string to seconds"""
    import re
    
    if not is_valid_duration(duration):
        raise ValueError("Invalid duration format")
    
    pattern = r'^(\d+)([smhd])$'
    match = re.match(pattern, duration.lower())
    
    if not match:
        raise ValueError("Invalid duration format")
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }
    
    return amount * multipliers[unit]

def format_duration(seconds: int) -> str:
    """Format seconds into a human-readable duration"""
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

class ModerationError(commands.CheckFailure):
    """Custom exception for moderation errors"""
    pass

class HierarchyError(ModerationError):
    """Exception for role hierarchy errors"""
    pass

class PermissionError(ModerationError):
    """Exception for permission errors"""
    pass

def cooldown_per_guild(rate, per):
    """Cooldown decorator that applies per guild"""
    def decorator(func):
        func.__cooldown__ = commands.Cooldown(rate, per, commands.BucketType.guild)
        return func
    return decorator

def cooldown_per_user(rate, per):
    """Cooldown decorator that applies per user"""
    def decorator(func):
        func.__cooldown__ = commands.Cooldown(rate, per, commands.BucketType.user)
        return func
    return decorator

def require_database():
    """Check if database is available and accessible"""
    async def predicate(ctx):
        try:
            conn = sqlite3.connect(ctx.bot.db_path)
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            return False
    
    return commands.check(predicate)

def is_in_guild():
    """Check if command is being used in a guild"""
    async def predicate(ctx):
        return ctx.guild is not None
    
    return commands.check(predicate)

def has_any_permission(**permissions):
    """Check if user has any of the specified permissions"""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        
        # Check if user is guild owner
        if ctx.author.id == ctx.guild.owner_id:
            return True
        
        # Check if user has administrator permission
        if ctx.author.guild_permissions.administrator:
            return True
        
        # Check if user has any of the specified permissions
        user_perms = ctx.author.guild_permissions
        for perm, value in permissions.items():
            if getattr(user_perms, perm) == value:
                return True
        
        return False
    
    return commands.check(predicate)

async def is_admin_or_moderator(interaction: discord.Interaction) -> bool:
    """Check if user has admin or moderator permissions for slash commands"""
    if not interaction.guild:
        return False
    
    # Check if user is guild owner
    if interaction.user.id == interaction.guild.owner_id:
        return True
    
    # Check if user has administrator permission
    if interaction.user.guild_permissions.administrator:
        return True
    
    # Check for custom mod role
    try:
        # Use the bot's database path
        db_path = getattr(interaction.client, 'db_path', 'nexguard/database/nexguard.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT mod_role_id FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            mod_role_id = result[0]
            mod_role = interaction.guild.get_role(mod_role_id)
            if mod_role:
                # Check if user has the mod role or any role above it
                user_top_role = interaction.user.top_role
                if user_top_role.position >= mod_role.position:
                    return True
                return False
    except Exception:
        pass
    
    # Check if user has specific moderation permissions (fallback)
    perms = interaction.user.guild_permissions
    if perms.manage_guild or perms.manage_roles or perms.manage_messages:
        return True
    
    return False
