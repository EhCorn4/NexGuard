import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import json
import re
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AutoModConfigView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        
    @discord.ui.select(
        placeholder="Select AutoMod features to configure...",
        min_values=1,
        max_values=5,
        options=[
            discord.SelectOption(
                label="Spam Protection",
                description="Configure spam detection settings",
                value="spam",
                emoji="🚫"
            ),
            discord.SelectOption(
                label="Link Filtering",
                description="Configure link and invite filtering",
                value="links", 
                emoji="🔗"
            ),
            discord.SelectOption(
                label="Bad Words Filter",
                description="Configure profanity and inappropriate content filtering",
                value="badwords",
                emoji="🤬"
            ),
            discord.SelectOption(
                label="Caps Lock Detection",
                description="Configure excessive caps lock detection",
                value="caps",
                emoji="🔠"
            ),
            discord.SelectOption(
                label="Mention Limits",
                description="Configure mention spam protection",
                value="mentions",
                emoji="📢"
            )
        ]
    )
    async def select_automod_features(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Handle automod feature selection"""
        await interaction.response.defer()
        
        # Get current settings
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT automod_settings FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        current_settings = {}
        if result and result[0]:
            try:
                current_settings = json.loads(result[0])
            except json.JSONDecodeError:
                current_settings = {}
        
        # Create configuration embed
        embed = discord.Embed(
            title="🤖 AutoMod Configuration",
            description="Configure the selected AutoMod features for your server",
            color=discord.Color.blue()
        )
        
        for feature in select.values:
            if feature == "spam":
                embed.add_field(
                    name="🚫 Spam Protection",
                    value=(
                        f"**Enabled:** {'✅' if current_settings.get('spam', {}).get('enabled', False) else '❌'}\n"
                        f"**Max Messages:** {current_settings.get('spam', {}).get('max_messages', 5)}\n"
                        f"**Time Window:** {current_settings.get('spam', {}).get('time_window', 5)}s\n"
                        f"**Action:** {current_settings.get('spam', {}).get('action', 'delete')}"
                    ),
                    inline=True
                )
            elif feature == "links":
                embed.add_field(
                    name="🔗 Link Filtering",
                    value=(
                        f"**Enabled:** {'✅' if current_settings.get('links', {}).get('enabled', False) else '❌'}\n"
                        f"**Block Invites:** {'✅' if current_settings.get('links', {}).get('block_invites', True) else '❌'}\n"
                        f"**Block URLs:** {'✅' if current_settings.get('links', {}).get('block_urls', False) else '❌'}\n"
                        f"**Action:** {current_settings.get('links', {}).get('action', 'delete')}"
                    ),
                    inline=True
                )
            elif feature == "badwords":
                embed.add_field(
                    name="🤬 Bad Words Filter",
                    value=(
                        f"**Enabled:** {'✅' if current_settings.get('badwords', {}).get('enabled', False) else '❌'}\n"
                        f"**Strict Mode:** {'✅' if current_settings.get('badwords', {}).get('strict', False) else '❌'}\n"
                        f"**Custom Words:** {len(current_settings.get('badwords', {}).get('custom_words', []))}\n"
                        f"**Action:** {current_settings.get('badwords', {}).get('action', 'delete')}"
                    ),
                    inline=True
                )
            elif feature == "caps":
                embed.add_field(
                    name="🔠 Caps Lock Detection",
                    value=(
                        f"**Enabled:** {'✅' if current_settings.get('caps', {}).get('enabled', False) else '❌'}\n"
                        f"**Threshold:** {current_settings.get('caps', {}).get('threshold', 70)}%\n"
                        f"**Min Length:** {current_settings.get('caps', {}).get('min_length', 10)}\n"
                        f"**Action:** {current_settings.get('caps', {}).get('action', 'delete')}"
                    ),
                    inline=True
                )
            elif feature == "mentions":
                embed.add_field(
                    name="📢 Mention Limits",
                    value=(
                        f"**Enabled:** {'✅' if current_settings.get('mentions', {}).get('enabled', False) else '❌'}\n"
                        f"**Max Mentions:** {current_settings.get('mentions', {}).get('max_mentions', 5)}\n"
                        f"**Max Role Mentions:** {current_settings.get('mentions', {}).get('max_role_mentions', 2)}\n"
                        f"**Action:** {current_settings.get('mentions', {}).get('action', 'delete')}"
                    ),
                    inline=True
                )
        
        embed.set_footer(text="Use the /automod command to configure these settings")
        await interaction.followup.send(embed=embed)

class AutoModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_message_history = {}  # Track user message history for spam detection
        
    @app_commands.command(name="automod", description="Configure AutoMod settings for your server")
    @app_commands.describe(
        action="Action to perform",
        feature="AutoMod feature to configure",
        enabled="Enable or disable the feature",
        value="Configuration value"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Configure", value="config"),
            app_commands.Choice(name="Status", value="status"),
            app_commands.Choice(name="Reset", value="reset")
        ],
        feature=[
            app_commands.Choice(name="Spam Protection", value="spam"),
            app_commands.Choice(name="Link Filtering", value="links"),
            app_commands.Choice(name="Bad Words Filter", value="badwords"),
            app_commands.Choice(name="Caps Lock Detection", value="caps"),
            app_commands.Choice(name="Mention Limits", value="mentions")
        ]
    )
    async def automod(self, interaction: discord.Interaction, 
                     action: str, 
                     feature: str = None,
                     enabled: bool = None,
                     value: str = None):
        """Configure AutoMod settings"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to use this command.", ephemeral=True)
            return
        
        if action == "config":
            view = AutoModConfigView(self.bot)
            embed = discord.Embed(
                title="🤖 AutoMod Configuration",
                description="Select which AutoMod features you want to configure for your server.",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Available Features",
                value=(
                    "🚫 **Spam Protection** - Detect and prevent spam messages\n"
                    "🔗 **Link Filtering** - Block Discord invites and suspicious URLs\n"
                    "🤬 **Bad Words Filter** - Filter inappropriate language\n"
                    "🔠 **Caps Lock Detection** - Prevent excessive caps lock usage\n"
                    "📢 **Mention Limits** - Limit excessive mentions and role pings"
                ),
                inline=False
            )
            await interaction.response.send_message(embed=embed, view=view)
            
        elif action == "status":
            await self.show_automod_status(interaction)
            
        elif action == "reset":
            await self.reset_automod_settings(interaction)
            
    async def show_automod_status(self, interaction: discord.Interaction):
        """Show current AutoMod status"""
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT automod_settings FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        settings = {}
        if result and result[0]:
            try:
                settings = json.loads(result[0])
            except json.JSONDecodeError:
                settings = {}
        
        embed = discord.Embed(
            title="🤖 AutoMod Status",
            description="Current AutoMod configuration for this server",
            color=discord.Color.green()
        )
        
        # Check each feature
        features = [
            ("spam", "🚫 Spam Protection"),
            ("links", "🔗 Link Filtering"),
            ("badwords", "🤬 Bad Words Filter"),
            ("caps", "🔠 Caps Lock Detection"),
            ("mentions", "📢 Mention Limits")
        ]
        
        enabled_features = []
        disabled_features = []
        
        for feature_key, feature_name in features:
            if settings.get(feature_key, {}).get('enabled', False):
                enabled_features.append(feature_name)
            else:
                disabled_features.append(feature_name)
        
        if enabled_features:
            embed.add_field(
                name="✅ Enabled Features",
                value="\n".join(enabled_features),
                inline=True
            )
        else:
            embed.add_field(
                name="✅ Enabled Features",
                value="None",
                inline=True
            )
        
        if disabled_features:
            embed.add_field(
                name="❌ Disabled Features",
                value="\n".join(disabled_features),
                inline=True
            )
        
        embed.set_footer(text="Use /automod config to modify these settings")
        await interaction.response.send_message(embed=embed)
        
    async def reset_automod_settings(self, interaction: discord.Interaction):
        """Reset AutoMod settings to default"""
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE guild_settings SET automod_settings = ? WHERE guild_id = ?', 
                      (json.dumps({}), interaction.guild.id))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="🔄 AutoMod Reset",
            description="All AutoMod settings have been reset to default (disabled).",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="automod-spam", description="Configure spam protection settings")
    @app_commands.describe(
        enabled="Enable or disable spam protection",
        max_messages="Maximum messages in time window",
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
        """Configure spam protection"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to use this command.", ephemeral=True)
            return
        
        # Validate inputs
        if max_messages < 1 or max_messages > 20:
            await interaction.response.send_message("❌ Max messages must be between 1 and 20.", ephemeral=True)
            return
            
        if time_window < 1 or time_window > 60:
            await interaction.response.send_message("❌ Time window must be between 1 and 60 seconds.", ephemeral=True)
            return
        
        # Get current settings
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT automod_settings FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
        result = cursor.fetchone()
        
        settings = {}
        if result and result[0]:
            try:
                settings = json.loads(result[0])
            except json.JSONDecodeError:
                settings = {}
        
        # Update spam settings
        settings['spam'] = {
            'enabled': enabled,
            'max_messages': max_messages,
            'time_window': time_window,
            'action': action
        }
        
        # Save settings
        cursor.execute('UPDATE guild_settings SET automod_settings = ? WHERE guild_id = ?', 
                      (json.dumps(settings), interaction.guild.id))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="🚫 Spam Protection Configured",
            description="Spam protection settings have been updated.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Settings",
            value=(
                f"**Enabled:** {'✅' if enabled else '❌'}\n"
                f"**Max Messages:** {max_messages}\n"
                f"**Time Window:** {time_window}s\n"
                f"**Action:** {action}"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="automod-links", description="Configure link filtering settings")
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
        """Configure link filtering"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to use this command.", ephemeral=True)
            return
        
        # Get current settings
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT automod_settings FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
        result = cursor.fetchone()
        
        settings = {}
        if result and result[0]:
            try:
                settings = json.loads(result[0])
            except json.JSONDecodeError:
                settings = {}
        
        # Update link settings
        settings['links'] = {
            'enabled': enabled,
            'block_invites': block_invites,
            'block_urls': block_urls,
            'action': action
        }
        
        # Save settings
        cursor.execute('UPDATE guild_settings SET automod_settings = ? WHERE guild_id = ?', 
                      (json.dumps(settings), interaction.guild.id))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="🔗 Link Filtering Configured",
            description="Link filtering settings have been updated.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Settings",
            value=(
                f"**Enabled:** {'✅' if enabled else '❌'}\n"
                f"**Block Invites:** {'✅' if block_invites else '❌'}\n"
                f"**Block URLs:** {'✅' if block_urls else '❌'}\n"
                f"**Action:** {action}"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="automod-badwords", description="Configure bad words filter settings")
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
        """Configure bad words filter"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to use this command.", ephemeral=True)
            return
        
        # Get current settings
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT automod_settings FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
        result = cursor.fetchone()
        
        settings = {}
        if result and result[0]:
            try:
                settings = json.loads(result[0])
            except json.JSONDecodeError:
                settings = {}
        
        # Update bad words settings
        settings['badwords'] = {
            'enabled': enabled,
            'strict': strict,
            'action': action,
            'custom_words': settings.get('badwords', {}).get('custom_words', [])
        }
        
        # Save settings
        cursor.execute('UPDATE guild_settings SET automod_settings = ? WHERE guild_id = ?', 
                      (json.dumps(settings), interaction.guild.id))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="🤬 Bad Words Filter Configured",
            description="Bad words filter settings have been updated.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Settings",
            value=(
                f"**Enabled:** {'✅' if enabled else '❌'}\n"
                f"**Strict Mode:** {'✅' if strict else '❌'}\n"
                f"**Custom Words:** {len(settings['badwords']['custom_words'])}\n"
                f"**Action:** {action}"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Note",
            value="Use `/automod-words add <word>` to add custom words to the filter.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
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
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to use this command.", ephemeral=True)
            return
        
        # Get current settings
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT automod_settings FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
        result = cursor.fetchone()
        
        settings = {}
        if result and result[0]:
            try:
                settings = json.loads(result[0])
            except json.JSONDecodeError:
                settings = {}
        
        # Initialize badwords settings if not exists
        if 'badwords' not in settings:
            settings['badwords'] = {
                'enabled': False,
                'strict': False,
                'action': 'delete',
                'custom_words': []
            }
        
        custom_words = settings['badwords'].get('custom_words', [])
        
        if action == "add":
            if not word:
                await interaction.response.send_message("❌ Please provide a word to add.", ephemeral=True)
                return
                
            word = word.lower().strip()
            if word not in custom_words:
                custom_words.append(word)
                settings['badwords']['custom_words'] = custom_words
                
                # Save settings
                cursor.execute('UPDATE guild_settings SET automod_settings = ? WHERE guild_id = ?', 
                              (json.dumps(settings), interaction.guild.id))
                conn.commit()
                
                embed = discord.Embed(
                    title="✅ Word Added",
                    description=f"Added '{word}' to the bad words filter.",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="⚠️ Word Already Exists",
                    description=f"'{word}' is already in the bad words filter.",
                    color=discord.Color.orange()
                )
                
        elif action == "remove":
            if not word:
                await interaction.response.send_message("❌ Please provide a word to remove.", ephemeral=True)
                return
                
            word = word.lower().strip()
            if word in custom_words:
                custom_words.remove(word)
                settings['badwords']['custom_words'] = custom_words
                
                # Save settings
                cursor.execute('UPDATE guild_settings SET automod_settings = ? WHERE guild_id = ?', 
                              (json.dumps(settings), interaction.guild.id))
                conn.commit()
                
                embed = discord.Embed(
                    title="✅ Word Removed",
                    description=f"Removed '{word}' from the bad words filter.",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="⚠️ Word Not Found",
                    description=f"'{word}' is not in the bad words filter.",
                    color=discord.Color.orange()
                )
                
        elif action == "list":
            if custom_words:
                embed = discord.Embed(
                    title="📝 Custom Bad Words",
                    description=f"**Total:** {len(custom_words)} words",
                    color=discord.Color.blue()
                )
                
                # Split words into chunks to avoid embed limits
                word_chunks = [custom_words[i:i+20] for i in range(0, len(custom_words), 20)]
                for i, chunk in enumerate(word_chunks):
                    embed.add_field(
                        name=f"Words {i*20+1}-{min((i+1)*20, len(custom_words))}",
                        value="• " + "\n• ".join(chunk),
                        inline=False
                    )
            else:
                embed = discord.Embed(
                    title="📝 Custom Bad Words",
                    description="No custom bad words configured.",
                    color=discord.Color.blue()
                )
                
        elif action == "clear":
            settings['badwords']['custom_words'] = []
            
            # Save settings
            cursor.execute('UPDATE guild_settings SET automod_settings = ? WHERE guild_id = ?', 
                          (json.dumps(settings), interaction.guild.id))
            conn.commit()
            
            embed = discord.Embed(
                title="🗑️ Words Cleared",
                description="All custom bad words have been cleared.",
                color=discord.Color.orange()
            )
            
        conn.close()
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoModCog(bot))