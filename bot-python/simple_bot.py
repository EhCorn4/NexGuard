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