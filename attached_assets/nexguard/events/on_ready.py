import discord
from discord.ext import commands, tasks
import json
import logging
import os
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class OnReadyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.changelog_path = "nexguard/changelog/log.json"
        self.current_guild_activity = None
        self.guild_activity_tracker = {}  # Track recent activity per guild
        
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.bot.user} has connected to Discord!')
        logger.info(f'Bot ID: {self.bot.user.id}')
        logger.info(f'Connected to {len(self.bot.guilds)} guilds')
        logger.info(f'Serving {len(self.bot.users)} users')
        
        # Ensure bot is set to online status
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for rule violations"
            ),
            status=discord.Status.online
        )
        
        # Then set bot status to most active guild or general activity
        most_active_guild = await self.get_most_active_guild()
        if most_active_guild:
            await self.update_activity_for_guild(most_active_guild)
        
        logger.info(f"Bot status set to ONLINE")
        
        # Post changelog if there are new updates
        await self.post_changelog()
        
        # Also post to configured changelog channels
        await self.post_auto_changelog()
        
        # Log bot statistics
        logger.info("Bot statistics:")
        logger.info(f"- Guilds: {len(self.bot.guilds)}")
        logger.info(f"- Users: {len(self.bot.users)}")
        logger.info(f"- Commands: {len(self.bot.commands)}")
        logger.info(f"- Cogs: {len(self.bot.cogs)}")
        
        # Check database connectivity
        try:
            import sqlite3
            conn = sqlite3.connect(self.bot.db_path)
            conn.close()
            logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
    
    async def get_default_prefix(self) -> str:
        """Get the default prefix"""
        return "!"
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Update activity when bot joins a guild"""
        logger.info(f"Bot joined guild: {guild.name}")
        await self.update_activity_for_guild(guild)
    
    @commands.Cog.listener() 
    async def on_guild_remove(self, guild):
        """Update activity when bot leaves a guild"""
        logger.info(f"Bot left guild: {guild.name}")
        # Reset to general activity
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for rule violations"
            ),
            status=discord.Status.online
        )
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        """Track interaction activity per guild"""
        if interaction.guild:
            # Update guild activity tracker
            import time
            self.guild_activity_tracker[interaction.guild.id] = time.time()
            
            # Update activity to show current active guild
            if self.current_guild_activity != interaction.guild.id:
                await self.update_activity_for_guild(interaction.guild)
                self.current_guild_activity = interaction.guild.id
    
    async def get_most_active_guild(self):
        """Get the most recently active guild"""
        if not self.guild_activity_tracker:
            return self.bot.guilds[0] if self.bot.guilds else None
        
        # Get the guild with most recent activity
        most_recent_guild_id = max(self.guild_activity_tracker.keys(), 
                                 key=lambda k: self.guild_activity_tracker[k])
        return self.bot.get_guild(most_recent_guild_id)
    
    async def update_activity_for_guild(self, guild):
        """Update bot activity to show defending specific guild"""
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"over {guild.name}"
            ),
            status=discord.Status.online
        )
        logger.info(f"Activity updated to: Defending {guild.name}")
    
    async def post_changelog(self):
        """Post changelog to designated channels"""
        try:
            if not os.path.exists(self.changelog_path):
                logger.info("No changelog file found, skipping changelog posting")
                return
            
            with open(self.changelog_path, 'r') as f:
                changelog_data = json.load(f)
            
            # Check if there are unposted updates
            unposted_updates = [update for update in changelog_data.get('updates', []) if not update.get('posted', False)]
            
            if not unposted_updates:
                logger.info("No new changelog updates to post")
                return
            
            logger.info(f"Found {len(unposted_updates)} unposted changelog updates")
            
            # Post to each guild's log channel
            for guild in self.bot.guilds:
                try:
                    # Get guild's log channel
                    import sqlite3
                    conn = sqlite3.connect(self.bot.db_path)
                    cursor = conn.cursor()
                    cursor.execute('SELECT log_channel FROM guild_settings WHERE guild_id = ?', (guild.id,))
                    result = cursor.fetchone()
                    conn.close()
                    
                    if not result or not result[0]:
                        continue
                    
                    log_channel = guild.get_channel(result[0])
                    if not log_channel:
                        continue
                    
                    # Post each unposted update
                    for update in unposted_updates:
                        embed = discord.Embed(
                            title="📋 NexGuard Update",
                            description=update.get('title', 'Bot Update'),
                            color=discord.Color.blue(),
                            timestamp=datetime.fromisoformat(update.get('date', datetime.utcnow().isoformat()))
                        )
                        
                        if update.get('description'):
                            embed.add_field(
                                name="Description",
                                value=update['description'],
                                inline=False
                            )
                        
                        if update.get('changes'):
                            changes_text = "\n".join([f"• {change}" for change in update['changes']])
                            embed.add_field(
                                name="Changes",
                                value=changes_text,
                                inline=False
                            )
                        
                        if update.get('fixes'):
                            fixes_text = "\n".join([f"• {fix}" for fix in update['fixes']])
                            embed.add_field(
                                name="Bug Fixes",
                                value=fixes_text,
                                inline=False
                            )
                        
                        embed.add_field(
                            name="Version",
                            value=update.get('version', 'Unknown'),
                            inline=True
                        )
                        
                        embed.set_footer(text="NexGuard Bot", icon_url=self.bot.user.display_avatar.url)
                        
                        try:
                            await log_channel.send(embed=embed)
                        except discord.Forbidden:
                            logger.warning(f"No permission to send changelog to {guild.name}")
                        except Exception as e:
                            logger.error(f"Error posting changelog to {guild.name}: {e}")
                
                except Exception as e:
                    logger.error(f"Error processing changelog for guild {guild.name}: {e}")
            
            # Mark updates as posted
            for update in unposted_updates:
                update['posted'] = True
            
            # Save updated changelog
            with open(self.changelog_path, 'w') as f:
                json.dump(changelog_data, f, indent=2)
            
            logger.info(f"Posted {len(unposted_updates)} changelog updates")
            
        except Exception as e:
            logger.error(f"Error posting changelog: {e}")
    
    async def post_auto_changelog(self):
        """Post changelog to configured channels"""
        import sqlite3
        
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            
            # Ensure changelog_config table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS changelog_config (
                    guild_id INTEGER PRIMARY KEY,
                    channel_id INTEGER NOT NULL,
                    enabled BOOLEAN DEFAULT TRUE,
                    last_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Get all guilds with changelog configuration
            cursor.execute('SELECT guild_id, channel_id FROM changelog_config WHERE enabled = TRUE')
            results = cursor.fetchall()
            conn.close()
            
            for guild_id, channel_id in results:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    continue
                    
                channel = guild.get_channel(channel_id)
                if not channel:
                    continue
                    
                # Get changelog cog and post changelog
                changelog_cog = self.bot.get_cog('ChangelogCog')
                if changelog_cog:
                    await changelog_cog.post_changelog(guild, channel)
                    logger.info(f"Posted auto-changelog to #{channel.name} in {guild.name}")
        except Exception as e:
            logger.error(f"Error posting auto-changelog: {e}")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild"""
        logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Initialize guild settings in database
        try:
            conn = self.bot.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)', (guild.id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Initialized settings for guild {guild.name}")
        except Exception as e:
            logger.error(f"Error initializing guild settings: {e}")
        
        # Update bot status
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.bot.guilds)} servers | Use {await self.get_default_prefix()}help"
            )
        )
        
        # Try to send welcome message to a suitable channel
        try:
            # Find a suitable channel to send welcome message
            channel = None
            
            # Try to find a general channel
            for ch in guild.text_channels:
                if ch.name.lower() in ['general', 'main', 'chat', 'lobby']:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
            
            # If no general channel found, use the first channel we can send to
            if not channel:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
            
            if channel:
                embed = discord.Embed(
                    title="👋 Hello! Thanks for adding NexGuard!",
                    description="I'm NexGuard, a comprehensive Discord moderation bot ready to help keep your server safe and organized.",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="🚀 Getting Started",
                    value=f"Use `{await self.get_default_prefix()}help` to see all available commands\n"
                          f"Use `{await self.get_default_prefix()}settings` to configure server settings",
                    inline=False
                )
                
                embed.add_field(
                    name="🔧 Quick Setup",
                    value=f"• Set a log channel: `{await self.get_default_prefix()}settings logchannel #channel`\n"
                          f"• Configure mute role: `{await self.get_default_prefix()}settings muterole @role`\n"
                          f"• Change prefix: `{await self.get_default_prefix()}prefix <new_prefix>`",
                    inline=False
                )
                
                embed.add_field(
                    name="📋 Key Features",
                    value="• Comprehensive moderation tools\n"
                          "• Automatic logging system\n"
                          "• Customizable permissions\n"
                          "• Member management\n"
                          "• Server utilities",
                    inline=False
                )
                
                embed.set_footer(text="Need help? Use the help command for detailed information")
                
                await channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error sending welcome message to {guild.name}: {e}")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Called when the bot leaves a guild"""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
        
        # Update bot status
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.bot.guilds)} servers | Use {await self.get_default_prefix()}help"
            )
        )
        
        # Note: We don't delete guild data immediately in case the bot is re-added
        # Guild data can be cleaned up with a periodic cleanup task
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description=f"You don't have the required permissions to use this command.\n"
                           f"Required: {', '.join(error.missing_permissions)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="❌ Bot Missing Permissions",
                description=f"I don't have the required permissions to execute this command.\n"
                           f"Required: {', '.join(error.missing_permissions)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏰ Command on Cooldown",
                description=f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Missing Required Argument",
                description=f"Missing required argument: `{error.param.name}`\n"
                           f"Use `{ctx.prefix}help {ctx.command.name}` for usage information.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Log unexpected errors
        logger.error(f"Unexpected error in command {ctx.command}: {error}", exc_info=True)
        
        embed = discord.Embed(
            title="❌ Unexpected Error",
            description="An unexpected error occurred while executing this command. "
                       "The error has been logged and will be investigated.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(OnReadyCog(bot))
