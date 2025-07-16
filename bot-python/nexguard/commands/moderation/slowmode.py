from discord.ext import commands
import discord

class SlowmodeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='slowmode')
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 5):
        """Set slowmode for the channel"""
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Slowmode set to {seconds} seconds.")

async def setup(bot):
    await bot.add_cog(SlowmodeCommand(bot))