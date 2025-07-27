import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import asyncpg
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServerStatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stat_channels: Dict[int, Dict[str, Any]] = {}
        self.update_stats_task.start()
        
    async def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.update_stats_task.cancel()
    
    async def cog_load(self):
        """Load existing stat channels from database and clean up orphaned entries"""
        try:
            async with self.bot.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT guild_id, channel_id, stat_type, channel_name_format 
                    FROM server_stat_channels 
                    WHERE enabled = TRUE
                """)
                
                valid_channels = 0
                cleaned_channels = 0
                
                for row in rows:
                    guild_id = int(row['guild_id'])
                    channel_id = int(row['channel_id'])
                    
                    # Check if guild and channel actually exist
                    guild = self.bot.get_guild(guild_id)
                    if not guild:
                        logger.warning(f"Guild {guild_id} not found, disabling stat channel {row['stat_type']}")
                        await conn.execute("""
                            UPDATE server_stat_channels 
                            SET enabled = FALSE 
                            WHERE guild_id = $1 AND stat_type = $2
                        """, str(guild_id), row['stat_type'])
                        cleaned_channels += 1
                        continue
                    
                    channel = guild.get_channel(channel_id)
                    if not channel:
                        logger.warning(f"Channel {channel_id} not found in {guild.name}, disabling stat channel {row['stat_type']}")
                        await conn.execute("""
                            UPDATE server_stat_channels 
                            SET enabled = FALSE 
                            WHERE guild_id = $1 AND stat_type = $2
                        """, str(guild_id), row['stat_type'])
                        cleaned_channels += 1
                        continue
                    
                    # Channel exists, add to cache
                    if guild_id not in self.stat_channels:
                        self.stat_channels[guild_id] = {}
                    
                    self.stat_channels[guild_id][row['stat_type']] = {
                        'channel_id': channel_id,
                        'format': row['channel_name_format']
                    }
                    valid_channels += 1
                    
                logger.info(f"Loaded {valid_channels} valid stat channels, cleaned {cleaned_channels} orphaned entries across {len(self.stat_channels)} guilds")
        except Exception as e:
            logger.error(f"Error loading stat channels: {e}")

    @app_commands.command(name="serverstats", description="Configure live server statistics channels")
    @app_commands.describe(
        action="Action to perform (setup, remove, list, force-update, cleanup)",
        stat_type="Type of statistic (members, humans, bots, channels, roles, online)",
        channel_name="Custom name format (use {count} for the number, e.g., 'Members: {count}')"
    )
    async def serverstats(self, interaction: discord.Interaction, 
                         action: str,
                         stat_type: Optional[str] = None, 
                         channel_name: Optional[str] = None):
        """Configure live server statistics channels"""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
            
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You need Manage Channels permission to use this command.", ephemeral=True)
            return
            
        guild = interaction.guild
        
        action = action.lower()
        
        if action == "setup":
            if not stat_type or not channel_name:
                await interaction.response.send_message("❌ For setup, you need to provide both stat_type and channel_name.", ephemeral=True)
                return
                
            await self.setup_stat_channel(interaction, stat_type.lower(), channel_name)
            
        elif action == "remove":
            if not stat_type:
                await interaction.response.send_message("❌ For remove, you need to specify the stat_type.", ephemeral=True)
                return
                
            await self.remove_stat_channel(interaction, stat_type.lower())
            
        elif action == "list":
            await self.list_stat_channels(interaction)
            
        elif action == "force-update":
            await self.force_update_stats(interaction)
            
        elif action == "cleanup":
            await self.cleanup_stat_channels(interaction)
            
        else:
            embed = discord.Embed(
                title="📊 Server Stats Channel Configuration",
                description="Configure live server statistics channels that update automatically.",
                color=0x00FFFF,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="Available Actions",
                value="`setup` - Create a new stat channel\n`remove` - Remove a stat channel\n`list` - List all stat channels\n`force-update` - Force immediate update of all stat channels\n`cleanup` - Clean up duplicate/orphaned stat channels",
                inline=False
            )
            
            embed.add_field(
                name="Available Statistics",
                value="`members` - Total member count\n`humans` - Human members only\n`bots` - Bot count\n`channels` - Total channels\n`roles` - Role count\n`online` - Online members",
                inline=False
            )
            
            embed.add_field(
                name="Example Usage",
                value="`/serverstats setup members \"👥 Members: {count}\"`\n`/serverstats setup bots \"🤖 Bots: {count}\"`\n`/serverstats remove members`",
                inline=False
            )
            
            embed.set_footer(text="NexGuard Server Statistics", icon_url=interaction.user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)

    async def setup_stat_channel(self, interaction: discord.Interaction, stat_type: str, channel_name: str):
        """Set up a new statistics channel"""
        valid_stats = ['members', 'humans', 'bots', 'channels', 'roles', 'online']
        
        if stat_type not in valid_stats:
            await interaction.response.send_message(f"❌ Invalid stat type. Choose from: {', '.join(valid_stats)}", ephemeral=True)
            return
        
        if '{count}' not in channel_name:
            await interaction.response.send_message("❌ Channel name must contain `{count}` placeholder for the statistic.", ephemeral=True)
            return
        
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
        
        # Check if a stat channel of this type already exists
        if guild.id in self.stat_channels and stat_type in self.stat_channels[guild.id]:
            existing_channel_id = self.stat_channels[guild.id][stat_type]['channel_id']
            existing_channel = guild.get_channel(existing_channel_id)
            
            if existing_channel:
                await interaction.response.send_message(
                    f"❌ A statistics channel for `{stat_type}` already exists: {existing_channel.mention}\n"
                    f"Use `/serverstats remove {stat_type}` first if you want to replace it.",
                    ephemeral=True
                )
                return
            else:
                # Channel doesn't exist anymore, remove from cache
                del self.stat_channels[guild.id][stat_type]
                if not self.stat_channels[guild.id]:
                    del self.stat_channels[guild.id]
        
        try:
            # Create voice channel
            category = None
            # Try to find or create a "Server Stats" category
            for cat in guild.categories:
                if "stats" in cat.name.lower():
                    category = cat
                    break
            
            if not category:
                category = await guild.create_category_channel("📊 Server Statistics")
                
            # Calculate current stat value
            current_value = await self.get_stat_value(guild, stat_type)
            channel_display_name = channel_name.format(count=current_value)
            
            # Create the voice channel
            stat_channel = await guild.create_voice_channel(
                name=channel_display_name,
                category=category,
                user_limit=0  # No user limit for stat channels
            )
            
            # Set permissions so users can't join but can see
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True),
                guild.me: discord.PermissionOverwrite(connect=True, manage_channels=True)
            }
            await stat_channel.edit(overwrites=overwrites)
            
            # Store in database
            await self.store_stat_channel(guild.id, stat_channel.id, stat_type, channel_name)
            
            # Update local cache
            if guild.id not in self.stat_channels:
                self.stat_channels[guild.id] = {}
            
            self.stat_channels[guild.id][stat_type] = {
                'channel_id': stat_channel.id,
                'format': channel_name
            }
            
            embed = discord.Embed(
                title="✅ Statistics Channel Created",
                description=f"Created live statistics channel for **{stat_type}**",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Channel", value=stat_channel.mention, inline=True)
            embed.add_field(name="Current Value", value=f"{current_value:,}", inline=True)
            embed.add_field(name="Update Frequency", value="Every 5 minutes", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creating stat channel: {e}")
            await interaction.response.send_message(f"❌ Error creating statistics channel: {str(e)}", ephemeral=True)

    async def remove_stat_channel(self, interaction: discord.Interaction, stat_type: str):
        """Remove a statistics channel"""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
        
        if guild.id not in self.stat_channels or stat_type not in self.stat_channels[guild.id]:
            await interaction.response.send_message(f"❌ No statistics channel found for `{stat_type}`.", ephemeral=True)
            return
        
        try:
            channel_id = self.stat_channels[guild.id][stat_type]['channel_id']
            channel = guild.get_channel(channel_id)
            
            if channel:
                await channel.delete()
            
            # Remove from database
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    DELETE FROM server_stat_channels 
                    WHERE guild_id = $1 AND stat_type = $2
                """, str(guild.id), stat_type)
            
            # Remove from cache
            del self.stat_channels[guild.id][stat_type]
            if not self.stat_channels[guild.id]:
                del self.stat_channels[guild.id]
            
            embed = discord.Embed(
                title="✅ Statistics Channel Removed",
                description=f"Removed statistics channel for **{stat_type}**",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error removing stat channel: {e}")
            await interaction.response.send_message(f"❌ Error removing statistics channel: {str(e)}", ephemeral=True)

    async def list_stat_channels(self, interaction: discord.Interaction):
        """List all active statistics channels"""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
        
        if guild.id not in self.stat_channels or not self.stat_channels[guild.id]:
            await interaction.response.send_message("❌ No statistics channels configured for this server.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📊 Active Statistics Channels",
            description="Currently configured live statistics channels:",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        for stat_type, data in self.stat_channels[guild.id].items():
            channel = guild.get_channel(data['channel_id'])
            if channel:
                current_value = await self.get_stat_value(guild, stat_type)
                embed.add_field(
                    name=f"{stat_type.title()} Statistics",
                    value=f"**Channel:** {channel.mention}\n**Current Value:** {current_value:,}\n**Format:** `{data['format']}`",
                    inline=True
                )
        
        embed.set_footer(text="Updates every 5 minutes", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    async def force_update_stats(self, interaction: discord.Interaction):
        """Force immediate update of all statistics channels"""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
        
        if guild.id not in self.stat_channels or not self.stat_channels[guild.id]:
            await interaction.response.send_message("❌ No statistics channels configured for this server.", ephemeral=True)
            return

        await interaction.response.defer()
        
        updated_count = 0
        errors = []
        
        try:
            stats = self.stat_channels[guild.id]
            
            for stat_type, data in stats.items():
                try:
                    channel = guild.get_channel(data['channel_id'])
                    if not channel:
                        errors.append(f"Channel for {stat_type} not found")
                        continue
                    
                    current_value = await self.get_stat_value(guild, stat_type)
                    new_name = data['format'].format(count=current_value)
                    
                    # Force update regardless of current name
                    await channel.edit(name=new_name)
                    updated_count += 1
                    logger.info(f"🔄 Force updated {stat_type} channel: {new_name}")
                    
                except Exception as e:
                    errors.append(f"Error updating {stat_type}: {str(e)}")
                    logger.error(f"Error force updating {stat_type}: {e}")
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error during force update: {str(e)}", ephemeral=True)
            return
        
        # Create response embed
        embed = discord.Embed(
            title="🔄 Force Update Complete",
            color=0x00FF00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Channels Updated", value=str(updated_count), inline=True)
        
        if errors:
            embed.add_field(name="Errors", value='\n'.join(errors[:5]), inline=False)
            embed.color = 0xFFAA00
            
        embed.set_footer(text="Next automatic update in 5 minutes")
        
        await interaction.followup.send(embed=embed)

    async def cleanup_stat_channels(self, interaction: discord.Interaction):
        """Clean up duplicate and orphaned stat channels"""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return

        await interaction.response.defer()
        
        try:
            # Get all stat channels from database for this guild
            async with self.bot.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT channel_id, stat_type 
                    FROM server_stat_channels 
                    WHERE guild_id = $1 AND enabled = TRUE
                """, str(guild.id))
            
            cleaned_count = 0
            active_count = 0
            errors = []
            
            # Check each channel
            for row in rows:
                try:
                    channel_id = int(row['channel_id'])
                    channel = guild.get_channel(channel_id)
                    
                    if not channel:
                        # Channel doesn't exist, disable in database
                        async with self.bot.db_pool.acquire() as conn:
                            await conn.execute("""
                                UPDATE server_stat_channels 
                                SET enabled = FALSE 
                                WHERE guild_id = $1 AND channel_id = $2
                            """, str(guild.id), str(channel_id))
                        
                        # Remove from cache
                        if guild.id in self.stat_channels and row['stat_type'] in self.stat_channels[guild.id]:
                            del self.stat_channels[guild.id][row['stat_type']]
                            
                        cleaned_count += 1
                        logger.info(f"🧹 Cleaned up orphaned {row['stat_type']} channel: {channel_id}")
                    else:
                        active_count += 1
                        
                except Exception as e:
                    errors.append(f"Error checking {row['stat_type']}: {str(e)}")
            
            # Create response embed
            embed = discord.Embed(
                title="🧹 Cleanup Complete",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Active Channels", value=str(active_count), inline=True)
            embed.add_field(name="Cleaned Up", value=str(cleaned_count), inline=True)
            
            if errors:
                embed.add_field(name="Errors", value='\n'.join(errors[:3]), inline=False)
                embed.color = 0xFFAA00
                
            embed.set_footer(text="Use /serverstats list to see active channels")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error during cleanup: {str(e)}", ephemeral=True)

    async def get_stat_value(self, guild: discord.Guild, stat_type: str) -> int:
        """Get the current value for a statistic type"""
        if stat_type == "members":
            return guild.member_count or 0
        elif stat_type == "humans":
            return sum(1 for member in guild.members if not member.bot)
        elif stat_type == "bots":
            return sum(1 for member in guild.members if member.bot)
        elif stat_type == "channels":
            return len(guild.channels)
        elif stat_type == "roles":
            return len(guild.roles)
        elif stat_type == "online":
            return sum(1 for member in guild.members if member.status != discord.Status.offline)
        else:
            return 0

    async def store_stat_channel(self, guild_id: int, channel_id: int, stat_type: str, channel_name_format: str):
        """Store stat channel configuration in database"""
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO server_stat_channels (guild_id, channel_id, stat_type, channel_name_format, enabled, created_at)
                    VALUES ($1, $2, $3, $4, TRUE, NOW())
                    ON CONFLICT (guild_id, stat_type) 
                    DO UPDATE SET 
                        channel_id = $2,
                        channel_name_format = $4,
                        enabled = TRUE,
                        updated_at = NOW()
                """, str(guild_id), str(channel_id), stat_type, channel_name_format)
        except Exception as e:
            logger.error(f"Error storing stat channel: {e}")

    @tasks.loop(minutes=5)
    async def update_stats_task(self):
        """Update all statistics channels every 5 minutes"""
        logger.info(f"🔄 Server stats update task running - checking {len(self.stat_channels)} guilds")
        try:
            for guild_id, stats in self.stat_channels.items():
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    logger.warning(f"Guild {guild_id} not found, skipping stat updates")
                    continue
                
                logger.info(f"📊 Updating {len(stats)} stat channels for guild {guild.name}")
                
                for stat_type, data in stats.items():
                    try:
                        channel = guild.get_channel(data['channel_id'])
                        if not channel:
                            continue
                        
                        current_value = await self.get_stat_value(guild, stat_type)
                        new_name = data['format'].format(count=current_value)
                        
                        # Only update if name changed (to avoid rate limits)
                        if channel.name != new_name:
                            await channel.edit(name=new_name)
                            logger.info(f"✅ Updated {stat_type} channel in {guild.name}: {new_name}")
                        else:
                            logger.debug(f"📌 {stat_type} channel already up to date: {channel.name}")
                        
                    except Exception as e:
                        logger.error(f"Error updating stat channel {stat_type} in guild {guild_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error in update_stats_task: {e}")

    @update_stats_task.before_loop
    async def before_update_stats_task(self):
        """Wait for bot to be ready before starting the update task"""
        await self.bot.wait_until_ready()
        # Load existing channels after bot is ready
        await self.cog_load()

async def setup(bot):
    # Create database table if it doesn't exist
    try:
        async with bot.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS server_stat_channels (
                    id SERIAL PRIMARY KEY,
                    guild_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    stat_type TEXT NOT NULL,
                    channel_name_format TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(guild_id, stat_type)
                )
            """)
    except Exception as e:
        logger.error(f"Error creating server_stat_channels table: {e}")
    
    await bot.add_cog(ServerStatsCog(bot))