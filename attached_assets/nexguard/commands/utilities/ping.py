import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='ping', description='Check the bot\'s latency and connection status')
    async def ping(self, interaction: discord.Interaction):
        """Check the bot's latency"""
        start_time = datetime.utcnow()
        
        # Calculate latency
        latency = round(self.bot.latency * 1000)
        
        # Create embed with bot status
        embed = discord.Embed(
            title="🏓 Pong!",
            description="Bot latency and connection information",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🌐 WebSocket Latency",
            value=f"`{latency}ms`",
            inline=True
        )
        
        embed.add_field(
            name="📊 Status",
            value="✅ Online",
            inline=True
        )
        
        embed.add_field(
            name="🔗 Guilds",
            value=f"`{len(self.bot.guilds)}`",
            inline=True
        )
        
        embed.add_field(
            name="👥 Users",
            value=f"`{len(self.bot.users)}`",
            inline=True
        )
        
        embed.add_field(
            name="📝 Commands",
            value=f"`{len(self.bot.commands)}`",
            inline=True
        )
        
        embed.add_field(
            name="🧩 Cogs",
            value=f"`{len(self.bot.cogs)}`",
            inline=True
        )
        
        # Calculate uptime
        uptime = datetime.utcnow() - self.bot.start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        embed.add_field(
            name="⏱️ Uptime",
            value=f"`{uptime_str}`",
            inline=False
        )
        
        embed.set_footer(text=f"Requested by {interaction.user}")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
        
        # Calculate response time
        end_time = datetime.utcnow()
        response_time = int((end_time - start_time).total_seconds() * 1000)
        
        logger.info(f"Ping command executed - Latency: {latency}ms, Response: {response_time}ms")

async def setup(bot):
    await bot.add_cog(PingCog(bot))