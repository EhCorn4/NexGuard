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
            return {}
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                config = await conn.fetchrow('''
                    SELECT automod_config FROM guilds WHERE id = $1
                ''', guild_id)
                
                if config and config['automod_config']:
                    return json.loads(config['automod_config'])
                return {}
        except Exception as e:
            logger.error(f"Error getting automod settings: {e}")
            return {}
    
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
            settings = await self.get_automod_settings(str(interaction.guild.id))
            
            embed = discord.Embed(
                title=f"{EMOJIS['CONFIG']} AutoMod Configuration",
                description="Current AutoMod settings for this server:",
                color=COLORS['INFO'],
                timestamp=datetime.utcnow()
            )
            
            # Add current settings for each module
            modules = {
                'spam': {'emoji': EMOJIS['SPAM'], 'name': 'Spam Protection'},
                'links': {'emoji': EMOJIS['LINK'], 'name': 'Link Filtering'},
                'badwords': {'emoji': EMOJIS['WORDS'], 'name': 'Bad Words Filter'},
                'caps': {'emoji': EMOJIS['CAPS'], 'name': 'Caps Lock Filter'},
                'mentions': {'emoji': EMOJIS['MENTION'], 'name': 'Mention Limits'}
            }
            
            for module_name, module_info in modules.items():
                module_settings = settings.get(module_name, {})
                enabled = module_settings.get('enabled', False)
                status_emoji = EMOJIS['SUCCESS'] if enabled else EMOJIS['ERROR']
                action = module_settings.get('action', 'delete')
                
                embed.add_field(
                    name=f"{status_emoji} {module_info['name']}",
                    value=f"Status: {'Enabled' if enabled else 'Disabled'}\nAction: {action.title()}",
                    inline=True
                )
            
            embed.add_field(
                name="📚 Available Commands",
                value="• `/automod-spam` - Configure spam protection\n• `/automod-links` - Configure link filtering\n• `/automod-badwords` - Configure bad words filter\n• `/automod-words` - Manage custom words\n• `/automod-reset` - Reset all settings",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing automod config: {e}")
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} Failed to load AutoMod configuration.", 
                ephemeral=True
            )
    
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
            
        except Exception as e:
            logger.error(f"Error configuring spam protection: {e}")
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} Failed to configure spam protection.", 
                ephemeral=True
            )
    
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
            
        except Exception as e:
            logger.error(f"Error configuring link filtering: {e}")
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} Failed to configure link filtering.", 
                ephemeral=True
            )
    
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
            
        except Exception as e:
            logger.error(f"Error configuring bad words filter: {e}")
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} Failed to configure bad words filter.", 
                ephemeral=True
            )
    
    @app_commands.command(name="automod-words", description="Manage custom bad words list")
    @app_commands.describe(
        action="Action to perform",
        word="Word to add or remove"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Add Word", value="add"),
            app_commands.Choice(name="Remove Word", value="remove"),
            app_commands.Choice(name="List Words", value="list"),
            app_commands.Choice(name="Clear All", value="clear")
        ]
    )
    async def automod_words(self, interaction: discord.Interaction,
                           action: str,
                           word: str = None):
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
                if not word:
                    await interaction.response.send_message(
                        f"{EMOJIS['ERROR']} Please provide a word to add.", 
                        ephemeral=True
                    )
                    return
                
                word = word.lower().strip()
                if word not in custom_words:
                    custom_words.append(word)
                    settings['badwords']['custom_words'] = custom_words
                    await self.save_automod_settings(str(interaction.guild.id), settings)
                    
                    embed = discord.Embed(
                        title=f"{EMOJIS['SUCCESS']} Word Added",
                        description=f"Added '||{word}||' to the bad words filter.",
                        color=COLORS['SUCCESS']
                    )
                else:
                    embed = discord.Embed(
                        title=f"{EMOJIS['WARNING']} Word Already Exists",
                        description=f"'||{word}||' is already in the bad words filter.",
                        color=COLORS['WARNING']
                    )
            
            elif action == "remove":
                if not word:
                    await interaction.response.send_message(
                        f"{EMOJIS['ERROR']} Please provide a word to remove.", 
                        ephemeral=True
                    )
                    return
                
                word = word.lower().strip()
                if word in custom_words:
                    custom_words.remove(word)
                    settings['badwords']['custom_words'] = custom_words
                    await self.save_automod_settings(str(interaction.guild.id), settings)
                    
                    embed = discord.Embed(
                        title=f"{EMOJIS['SUCCESS']} Word Removed",
                        description=f"Removed '||{word}||' from the bad words filter.",
                        color=COLORS['SUCCESS']
                    )
                else:
                    embed = discord.Embed(
                        title=f"{EMOJIS['WARNING']} Word Not Found",
                        description=f"'||{word}||' is not in the bad words filter.",
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
    
    # Message event listener for automod enforcement
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages for AutoMod enforcement"""
        # Skip bots and DMs
        if message.author.bot or not message.guild:
            return
        
        # Skip if no database connection
        if not self.bot.db_pool:
            return
        
        # Skip moderators and admins
        if (message.author.guild_permissions.administrator or 
            message.author.guild_permissions.manage_messages):
            return
        
        try:
            settings = await self.get_automod_settings(str(message.guild.id))
            
            # Check each automod module
            if await self.check_spam_filter(message, settings.get('spam', {})):
                return
            if await self.check_link_filter(message, settings.get('links', {})):
                return
            if await self.check_badwords_filter(message, settings.get('badwords', {})):
                return
                
        except Exception as e:
            logger.error(f"Error in automod message handler: {e}")
    
    async def check_spam_filter(self, message, settings) -> bool:
        """Check message against spam filter"""
        if not settings.get('enabled', False):
            return False
        
        # Basic spam detection logic would go here
        # For now, just return False
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
                    await self.take_action(message, settings.get('action', 'delete'), "Discord invite")
                    return True
        
        # Check for URLs
        if settings.get('block_urls', False):
            url_pattern = r'https?://[^\s]+'
            if re.search(url_pattern, content):
                await self.take_action(message, settings.get('action', 'delete'), "URL")
                return True
        
        return False
    
    async def check_badwords_filter(self, message, settings) -> bool:
        """Check message against bad words filter"""
        if not settings.get('enabled', False):
            return False
        
        content = message.content.lower()
        custom_words = settings.get('custom_words', [])
        strict_mode = settings.get('strict', False)
        
        for word in custom_words:
            if strict_mode:
                # Exact word match
                if word in content.split():
                    await self.take_action(message, settings.get('action', 'delete'), f"bad word: {word}")
                    return True
            else:
                # Contains match
                if word in content:
                    await self.take_action(message, settings.get('action', 'delete'), f"bad word: {word}")
                    return True
        
        return False
    
    async def take_action(self, message, action, reason):
        """Take the specified action on a message"""
        try:
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
                    await message.author.timeout(timedelta(minutes=5), reason=f"AutoMod: {reason}")
                    logger.info(f"Timed out {message.author} for {reason}")
                except:
                    pass  # Insufficient permissions
        
        except Exception as e:
            logger.error(f"Error taking automod action: {e}")

async def setup(bot):
    await bot.add_cog(AutoModCog(bot))