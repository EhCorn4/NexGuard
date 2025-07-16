from discord.ext import commands
import discord

class WarnCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='warn')
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Warn a member"""
        await ctx.send(f"{member.mention} has been warned. Reason: {reason}")

async def setup(bot):
    await bot.add_cog(WarnCommand(bot))