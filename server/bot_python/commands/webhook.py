import discord
from discord.ext import commands
import json
import random
import asyncio
import logging
import aiohttp
from aiohttp import web

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
            add_reactions = data.get('add_reactions', False)
            
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
            logger.info(f"🎭 Webhook message sent to #{channel.name} in {channel.guild.name}")
            
            # Add reactions if requested
            if add_reactions:
                fun_reactions = ['😂', '🎉', '✨', '🔥', '💀', '😎', '🤡', '🎪', '🎭', '🚀']
                # Add 1-3 random reactions
                for _ in range(random.randint(1, 3)):
                    reaction = random.choice(fun_reactions)
                    try:
                        await message.add_reaction(reaction)
                        await asyncio.sleep(0.5)  # Small delay between reactions
                    except discord.HTTPException:
                        pass  # Ignore reaction errors
            
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

    @commands.command(name='webhook-test', hidden=True)
    @commands.has_permissions(administrator=True)
    async def webhook_test(self, ctx, *, message: str = "Test webhook message! 🎭"):
        """Test the webhook functionality"""
        try:
            # Send a test message using the webhook system
            test_data = {
                'channel_id': str(ctx.channel.id),
                'content': f"{message} {{funny}}",
                'add_reactions': True
            }
            
            # Simulate webhook call
            async with aiohttp.ClientSession() as session:
                async with session.post('http://localhost:5001/api/bot/send-message', 
                                      json=test_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        embed = discord.Embed(
                            title="✅ Webhook Test Successful",
                            description=f"Message sent via webhook system!\nMessage ID: {result.get('message_id')}",
                            color=0x00ff00
                        )
                        await ctx.send(embed=embed)
                    else:
                        error = await response.text()
                        embed = discord.Embed(
                            title="❌ Webhook Test Failed",
                            description=f"Error: {error}",
                            color=0xff0000
                        )
                        await ctx.send(embed=embed)
                        
        except Exception as e:
            embed = discord.Embed(
                title="❌ Webhook Test Error",
                description=f"Error: {e}",
                color=0xff0000
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WebhookCog(bot))
    logger.info("Webhook system initialized")