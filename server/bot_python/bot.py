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
            'server.bot_python.commands.embedhelp'
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
            latency = round(self.latency * 1000)
            
            embed = discord.Embed(
                title="👋 Hello there!",
                description=f"Hey {message.author.mention}! I'm NexGuard, your server management assistant.\n\nMy latency is **{latency}ms**",
                color=0x00FFFF,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="💡 Quick Tip",
                value="Use `/help` to see all my commands!",
                inline=False
            )
            
            embed.set_footer(text=f"NexGuard v2.3.2 | Pinged by {message.author.name}", icon_url=message.author.display_avatar.url)
            
            await message.reply(embed=embed)
            return
        
        # Check if message contains "ping" (case insensitive)
        if "ping" in message.content.lower():
            latency = round(self.latency * 1000)
            
            responses = [
                f"🏓 Pong! {latency}ms",
                f"🏓 Pong! Latency: {latency}ms",
                f"🏓 Pong! I'm here with {latency}ms latency!",
                f"🏓 Pong! Ready to help with {latency}ms response time!"
            ]
            
            # Pick a random response
            response = random.choice(responses)
            
            await message.reply(response)
            return
        
        # Check for auto-replies
        await self.check_auto_replies(message)
        
        # Process other commands
        await self.process_commands(message)
    
    async def check_auto_replies(self, message):
        """Check for and process auto-replies"""
        if not self.db_pool or not message.guild:
            return
        
        try:
            guild_id = str(message.guild.id)
            
            async with self.db_pool.acquire() as conn:
                # Get all active auto-replies for this guild
                auto_replies = await conn.fetch(
                    "SELECT trigger, response, trigger_type, case_sensitive FROM auto_replies WHERE guild_id = $1 AND is_active = TRUE",
                    guild_id
                )
                
                if not auto_replies:
                    return
                
                message_content = message.content
                
                for reply in auto_replies:
                    trigger = reply['trigger']
                    response = reply['response']
                    trigger_type = reply['trigger_type']
                    case_sensitive = reply['case_sensitive']
                    
                    # Prepare text for comparison
                    if case_sensitive:
                        msg_text = message_content
                        trigger_text = trigger
                    else:
                        msg_text = message_content.lower()
                        trigger_text = trigger.lower()
                    
                    # Check if trigger matches based on type
                    matched = False
                    
                    if trigger_type == "contains":
                        matched = trigger_text in msg_text
                    elif trigger_type == "exact":
                        matched = msg_text.strip() == trigger_text
                    elif trigger_type == "starts_with":
                        matched = msg_text.startswith(trigger_text)
                    elif trigger_type == "ends_with":
                        matched = msg_text.endswith(trigger_text)
                    
                    if matched:
                        # Replace placeholders in response
                        response = response.replace('{user}', message.author.mention)
                        response = response.replace('{user.name}', message.author.name)
                        response = response.replace('{user.display_name}', message.author.display_name)
                        response = response.replace('{user.mention}', message.author.mention)
                        response = response.replace('{server}', message.guild.name)
                        response = response.replace('{guild.name}', message.guild.name)
                        response = response.replace('{channel}', message.channel.mention)
                        response = response.replace('{channel.name}', message.channel.name)
                        
                        # Send the auto-reply
                        await message.reply(response)
                        logger.info(f"Auto-reply triggered in {message.guild.name}: '{trigger}' -> '{response}'")
                        return  # Only respond to first match
                        
        except Exception as e:
            logger.error(f"Error checking auto-replies: {e}")
    
    async def handle_guild_join(self, guild):
        """Handle bot joining a guild"""
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