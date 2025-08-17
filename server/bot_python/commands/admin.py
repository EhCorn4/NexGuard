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
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
            
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
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
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
            
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
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
            
            # Get additional settings from database (safely handle missing columns)
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    # Get all available guild data
                    guild_result = await conn.fetchrow('''
                        SELECT * FROM guilds WHERE id = $1
                    ''', guild_id)
                    
                    if guild_result:
                        # Merge guild data into config
                        guild_data = dict(guild_result)
                        config.update(guild_data)
            
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
            
            # Mod role (basic moderation) - check both possible column names
            mod_role_id = config.get('moderator_role_id') or config.get('mod_role_id')
            if mod_role_id:
                mod_role = interaction.guild.get_role(int(mod_role_id))
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
            
            # AutoMod Settings - Show ALL automod features
            automod_status = []
            
            # Get JSON-based automod config
            automod_config = {}
            if config.get('automod_config'):
                try:
                    automod_config = json.loads(config.get('automod_config', '{}'))
                except json.JSONDecodeError:
                    pass
            
            # Check JSON-based modules
            spam_enabled = automod_config.get('spam', {}).get('enabled', False)
            links_enabled = automod_config.get('links', {}).get('enabled', False)
            badwords_enabled = automod_config.get('badwords', {}).get('enabled', False)
            
            # Check database column-based modules
            caps_enabled = config.get('automod_caps_enabled', False)
            mentions_enabled = config.get('automod_mentions_enabled', False)
            
            # Display all automod modules
            automod_status.append(f"**Spam Protection:** {'✅ Enabled' if spam_enabled else '❌ Disabled'}")
            if spam_enabled:
                max_msg = automod_config.get('spam', {}).get('max_messages', 5)
                time_window = automod_config.get('spam', {}).get('time_window', 5)
                automod_status.append(f"  └ Limit: {max_msg} messages per {time_window}s")
            
            automod_status.append(f"**Link Filtering:** {'✅ Enabled' if links_enabled else '❌ Disabled'}")
            if links_enabled:
                block_invites = automod_config.get('links', {}).get('block_invites', True)
                block_urls = automod_config.get('links', {}).get('block_urls', True)
                automod_status.append(f"  └ Invites: {'✅ Blocked' if block_invites else '❌ Allowed'}, URLs: {'✅ Blocked' if block_urls else '❌ Allowed'}")
            
            automod_status.append(f"**Bad Words Filter:** {'✅ Enabled' if badwords_enabled else '❌ Disabled'}")
            if badwords_enabled:
                strict_mode = automod_config.get('badwords', {}).get('strict', False)
                custom_words_count = len(automod_config.get('badwords', {}).get('custom_words', []))
                automod_status.append(f"  └ Strict Mode: {'✅ On' if strict_mode else '❌ Off'}, Custom Words: {custom_words_count}")
            
            automod_status.append(f"**Caps Lock Filter:** {'✅ Enabled' if caps_enabled else '❌ Disabled'}")
            if caps_enabled:
                threshold = config.get('automod_caps_threshold', 70)
                automod_status.append(f"  └ Threshold: {threshold}% caps required")
            
            automod_status.append(f"**Mention Limits:** {'✅ Enabled' if mentions_enabled else '❌ Disabled'}")
            if mentions_enabled:
                limit = config.get('automod_mentions_limit', 5)
                automod_status.append(f"  └ Limit: {limit} mentions per message")
            
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
                text=f"Server ID: {interaction.guild.id}",
                icon_url=None
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
                embed.set_footer(text="Admin Role Configuration", icon_url=None)
                
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
                embed.set_footer(text="Automod Command Enabled", icon_url=None)
                
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
                embed.set_footer(text="Automod Command Disabled", icon_url=None)
                
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
                embed.set_footer(text="Admin Role Removed", icon_url=None)
                
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
                
                embed.set_footer(text="Auto-Role Configuration", icon_url=None)
                
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

    @app_commands.command(name="botlogs", description="Automatically set up all bot logging channels and configure them")
    @app_commands.describe(
        action="Action to perform with bot logs setup"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="setup", value="setup"),
        app_commands.Choice(name="view", value="view"),
        app_commands.Choice(name="cleanup", value="cleanup")
    ])
    async def botlogs(self, interaction: discord.Interaction, action: str = "setup"):
        """Automatically set up all bot logging channels and configure them"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to use this command.", ephemeral=True)
            return
        
        try:
            guild = interaction.guild
            guild_id = str(guild.id)
            
            if action == "setup":
                # Defer the response as this will take some time
                await interaction.response.defer(ephemeral=True)
                
                # Check if bot has necessary permissions
                bot_member = guild.get_member(self.bot.user.id)
                if not bot_member.guild_permissions.manage_channels:
                    await interaction.followup.send("❌ I need 'Manage Channels' permission to set up logging channels.", ephemeral=True)
                    return
                
                # Define all log channel types and their descriptions
                log_channels = [
                    ("general-logs", "general_log_channel_id", "📋 General bot events and command usage"),
                    ("member-logs", "member_log_channel_id", "👥 Member joins, leaves, and profile updates"),
                    ("message-logs", "message_log_channel_id", "💬 Message edits, deletions, and events"),
                    ("voice-logs", "voice_log_channel_id", "🔊 Voice channel joins, leaves, and events"),
                    ("channel-logs", "channel_log_channel_id", "🏗️ Channel creation, deletion, and modifications"),
                    ("role-logs", "role_log_channel_id", "🎭 Role creation, deletion, and permission changes"),
                    ("moderation-logs", "moderation_log_channel_id", "🛡️ Moderation actions and automod events")
                ]
                
                created_channels = []
                setup_errors = []
                
                # Check if "Bot Logs" category exists, create if not
                category = None
                for cat in guild.categories:
                    if cat.name.lower() == "bot logs":
                        category = cat
                        break
                
                if not category:
                    try:
                        category = await guild.create_category(
                            "Bot Logs",
                            reason="NexGuard bot logs setup"
                        )
                        created_channels.append(f"📁 Created category: **{category.name}**")
                    except discord.Forbidden:
                        await interaction.followup.send("❌ I don't have permission to create categories.", ephemeral=True)
                        return
                    except Exception as e:
                        await interaction.followup.send(f"❌ Failed to create Bot Logs category: {e}", ephemeral=True)
                        return
                
                # Create or find log channels and configure them with eventlog system
                for channel_name, db_column, description in log_channels:
                    try:
                        # Check if channel already exists
                        existing_channel = None
                        for channel in guild.text_channels:
                            if channel.name == channel_name and channel.category == category:
                                existing_channel = channel
                                break
                        
                        target_channel = None
                        if existing_channel:
                            target_channel = existing_channel
                            created_channels.append(f"✅ Found existing: {existing_channel.mention}")
                        else:
                            # Create new channel
                            new_channel = await guild.create_text_channel(
                                channel_name,
                                category=category,
                                topic=description,
                                reason="NexGuard bot logs setup"
                            )
                            target_channel = new_channel
                            created_channels.append(f"🆕 Created: {new_channel.mention}")
                        
                        # Configure the channel using eventlog system (same as /eventlog command)
                        if target_channel:
                            # Use the exact same database operation as /eventlog command
                            async with self.bot.db_pool.acquire() as conn:
                                await conn.execute(f"""
                                    INSERT INTO guild_settings (guild_id, {db_column})
                                    VALUES ($1, $2)
                                    ON CONFLICT (guild_id) DO UPDATE SET
                                    {db_column} = EXCLUDED.{db_column}
                                """, str(guild.id), target_channel.id)
                            
                            # Extract log type name for display (remove _log_channel_id suffix)
                            log_type_display = db_column.replace('_log_channel_id', '').replace('_', ' ').title()
                            created_channels.append(f"⚙️ Configured {log_type_display} logging to {target_channel.mention}")
                            
                    except discord.Forbidden:
                        setup_errors.append(f"❌ No permission to create {channel_name}")
                    except Exception as e:
                        setup_errors.append(f"❌ Failed to create/configure {channel_name}: {str(e)[:50]}")
                
                # Count successful configurations
                config_count = len([ch for ch in created_channels if "⚙️ Configured" in ch])
                
                # Create success embed
                embed = discord.Embed(
                    title="🎉 Bot Logs Setup Complete!",
                    description=f"Successfully configured comprehensive logging system using **eventlog integration**\n\n✅ **{config_count}/7** log types configured automatically",
                    color=0x00FF00,
                    timestamp=datetime.utcnow()
                )
                
                if created_channels:
                    # Split into channels and configurations for better readability
                    channel_actions = [ch for ch in created_channels if not ch.startswith("⚙️")]
                    config_actions = [ch for ch in created_channels if ch.startswith("⚙️")]
                    
                    if channel_actions:
                        embed.add_field(
                            name="📁 Channels & Category",
                            value="\n".join(channel_actions),
                            inline=False
                        )
                    
                    if config_actions:
                        embed.add_field(
                            name="⚙️ EventLog Configurations",
                            value="\n".join(config_actions),
                            inline=False
                        )
                
                if setup_errors:
                    embed.add_field(
                        name="⚠️ Setup Issues",
                        value="\n".join(setup_errors),
                        inline=False
                    )
                
                embed.add_field(
                    name="✨ What's Next?",
                    value="Your bot will now automatically log all events to their respective channels. Use `/eventlog view` to see all configurations, or `/eventlog set` to modify individual log channels.",
                    inline=False
                )
                
                embed.add_field(
                    name="🔗 Integration",
                    value="This setup fully integrates with the `/eventlog` command system for seamless log management.",
                    inline=False
                )
                
                embed.set_footer(text="Join Message Setup Complete", icon_url=None)
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                
                # Log command usage
                parameters = {"action": action, "channels_created": len(created_channels), "errors": len(setup_errors)}
                await self.bot.log_command_usage(interaction, "botlogs", parameters)
                
            elif action == "view":
                await interaction.response.defer(ephemeral=True)
                
                # Get current log channel configuration
                config = await self.bot.get_guild_config(guild_id)
                
                log_channels_config = [
                    ("General Logs", config.get('general_log_channel_id'), "📋"),
                    ("Member Logs", config.get('member_log_channel_id'), "👥"),
                    ("Message Logs", config.get('message_log_channel_id'), "💬"),
                    ("Voice Logs", config.get('voice_log_channel_id'), "🔊"),
                    ("Channel Logs", config.get('channel_log_channel_id'), "🏗️"),
                    ("Role Logs", config.get('role_log_channel_id'), "🎭"),
                    ("Moderation Logs", config.get('moderation_log_channel_id'), "🛡️")
                ]
                
                embed = discord.Embed(
                    title="📋 Bot Logs Configuration",
                    description="Current logging channel setup",
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                
                configured_channels = []
                missing_channels = []
                
                for log_type, channel_id, emoji in log_channels_config:
                    if channel_id:
                        channel = guild.get_channel(int(channel_id))
                        if channel:
                            configured_channels.append(f"{emoji} **{log_type}:** {channel.mention}")
                        else:
                            missing_channels.append(f"{emoji} **{log_type}:** ⚠️ Channel not found (ID: {channel_id})")
                    else:
                        missing_channels.append(f"{emoji} **{log_type}:** ❌ Not configured")
                
                if configured_channels:
                    embed.add_field(
                        name="✅ Configured Channels",
                        value="\n".join(configured_channels),
                        inline=False
                    )
                
                if missing_channels:
                    embed.add_field(
                        name="❌ Missing/Issues",
                        value="\n".join(missing_channels),
                        inline=False
                    )
                
                # Check if Bot Logs category exists
                bot_logs_category = None
                for category in guild.categories:
                    if category.name.lower() == "bot logs":
                        bot_logs_category = category
                        break
                
                if bot_logs_category:
                    embed.add_field(
                        name="📁 Category",
                        value=f"✅ **Bot Logs** category exists ({len(bot_logs_category.channels)} channels)",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="📁 Category", 
                        value="❌ **Bot Logs** category not found",
                        inline=True
                    )
                
                embed.set_footer(text="Error Log Configuration", icon_url=None)
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                
            elif action == "cleanup":
                await interaction.response.defer(ephemeral=True)
                
                # Find and remove Bot Logs category and its channels
                bot_logs_category = None
                for category in guild.categories:
                    if category.name.lower() == "bot logs":
                        bot_logs_category = category
                        break
                
                if not bot_logs_category:
                    await interaction.followup.send("❌ No 'Bot Logs' category found to cleanup.", ephemeral=True)
                    return
                
                deleted_channels = []
                cleanup_errors = []
                
                # Delete all channels in the category
                for channel in bot_logs_category.channels:
                    try:
                        await channel.delete(reason="Bot logs cleanup")
                        deleted_channels.append(f"🗑️ Deleted: #{channel.name}")
                    except Exception as e:
                        cleanup_errors.append(f"❌ Failed to delete #{channel.name}: {str(e)[:50]}")
                
                # Delete the category
                try:
                    await bot_logs_category.delete(reason="Bot logs cleanup")
                    deleted_channels.append(f"📁 Deleted category: **{bot_logs_category.name}**")
                except Exception as e:
                    cleanup_errors.append(f"❌ Failed to delete category: {str(e)[:50]}")
                
                # Clear database configuration using the same approach as eventlog
                try:
                    async with self.bot.db_pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE guild_settings 
                            SET general_log_channel_id = NULL,
                                member_log_channel_id = NULL,
                                message_log_channel_id = NULL,
                                voice_log_channel_id = NULL,
                                channel_log_channel_id = NULL,
                                role_log_channel_id = NULL,
                                moderation_log_channel_id = NULL
                            WHERE guild_id = $1
                        """, str(guild.id))
                    deleted_channels.append("🗑️ Cleared all eventlog configurations")
                except Exception as e:
                    cleanup_errors.append(f"❌ Database cleanup error: {str(e)[:50]}")
                
                embed = discord.Embed(
                    title="🧹 Bot Logs Cleanup Complete",
                    description="Removed bot logs setup",
                    color=0xFF4444,
                    timestamp=datetime.utcnow()
                )
                
                if deleted_channels:
                    embed.add_field(
                        name="🗑️ Removed",
                        value="\n".join(deleted_channels),
                        inline=False
                    )
                
                if cleanup_errors:
                    embed.add_field(
                        name="⚠️ Cleanup Issues",
                        value="\n".join(cleanup_errors),
                        inline=False
                    )
                
                embed.set_footer(text="Join Message Cleanup Complete", icon_url=None)
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                
                # Log command usage
                parameters = {"action": action, "channels_deleted": len(deleted_channels), "errors": len(cleanup_errors)}
                await self.bot.log_command_usage(interaction, "botlogs", parameters)
                
        except Exception as e:
            logger.error(f"Error with botlogs command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Failed to process bot logs command. Please try again.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Failed to process bot logs command. Please try again.", ephemeral=True)
            except:
                pass

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))