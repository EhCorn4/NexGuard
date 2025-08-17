import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EmbedHelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="embedhelp", description="Get help with embed commands and formatting")
    async def embedhelp(self, interaction: discord.Interaction):
        """Get help with embed commands and formatting"""
        embed = discord.Embed(
            title="📖 Embed Commands Help",
            description="Learn how to create beautiful embeds with NexGuard!",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        # Basic Embed Command
        embed.add_field(
            name="🎨 Basic Embed - `/embed`",
            value=(
                "**Parameters:**\n"
                "• `title` - Embed title\n"
                "• `description` - Main content\n"
                "• `color` - Hex color (e.g., #FF0000)\n"
                "• `thumbnail` - Small image URL\n"
                "• `image` - Large image URL\n"
                "• `footer` - Footer text\n"
                "• `author` - Author name\n"
                "• `author_icon` - Author icon URL\n"
                "• `url` - Makes title clickable\n"
                "• `channel` - Target channel"
            ),
            inline=False
        )
        
        # Advanced Embed Command
        embed.add_field(
            name="⚡ Advanced Embed - `/embedbuilder`",
            value=(
                "**Additional Features:**\n"
                "• `fields` - Multiple fields with custom formatting\n"
                "• `buttons` - Interactive buttons\n"
                "• All basic embed features included"
            ),
            inline=False
        )
        
        # Fields Format
        embed.add_field(
            name="📋 Fields Format",
            value=(
                "**Format:** `name1|value1|inline1;name2|value2|inline2`\n"
                "**Example:** `Status|Online|true;Users|1,500|true;Uptime|2 days|false`\n"
                "**inline:** `true` = side by side, `false` = full width"
            ),
            inline=False
        )
        
        # Buttons Format
        embed.add_field(
            name="🔘 Buttons Format",
            value=(
                "**Format:** `label1|url1|style1;label2|url2|style2`\n"
                "**Example:** `Website|https://example.com|link;Support|discord.gg/abc|primary`\n"
                "**Styles:** `primary` (blue), `secondary` (gray), `success` (green), `danger` (red), `link` (URL)"
            ),
            inline=False
        )
        
        # Color Examples
        embed.add_field(
            name="🎨 Color Examples",
            value=(
                "• `#FF0000` - Red\n"
                "• `#00FF00` - Green\n"
                "• `#0000FF` - Blue\n"
                "• `#FFFF00` - Yellow\n"
                "• `#FF00FF` - Magenta\n"
                "• `#00FFFF` - Cyan\n"
                "• `#FFA500` - Orange\n"
                "• `#800080` - Purple"
            ),
            inline=True
        )
        
        # Tips
        embed.add_field(
            name="💡 Tips",
            value=(
                "• Use `\\n` for line breaks in descriptions\n"
                "• Maximum 25 fields per embed\n"
                "• Field names max 256 characters\n"
                "• Field values max 1024 characters\n"
                "• Description max 4096 characters\n"
                "• Title max 256 characters"
            ),
            inline=True
        )
        
        embed.set_footer(text="NexGuard v2.3.2 | Need more help? Use /help", icon_url=None)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="embedexample", description="Show embed examples")
    async def embedexample(self, interaction: discord.Interaction):
        """Show embed examples"""
        # Example 1: Basic embed
        example_embed = discord.Embed(
            title="🎉 Server Announcement",
            description="Welcome to our amazing Discord server! We're excited to have you here.",
            color=0x00FF00,
            timestamp=datetime.utcnow()
        )
        
        example_embed.set_author(name="Server Admin", icon_url=None)
        example_embed.add_field(name="🔥 What's New", value="• New channels added\n• Updated rules\n• Fun events coming soon!", inline=False)
        example_embed.add_field(name="👥 Members", value="1,500+", inline=True)
        example_embed.add_field(name="⭐ Rating", value="5/5 Stars", inline=True)
        example_embed.add_field(name="🌟 Featured", value="Community Pick", inline=True)
        example_embed.set_thumbnail(url="https://via.placeholder.com/100x100/00FF00/FFFFFF?text=NEW")
        example_embed.set_footer(text="Thanks for being part of our community!", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        # Create view with example buttons
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Visit Website", url="https://example.com", style=discord.ButtonStyle.link))
        view.add_item(discord.ui.Button(label="Join Events", style=discord.ButtonStyle.primary, custom_id="join_events"))
        view.add_item(discord.ui.Button(label="Get Support", style=discord.ButtonStyle.secondary, custom_id="get_support"))
        
        await interaction.response.send_message("**Example Embed:**", embed=example_embed, view=view)

async def setup(bot):
    await bot.add_cog(EmbedHelpCommands(bot))