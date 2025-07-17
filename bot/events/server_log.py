import discord
from discord.ext import commands
import sqlite3
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ServerLogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Log channel creation"""
        await self.log_channel_event(channel.guild, "Channel Created", f"#{channel.name}", 
                                    f"**{channel.mention}** was created.", discord.Color.green())
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Log channel deletion"""
        await self.log_channel_event(channel.guild, "Channel Deleted", f"#{channel.name}",
                                    f"**#{channel.name}** was deleted.", discord.Color.red())
    
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        """Log channel updates"""
        if before.name != after.name:
            await self.log_channel_event(after.guild, "Channel Renamed", f"#{after.name}",
                                       f"**{after.mention}** was renamed from **#{before.name}** to **#{after.name}**.",
                                       discord.Color.orange())
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """Log role creation"""
        await self.log_role_event(role.guild, "Role Created", role.name,
                                f"**{role.mention}** was created.", discord.Color.green())
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Log role deletion"""
        await self.log_role_event(role.guild, "Role Deleted", role.name,
                                f"**@{role.name}** was deleted.", discord.Color.red())
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        """Log role updates"""
        if before.name != after.name:
            await self.log_role_event(after.guild, "Role Renamed", after.name,
                                    f"**{after.mention}** was renamed from **@{before.name}** to **@{after.name}**.",
                                    discord.Color.orange())
    
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        """Log server updates"""
        changes = []
        
        if before.name != after.name:
            changes.append(f"**Name:** {before.name} → {after.name}")
        
        if before.icon != after.icon:
            changes.append("**Icon:** Changed")
        
        if before.banner != after.banner:
            changes.append("**Banner:** Changed")
        
        if before.verification_level != after.verification_level:
            changes.append(f"**Verification Level:** {before.verification_level} → {after.verification_level}")
        
        if changes:
            await self.log_server_event(after, "Server Updated", "\n".join(changes), discord.Color.orange())
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Log voice activity"""
        # Check if voice logging is enabled
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT log_channel, voice_logs FROM guild_settings WHERE guild_id = ?', (member.guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0] or not result[1]:
            return
        
        log_channel = member.guild.get_channel(result[0])
        if not log_channel:
            return
        
        # Determine what happened
        if before.channel is None and after.channel is not None:
            # User joined a voice channel
            embed = discord.Embed(
                title="🎙️ Voice Channel Joined",
                description=f"**{member}** joined {after.channel.mention}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
        elif before.channel is not None and after.channel is None:
            # User left a voice channel
            embed = discord.Embed(
                title="🎙️ Voice Channel Left",
                description=f"**{member}** left {before.channel.mention}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
        elif before.channel != after.channel:
            # User moved between voice channels
            embed = discord.Embed(
                title="🎙️ Voice Channel Moved",
                description=f"**{member}** moved from {before.channel.mention} to {after.channel.mention}",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
        else:
            # Other voice state changes (mute, deafen, etc.) - skip for now
            return
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"User ID: {member.id}")
        
        try:
            await log_channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(f"Cannot send voice log in {member.guild.name}: Missing permissions")
    
    async def log_channel_event(self, guild, event_title, channel_name, description, color):
        """Log channel events"""
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT log_channel, channel_logs FROM guild_settings WHERE guild_id = ?', (guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0] or not result[1]:
            return
        
        log_channel = guild.get_channel(result[0])
        if not log_channel:
            return
        
        embed = discord.Embed(
            title=f"📁 {event_title}",
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Channel",
            value=channel_name,
            inline=True
        )
        
        try:
            await log_channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(f"Cannot send channel log in {guild.name}: Missing permissions")
    
    async def log_role_event(self, guild, event_title, role_name, description, color):
        """Log role events"""
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT log_channel, role_logs FROM guild_settings WHERE guild_id = ?', (guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0] or not result[1]:
            return
        
        log_channel = guild.get_channel(result[0])
        if not log_channel:
            return
        
        embed = discord.Embed(
            title=f"🎭 {event_title}",
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Role",
            value=role_name,
            inline=True
        )
        
        try:
            await log_channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(f"Cannot send role log in {guild.name}: Missing permissions")
    
    async def log_server_event(self, guild, event_title, description, color):
        """Log server events"""
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT log_channel, server_logs FROM guild_settings WHERE guild_id = ?', (guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0] or not result[1]:
            return
        
        log_channel = guild.get_channel(result[0])
        if not log_channel:
            return
        
        embed = discord.Embed(
            title=f"🏠 {event_title}",
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        try:
            await log_channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(f"Cannot send server log in {guild.name}: Missing permissions")

async def setup(bot):
    await bot.add_cog(ServerLogCog(bot))