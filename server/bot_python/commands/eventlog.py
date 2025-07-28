#!/usr/bin/env python3

import discord
from discord.ext import commands
from datetime import datetime, timezone
import asyncio
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EventLogger(commands.Cog):
    """Comprehensive event logging system for advanced server monitoring"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("Event Logger system initialized")
    
    async def get_log_channel(self, guild_id: int, log_type: str = 'general') -> Optional[discord.TextChannel]:
        """Get the configured log channel for specific event types"""
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Check for specific log channel type first
                result = await conn.fetchrow(
                    f"SELECT {log_type}_log_channel_id FROM guild_settings WHERE guild_id = $1",
                    str(guild_id)
                )
                
                if not result:
                    # Fallback to general log channel
                    result = await conn.fetchrow(
                        "SELECT log_channel_id FROM guild_settings WHERE guild_id = $1",
                        str(guild_id)
                    )
                
                if result:
                    channel_id = result.get(f'{log_type}_log_channel_id') or result.get('log_channel_id')
                    if channel_id:
                        return self.bot.get_channel(channel_id)
                        
        except Exception as e:
            logger.error(f"Error getting log channel for {guild_id}: {e}")
        
        return None
    
    async def log_event(self, guild: discord.Guild, embed: discord.Embed, log_type: str = 'general'):
        """Send log embed to appropriate channel"""
        try:
            log_channel = await self.get_log_channel(guild.id, log_type)
            if log_channel:
                await log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error sending log to {guild.name}: {e}")
    
    def create_embed(self, title: str, description: str, color: discord.Color, user: Optional[discord.Member] = None) -> discord.Embed:
        """Create standardized log embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        
        if user:
            embed.set_author(
                name=f"{user.display_name} ({user.name})",
                icon_url=user.display_avatar.url
            )
            embed.add_field(name="User ID", value=f"`{user.id}`", inline=True)
        
        embed.set_footer(text="NexGuard Event Logger")
        return embed

    # === MEMBER EVENTS ===
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Log member joins with comprehensive information AND handle core functionality"""
        try:
            logger.info(f"🔔 EVENTLOG: Member join event triggered for {member.name} in {member.guild.name}")
            # Handle core bot functionality (analytics, welcome, autorole)
            await self.bot.handle_member_join_core(member)
            
            # Create and send event log
            embed = self.create_embed(
                title="Member Joined",
                description=f"{member.mention} has joined the server",
                color=discord.Color.green(),
                user=member
            )
            
            # Account information
            embed.add_field(
                name="Account Created",
                value=f"<t:{int(member.created_at.timestamp())}:R>",
                inline=True
            )
            embed.add_field(
                name="Member Count",
                value=f"{member.guild.member_count}",
                inline=True
            )
            
            # Check for suspicious accounts
            account_age = datetime.now(timezone.utc) - member.created_at
            if account_age.days < 7:
                embed.add_field(
                    name="⚠️ New Account Warning",
                    value=f"Account is only {account_age.days} days old",
                    inline=False
                )
            
            await self.log_event(member.guild, embed, 'member')
            
        except Exception as e:
            logger.error(f"Error logging member join: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Log member leaves with role and activity information"""
        try:
            embed = self.create_embed(
                title="Member Left",
                description=f"**{member.display_name}** ({member.name}) has left the server",
                color=discord.Color.red(),
                user=member
            )
            
            # Join information
            if member.joined_at:
                embed.add_field(
                    name="Joined Server",
                    value=f"<t:{int(member.joined_at.timestamp())}:R>",
                    inline=True
                )
            
            embed.add_field(
                name="Member Count",
                value=f"{member.guild.member_count}",
                inline=True
            )
            
            # Roles information (excluding @everyone)
            roles = [role.mention for role in member.roles[1:]]
            if roles:
                roles_text = ', '.join(roles) if len(roles) <= 5 else f"{', '.join(roles[:5])} and {len(roles) - 5} more"
                embed.add_field(
                    name=f"Roles ({len(roles)})",
                    value=roles_text,
                    inline=False
                )
            
            await self.log_event(member.guild, embed, 'member')
            
        except Exception as e:
            logger.error(f"Error logging member leave: {e}")
    
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Log member updates including nickname and role changes"""
        try:
            # Nickname changes
            if before.nick != after.nick:
                embed = self.create_embed(
                    title="Nickname Changed",
                    description=f"{after.mention}'s nickname was updated",
                    color=discord.Color.orange(),
                    user=after
                )
                
                embed.add_field(
                    name="Before",
                    value=before.nick or before.name,
                    inline=True
                )
                embed.add_field(
                    name="After", 
                    value=after.nick or after.name,
                    inline=True
                )
                
                await self.log_event(after.guild, embed, 'member')
            
            # Role changes
            if before.roles != after.roles:
                added_roles = set(after.roles) - set(before.roles)
                removed_roles = set(before.roles) - set(after.roles)
                
                if added_roles or removed_roles:
                    embed = self.create_embed(
                        title="Member Roles Updated",
                        description=f"{after.mention}'s roles were modified",
                        color=discord.Color.blue(),
                        user=after
                    )
                    
                    if added_roles:
                        embed.add_field(
                            name="✅ Roles Added",
                            value=', '.join([role.mention for role in added_roles]),
                            inline=False
                        )
                    
                    if removed_roles:
                        embed.add_field(
                            name="❌ Roles Removed", 
                            value=', '.join([role.mention for role in removed_roles]),
                            inline=False
                        )
                    
                    await self.log_event(after.guild, embed, 'member')
            
        except Exception as e:
            logger.error(f"Error logging member update: {e}")

    # === MESSAGE EVENTS ===
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Log message deletions with content and attachment info"""
        if message.author.bot or not message.guild:
            return
            
        try:
            embed = self.create_embed(
                title="Message Deleted",
                description=f"Message by {message.author.mention} was deleted in {message.channel.mention}",
                color=discord.Color.red(),
                user=message.author
            )
            
            # Message content (truncated if too long)
            content = message.content or "*No text content*"
            if len(content) > 1024:
                content = content[:1021] + "..."
            
            embed.add_field(
                name="Content",
                value=f"```{content}```",
                inline=False
            )
            
            embed.add_field(
                name="Channel",
                value=message.channel.mention,
                inline=True
            )
            embed.add_field(
                name="Message ID",
                value=f"`{message.id}`",
                inline=True
            )
            
            # Attachments
            if message.attachments:
                attachment_info = []
                for att in message.attachments:
                    attachment_info.append(f"[{att.filename}]({att.url})")
                
                embed.add_field(
                    name=f"Attachments ({len(message.attachments)})",
                    value='\n'.join(attachment_info),
                    inline=False
                )
            
            await self.log_event(message.guild, embed, 'message')
            
        except Exception as e:
            logger.error(f"Error logging message deletion: {e}")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Log message edits with before/after content"""
        if before.author.bot or not before.guild or before.content == after.content:
            return
            
        try:
            embed = self.create_embed(
                title="Message Edited",
                description=f"Message by {after.author.mention} was edited in {after.channel.mention}",
                color=discord.Color.yellow(),
                user=after.author
            )
            
            # Before content
            before_content = before.content or "*No text content*"
            if len(before_content) > 512:
                before_content = before_content[:509] + "..."
            
            embed.add_field(
                name="Before",
                value=f"```{before_content}```",
                inline=False
            )
            
            # After content
            after_content = after.content or "*No text content*"
            if len(after_content) > 512:
                after_content = after_content[:509] + "..."
            
            embed.add_field(
                name="After",
                value=f"```{after_content}```",
                inline=False
            )
            
            embed.add_field(
                name="Channel",
                value=after.channel.mention,
                inline=True
            )
            embed.add_field(
                name="Jump to Message",
                value=f"[Click Here]({after.jump_url})",
                inline=True
            )
            
            await self.log_event(after.guild, embed, 'message')
            
        except Exception as e:
            logger.error(f"Error logging message edit: {e}")

    # === VOICE EVENTS ===
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Log voice channel activity"""
        try:
            # Member joined voice channel
            if before.channel is None and after.channel is not None:
                embed = self.create_embed(
                    title="Voice Channel Joined",
                    description=f"{member.mention} joined voice channel",
                    color=discord.Color.green(),
                    user=member
                )
                embed.add_field(
                    name="Channel",
                    value=after.channel.mention,
                    inline=True
                )
                
                await self.log_event(member.guild, embed, 'voice')
            
            # Member left voice channel
            elif before.channel is not None and after.channel is None:
                embed = self.create_embed(
                    title="Voice Channel Left",
                    description=f"{member.mention} left voice channel",
                    color=discord.Color.red(),
                    user=member
                )
                embed.add_field(
                    name="Channel",
                    value=before.channel.mention,
                    inline=True
                )
                
                await self.log_event(member.guild, embed, 'voice')
            
            # Member moved between channels
            elif before.channel != after.channel and before.channel is not None and after.channel is not None:
                embed = self.create_embed(
                    title="Voice Channel Moved",
                    description=f"{member.mention} moved between voice channels",
                    color=discord.Color.blue(),
                    user=member
                )
                embed.add_field(
                    name="From",
                    value=before.channel.mention,
                    inline=True
                )
                embed.add_field(
                    name="To",
                    value=after.channel.mention,
                    inline=True
                )
                
                await self.log_event(member.guild, embed, 'voice')
            
        except Exception as e:
            logger.error(f"Error logging voice state update: {e}")

    # === CHANNEL EVENTS ===
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Log channel creation"""
        try:
            embed = discord.Embed(
                title="Channel Created",
                description=f"New channel {channel.mention} was created",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(name="Channel Type", value=str(channel.type).title(), inline=True)
            embed.add_field(name="Channel ID", value=f"`{channel.id}`", inline=True)
            
            if hasattr(channel, 'category') and channel.category:
                embed.add_field(name="Category", value=channel.category.name, inline=True)
            
            embed.set_footer(text="NexGuard Event Logger")
            await self.log_event(channel.guild, embed, 'channel')
            
        except Exception as e:
            logger.error(f"Error logging channel creation: {e}")
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Log channel deletion"""
        try:
            embed = discord.Embed(
                title="Channel Deleted",
                description=f"Channel **{channel.name}** was deleted",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(name="Channel Type", value=str(channel.type).title(), inline=True)
            embed.add_field(name="Channel ID", value=f"`{channel.id}`", inline=True)
            
            if hasattr(channel, 'category') and channel.category:
                embed.add_field(name="Category", value=channel.category.name, inline=True)
            
            embed.set_footer(text="NexGuard Event Logger")
            await self.log_event(channel.guild, embed, 'channel')
            
        except Exception as e:
            logger.error(f"Error logging channel deletion: {e}")

    # === ROLE EVENTS ===
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        """Log role creation"""
        try:
            embed = discord.Embed(
                title="Role Created",
                description=f"New role {role.mention} was created",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(name="Role Name", value=role.name, inline=True)
            embed.add_field(name="Role ID", value=f"`{role.id}`", inline=True)
            embed.add_field(name="Color", value=str(role.color), inline=True)
            embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
            embed.add_field(name="Hoisted", value="Yes" if role.hoist else "No", inline=True)
            
            embed.set_footer(text="NexGuard Event Logger")
            await self.log_event(role.guild, embed, 'role')
            
        except Exception as e:
            logger.error(f"Error logging role creation: {e}")
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        """Log role deletion"""
        try:
            embed = discord.Embed(
                title="Role Deleted",
                description=f"Role **{role.name}** was deleted",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(name="Role Name", value=role.name, inline=True)
            embed.add_field(name="Role ID", value=f"`{role.id}`", inline=True)
            embed.add_field(name="Color", value=str(role.color), inline=True)
            
            embed.set_footer(text="NexGuard Event Logger")
            await self.log_event(role.guild, embed, 'role')
            
        except Exception as e:
            logger.error(f"Error logging role deletion: {e}")

    # === BAN EVENTS ===
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """Log member bans"""
        try:
            # Get ban reason from audit log
            ban_reason = "No reason provided"
            ban_moderator = "Unknown"
            
            try:
                async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=5):
                    if entry.target.id == user.id:
                        ban_reason = entry.reason or "No reason provided"
                        ban_moderator = entry.user.mention
                        break
            except:
                pass
            
            embed = discord.Embed(
                title="Member Banned",
                description=f"**{user.display_name}** ({user.name}) was banned from the server",
                color=discord.Color.dark_red(),
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.set_author(name=f"{user.display_name} ({user.name})", icon_url=user.display_avatar.url)
            embed.add_field(name="User ID", value=f"`{user.id}`", inline=True)
            embed.add_field(name="Moderator", value=ban_moderator, inline=True)
            embed.add_field(name="Reason", value=ban_reason, inline=False)
            
            embed.set_footer(text="NexGuard Event Logger")
            await self.log_event(guild, embed, 'moderation')
            
        except Exception as e:
            logger.error(f"Error logging member ban: {e}")
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        """Log member unbans"""
        try:
            embed = discord.Embed(
                title="Member Unbanned",
                description=f"**{user.display_name}** ({user.name}) was unbanned",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.set_author(name=f"{user.display_name} ({user.name})", icon_url=user.display_avatar.url)
            embed.add_field(name="User ID", value=f"`{user.id}`", inline=True)
            
            embed.set_footer(text="NexGuard Event Logger")
            await self.log_event(guild, embed, 'moderation')
            
        except Exception as e:
            logger.error(f"Error logging member unban: {e}")

    # === ADMIN COMMANDS ===
    
    @discord.app_commands.command(name="eventlog", description="Configure event logging channels")
    @discord.app_commands.describe(
        action="Configure event logging settings",
        log_type="Type of events to log",
        channel="Channel to send logs to"
    )
    @discord.app_commands.choices(action=[
        discord.app_commands.Choice(name="Set Channel", value="set"),
        discord.app_commands.Choice(name="View Settings", value="view"),
        discord.app_commands.Choice(name="Clear Channel", value="clear")
    ])
    @discord.app_commands.choices(log_type=[
        discord.app_commands.Choice(name="General Logs", value="general"),
        discord.app_commands.Choice(name="Member Events", value="member"),
        discord.app_commands.Choice(name="Message Events", value="message"),
        discord.app_commands.Choice(name="Voice Events", value="voice"),
        discord.app_commands.Choice(name="Channel Events", value="channel"),
        discord.app_commands.Choice(name="Role Events", value="role"),
        discord.app_commands.Choice(name="Moderation Events", value="moderation")
    ])
    async def eventlog_command(
        self, 
        interaction: discord.Interaction, 
        action: str,
        log_type: str = "general",
        channel: discord.TextChannel = None
    ):
        """Configure comprehensive event logging"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need `Manage Server` permission to use this command.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            if action == "set":
                if not channel:
                    await interaction.followup.send(
                        "❌ Please specify a channel to set as the log channel.",
                        ephemeral=True
                    )
                    return
                
                # Update database with new log channel
                async with self.bot.db_pool.acquire() as conn:
                    await conn.execute(f"""
                        INSERT INTO guild_settings (guild_id, {log_type}_log_channel_id)
                        VALUES ($1, $2)
                        ON CONFLICT (guild_id) DO UPDATE SET
                        {log_type}_log_channel_id = EXCLUDED.{log_type}_log_channel_id
                    """, str(interaction.guild.id), channel.id)
                
                embed = discord.Embed(
                    title="Event Logging Configured",
                    description=f"✅ {log_type.title()} events will now be logged to {channel.mention}",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed)
            
            elif action == "view":
                # Get current settings
                async with self.bot.db_pool.acquire() as conn:
                    result = await conn.fetchrow(
                        """
                        SELECT 
                            general_log_channel_id,
                            member_log_channel_id,
                            message_log_channel_id,
                            voice_log_channel_id,
                            channel_log_channel_id,
                            role_log_channel_id,
                            moderation_log_channel_id,
                            log_channel_id
                        FROM guild_settings 
                        WHERE guild_id = $1
                        """,
                        str(interaction.guild.id)
                    )
                
                embed = discord.Embed(
                    title="Event Logging Settings",
                    description="Current logging channel configuration:",
                    color=discord.Color.blue()
                )
                
                log_types = [
                    ("General", "general_log_channel_id"),
                    ("Member Events", "member_log_channel_id"),
                    ("Message Events", "message_log_channel_id"),
                    ("Voice Events", "voice_log_channel_id"),
                    ("Channel Events", "channel_log_channel_id"),
                    ("Role Events", "role_log_channel_id"),
                    ("Moderation Events", "moderation_log_channel_id"),
                    ("Legacy Log Channel", "log_channel_id")
                ]
                
                for log_name, column_name in log_types:
                    if result and result[column_name]:
                        channel_obj = self.bot.get_channel(result[column_name])
                        channel_text = channel_obj.mention if channel_obj else "Channel not found"
                    else:
                        channel_text = "Not configured"
                    
                    embed.add_field(
                        name=log_name,
                        value=channel_text,
                        inline=True
                    )
                
                await interaction.followup.send(embed=embed)
            
            elif action == "clear":
                # Clear log channel
                async with self.bot.db_pool.acquire() as conn:
                    await conn.execute(f"""
                        UPDATE guild_settings 
                        SET {log_type}_log_channel_id = NULL
                        WHERE guild_id = $1
                    """, str(interaction.guild.id))
                
                embed = discord.Embed(
                    title="Event Logging Cleared",
                    description=f"✅ {log_type.title()} event logging has been disabled",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in eventlog command: {e}")
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )

    @discord.app_commands.command(name="logtest", description="Test event logging with a sample message")
    @discord.app_commands.describe(log_type="Type of log to test")
    @discord.app_commands.choices(log_type=[
        discord.app_commands.Choice(name="General", value="general"),
        discord.app_commands.Choice(name="Member", value="member"),
        discord.app_commands.Choice(name="Message", value="message"),
        discord.app_commands.Choice(name="Voice", value="voice"),
        discord.app_commands.Choice(name="Channel", value="channel"),
        discord.app_commands.Choice(name="Role", value="role"),
        discord.app_commands.Choice(name="Moderation", value="moderation")
    ])
    async def logtest_command(self, interaction: discord.Interaction, log_type: str = "general"):
        """Test event logging functionality"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need `Manage Server` permission to use this command.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            # Create test embed
            embed = self.create_embed(
                title=f"🧪 Event Log Test - {log_type.title()}",
                description=f"This is a test message for {log_type} event logging. If you can see this message, your {log_type} logging is working correctly!",
                color=discord.Color.purple(),
                user=interaction.user
            )
            
            embed.add_field(
                name="Test Information",
                value="This test was triggered by an administrator to verify logging functionality.",
                inline=False
            )
            
            # Send test log
            await self.log_event(interaction.guild, embed, log_type)
            
            await interaction.followup.send(
                f"✅ Test log sent! Check your {log_type} logging channel.",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error in logtest command: {e}")
            await interaction.followup.send(
                f"❌ An error occurred during testing: {str(e)}",
                ephemeral=True
            )

    # === GUILD AND MESSAGE EVENTS (to prevent duplication from bot.py) ===
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Handle guild join events and call core functionality"""
        try:
            # Handle core functionality first
            await self.bot.handle_guild_join_core(guild)
            
            # Then log the event
            embed = self.create_embed(
                title="Bot Added to Server",
                description=f"NexGuard has been added to **{guild.name}**",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Server Name", value=guild.name, inline=True)
            embed.add_field(name="Member Count", value=f"{guild.member_count:,}", inline=True)
            embed.add_field(name="Server ID", value=f"`{guild.id}`", inline=True)
            
            # Log to a general logging channel if available
            await self.log_event(guild, embed, 'general')
            
        except Exception as e:
            logger.error(f"Error handling guild join: {e}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Handle guild leave events and call core functionality"""
        try:
            # Handle core functionality first
            await self.bot.handle_guild_leave_core(guild)
            
            # Then log the event (though this won't be visible to the guild anymore)
            logger.info(f"Bot removed from guild: {guild.name} ({guild.id})")
            
        except Exception as e:
            logger.error(f"Error handling guild leave: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle message events and process through various systems"""
        # Ignore messages from bots
        if message.author.bot:
            return
            
        try:
            # Check AutoMod first (it may delete messages)
            automod_cog = self.bot.get_cog('AutoModCog')
            if automod_cog:
                # If AutoMod takes action (deletes message), it returns True
                automod_action_taken = await automod_cog.on_message(message)
                if automod_action_taken:
                    return  # Don't process further if message was deleted
            
            # Analytics are handled by the AnalyticsTracker cog's on_message listener
            
            # Check for auto-replies
            autoreply_cog = self.bot.get_cog('AutoReply')
            if autoreply_cog:
                await autoreply_cog.process_auto_replies(message)
            
            # Process other commands
            await self.bot.process_commands(message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")

async def setup(bot):
    await bot.add_cog(EventLogger(bot))