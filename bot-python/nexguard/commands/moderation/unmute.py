from discord.ext import commands
import discord

class UnmuteCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='unmute')
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmute a member in the server"""
        await member.timeout(None)
        await ctx.send(f"{member.mention} has been unmuted.")

async def setup(bot):
    await bot.add_cog(UnmuteCommand(bot))