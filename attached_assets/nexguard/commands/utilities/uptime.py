import discord
from discord.ext import commands
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UptimeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='uptime')
    async def uptime(self, ctx):
        """Check the bot's uptime"""
        try:
            current_time = datetime.utcnow()
            uptime_duration = current_time - self.bot.start_time
            
            # Calculate time components
            days = uptime_duration.days
            hours, remainder = divmod(uptime_duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # Format uptime string
            uptime_parts = []
            if days > 0:
                uptime_parts.append(f"{days} day{'s' if days != 1 else ''}")
            if hours > 0:
                uptime_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
            if minutes > 0:
                uptime_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
            if seconds > 0 or not uptime_parts:
                uptime_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
            
            uptime_string = ", ".join(uptime_parts)
            
            # Create embed
            embed = discord.Embed(
                title="⏰ Bot Uptime",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="Current Uptime",
                value=f"```{uptime_string}```",
                inline=False
            )
            
            embed.add_field(
                name="Started At",
                value=f"<t:{int(self.bot.start_time.timestamp())}:F>",
                inline=False
            )
            
            embed.add_field(
                name="Total Seconds",
                value=f"`{int(uptime_duration.total_seconds())}`",
                inline=True
            )
            
            # Add some statistics
            embed.add_field(
                name="Servers",
                value=f"`{len(self.bot.guilds)}`",
                inline=True
            )
            
            embed.add_field(
                name="Users",
                value=f"`{len(self.bot.users)}`",
                inline=True
            )
            
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred while checking uptime: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error(f"Error checking uptime: {e}")

async def setup(bot):
    await bot.add_cog(UptimeCog(bot))
