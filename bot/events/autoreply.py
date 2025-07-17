"""
NexGuard Auto-Reply Event Handler
Handles message scanning and auto-reply triggering
"""

import discord
from discord.ext import commands
import json
import logging
import sqlite3

logger = logging.getLogger(__name__)

class AutoReplyHandler(commands.Cog):
    """Event handler for auto-reply system"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def _is_non_text_message(self, message):
        """Check if message contains only non-text content (links, attachments, embeds)"""
        import re
        
        # Check for attachments
        if message.attachments:
            return True
        
        # Check for embeds
        if message.embeds:
            return True
        
        # Check if message is only URLs/links
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, message.content)
        
        # Remove URLs from content to check what's left
        content_without_urls = re.sub(url_pattern, '', message.content).strip()
        
        # If content is mostly URLs or empty after removing URLs, skip
        if not content_without_urls or len(content_without_urls) < 3:
            return True
        
        # Check for Discord invite links
        invite_pattern = r'(discord\.gg/|discord\.com/invite/|discordapp\.com/invite/)[^\s]+'
        if re.search(invite_pattern, message.content, re.IGNORECASE):
            return True
        
        # Check for common GIF/image hosting domains
        media_domains = [
            'tenor.com', 'giphy.com', 'imgur.com', 'media.discordapp.net',
            'cdn.discordapp.com', 'i.redd.it', 'gfycat.com', 'streamable.com'
        ]
        
        for domain in media_domains:
            if domain in message.content.lower():
                return True
        
        return False
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle message events for auto-reply scanning"""
        # Skip if bot message or no guild
        if message.author.bot or not message.guild:
            return
        
        # Skip system messages (joins, boosts, etc.)
        if message.type != discord.MessageType.default:
            return
        
        # Skip if message is empty or too short
        if not message.content or len(message.content) < 2:
            return
        
        # Skip if message contains only links, attachments, or embeds
        if self._is_non_text_message(message):
            return
        
        # Skip if message starts with command prefix
        if message.content.startswith(('!', '/', '.', '>', '<', '?', ';')):
            return
        
        try:
            # Get enabled auto-reply rules for this guild
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, keywords, response_data, match_type, cooldown
                    FROM autoreply_rules 
                    WHERE guild_id = ? AND enabled = TRUE
                    ORDER BY id
                ''', (str(message.guild.id),))
                
                rules = cursor.fetchall()
            
            if not rules:
                logger.debug(f"No enabled auto-reply rules found for guild {message.guild.id}")
                return
            
            # Get the AutoReply cog for helper methods
            autoreply_cog = self.bot.get_cog('AutoReply')
            if not autoreply_cog:
                return
            
            # Check each rule
            for rule in rules:
                rule_id, name, keywords, response_data, match_type, cooldown = rule
                
                # Check if message matches keywords
                if autoreply_cog.check_message_for_keywords(message.content, keywords, match_type):
                    # Check cooldown
                    if autoreply_cog.check_cooldown(
                        str(message.guild.id), 
                        rule_id, 
                        str(message.author.id), 
                        str(message.channel.id), 
                        cooldown
                    ):
                        continue  # Skip if on cooldown
                    
                    # Update cooldown
                    autoreply_cog.update_cooldown(
                        str(message.guild.id), 
                        rule_id, 
                        str(message.author.id), 
                        str(message.channel.id)
                    )
                    
                    # Log the trigger
                    autoreply_cog.log_trigger(
                        str(message.guild.id), 
                        rule_id, 
                        str(message.author.id), 
                        str(message.channel.id)
                    )
                    
                    # Send the auto-reply
                    await self.send_autoreply(message, response_data, name)
                    
                    # Only trigger one rule per message
                    break
                    
        except Exception as e:
            logger.error(f"Error processing auto-reply for message {message.id}: {e}")
    
    async def send_autoreply(self, message, response_data_str, rule_name):
        """Send an auto-reply embed"""
        try:
            response_data = json.loads(response_data_str)
            
            # Create embed
            embed = discord.Embed(
                title=response_data.get('title', 'Auto Reply'),
                description=response_data.get('description', ''),
                color=response_data.get('color', 0x00d4ff)
            )
            
            # Add timestamp if specified
            if response_data.get('timestamp'):
                embed.timestamp = discord.utils.utcnow()
            
            # Add footer if specified
            footer_data = response_data.get('footer')
            if footer_data:
                embed.set_footer(
                    text=footer_data.get('text', ''),
                    icon_url=footer_data.get('icon_url')
                )
            
            # Add fields if specified
            fields = response_data.get('fields', [])
            for field in fields:
                embed.add_field(
                    name=field.get('name', 'Field'),
                    value=field.get('value', ''),
                    inline=field.get('inline', False)
                )
            
            # Add image if specified
            if response_data.get('image'):
                embed.set_image(url=response_data['image'])
            
            # Add thumbnail if specified
            if response_data.get('thumbnail'):
                embed.set_thumbnail(url=response_data['thumbnail'])
            
            # Send the embed
            await message.reply(embed=embed, mention_author=False)
            
            logger.info(f"Auto-reply '{rule_name}' sent in guild {message.guild.id}, channel {message.channel.id}")
            
        except Exception as e:
            logger.error(f"Error sending auto-reply: {e}")
            
            # Send a simple text message if embed fails
            try:
                await message.reply(f"Auto-reply system triggered but failed to send embed: {rule_name}", mention_author=False)
            except:
                pass  # Silently fail if we can't send even a simple message

async def setup(bot):
    await bot.add_cog(AutoReplyHandler(bot))