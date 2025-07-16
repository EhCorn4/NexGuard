import discord
from discord.ext import commands
import logging
import sqlite3
import json

logger = logging.getLogger(__name__)

class WelcomeEventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle member join events and send welcome messages"""
        
        # Skip bots for welcome messages (but still log them)
        if member.bot:
            logger.info(f"Bot {member.name} joined {member.guild.name}")
            return
        
        try:
            # Get welcome settings
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT welcome_settings FROM guild_settings WHERE guild_id = ?', (member.guild.id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result or not result[0]:
                # No welcome settings configured
                return
            
            try:
                settings = json.loads(result[0])
            except json.JSONDecodeError:
                logger.error(f"Invalid welcome settings JSON for guild {member.guild.id}")
                return
            
            if not settings.get('enabled', False):
                # Welcome messages disabled
                return
            
            # Get welcome channel
            channel_id = settings.get('channel_id')
            if not channel_id:
                logger.warning(f"No welcome channel configured for guild {member.guild.name}")
                return
            
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.warning(f"Welcome channel {channel_id} not found for guild {member.guild.name}")
                return
            
            # Get the welcome cog to generate message
            welcome_cog = self.bot.get_cog('WelcomeCog')
            if not welcome_cog:
                logger.error("WelcomeCog not found, cannot generate welcome message")
                return
            
            # Generate and send welcome message
            welcome_message = await welcome_cog.generate_welcome_message(member)
            
            if welcome_message:
                if isinstance(welcome_message, discord.Embed):
                    await channel.send(embed=welcome_message)
                else:
                    await channel.send(welcome_message)
                
                logger.info(f"Welcome message sent for {member.name} in {member.guild.name}")
                
                # Log the welcome message event
                self.log_welcome_event(member.guild.id, member.id, "welcome_sent", {
                    'ai_powered': settings.get('ai_personalization', False),
                    'tone': settings.get('tone', 'friendly'),
                    'channel': channel.name
                })
            
        except Exception as e:
            logger.error(f"Error sending welcome message for {member.name} in {member.guild.name}: {e}")
    
    def log_welcome_event(self, guild_id, user_id, event_type, additional_data):
        """Log welcome events to database"""
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO member_logs (guild_id, user_id, action, additional_info)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, user_id, event_type, json.dumps(additional_data)))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log welcome event: {e}")

async def setup(bot):
    await bot.add_cog(WelcomeEventsCog(bot))