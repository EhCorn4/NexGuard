import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PrefixCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='prefix', description='View or change the bot\'s prefix for this server')
    @app_commands.describe(new_prefix='The new prefix to set (leave empty to view current)')
    async def prefix(self, interaction: discord.Interaction, new_prefix: str = None):
        """View or change the bot's prefix for this server"""
        
        if new_prefix is None:
            # Show current prefix
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT prefix FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
            result = cursor.fetchone()
            conn.close()
            
            current_prefix = result[0] if result else '!'
            
            embed = discord.Embed(
                title="🔧 Current Prefix",
                description=f"The current prefix for this server is: **`{current_prefix}`**",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(
                name="Usage",
                value=f"Use `{current_prefix}help` to see all commands",
                inline=False
            )
            embed.set_footer(text=f"Requested by {interaction.user}")
            await interaction.response.send_message(embed=embed)
            return
        
        # Check permissions to change prefix
        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need the 'Manage Server' permission to change the prefix.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate new prefix
        if len(new_prefix) > 5:
            embed = discord.Embed(
                title="❌ Invalid Prefix",
                description="Prefix must be 5 characters or less.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if '`' in new_prefix:
            embed = discord.Embed(
                title="❌ Invalid Prefix",
                description="Prefix cannot contain backticks (`).",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Update prefix in database
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO guild_settings (guild_id, prefix)
                VALUES (?, ?)
            ''', (interaction.guild.id, new_prefix))
            conn.commit()
            conn.close()
            
            # Send confirmation
            embed = discord.Embed(
                title="✅ Prefix Updated",
                description=f"Successfully changed the prefix to: **`{new_prefix}`**",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(
                name="Usage",
                value=f"Use `{new_prefix}help` to see all commands",
                inline=False
            )
            embed.set_footer(text=f"Changed by {interaction.user}")
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"Prefix changed to '{new_prefix}' in {interaction.guild.name} by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error updating prefix: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while updating the prefix.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='resetprefix', description='Reset the bot\'s prefix to default (!)')
    async def resetprefix(self, interaction: discord.Interaction):
        """Reset the bot's prefix to default (!)"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need the 'Manage Server' permission to reset the prefix.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Reset prefix in database
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO guild_settings (guild_id, prefix)
                VALUES (?, ?)
            ''', (interaction.guild.id, '!'))
            conn.commit()
            conn.close()
            
            # Send confirmation
            embed = discord.Embed(
                title="🔄 Prefix Reset",
                description="Successfully reset the prefix to default: **`!`**",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(
                name="Usage",
                value="Use `!help` to see all commands",
                inline=False
            )
            embed.set_footer(text=f"Reset by {interaction.user}")
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"Prefix reset to default in {interaction.guild.name} by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error resetting prefix: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while resetting the prefix.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(PrefixCog(bot))