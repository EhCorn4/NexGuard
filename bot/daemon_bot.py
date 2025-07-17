#!/usr/bin/env python3
"""
Daemon Bot Runner
Ensures the bot stays running in the background and responds to Discord commands
"""

import os
import sys
import signal
import asyncio
import logging
from index import NexGuard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/nexguard_daemon.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BotDaemon:
    def __init__(self):
        self.bot = None
        self.running = True
        
    def signal_handler(self, signum, frame):
        logger.info(f'Received signal {signum}, shutting down...')
        self.running = False
        if self.bot:
            asyncio.create_task(self.bot.close())
            
    async def run(self):
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Get token
        token = os.getenv('DISCORD_BOT_TOKEN', '').strip()
        if not token:
            token = os.getenv('DISCORD_TOKEN', '').strip()
            
        if not token:
            logger.error('No Discord token found!')
            return
            
        while self.running:
            try:
                logger.info('Starting bot daemon...')
                self.bot = NexGuard()
                
                # Custom event handlers for daemon mode
                @self.bot.event
                async def on_ready():
                    logger.info(f'Bot daemon ready: {self.bot.user}')
                    logger.info(f'Guilds: {len(self.bot.guilds)}')
                    logger.info('Bot is ready and will respond to slash commands')
                    
                    # Update status file
                    import json
                    from datetime import datetime
                    status_data = {
                        'online': True,
                        'guilds': len(self.bot.guilds),
                        'users': sum(guild.member_count for guild in self.bot.guilds),
                        'uptime': '0s',
                        'commands': len(self.bot.tree.get_commands()),
                        'lastHeartbeat': datetime.utcnow().isoformat() + 'Z',
                        'version': '2.3.2',
                        'lastUpdated': datetime.utcnow().isoformat() + 'Z'
                    }
                    
                    with open('/tmp/nexguard_bot_status.json', 'w') as f:
                        json.dump(status_data, f)
                
                @self.bot.event
                async def on_error(event, *args, **kwargs):
                    logger.error(f'Bot error in event {event}:')
                    import traceback
                    traceback.print_exc()
                
                # Start the bot
                await self.bot.start(token)
                
            except Exception as e:
                logger.error(f'Bot daemon error: {e}')
                if self.running:
                    logger.info('Restarting in 5 seconds...')
                    await asyncio.sleep(5)
                else:
                    break
                    
        logger.info('Bot daemon stopped')

if __name__ == '__main__':
    daemon = BotDaemon()
    try:
        asyncio.run(daemon.run())
    except KeyboardInterrupt:
        logger.info('Bot daemon stopped by user')