from discord.ext import commands
import discord

class PingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check the bot's latency"""
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')

async def setup(bot):
    await bot.add_cog(PingCommand(bot))