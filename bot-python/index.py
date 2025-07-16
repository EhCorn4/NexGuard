import discord
from discord.ext import commands
import sqlite3
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import asyncio

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

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.guild_messages = True

class NexGuard(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.start_time = datetime.utcnow()
        self.db_path = "nexguard/database/nexguard.db"
        self.setup_database()
        
    def setup_database(self):
        """Initialize the SQLite database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                prefix TEXT DEFAULT '!',
                log_channel INTEGER,
                mute_role INTEGER,
                welcome_channel INTEGER,
                auto_role INTEGER,
                mod_role_id INTEGER,
                message_logs INTEGER DEFAULT 1,
                member_logs INTEGER DEFAULT 1,
                moderation_logs INTEGER DEFAULT 1,
                channel_logs INTEGER DEFAULT 0,
                role_logs INTEGER DEFAULT 0,
                server_logs INTEGER DEFAULT 0,
                voice_logs INTEGER DEFAULT 0
            )
        ''')
        
        # Add new columns to existing tables if they don't exist
        new_columns = [
            'mod_role_id INTEGER',
            'message_logs INTEGER DEFAULT 1',
            'member_logs INTEGER DEFAULT 1', 
            'moderation_logs INTEGER DEFAULT 1',
            'channel_logs INTEGER DEFAULT 0',
            'role_logs INTEGER DEFAULT 0',
            'server_logs INTEGER DEFAULT 0',
            'voice_logs INTEGER DEFAULT 0',
            'automod_settings TEXT DEFAULT "{}"',
            'welcome_settings TEXT DEFAULT "{}"',
            'autorole_settings TEXT DEFAULT \'{"enabled": false, "roles": []}\''
        ]
        
        for column in new_columns:
            try:
                cursor.execute(f'ALTER TABLE guild_settings ADD COLUMN {column}')
            except sqlite3.OperationalError:
                # Column already exists
                pass
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mutes (
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                channel_id INTEGER,
                user_id INTEGER,
                message_id INTEGER,
                content TEXT,
                action TEXT,
                additional_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS member_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                action TEXT,
                additional_info TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def get_prefix(self, message):
        """Get the prefix for a guild"""
        if not message.guild:
            return '!'
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT prefix FROM guild_settings WHERE guild_id = ?', (message.guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            # Insert default settings for new guild
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)', (message.guild.id,))
            conn.commit()
            conn.close()
            return '!'
    
    async def load_extensions(self):
        """Load all command extensions"""
        extensions = [
            'commands.moderation.ban',
            'commands.moderation.mute',
            'commands.moderation.kick',
            'commands.moderation.warn',
            'commands.moderation.purge',
            'commands.moderation.unban',
            'commands.moderation.unmute',
            'commands.moderation.timeout',
            'commands.moderation.slowmode',
            'commands.moderation.lock',
            'commands.utilities.ping',
            'commands.utilities.userinfo',
            'commands.utilities.serverinfo',
            'commands.utilities.commands',
            'commands.utilities.help',
            'commands.utilities.embed',
            'commands.utilities.ai_assistant',
            'commands.utilities.dashboard',
            'commands.tickets.ticket',
            'commands.tickets.transcript',
            'commands.tickets.manage',
            'commands.admin.prefix',
            'commands.admin.changelog',
            'commands.admin.modrole',
            'commands.admin.logging',
            'commands.admin.automod',
            'commands.admin.welcome',
            'commands.admin.autorole',
            'commands.admin.autoreply',
            'events.on_ready',
            'events.message_log',
            'events.member_log',
            'events.server_log',
            'events.automod',
            'events.welcome',
            'events.autorole',
            'events.autoreply'
        ]
        
        for extension in extensions:
            try:
                await self.load_extension(f'nexguard.{extension}')
                logger.info(f'Loaded {extension}')
            except Exception as e:
                logger.error(f'Failed to load {extension}: {e}')
    
    async def setup_hook(self):
        """Setup hook called when bot starts"""
        await self.load_extensions()
        
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Sync slash commands
        try:
            # Sync globally first
            synced = await self.tree.sync()
            logger.info(f'Synced {len(synced)} slash commands globally')
            
            # Also sync for each guild to ensure immediate availability
            for guild in self.guilds:
                try:
                    guild_synced = await self.tree.sync(guild=guild)
                    logger.info(f'Synced {len(guild_synced)} commands for guild: {guild.name}')
                except Exception as guild_e:
                    logger.error(f'Failed to sync commands for guild {guild.name}: {guild_e}')
                    
        except Exception as e:
            logger.error(f'Failed to sync slash commands: {e}')
        
        # Bot status will be set by the on_ready event handler

# Create bot instance
bot = NexGuard()

# Run the bot
if __name__ == "__main__":
    try:
        token = os.getenv('DISCORD_TOKEN', '').strip()
        
        # Handle cases where token might have the format "DISCORD_TOKEN=actual_token"
        if '=' in token and token.startswith('DISCORD_TOKEN='):
            token = token.split('=', 1)[1].strip()
        
        if not token or token == 'your_bot_token_here':
            logger.error('No valid Discord token found. Please set the DISCORD_TOKEN environment variable.')
            exit(1)
        
        logger.info(f'Starting bot with token length: {len(token)}')
        bot.run(token)
    except Exception as e:
        logger.error(f'Failed to start bot: {e}')
