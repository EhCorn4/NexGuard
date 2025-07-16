import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import json
import re
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AutoModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = bot.db_path
    
    def get_automod_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get automod settings for a guild"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT automod_settings FROM guild_settings WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            try:
                return json.loads(result[0])
            except json.JSONDecodeError:
                return {}
        return {}
    
    def save_automod_settings(self, guild_id: int, settings: Dict[str, Any]):
        """Save automod settings for a guild"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE guild_settings SET automod_settings = ? WHERE guild_id = ?', 
                      (json.dumps(settings), guild_id))
        conn.commit()
        conn.close()
    
    @app_commands.command(name="automod-config", description="Configure AutoMod settings")
    async def automod_config(self, interaction: discord.Interaction):
        """Configure AutoMod settings with interactive menu"""
        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need 'Manage Server' permission to configure AutoMod.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        settings = self.get_automod_settings(interaction.guild.id)
        
        embed = discord.Embed(
            title="🤖 AutoMod Configuration",
            description="Current AutoMod settings for this server:",
            color=discord.Color.blue()
        )
        
        # Add current settings
        for feature in ['spam', 'links', 'badwords', 'caps', 'mentions']:
            feature_settings = settings.get(feature, {})
            enabled = feature_settings.get('enabled', False)
            embed.add_field(
                name=f"{'✅' if enabled else '❌'} {feature.title()}",
                value=f"Status: {'Enabled' if enabled else 'Disabled'}",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
    
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
        """Configure spam protection"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to use this command.", ephemeral=True)
            return
        
        settings = self.get_automod_settings(interaction.guild.id)
        settings['spam'] = {
            'enabled': enabled,
            'max_messages': max_messages,
            'time_window': time_window,
            'action': action
        }
        
        self.save_automod_settings(interaction.guild.id, settings)
        
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
        """Configure link filtering"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to use this command.", ephemeral=True)
            return
        
        settings = self.get_automod_settings(interaction.guild.id)
        settings['links'] = {
            'enabled': enabled,
            'block_invites': block_invites,
            'block_urls': block_urls,
            'action': action
        }
        
        self.save_automod_settings(interaction.guild.id, settings)
        
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
        """Configure bad words filter"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to use this command.", ephemeral=True)
            return
        
        settings = self.get_automod_settings(interaction.guild.id)
        if 'badwords' not in settings:
            settings['badwords'] = {'custom_words': []}
        
        settings['badwords'].update({
            'enabled': enabled,
            'strict': strict,
            'action': action
        })
        
        self.save_automod_settings(interaction.guild.id, settings)
        
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
        
        settings = self.get_automod_settings(interaction.guild.id)
        if 'badwords' not in settings:
            settings['badwords'] = {'custom_words': []}
        
        custom_words = settings['badwords']['custom_words']
        
        if action == "add":
            if not word:
                await interaction.response.send_message("❌ Please provide a word to add.", ephemeral=True)
                return
            
            word = word.lower().strip()
            if word not in custom_words:
                custom_words.append(word)
                settings['badwords']['custom_words'] = custom_words
                self.save_automod_settings(interaction.guild.id, settings)
                
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
                self.save_automod_settings(interaction.guild.id, settings)
                
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
                
                # Split words into chunks
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
            self.save_automod_settings(interaction.guild.id, settings)
            
            embed = discord.Embed(
                title="🗑️ Words Cleared",
                description="All custom bad words have been cleared.",
                color=discord.Color.orange()
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoModCog(bot))