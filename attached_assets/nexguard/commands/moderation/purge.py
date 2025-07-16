import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PurgeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='purge', description='Delete multiple messages from the channel')
    @app_commands.describe(
        amount='Number of messages to delete (1-100)',
        member='Only delete messages from this member'
    )
    async def purge(self, interaction: discord.Interaction, amount: int, member: discord.Member = None):
        """Purge messages from the channel"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_messages:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to manage messages.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if amount < 1 or amount > 100:
            embed = discord.Embed(
                title="❌ Invalid Amount",
                description="Please specify a number between 1 and 100.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Defer the response since purging might take time
            await interaction.response.defer()
            
            # Define check function for filtering messages
            def check(message):
                if member:
                    return message.author == member
                return True
            
            # Delete messages
            deleted = await interaction.channel.purge(limit=amount, check=check)
            
            # Log the purge
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interaction.guild.id, interaction.channel.id, interaction.user.id, interaction.id, 
                  f"Purged {len(deleted)} messages" + (f" from {member}" if member else ""), 'PURGE'))
            conn.commit()
            conn.close()
            
            # Send confirmation
            embed = discord.Embed(
                title="🗑️ Messages Purged",
                description=f"Successfully deleted **{len(deleted)}** messages" + (f" from {member.mention}" if member else ""),
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"Purged by {interaction.user}")
            
            # Send as followup since we already deferred
            await interaction.followup.send(embed=embed)
            
            logger.info(f"Purged {len(deleted)} messages in {interaction.channel.name} by {interaction.user}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to delete messages in this channel.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error purging messages: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while trying to purge messages.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name='purgebot', description='Delete bot messages from the channel')
    @app_commands.describe(amount='Number of messages to scan (1-100)')
    async def purgebot(self, interaction: discord.Interaction, amount: int = 50):
        """Purge bot messages from the channel"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_messages:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to manage messages.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if amount < 1 or amount > 100:
            embed = discord.Embed(
                title="❌ Invalid Amount",
                description="Please specify a number between 1 and 100.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Defer the response since purging might take time
            await interaction.response.defer()
            
            # Define check function for bot messages
            def check(message):
                return message.author.bot
            
            # Delete messages
            deleted = await interaction.channel.purge(limit=amount, check=check)
            
            # Log the purge
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interaction.guild.id, interaction.channel.id, interaction.user.id, interaction.id, 
                  f"Purged {len(deleted)} bot messages", 'PURGE_BOT'))
            conn.commit()
            conn.close()
            
            # Send confirmation
            embed = discord.Embed(
                title="🤖 Bot Messages Purged",
                description=f"Successfully deleted **{len(deleted)}** bot messages",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"Purged by {interaction.user}")
            
            # Send as followup since we already deferred
            await interaction.followup.send(embed=embed)
            
            logger.info(f"Purged {len(deleted)} bot messages in {interaction.channel.name} by {interaction.user}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to delete messages in this channel.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error purging bot messages: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while trying to purge bot messages.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(PurgeCog(bot))