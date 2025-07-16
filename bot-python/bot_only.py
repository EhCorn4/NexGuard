#!/usr/bin/env python3
"""
Discord Bot Only - No HTTP server, just the Discord bot
"""

import asyncio
import os
import logging
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexguard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up Discord token
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN') or os.getenv('DISCORD_TOKEN')

if not DISCORD_TOKEN:
    logger.error("DISCORD_TOKEN or DISCORD_BOT_TOKEN not found in environment variables")
    sys.exit(1)

async def main():
    """Main function to start the Discord bot"""
    try:
        logger.info("Starting NexGuard Discord Bot...")
        
        # Import and run the bot
        from index import bot
        
        logger.info("Bot imported successfully, starting...")
        await bot.start(DISCORD_TOKEN)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)