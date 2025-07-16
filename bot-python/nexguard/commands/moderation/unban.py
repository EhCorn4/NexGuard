from discord.ext import commands
import discord

class UnbanCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        """Unban a user from the server"""
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"{user.mention} has been unbanned.")

async def setup(bot):
    await bot.add_cog(UnbanCommand(bot))