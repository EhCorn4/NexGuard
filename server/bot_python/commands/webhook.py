import discord
from discord.ext import commands
import json
import random
import asyncio
import logging
import aiohttp
from aiohttp import web
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WebhookCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_server = None
        self.app = None
        
    async def cog_load(self):
        """Start webhook server when cog loads"""
        await self.start_webhook_server()
        
    async def cog_unload(self):
        """Stop webhook server when cog unloads"""
        if self.webhook_server:
            await self.webhook_server.close()
            
    async def start_webhook_server(self):
        """Start internal webhook server for receiving messages"""
        try:
            self.app = web.Application()
            self.app.router.add_post('/api/bot/send-message', self.handle_webhook_message)
            self.app.router.add_post('/api/bot/create-stats-embed', self.handle_create_stats_embed)
            
            # Start server on port 5001 (different from main Express server)
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, 'localhost', 5001)
            await site.start()
            logger.info("🎭 Webhook server started on http://localhost:5001")
            
        except Exception as e:
            logger.error(f"Failed to start webhook server: {e}")
    
    async def handle_webhook_message(self, request):
        """Handle incoming webhook message requests"""
        try:
            data = await request.json()
            channel_id = data.get('channel_id')
            content = data.get('content')
            embed_data = data.get('embed')
            
            # Get the Discord channel
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                return web.json_response({'error': 'Channel not found'}, status=404)
            
            # Check if bot has permission to send messages
            if not channel.permissions_for(channel.guild.me).send_messages:
                return web.json_response({'error': 'No permission to send messages'}, status=403)
            
            # Build message components
            message_kwargs = {}
            
            if content:
                message_kwargs['content'] = content
            
            if embed_data:
                embed = discord.Embed()
                if embed_data.get('title'):
                    embed.title = embed_data['title']
                if embed_data.get('description'):
                    embed.description = embed_data['description']
                if embed_data.get('color'):
                    # Handle color as hex string or integer
                    color = embed_data['color']
                    if isinstance(color, str):
                        if color.startswith('#'):
                            color = int(color[1:], 16)
                        elif color.startswith('0x'):
                            color = int(color, 16)
                        else:
                            # Try to parse as named color
                            color_map = {
                                'red': 0xff0000, 'green': 0x00ff00, 'blue': 0x0000ff,
                                'yellow': 0xffff00, 'purple': 0x800080, 'orange': 0xffa500,
                                'pink': 0xffc0cb, 'cyan': 0x00ffff, 'magenta': 0xff00ff
                            }
                            color = color_map.get(color.lower(), 0x5865F2)
                    embed.color = color
                message_kwargs['embed'] = embed
            
            # Send the message
            message = await channel.send(**message_kwargs)
            logger.info(f"Webhook message sent to #{channel.name} in {channel.guild.name}")
            
            return web.json_response({
                'success': True,
                'message_id': str(message.id),
                'channel': channel.name,
                'guild': channel.guild.name
            })
            
        except json.JSONDecodeError:
            return web.json_response({'error': 'Invalid JSON'}, status=400)
        except ValueError as e:
            return web.json_response({'error': f'Invalid channel ID: {e}'}, status=400)
        except discord.HTTPException as e:
            return web.json_response({'error': f'Discord error: {e}'}, status=500)
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    async def handle_create_stats_embed(self, request):
        """Handle creating a live stats embed"""
        try:
            data = await request.json()
            channel_id = data.get('channel_id')
            
            if not channel_id:
                return web.json_response({'error': 'channel_id is required'}, status=400)
            
            # Get the Discord channel
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                return web.json_response({'error': 'Channel not found'}, status=404)
            
            # Check if bot has permission to send messages
            if not channel.permissions_for(channel.guild.me).send_messages:
                return web.json_response({'error': 'No permission to send messages'}, status=403)
            
            # Create the stats embed
            embed = await self.create_stats_embed()
            
            # Send the embed
            message = await channel.send(embed=embed)
            logger.info(f"Stats embed created in #{channel.name} in {channel.guild.name}")
            
            # Store embed info for future updates (in memory for now)
            if not hasattr(self, 'stats_embeds'):
                self.stats_embeds = {}
            
            self.stats_embeds[channel_id] = {
                'channel_id': channel_id,
                'message_id': message.id,
                'guild_id': channel.guild.id
            }
            
            # Start the update task if not already running
            if not hasattr(self, 'update_task_started'):
                self.update_task_started = True
                asyncio.create_task(self.update_stats_embeds_loop())
            
            return web.json_response({
                'success': True,
                'message_id': str(message.id),
                'channel': channel.name,
                'guild': channel.guild.name,
                'embed_title': embed.title
            })
            
        except json.JSONDecodeError:
            return web.json_response({'error': 'Invalid JSON'}, status=400)
        except ValueError as e:
            return web.json_response({'error': f'Invalid channel ID: {e}'}, status=400)
        except discord.HTTPException as e:
            return web.json_response({'error': f'Discord error: {e}'}, status=500)
        except Exception as e:
            logger.error(f"Stats embed creation error: {e}")
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    async def create_stats_embed(self) -> discord.Embed:
        """Create the bot statistics embed"""
        try:
            from datetime import datetime, timedelta
            
            # Calculate uptime (since bot start)
            current_time = datetime.utcnow()
            uptime = current_time - getattr(self.bot, 'bot_start_time', current_time)
            uptime_str = self.format_uptime(uptime)
            
            # Get bot statistics
            total_guilds = len(self.bot.guilds)
            total_users = sum(guild.member_count for guild in self.bot.guilds if guild.member_count)
            
            # Get command count from synced commands
            synced_commands = len(await self.bot.tree.fetch_commands()) if hasattr(self.bot, 'tree') else 61
            
            # Create embed
            embed = discord.Embed(
                title="🤖 NexGuard Bot Statistics",
                description="Live bot performance and usage statistics",
                color=0x00FFFF,  # Cyan color
                timestamp=current_time
            )
            
            # Bot Status Field
            embed.add_field(
                name="🟢 Bot Status", 
                value="**Online** • Ready",
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
            latency_ms = round(self.bot.latency * 1000, 1) if self.bot.latency else 0
            embed.add_field(
                name="📡 Latency",
                value=f"**{latency_ms}ms**",
                inline=True
            )
            
            # Available Commands
            embed.add_field(
                name="⚙️ Commands",
                value=f"**{synced_commands}+** slash commands",
                inline=True
            )
            
            # Version
            embed.add_field(
                name="🔧 Version",
                value="**v2.5.1**",
                inline=True
            )
            
            # Memory usage (if available)
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                embed.add_field(
                    name="🧠 Memory",
                    value=f"**{memory_mb:.1f}MB**",
                    inline=True
                )
            except ImportError:
                embed.add_field(
                    name="💾 System",
                    value="**Optimized**",
                    inline=True
                )
            
            # Footer
            embed.set_footer(
                text="NexGuard • Updates every minute",
                icon_url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None
            )
            
            return embed
            
        except Exception as e:
            logger.error(f"Error creating stats embed: {e}")
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
    
    async def update_stats_embeds_loop(self):
        """Update all stats embeds every minute"""
        await self.bot.wait_until_ready()
        
        while True:
            try:
                await asyncio.sleep(60)  # Wait 1 minute
                
                if not hasattr(self, 'stats_embeds') or not self.stats_embeds:
                    continue
                
                embed = await self.create_stats_embed()
                
                for channel_id, embed_data in list(self.stats_embeds.items()):
                    try:
                        channel = self.bot.get_channel(int(channel_id))
                        if not channel:
                            # Channel no longer exists, remove from cache
                            del self.stats_embeds[channel_id]
                            continue
                        
                        # Try to fetch and update the message
                        try:
                            message = await channel.fetch_message(embed_data['message_id'])
                            await message.edit(embed=embed)
                            logger.info(f"Updated stats embed in #{channel.name}")
                        except discord.NotFound:
                            # Message was deleted, create a new one
                            new_message = await channel.send(embed=embed)
                            self.stats_embeds[channel_id]['message_id'] = new_message.id
                            logger.info(f"Recreated stats embed in #{channel.name}")
                        except discord.Forbidden:
                            logger.warning(f"No permission to update stats embed in #{channel.name}")
                        
                    except Exception as e:
                        logger.error(f"Error updating stats embed in channel {channel_id}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in stats embed update loop: {e}")
                await asyncio.sleep(60)  # Continue trying after error

    @discord.app_commands.command(name="stats-embed", description="Create a live bot statistics embed that updates every minute")
    @discord.app_commands.describe(action="Create or remove the stats embed")
    async def stats_embed_command(self, interaction: discord.Interaction, action: str = "create"):
        """Create or manage a live bot statistics embed"""
        
        # Check permissions
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You need 'Manage Channels' permission to use this command.", ephemeral=True)
            return
        
        if action.lower() == "create":
            await self.create_stats_embed_command(interaction)
        elif action.lower() == "remove":
            await self.remove_stats_embed_command(interaction)
        else:
            await interaction.response.send_message("❌ Invalid action. Use `create` or `remove`.", ephemeral=True)
    
    async def create_stats_embed_command(self, interaction: discord.Interaction):
        """Create a new stats embed in the current channel"""
        try:
            channel = interaction.channel
            
            # Check if embed already exists in this channel
            if hasattr(self, 'stats_embeds') and str(channel.id) in self.stats_embeds:
                await interaction.response.send_message(
                    f"❌ A stats embed already exists in this channel. Remove it first with `/stats-embed remove`.",
                    ephemeral=True
                )
                return
            
            # Create the stats embed
            embed = await self.create_stats_embed()
            
            # Send the embed
            await interaction.response.send_message("✅ Creating live bot statistics embed...", ephemeral=True)
            message = await channel.send(embed=embed)
            
            # Store embed info for future updates
            if not hasattr(self, 'stats_embeds'):
                self.stats_embeds = {}
            
            self.stats_embeds[str(channel.id)] = {
                'channel_id': channel.id,
                'message_id': message.id,
                'guild_id': interaction.guild.id
            }
            
            # Start the update task if not already running
            if not hasattr(self, 'update_task_started'):
                self.update_task_started = True
                asyncio.create_task(self.update_stats_embeds_loop())
            
            success_embed = discord.Embed(
                title="✅ Bot Stats Embed Created",
                description=f"Live bot statistics embed created in {channel.mention}",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            success_embed.add_field(name="Update Frequency", value="Every 1 minute", inline=True)
            success_embed.add_field(name="Message ID", value=str(message.id), inline=True)
            
            await interaction.followup.send(embed=success_embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error creating stats embed: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Error creating stats embed: {str(e)}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Error creating stats embed: {str(e)}", ephemeral=True)
    
    async def remove_stats_embed_command(self, interaction: discord.Interaction):
        """Remove a stats embed from the current channel"""
        try:
            channel = interaction.channel
            
            if not hasattr(self, 'stats_embeds') or str(channel.id) not in self.stats_embeds:
                await interaction.response.send_message(
                    f"❌ No stats embed found in this channel.",
                    ephemeral=True
                )
                return
            
            embed_data = self.stats_embeds[str(channel.id)]
            
            # Try to delete the message
            try:
                if embed_data.get('message_id'):
                    message = await channel.fetch_message(embed_data['message_id'])
                    await message.delete()
            except discord.NotFound:
                pass  # Message already deleted
            except Exception as e:
                logger.warning(f"Could not delete stats embed message: {e}")
            
            # Remove from cache
            del self.stats_embeds[str(channel.id)]
            
            success_embed = discord.Embed(
                title="✅ Bot Stats Embed Removed",
                description=f"Removed stats embed from {channel.mention}",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error removing stats embed: {e}")
            await interaction.response.send_message(f"❌ Error removing stats embed: {str(e)}", ephemeral=True)

    @discord.app_commands.command(name="webhook-test", description="Test the webhook functionality")
    @discord.app_commands.describe(message="Message to send via webhook")
    async def webhook_test(self, interaction: discord.Interaction, message: str = "Test webhook message"):
        """Test the webhook functionality"""
        
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
            return
            
        # Always use your specific channel
        target_channel_id = "1332207898545229978"
        
        # Send immediate response to avoid timeout
        await interaction.response.send_message(f"Sending webhook test message to <#{target_channel_id}>...", ephemeral=True)
        
        try:
            # Use the Express webhook endpoint for consistency
            async with aiohttp.ClientSession() as session:
                async with session.post('http://localhost:5000/webhook/send', 
                                      json={
                                          'api_key': 'nexguard-fun-webhook',
                                          'channel_id': target_channel_id,
                                          'content': message
                                      }) as response:
                    if response.status == 200:
                        result = await response.json()
                        embed = discord.Embed(
                            title="Webhook Test Successful",
                            description=f"Message sent to <#{target_channel_id}>\nContent: {message}",
                            color=0x00ff00
                        )
                        await interaction.followup.send(embed=embed, ephemeral=True)
                    else:
                        error = await response.text()
                        embed = discord.Embed(
                            title="Webhook Test Failed",
                            description=f"Error: {error}",
                            color=0xff0000
                        )
                        await interaction.followup.send(embed=embed, ephemeral=True)
                        
        except Exception as e:
            embed = discord.Embed(
                title="Webhook Test Error",
                description=f"Error: {e}",
                color=0xff0000
            )
            try:
                await interaction.followup.send(embed=embed, ephemeral=True)
            except:
                # If followup fails, try editing original response
                pass

async def setup(bot):
    await bot.add_cog(WebhookCog(bot))
    logger.info("Webhook system initialized")