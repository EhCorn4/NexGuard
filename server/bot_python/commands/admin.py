import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="setprefix", description="Set the command prefix for this server")
    @app_commands.describe(prefix="The new prefix to set")
    async def setprefix(self, interaction: discord.Interaction, prefix: str):
        """Set the command prefix for this server"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to use this command.", ephemeral=True)
            return
        
        try:
            await self.bot.update_guild_config(str(interaction.guild.id), prefix=prefix)
            await interaction.response.send_message(f"✅ Server prefix updated to: `{prefix}`", ephemeral=True)
        except Exception as e:
            logger.error(f"Error updating prefix: {e}")
            await interaction.response.send_message("❌ Failed to update prefix. Please try again.", ephemeral=True)
    
    @app_commands.command(name="configure", description="Configure server settings")
    @app_commands.describe(
        setting="The setting to configure",
        value="The value to set"
    )
    @app_commands.choices(setting=[
        app_commands.Choice(name="moderation", value="moderation"),
        app_commands.Choice(name="welcome", value="welcome"),
        app_commands.Choice(name="automod", value="automod"),
        app_commands.Choice(name="logging", value="logging"),
        app_commands.Choice(name="error-logging", value="error-logging")
    ])
    async def configure(self, interaction: discord.Interaction, setting: str, value: str):
        """Configure server settings"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to use this command.", ephemeral=True)
            return
        
        try:
            guild_id = str(interaction.guild.id)
            
            if setting == "moderation":
                enabled = value.lower() in ['true', 'yes', '1', 'on', 'enable']
                await self.bot.update_guild_config(guild_id, moderation_enabled=enabled)
                status = "enabled" if enabled else "disabled"
                await interaction.response.send_message(f"✅ Moderation features {status}.", ephemeral=True)
                
            elif setting == "welcome":
                # Parse channel mention or ID
                channel_id = value.replace('<#', '').replace('>', '')
                try:
                    channel = self.bot.get_channel(int(channel_id))
                    if channel and channel.guild.id == interaction.guild.id:
                        await self.bot.update_guild_config(guild_id, welcome_channel_id=channel_id)
                        await interaction.response.send_message(f"✅ Welcome channel set to {channel.mention}.", ephemeral=True)
                    else:
                        await interaction.response.send_message("❌ Invalid channel. Please mention a valid channel.", ephemeral=True)
                except ValueError:
                    await interaction.response.send_message("❌ Invalid channel ID. Please mention a valid channel.", ephemeral=True)
                    
            elif setting == "automod":
                enabled = value.lower() in ['true', 'yes', '1', 'on', 'enable']
                await self.bot.update_guild_config(guild_id, automod_enabled=enabled)
                status = "enabled" if enabled else "disabled"
                await interaction.response.send_message(f"✅ Automod features {status}.", ephemeral=True)
                
            elif setting == "logging":
                # Parse channel mention or ID
                channel_id = value.replace('<#', '').replace('>', '')
                try:
                    channel = self.bot.get_channel(int(channel_id))
                    if channel and channel.guild.id == interaction.guild.id:
                        await self.bot.update_guild_config(guild_id, log_channel_id=channel_id)
                        await interaction.response.send_message(f"✅ Logging channel set to {channel.mention}.", ephemeral=True)
                    else:
                        await interaction.response.send_message("❌ Invalid channel. Please mention a valid channel.", ephemeral=True)
                except ValueError:
                    await interaction.response.send_message("❌ Invalid channel ID. Please mention a valid channel.", ephemeral=True)
                    
            elif setting == "error-logging":
                # Parse channel mention or ID
                channel_id = value.replace('<#', '').replace('>', '')
                try:
                    channel = self.bot.get_channel(int(channel_id))
                    if channel and channel.guild.id == interaction.guild.id:
                        await self.bot.update_guild_config(guild_id, error_log_channel_id=channel_id)
                        await interaction.response.send_message(f"✅ Error logging channel set to {channel.mention}.", ephemeral=True)
                    else:
                        await interaction.response.send_message("❌ Invalid channel. Please mention a valid channel.", ephemeral=True)
                except ValueError:
                    await interaction.response.send_message("❌ Invalid channel ID. Please mention a valid channel.", ephemeral=True)
            
            # Log command usage if successful
            if not interaction.response.is_done():
                parameters = {"setting": setting, "value": value}
                await self.bot.log_command_usage(interaction, "configure", parameters)
                    
        except Exception as e:
            logger.error(f"Error configuring server: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Failed to update configuration. Please try again.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Failed to update configuration. Please try again.", ephemeral=True)
            except:
                pass
    
    @app_commands.command(name="welcome", description="Configure welcome messages for new members")
    @app_commands.describe(
        action="Action to perform",
        message="Welcome message (use {user.mention}, {user.name}, {guild.name}, {member.count} placeholders)",
        channel="Channel for welcome messages",
        embed_mode="Enable embed mode for welcome messages"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="enable", value="enable"),
        app_commands.Choice(name="disable", value="disable"),
        app_commands.Choice(name="set", value="set"),
        app_commands.Choice(name="test", value="test"),
        app_commands.Choice(name="view", value="view"),
        app_commands.Choice(name="channel", value="channel"),
        app_commands.Choice(name="embed", value="embed")
    ])
    async def welcome(self, interaction: discord.Interaction, action: str, message: str = None, 
                     channel: discord.TextChannel = None, embed_mode: bool = None):
        """Set welcome message for new members"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to use this command.", ephemeral=True)
            return
        
        try:
            guild_id = str(interaction.guild.id)
            
            if action == "enable":
                await interaction.response.send_message("⏳ Enabling welcome messages...", ephemeral=True)
                await self.bot.update_guild_config(guild_id, welcome_enabled=True)
                await interaction.edit_original_response(content="✅ Welcome messages enabled! Use `/welcome channel` to set a welcome channel.")
                
            elif action == "disable":
                await interaction.response.send_message("⏳ Disabling welcome messages...", ephemeral=True)
                await self.bot.update_guild_config(guild_id, welcome_enabled=False)
                await interaction.edit_original_response(content="❌ Welcome messages disabled.")
                
            elif action == "channel":
                if not channel:
                    await interaction.response.send_message("❌ Please specify a channel.", ephemeral=True)
                    return
                
                await interaction.response.send_message("⏳ Setting welcome channel...", ephemeral=True)
                logger.info(f"Setting welcome channel for {guild_id}: {channel.id} ({channel.name})")
                await self.bot.update_guild_config(guild_id, welcome_channel_id=str(channel.id))
                
                # Verify the update
                updated_config = await self.bot.get_guild_config(guild_id)
                logger.info(f"After channel update - welcome_channel_id: {updated_config.get('welcome_channel_id')}")
                
                await interaction.edit_original_response(content=f"✅ Welcome channel set to {channel.mention}\n**Debug:** Channel ID `{channel.id}` saved")
                
            elif action == "embed":
                if embed_mode is None:
                    await interaction.response.send_message("❌ Please specify whether to enable or disable embed mode.", ephemeral=True)
                    return
                
                await interaction.response.send_message("⏳ Updating embed mode...", ephemeral=True)
                logger.info(f"Setting welcome embed mode for {guild_id}: {embed_mode}")
                await self.bot.update_guild_config(guild_id, welcome_embed=embed_mode)
                
                # Verify the update
                updated_config = await self.bot.get_guild_config(guild_id)
                logger.info(f"After embed update - welcome_embed: {updated_config.get('welcome_embed')}")
                
                status = "enabled" if embed_mode else "disabled"
                await interaction.edit_original_response(content=f"✅ Welcome embed mode {status}.\n**Debug:** Embed mode set to `{embed_mode}`")
                
            elif action == "set":
                if not message:
                    await interaction.response.send_message("❌ Please provide a welcome message.", ephemeral=True)
                    return
                
                await interaction.response.send_message("⏳ Updating welcome message...", ephemeral=True)
                await self.bot.update_guild_config(guild_id, welcome_message=message)
                await interaction.edit_original_response(content=f"✅ Welcome message updated:\n```{message}```")
                
            elif action == "test":
                await interaction.response.send_message("⏳ Generating welcome message preview...", ephemeral=True)
                config = await self.bot.get_guild_config(guild_id)
                welcome_msg = config.get('welcome_message') or 'Welcome {user.mention} to {guild.name}!'
                
                # Replace placeholders for test
                test_message = str(welcome_msg).replace("{user.mention}", interaction.user.mention)
                test_message = test_message.replace("{user.name}", interaction.user.name)
                test_message = test_message.replace("{guild.name}", interaction.guild.name)
                test_message = test_message.replace("{member.count}", str(interaction.guild.member_count))
                test_message = test_message.replace("{user.id}", str(interaction.user.id))
                test_message = test_message.replace("{user.display_name}", interaction.user.display_name)
                
                embed = discord.Embed(
                    title="🎉 Welcome Message Test",
                    description=test_message,
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                embed.add_field(name="📅 Account Created", value=discord.utils.format_dt(interaction.user.created_at, "R"), inline=True)
                embed.add_field(name="🆔 User ID", value=f"`{interaction.user.id}`", inline=True)
                embed.add_field(name="👥 Member Count", value=f"**{interaction.guild.member_count}**", inline=True)
                embed.set_footer(text=f"Member #{interaction.guild.member_count}", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                
                await interaction.edit_original_response(content="**Welcome Message Preview:**", embed=embed)
                
            elif action == "view":
                await interaction.response.send_message("⏳ Loading welcome configuration...", ephemeral=True)
                config = await self.bot.get_guild_config(guild_id)
                welcome_enabled = config.get('welcome_enabled', False)
                welcome_msg = config.get('welcome_message', 'Welcome {user.mention} to {guild.name}!')
                welcome_embed = config.get('welcome_embed', False)
                channel_id = config.get('welcome_channel_id')
                
                # Log the raw config for debugging
                logger.info(f"Raw config for {guild_id}: {config}")
                
                # Properly format channel info
                if channel_id:
                    try:
                        # Validate channel exists and bot can access it
                        channel = interaction.guild.get_channel(int(channel_id))
                        if channel:
                            channel_info = f"<#{channel_id}> (#{channel.name})"
                        else:
                            channel_info = f"<#{channel_id}> ⚠️ (Channel not found)"
                    except (ValueError, TypeError):
                        channel_info = "⚠️ Invalid channel ID"
                else:
                    channel_info = "❌ Not set"
                
                status = "✅ Enabled" if welcome_enabled else "❌ Disabled"
                embed_status = "✅ Enabled" if welcome_embed else "❌ Disabled"
                
                embed = discord.Embed(
                    title="🎉 Welcome Configuration",
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Status", value=status, inline=True)
                embed.add_field(name="Channel", value=channel_info, inline=True)
                embed.add_field(name="Embed Mode", value=embed_status, inline=True)
                embed.add_field(name="Message", value=f"```{welcome_msg[:500]}{'...' if len(welcome_msg) > 500 else ''}```", inline=False)
                embed.add_field(name="Available Placeholders", value="`{user.mention}`, `{user.name}`, `{user.display_name}`, `{user.id}`, `{guild.name}`, `{member.count}`", inline=False)
                embed.add_field(name="Raw Debug Values", value=f"**Enabled:** `{welcome_enabled}`\n**Channel ID:** `{channel_id}`\n**Embed:** `{welcome_embed}`\n**Message Length:** `{len(welcome_msg)}`", inline=False)
                
                await interaction.edit_original_response(content=None, embed=embed)
            
            # Log command usage
            parameters = {"action": action}
            if message:
                parameters["message"] = message[:50] + "..." if len(message) > 50 else message
            if channel:
                parameters["channel"] = channel.mention
            if embed_mode is not None:
                parameters["embed_mode"] = embed_mode
            await self.bot.log_command_usage(interaction, "welcome", parameters)
                
        except Exception as e:
            logger.error(f"Error with welcome command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Failed to process welcome command. Please try again.", ephemeral=True)
                else:
                    await interaction.edit_original_response(content="❌ Failed to process welcome command. Please try again.")
            except:
                try:
                    await interaction.followup.send("❌ Failed to process welcome command. Please try again.", ephemeral=True)
                except:
                    pass
    
    @app_commands.command(name="settings", description="View comprehensive server settings")
    async def settings(self, interaction: discord.Interaction):
        """View comprehensive server settings"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to use this command.", ephemeral=True)
            return
        
        try:
            # Defer the response to prevent timeout issues
            await interaction.response.defer(ephemeral=True)
            
            guild_id = str(interaction.guild.id)
            
            # Get basic guild config
            config = await self.bot.get_guild_config(guild_id)
            
            # Get automod settings from database
            automod_settings = {}
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    # Get automod settings
                    automod_result = await conn.fetchrow('''
                        SELECT automod_spam_enabled, automod_spam_limit, automod_spam_window,
                               automod_links_enabled, automod_badwords_enabled, automod_badwords_strict
                        FROM guilds WHERE id = $1
                    ''', guild_id)
                    
                    if automod_result:
                        automod_settings = dict(automod_result)
                    
                    # Get role settings
                    role_result = await conn.fetchrow('''
                        SELECT moderator_role_id, admin_role_id
                        FROM guilds WHERE id = $1
                    ''', guild_id)
                    
                    if role_result:
                        config.update(dict(role_result))
            
            embed = discord.Embed(
                title=f"🛠️ Server Settings - {interaction.guild.name}",
                description="Complete overview of your server configuration",
                color=0x00FFFF,
                timestamp=datetime.utcnow()
            )
            
            # Basic Settings
            basic_settings = []
            basic_settings.append(f"**Prefix:** `{config.get('prefix', '!')}`")
            basic_settings.append(f"**Moderation:** {'✅ Enabled' if config.get('moderation_enabled', True) else '❌ Disabled'}")
            
            embed.add_field(
                name="⚙️ Basic Settings",
                value="\n".join(basic_settings),
                inline=False
            )
            
            # Channels Configuration
            channels_config = []
            welcome_channel = f"<#{config.get('welcome_channel_id')}>" if config.get('welcome_channel_id') else "❌ Not set"
            log_channel = f"<#{config.get('log_channel_id')}>" if config.get('log_channel_id') else "❌ Not set"
            error_log_channel = f"<#{config.get('error_log_channel_id')}>" if config.get('error_log_channel_id') else "❌ Not set"
            
            channels_config.append(f"**Welcome Channel:** {welcome_channel}")
            channels_config.append(f"**Log Channel:** {log_channel}")
            channels_config.append(f"**Error Log Channel:** {error_log_channel}")
            
            embed.add_field(
                name="📋 Channel Configuration",
                value="\n".join(channels_config),
                inline=False
            )
            
            # Role Configuration (including new hierarchical roles)
            roles_config = []
            
            # Mod role (basic moderation)
            if config.get('moderator_role_id'):
                mod_role = interaction.guild.get_role(int(config.get('moderator_role_id')))
                roles_config.append(f"**Moderation Role:** {mod_role.mention if mod_role else '⚠️ Role not found'}")
            else:
                roles_config.append("**Moderation Role:** ❌ Not set (using Discord defaults)")
            
            # Admin role (advanced moderation)
            if config.get('admin_role_id'):
                admin_role = interaction.guild.get_role(int(config.get('admin_role_id')))
                roles_config.append(f"**Admin Role:** {admin_role.mention if admin_role else '⚠️ Role not found'}")
            else:
                roles_config.append("**Admin Role:** ❌ Not set (using Discord defaults)")
            
            # Auto-role
            autorole_role = f"<@&{config.get('auto_role_id')}>" if config.get('auto_role_id') else "❌ Not set"
            autorole_status = "✅ Enabled" if config.get('auto_role_enabled', False) else "❌ Disabled"
            roles_config.append(f"**Auto-Role:** {autorole_role} ({autorole_status})")
            
            embed.add_field(
                name="👥 Role Configuration",
                value="\n".join(roles_config),
                inline=False
            )
            
            # AutoMod Settings (detailed status)
            automod_status = []
            
            # Spam Protection
            spam_enabled = automod_settings.get('automod_spam_enabled', False)
            if spam_enabled:
                spam_limit = automod_settings.get('automod_spam_limit', 5)
                spam_window = automod_settings.get('automod_spam_window', 10)
                automod_status.append(f"**Spam Protection:** ✅ Enabled")
                automod_status.append(f"  └ Limit: {spam_limit} messages per {spam_window} seconds")
            else:
                automod_status.append("**Spam Protection:** ❌ Disabled")
            
            # Link Blocking
            links_enabled = automod_settings.get('automod_links_enabled', False)
            automod_status.append(f"**Link Blocking:** {'✅ Enabled' if links_enabled else '❌ Disabled'}")
            
            # Bad Words Filter
            badwords_enabled = automod_settings.get('automod_badwords_enabled', False)
            if badwords_enabled:
                strict_mode = automod_settings.get('automod_badwords_strict', False)
                automod_status.append(f"**Bad Words Filter:** ✅ Enabled")
                automod_status.append(f"  └ Strict Mode: {'✅ On' if strict_mode else '❌ Off'}")
            else:
                automod_status.append("**Bad Words Filter:** ❌ Disabled")
            
            embed.add_field(
                name="🛡️ AutoMod Protection",
                value="\n".join(automod_status),
                inline=False
            )
            
            # Welcome System
            welcome_config = []
            welcome_enabled = config.get('welcome_enabled', False)
            welcome_embed_mode = config.get('welcome_embed_mode', True)
            
            welcome_config.append(f"**Status:** {'✅ Enabled' if welcome_enabled else '❌ Disabled'}")
            if welcome_enabled:
                welcome_config.append(f"**Format:** {'Rich Embed' if welcome_embed_mode else 'Simple Message'}")
            
            embed.add_field(
                name="👋 Welcome System",
                value="\n".join(welcome_config),
                inline=True
            )
            
            # Command Permissions Summary
            permissions_summary = []
            permissions_summary.append("**Basic Moderation:** Mod Role + Admin Role")
            permissions_summary.append("  └ `/mute`, `/timeout`, `/warn`, `/untimeout`")
            permissions_summary.append("**Advanced Admin:** Admin Role Only")
            permissions_summary.append("  └ `/ban`, `/unban`, `/lock`, `/unlock`, `/slowmode`")
            
            embed.add_field(
                name="🔐 Permission Structure",
                value="\n".join(permissions_summary),
                inline=True
            )
            
            embed.set_footer(
                text=f"Requested by {interaction.user.name} • Server ID: {interaction.guild.id}",
                icon_url=interaction.user.display_avatar.url
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Log command usage
            parameters = {"guild": interaction.guild.name}
            await self.bot.log_command_usage(interaction, "settings", parameters)
            
        except Exception as e:
            logger.error(f"Error viewing settings: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Failed to load settings. Please try again.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Failed to load settings. Please try again.", ephemeral=True)
            except:
                pass
    
    @app_commands.command(name="autorole", description="Configure automatic role assignment for new members")
    @app_commands.describe(
        action="Action to perform",
        role="Role to assign to new members"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="set", value="set"),
        app_commands.Choice(name="enable", value="enable"),
        app_commands.Choice(name="disable", value="disable"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="view", value="view")
    ])
    async def autorole(self, interaction: discord.Interaction, action: str, role: discord.Role = None):
        """Configure automatic role assignment for new members"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to use this command.", ephemeral=True)
            return
        
        try:
            guild_id = str(interaction.guild.id)
            config = await self.bot.get_guild_config(guild_id)
            
            if action == "set":
                if not role:
                    await interaction.response.send_message("❌ Please specify a role to set as auto-role.", ephemeral=True)
                    return
                
                # Check if the role is manageable by the bot
                if role.position >= interaction.guild.me.top_role.position:
                    await interaction.response.send_message("❌ I cannot assign this role as it's higher than or equal to my highest role.", ephemeral=True)
                    return
                
                # Check if the role is @everyone
                if role.id == interaction.guild.id:
                    await interaction.response.send_message("❌ Cannot set @everyone as auto-role.", ephemeral=True)
                    return
                
                await self.bot.update_guild_config(guild_id, auto_role_id=str(role.id), auto_role_enabled=True)
                
                embed = discord.Embed(
                    title="✅ Auto-Role Configured",
                    description=f"New members will automatically receive the {role.mention} role.",
                    color=0x00FF00,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Role", value=role.mention, inline=True)
                embed.add_field(name="Status", value="✅ Enabled", inline=True)
                embed.set_footer(text=f"Set by {interaction.user}", icon_url=interaction.user.display_avatar.url)
                
                await interaction.response.send_message(embed=embed)
                
                # Log command usage
                parameters = {"action": action, "role": role.name}
                await self.bot.log_command_usage(interaction, "autorole", parameters)
                
            elif action == "enable":
                if not config.get('auto_role_id'):
                    await interaction.response.send_message("❌ No auto-role has been set. Use `/autorole set @role` first.", ephemeral=True)
                    return
                
                await self.bot.update_guild_config(guild_id, auto_role_enabled=True)
                
                role_id = config.get('auto_role_id')
                role_obj = interaction.guild.get_role(int(role_id))
                role_mention = role_obj.mention if role_obj else f"<@&{role_id}>"
                
                embed = discord.Embed(
                    title="✅ Auto-Role Enabled",
                    description=f"Auto-role feature has been enabled. New members will receive {role_mention}.",
                    color=0x00FF00,
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"Enabled by {interaction.user}", icon_url=interaction.user.display_avatar.url)
                
                await interaction.response.send_message(embed=embed)
                
                # Log command usage
                parameters = {"action": action}
                await self.bot.log_command_usage(interaction, "autorole", parameters)
                
            elif action == "disable":
                await self.bot.update_guild_config(guild_id, auto_role_enabled=False)
                
                embed = discord.Embed(
                    title="❌ Auto-Role Disabled",
                    description="Auto-role feature has been disabled. New members will not receive automatic roles.",
                    color=0xFF4444,
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"Disabled by {interaction.user}", icon_url=interaction.user.display_avatar.url)
                
                await interaction.response.send_message(embed=embed)
                
                # Log command usage
                parameters = {"action": action}
                await self.bot.log_command_usage(interaction, "autorole", parameters)
                
            elif action == "remove":
                await self.bot.update_guild_config(guild_id, auto_role_id=None, auto_role_enabled=False)
                
                embed = discord.Embed(
                    title="🗑️ Auto-Role Removed",
                    description="Auto-role configuration has been completely removed.",
                    color=0xFF4444,
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"Removed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
                
                await interaction.response.send_message(embed=embed)
                
                # Log command usage
                parameters = {"action": action}
                await self.bot.log_command_usage(interaction, "autorole", parameters)
                
            elif action == "view":
                role_id = config.get('auto_role_id')
                enabled = config.get('auto_role_enabled', False)
                
                embed = discord.Embed(
                    title="📋 Auto-Role Configuration",
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                
                if role_id:
                    role_obj = interaction.guild.get_role(int(role_id))
                    if role_obj:
                        embed.add_field(name="Role", value=role_obj.mention, inline=True)
                        embed.add_field(name="Role Name", value=role_obj.name, inline=True)
                        embed.add_field(name="Role ID", value=role_id, inline=True)
                    else:
                        embed.add_field(name="Role", value=f"⚠️ Role not found (ID: {role_id})", inline=False)
                else:
                    embed.add_field(name="Role", value="Not configured", inline=False)
                
                status_emoji = "✅" if enabled else "❌"
                status_text = "Enabled" if enabled else "Disabled"
                embed.add_field(name="Status", value=f"{status_emoji} {status_text}", inline=True)
                
                if role_id and enabled:
                    embed.add_field(name="Bot Can Assign", value="✅ Yes" if role_obj and role_obj.position < interaction.guild.me.top_role.position else "❌ No", inline=True)
                
                embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
                
                await interaction.response.send_message(embed=embed)
                
                # Log command usage
                parameters = {"action": action}
                await self.bot.log_command_usage(interaction, "autorole", parameters)
                
        except Exception as e:
            logger.error(f"Error with autorole command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Failed to configure auto-role. Please try again.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Failed to configure auto-role. Please try again.", ephemeral=True)
            except:
                pass


    @app_commands.command(name="errorlog", description="Configure error logging for this server")
    @app_commands.describe(
        action="Action to perform",
        channel="Channel to send error logs to"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="enable", value="enable"),
        app_commands.Choice(name="disable", value="disable"),
        app_commands.Choice(name="set", value="set"),
        app_commands.Choice(name="view", value="view")
    ])
    async def errorlog(self, interaction: discord.Interaction, action: str, channel: discord.TextChannel = None):
        """Configure error logging channel"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to use this command.", ephemeral=True)
            return
        
        try:
            guild_id = str(interaction.guild.id)
            guild_config = await self.bot.get_guild_config(guild_id)
            
            if action == "enable":
                if not guild_config.get('error_log_channel_id'):
                    await interaction.response.send_message("❌ Please set an error log channel first using `/errorlog set #channel`.", ephemeral=True)
                    return
                
                await self.bot.update_guild_config(guild_id, error_logging_enabled=True)
                channel = self.bot.get_channel(int(guild_config['error_log_channel_id']))
                await interaction.response.send_message(f"✅ Error logging enabled! Errors will be sent to {channel.mention}.", ephemeral=True)
                
            elif action == "disable":
                await self.bot.update_guild_config(guild_id, error_logging_enabled=False)
                await interaction.response.send_message("❌ Error logging disabled.", ephemeral=True)
                
            elif action == "set":
                if not channel:
                    await interaction.response.send_message("❌ Please specify a channel for error logging.", ephemeral=True)
                    return
                
                await self.bot.update_guild_config(guild_id, error_log_channel_id=str(channel.id), error_logging_enabled=True)
                await interaction.response.send_message(f"✅ Error logging channel set to {channel.mention} and enabled!", ephemeral=True)
                
            elif action == "view":
                error_channel_id = guild_config.get('error_log_channel_id')
                error_enabled = guild_config.get('error_logging_enabled', False)
                
                embed = discord.Embed(
                    title="🚨 Error Logging Configuration",
                    color=0xFF4444,
                    timestamp=datetime.utcnow()
                )
                
                if error_channel_id:
                    channel = self.bot.get_channel(int(error_channel_id))
                    embed.add_field(
                        name="Error Log Channel",
                        value=channel.mention if channel else f"<#{error_channel_id}> (Not found)",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="Error Log Channel",
                        value="Not configured",
                        inline=False
                    )
                
                embed.add_field(
                    name="Status",
                    value="🟢 Enabled" if error_enabled else "🔴 Disabled",
                    inline=False
                )
                
                embed.set_footer(text=f"Server: {interaction.guild.name}")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Log command usage
            if not interaction.response.is_done():
                parameters = {"action": action}
                if channel:
                    parameters["channel"] = channel.name
                await self.bot.log_command_usage(interaction, "errorlog", parameters)
                    
        except Exception as e:
            logger.error(f"Error configuring error logging: {e}")
            await self.bot.log_error(interaction.guild.id, "ErrorLog Command Error", str(e), "errorlog command")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Failed to configure error logging. Please try again.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Failed to configure error logging. Please try again.", ephemeral=True)
            except:
                pass

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))