import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Detailed command information
        self.command_info = {
            # Moderation Commands
            "ban": {
                "category": "🛡️ Moderation",
                "description": "Ban a member from the server",
                "usage": "/ban <member> [reason]",
                "examples": [
                    "/ban @user Spamming in chat",
                    "/ban @user Breaking server rules"
                ],
                "permissions": "Ban Members",
                "notes": "Permanently removes the user from the server. They won't be able to rejoin unless unbanned."
            },
            "kick": {
                "category": "🛡️ Moderation",
                "description": "Kick a member from the server",
                "usage": "/kick <member> [reason]",
                "examples": [
                    "/kick @user Minor rule violation",
                    "/kick @user Inappropriate behavior"
                ],
                "permissions": "Kick Members",
                "notes": "Removes the user from the server. They can rejoin with a new invite."
            },
            "mute": {
                "category": "🛡️ Moderation",
                "description": "Mute a member for a specified duration",
                "usage": "/mute <member> <duration> [reason]",
                "examples": [
                    "/mute @user 1h Excessive caps",
                    "/mute @user 30m Mild disruption"
                ],
                "permissions": "Moderate Members",
                "notes": "Temporarily prevents the user from sending messages. Duration format: 1h, 30m, 1d, etc."
            },
            "timeout": {
                "category": "🛡️ Moderation",
                "description": "Put a member in timeout using Discord's native timeout feature",
                "usage": "/timeout <member> <duration> [reason]",
                "examples": [
                    "/timeout @user 10m Disruptive behavior",
                    "/timeout @user 1h Repeated warnings"
                ],
                "permissions": "Moderate Members",
                "notes": "Uses Discord's built-in timeout feature. Max duration is 28 days."
            },
            "warn": {
                "category": "🛡️ Moderation",
                "description": "Issue a warning to a member",
                "usage": "/warn <member> <reason>",
                "examples": [
                    "/warn @user Please follow chat rules",
                    "/warn @user Inappropriate language"
                ],
                "permissions": "Moderate Members",
                "notes": "Adds a warning to the user's record. Warnings are stored in the database."
            },
            "purge": {
                "category": "🛡️ Moderation",
                "description": "Delete multiple messages at once",
                "usage": "/purge <amount> [user]",
                "examples": [
                    "/purge 10",
                    "/purge 50 @user"
                ],
                "permissions": "Manage Messages",
                "notes": "Can delete up to 100 messages. If user is specified, only their messages are deleted."
            },
            "slowmode": {
                "category": "🛡️ Moderation",
                "description": "Set slowmode for a channel",
                "usage": "/slowmode <seconds> [channel]",
                "examples": [
                    "/slowmode 30",
                    "/slowmode 0 #general"
                ],
                "permissions": "Manage Channels",
                "notes": "Sets message delay. Use 0 to disable slowmode. Max is 21600 seconds (6 hours)."
            },
            "lock": {
                "category": "🛡️ Moderation",
                "description": "Lock a channel to prevent messages",
                "usage": "/lock [channel] [reason]",
                "examples": [
                    "/lock Temporary maintenance",
                    "/lock #general Spam cleanup"
                ],
                "permissions": "Manage Channels",
                "notes": "Prevents @everyone from sending messages. Use /unlock to reverse."
            },
            
            # Ticket System
            "ticket": {
                "category": "🎫 Tickets",
                "description": "Create a new support ticket",
                "usage": "/ticket",
                "examples": ["/ticket"],
                "permissions": "None",
                "notes": "Opens a modal form to create a private support ticket with staff."
            },
            "ticket-setup": {
                "category": "🎫 Tickets",
                "description": "Configure the ticket system",
                "usage": "/ticket-setup",
                "examples": ["/ticket-setup"],
                "permissions": "Administrator",
                "notes": "Sets up ticket categories, support roles, and custom messages."
            },
            
            # Utilities
            "ping": {
                "category": "🔧 Utilities",
                "description": "Check the bot's latency and response time",
                "usage": "/ping",
                "examples": ["/ping"],
                "permissions": "None",
                "notes": "Shows bot latency, database response time, and uptime."
            },
            "userinfo": {
                "category": "🔧 Utilities",
                "description": "Get detailed information about a user",
                "usage": "/userinfo [user]",
                "examples": [
                    "/userinfo",
                    "/userinfo @user"
                ],
                "permissions": "None",
                "notes": "Shows join date, roles, account creation date, and more."
            },
            "serverinfo": {
                "category": "🔧 Utilities",
                "description": "Get detailed information about the server",
                "usage": "/serverinfo",
                "examples": ["/serverinfo"],
                "permissions": "None",
                "notes": "Shows member count, channels, roles, server features, and more."
            },
            "avatar": {
                "category": "🔧 Utilities",
                "description": "Display a user's avatar",
                "usage": "/avatar [user]",
                "examples": [
                    "/avatar",
                    "/avatar @user"
                ],
                "permissions": "None",
                "notes": "Shows the user's profile picture in full resolution."
            },
            "embed": {
                "category": "🔧 Utilities",
                "description": "Create custom embeds with action buttons",
                "usage": "/embed <title/description> [options]",
                "examples": [
                    "/embed title:Welcome description:Hello everyone!",
                    "/embed title:Support description:Need help? button_label:Open Ticket button_action:open_ticket"
                ],
                "permissions": "None",
                "notes": "Create rich embeds with colors, images, and interactive buttons."
            },
            
            # Administration
            "prefix": {
                "category": "⚙️ Administration",
                "description": "View or change the bot's command prefix",
                "usage": "/prefix [new_prefix]",
                "examples": [
                    "/prefix",
                    "/prefix !"
                ],
                "permissions": "Administrator",
                "notes": "Changes the prefix for legacy text commands. Default is '!'."
            },
            "modrole": {
                "category": "⚙️ Administration",
                "description": "Set the minimum role required for moderation commands",
                "usage": "/modrole [role]",
                "examples": [
                    "/modrole",
                    "/modrole @Moderator"
                ],
                "permissions": "Administrator",
                "notes": "Users with this role or higher can use moderation commands. Use without arguments to view current setting."
            },
            "resetmodrole": {
                "category": "⚙️ Administration",
                "description": "Reset moderation role to default permissions",
                "usage": "/resetmodrole",
                "examples": ["/resetmodrole"],
                "permissions": "Administrator",
                "notes": "Removes custom moderation role and returns to default permission-based system."
            },
            "changelog": {
                "category": "⚙️ Administration",
                "description": "Configure automatic changelog posting",
                "usage": "/changelog",
                "examples": ["/changelog"],
                "permissions": "Administrator",
                "notes": "Set up automatic changelog posts when the bot restarts or updates."
            }
        }
    
    @app_commands.command(name='help', description='Get detailed help for a specific command')
    @app_commands.describe(command="The command to get help for")
    async def help_command(self, interaction: discord.Interaction, command: str):
        """Get detailed help for a specific command"""
        
        command_name = command.lower().replace('/', '')
        
        if command_name not in self.command_info:
            # Show available commands
            embed = discord.Embed(
                title="❓ Command Not Found",
                description=f"Command `{command}` not found. Here are available commands:",
                color=discord.Color.red()
            )
            
            # Group commands by category
            categories = {}
            for cmd, info in self.command_info.items():
                category = info['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(cmd)
            
            for category, commands in categories.items():
                command_list = ", ".join([f"`{cmd}`" for cmd in commands])
                embed.add_field(
                    name=category,
                    value=command_list,
                    inline=False
                )
            
            embed.set_footer(text="Use /help <command> for detailed information about a specific command")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get command info
        info = self.command_info[command_name]
        
        # Create detailed help embed
        embed = discord.Embed(
            title=f"📚 Help: /{command_name}",
            description=info['description'],
            color=discord.Color.blue()
        )
        
        # Add category
        embed.add_field(
            name="📂 Category",
            value=info['category'],
            inline=True
        )
        
        # Add permissions
        embed.add_field(
            name="🔒 Required Permissions",
            value=info['permissions'],
            inline=True
        )
        
        # Add usage
        embed.add_field(
            name="💡 Usage",
            value=f"`{info['usage']}`",
            inline=False
        )
        
        # Add examples
        if info['examples']:
            examples_text = "\n".join([f"`{example}`" for example in info['examples']])
            embed.add_field(
                name="📝 Examples",
                value=examples_text,
                inline=False
            )
        
        # Add notes
        if info['notes']:
            embed.add_field(
                name="📋 Notes",
                value=info['notes'],
                inline=False
            )
        
        embed.set_footer(text="Use /commands to see all available commands")
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        logger.info(f"Help requested for command '{command_name}' by {interaction.user} in {interaction.guild.name}")

async def setup(bot):
    await bot.add_cog(HelpCog(bot))