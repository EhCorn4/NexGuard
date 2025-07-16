import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='commands', description='List all available bot commands with descriptions')
    async def commands_list(self, interaction: discord.Interaction):
        """Display all available bot commands organized by category"""
        
        # Define command categories and their commands
        command_categories = {
            "🛡️ Moderation Commands": [
                ("ban", "Ban a member from the server"),
                ("kick", "Kick a member from the server"),
                ("mute", "Mute a member for a specified duration"),
                ("unmute", "Unmute a previously muted member"),
                ("timeout", "Put a member in timeout"),
                ("warn", "Issue a warning to a member"),
                ("purge", "Delete multiple messages at once"),
                ("unban", "Unban a previously banned user"),
                ("slowmode", "Set slowmode for a channel"),
                ("lock", "Lock a channel to prevent messages"),
            ],
            "🎫 Ticket System": [
                ("ticket-setup", "Configure the ticket system with custom settings"),
                ("ticket", "Create a new support ticket"),
                ("ticket-list", "List all active tickets (Admin only)"),
                ("ticket-close", "Close a ticket (Admin only)"),
                ("ticket-info", "Get information about a ticket"),
                ("ticket-cleanup", "Clean up deleted ticket channels (Admin only)"),
                ("transcript", "Generate a transcript of the current channel"),
            ],
            "🔧 Utilities": [
                ("ping", "Check the bot's latency and response time"),
                ("userinfo", "Get detailed information about a user"),
                ("serverinfo", "Get detailed information about the server"),
                ("avatar", "Display a user's avatar"),
                ("help", "Get detailed help for a specific command"),
                ("commands", "Show this command list"),
                ("embed", "Create custom embeds with interactive builder"),
                ("embed-json", "Create embeds from JSON code"),
                ("embed-help", "Get help for using the embed builder"),
            ],
            "⚙️ Administration": [
                ("prefix", "View or change the bot's command prefix"),
                ("modrole", "Set the minimum role required for moderation commands"),
                ("resetmodrole", "Reset moderation role to default permissions"),
                ("changelog", "Configure automatic changelog posting"),
                ("changelog-disable", "Disable automatic changelog posts"),
                ("changelog-test", "Send a test changelog post"),
            ],
        }
        
        # Create main embed
        embed = discord.Embed(
            title="📋 NexGuard Bot Commands",
            description="Here are all available slash commands organized by category:",
            color=discord.Color.blue()
        )
        
        # Add each category as a field
        for category, command_list in command_categories.items():
            command_text = ""
            for cmd_name, cmd_desc in command_list:
                command_text += f"**/{cmd_name}** - {cmd_desc}\n"
            
            embed.add_field(
                name=category,
                value=command_text,
                inline=False
            )
        
        # Add footer information
        embed.add_field(
            name="ℹ️ Usage Information",
            value="• All commands use Discord's slash command system\n• Type `/` and start typing a command name to see options\n• Some commands require specific permissions\n• Use `/help <command>` for detailed help on specific commands",
            inline=False
        )
        
        embed.set_footer(text=f"NexGuard Bot | Total Commands: {sum(len(cmds) for cmds in command_categories.values())} | Use /help <command> for detailed help")
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        logger.info(f"Commands list requested by {interaction.user} in {interaction.guild.name}")

async def setup(bot):
    await bot.add_cog(CommandsCog(bot))