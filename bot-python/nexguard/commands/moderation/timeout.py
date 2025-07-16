from discord.ext import commands
import discord
from datetime import datetime, timedelta

class TimeoutCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='timeout')
    @commands.has_permissions(manage_messages=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int = 10, *, reason="No reason provided"):
        """Timeout a member for specified minutes"""
        duration = timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        await ctx.send(f"{member.mention} has been timed out for {minutes} minutes. Reason: {reason}")

async def setup(bot):
    await bot.add_cog(TimeoutCommand(bot))