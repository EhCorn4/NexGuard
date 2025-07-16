from discord.ext import commands
import discord

class KickCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member from the server"""
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked. Reason: {reason}")

async def setup(bot):
    await bot.add_cog(KickCommand(bot))