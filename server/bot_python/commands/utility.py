import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime
import platform
import psutil
import os
from typing import Optional

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
        
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
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
        
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
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
        
        embed.set_footer(text=f"NexGuard v2.3.2 | Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="guildlist", description="List all guilds the bot is connected to (Admin only)")
    async def guildlist(self, interaction: discord.Interaction):
        """List all guilds the bot is connected to"""
        # Check if user has admin permissions or is bot owner
        is_authorized = False
        
        # Check for administrator permissions
        if hasattr(interaction.user, 'guild_permissions') and interaction.user.guild_permissions.administrator:
            is_authorized = True
        
        # Check for specific owner IDs (add your Discord user ID here)
        owner_ids = [533347500679503872]  # Replace with actual owner Discord user IDs
        if interaction.user.id in owner_ids:
            is_authorized = True
            
        # Allow if user has manage server permission
        if hasattr(interaction.user, 'guild_permissions') and interaction.user.guild_permissions.manage_guild:
            is_authorized = True
        
        if not is_authorized:
            await interaction.response.send_message("❌ This command requires administrator permissions.", ephemeral=True)
            return
        
        guilds = self.bot.guilds
        guild_count = len(guilds)
        total_users = sum(guild.member_count for guild in guilds if guild.member_count)
        
        # Create embed with guild information
        embed = discord.Embed(
            title="🌐 NexGuard Guild List",
            description=f"Connected to **{guild_count}** guilds protecting **{total_users:,}** users",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        # Split guilds into chunks for multiple fields (Discord field limit)
        chunk_size = 10
        guild_chunks = [guilds[i:i + chunk_size] for i in range(0, len(guilds), chunk_size)]
        
        for i, chunk in enumerate(guild_chunks):
            guild_info = []
            for guild in chunk:
                guild_info.append(f"**{guild.name}**\n`ID: {guild.id}`\nMembers: {guild.member_count:,}")
            
            field_name = f"📋 Guilds {i*chunk_size + 1}-{min((i+1)*chunk_size, guild_count)}"
            embed.add_field(
                name=field_name,
                value="\n\n".join(guild_info),
                inline=True
            )
        
        # Add summary field
        embed.add_field(
            name="📊 Summary",
            value=f"**Total Guilds:** {guild_count}\n**Total Users:** {total_users:,}\n**Average Users/Guild:** {total_users//guild_count if guild_count > 0 else 0}",
            inline=False
        )
        
        # Create text file with all guild IDs for easy copying
        guild_ids_text = "\n".join([f"{guild.name}: {guild.id}" for guild in guilds])
        guild_ids_simple = ", ".join([str(guild.id) for guild in guilds])
        
        # Create downloadable file
        file_content = f"NexGuard Guild List - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
        file_content += "=" * 60 + "\n\n"
        file_content += f"Total Guilds: {guild_count}\n"
        file_content += f"Total Users: {total_users:,}\n\n"
        file_content += "Guild Details:\n" + "-" * 30 + "\n"
        file_content += guild_ids_text + "\n\n"
        file_content += "Guild IDs Only (comma-separated):\n" + "-" * 40 + "\n"
        file_content += guild_ids_simple
        
        # Send embed and file
        file = discord.File(StringIO(file_content), filename=f"nexguard_guilds_{datetime.utcnow().strftime('%Y%m%d')}.txt")
        
        embed.set_footer(text=f"Requested by {interaction.user.name} | See attached file for complete list", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed, file=file, ephemeral=True)
    
    @app_commands.command(name="help", description="Get help with bot commands")
    @app_commands.describe(command="Get detailed help for a specific command")
    async def help(self, interaction: discord.Interaction, command: Optional[str] = None):
        """Get help with bot commands"""
        if command:
            # Get specific command help
            cmd = self.bot.tree.get_command(command)
            if cmd:
                embed = discord.Embed(
                    title=f"📖 Help - /{command}",
                    description=cmd.description,
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                
                if hasattr(cmd, 'parameters') and cmd.parameters:
                    params = []
                    for param in cmd.parameters:
                        required = "Required" if param.required else "Optional"
                        params.append(f"`{param.name}` - {param.description} ({required})")
                    embed.add_field(name="Parameters", value="\n".join(params), inline=False)
                
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"❌ Command `{command}` not found.", ephemeral=True)
        else:
            # General help
            embed = discord.Embed(
                title="📖 NexGuard Command Reference",
                description="Complete list of all 56 available commands:",
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
                name="🔍 Utility Commands (7)",
                value="`/ping` `/userinfo` `/serverinfo` `/avatar` `/botstats` `/help` `/uptime` `/embed`",
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
                name="Need more help?",
                value="Use `/help <command>` for detailed information about a specific command.\n\n**Total Commands:** 56 across 8 categories\n**Server Coverage:** 18 guilds, 406 users protected",
                inline=False
            )
            
            embed.set_footer(text=f"NexGuard v2.3.2 | Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            
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
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
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
            embed.set_footer(text=processed_footer, icon_url=interaction.user.display_avatar.url)
        else:
            embed.set_footer(text=f"Created by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
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
    
    @app_commands.command(name="commands", description="List all available bot commands")
    async def commands_list(self, interaction: discord.Interaction):
        """List all available bot commands"""
        embed = discord.Embed(
            title="📋 NexGuard Commands",
            description="Here are all the available commands organized by category:",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        # Admin Commands
        admin_commands = [
            "`/settings` - View server settings",
            "`/welcome` - Manage welcome messages",
            "`/botlogging` - Configure bot logging",
            "`/errorlog` - Configure error logging",
            "`/changelog` - Manage bot changelog"
        ]
        embed.add_field(name="⚙️ Admin Commands", value="\n".join(admin_commands), inline=False)
        
        # Moderation Commands
        mod_commands = [
            "`/ban` - Ban a user (with temp duration)",
            "`/kick` - Kick a user",
            "`/warn` - Warn a user",
            "`/timeout` - Timeout a user",
            "`/untimeout` - Remove timeout from user",
            "`/unban` - Unban a user",
            "`/mute` - Mute a user",
            "`/unmute` - Unmute a user",
            "`/lock` - Lock a channel",
            "`/unlock` - Unlock a channel",
            "`/slowmode` - Set channel slowmode",
            "`/purge` - Delete multiple messages"
        ]
        embed.add_field(name="⚖️ Moderation Commands", value="\n".join(mod_commands), inline=False)
        
        # Utility Commands
        util_commands = [
            "`/ping` - Check bot latency",
            "`/userinfo` - Get user information",
            "`/serverinfo` - Get server information",
            "`/avatar` - Get user avatar",
            "`/botstats` - Get bot statistics",
            "`/help` - Get help with commands",
            "`/uptime` - Check bot uptime",
            "`/embed` - Create custom embeds",
            "`/embedbuilder` - Create advanced embeds with fields and buttons",
            "`/embedhelp` - Get help with embed formatting",
            "`/embedexample` - View embed examples",
            "`/commands` - List all commands"
        ]
        embed.add_field(name="🔍 Utility Commands", value="\n".join(util_commands), inline=False)
        
        # Ticket Commands
        ticket_commands = [
            "`/ticket` - Create support ticket",
            "`/tickets` - List and manage tickets",
            "`/ticketcategory` - Manage ticket categories"
        ]
        embed.add_field(name="🎫 Ticket Commands", value="\n".join(ticket_commands), inline=False)
        
        embed.add_field(
            name="Need Help?",
            value="Use `/help <command>` for detailed information about any command.",
            inline=False
        )
        
        # AutoMod Commands
        automod_commands = [
            "`/automod-config` - View AutoMod configuration",
            "`/automod-spam` - Configure spam protection",
            "`/automod-links` - Configure link filtering",
            "`/automod-badwords` - Configure bad words filter",
            "`/automod-caps` - Configure caps lock filter",
            "`/automod-mentions` - Configure mention limits",
            "`/automod-words` - Manage custom bad words",
            "`/automod-reset` - Reset all AutoMod settings"
        ]
        embed.add_field(name="🛡️ AutoMod Commands", value="\n".join(automod_commands), inline=False)
        
        # Auto-Reply Commands
        autoreply_commands = [
            "`/autoreply-create` - Create auto-reply rules",
            "`/autoreply-list` - List all auto-reply rules",
            "`/autoreply-toggle` - Enable/disable auto-reply rules",
            "`/autoreply-delete` - Delete auto-reply rules",
            "`/autoreply-stats` - View auto-reply statistics"
        ]
        embed.add_field(name="🤖 Auto-Reply Commands", value="\n".join(autoreply_commands), inline=False)
        
        # Role Management Commands
        role_commands = [
            "`/modrole` - Set custom moderation role",
            "`/adminrole` - Set custom admin role",
            "`/resetmodrole` - Reset custom roles",
            "`/modpermissions` - View mod permissions",
            "`/autorole` - Configure auto-role assignment"
        ]
        embed.add_field(name="👥 Role Management", value="\n".join(role_commands), inline=False)
        
        embed.set_footer(text=f"NexGuard v2.3.2 | Total Commands: 51+", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
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
            embed.set_author(name=author, icon_url=interaction.user.display_avatar.url)
        
        if footer:
            embed.set_footer(text=footer, icon_url=interaction.user.display_avatar.url)
        else:
            embed.set_footer(text=f"Created by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
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
        embed.set_footer(text=f"Clicked by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))