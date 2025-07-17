"""
Dashboard Integration Commands
Commands for interacting with the NexGuard web dashboard
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.api_integration import api
from utils.checks import is_moderator

logger = logging.getLogger(__name__)

class Dashboard(commands.Cog):
    """Dashboard integration commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="config", description="View current server configuration from dashboard")
    @app_commands.describe(
        show_private="Show configuration in a private message (default: False)"
    )
    async def config(self, interaction: discord.Interaction, show_private: bool = False):
        """Display current server configuration"""
        await interaction.response.defer(ephemeral=show_private)
        
        try:
            config = api.get_server_config(str(interaction.guild.id))
            
            if not config:
                embed = discord.Embed(
                    title="⚠️ Configuration Not Found",
                    description="No configuration found for this server. Using default settings.",
                    color=0xff9900
                )
                embed.add_field(
                    name="Dashboard", 
                    value=f"[Configure Settings]({api.base_url}/guild/{interaction.guild.id})",
                    inline=False
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🛡️ NexGuard Server Configuration",
                description=f"Configuration for **{interaction.guild.name}**",
                color=0x5865f2
            )
            
            # Add configuration fields
            embed.add_field(
                name="🔨 Moderation", 
                value="✅ Enabled" if config.get("moderationEnabled", False) else "❌ Disabled", 
                inline=True
            )
            embed.add_field(
                name="🤖 Auto-Mod", 
                value="✅ Enabled" if config.get("autoModEnabled", False) else "❌ Disabled", 
                inline=True
            )
            embed.add_field(
                name="🛡️ Spam Protection", 
                value="✅ Enabled" if config.get("spamProtection", False) else "❌ Disabled", 
                inline=True
            )
            embed.add_field(
                name="👋 Welcome Messages", 
                value="✅ Enabled" if config.get("welcomeEnabled", False) else "❌ Disabled", 
                inline=True
            )
            embed.add_field(
                name="⚙️ Custom Commands", 
                value="✅ Enabled" if config.get("customCommandsEnabled", False) else "❌ Disabled", 
                inline=True
            )
            embed.add_field(
                name="📊 Dashboard", 
                value=f"[Configure Settings]({api.base_url}/guild/{interaction.guild.id})",
                inline=False
            )
            
            embed.set_footer(text="Use the dashboard link to modify these settings")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in config command: {e}")
            await interaction.followup.send(
                "❌ An error occurred while fetching the configuration.",
                ephemeral=True
            )
    
    @app_commands.command(name="addcmd", description="Add a custom command via Discord")
    @app_commands.describe(
        name="Name of the custom command",
        response="Response text for the command"
    )
    @is_moderator()
    async def addcmd(self, interaction: discord.Interaction, name: str, response: str):
        """Add a custom command"""
        await interaction.response.defer()
        
        try:
            result = api.create_custom_command(
                str(interaction.guild.id), 
                name, 
                response, 
                str(interaction.user.id)
            )
            
            if result:
                embed = discord.Embed(
                    title="✅ Custom Command Added",
                    description=f"Custom command `/{name}` has been created successfully!",
                    color=0x00ff00
                )
                embed.add_field(name="Command", value=f"`/{name}`", inline=True)
                embed.add_field(name="Response", value=response[:100] + "..." if len(response) > 100 else response, inline=True)
                embed.add_field(name="Created By", value=interaction.user.mention, inline=True)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(
                    f"❌ Failed to create command `/{name}`. Please check the dashboard for more details.",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Error in addcmd command: {e}")
            await interaction.followup.send(
                "❌ An error occurred while creating the custom command.",
                ephemeral=True
            )
    
    @app_commands.command(name="dashboard", description="Get the dashboard link for this server")
    async def dashboard(self, interaction: discord.Interaction):
        """Provide dashboard link"""
        embed = discord.Embed(
            title="🌐 NexGuard Dashboard",
            description="Access the web dashboard to configure your server settings",
            color=0x5865f2
        )
        
        embed.add_field(
            name="📊 Main Dashboard", 
            value=f"[Open Dashboard]({api.base_url}/)",
            inline=False
        )
        embed.add_field(
            name="⚙️ Server Settings", 
            value=f"[Configure {interaction.guild.name}]({api.base_url}/guild/{interaction.guild.id})",
            inline=False
        )
        embed.add_field(
            name="🤖 AutoMod Settings", 
            value=f"[AutoMod Configuration]({api.base_url}/guild/{interaction.guild.id}/automod)",
            inline=False
        )
        embed.add_field(
            name="👋 Welcome Settings", 
            value=f"[Welcome Configuration]({api.base_url}/guild/{interaction.guild.id}/welcome)",
            inline=False
        )
        
        embed.set_footer(text="Use the dashboard to easily configure NexGuard settings")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="sync-config", description="Sync configuration from dashboard")
    @is_moderator()
    async def sync_config(self, interaction: discord.Interaction):
        """Sync configuration from dashboard"""
        await interaction.response.defer()
        
        try:
            config = api.get_server_config(str(interaction.guild.id))
            
            if config:
                embed = discord.Embed(
                    title="🔄 Configuration Synced",
                    description="Successfully synchronized configuration from dashboard",
                    color=0x00ff00
                )
                embed.add_field(name="Status", value="✅ Sync Complete", inline=True)
                embed.add_field(name="Last Updated", value="Just now", inline=True)
            else:
                embed = discord.Embed(
                    title="⚠️ Sync Warning",
                    description="No configuration found on dashboard. Using default settings.",
                    color=0xff9900
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in sync_config command: {e}")
            await interaction.followup.send(
                "❌ An error occurred while syncing configuration.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Dashboard(bot))