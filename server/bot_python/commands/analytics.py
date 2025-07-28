import discord
from discord.ext import commands, tasks
import logging
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class AnalyticsTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_counts = {}  # Guild ID -> count
        self.command_counts = {}  # Guild ID -> count
        self.collect_analytics.start()
        
    async def cog_unload(self):
        self.collect_analytics.cancel()
    
    @tasks.loop(minutes=5)  # Collect analytics every 5 minutes
    async def collect_analytics(self):
        """Collect and store server analytics data"""
        try:
            if not self.bot.db_pool:
                return
            
            # Batch operations for better performance
            server_analytics_batch = []
            channel_analytics_batch = []
            
            for guild in self.bot.guilds:
                try:
                    # Calculate member counts efficiently
                    member_count = guild.member_count or 0
                    online_members = sum(1 for m in guild.members if m.status != discord.Status.offline)
                    voice_members = sum(1 for m in guild.members if m.voice)
                    
                    # Get message and command counts for this period
                    messages_this_period = self.message_counts.get(str(guild.id), 0)
                    commands_this_period = self.command_counts.get(str(guild.id), 0)
                    
                    # Prepare server analytics data
                    server_analytics_batch.append((
                        str(guild.id), member_count, online_members, 
                        messages_this_period, commands_this_period, voice_members
                    ))
                    
                    # Prepare channel analytics data (limited to avoid performance issues)
                    for channel in guild.text_channels[:50]:  # Limit to first 50 channels
                        channel_analytics_batch.append((
                            str(guild.id), str(channel.id), channel.name, "text", datetime.utcnow()
                        ))
                    
                    for channel in guild.voice_channels[:20]:  # Limit to first 20 voice channels
                        channel_analytics_batch.append((
                            str(guild.id), str(channel.id), channel.name, "voice", datetime.utcnow()
                        ))
                        
                except Exception as e:
                    logger.error(f"Error preparing analytics for guild {guild.id}: {e}")
            
            # Batch insert server analytics
            if server_analytics_batch:
                async with self.bot.db_pool.acquire() as conn:
                    await conn.executemany("""
                        INSERT INTO server_analytics 
                        (guild_id, member_count, online_members, messages_per_hour, 
                         commands_executed, voice_members)
                        VALUES ($1, $2, $3, $4, $5, $6)
                    """, server_analytics_batch)
            
            # Batch insert channel analytics
            if channel_analytics_batch:
                async with self.bot.db_pool.acquire() as conn:
                    for batch_data in channel_analytics_batch:
                        try:
                            await conn.execute("""
                                INSERT INTO channel_analytics 
                                (guild_id, channel_id, channel_name, channel_type, last_activity)
                                VALUES ($1, $2, $3, $4, $5)
                                ON CONFLICT (guild_id, channel_id) 
                                DO UPDATE SET last_activity = EXCLUDED.last_activity
                            """, *batch_data)
                        except Exception as e:
                            logger.error(f"Error inserting channel analytics: {e}")
            
            logger.info(f"Analytics collected for {len(server_analytics_batch)} guilds")
            
            # Reset counters
            self.message_counts.clear()
            self.command_counts.clear()
                
        except Exception as e:
            logger.error(f"Error in analytics collection: {e}")
    
    @collect_analytics.before_loop
    async def before_collect_analytics(self):
        await self.bot.wait_until_ready()
    
    async def process_message_analytics(self, message):
        """Track message analytics efficiently"""
        if message.author.bot or not message.guild:
            return
            
        guild_id = str(message.guild.id)
        
        # Increment in-memory counter for performance
        self.message_counts[guild_id] = self.message_counts.get(guild_id, 0) + 1
        
        # Store detailed message analytics (optimized)
        try:
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    current_time = datetime.utcnow()
                    hour = current_time.hour
                    
                    # Use single transaction for better performance
                    async with conn.transaction():
                        await conn.execute("""
                            INSERT INTO message_analytics 
                            (guild_id, channel_id, user_id, message_id, hour, timestamp, content_length, has_attachments)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        """, guild_id, str(message.channel.id), str(message.author.id), 
                             str(message.id), hour, current_time, len(message.content), len(message.attachments) > 0)
                        
                        # Update user activity efficiently
                        await conn.execute("""
                            INSERT INTO user_activity 
                            (guild_id, user_id, username, message_count, last_active)
                            VALUES ($1, $2, $3, 1, $4)
                            ON CONFLICT (guild_id, user_id)
                            DO UPDATE SET 
                                message_count = user_activity.message_count + 1,
                                last_active = $4,
                                username = $3
                        """, guild_id, str(message.author.id), message.author.name, current_time)
                    
        except Exception as e:
            logger.error(f"Error storing message analytics: {e}")
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Track command usage analytics"""
        if not ctx.guild:
            return
            
        guild_id = str(ctx.guild.id)
        
        # Increment command count
        self.command_counts[guild_id] = self.command_counts.get(guild_id, 0) + 1
        
        # Store detailed command analytics
        try:
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO command_analytics 
                        (guild_id, command_name, user_id, success)
                        VALUES ($1, $2, $3, $4)
                    """, guild_id, ctx.command.name, str(ctx.author.id), True)
                    
                    # Update user activity
                    await conn.execute("""
                        INSERT INTO user_activity 
                        (guild_id, user_id, username, command_count)
                        VALUES ($1, $2, $3, 1)
                        ON CONFLICT (guild_id, user_id)
                        DO UPDATE SET 
                            command_count = user_activity.command_count + 1,
                            last_active = EXCLUDED.last_active,
                            username = EXCLUDED.username
                    """, guild_id, str(ctx.author.id), ctx.author.name)
                    
        except Exception as e:
            logger.error(f"Error storing command analytics: {e}")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Track failed command analytics"""
        if not ctx.guild:
            return
            
        try:
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO command_analytics 
                        (guild_id, command_name, user_id, success)
                        VALUES ($1, $2, $3, $4)
                    """, str(ctx.guild.id), getattr(ctx.command, 'name', 'unknown'), 
                         str(ctx.author.id), False)
                    
        except Exception as e:
            logger.error(f"Error storing failed command analytics: {e}")
    
    # Removed duplicate member join/leave handlers to prevent conflicts with main bot handlers

async def setup(bot):
    await bot.add_cog(AnalyticsTracker(bot))
    logger.info("Analytics Tracker initialized")