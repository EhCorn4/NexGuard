import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime
import platform
import psutil
import os
from typing import Optional
from io import StringIO, BytesIO

logger = logging.getLogger(__name__)

def process_newlines(text: str) -> str:
    """Process newline characters in text for proper Discord embed display"""
    if not text:
        return text
    
    # Convert common newline representations to actual newlines
    result = text.replace('\\n', '\n')  # \n literal
    result = result.replace('\\r\\n', '\n')  # Windows line endings
    result = result.replace('\\r', '\n')  # Mac line endings
    result = result.replace('\r\n', '\n')  # Normalize Windows endings
    result = result.replace('\r', '\n')   # Normalize Mac endings
    
    return result

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        """Check the bot's latency"""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Log command usage
        await self.bot.log_command_usage(interaction, "ping")
    
    @app_commands.command(name="userinfo", description="Get information about a user")
    @app_commands.describe(user="The user to get information about")
    async def userinfo(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Get information about a user"""
        if user is None:
            if isinstance(interaction.user, discord.Member):
                user = interaction.user
            else:
                await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
                return
        
        embed = discord.Embed(
            title=f"👤 User Information - {user.name}",
            color=user.color if user.color != discord.Color.default() else 0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        
        embed.add_field(name="Username", value=user.name, inline=True)
        embed.add_field(name="Display Name", value=user.display_name, inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        
        embed.add_field(name="Bot", value="Yes" if user.bot else "No", inline=True)
        embed.add_field(name="Account Created", value=discord.utils.format_dt(user.created_at, "F"), inline=True)
        embed.add_field(name="Joined Server", value=discord.utils.format_dt(user.joined_at, "F") if user.joined_at else "Unknown", inline=True)
        
        roles = [role.mention for role in user.roles[1:]]  # Skip @everyone
        embed.add_field(name=f"Roles ({len(roles)})", value=" ".join(roles) if roles else "None", inline=False)
        
        embed.set_footer(text="User Information", icon_url=None)
        
        await interaction.response.send_message(embed=embed)
        
        # Log command usage
        parameters = {"user": user.mention if user != interaction.user else "self"}
        await self.bot.log_command_usage(interaction, "userinfo", parameters)
    
    @app_commands.command(name="serverinfo", description="View comprehensive server statistics")
    async def serverinfo(self, interaction: discord.Interaction):
        """Get comprehensive server statistics"""
        guild = interaction.guild
        
        if guild is None:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
        
        # Calculate detailed member statistics
        total_members = guild.member_count or 0
        human_members = sum(1 for member in guild.members if not member.bot)
        bot_members = sum(1 for member in guild.members if member.bot)
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        
        # Calculate channel statistics
        total_channels = len(guild.channels)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Role count
        roles_count = len(guild.roles)
        
        # Create main embed with server stats format
        embed = discord.Embed(
            title=f"📊 SERVER STATS 📊",
            description=f"**{guild.name}**",
            color=0x5865F2,  # Discord blurple color
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Server statistics in the exact format from your image
        stats_text = f"👥 **All Members:** {total_members:,}\n"
        stats_text += f"👤 **Members:** {human_members:,}\n" 
        stats_text += f"🤖 **Bots:** {bot_members:,}\n"
        stats_text += f"📺 **Channels:** {total_channels:,}\n"
        stats_text += f"🎭 **Roles:** {roles_count:,}"
        
        embed.add_field(name="", value=stats_text, inline=False)
        
        # Additional server details
        details_text = f"🟢 **Online:** {online_members:,}\n"
        details_text += f"💬 **Text Channels:** {text_channels:,}\n"
        details_text += f"🔊 **Voice Channels:** {voice_channels:,}\n"
        details_text += f"📂 **Categories:** {categories:,}\n"
        details_text += f"⭐ **Boost Level:** {guild.premium_tier}\n"
        details_text += f"🚀 **Boosts:** {guild.premium_subscription_count or 0}"
        
        embed.add_field(name="📈 Additional Stats", value=details_text, inline=True)
        
        # Server information
        info_text = f"**Owner:** <@{guild.owner_id}>\n"
        info_text += f"**Created:** {discord.utils.format_dt(guild.created_at, 'R')}\n"
        info_text += f"**ID:** `{guild.id}`\n"
        info_text += f"**Verification:** {guild.verification_level.name.title()}"
        
        embed.add_field(name="ℹ️ Server Info", value=info_text, inline=True)
        
        embed.set_footer(
            text=f"NexGuard Server Statistics • {human_members:,} humans, {bot_members:,} bots", 
            icon_url=guild.icon.url if guild.icon else None
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Log command usage
        await self.bot.log_command_usage(interaction, "serverinfo")
    
    @app_commands.command(name="avatar", description="Get a user's avatar")
    @app_commands.describe(user="The user to get the avatar of")
    async def avatar(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Get a user's avatar"""
        if user is None:
            if isinstance(interaction.user, discord.Member):
                user = interaction.user
            else:
                await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
                return
        
        embed = discord.Embed(
            title=f"🖼️ Avatar - {user.name}",
            color=user.color if user.color != discord.Color.default() else 0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        embed.set_image(url=user.display_avatar.url)
        embed.add_field(name="Download Links", value=f"[PNG]({user.display_avatar.with_format('png').url}) | [JPG]({user.display_avatar.with_format('jpg').url}) | [WEBP]({user.display_avatar.with_format('webp').url})", inline=False)
        
        embed.set_footer(text="Avatar Image", icon_url=None)
        
        await interaction.response.send_message(embed=embed)
        
        # Log command usage
        parameters = {"user": user.mention if user != interaction.user else "self"}
        await self.bot.log_command_usage(interaction, "avatar", parameters)
    
    @app_commands.command(name="botstats", description="Get bot statistics")
    async def botstats(self, interaction: discord.Interaction):
        """Get bot statistics"""
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Calculate uptime
        uptime = datetime.utcnow() - self.bot.bot_start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        embed = discord.Embed(
            title="🤖 Bot Statistics",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=sum(guild.member_count for guild in self.bot.guilds), inline=True)
        embed.add_field(name="Channels", value=sum(len(guild.channels) for guild in self.bot.guilds), inline=True)
        
        embed.add_field(name="Uptime", value=uptime_str, inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        
        embed.add_field(name="CPU Usage", value=f"{cpu_percent}%", inline=True)
        embed.add_field(name="Memory Usage", value=f"{memory.percent}%", inline=True)
        embed.add_field(name="Disk Usage", value=f"{disk.percent}%", inline=True)
        
        embed.set_footer(text="NexGuard v2.3.2", icon_url=None)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="guildlist", description="List all guilds the bot is connected to (Admin only)")
    async def guildlist(self, interaction: discord.Interaction):
        """List all guilds the bot is connected to"""
        # Check if user has admin permissions or is bot owner
        is_authorized = False
        
        # Check for administrator permissions
        if hasattr(interaction.user, 'guild_permissions') and hasattr(interaction.user.guild_permissions, 'administrator') and interaction.user.guild_permissions.administrator:
            is_authorized = True
        
        # Check for specific owner IDs
        owner_ids = [533347500679503872, 409889861441421315]  # Bot owner Discord user IDs
        if interaction.user.id in owner_ids:
            is_authorized = True
            
        # Allow if user has manage server permission
        if hasattr(interaction.user, 'guild_permissions') and hasattr(interaction.user.guild_permissions, 'manage_guild') and interaction.user.guild_permissions.manage_guild:
            is_authorized = True
        
        if not is_authorized:
            await interaction.response.send_message("❌ This command requires administrator permissions.", ephemeral=True)
            return
        
        # Get live data from bot's current connections
        guilds = self.bot.guilds
        guild_count = len(guilds)
        total_users = sum(guild.member_count for guild in guilds if guild.member_count)
        
        # Calculate additional live metrics
        online_members = 0
        large_guilds = 0
        for guild in guilds:
            if hasattr(guild, 'presence_count'):
                online_members += guild.presence_count or 0
            if guild.member_count and guild.member_count >= 1000:
                large_guilds += 1
        
        # Create embed with live guild information
        embed = discord.Embed(
            title="🔴 LIVE Guild Status | NexGuard",
            description=f"🌐 **Real-time data** from {guild_count} connected guilds\n💡 Protecting **{total_users:,}** total users across all servers\n⚡ Data refreshed: <t:{int(datetime.utcnow().timestamp())}:R>",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        # Split guilds into chunks for multiple fields (Discord field limit)
        chunk_size = 10
        guild_chunks = [guilds[i:i + chunk_size] for i in range(0, len(guilds), chunk_size)]
        
        for i, chunk in enumerate(guild_chunks):
            guild_info = []
            for guild in chunk:
                # Add live status indicators
                status_indicator = "🟢" if guild.member_count and guild.member_count > 0 else "🔴"
                large_guild_indicator = " 🏢" if guild.member_count and guild.member_count >= 1000 else ""
                boost_indicator = f" ⭐{guild.premium_subscription_count}" if hasattr(guild, 'premium_subscription_count') and guild.premium_subscription_count > 0 else ""
                
                guild_info.append(f"{status_indicator} **{guild.name}**{large_guild_indicator}{boost_indicator}\n`ID: {guild.id}`\n👥 {guild.member_count:,} members")
            
            field_name = f"📋 Live Data: Guilds {i*chunk_size + 1}-{min((i+1)*chunk_size, guild_count)}"
            embed.add_field(
                name=field_name,
                value="\n\n".join(guild_info),
                inline=True
            )
        
        # Add live metrics summary field
        avg_users = total_users//guild_count if guild_count > 0 else 0
        
        embed.add_field(
            name="📊 Live Metrics Summary",
            value=f"🌐 **Total Guilds:** {guild_count}\n👥 **Total Users:** {total_users:,}\n📈 **Average Users/Guild:** {avg_users:,}\n🏢 **Large Guilds (1000+):** {large_guilds}\n🔴 **Real-time Status:** All data live from Discord API",
            inline=False
        )
        
        # Add bot status field for context
        bot_uptime = "Connected" if self.bot.is_ready() else "Connecting"
        embed.add_field(
            name="🤖 Bot Status",
            value=f"⚡ **Status:** {bot_uptime}\n🔄 **Last Updated:** Just now\n📡 **Connection:** Active to all guilds\n💡 Use this command again for refreshed data",
            inline=False
        )
        
        # Create text file with all guild IDs for easy copying
        guild_ids_text = "\n".join([f"{guild.name}: {guild.id}" for guild in guilds])
        guild_ids_simple = ", ".join([str(guild.id) for guild in guilds])
        
        # Create downloadable file with live data snapshot
        file_content = f"🔴 LIVE NexGuard Guild Data - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        file_content += "=" * 80 + "\n\n"
        file_content += "📊 LIVE METRICS SUMMARY:\n"
        file_content += f"Total Guilds: {guild_count}\n"
        file_content += f"Total Users: {total_users:,}\n"
        file_content += f"Average Users/Guild: {avg_users:,}\n"
        file_content += f"Large Guilds (1000+ members): {large_guilds}\n"
        file_content += f"Data Timestamp: {datetime.utcnow().isoformat()} UTC\n\n"
        file_content += "🌐 DETAILED GUILD LIST:\n" + "-" * 50 + "\n"
        
        # Enhanced guild details with live data
        for guild in guilds:
            status = "ACTIVE" if guild.member_count and guild.member_count > 0 else "INACTIVE"
            large_status = " (LARGE GUILD)" if guild.member_count and guild.member_count >= 1000 else ""
            boosts = f" | Boosts: {guild.premium_subscription_count}" if hasattr(guild, 'premium_subscription_count') and guild.premium_subscription_count > 0 else ""
            
            file_content += f"{guild.name}: {guild.id} | Members: {guild.member_count:,} | Status: {status}{large_status}{boosts}\n"
        
        file_content += "\n" + "🆔 GUILD IDS ONLY (comma-separated):\n" + "-" * 50 + "\n"
        file_content += guild_ids_simple
        file_content += f"\n\n🔄 This data was captured live at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} and reflects real-time Discord API data."
        
        # Send embed and file
        file_bytes = BytesIO(file_content.encode('utf-8'))
        file = discord.File(file_bytes, filename=f"nexguard_guilds_{datetime.utcnow().strftime('%Y%m%d')}.txt")
        
        embed.set_footer(text="🔴 LIVE DATA | See attached file for complete real-time snapshot", icon_url=None)
        
        await interaction.response.send_message(embed=embed, file=file, ephemeral=True)
    
    @app_commands.command(name="getinvite", description="Generate an invite link for a guild (Owner only)")
    @app_commands.describe(guild_id="The guild ID to generate an invite for")
    async def getinvite(self, interaction: discord.Interaction, guild_id: str):
        """Generate an invite link for a specified guild"""
        # Check if user is bot owner
        owner_ids = [533347500679503872, 409889861441421315]  # Bot owner Discord user IDs
        if interaction.user.id not in owner_ids:
            await interaction.response.send_message("❌ This command is restricted to bot owners.", ephemeral=True)
            return
        
        try:
            guild_id_int = int(guild_id)
            guild = self.bot.get_guild(guild_id_int)
            
            if not guild:
                await interaction.response.send_message(f"❌ Bot is not connected to guild with ID: {guild_id}", ephemeral=True)
                return
            
            # Try to create an invite
            try:
                # Get the first available text channel or system channel
                invite_channel = None
                
                # Try system channel first
                if guild.system_channel and guild.system_channel.permissions_for(guild.me).create_instant_invite:
                    invite_channel = guild.system_channel
                else:
                    # Find first text channel where bot can create invites
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).create_instant_invite:
                            invite_channel = channel
                            break
                
                if not invite_channel:
                    await interaction.response.send_message(f"❌ No permission to create invites in **{guild.name}**", ephemeral=True)
                    return
                
                # Create invite
                invite = await invite_channel.create_invite(
                    max_age=3600,  # 1 hour
                    max_uses=1,    # Single use
                    unique=True,
                    reason=f"Invite requested by {interaction.user.name}"
                )
                
                embed = discord.Embed(
                    title="🔗 Guild Invite Generated",
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(name="Guild", value=f"**{guild.name}**", inline=True)
                embed.add_field(name="Guild ID", value=f"`{guild.id}`", inline=True)
                embed.add_field(name="Members", value=f"{guild.member_count:,}", inline=True)
                
                embed.add_field(name="Channel", value=f"#{invite_channel.name}", inline=True)
                embed.add_field(name="Expires", value="1 hour", inline=True)
                embed.add_field(name="Max Uses", value="1", inline=True)
                
                embed.add_field(name="🎫 Invite Link", value=f"[Click Here]({invite.url})", inline=False)
                embed.add_field(name="📋 Direct Link", value=f"`{invite.url}`", inline=False)
                
                embed.set_footer(text="Guild Invite", icon_url=None)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
            except discord.Forbidden:
                await interaction.response.send_message(f"❌ No permission to create invites in **{guild.name}**", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ Error creating invite: {str(e)}", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ Invalid guild ID format. Please provide a valid numeric guild ID.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="community", description="Join the official NexGuard Community Server")
    async def community(self, interaction: discord.Interaction):
        """Advertise NexGuard's community server"""
        embed = discord.Embed(
            title="🌟 NexGuard Community",
            description="Get support, updates, and connect with other admins",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🚀 Why Join?",
            value="**Expert Support** • **Early Updates** • **Active Community**\n**Beta Access** • **Direct Developer Contact** • **100% Free**",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Join Now",
            value="[**discord.gg/DNxp3Xxw59**](https://discord.gg/DNxp3Xxw59)",
            inline=False
        )
        
        embed.add_field(
            name="📊 Bot Stats",
            value=f"**{len(self.bot.guilds)}** servers • **{sum(guild.member_count for guild in self.bot.guilds)}** users • **59** commands",
            inline=False
        )
        
        embed.set_footer(text="NexGuard Community", icon_url=None)
        
        await interaction.response.send_message(embed=embed)
        
        # Log command usage
        await self.bot.log_command_usage(interaction, "community")
    
    @app_commands.command(name="broadcast-community", description="Send community invite to all servers (Owner only)")
    async def broadcast_community(self, interaction: discord.Interaction):
        """Broadcast community message to all connected servers"""
        # Check if user is bot owner
        owner_ids = [533347500679503872, 409889861441421315]  # Bot owner Discord user IDs
        if interaction.user.id not in owner_ids:
            await interaction.response.send_message("❌ This command is restricted to bot owners.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        guilds = self.bot.guilds
        success_count = 0
        failed_count = 0
        results = []
        
        # Community embed to send
        embed = discord.Embed(
            title="🌟 NexGuard Community",
            description="Get support, updates, and connect with other admins",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🚀 Why Join?",
            value="**Expert Support** • **Early Updates** • **Active Community**\n**Beta Access** • **Direct Developer Contact** • **100% Free**",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Join Now",
            value="[**discord.gg/DNxp3Xxw59**](https://discord.gg/DNxp3Xxw59)",
            inline=False
        )
        
        embed.add_field(
            name="📊 Bot Stats",
            value=f"**{len(self.bot.guilds)}** servers • **{sum(guild.member_count for guild in self.bot.guilds)}** users • **59** commands",
            inline=False
        )
        
        embed.set_footer(text="NexGuard Community Announcement")
        
        for guild in guilds:
            try:
                # Find suitable channel
                target_channel = None
                
                # Priority order for channel selection
                channel_names = ['general', 'announcements', 'chat', 'main', 'lobby', 'welcome']
                
                # Try to find channel by name
                for name in channel_names:
                    for channel in guild.text_channels:
                        if name in channel.name.lower() and channel.permissions_for(guild.me).send_messages:
                            target_channel = channel
                            break
                    if target_channel:
                        break
                
                # If no preferred channel found, use first available text channel
                if not target_channel:
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            target_channel = channel
                            break
                
                if target_channel:
                    await target_channel.send(embed=embed)
                    success_count += 1
                    results.append(f"✅ **{guild.name}** → #{target_channel.name}")
                else:
                    failed_count += 1
                    results.append(f"❌ **{guild.name}** → No permission")
                    
            except Exception as e:
                failed_count += 1
                results.append(f"❌ **{guild.name}** → {str(e)[:50]}")
        
        # Create result embed
        result_embed = discord.Embed(
            title="📢 Community Broadcast Complete",
            description=f"Sent to **{success_count}** servers, **{failed_count}** failed",
            color=0x00FF00 if failed_count == 0 else 0xFFFF00,
            timestamp=datetime.utcnow()
        )
        
        # Split results into chunks for multiple fields
        chunk_size = 10
        result_chunks = [results[i:i + chunk_size] for i in range(0, len(results), chunk_size)]
        
        for i, chunk in enumerate(result_chunks):
            field_name = f"📋 Results {i*chunk_size + 1}-{min((i+1)*chunk_size, len(results))}"
            result_embed.add_field(
                name=field_name,
                value="\n".join(chunk),
                inline=False
            )
        
        result_embed.set_footer(text="Broadcast Message")
        
        await interaction.followup.send(embed=result_embed, ephemeral=True)
        
        # Log command usage
        await self.bot.log_command_usage(interaction, "broadcast-community", {"success": success_count, "failed": failed_count})
    
    @app_commands.command(name="commands", description="List all available bot commands")
    async def commands(self, interaction: discord.Interaction):
        """List all available bot commands"""
        embed = discord.Embed(
            title="📋 NexGuard Commands",
            description="Complete list of all 60 available commands",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🔧 Admin Commands (8)",
            value="`/setprefix` `/configure` `/welcome` `/settings` `/logging-setup` `/autoreply-setup` `/automod-setup` `/modrole-setup`",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ Moderation Commands (13)", 
            value="`/ban` `/kick` `/warn` `/timeout` `/unban` `/purge` `/slowmode` `/lock` `/unlock` `/nuke` `/warnlist` `/unwarn` `/modlogs`",
            inline=False
        )
        
        embed.add_field(
            name="🎫 Ticket Commands (11)",
            value="`/ticket-panel` `/ticket-info` `/ticket-list` `/ticket-manage` `/ticket-deploy` `/close` `/close-request` `/claim` `/add` `/rename` `/ticket-logs`",
            inline=False
        )
        
        embed.add_field(
            name="🔍 Utility Commands (11)",
            value="`/ping` `/userinfo` `/serverinfo` `/avatar` `/botstats` `/uptime` `/embed` `/guildlist` `/getinvite` `/community` `/broadcast-community`",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ AutoMod Commands (6)",
            value="`/automod-toggle` `/automod-settings` `/automod-whitelist` `/automod-logs` `/automod-status` `/automod-reset`",
            inline=False
        )
        
        embed.add_field(
            name="💬 Auto-Reply Commands (4)",
            value="`/autoreply-add` `/autoreply-remove` `/autoreply-list` `/autoreply-toggle`",
            inline=False
        )
        
        embed.add_field(
            name="📊 Event Logging Commands (3)",
            value="`/eventlog-setup` `/eventlog-toggle` `/eventlog-status`",
            inline=False
        )
        
        embed.add_field(
            name="🎭 Role Management Commands (4)", 
            value="`/modrole-add` `/modrole-remove` `/modrole-list` `/reaction-role`",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Information",
            value="Use `/help <command>` for detailed information about any command.\nUse `/commands` to see this list anytime.",
            inline=False
        )
        
        embed.set_footer(text="NexGuard v2.3.2 | Total: 60 Commands", icon_url=None)
        
        await interaction.response.send_message(embed=embed)
        
        # Log command usage
        await self.bot.log_command_usage(interaction, "commands")
    
    @app_commands.command(name="help", description="Get detailed help for a specific command")
    @app_commands.describe(command="Get detailed help for a specific command")
    async def help(self, interaction: discord.Interaction, command: Optional[str] = None):
        """Get help with bot commands"""
        
        # Define all commands with their detailed descriptions
        command_help = {
            # Admin Commands
            "setprefix": {"desc": "Set a custom prefix for the bot", "params": ["prefix (Required): New prefix to use"]},
            "configure": {"desc": "Configure bot settings for your server", "params": []},
            "welcome": {"desc": "Set up welcome messages for new members", "params": ["channel (Optional): Welcome channel", "message (Optional): Welcome message"]},
            "settings": {"desc": "View current server settings", "params": []},
            "logging-setup": {"desc": "Configure logging channels", "params": ["channel (Required): Logging channel"]},
            "autoreply-setup": {"desc": "Set up auto-reply system", "params": []},
            "automod-setup": {"desc": "Configure AutoMod settings", "params": []},
            "modrole-setup": {"desc": "Set up moderation roles", "params": []},
            
            # Moderation Commands
            "ban": {"desc": "Ban a user from the server", "params": ["user (Required): User to ban", "reason (Optional): Ban reason"]},
            "kick": {"desc": "Kick a user from the server", "params": ["user (Required): User to kick", "reason (Optional): Kick reason"]},
            "warn": {"desc": "Warn a user", "params": ["user (Required): User to warn", "reason (Required): Warning reason"]},
            "timeout": {"desc": "Timeout a user", "params": ["user (Required): User to timeout", "duration (Required): Timeout duration", "reason (Optional): Timeout reason"]},
            "unban": {"desc": "Unban a user", "params": ["user (Required): User ID to unban", "reason (Optional): Unban reason"]},
            "purge": {"desc": "Delete multiple messages", "params": ["amount (Required): Number of messages to delete"]},
            "slowmode": {"desc": "Set channel slowmode", "params": ["seconds (Required): Slowmode duration in seconds"]},
            "lock": {"desc": "Lock a channel", "params": ["channel (Optional): Channel to lock"]},
            "unlock": {"desc": "Unlock a channel", "params": ["channel (Optional): Channel to unlock"]},
            "nuke": {"desc": "Delete and recreate a channel", "params": ["channel (Optional): Channel to nuke"]},
            "warnlist": {"desc": "View warnings for a user", "params": ["user (Required): User to check warnings"]},
            "unwarn": {"desc": "Remove a warning", "params": ["user (Required): User", "warning_id (Required): Warning ID to remove"]},
            "modlogs": {"desc": "View moderation logs", "params": ["user (Optional): User to check logs"]},
            
            # Ticket Commands
            "ticket-panel": {"desc": "Create or manage ticket panels", "params": ["action (Required): create/edit/delete", "name (Optional): Panel name"]},
            "ticket-info": {"desc": "Get information about current ticket", "params": []},
            "ticket-list": {"desc": "List all ticket panels", "params": []},
            "ticket-manage": {"desc": "Manage ticket settings", "params": []},
            "ticket-deploy": {"desc": "Deploy ticket panel to channel", "params": ["panel (Required): Panel name", "channel (Required): Target channel"]},
            "close": {"desc": "Close current ticket", "params": ["reason (Optional): Close reason"]},
            "close-request": {"desc": "Request ticket closure", "params": ["reason (Optional): Close reason"]},
            "claim": {"desc": "Claim a ticket", "params": []},
            "add": {"desc": "Add user to ticket", "params": ["user (Required): User to add"]},
            "rename": {"desc": "Rename ticket channel", "params": ["name (Required): New channel name"]},
            "ticket-logs": {"desc": "View ticket logs", "params": ["ticket_id (Optional): Specific ticket ID"]},
            
            # Utility Commands
            "ping": {"desc": "Check bot latency", "params": []},
            "userinfo": {"desc": "Get information about a user", "params": ["user (Optional): User to get info about"]},
            "serverinfo": {"desc": "Get information about the server", "params": []},
            "avatar": {"desc": "Get a user's avatar", "params": ["user (Optional): User to get avatar"]},
            "botstats": {"desc": "Get bot statistics", "params": []},
            "uptime": {"desc": "Check how long the bot has been running", "params": []},
            "embed": {"desc": "Create custom embeds", "params": ["title (Required): Embed title", "description (Optional): Embed description"]},
            "guildlist": {"desc": "List all guilds (Admin only)", "params": []},
            "getinvite": {"desc": "Generate invite for guild (Owner only)", "params": ["guild_id (Required): Guild ID"]},
            "community": {"desc": "Join NexGuard Community Server", "params": []},
            "broadcast-community": {"desc": "Broadcast community invite (Owner only)", "params": []},
            
            # AutoMod Commands
            "automod-toggle": {"desc": "Toggle AutoMod on/off", "params": ["enabled (Required): true/false"]},
            "automod-settings": {"desc": "Configure AutoMod settings", "params": []},
            "automod-whitelist": {"desc": "Manage AutoMod whitelist", "params": ["action (Required): add/remove", "item (Required): Item to whitelist"]},
            "automod-logs": {"desc": "View AutoMod logs", "params": []},
            "automod-status": {"desc": "Check AutoMod status", "params": []},
            "automod-reset": {"desc": "Reset AutoMod settings", "params": []},
            
            # Auto-Reply Commands
            "autoreply-add": {"desc": "Add auto-reply trigger", "params": ["trigger (Required): Trigger word/phrase", "response (Required): Auto response"]},
            "autoreply-remove": {"desc": "Remove auto-reply trigger", "params": ["trigger (Required): Trigger to remove"]},
            "autoreply-list": {"desc": "List all auto-reply triggers", "params": []},
            "autoreply-toggle": {"desc": "Toggle auto-reply system", "params": ["enabled (Required): true/false"]},
            
            # Event Logging Commands
            "eventlog-setup": {"desc": "Set up event logging", "params": ["channel (Required): Logging channel"]},
            "eventlog-toggle": {"desc": "Toggle event logging", "params": ["event_type (Required): Event type", "enabled (Required): true/false"]},
            "eventlog-status": {"desc": "Check event logging status", "params": []},
            
            # Role Management Commands
            "modrole-add": {"desc": "Add moderation role", "params": ["role (Required): Role to add"]},
            "modrole-remove": {"desc": "Remove moderation role", "params": ["role (Required): Role to remove"]},
            "modrole-list": {"desc": "List moderation roles", "params": []},
            "reaction-role": {"desc": "Set up reaction roles", "params": ["message_id (Required): Message ID", "emoji (Required): Emoji", "role (Required): Role to assign"]},
            
            # Information Commands
            "commands": {"desc": "List all available commands", "params": []},
            "help": {"desc": "Get help for specific commands", "params": ["command (Optional): Command to get help for"]}
        }
        
        if command:
            if command in command_help:
                cmd_info = command_help[command]
                embed = discord.Embed(
                    title=f"📖 Help - /{command}",
                    description=cmd_info["desc"],
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                
                if cmd_info["params"]:
                    embed.add_field(
                        name="Parameters",
                        value="\n".join([f"• {param}" for param in cmd_info["params"]]),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="Parameters",
                        value="No parameters required",
                        inline=False
                    )
                
                embed.add_field(
                    name="Usage",
                    value=f"`/{command}` - {cmd_info['desc']}",
                    inline=False
                )
                
                embed.set_footer(text="Use /commands to see all commands", icon_url=None)
                
                await interaction.response.send_message(embed=embed)
            else:
                embed = discord.Embed(
                    title="❌ Command Not Found",
                    description=f"Command `/{command}` not found.\n\nUse `/commands` to see all available commands.",
                    color=0xFF0000,
                    timestamp=datetime.utcnow()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            # Show general help
            embed = discord.Embed(
                title="📖 NexGuard Help",
                description="Get detailed help for any command",
                color=0x00FFFF,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="🔍 How to Use",
                value="• Use `/commands` to see all available commands\n• Use `/help <command>` to get detailed help for a specific command\n• Example: `/help ban` for ban command details",
                inline=False
            )
            
            embed.add_field(
                name="📊 Quick Stats",
                value=f"**61** total commands across **8** categories\n**{len(self.bot.guilds)}** servers protected\n**{sum(guild.member_count for guild in self.bot.guilds)}** users secured",
                inline=False
            )
            
            embed.add_field(
                name="🌟 Popular Commands",
                value="`/commands` `/ticket-panel` `/ban` `/help` `/community`",
                inline=False
            )
            
            embed.set_footer(text="NexGuard v2.3.2", icon_url=None)
            
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="uptime", description="Check how long the bot has been running")
    async def uptime(self, interaction: discord.Interaction):
        """Check how long the bot has been running"""
        uptime = datetime.utcnow() - self.bot.bot_start_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        
        embed = discord.Embed(
            title="⏱️ Bot Uptime",
            description=f"I've been running for **{uptime_str}**",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Started", value=discord.utils.format_dt(self.bot.bot_start_time, "F"), inline=False)
        embed.set_footer(text="Bot Uptime", icon_url=None)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="embed", description="Create a custom embed message")
    @app_commands.describe(
        title="Title of the embed",
        description="Description of the embed (supports \\n for newlines)",
        color="Color in hex format (e.g., #00FFFF)",
        thumbnail="URL for thumbnail image",
        image="URL for main image",
        footer="Footer text (supports \\n for newlines)",
        author="Author name (supports \\n for newlines)",
        author_icon="Author icon URL",
        url="URL to make title clickable",
        channel="Channel to send the embed to"
    )
    async def embed(self, interaction: discord.Interaction, title: str, description: str, 
                   color: str = "#00FFFF", thumbnail: Optional[str] = None, image: Optional[str] = None, 
                   footer: Optional[str] = None, author: Optional[str] = None, author_icon: Optional[str] = None,
                   url: Optional[str] = None, channel: Optional[discord.TextChannel] = None):
        """Create a custom embed message with newline support"""
        await interaction.response.defer()
        
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.manage_messages:
            await interaction.followup.send("❌ You need Manage Messages permission to use this command.", ephemeral=True)
            return
        
        try:
            # Parse color
            if color.startswith('#'):
                color = color[1:]
            color_int = int(color, 16)
        except ValueError:
            color_int = 0x00FFFF
        
        # Process newlines in text fields
        processed_title = process_newlines(title)
        processed_description = process_newlines(description)
        processed_footer = process_newlines(footer) if footer else None
        processed_author = process_newlines(author) if author else None
        
        # Create embed with newline processing
        embed = discord.Embed(
            title=processed_title,
            description=processed_description,
            color=color_int,
            timestamp=datetime.utcnow(),
            url=url
        )
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        if image:
            embed.set_image(url=image)
        
        if processed_author:
            embed.set_author(name=processed_author, icon_url=author_icon)
        
        if processed_footer:
            embed.set_footer(text=processed_footer, icon_url=None)
        else:
            embed.set_footer(text="Custom Embed", icon_url=None)
        
        # Send to specified channel or current channel
        target_channel = channel or interaction.channel
        
        try:
            await target_channel.send(embed=embed)
            
            # Confirm to user
            confirm_embed = discord.Embed(
                title="✅ Embed Created",
                description=f"Your embed has been sent to {target_channel.mention}",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            
            await interaction.followup.send(embed=confirm_embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error creating embed: {e}")
            await interaction.followup.send(f"❌ Failed to send embed: {str(e)}", ephemeral=True)
    

    @app_commands.command(name="embedbuilder", description="Create advanced embeds with fields and buttons")
    @app_commands.describe(
        title="Title of the embed",
        description="Description of the embed",
        color="Color in hex format (e.g., #00FFFF)",
        fields="Fields in format: name1|value1|inline1;name2|value2|inline2 (inline: true/false)",
        buttons="Buttons in format: label1|url1|style1;label2|url2|style2 (style: primary/secondary/success/danger/link)",
        thumbnail="URL for thumbnail image",
        image="URL for main image",
        footer="Footer text",
        author="Author name",
        channel="Channel to send the embed to"
    )
    async def embedbuilder(self, interaction: discord.Interaction, title: str, description: Optional[str] = None,
                          color: str = "#00FFFF", fields: Optional[str] = None, buttons: Optional[str] = None,
                          thumbnail: Optional[str] = None, image: Optional[str] = None, footer: Optional[str] = None,
                          author: Optional[str] = None, channel: Optional[discord.TextChannel] = None):
        """Create advanced embeds with fields and buttons"""
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You need Manage Messages permission to use this command.", ephemeral=True)
            return
        
        try:
            # Parse color
            if color.startswith('#'):
                color = color[1:]
            color_int = int(color, 16)
        except ValueError:
            color_int = 0x00FFFF
        
        # Create embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=color_int,
            timestamp=datetime.utcnow()
        )
        
        # Add fields if provided
        if fields:
            try:
                field_list = fields.split(';')
                for field in field_list:
                    parts = field.split('|')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        value = parts[1].strip()
                        inline = parts[2].strip().lower() == 'true' if len(parts) > 2 else False
                        embed.add_field(name=name, value=value, inline=inline)
            except Exception as e:
                await interaction.response.send_message(f"❌ Error parsing fields: {str(e)}", ephemeral=True)
                return
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        if image:
            embed.set_image(url=image)
        
        if author:
            embed.set_author(name=author, icon_url=None)
        
        if footer:
            embed.set_footer(text=footer, icon_url=None)
        else:
            embed.set_footer(text="Custom Embed Builder", icon_url=None)
        
        # Create view with buttons if provided
        view = None
        if buttons:
            try:
                view = EmbedButtonView()
                button_list = buttons.split(';')
                for button in button_list:
                    parts = button.split('|')
                    if len(parts) >= 2:
                        label = parts[0].strip()
                        url = parts[1].strip()
                        style = parts[2].strip().lower() if len(parts) > 2 else 'primary'
                        
                        # Convert style string to Discord style
                        style_map = {
                            'primary': discord.ButtonStyle.primary,
                            'secondary': discord.ButtonStyle.secondary,
                            'success': discord.ButtonStyle.success,
                            'danger': discord.ButtonStyle.danger,
                            'link': discord.ButtonStyle.link
                        }
                        
                        button_style = style_map.get(style, discord.ButtonStyle.primary)
                        
                        if button_style == discord.ButtonStyle.link:
                            view.add_item(discord.ui.Button(label=label, url=url, style=button_style))
                        else:
                            view.add_item(EmbedButton(label=label, style=button_style, custom_id=f"embed_btn_{len(view.children)}"))
                            
            except Exception as e:
                await interaction.response.send_message(f"❌ Error parsing buttons: {str(e)}", ephemeral=True)
                return
        
        # Send to specified channel or current channel
        target_channel = channel or interaction.channel
        
        try:
            if view and view.children:
                await target_channel.send(embed=embed, view=view)
            else:
                await target_channel.send(embed=embed)
            
            # Confirm to user
            confirm_embed = discord.Embed(
                title="✅ Advanced Embed Created",
                description=f"Your advanced embed has been sent to {target_channel.mention}",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            
            if fields:
                confirm_embed.add_field(name="Fields Added", value=str(len(fields.split(';'))), inline=True)
            if buttons:
                confirm_embed.add_field(name="Buttons Added", value=str(len(buttons.split(';'))), inline=True)
            
            await interaction.response.send_message(embed=confirm_embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to send embed: {str(e)}", ephemeral=True)

class EmbedButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # No timeout for persistent buttons

class EmbedButton(discord.ui.Button):
    def __init__(self, label: str, style: discord.ButtonStyle, custom_id: str):
        super().__init__(label=label, style=style, custom_id=custom_id)
    
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Button Clicked!",
            description=f"You clicked the **{self.label}** button.",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Button Interaction", icon_url=None)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))