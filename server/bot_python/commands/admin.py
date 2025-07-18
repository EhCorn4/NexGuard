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
        app_commands.Choice(name="logging", value="logging")
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
                    
        except Exception as e:
            logger.error(f"Error configuring server: {e}")
            await interaction.response.send_message("❌ Failed to update configuration. Please try again.", ephemeral=True)
    
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
                await self.bot.update_guild_config(guild_id, welcome_enabled=True)
                await interaction.response.send_message("✅ Welcome messages enabled! Use `/welcome channel` to set a welcome channel.", ephemeral=True)
                
            elif action == "disable":
                await self.bot.update_guild_config(guild_id, welcome_enabled=False)
                await interaction.response.send_message("❌ Welcome messages disabled.", ephemeral=True)
                
            elif action == "channel":
                if not channel:
                    await interaction.response.send_message("❌ Please specify a channel.", ephemeral=True)
                    return
                
                await self.bot.update_guild_config(guild_id, welcome_channel_id=str(channel.id))
                await interaction.response.send_message(f"✅ Welcome channel set to {channel.mention}", ephemeral=True)
                
            elif action == "embed":
                if embed_mode is None:
                    await interaction.response.send_message("❌ Please specify whether to enable or disable embed mode.", ephemeral=True)
                    return
                
                await self.bot.update_guild_config(guild_id, welcome_embed=embed_mode)
                status = "enabled" if embed_mode else "disabled"
                await interaction.response.send_message(f"✅ Welcome embed mode {status}.", ephemeral=True)
                
            elif action == "set":
                if not message:
                    await interaction.response.send_message("❌ Please provide a welcome message.", ephemeral=True)
                    return
                
                await self.bot.update_guild_config(guild_id, welcome_message=message)
                await interaction.response.send_message(f"✅ Welcome message updated:\n```{message}```", ephemeral=True)
                
            elif action == "test":
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
                
                await interaction.response.send_message("**Welcome Message Preview:**", embed=embed, ephemeral=True)
                
            elif action == "view":
                config = await self.bot.get_guild_config(guild_id)
                welcome_enabled = config.get('welcome_enabled', False)
                welcome_msg = config.get('welcome_message', 'Welcome {user.mention} to {guild.name}!')
                welcome_embed = config.get('welcome_embed', False)
                channel_id = config.get('welcome_channel_id')
                
                channel_info = f"<#{channel_id}>" if channel_id else "Not set"
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
                embed.add_field(name="Message", value=f"```{welcome_msg}```", inline=False)
                embed.add_field(name="Available Placeholders", value="`{user.mention}`, `{user.name}`, `{user.display_name}`, `{user.id}`, `{guild.name}`, `{member.count}`", inline=False)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error with welcome command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Failed to process welcome command. Please try again.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Failed to process welcome command. Please try again.", ephemeral=True)
            except:
                pass
    
    @app_commands.command(name="settings", description="View server settings")
    async def settings(self, interaction: discord.Interaction):
        """View server settings"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to use this command.", ephemeral=True)
            return
        
        try:
            config = await self.bot.get_guild_config(str(interaction.guild.id))
            
            embed = discord.Embed(
                title=f"Server Settings - {interaction.guild.name}",
                color=0x00FFFF,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Prefix", value=config.get('prefix', '!'), inline=True)
            embed.add_field(name="Moderation", value="✅ Enabled" if config.get('moderation_enabled', True) else "❌ Disabled", inline=True)
            embed.add_field(name="Automod", value="✅ Enabled" if config.get('automod_enabled', False) else "❌ Disabled", inline=True)
            
            welcome_channel = f"<#{config.get('welcome_channel_id')}>" if config.get('welcome_channel_id') else "Not set"
            embed.add_field(name="Welcome Channel", value=welcome_channel, inline=True)
            
            log_channel = f"<#{config.get('log_channel_id')}>" if config.get('log_channel_id') else "Not set"
            embed.add_field(name="Log Channel", value=log_channel, inline=True)
            
            mod_role = f"<@&{config.get('mod_role_id')}>" if config.get('mod_role_id') else "Not set"
            embed.add_field(name="Mod Role", value=mod_role, inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error viewing settings: {e}")
            await interaction.response.send_message("❌ Failed to load settings. Please try again.", ephemeral=True)
    


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))