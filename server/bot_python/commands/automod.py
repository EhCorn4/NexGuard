"""
NexGuard AutoMod System
Advanced automated moderation with comprehensive filtering and configuration
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import re
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Constants
COLORS = {
    'SUCCESS': 0x00FF00,
    'ERROR': 0xFF0000,
    'INFO': 0x00FFFF,
    'WARNING': 0xFFFF00,
    'BLUE': 0x0000FF,
    'ORANGE': 0xFFA500
}

EMOJIS = {
    'SUCCESS': '✅',
    'ERROR': '❌',
    'INFO': 'ℹ️',
    'WARNING': '⚠️',
    'CONFIG': '🤖',
    'SPAM': '🚫',
    'LINK': '🔗',
    'WORDS': '🤬',
    'CAPS': '🔤',
    'MENTION': '📢'
}

# Default bad words list for all servers
DEFAULT_BAD_WORDS = [
    "cunt", "dumb faggot", "dumb nigga", "faggot", "faggot retard", "fuck", 
    "fuckin", "fucking", "fucking faggot", "fucking nigga", "fucking retard", 
    "gay faggot", "gay nigga", "gay retard", "grooms", "nigger retard", 
    "retard", "retarded faggot", "retarded nigga", "retarded nigger", "shit", 
    "stupid faggot", "stupid retard", "bitch", "bitchs", "bitchass"
]

# Default automod configuration for new guilds
DEFAULT_AUTOMOD_CONFIG = {
    "spam": {
        "enabled": True,
        "action": "warn",
        "max_messages": 5,
        "time_window": 5
    },
    "links": {
        "enabled": False,
        "action": "delete",
        "block_urls": False,
        "block_invites": True
    },
    "badwords": {
        "enabled": True,
        "action": "delete",
        "strict": True,
        "custom_words": DEFAULT_BAD_WORDS
    }
}

class AutoModCog(commands.Cog):
    """Advanced AutoMod system for comprehensive server moderation"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("AutoMod system initialized")
    
    async def is_admin_or_moderator(self, interaction: discord.Interaction) -> bool:
        """Check if user has admin or moderator permissions"""
        return (interaction.user.guild_permissions.administrator or 
                interaction.user.guild_permissions.manage_guild or
                interaction.user.guild_permissions.manage_messages)
    
    async def get_automod_settings(self, guild_id: str) -> Dict[str, Any]:
        """Get automod settings for a guild from database"""
        if not self.bot.db_pool:
            return DEFAULT_AUTOMOD_CONFIG.copy()
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                config = await conn.fetchrow('''
                    SELECT automod_config FROM guilds WHERE id = $1
                ''', guild_id)
                
                if config and config['automod_config']:
                    return json.loads(config['automod_config'])
                else:
                    # Return default config and save it for new guilds
                    default_config = DEFAULT_AUTOMOD_CONFIG.copy()
                    await self.save_automod_settings(guild_id, default_config)
                    return default_config
        except Exception as e:
            logger.error(f"Error getting automod settings: {e}")
            return DEFAULT_AUTOMOD_CONFIG.copy()
    
    async def save_automod_settings(self, guild_id: str, settings: Dict[str, Any]):
        """Save automod settings for a guild to database"""
        if not self.bot.db_pool:
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Ensure guild exists
                await conn.execute('''
                    INSERT INTO guilds (id, name, automod_config, joined_at, updated_at)
                    VALUES ($1, 'Unknown', $2, NOW(), NOW())
                    ON CONFLICT (id) 
                    DO UPDATE SET automod_config = $2, updated_at = NOW()
                ''', guild_id, json.dumps(settings))
        except Exception as e:
            logger.error(f"Error saving automod settings: {e}")
    
    
    @app_commands.command(name="automod-config", description="Configure AutoMod settings")
    async def automod_config(self, interaction: discord.Interaction):
        """Configure AutoMod settings with interactive overview"""
        if not await self.is_admin_or_moderator(interaction):
            embed = discord.Embed(
                title=f"{EMOJIS['ERROR']} Permission Denied",
                description="You need 'Manage Server' or 'Manage Messages' permission to configure AutoMod.",
                color=COLORS['ERROR']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Get both JSON settings and individual database columns
            settings = await self.get_automod_settings(str(interaction.guild.id))
            
            # Get individual database settings too
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    db_config = await conn.fetchrow('''
                        SELECT automod_caps_enabled, automod_caps_threshold, 
                               automod_mentions_enabled, automod_mentions_limit
                        FROM guilds WHERE id = $1
                    ''', str(interaction.guild.id))
            else:
                db_config = {}
            
            embed = discord.Embed(
                title=f"{EMOJIS['CONFIG']} AutoMod Configuration",
                description="Current AutoMod settings for this server:",
                color=COLORS['INFO'],
                timestamp=datetime.utcnow()
            )
            
            # Traditional JSON-based modules
            json_modules = {
                'spam': {'emoji': EMOJIS['SPAM'], 'name': 'Spam Protection'},
                'links': {'emoji': EMOJIS['LINK'], 'name': 'Link Filtering'},
                'badwords': {'emoji': EMOJIS['WORDS'], 'name': 'Bad Words Filter'}
            }
            
            for module_name, module_info in json_modules.items():
                module_settings = settings.get(module_name, {})
                enabled = module_settings.get('enabled', False)
                status_emoji = EMOJIS['SUCCESS'] if enabled else EMOJIS['ERROR']
                action = module_settings.get('action', 'delete')
                
                embed.add_field(
                    name=f"{status_emoji} {module_info['name']}",
                    value=f"Status: {'Enabled' if enabled else 'Disabled'}\nAction: {action.title()}",
                    inline=True
                )
            
            # Database-based modules
            if db_config:
                # Caps Lock Filter
                caps_enabled = db_config.get('automod_caps_enabled', False)
                caps_threshold = db_config.get('automod_caps_threshold', 70)
                caps_emoji = EMOJIS['SUCCESS'] if caps_enabled else EMOJIS['ERROR']
                
                embed.add_field(
                    name=f"{caps_emoji} Caps Lock Filter",
                    value=f"Status: {'Enabled' if caps_enabled else 'Disabled'}\nThreshold: {caps_threshold}%",
                    inline=True
                )
                
                # Mention Limits
                mentions_enabled = db_config.get('automod_mentions_enabled', False)
                mentions_limit = db_config.get('automod_mentions_limit', 5)
                mentions_emoji = EMOJIS['SUCCESS'] if mentions_enabled else EMOJIS['ERROR']
                
                embed.add_field(
                    name=f"{mentions_emoji} Mention Limits",
                    value=f"Status: {'Enabled' if mentions_enabled else 'Disabled'}\nLimit: {mentions_limit} mentions",
                    inline=True
                )
            else:
                # Fallback display if no database config
                embed.add_field(
                    name=f"{EMOJIS['ERROR']} Caps Lock Filter",
                    value="Status: Disabled\nThreshold: 70%",
                    inline=True
                )
                
                embed.add_field(
                    name=f"{EMOJIS['ERROR']} Mention Limits", 
                    value="Status: Disabled\nLimit: 5 mentions",
                    inline=True
                )
            
            embed.add_field(
                name="📚 Available Commands",
                value="• `/automod-spam` - Configure spam protection\n• `/automod-links` - Configure link filtering\n• `/automod-badwords` - Configure bad words filter\n• `/automod-caps` - Configure caps lock filter\n• `/automod-mentions` - Configure mention limits\n• `/automod-words` - Manage custom words\n• `/automod-reset` - Reset all settings",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log command usage
            await self.bot.log_command_usage(interaction, "automod-config")
            
        except Exception as e:
            logger.error(f"Error showing automod config: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"{EMOJIS['ERROR']} Failed to load AutoMod configuration.", ephemeral=True)
                else:
                    await interaction.followup.send(f"{EMOJIS['ERROR']} Failed to load AutoMod configuration.", ephemeral=True)
            except:
                pass
    
    @app_commands.command(name="automod-spam", description="Configure spam protection")
    @app_commands.describe(
        enabled="Enable or disable spam protection",
        max_messages="Maximum messages allowed in time window",
        time_window="Time window in seconds",
        action="Action to take on spam detection"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Delete Message", value="delete"),
            app_commands.Choice(name="Delete & Warn", value="warn"),
            app_commands.Choice(name="Delete & Timeout", value="timeout")
        ]
    )
    async def automod_spam(self, interaction: discord.Interaction,
                          enabled: bool,
                          max_messages: int = 5,
                          time_window: int = 5,
                          action: str = "delete"):
        """Configure spam protection settings"""
        if not await self.is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} You need 'Manage Server' permission to use this command.", 
                ephemeral=True
            )
            return
        
        # Validate inputs
        if max_messages < 1 or max_messages > 20:
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} Max messages must be between 1 and 20.", 
                ephemeral=True
            )
            return
        
        if time_window < 1 or time_window > 60:
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} Time window must be between 1 and 60 seconds.", 
                ephemeral=True
            )
            return
        
        try:
            settings = await self.get_automod_settings(str(interaction.guild.id))
            settings['spam'] = {
                'enabled': enabled,
                'max_messages': max_messages,
                'time_window': time_window,
                'action': action
            }
            
            await self.save_automod_settings(str(interaction.guild.id), settings)
            
            embed = discord.Embed(
                title=f"{EMOJIS['SPAM']} Spam Protection Configured",
                description="Spam protection settings have been updated.",
                color=COLORS['SUCCESS']
            )
            
            embed.add_field(
                name="Settings",
                value=(
                    f"**Enabled:** {EMOJIS['SUCCESS'] if enabled else EMOJIS['ERROR']}\n"
                    f"**Max Messages:** {max_messages}\n"
                    f"**Time Window:** {time_window}s\n"
                    f"**Action:** {action.title()}"
                ),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Spam protection configured in guild {interaction.guild.id}")
            
            # Log command usage
            parameters = {
                "enabled": enabled,
                "max_messages": max_messages,
                "time_window": time_window,
                "action": action
            }
            await self.bot.log_command_usage(interaction, "automod-spam", parameters)
            
        except Exception as e:
            logger.error(f"Error configuring spam protection: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"{EMOJIS['ERROR']} Failed to configure spam protection.", ephemeral=True)
                else:
                    await interaction.followup.send(f"{EMOJIS['ERROR']} Failed to configure spam protection.", ephemeral=True)
            except:
                pass
    
    @app_commands.command(name="automod-links", description="Configure link filtering")
    @app_commands.describe(
        enabled="Enable or disable link filtering",
        block_invites="Block Discord invites",
        block_urls="Block all URLs",
        action="Action to take on link detection"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Delete Message", value="delete"),
            app_commands.Choice(name="Delete & Warn", value="warn"),
            app_commands.Choice(name="Delete & Timeout", value="timeout")
        ]
    )
    async def automod_links(self, interaction: discord.Interaction,
                           enabled: bool,
                           block_invites: bool = True,
                           block_urls: bool = False,
                           action: str = "delete"):
        """Configure link filtering settings"""
        if not await self.is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} You need 'Manage Server' permission to use this command.", 
                ephemeral=True
            )
            return
        
        try:
            settings = await self.get_automod_settings(str(interaction.guild.id))
            settings['links'] = {
                'enabled': enabled,
                'block_invites': block_invites,
                'block_urls': block_urls,
                'action': action
            }
            
            await self.save_automod_settings(str(interaction.guild.id), settings)
            
            embed = discord.Embed(
                title=f"{EMOJIS['LINK']} Link Filtering Configured",
                description="Link filtering settings have been updated.",
                color=COLORS['SUCCESS']
            )
            
            embed.add_field(
                name="Settings",
                value=(
                    f"**Enabled:** {EMOJIS['SUCCESS'] if enabled else EMOJIS['ERROR']}\n"
                    f"**Block Invites:** {EMOJIS['SUCCESS'] if block_invites else EMOJIS['ERROR']}\n"
                    f"**Block URLs:** {EMOJIS['SUCCESS'] if block_urls else EMOJIS['ERROR']}\n"
                    f"**Action:** {action.title()}"
                ),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Link filtering configured in guild {interaction.guild.id}")
            
            # Log command usage
            parameters = {
                "enabled": enabled,
                "block_invites": block_invites,
                "block_urls": block_urls,
                "action": action
            }
            await self.bot.log_command_usage(interaction, "automod-links", parameters)
            
        except Exception as e:
            logger.error(f"Error configuring link filtering: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"{EMOJIS['ERROR']} Failed to configure link filtering.", ephemeral=True)
                else:
                    await interaction.followup.send(f"{EMOJIS['ERROR']} Failed to configure link filtering.", ephemeral=True)
            except:
                pass
    
    @app_commands.command(name="automod-badwords", description="Configure bad words filter")
    @app_commands.describe(
        enabled="Enable or disable bad words filter",
        strict="Use strict mode (exact word match)",
        action="Action to take on bad word detection"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Delete Message", value="delete"),
            app_commands.Choice(name="Delete & Warn", value="warn"),
            app_commands.Choice(name="Delete & Timeout", value="timeout")
        ]
    )
    async def automod_badwords(self, interaction: discord.Interaction,
                              enabled: bool,
                              strict: bool = False,
                              action: str = "delete"):
        """Configure bad words filter settings"""
        if not await self.is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} You need 'Manage Server' permission to use this command.", 
                ephemeral=True
            )
            return
        
        try:
            settings = await self.get_automod_settings(str(interaction.guild.id))
            if 'badwords' not in settings:
                settings['badwords'] = {'custom_words': []}
            
            settings['badwords'].update({
                'enabled': enabled,
                'strict': strict,
                'action': action
            })
            
            await self.save_automod_settings(str(interaction.guild.id), settings)
            
            embed = discord.Embed(
                title=f"{EMOJIS['WORDS']} Bad Words Filter Configured",
                description="Bad words filter settings have been updated.",
                color=COLORS['SUCCESS']
            )
            
            custom_words_count = len(settings['badwords'].get('custom_words', []))
            embed.add_field(
                name="Settings",
                value=(
                    f"**Enabled:** {EMOJIS['SUCCESS'] if enabled else EMOJIS['ERROR']}\n"
                    f"**Strict Mode:** {EMOJIS['SUCCESS'] if strict else EMOJIS['ERROR']}\n"
                    f"**Custom Words:** {custom_words_count}\n"
                    f"**Action:** {action.title()}"
                ),
                inline=False
            )
            
            embed.add_field(
                name="💡 Tip",
                value="Use `/automod-words` to manage your custom bad words list.",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Bad words filter configured in guild {interaction.guild.id}")
            
            # Log command usage
            parameters = {
                "enabled": enabled,
                "strict": strict,
                "action": action
            }
            await self.bot.log_command_usage(interaction, "automod-badwords", parameters)
            
        except Exception as e:
            logger.error(f"Error configuring bad words filter: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"{EMOJIS['ERROR']} Failed to configure bad words filter.", ephemeral=True)
                else:
                    await interaction.followup.send(f"{EMOJIS['ERROR']} Failed to configure bad words filter.", ephemeral=True)
            except:
                pass
    
    @app_commands.command(name="automod-words", description="Manage custom bad words list")
    @app_commands.describe(
        action="Action to perform",
        words="Word(s) to add or remove (separate multiple words with commas)"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Add Words", value="add"),
            app_commands.Choice(name="Remove Words", value="remove"),
            app_commands.Choice(name="List Words", value="list"),
            app_commands.Choice(name="Clear All", value="clear")
        ]
    )
    async def automod_words(self, interaction: discord.Interaction,
                           action: str,
                           words: str = None):
        """Manage custom bad words list"""
        if not await self.is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} You need 'Manage Server' permission to use this command.", 
                ephemeral=True
            )
            return
        
        try:
            settings = await self.get_automod_settings(str(interaction.guild.id))
            if 'badwords' not in settings:
                settings['badwords'] = {'custom_words': []}
            
            custom_words = settings['badwords'].get('custom_words', [])
            
            if action == "add":
                if not words:
                    await interaction.response.send_message(
                        f"{EMOJIS['ERROR']} Please provide word(s) to add. Separate multiple words with commas.", 
                        ephemeral=True
                    )
                    return
                
                # Split by commas and clean up
                word_list = [word.lower().strip() for word in words.split(',') if word.strip()]
                
                if not word_list:
                    await interaction.response.send_message(
                        f"{EMOJIS['ERROR']} No valid words provided.", 
                        ephemeral=True
                    )
                    return
                
                added_words = []
                existing_words = []
                
                for word in word_list:
                    if word not in custom_words:
                        custom_words.append(word)
                        added_words.append(word)
                    else:
                        existing_words.append(word)
                
                if added_words:
                    settings['badwords']['custom_words'] = custom_words
                    await self.save_automod_settings(str(interaction.guild.id), settings)
                
                # Create response embed
                if added_words and existing_words:
                    embed = discord.Embed(
                        title=f"{EMOJIS['SUCCESS']} Words Processed",
                        color=COLORS['SUCCESS']
                    )
                    embed.add_field(
                        name="Added Words",
                        value="• " + "\n• ".join([f"||{w}||" for w in added_words]),
                        inline=False
                    )
                    embed.add_field(
                        name="Already Existed",
                        value="• " + "\n• ".join([f"||{w}||" for w in existing_words]),
                        inline=False
                    )
                elif added_words:
                    embed = discord.Embed(
                        title=f"{EMOJIS['SUCCESS']} Words Added",
                        description=f"Added {len(added_words)} word(s) to the bad words filter:\n• " + "\n• ".join([f"||{w}||" for w in added_words]),
                        color=COLORS['SUCCESS']
                    )
                else:
                    embed = discord.Embed(
                        title=f"{EMOJIS['WARNING']} All Words Already Exist",
                        description="All provided words are already in the bad words filter.",
                        color=COLORS['WARNING']
                    )
            
            elif action == "remove":
                if not words:
                    await interaction.response.send_message(
                        f"{EMOJIS['ERROR']} Please provide word(s) to remove. Separate multiple words with commas.", 
                        ephemeral=True
                    )
                    return
                
                # Split by commas and clean up
                word_list = [word.lower().strip() for word in words.split(',') if word.strip()]
                
                if not word_list:
                    await interaction.response.send_message(
                        f"{EMOJIS['ERROR']} No valid words provided.", 
                        ephemeral=True
                    )
                    return
                
                removed_words = []
                not_found_words = []
                
                for word in word_list:
                    if word in custom_words:
                        custom_words.remove(word)
                        removed_words.append(word)
                    else:
                        not_found_words.append(word)
                
                if removed_words:
                    settings['badwords']['custom_words'] = custom_words
                    await self.save_automod_settings(str(interaction.guild.id), settings)
                
                # Create response embed
                if removed_words and not_found_words:
                    embed = discord.Embed(
                        title=f"{EMOJIS['SUCCESS']} Words Processed",
                        color=COLORS['SUCCESS']
                    )
                    embed.add_field(
                        name="Removed Words",
                        value="• " + "\n• ".join([f"||{w}||" for w in removed_words]),
                        inline=False
                    )
                    embed.add_field(
                        name="Not Found",
                        value="• " + "\n• ".join([f"||{w}||" for w in not_found_words]),
                        inline=False
                    )
                elif removed_words:
                    embed = discord.Embed(
                        title=f"{EMOJIS['SUCCESS']} Words Removed",
                        description=f"Removed {len(removed_words)} word(s) from the bad words filter:\n• " + "\n• ".join([f"||{w}||" for w in removed_words]),
                        color=COLORS['SUCCESS']
                    )
                else:
                    embed = discord.Embed(
                        title=f"{EMOJIS['WARNING']} No Words Found",
                        description="None of the provided words were found in the bad words filter.",
                        color=COLORS['WARNING']
                    )
            
            elif action == "list":
                if custom_words:
                    embed = discord.Embed(
                        title=f"{EMOJIS['INFO']} Custom Bad Words",
                        description=f"**Total:** {len(custom_words)} words",
                        color=COLORS['INFO']
                    )
                    
                    # Split words into chunks to avoid field limit
                    word_chunks = [custom_words[i:i+20] for i in range(0, len(custom_words), 20)]
                    for i, chunk in enumerate(word_chunks[:3]):  # Show max 3 chunks (60 words)
                        embed.add_field(
                            name=f"Words {i*20+1}-{min((i+1)*20, len(custom_words))}",
                            value="• " + "\n• ".join([f"||{w}||" for w in chunk]),
                            inline=False
                        )
                    
                    if len(custom_words) > 60:
                        embed.add_field(
                            name="📄 Note",
                            value=f"Showing first 60 of {len(custom_words)} words. Use smaller chunks for full list.",
                            inline=False
                        )
                else:
                    embed = discord.Embed(
                        title=f"{EMOJIS['INFO']} Custom Bad Words",
                        description="No custom bad words configured.\nUse `/automod-words add <word>` to add words.",
                        color=COLORS['INFO']
                    )
            
            elif action == "clear":
                if custom_words:
                    settings['badwords']['custom_words'] = []
                    await self.save_automod_settings(str(interaction.guild.id), settings)
                    
                    embed = discord.Embed(
                        title=f"{EMOJIS['WARNING']} Words Cleared",
                        description=f"All {len(custom_words)} custom bad words have been cleared.",
                        color=COLORS['WARNING']
                    )
                else:
                    embed = discord.Embed(
                        title=f"{EMOJIS['INFO']} No Words to Clear",
                        description="There are no custom bad words to clear.",
                        color=COLORS['INFO']
                    )
            
            await interaction.response.send_message(embed=embed, ephemeral=action in ["add", "remove", "clear"])
            
        except Exception as e:
            logger.error(f"Error managing custom words: {e}")
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} Failed to manage custom words.", 
                ephemeral=True
            )
    
    @app_commands.command(name="automod-reset", description="Reset all AutoMod settings")
    async def automod_reset(self, interaction: discord.Interaction):
        """Reset all AutoMod settings to default (disabled)"""
        if not await self.is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} You need 'Manage Server' permission to use this command.", 
                ephemeral=True
            )
            return
        
        try:
            # Clear all automod settings
            await self.save_automod_settings(str(interaction.guild.id), {})
            
            embed = discord.Embed(
                title=f"{EMOJIS['WARNING']} AutoMod Settings Reset",
                description="All AutoMod settings have been reset to default (disabled).",
                color=COLORS['WARNING']
            )
            
            # Reset database columns too
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    await conn.execute('''
                        UPDATE guilds SET 
                            automod_caps_enabled = $1,
                            automod_mentions_enabled = $1
                        WHERE id = $2
                    ''', False, str(interaction.guild.id))
            
            embed.add_field(
                name="What was reset:",
                value="• Spam Protection\n• Link Filtering\n• Bad Words Filter\n• Custom Words List\n• Caps Lock Filter\n• Mention Limits",
                inline=False
            )
            
            embed.add_field(
                name="Next steps:",
                value="Use `/automod-config` to view available configuration commands.",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"AutoMod settings reset in guild {interaction.guild.id}")
            
        except Exception as e:
            logger.error(f"Error resetting automod settings: {e}")
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} Failed to reset AutoMod settings.", 
                ephemeral=True
            )
    
    # AutoMod message processing method (called by eventlog.py to prevent duplicate listeners)
    async def process_automod_checks(self, message):
        """Handle incoming messages for AutoMod enforcement"""
        # Skip bots and DMs
        if message.author.bot or not message.guild:
            return
        
        # Skip if no database connection
        if not self.bot.db_pool:
            return
        
        try:
            # Skip moderators and admins for automod checks
            if (message.author.guild_permissions.administrator or 
                message.author.guild_permissions.manage_messages):
                return
            
            settings = await self.get_automod_settings(str(message.guild.id))
            
            # Check each automod module
            if await self.check_spam_filter(message, settings.get('spam', {})):
                return True
            if await self.check_link_filter(message, settings.get('links', {})):
                return True
            if await self.check_badwords_filter(message, settings.get('badwords', {})):
                return True
            if await self.check_caps_filter(message):
                return True
            if await self.check_mentions_filter(message):
                return True
                
        except Exception as e:
            logger.error(f"Error in automod message handler: {e}")
        
        return False
    

    
    async def check_spam_filter(self, message, settings) -> bool:
        """Check message against spam filter"""
        if not settings.get('enabled', False):
            return False
        
        max_messages = settings.get('max_messages', 5)
        time_window = settings.get('time_window', 10)  # seconds
        action = settings.get('action', 'delete')
        
        if not self.bot.db_pool:
            return False
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Get recent messages from this user
                cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)
                
                # Count recent messages (we'll store this in analytics for now)
                recent_count = await conn.fetchval('''
                    SELECT COUNT(*) FROM message_analytics 
                    WHERE user_id = $1 AND guild_id = $2 AND timestamp > $3
                ''', str(message.author.id), str(message.guild.id), cutoff_time)
                
                if recent_count and recent_count >= max_messages:
                    # Spam detected! Take action
                    await self.take_automod_action(message, 'spam', action, f"Sent {recent_count + 1} messages in {time_window} seconds")
                    return True
                    
        except Exception as e:
            logger.error(f"Error checking spam filter: {e}")
        
        return False
    
    async def check_link_filter(self, message, settings) -> bool:
        """Check message against link filter"""
        if not settings.get('enabled', False):
            return False
        
        content = message.content.lower()
        
        # Check for Discord invites
        if settings.get('block_invites', False):
            invite_patterns = [r'discord\.gg/', r'discord\.com/invite/', r'discordapp\.com/invite/']
            for pattern in invite_patterns:
                if re.search(pattern, content):
                    await self.take_action(message, settings.get('action', 'delete'), "Discord invite detected")
                    return True
        
        # Check for URLs
        if settings.get('block_urls', False):
            url_pattern = r'https?://[^\s]+'
            if re.search(url_pattern, content):
                await self.take_action(message, settings.get('action', 'delete'), "URL detected")
                return True
        
        return False
    
    async def check_badwords_filter(self, message, settings) -> bool:
        """Check message against bad words filter - ALWAYS ACTIVE like anti-nuke protection"""
        content = message.content.lower()
        
        # Always use default bad words (like anti-nuke protection)
        # These are automatically active for all servers
        words_to_check = DEFAULT_BAD_WORDS.copy()
        
        # If server has custom settings, merge with defaults
        if settings.get('enabled', True):  # Default to enabled
            custom_words = settings.get('custom_words', [])
            # Add custom words to the default list (remove duplicates)
            for word in custom_words:
                if word not in words_to_check:
                    words_to_check.append(word)
        
        # Always use delete action (like anti-nuke protection)
        action = 'delete'
        strict_mode = settings.get('strict', True)  # Default to strict mode
        
        for word in words_to_check:
            if strict_mode:
                # Exact word match
                if word in content.split():
                    await self.take_action(message, action, f"Inappropriate content detected")
                    return True
            else:
                # Contains match
                if word in content:
                    await self.take_action(message, action, f"Inappropriate content detected")
                    return True
        
        return False
    
    async def log_automod_action(self, message: discord.Message, filter_type: str, reason: str, action: str):
        """Log automod action to the guild's configured logging channel - DISABLED to prevent duplicate logging with eventlog.py"""
        # DISABLED: AutoMod logging disabled to prevent duplication with comprehensive eventlog.py system
        return
        
        try:
            guild_config = await self.bot.get_guild_config(str(message.guild.id))
            log_channel_id = guild_config.get('log_channel_id')
            
            if not log_channel_id:
                return  # No logging channel configured
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return  # Channel doesn't exist or bot can't access it
            
            # Create professional automod log embed
            embed = discord.Embed(
                title="🛡️ AutoMod Action",
                color=COLORS['WARNING'],
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="Filter Type",
                value=filter_type,
                inline=True
            )
            
            embed.add_field(
                name="Action Taken",
                value=action.title(),
                inline=True
            )
            
            embed.add_field(
                name="User",
                value=f"{message.author.mention}\n(`{message.author.id}`)",
                inline=True
            )
            
            embed.add_field(
                name="Channel",
                value=f"{message.channel.mention}\n(`{message.channel.id}`)",
                inline=True
            )
            
            embed.add_field(
                name="Reason",
                value=reason,
                inline=True
            )
            
            # Add message content (truncated if too long)
            content = message.content
            if len(content) > 200:
                content = content[:197] + "..."
            
            embed.add_field(
                name="Message Content",
                value=f"```{content}```" if content else "*(No text content)*",
                inline=False
            )
            
            embed.set_footer(
                text=f"Guild: {message.guild.name}",
                icon_url=message.guild.icon.url if message.guild.icon else None
            )
            
            embed.set_thumbnail(url=message.author.display_avatar.url)
            
            # DISABLED: Direct logging call disabled to prevent duplication with eventlog.py
            # await log_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to log automod action: {e}")

    async def take_automod_action(self, message, filter_type, action, reason):
        """Take automod action for specific filter types like spam"""
        try:
            if action == "delete":
                await message.delete()
                logger.info(f"AutoMod deleted message from {message.author} for {reason}")
            
            elif action == "warn":
                await message.delete()
                # Send warning to user
                try:
                    embed = discord.Embed(
                        title=f"{EMOJIS['WARNING']} AutoMod Warning",
                        description=f"Your message was deleted for: {reason}",
                        color=COLORS['WARNING']
                    )
                    embed.add_field(name="Filter", value=filter_type.title(), inline=True)
                    await message.author.send(embed=embed)
                except:
                    pass  # User has DMs disabled
                logger.info(f"AutoMod warned {message.author} for {reason}")
            
            elif action == "timeout":
                await message.delete()
                # Timeout user for 5 minutes
                try:
                    timeout_until = discord.utils.utcnow() + timedelta(minutes=5)
                    await message.author.timeout(timeout_until, reason=f"AutoMod {filter_type}: {reason}")
                    logger.info(f"AutoMod timed out {message.author} for {reason}")
                except:
                    pass  # Insufficient permissions
            
            # Log the automod action
            await self.log_automod_action(message, f"{filter_type.title()} Filter", reason, action)
        
        except Exception as e:
            logger.error(f"Error taking automod action: {e}")

    async def take_action(self, message, action, reason):
        """Take the specified action on a message"""
        try:
            filter_type = "AutoMod Filter"
            
            if action == "delete":
                await message.delete()
                logger.info(f"Deleted message from {message.author} for {reason}")
            
            elif action == "warn":
                await message.delete()
                # Send warning to user
                try:
                    embed = discord.Embed(
                        title=f"{EMOJIS['WARNING']} AutoMod Warning",
                        description=f"Your message was deleted for: {reason}",
                        color=COLORS['WARNING']
                    )
                    await message.author.send(embed=embed)
                except:
                    pass  # User has DMs disabled
                logger.info(f"Warned {message.author} for {reason}")
            
            elif action == "timeout":
                await message.delete()
                # Timeout user for 5 minutes
                try:
                    timeout_until = discord.utils.utcnow() + timedelta(minutes=5)
                    await message.author.timeout(timeout_until, reason=f"AutoMod: {reason}")
                    logger.info(f"Timed out {message.author} for {reason}")
                except:
                    pass  # Insufficient permissions
            
            # Log the automod action
            await self.log_automod_action(message, filter_type, reason, action)
        
        except Exception as e:
            logger.error(f"Error taking automod action: {e}")

    async def check_caps_filter(self, message) -> bool:
        """Check message for excessive caps lock"""
        if not self.bot.db_pool:
            return False
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                config = await conn.fetchrow('''
                    SELECT automod_caps_enabled, automod_caps_threshold 
                    FROM guilds WHERE id = $1
                ''', str(message.guild.id))
                
                if not config or not config['automod_caps_enabled']:
                    return False
                
                threshold = config['automod_caps_threshold'] or 70
                
                # Calculate caps percentage
                text = message.content
                if len(text) < 3:  # Skip very short messages
                    return False
                
                # Count letters only (ignore numbers, symbols, spaces)
                letters = [c for c in text if c.isalpha()]
                if len(letters) < 3:  # Need at least 3 letters to check
                    return False
                
                caps_count = sum(1 for c in letters if c.isupper())
                caps_percentage = (caps_count / len(letters)) * 100
                
                if caps_percentage >= threshold:
                    # Take action
                    await self.take_automod_action(message, "caps", f"Excessive caps ({caps_percentage:.1f}% >= {threshold}%)")
                    
                    # Log to configured channel
                    await self.log_automod_action(
                        message, 
                        "Caps Lock Filter", 
                        f"Message contained {caps_percentage:.1f}% caps (threshold: {threshold}%)",
                        COLORS['WARNING']
                    )
                    return True
                    
        except Exception as e:
            logger.error(f"Error checking caps filter: {e}")
        
        return False

    async def check_mentions_filter(self, message) -> bool:
        """Check message for excessive mentions"""
        if not self.bot.db_pool:
            return False
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                config = await conn.fetchrow('''
                    SELECT automod_mentions_enabled, automod_mentions_limit 
                    FROM guilds WHERE id = $1
                ''', str(message.guild.id))
                
                if not config or not config['automod_mentions_enabled']:
                    return False
                
                limit = config['automod_mentions_limit'] or 5
                
                # Count all types of mentions
                mention_count = 0
                mention_count += len(message.mentions)  # User mentions
                mention_count += len(message.role_mentions)  # Role mentions
                if message.mention_everyone:  # @everyone or @here
                    mention_count += 1
                
                if mention_count > limit:
                    # Take action
                    await self.take_automod_action(message, "mentions", f"Excessive mentions ({mention_count} > {limit})")
                    
                    # Log to configured channel
                    await self.log_automod_action(
                        message, 
                        "Mention Limits", 
                        f"Message contained {mention_count} mentions (limit: {limit})",
                        COLORS['WARNING']
                    )
                    return True
                    
        except Exception as e:
            logger.error(f"Error checking mentions filter: {e}")
        
        return False

    @app_commands.command(name="automod-caps", description="Configure caps lock filter")
    @app_commands.describe(
        action="Enable or disable caps lock filter",
        threshold="Percentage of caps required to trigger (default: 70%)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="enable", value="enable"),
        app_commands.Choice(name="disable", value="disable"),
        app_commands.Choice(name="settings", value="settings")
    ])
    async def automod_caps(self, interaction: discord.Interaction, action: str, threshold: int = 70):
        """Configure caps lock filter protection"""
        if not await self.is_admin_or_moderator(interaction):
            await interaction.response.send_message("❌ You need Manage Server or Manage Messages permissions to use this command.", ephemeral=True)
            return
        
        if threshold < 10 or threshold > 100:
            await interaction.response.send_message("❌ Threshold must be between 10% and 100%.", ephemeral=True)
            return
        
        try:
            guild_id = str(interaction.guild.id)
            
            if action == "enable":
                if self.bot.db_pool:
                    async with self.bot.db_pool.acquire() as conn:
                        await conn.execute('''
                            UPDATE guilds 
                            SET automod_caps_enabled = $1, automod_caps_threshold = $2
                            WHERE id = $3
                        ''', True, threshold, guild_id)
                
                embed = discord.Embed(
                    title=f"{EMOJIS['CAPS']} Caps Lock Filter Enabled",
                    description=f"Caps lock filter is now **enabled** with {threshold}% threshold.",
                    color=COLORS['SUCCESS'],
                    timestamp=datetime.utcnow()
                )
                embed.add_field(
                    name="📊 Settings",
                    value=f"**Threshold:** {threshold}% caps required to trigger\n"
                          f"**Action:** Delete message and warn user\n"
                          f"**Bypass:** Users with Manage Messages permission",
                    inline=False
                )
                embed.set_footer(text="AutoMod Caps Filter Enabled", icon_url=None)
                
                await interaction.response.send_message(embed=embed)
                
            elif action == "disable":
                if self.bot.db_pool:
                    async with self.bot.db_pool.acquire() as conn:
                        await conn.execute('''
                            UPDATE guilds SET automod_caps_enabled = $1 WHERE id = $2
                        ''', False, guild_id)
                
                embed = discord.Embed(
                    title=f"{EMOJIS['CAPS']} Caps Lock Filter Disabled",
                    description="Caps lock filter protection has been **disabled**.",
                    color=COLORS['WARNING'],
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text="AutoMod Caps Filter Disabled", icon_url=None)
                
                await interaction.response.send_message(embed=embed)
                
            elif action == "settings":
                if self.bot.db_pool:
                    async with self.bot.db_pool.acquire() as conn:
                        config = await conn.fetchrow('''
                            SELECT automod_caps_enabled, automod_caps_threshold 
                            FROM guilds WHERE id = $1
                        ''', guild_id)
                        
                        caps_enabled = config['automod_caps_enabled'] if config else False
                        caps_threshold = config['automod_caps_threshold'] if config else 70
                
                embed = discord.Embed(
                    title=f"{EMOJIS['CAPS']} Caps Lock Filter Settings",
                    description=f"Current caps lock filter configuration for **{interaction.guild.name}**",
                    color=COLORS['INFO'],
                    timestamp=datetime.utcnow()
                )
                
                status_emoji = "✅" if caps_enabled else "❌"
                embed.add_field(
                    name="📊 Current Status",
                    value=f"**Status:** {status_emoji} {'Enabled' if caps_enabled else 'Disabled'}\n"
                          f"**Threshold:** {caps_threshold}% caps required\n"
                          f"**Action:** Delete message and warn user",
                    inline=False
                )
                
                if caps_enabled:
                    embed.add_field(
                        name="🔧 How it works",
                        value="• Scans all messages for excessive caps\n"
                              f"• Triggers when {caps_threshold}% or more text is in caps\n"
                              "• Deletes message and warns the user\n"
                              "• Bypassed for users with Manage Messages permission",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="💡 Enable Protection",
                        value="Use `/automod-caps enable` to activate caps lock filtering",
                        inline=False
                    )
                
                embed.set_footer(text="AutoMod Caps Filter Settings", icon_url=None)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Log command usage
            parameters = {"action": action, "threshold": threshold}
            await self.bot.log_command_usage(interaction, "automod-caps", parameters)
                
        except Exception as e:
            logger.error(f"Error with automod caps: {e}")
            await interaction.response.send_message("❌ Failed to configure caps lock filter. Please try again.", ephemeral=True)

    @app_commands.command(name="automod-mentions", description="Configure mention limits")
    @app_commands.describe(
        action="Enable or disable mention limits",
        limit="Maximum mentions allowed per message (default: 5)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="enable", value="enable"),
        app_commands.Choice(name="disable", value="disable"),
        app_commands.Choice(name="settings", value="settings")
    ])
    async def automod_mentions(self, interaction: discord.Interaction, action: str, limit: int = 5):
        """Configure mention limits protection"""
        if not await self.is_admin_or_moderator(interaction):
            await interaction.response.send_message("❌ You need Manage Server or Manage Messages permissions to use this command.", ephemeral=True)
            return
        
        if limit < 1 or limit > 20:
            await interaction.response.send_message("❌ Mention limit must be between 1 and 20 mentions.", ephemeral=True)
            return
        
        try:
            guild_id = str(interaction.guild.id)
            
            if action == "enable":
                if self.bot.db_pool:
                    async with self.bot.db_pool.acquire() as conn:
                        await conn.execute('''
                            UPDATE guilds 
                            SET automod_mentions_enabled = $1, automod_mentions_limit = $2
                            WHERE id = $3
                        ''', True, limit, guild_id)
                
                embed = discord.Embed(
                    title=f"{EMOJIS['MENTION']} Mention Limits Enabled",
                    description=f"Mention limits are now **enabled** with a limit of {limit} mentions per message.",
                    color=COLORS['SUCCESS'],
                    timestamp=datetime.utcnow()
                )
                embed.add_field(
                    name="📊 Settings",
                    value=f"**Limit:** {limit} mentions per message\n"
                          f"**Includes:** @user, @role, @everyone, @here\n"
                          f"**Action:** Delete message and warn user\n"
                          f"**Bypass:** Users with Manage Messages permission",
                    inline=False
                )
                embed.set_footer(text="AutoMod Mention Limits Enabled", icon_url=None)
                
                await interaction.response.send_message(embed=embed)
                
            elif action == "disable":
                if self.bot.db_pool:
                    async with self.bot.db_pool.acquire() as conn:
                        await conn.execute('''
                            UPDATE guilds SET automod_mentions_enabled = $1 WHERE id = $2
                        ''', False, guild_id)
                
                embed = discord.Embed(
                    title=f"{EMOJIS['MENTION']} Mention Limits Disabled",
                    description="Mention limits protection has been **disabled**.",
                    color=COLORS['WARNING'],
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text="AutoMod Mention Limits Disabled", icon_url=None)
                
                await interaction.response.send_message(embed=embed)
                
            elif action == "settings":
                if self.bot.db_pool:
                    async with self.bot.db_pool.acquire() as conn:
                        config = await conn.fetchrow('''
                            SELECT automod_mentions_enabled, automod_mentions_limit 
                            FROM guilds WHERE id = $1
                        ''', guild_id)
                        
                        mentions_enabled = config['automod_mentions_enabled'] if config else False
                        mentions_limit = config['automod_mentions_limit'] if config else 5
                
                embed = discord.Embed(
                    title=f"{EMOJIS['MENTION']} Mention Limits Settings",
                    description=f"Current mention limits configuration for **{interaction.guild.name}**",
                    color=COLORS['INFO'],
                    timestamp=datetime.utcnow()
                )
                
                status_emoji = "✅" if mentions_enabled else "❌"
                embed.add_field(
                    name="📊 Current Status",
                    value=f"**Status:** {status_emoji} {'Enabled' if mentions_enabled else 'Disabled'}\n"
                          f"**Limit:** {mentions_limit} mentions per message\n"
                          f"**Action:** Delete message and warn user",
                    inline=False
                )
                
                if mentions_enabled:
                    embed.add_field(
                        name="🔧 How it works",
                        value="• Counts all mentions in each message\n"
                              f"• Triggers when {mentions_limit}+ mentions detected\n"
                              "• Includes @user, @role, @everyone, @here\n"
                              "• Deletes message and warns the user\n"
                              "• Bypassed for users with Manage Messages permission",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="💡 Enable Protection",
                        value="Use `/automod-mentions enable` to activate mention limits",
                        inline=False
                    )
                
                embed.set_footer(text="AutoMod Mention Limits Settings", icon_url=None)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Log command usage
            parameters = {"action": action, "limit": limit}
            await self.bot.log_command_usage(interaction, "automod-mentions", parameters)
                
        except Exception as e:
            logger.error(f"Error with automod mentions: {e}")
            await interaction.response.send_message("❌ Failed to configure mention limits. Please try again.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AutoModCog(bot))