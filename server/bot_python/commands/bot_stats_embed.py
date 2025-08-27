#!/usr/bin/env python3

import discord
from discord.ext import commands, tasks
import asyncio
import json
import logging
import psutil
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BotStatsEmbedCog(commands.Cog):
    """A cog that creates and maintains live bot statistics embeds"""
    
    def __init__(self, bot):
        self.bot = bot
        self.stats_embeds = {}  # Dictionary to store embed channel configs
        self.startup_time = datetime.utcnow()
        
    async def cog_load(self):
        """Called when the cog is loaded"""
        # Start loading stats embeds without blocking
        asyncio.create_task(self.initialize_after_ready())
        logger.info("Bot Stats Embed system initialized")
        
    async def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.update_stats_embeds.cancel()
    
    async def initialize_after_ready(self):
        """Initialize stats embeds after bot is ready"""
        await self.bot.wait_until_ready()
        await self.load_stats_embeds()
        self.update_stats_embeds.start()
        
    async def load_stats_embeds(self):
        """Load existing stats embeds from database"""
        try:
            if not self.bot.db_pool:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                # Create table if it doesn't exist
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_stats_embeds (
                        id SERIAL PRIMARY KEY,
                        guild_id BIGINT NOT NULL,
                        channel_id BIGINT NOT NULL,
                        message_id BIGINT,
                        enabled BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(guild_id, channel_id)
                    )
                """)
                
                # Load existing embeds
                rows = await conn.fetch("SELECT * FROM bot_stats_embeds WHERE enabled = TRUE")
                for row in rows:
                    guild_id = int(row['guild_id'])
                    channel_id = int(row['channel_id'])
                    message_id = int(row['message_id']) if row['message_id'] else None
                    
                    self.stats_embeds[channel_id] = {
                        'guild_id': guild_id,
                        'channel_id': channel_id,
                        'message_id': message_id
                    }
                    
                logger.info(f"Loaded {len(self.stats_embeds)} bot stats embeds")
                
        except Exception as e:
            logger.error(f"Error loading stats embeds: {e}")
    
    @discord.app_commands.command(name="stats-embed")
    @discord.app_commands.describe(
        action="Create or remove the stats embed",
        channel="The channel to create the embed in (defaults to current channel)"
    )
    async def stats_embed(self, interaction: discord.Interaction, 
                         action: str, 
                         channel: Optional[discord.TextChannel] = None):
        """Create or manage a live bot statistics embed"""
        
        # Check permissions (works for both User and Member)
        member = interaction.guild.get_member(interaction.user.id) if interaction.guild else None
        if not member or not member.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You need 'Manage Channels' permission to use this command.", ephemeral=True)
            return
        
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
        
        target_channel = channel or interaction.channel
        
        # Ensure it's a text channel
        if not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message("❌ This command can only be used in text channels.", ephemeral=True)
            return
        
        if action.lower() == "create":
            await self.create_stats_embed(interaction, target_channel)
        elif action.lower() == "remove":
            await self.remove_stats_embed(interaction, target_channel)
        else:
            await interaction.response.send_message("❌ Invalid action. Use `create` or `remove`.", ephemeral=True)
    
    async def create_stats_embed(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Create a new stats embed in the specified channel"""
        try:
            # Check if embed already exists in this channel
            if channel.id in self.stats_embeds:
                await interaction.response.send_message(
                    f"❌ A stats embed already exists in {channel.mention}. Remove it first with `/stats-embed remove`.",
                    ephemeral=True
                )
                return
            
            # Create initial embed
            embed = await self.create_bot_stats_embed()
            
            # Send the embed
            message = await channel.send(embed=embed)
            
            # Store in database
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO bot_stats_embeds (guild_id, channel_id, message_id) 
                    VALUES ($1, $2, $3)
                    ON CONFLICT (guild_id, channel_id) 
                    DO UPDATE SET message_id = $3, enabled = TRUE
                """, interaction.guild.id, channel.id, message.id)
            
            # Update local cache
            self.stats_embeds[channel.id] = {
                'guild_id': interaction.guild.id,
                'channel_id': channel.id,
                'message_id': message.id
            }
            
            success_embed = discord.Embed(
                title="✅ Bot Stats Embed Created",
                description=f"Live bot statistics embed created in {channel.mention}",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            success_embed.add_field(name="Update Frequency", value="Every 1 minute", inline=True)
            success_embed.add_field(name="Message ID", value=str(message.id), inline=True)
            
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error creating stats embed: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Error creating stats embed: {str(e)}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Error creating stats embed: {str(e)}", ephemeral=True)
    
    async def remove_stats_embed(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Remove a stats embed from the specified channel"""
        try:
            if channel.id not in self.stats_embeds:
                await interaction.response.send_message(
                    f"❌ No stats embed found in {channel.mention}.",
                    ephemeral=True
                )
                return
            
            embed_data = self.stats_embeds[channel.id]
            
            # Try to delete the message
            try:
                if embed_data.get('message_id'):
                    message = await channel.fetch_message(embed_data['message_id'])
                    await message.delete()
            except discord.NotFound:
                pass  # Message already deleted
            except Exception as e:
                logger.warning(f"Could not delete stats embed message: {e}")
            
            # Remove from database
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    DELETE FROM bot_stats_embeds 
                    WHERE guild_id = $1 AND channel_id = $2
                """, interaction.guild.id, channel.id)
            
            # Remove from cache
            del self.stats_embeds[channel.id]
            
            success_embed = discord.Embed(
                title="✅ Bot Stats Embed Removed",
                description=f"Removed stats embed from {channel.mention}",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error removing stats embed: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Error removing stats embed: {str(e)}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Error removing stats embed: {str(e)}", ephemeral=True)
    
    async def create_bot_stats_embed(self) -> discord.Embed:
        """Create the bot statistics embed"""
        try:
            # Calculate uptime
            current_time = datetime.utcnow()
            uptime = current_time - self.startup_time
            uptime_str = self.format_uptime(uptime)
            
            # Get bot statistics
            total_guilds = len(self.bot.guilds)
            total_users = sum(guild.member_count for guild in self.bot.guilds if guild.member_count)
            
            # Get database stats if available
            commands_today = 0
            total_commands = 0
            try:
                if self.bot.db_pool:
                    async with self.bot.db_pool.acquire() as conn:
                        # Commands executed today
                        result = await conn.fetchval("""
                            SELECT COUNT(*) FROM command_logs 
                            WHERE DATE(timestamp) = CURRENT_DATE
                        """)
                        commands_today = result or 0
                        
                        # Total commands ever
                        result = await conn.fetchval("SELECT COUNT(*) FROM command_logs")
                        total_commands = result or 0
            except Exception as e:
                logger.debug(f"Could not fetch command stats: {e}")
            
            # Create embed
            embed = discord.Embed(
                title="🤖 NexGuard Bot Statistics",
                description="Live bot performance and usage statistics",
                color=0x00FFFF,
                timestamp=current_time
            )
            
            # Bot Status Field
            embed.add_field(
                name="🟢 Bot Status",
                value=f"**Online** • Ready",
                inline=True
            )
            
            # Server Statistics
            embed.add_field(
                name="🏰 Servers",
                value=f"**{total_guilds:,}** servers",
                inline=True
            )
            
            # User Statistics
            embed.add_field(
                name="👥 Users",
                value=f"**{total_users:,}** users",
                inline=True
            )
            
            # Uptime
            embed.add_field(
                name="⏰ Uptime",
                value=f"**{uptime_str}**",
                inline=True
            )
            

            
            # Latency
            latency_ms = round(self.bot.latency * 1000, 1)
            embed.add_field(
                name="📡 Latency",
                value=f"**{latency_ms}ms**",
                inline=True
            )
            
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            embed.add_field(
                name="🖥️ CPU Usage",
                value=f"**{cpu_percent:.1f}%**",
                inline=True
            )
            
            # Memory Usage
            memory = psutil.virtual_memory()
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            memory_percent = memory.percent
            embed.add_field(
                name="💾 Memory Usage",
                value=f"**{memory_used_gb:.1f}GB / {memory_total_gb:.1f}GB**\n({memory_percent:.1f}%)",
                inline=True
            )
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            disk_percent = (disk.used / disk.total) * 100
            embed.add_field(
                name="💽 Disk Usage",
                value=f"**{disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB**\n({disk_percent:.1f}%)",
                inline=True
            )
            
            # Version/Build
            embed.add_field(
                name="🔧 Version",
                value="**v2.5.1**",
                inline=True
            )
            
            # Available Commands
            embed.add_field(
                name="⚙️ Commands",
                value="**62** slash commands",
                inline=True
            )
            
            # Footer
            embed.set_footer(
                text="NexGuard • Updates every minute",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            
            return embed
            
        except Exception as e:
            logger.error(f"Error creating bot stats embed: {e}")
            # Return a simple error embed
            return discord.Embed(
                title="❌ Statistics Error",
                description="Unable to fetch current statistics",
                color=0xFF0000,
                timestamp=datetime.utcnow()
            )
    
    def format_uptime(self, uptime: timedelta) -> str:
        """Format uptime timedelta into a readable string"""
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    @tasks.loop(minutes=1)
    async def update_stats_embeds(self):
        """Update all active stats embeds every minute"""
        try:
            if not self.stats_embeds:
                return
            
            embed = await self.create_bot_stats_embed()
            
            for channel_id, embed_data in list(self.stats_embeds.items()):
                try:
                    guild = self.bot.get_guild(embed_data['guild_id'])
                    if not guild:
                        # Guild no longer exists, remove from cache
                        del self.stats_embeds[channel_id]
                        continue
                    
                    channel = guild.get_channel(embed_data['channel_id'])
                    if not channel:
                        # Channel no longer exists, remove from cache
                        del self.stats_embeds[channel_id]
                        continue
                    
                    # Try to fetch and update the message
                    if embed_data.get('message_id'):
                        try:
                            message = await channel.fetch_message(embed_data['message_id'])
                            await message.edit(embed=embed)
                        except discord.NotFound:
                            # Message was deleted, create a new one
                            new_message = await channel.send(embed=embed)
                            
                            # Update database with new message ID
                            async with self.bot.db_pool.acquire() as conn:
                                await conn.execute("""
                                    UPDATE bot_stats_embeds 
                                    SET message_id = $1 
                                    WHERE guild_id = $2 AND channel_id = $3
                                """, new_message.id, embed_data['guild_id'], channel_id)
                            
                            # Update cache
                            self.stats_embeds[channel_id]['message_id'] = new_message.id
                        except discord.Forbidden:
                            logger.warning(f"No permission to edit stats embed in {guild.name}")
                        except Exception as e:
                            logger.error(f"Error updating stats embed in {guild.name}: {e}")
                    
                except Exception as e:
                    logger.error(f"Error processing stats embed for channel {channel_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error in update_stats_embeds task: {e}")
    
    @update_stats_embeds.before_loop
    async def before_update_stats_embeds(self):
        """Wait for bot to be ready before starting the loop"""
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(BotStatsEmbedCog(bot))