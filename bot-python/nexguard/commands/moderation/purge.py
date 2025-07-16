from discord.ext import commands
import discord

class PurgeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='purge')
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 10):
        """Purge messages from the channel"""
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"Purged {amount} messages.", delete_after=5)

async def setup(bot):
    await bot.add_cog(PurgeCommand(bot))