from discord.ext import commands
import discord

class LockCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='lock')
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        """Lock the channel"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("Channel has been locked.")

async def setup(bot):
    await bot.add_cog(LockCommand(bot))