import discord
from discord.ext import commands
import sqlite3
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageLogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log message edits"""
        if before.author.bot:
            return
        
        if before.content == after.content:
            return  # No actual content change
        
        try:
            # Check if message logging is enabled
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT log_channel, message_logs FROM guild_settings WHERE guild_id = ?', (before.guild.id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result or not result[0] or not result[1]:
                return
                
            log_channel = before.guild.get_channel(result[0])
            if not log_channel:
                return
            
            # Log to database
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action, additional_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                before.guild.id,
                before.channel.id,
                before.author.id,
                before.id,
                before.content,
                'EDIT',
                json.dumps({
                    'before': before.content[:1000],  # Limit content length
                    'after': after.content[:1000],
                    'channel_name': before.channel.name
                })
            ))
            conn.commit()
            conn.close()
            
            # Create embed for log channel
            embed = discord.Embed(
                title="📝 Message Edited",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="User",
                value=f"{before.author} (`{before.author.id}`)",
                inline=True
            )
            
            embed.add_field(
                name="Channel",
                value=f"{before.channel.mention}",
                inline=True
            )
            
            embed.add_field(
                name="Message ID",
                value=f"`{before.id}`",
                inline=True
            )
            
            # Show before/after content
            if before.content:
                embed.add_field(
                    name="Before",
                    value=before.content[:1000] + ("..." if len(before.content) > 1000 else ""),
                    inline=False
                )
            
            if after.content:
                embed.add_field(
                    name="After",
                    value=after.content[:1000] + ("..." if len(after.content) > 1000 else ""),
                    inline=False
                )
            
            embed.add_field(
                name="Jump to Message",
                value=f"[Click here]({after.jump_url})",
                inline=False
            )
            
            embed.set_footer(text=f"User ID: {before.author.id}")
            embed.set_thumbnail(url=before.author.display_avatar.url)
            
            await log_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error logging message edit: {e}")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log message deletions"""
        if message.author.bot:
            return
        
        try:
            # Check if message logging is enabled
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT log_channel, message_logs FROM guild_settings WHERE guild_id = ?', (message.guild.id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result or not result[0] or not result[1]:
                return
                
            log_channel = message.guild.get_channel(result[0])
            if not log_channel:
                return
            
            # Log to database
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action, additional_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                message.guild.id,
                message.channel.id,
                message.author.id,
                message.id,
                message.content,
                'DELETE',
                json.dumps({
                    'channel_name': message.channel.name,
                    'attachments': [att.filename for att in message.attachments],
                    'embeds': len(message.embeds)
                })
            ))
            conn.commit()
            conn.close()
            
            # Create embed for log channel
            embed = discord.Embed(
                title="🗑️ Message Deleted",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="User",
                value=f"{message.author} (`{message.author.id}`)",
                inline=True
            )
            
            embed.add_field(
                name="Channel",
                value=f"{message.channel.mention}",
                inline=True
            )
            
            embed.add_field(
                name="Message ID",
                value=f"`{message.id}`",
                inline=True
            )
            
            if message.content:
                embed.add_field(
                    name="Content",
                    value=message.content[:1000] + ("..." if len(message.content) > 1000 else ""),
                    inline=False
                )
            
            if message.attachments:
                attachment_names = [att.filename for att in message.attachments]
                embed.add_field(
                    name="Attachments",
                    value=", ".join(attachment_names),
                    inline=False
                )
            
            if message.embeds:
                embed.add_field(
                    name="Embeds",
                    value=f"{len(message.embeds)} embed(s)",
                    inline=False
                )
            
            embed.set_footer(text=f"User ID: {message.author.id}")
            embed.set_thumbnail(url=message.author.display_avatar.url)
            
            await log_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error logging message deletion: {e}")
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        """Log bulk message deletions"""
        if not messages:
            return
        
        # Get the first message to determine guild/channel
        first_message = messages[0]
        
        try:
            # Get log channel
            log_channel = await self.get_log_channel(first_message.guild)
            if not log_channel:
                return
            
            # Log to database
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            
            for message in messages:
                if not message.author.bot:
                    cursor.execute('''
                        INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action, additional_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        message.guild.id,
                        message.channel.id,
                        message.author.id,
                        message.id,
                        message.content,
                        'BULK_DELETE',
                        json.dumps({
                            'channel_name': message.channel.name,
                            'total_deleted': len(messages)
                        })
                    ))
            
            conn.commit()
            conn.close()
            
            # Create embed for log channel
            embed = discord.Embed(
                title="🗑️ Bulk Message Deletion",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="Channel",
                value=f"{first_message.channel.mention}",
                inline=True
            )
            
            embed.add_field(
                name="Messages Deleted",
                value=f"{len(messages)}",
                inline=True
            )
            
            embed.add_field(
                name="Channel ID",
                value=f"`{first_message.channel.id}`",
                inline=True
            )
            
            # Show some statistics
            user_counts = {}
            for message in messages:
                if not message.author.bot:
                    user_counts[message.author] = user_counts.get(message.author, 0) + 1
            
            if user_counts:
                top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                user_list = []
                for user, count in top_users:
                    user_list.append(f"{user}: {count} messages")
                
                embed.add_field(
                    name="Top Users (Messages Deleted)",
                    value="\n".join(user_list),
                    inline=False
                )
            
            await log_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error logging bulk message deletion: {e}")
    
    # Removed old basic automod - now handled by dedicated automod engine
    
    async def get_log_channel(self, guild):
        """Get the log channel for a guild"""
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT log_channel FROM guild_settings WHERE guild_id = ?', (guild.id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return guild.get_channel(result[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting log channel: {e}")
            return None

async def setup(bot):
    await bot.add_cog(MessageLogCog(bot))
