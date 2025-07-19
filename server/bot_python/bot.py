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
            'server.bot_python.commands.analytics'
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
        await self.handle_welcome_message(member)
    
    async def on_message(self, message):
        """Called when a message is sent"""
        # Ignore messages from bots
        if message.author.bot:
            return
        
        # Check if bot is mentioned
        if self.user in message.mentions:
            logger.info(f"🔥 Bot mentioned by {message.author.name} - showing enhanced bio")
            latency = round(self.latency * 1000)
            
            embed = discord.Embed(
                title="🛡️ NexGuard - Advanced Discord Moderation",
                description=f"Hey {message.author.mention}! I'm **NexGuard**, your comprehensive server protection and management solution.\n\n🌐 **Currently protecting {len(self.guilds)} servers with {sum(guild.member_count for guild in self.guilds)} users**\n⚡ **Response time: {latency}ms**",
                color=0x00FFFF,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="🔧 Core Features",
                value="• **Advanced Moderation** - Warn, mute, kick, ban with temporary options\n• **Smart AutoMod** - Spam detection, link filtering, bad word blocking\n• **Ticket System** - Multi-category support with priority management\n• **Auto-Reply** - Custom triggered responses with rich embeds",
                inline=False
            )
            
            embed.add_field(
                name="📊 Management Tools",
                value="• **Analytics Dashboard** - Real-time server insights\n• **Welcome System** - Customizable member greetings\n• **Role Management** - Custom moderator permissions\n• **Logging** - Comprehensive action tracking",
                inline=False
            )
            
            embed.add_field(
                name="🚀 Get Started",
                value="Use `/commands` to explore **41+ slash commands**\nVisit our website for full documentation and setup guides",
                inline=False
            )
            
            embed.set_footer(text=f"NexGuard v2.3.2 | Enterprise-grade Discord protection | Requested by {message.author.name}", icon_url=message.author.display_avatar.url)
            embed.set_thumbnail(url=self.user.display_avatar.url)
            
            await message.reply(embed=embed)
            return
        
        # Only process auto-replies and other commands if bot wasn't mentioned
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
            
        try:
            async with self.db_pool.acquire() as conn:
                # Get comprehensive guild welcome settings
                settings = await conn.fetchrow("""
                    SELECT welcome_enabled, welcome_channel_id, welcome_message, welcome_embed,
                           welcome_embed_title, welcome_embed_description, welcome_embed_color,
                           welcome_embed_thumbnail, welcome_embed_footer
                    FROM guilds WHERE id = $1
                """, str(member.guild.id))
                
                if not settings or not settings['welcome_enabled'] or not settings['welcome_channel_id']:
                    return
                
                channel = self.get_channel(int(settings['welcome_channel_id']))
                if not channel:
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
                
                logger.info(f"Sent enhanced welcome message for {member.name} in {member.guild.name}")
                
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")
    
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
                logger.info(f"Updated guild config for {guild_id}")
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