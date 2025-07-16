#!/usr/bin/env python3
"""
Main entry point for NexGuard Discord Bot with HTTP health check server
"""

import asyncio
import threading
import os
import logging
from aiohttp import web
from nexguard.index import bot
from nexguard.utils.api_integration import api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexguard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint for deployment"""
    try:
        # Check if bot is connected and ready
        if bot.is_ready():
            # Create a simple HTML page with links to bot download
            html = f'''<!DOCTYPE html>
<html>
<head><title>NexGuard Bot</title></head>
<body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
    <h1>🛡️ NexGuard Discord Bot</h1>
    <p>Bot is running and connected to {len(bot.guilds)} guilds serving {len(bot.users)} users</p>
    <p><a href="/bot" style="background: #5865F2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Download Bot Package</a></p>
    <p><a href="/status">Bot Status (JSON)</a></p>
</body>
</html>'''
            return web.Response(text=html, content_type='text/html')
        else:
            return web.Response(text="NexGuard Discord Bot is starting...", status=200)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return web.Response(text="NexGuard Discord Bot is running (health check)", status=200)

async def status_endpoint(request):
    """Status endpoint with bot information"""
    if bot.is_ready():
        status = {
            "status": "online",
            "guilds": len(bot.guilds),
            "users": len(bot.users),
            "uptime": str(bot.uptime) if hasattr(bot, 'uptime') else "N/A"
        }
        return web.json_response(status)
    else:
        return web.json_response({"status": "starting"}, status=503)

async def download_page(request):
    """Download page for bot package"""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NexGuard Bot - Download</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; 
               background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 2rem; }
        .logo { text-align: center; font-size: 3rem; margin-bottom: 1rem; }
        .download-btn { display: block; width: 300px; margin: 2rem auto; padding: 1rem; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; text-decoration: none; border-radius: 10px; text-align: center; font-weight: bold; }
        .download-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .features { background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 2rem 0; }
        .features ul { list-style: none; padding: 0; }
        .features li { padding: 0.5rem 0; border-bottom: 1px solid #eee; }
        .features li:before { content: "✅ "; margin-right: 0.5rem; }
        .info { text-align: center; color: #666; margin: 1rem 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🛡️</div>
        <h1>NexGuard Discord Bot v2.0.0</h1>
        <p class="info">Complete bot package with all features, documentation, and setup files</p>
        
        <div class="features">
            <h3>Package Contents:</h3>
            <ul>
                <li>Complete bot source code with 50 slash commands</li>
                <li>AI-powered welcome system with OpenAI integration</li>
                <li>Advanced AutoMod with 5 detection types</li>
                <li>Comprehensive logging and ticket system</li>
                <li>Web dashboard for server management</li>
                <li>Production deployment configuration</li>
                <li>Complete documentation and setup guides</li>
            </ul>
        </div>
        
        <a href="/download" class="download-btn">📥 Download Bot Package (0.31 MB)</a>
        
        <p class="info">After download, run install.sh to get started</p>
    </div>
</body>
</html>'''
    return web.Response(text=html, content_type='text/html')

async def download_file(request):
    """Download the bot package"""
    zip_file = "nexguard-bot-v2.0.0-20250710.zip"
    if os.path.exists(zip_file):
        return web.FileResponse(zip_file, 
                               headers={'Content-Disposition': 'attachment; filename="nexguard-bot-v2.0.0.zip"'})
    else:
        return web.Response(text="Download file not found", status=404)

async def start_web_server():
    """Start the HTTP server for health checks"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', status_endpoint)
    app.router.add_get('/bot', download_page)
    app.router.add_get('/download', download_file)
    
    # Use PORT environment variable for deployment compatibility
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Attempting to start HTTP server on port {port}")
    
    # Ensure port is valid for deployment
    if port < 1000 or port > 65535:
        logger.warning(f"Port {port} may not be valid for deployment, using 5000")
        port = 5000
    
    try:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        logger.info(f"HTTP health check server started on 0.0.0.0:{port}")
        logger.info(f"Health endpoints available at:")
        logger.info(f"  - / (health check)")
        logger.info(f"  - /health (health check)")
        logger.info(f"  - /status (bot status)")
        logger.info(f"  - /bot (download page)")
        logger.info(f"  - /download (download file)")
        return runner
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
        raise

async def start_discord_bot():
    """Start the Discord bot"""
    try:
        token = os.getenv('DISCORD_TOKEN', '').strip()
        
        # Handle cases where token might have the format "DISCORD_TOKEN=actual_token"
        if '=' in token and token.startswith('DISCORD_TOKEN='):
            token = token.split('=', 1)[1].strip()
        
        if not token or token == 'your_bot_token_here':
            logger.error('No valid Discord token found. Please set the DISCORD_TOKEN environment variable.')
            return
        
        logger.info(f'Starting Discord bot with token length: {len(token)}')
        await bot.start(token)
    except Exception as e:
        logger.error(f'Failed to start Discord bot: {e}')

async def main():
    """Main function to start both HTTP server and Discord bot"""
    logger.info("Starting NexGuard Discord Bot with HTTP health check server...")
    
    web_runner = None
    try:
        # Start HTTP server
        web_runner = await start_web_server()
        
        # Create tasks for both HTTP server and Discord bot
        discord_task = asyncio.create_task(start_discord_bot())
        
        # Wait for Discord bot to connect or fail
        await discord_task
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        # Keep HTTP server running even if Discord bot fails
        if web_runner:
            logger.info("HTTP server will continue running for health checks")
            # Keep the process alive for health checks
            try:
                while True:
                    await asyncio.sleep(10)
            except KeyboardInterrupt:
                logger.info("Shutting down HTTP server...")
    finally:
        # Cleanup
        if web_runner:
            await web_runner.cleanup()
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")