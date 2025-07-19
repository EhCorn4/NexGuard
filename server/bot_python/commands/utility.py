import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime
import platform
import psutil
import os

logger = logging.getLogger(__name__)

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
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        """Get information about a user"""
        if user is None:
            user = interaction.user
        
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
    
    @app_commands.command(name="serverinfo", description="Get information about the server")
    async def serverinfo(self, interaction: discord.Interaction):
        """Get information about the server"""
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"🏠 Server Information - {guild.name}",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Server Name", value=guild.name, inline=True)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        
        embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at, "F"), inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Verification Level", value=guild.verification_level.name.title(), inline=True)
        
        embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        
        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        embed.add_field(name="Boost Count", value=guild.premium_subscription_count, inline=True)
        embed.add_field(name="File Size Limit", value=f"{guild.filesize_limit // 1024 // 1024}MB", inline=True)
        
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
        
        # Log command usage
        await self.bot.log_command_usage(interaction, "serverinfo")
    
    @app_commands.command(name="avatar", description="Get a user's avatar")
    @app_commands.describe(user="The user to get the avatar of")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        """Get a user's avatar"""
        if user is None:
            user = interaction.user
        
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
    
    @app_commands.command(name="help", description="Get help with bot commands")
    @app_commands.describe(command="Get detailed help for a specific command")
    async def help(self, interaction: discord.Interaction, command: str = None):
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
                title="📖 NexGuard Help",
                description="Here are the available command categories:",
                color=0x00FFFF,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="🔧 Admin Commands",
                value="`/setprefix` `/configure` `/welcome` `/settings`",
                inline=False
            )
            
            embed.add_field(
                name="🛡️ Moderation Commands", 
                value="`/ban` `/kick` `/warn` `/timeout` `/unban` `/purge`",
                inline=False
            )
            
            embed.add_field(
                name="🎫 Ticket Commands",
                value="`/ticket` `/ticketinfo` `/ticketmanage`",
                inline=False
            )
            
            embed.add_field(
                name="🔍 Utility Commands",
                value="`/ping` `/userinfo` `/serverinfo` `/avatar` `/botstats`",
                inline=False
            )
            
            embed.add_field(
                name="Need more help?",
                value="Use `/help <command>` for detailed information about a specific command.",
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
        description="Description of the embed",
        color="Color in hex format (e.g., #00FFFF)",
        thumbnail="URL for thumbnail image",
        image="URL for main image",
        footer="Footer text",
        author="Author name",
        author_icon="Author icon URL",
        url="URL to make title clickable",
        channel="Channel to send the embed to"
    )
    async def embed(self, interaction: discord.Interaction, title: str, description: str, 
                   color: str = "#00FFFF", thumbnail: str = None, image: str = None, 
                   footer: str = None, author: str = None, author_icon: str = None,
                   url: str = None, channel: discord.TextChannel = None):
        """Create a custom embed message"""
        if not interaction.user.guild_permissions.manage_messages:
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
            timestamp=datetime.utcnow(),
            url=url
        )
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        if image:
            embed.set_image(url=image)
        
        if author:
            embed.set_author(name=author, icon_url=author_icon)
        
        if footer:
            embed.set_footer(text=footer, icon_url=interaction.user.display_avatar.url)
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
            
            await interaction.response.send_message(embed=confirm_embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to send embed: {str(e)}", ephemeral=True)
    
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
            "`/setprefix` - Set command prefix",
            "`/configure` - Configure server settings",
            "`/welcome` - Manage welcome messages",
            "`/settings` - View server settings"
        ]
        embed.add_field(name="🔧 Admin Commands", value="\n".join(admin_commands), inline=False)
        
        # Moderation Commands
        mod_commands = [
            "`/ban` - Ban a user",
            "`/kick` - Kick a user",
            "`/warn` - Warn a user",
            "`/timeout` - Timeout a user",
            "`/unban` - Unban a user",
            "`/purge` - Delete multiple messages"
        ]
        embed.add_field(name="🛡️ Moderation Commands", value="\n".join(mod_commands), inline=False)
        
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
            "`/ticketinfo` - Get ticket information",
            "`/ticketmanage` - Manage tickets (staff only)"
        ]
        embed.add_field(name="🎫 Ticket Commands", value="\n".join(ticket_commands), inline=False)
        
        embed.add_field(
            name="Need Help?",
            value="Use `/help <command>` for detailed information about any command.",
            inline=False
        )
        
        embed.set_footer(text=f"NexGuard v2.3.2 | Total Commands: 27", icon_url=interaction.user.display_avatar.url)
        
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
    async def embedbuilder(self, interaction: discord.Interaction, title: str, description: str = None,
                          color: str = "#00FFFF", fields: str = None, buttons: str = None,
                          thumbnail: str = None, image: str = None, footer: str = None,
                          author: str = None, channel: discord.TextChannel = None):
        """Create advanced embeds with fields and buttons"""
        if not interaction.user.guild_permissions.manage_messages:
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
            await target_channel.send(embed=embed, view=view)
            
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