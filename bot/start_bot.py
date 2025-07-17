#!/usr/bin/env python3
"""
Persistent Bot Starter
Ensures the bot stays running and handles reconnections
"""

import asyncio
import os
import sys
import signal
import logging
from datetime import datetime
from index import bot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/nexguard_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global flag to control bot lifecycle
should_run = True

def signal_handler(signum, frame):
    global should_run
    logger.info(f"Received signal {signum}, shutting down...")
    should_run = False
    asyncio.create_task(bot.close())

async def main():
    global should_run
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get Discord token
    token = os.getenv('DISCORD_BOT_TOKEN', '').strip()
    if not token:
        token = os.getenv('DISCORD_TOKEN', '').strip()
    
    if not token:
        logger.error("No Discord token found!")
        sys.exit(1)
    
    logger.info(f"Starting persistent bot with token length: {len(token)}")
    
    while should_run:
        try:
            # Start the bot
            logger.info("Starting bot connection...")
            await bot.start(token)
            
        except discord.ConnectionClosed:
            logger.warning("Bot disconnected, attempting to reconnect...")
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Bot error: {e}")
            if should_run:
                logger.info("Retrying in 10 seconds...")
                await asyncio.sleep(10)
            else:
                break
    
    logger.info("Bot shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)