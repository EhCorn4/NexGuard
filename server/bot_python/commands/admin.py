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
    
    @app_commands.command(name="welcome", description="Set welcome message for new members")
    @app_commands.describe(
        action="Action to perform",
        message="Welcome message (use {user.mention}, {user.name}, {guild.name}, {member.count} placeholders)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="set", value="set"),
        app_commands.Choice(name="test", value="test"),
        app_commands.Choice(name="view", value="view")
    ])
    async def welcome(self, interaction: discord.Interaction, action: str, message: str = None):
        """Set welcome message for new members"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to use this command.", ephemeral=True)
            return
        
        try:
            guild_id = str(interaction.guild.id)
            
            if action == "set":
                if not message:
                    await interaction.response.send_message("❌ Please provide a welcome message.", ephemeral=True)
                    return
                
                await self.bot.update_guild_config(guild_id, welcome_message=message)
                await interaction.response.send_message(f"✅ Welcome message updated:\n```{message}```", ephemeral=True)
                
            elif action == "test":
                config = await self.bot.get_guild_config(guild_id)
                welcome_msg = config.get('welcome_message', 'Welcome {user.mention} to {guild.name}!')
                
                # Replace placeholders for test
                test_message = welcome_msg.replace("{user.mention}", interaction.user.mention)
                test_message = test_message.replace("{user.name}", interaction.user.name)
                test_message = test_message.replace("{guild.name}", interaction.guild.name)
                test_message = test_message.replace("{member.count}", str(interaction.guild.member_count))
                
                await interaction.response.send_message(f"**Welcome Message Preview:**\n{test_message}", ephemeral=True)
                
            elif action == "view":
                config = await self.bot.get_guild_config(guild_id)
                welcome_msg = config.get('welcome_message', 'Welcome {user.mention} to {guild.name}!')
                channel_id = config.get('welcome_channel_id')
                
                channel_info = f"<#{channel_id}>" if channel_id else "Not set"
                
                embed = discord.Embed(
                    title="Welcome Configuration",
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Channel", value=channel_info, inline=False)
                embed.add_field(name="Message", value=f"```{welcome_msg}```", inline=False)
                embed.add_field(name="Available Placeholders", value="`{user.mention}`, `{user.name}`, `{guild.name}`, `{member.count}`", inline=False)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error with welcome command: {e}")
            await interaction.response.send_message("❌ Failed to process welcome command. Please try again.", ephemeral=True)
    
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