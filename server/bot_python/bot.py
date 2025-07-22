#!/usr/bin/env python3

import discord
from discord.ext import commands, tasks
import asyncio
import asyncpg
import os
import json
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NexGuardBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        self.db_pool = None
        self.bot_start_time = datetime.utcnow()
        
        # Set up OpenAI if API key is available
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            logger.info("🤖 OpenAI API key found - AI chatbot features enabled")
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        await self.setup_database()
        await self.load_extensions()
        
        # Start background tasks
        self.update_bot_status.start()
        
        # Sync commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def setup_database(self):
        """Setup database connection pool"""
        try:
            self.db_pool = await asyncpg.create_pool(
                os.getenv('DATABASE_URL'),
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool established")
        except Exception as e:
            logger.error(f"Failed to setup database: {e}")
    
    async def load_extensions(self):
        """Load all command extensions"""
        extensions = [
            'server.bot_python.commands.admin',
            'server.bot_python.commands.moderation', 
            'server.bot_python.commands.utility',
            'server.bot_python.commands.tickets',
            'server.bot_python.commands.embedhelp',
            'server.bot_python.commands.autoreply',
            'server.bot_python.commands.automod',
            'server.bot_python.commands.modrole',
            'server.bot_python.commands.analytics',
            'server.bot_python.commands.webhook',
            'server.bot_python.commands.chatbot'  # AI Chatbot system
        ]
        
        for extension in extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'✅ {self.user} is online!')
        logger.info(f'Bot ID: {self.user.id}')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # Set custom activity status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | /commands for help"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
        logger.info(f'🎯 Activity set: Watching {len(self.guilds)} servers')
        
        # Update bot status in database
        await self.update_status_in_db()
    
    async def on_guild_join(self, guild):
        """Called when bot joins a guild"""
        await self.handle_guild_join(guild)
    
    async def on_guild_remove(self, guild):
        """Called when bot leaves a guild"""
        await self.handle_guild_leave(guild)
    
    async def on_member_join(self, member):
        """Called when a member joins a guild"""
        logger.info(f"👋 Member join event triggered: {member.name} joined {member.guild.name}")
        
        # Track member join analytics
        try:
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    # Update server analytics with new join
                    await conn.execute("""
                        UPDATE server_analytics 
                        SET new_joins = new_joins + 1
                        WHERE guild_id = $1 
                        AND timestamp >= $2
                    """, str(member.guild.id), datetime.utcnow() - timedelta(hours=1))
        except Exception as e:
            logger.error(f"Error tracking member join: {e}")
        
        # Handle welcome and autorole in sequence (not parallel to avoid race conditions)
        await self.handle_welcome_message(member)
        await self.handle_auto_role(member)
    
    async def on_message(self, message):
        """Called when a message is sent"""
        # Ignore messages from bots
        if message.author.bot:
            return
        

        # Check AutoMod first (it may delete messages)
        automod_cog = self.get_cog('AutoModCog')
        if automod_cog:
            # If AutoMod takes action (deletes message), it returns True
            automod_action_taken = await automod_cog.on_message(message)
            if automod_action_taken:
                return  # Don't process further if message was deleted
        
        # Track message analytics for spam detection
        analytics_cog = self.get_cog('AnalyticsTracker')
        if analytics_cog:
            try:
                if not self.db_pool or message.author.bot:
                    pass
                else:
                    async with self.db_pool.acquire() as conn:
                        await conn.execute('''
                            INSERT INTO message_analytics (guild_id, user_id, channel_id, message_id, content_length, has_attachments, timestamp)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ''', 
                        str(message.guild.id) if message.guild else None,
                        str(message.author.id),
                        str(message.channel.id),
                        str(message.id),
                        len(message.content),
                        len(message.attachments) > 0,
                        datetime.utcnow()
                        )
            except Exception as e:
                logger.error(f"Error storing message analytics: {e}")
        
        # Check for auto-replies
        autoreply_cog = self.get_cog('AutoReply')
        if autoreply_cog:
            await autoreply_cog.process_auto_replies(message)
        
        # Process other commands
        await self.process_commands(message)
    

    async def handle_guild_join(self, guild):
        """Handle bot joining a guild"""
        # Send welcome message to the guild
        await self.send_guild_welcome_message(guild)
        
        if not self.db_pool:
            return
            
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO guilds (id, name, member_count, joined_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        member_count = EXCLUDED.member_count,
                        updated_at = EXCLUDED.updated_at
                """, str(guild.id), guild.name, guild.member_count, datetime.utcnow(), datetime.utcnow())
                
                logger.info(f"Registered guild: {guild.name} ({guild.id})")
        except Exception as e:
            logger.error(f"Failed to register guild: {e}")
    
    async def handle_guild_leave(self, guild):
        """Handle bot leaving a guild"""
        if not self.db_pool:
            return
            
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE guilds SET updated_at = $1 WHERE id = $2
                """, datetime.utcnow(), str(guild.id))
                
                logger.info(f"Updated guild leave: {guild.name} ({guild.id})")
        except Exception as e:
            logger.error(f"Failed to update guild leave: {e}")
    
    async def handle_welcome_message(self, member):
        """Handle welcome message for new members"""
        if not self.db_pool:
            return
        
        # Prevent duplicate welcome messages with a robust cooldown check
        cooldown_key = f"welcome_{member.guild.id}_{member.id}"
        if not hasattr(self, '_welcome_cooldowns'):
            self._welcome_cooldowns = {}
        
        # Check if already processed recently (more robust check)
        current_time = datetime.utcnow()
        if cooldown_key in self._welcome_cooldowns:
            time_diff = (current_time - self._welcome_cooldowns[cooldown_key]).total_seconds()
            logger.warning(f"🚫 DUPLICATE WELCOME PREVENTED for {member.name} in {member.guild.name} (blocked after {time_diff:.1f}s)")
            return
        
        # Add to cooldown immediately with timestamp
        self._welcome_cooldowns[cooldown_key] = current_time
        logger.info(f"🎉 Processing welcome message for {member.name} in {member.guild.name} (cooldown set)")
        
        try:
            async with self.db_pool.acquire() as conn:
                # Get comprehensive guild welcome settings
                settings = await conn.fetchrow("""
                    SELECT welcome_enabled, welcome_channel_id, welcome_message, welcome_embed,
                           welcome_embed_title, welcome_embed_description, welcome_embed_color,
                           welcome_embed_thumbnail, welcome_embed_footer
                    FROM guilds WHERE id = $1
                """, str(member.guild.id))
                
                if not settings or not settings['welcome_enabled']:
                    return
                
                # Try to get the configured channel first
                channel = None
                if settings['welcome_channel_id']:
                    try:
                        channel = self.get_channel(int(settings['welcome_channel_id']))
                        if channel and not channel.permissions_for(member.guild.me).send_messages:
                            channel = None  # No permission to send messages
                    except (ValueError, TypeError):
                        channel = None
                
                # Fallback to finding a suitable channel if configured channel doesn't work
                if not channel:
                    logger.warning(f"Configured welcome channel not accessible in {member.guild.name}, finding fallback")
                    
                    # Try system channel first
                    if member.guild.system_channel and member.guild.system_channel.permissions_for(member.guild.me).send_messages:
                        channel = member.guild.system_channel
                    else:
                        # Look for general, welcome, main, chat channels
                        for text_channel in member.guild.text_channels:
                            if text_channel.permissions_for(member.guild.me).send_messages:
                                if any(name in text_channel.name.lower() for name in ['general', 'welcome', 'main', 'chat', 'lobby']):
                                    channel = text_channel
                                    break
                        
                        # If still no channel, use first available text channel
                        if not channel:
                            for text_channel in member.guild.text_channels:
                                if text_channel.permissions_for(member.guild.me).send_messages:
                                    channel = text_channel
                                    break
                
                if not channel:
                    logger.error(f"No accessible text channel found for welcome message in {member.guild.name}")
                    return
                
                # Enhanced placeholders
                placeholders = {
                    '{user.mention}': member.mention,
                    '{user.name}': member.name,
                    '{user.display_name}': member.display_name,
                    '{user.id}': str(member.id),
                    '{guild.name}': member.guild.name,
                    '{guild.member_count}': str(member.guild.member_count),
                    '{member.count}': str(member.guild.member_count),
                    '{server}': member.guild.name,
                    '{user}': member.mention,
                    '{created_at}': discord.utils.format_dt(member.created_at, "R"),
                    '{joined_at}': discord.utils.format_dt(member.joined_at, "R") if member.joined_at else "Just now"
                }
                
                def replace_placeholders(text):
                    if not text:
                        return text
                    for placeholder, value in placeholders.items():
                        text = text.replace(placeholder, value)
                    return text
                
                if settings['welcome_embed']:
                    # Create enhanced welcome embed
                    embed_title = replace_placeholders(settings['welcome_embed_title'] or 'Welcome to {guild.name}!')
                    embed_description = replace_placeholders(settings['welcome_embed_description'] or 'Hello {user.mention}, welcome to **{guild.name}**! We\'re excited to have you here.')
                    embed_footer = replace_placeholders(settings['welcome_embed_footer'] or 'Member #{member.count}')
                    
                    # Parse color
                    try:
                        embed_color = settings['welcome_embed_color'] or '#00FFFF'
                        if embed_color.startswith('#'):
                            embed_color = embed_color[1:]
                        color_int = int(embed_color, 16)
                    except ValueError:
                        color_int = 0x00FFFF
                    
                    embed = discord.Embed(
                        title=embed_title,
                        description=embed_description,
                        color=color_int,
                        timestamp=datetime.utcnow()
                    )
                    
                    # Add thumbnail if enabled
                    if settings['welcome_embed_thumbnail']:
                        embed.set_thumbnail(url=member.display_avatar.url)
                    
                    # Add comprehensive fields
                    embed.add_field(name="📅 Account Created", value=discord.utils.format_dt(member.created_at, "R"), inline=True)
                    embed.add_field(name="🆔 User ID", value=f"`{member.id}`", inline=True)
                    embed.add_field(name="👥 Member Count", value=f"**{member.guild.member_count}**", inline=True)
                    
                    # Add server info
                    embed.add_field(name="🌟 Server Info", value=f"**{member.guild.name}** has been your home since {discord.utils.format_dt(member.guild.created_at, 'R')}", inline=False)
                    
                    # Add footer
                    embed.set_footer(text=embed_footer, icon_url=member.guild.icon.url if member.guild.icon else None)
                    
                    # Add welcome reactions
                    message = await channel.send(embed=embed)
                    try:
                        await message.add_reaction("👋")
                        await message.add_reaction("🎉")
                        await message.add_reaction("💫")
                    except:
                        pass  # Ignore reaction errors
                else:
                    # Send enhanced text message
                    welcome_message = replace_placeholders(settings['welcome_message'] or 'Welcome {user.mention} to {guild.name}! You are our #{member.count} member.')
                    
                    message = await channel.send(welcome_message)
                    try:
                        await message.add_reaction("👋")
                    except:
                        pass  # Ignore reaction errors
                
                logger.info(f"✅ Successfully sent welcome message for {member.name} in {member.guild.name} to #{channel.name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to send welcome message for {member.name} in {member.guild.name}: {e}")
            # Remove from cooldown if failed to allow retry
            if cooldown_key in self._welcome_cooldowns:
                del self._welcome_cooldowns[cooldown_key]
        finally:
            # Clean up old cooldowns (older than 2 minutes)
            if hasattr(self, '_welcome_cooldowns'):
                current_time = datetime.utcnow()
                to_remove = []
                for key, timestamp in self._welcome_cooldowns.items():
                    if (current_time - timestamp).total_seconds() > 120:  # 2 minutes
                        to_remove.append(key)
                
                for key in to_remove:
                    del self._welcome_cooldowns[key]
                    
                if to_remove:
                    logger.debug(f"🧹 Cleaned up {len(to_remove)} old welcome cooldowns")
    
    @tasks.loop(seconds=30)
    async def update_bot_status(self):
        """Update bot status every 30 seconds"""
        await self.update_status_in_db()
        
        # Update Discord activity status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | /commands for help"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
    
    async def update_status_in_db(self):
        """Update bot status in database"""
        if not self.db_pool:
            return
            
        try:
            # Calculate uptime
            uptime = datetime.utcnow() - self.bot_start_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE bot_status SET
                        is_online = $1,
                        guilds_count = $2,
                        users_count = $3,
                        uptime = $4,
                        updated_at = $5
                    WHERE id = 1
                """, True, len(self.guilds), sum(guild.member_count for guild in self.guilds), 
                uptime_str, datetime.utcnow())
                
                logger.info(f"📊 Bot status updated: Online=True, Guilds={len(self.guilds)}, Users={sum(guild.member_count for guild in self.guilds)}")
        except Exception as e:
            logger.error(f"Failed to update bot status: {e}")
    
    async def log_error(self, guild_id: int, error_title: str, error_message: str, command_context: str = None):
        """Log errors to the configured error log channel"""
        try:
            guild_config = await self.get_guild_config(str(guild_id))
            error_channel_id = guild_config.get('error_log_channel_id')
            error_logging_enabled = guild_config.get('error_logging_enabled', False)
            
            if not error_channel_id or not error_logging_enabled:
                return  # No error logging configured or disabled
            
            error_channel = self.get_channel(int(error_channel_id))
            if not error_channel:
                return  # Channel doesn't exist or bot can't access it
            
            # Create detailed error embed
            embed = discord.Embed(
                title=f"🚨 {error_title}",
                color=0xFF4444,
                timestamp=datetime.utcnow()
            )
            
            # Truncate error message if too long
            if len(error_message) > 1024:
                error_message = error_message[:1021] + "..."
            
            embed.add_field(
                name="Error Details",
                value=f"```\n{error_message}\n```",
                inline=False
            )
            
            if command_context:
                embed.add_field(
                    name="Context",
                    value=command_context,
                    inline=True
                )
            
            embed.add_field(
                name="Timestamp",
                value=f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
                inline=True
            )
            
            guild = self.get_guild(guild_id)
            if guild:
                embed.add_field(
                    name="Server",
                    value=f"{guild.name} (`{guild.id}`)",
                    inline=True
                )
            
            embed.add_field(
                name="Bot Status",
                value=f"Guilds: {len(self.guilds)}\nUsers: {sum(guild.member_count for guild in self.guilds)}",
                inline=True
            )
            
            embed.set_footer(
                text="NexGuard Error Logging System",
                icon_url=self.user.display_avatar.url if self.user else None
            )
            
            await error_channel.send(embed=embed)
            logger.info(f"📝 Error logged to #{error_channel.name} in {guild.name if guild else guild_id}")
            
        except Exception as log_error:
            logger.error(f"Failed to log error to channel: {log_error}")
    
    async def log_command_usage(self, interaction: discord.Interaction, command_name: str, parameters: dict = None, result: str = "Success"):
        """Log command usage to the guild's configured logging channel"""
        try:
            guild_config = await self.get_guild_config(str(interaction.guild.id))
            log_channel_id = guild_config.get('log_channel_id')
            
            if not log_channel_id:
                return  # No logging channel configured
            
            log_channel = self.get_channel(int(log_channel_id))
            if not log_channel:
                return  # Channel doesn't exist or bot can't access it
            
            # Create professional embed
            embed = discord.Embed(
                title="🔧 Command Executed",
                color=0x00FFFF,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="Command",
                value=f"`/{command_name}`",
                inline=True
            )
            
            embed.add_field(
                name="User",
                value=f"{interaction.user.mention}\n(`{interaction.user.id}`)",
                inline=True
            )
            
            embed.add_field(
                name="Channel",
                value=f"{interaction.channel.mention}\n(`{interaction.channel.id}`)",
                inline=True
            )
            
            if parameters:
                param_text = ""
                for key, value in parameters.items():
                    if len(str(value)) > 50:
                        value = str(value)[:47] + "..."
                    param_text += f"**{key}:** {value}\n"
                
                if param_text:
                    embed.add_field(
                        name="Parameters",
                        value=param_text[:1024],  # Discord field limit
                        inline=False
                    )
            
            embed.add_field(
                name="Result",
                value=result,
                inline=True
            )
            
            embed.set_footer(
                text=f"Guild: {interaction.guild.name}",
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None
            )
            
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            
            await log_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to log command usage: {e}")

    async def get_guild_config(self, guild_id: str) -> Dict[str, Any]:
        """Get guild configuration from database"""
        if not self.db_pool:
            return {}
            
        try:
            async with self.db_pool.acquire() as conn:
                config = await conn.fetchrow("""
                    SELECT * FROM guilds WHERE id = $1
                """, guild_id)
                
                if config:
                    return dict(config)
                else:
                    # Create default config
                    await conn.execute("""
                        INSERT INTO guilds (id, name, settings)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (id) DO NOTHING
                    """, guild_id, "Unknown", json.dumps({}))
                    return {}
        except Exception as e:
            logger.error(f"Failed to get guild config: {e}")
            return {}
    
    async def update_guild_config(self, guild_id: str, **kwargs):
        """Update guild configuration in database"""
        if not self.db_pool:
            return
            
        try:
            async with self.db_pool.acquire() as conn:
                # Build update query dynamically
                set_clauses = []
                values = []
                param_count = 1
                
                for key, value in kwargs.items():
                    set_clauses.append(f"{key} = ${param_count}")
                    values.append(value)
                    param_count += 1
                
                set_clauses.append(f"updated_at = ${param_count}")
                values.append(datetime.utcnow())
                values.append(guild_id)
                
                query = f"""
                    UPDATE guilds SET {', '.join(set_clauses)}
                    WHERE id = ${param_count + 1}
                """
                
                await conn.execute(query, *values)
                logger.info(f"Updated guild config for {guild_id}: {kwargs}")
                
                # Verify the update worked
                updated_config = await conn.fetchrow("SELECT * FROM guilds WHERE id = $1", guild_id)
                if updated_config:
                    logger.info(f"Verified config update - Current values: {dict(updated_config)}")
        except Exception as e:
            logger.error(f"Failed to update guild config: {e}")
    
    async def send_guild_welcome_message(self, guild):
        """Send welcome message when bot joins a new guild"""
        try:
            # Find a suitable channel to send the welcome message
            target_channel = None
            
            # Try to find the system channel first
            if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
                target_channel = guild.system_channel
            else:
                # Look for a general channel
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        if any(name in channel.name.lower() for name in ['general', 'main', 'chat', 'welcome', 'lobby']):
                            target_channel = channel
                            break
                
                # If no general channel found, use the first available text channel
                if not target_channel:
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            target_channel = channel
                            break
            
            if not target_channel:
                logger.warning(f"No suitable channel found to send welcome message in {guild.name}")
                return
            
            # Create welcome embed
            embed = discord.Embed(
                title="🛡️ NexGuard Has Joined Your Server!",
                description=f"Thank you for adding **NexGuard** to **{guild.name}**! I'm here to help you manage and protect your Discord server with advanced moderation tools.",
                color=0x00FFFF,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="🚀 Quick Start",
                value="• Use `/commands` to see all 41+ slash commands\n• Try `/help` for detailed command information\n• Use `/config` to customize server settings",
                inline=False
            )
            
            embed.add_field(
                name="🔧 Key Features",
                value="• **Advanced Moderation** - Warn, mute, kick, ban with temporary options\n• **Smart AutoMod** - Spam detection, link filtering, bad word blocking\n• **Ticket System** - Multi-category support ticket management\n• **Auto-Reply** - Custom triggered responses with rich embeds",
                inline=False
            )
            
            embed.add_field(
                name="📊 Additional Tools",
                value="• **Analytics Dashboard** - Real-time server insights\n• **Welcome System** - Customizable member greetings\n• **Role Management** - Custom moderator permissions\n• **Comprehensive Logging** - Detailed action tracking",
                inline=False
            )
            
            embed.add_field(
                name="💡 Getting Help",
                value="• Visit our website for full documentation\n• Use `/support` to get assistance\n• Join our support server for community help",
                inline=False
            )
            
            embed.set_footer(
                text=f"NexGuard v2.3.2 | Now protecting {len(self.guilds)} servers | Enterprise-grade Discord protection", 
                icon_url=self.user.display_avatar.url
            )
            embed.set_thumbnail(url=self.user.display_avatar.url)
            
            # Send the welcome message
            message = await target_channel.send(embed=embed)
            
            # Add reaction to show bot is active
            try:
                await message.add_reaction("🛡️")
                await message.add_reaction("✅")
            except:
                pass  # Ignore reaction errors
            
            logger.info(f"✅ Welcome message sent to {guild.name} in #{target_channel.name}")
            
        except Exception as e:
            logger.error(f"Failed to send guild welcome message to {guild.name}: {e}")

    async def handle_auto_role(self, member):
        """Handle automatic role assignment for new members"""
        if not self.db_pool:
            return
            
        try:
            guild_id = str(member.guild.id)
            config = await self.get_guild_config(guild_id)
            
            # Check if auto-role is enabled and configured
            if not config.get('auto_role_enabled', False):
                return
            
            role_id = config.get('auto_role_id')
            if not role_id:
                return
            
            # Get the role object
            role = member.guild.get_role(int(role_id))
            if not role:
                logger.warning(f"Auto-role {role_id} not found in guild {member.guild.name}")
                return
            
            # Check if bot can assign the role
            if role.position >= member.guild.me.top_role.position:
                logger.warning(f"Cannot assign auto-role {role.name} - role hierarchy issue in {member.guild.name}")
                return
            
            # Check if the member already has the role
            if role in member.roles:
                return
            
            # Assign the role
            await member.add_roles(role, reason="Auto-role assignment")
            
            # Log the action
            logger.info(f"Assigned auto-role {role.name} to {member.name} in {member.guild.name}")
            
            # Log to command logging channel if configured
            log_channel_id = config.get('log_channel_id')
            if log_channel_id:
                log_channel = self.get_channel(int(log_channel_id))
                if log_channel:
                    embed = discord.Embed(
                        title="🎭 Auto-Role Assigned",
                        description=f"Automatically assigned role to new member",
                        color=0x00FF00,
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Member", value=f"{member.mention} ({member.name})", inline=True)
                    embed.add_field(name="Role", value=role.mention, inline=True)
                    embed.add_field(name="Member ID", value=str(member.id), inline=True)
                    embed.set_footer(text="NexGuard Auto-Role System")
                    embed.set_thumbnail(url=member.display_avatar.url)
                    
                    try:
                        await log_channel.send(embed=embed)
                    except Exception as e:
                        logger.error(f"Failed to send auto-role log: {e}")
            
        except Exception as e:
            logger.error(f"Error assigning auto-role to {member.name}: {e}")

    async def close(self):
        """Cleanup when bot shuts down"""
        if self.db_pool:
            await self.db_pool.close()
        await super().close()

# Global bot instance
bot = NexGuardBot()

async def main():
    """Main entry point"""
    discord_token = os.getenv('DISCORD_TOKEN')
    if not discord_token:
        logger.error("DISCORD_TOKEN environment variable not set")
        return
    
    try:
        await bot.start(discord_token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())