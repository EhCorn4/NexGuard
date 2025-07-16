from discord.ext import commands
import discord

class MuteCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='mute')
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Mute a member in the server"""
        await member.timeout(None, reason=reason)
        await ctx.send(f"{member.mention} has been muted. Reason: {reason}")

async def setup(bot):
    await bot.add_cog(MuteCommand(bot))