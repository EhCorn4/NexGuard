#!/usr/bin/env python3
"""
Simple Direct Bot Startup - No complex extensions, just core functionality
"""
import os
import sys
import asyncio
import logging
import json
from datetime import datetime
import discord
from discord.ext import commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/nexguard_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get bot token
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN') or os.getenv('DISCORD_TOKEN')
if not BOT_TOKEN:
    logger.error("No bot token found! Set DISCORD_BOT_TOKEN environment variable.")
    sys.exit(1)

# Create bot instance
class SimpleNexGuard(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents)
        
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        logger.info(f'Bot can see {len(self.users)} users')
        
        # Create status file for bot manager
        try:
            status_data = {
                "status": "ready",
                "timestamp": datetime.now().isoformat(),
                "guilds": len(self.guilds),
                "users": len(self.users),
                "bot_name": str(self.user),
                "bot_id": str(self.user.id)
            }
            with open("/tmp/nexguard_bot_status.json", "w") as f:
                json.dump(status_data, f, indent=2)
            logger.info("Bot status file created - ready")
        except Exception as e:
            logger.error(f"Failed to create status file: {e}")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f'Synced {len(synced)} slash commands globally')
            
            # Also sync for each guild for immediate availability
            for guild in self.guilds:
                try:
                    guild_synced = await self.tree.sync(guild=guild)
                    logger.info(f'Synced {len(guild_synced)} commands for guild: {guild.name}')
                except Exception as guild_e:
                    logger.error(f'Failed to sync commands for guild {guild.name}: {guild_e}')
        except Exception as e:
            logger.error(f'Failed to sync slash commands: {e}')

    async def on_message(self, message):
        """Handle messages"""
        if message.author == self.user:
            return
        
        # Basic ping command
        if message.content.lower() == '!ping':
            await message.channel.send('Pong! 🏓')
        
        # Process commands
        await self.process_commands(message)

    async def on_guild_join(self, guild):
        """Called when bot joins a guild"""
        logger.info(f'Bot joined guild: {guild.name} (ID: {guild.id})')
        
    async def on_guild_remove(self, guild):
        """Called when bot leaves a guild"""
        logger.info(f'Bot left guild: {guild.name} (ID: {guild.id})')

# Add some basic commands
bot = SimpleNexGuard()

@bot.command(name='test')
async def test_command(ctx):
    """Test command"""
    await ctx.send('✅ Bot is working!')

@bot.command(name='info')
async def info_command(ctx):
    """Bot info command"""
    embed = discord.Embed(
        title="NexGuard Bot Info",
        description="Simple Discord moderation bot",
        color=0x00ff00
    )
    embed.add_field(name="Guilds", value=len(bot.guilds), inline=True)
    embed.add_field(name="Users", value=len(bot.users), inline=True)
    embed.add_field(name="Latency", value=f"{bot.latency*1000:.2f}ms", inline=True)
    await ctx.send(embed=embed)

# Add slash commands
@bot.tree.command(name='ping', description='Check if the bot is responsive')
async def ping_slash(interaction: discord.Interaction):
    """Ping slash command"""
    await interaction.response.send_message('Pong! 🏓')

@bot.tree.command(name='info', description='Get bot information')
async def info_slash(interaction: discord.Interaction):
    """Info slash command"""
    embed = discord.Embed(
        title="NexGuard Bot Info",
        description="Simple Discord moderation bot",
        color=0x00ff00
    )
    embed.add_field(name="Guilds", value=len(bot.guilds), inline=True)
    embed.add_field(name="Users", value=len(bot.users), inline=True)
    embed.add_field(name="Latency", value=f"{bot.latency*1000:.2f}ms", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='ban', description='Ban a user from the server')
async def ban_slash(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    """Ban slash command"""
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ You don't have permission to ban members!", ephemeral=True)
        return
    
    try:
        await user.ban(reason=reason)
        embed = discord.Embed(
            title="User Banned",
            description=f"✅ {user.mention} has been banned from the server.",
            color=0xff0000
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Banned by", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to ban this user!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error banning user: {str(e)}", ephemeral=True)

@bot.tree.command(name='kick', description='Kick a user from the server')
async def kick_slash(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    """Kick slash command"""
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ You don't have permission to kick members!", ephemeral=True)
        return
    
    try:
        await user.kick(reason=reason)
        embed = discord.Embed(
            title="User Kicked",
            description=f"✅ {user.mention} has been kicked from the server.",
            color=0xff9900
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Kicked by", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to kick this user!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error kicking user: {str(e)}", ephemeral=True)

@bot.tree.command(name='mute', description='Timeout a user')
async def mute_slash(interaction: discord.Interaction, user: discord.Member, duration: int = 60, reason: str = "No reason provided"):
    """Mute/timeout slash command"""
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ You don't have permission to timeout members!", ephemeral=True)
        return
    
    try:
        import datetime
        timeout_duration = datetime.timedelta(minutes=duration)
        await user.timeout(timeout_duration, reason=reason)
        embed = discord.Embed(
            title="User Timed Out",
            description=f"✅ {user.mention} has been timed out for {duration} minutes.",
            color=0xffff00
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Timed out by", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to timeout this user!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error timing out user: {str(e)}", ephemeral=True)

@bot.tree.command(name='unmute', description='Remove timeout from a user')
async def unmute_slash(interaction: discord.Interaction, user: discord.Member):
    """Unmute slash command"""
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ You don't have permission to remove timeouts!", ephemeral=True)
        return
    
    try:
        await user.timeout(None)
        embed = discord.Embed(
            title="User Timeout Removed",
            description=f"✅ {user.mention}'s timeout has been removed.",
            color=0x00ff00
        )
        embed.add_field(name="Removed by", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to remove timeout from this user!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error removing timeout: {str(e)}", ephemeral=True)

@bot.tree.command(name='purge', description='Delete multiple messages')
async def purge_slash(interaction: discord.Interaction, amount: int):
    """Purge slash command"""
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You don't have permission to manage messages!", ephemeral=True)
        return
    
    if amount < 1 or amount > 100:
        await interaction.response.send_message("❌ Amount must be between 1 and 100!", ephemeral=True)
        return
    
    try:
        await interaction.response.defer()
        deleted = await interaction.channel.purge(limit=amount)
        embed = discord.Embed(
            title="Messages Purged",
            description=f"✅ Deleted {len(deleted)} messages.",
            color=0x0099ff
        )
        embed.add_field(name="Purged by", value=interaction.user.mention, inline=True)
        await interaction.followup.send(embed=embed)
    except discord.Forbidden:
        await interaction.followup.send("❌ I don't have permission to delete messages!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error purging messages: {str(e)}", ephemeral=True)

async def main():
    """Main function to start the bot"""
    logger.info("Starting simple NexGuard Discord Bot...")
    
    try:
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())