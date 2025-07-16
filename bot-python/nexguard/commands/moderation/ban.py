from discord.ext import commands
import discord

class BanCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a member from the server"""
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned. Reason: {reason}")

async def setup(bot):
    await bot.add_cog(BanCommand(bot))