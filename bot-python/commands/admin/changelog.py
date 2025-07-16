import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChangelogSetupView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.selected_channel = None
        
    @discord.ui.select(
        placeholder="Select a channel for changelog posts...",
        min_values=1,
        max_values=1,
        row=0,
        options=[discord.SelectOption(label="Loading...", value="loading")]
    )
    async def select_channel(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "loading":
            await interaction.response.defer()
            return
            
        channel_id = int(select.values[0])
        self.selected_channel = interaction.guild.get_channel(channel_id)
        
        embed = discord.Embed(
            title="📢 Changelog Channel Selected",
            description=f"Changelog posts will be sent to {self.selected_channel.mention}",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Channel Information",
            value=f"**Name:** {self.selected_channel.name}\n**Type:** {self.selected_channel.type}\n**ID:** {self.selected_channel.id}",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
        
    @discord.ui.button(label='✅ Confirm & Save', style=discord.ButtonStyle.success, row=1)
    async def confirm_selection(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_channel:
            embed = discord.Embed(
                title="❌ No Channel Selected",
                description="Please select a channel first.",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=self)
            return
            
        # Save to database
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS changelog_config (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                last_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            INSERT OR REPLACE INTO changelog_config (guild_id, channel_id, enabled)
            VALUES (?, ?, ?)
        ''', (interaction.guild.id, self.selected_channel.id, True))
        
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="✅ Changelog Configuration Saved",
            description=f"Changelog posts will now be automatically sent to {self.selected_channel.mention} when the bot restarts.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Next Steps",
            value="• The bot will post changelog updates on restart\n• Use `/changelog disable` to turn off automatic posts\n• Use `/changelog test` to send a test changelog",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
        
        logger.info(f"Changelog channel configured to #{self.selected_channel.name} in {interaction.guild.name}")

class ChangelogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='changelog', description='Configure changelog settings and channel')
    async def changelog_setup(self, interaction: discord.Interaction):
        """Configure changelog posting settings"""
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need administrator permissions to configure changelog settings.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Create setup view
        setup_view = ChangelogSetupView(self.bot)
        
        # Get text channels
        text_channels = [ch for ch in interaction.guild.channels if isinstance(ch, discord.TextChannel)]
        
        if not text_channels:
            embed = discord.Embed(
                title="❌ No Text Channels",
                description="No text channels found in this server.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Sort channels by position
        text_channels.sort(key=lambda ch: ch.position)
        
        # Add channel options to dropdown
        setup_view.select_channel.options = [
            discord.SelectOption(
                label=f"#{channel.name}",
                description=f"Category: {channel.category.name if channel.category else 'None'}",
                value=str(channel.id),
                emoji="📝"
            ) for channel in text_channels[:25]  # Discord limit
        ]
        
        embed = discord.Embed(
            title="📢 Changelog Configuration",
            description="Select a channel where changelog updates will be posted automatically when the bot restarts.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Available Channels",
            value=f"Found {len(text_channels)} text channels in this server",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=setup_view, ephemeral=True)
        
        logger.info(f"Changelog setup initiated in {interaction.guild.name} by {interaction.user}")
        
    @app_commands.command(name='changelog-disable', description='Disable automatic changelog posts')
    async def changelog_disable(self, interaction: discord.Interaction):
        """Disable automatic changelog posting"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need administrator permissions to modify changelog settings.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE changelog_config SET enabled = FALSE WHERE guild_id = ?', (interaction.guild.id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            embed = discord.Embed(
                title="✅ Changelog Disabled",
                description="Automatic changelog posts have been disabled for this server.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ No Configuration Found",
                description="No changelog configuration found for this server. Use `/changelog` to set it up first.",
                color=discord.Color.red()
            )
            
        conn.close()
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @app_commands.command(name='changelog-test', description='Send a test changelog post')
    async def changelog_test(self, interaction: discord.Interaction):
        """Send a test changelog post"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need administrator permissions to send test changelog posts.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Get changelog channel
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT channel_id, enabled FROM changelog_config WHERE guild_id = ?', (interaction.guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            embed = discord.Embed(
                title="❌ No Configuration Found",
                description="No changelog configuration found. Use `/changelog` to set it up first.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        channel_id, enabled = result
        if not enabled:
            embed = discord.Embed(
                title="❌ Changelog Disabled",
                description="Changelog posting is disabled for this server.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        changelog_channel = interaction.guild.get_channel(channel_id)
        if not changelog_channel:
            embed = discord.Embed(
                title="❌ Channel Not Found",
                description="The configured changelog channel was not found. Please reconfigure with `/changelog`.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Create test changelog
        await self.post_changelog(interaction.guild, changelog_channel, test=True)
        
        embed = discord.Embed(
            title="✅ Test Changelog Sent",
            description=f"Test changelog posted to {changelog_channel.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    async def post_changelog(self, guild, channel, test=False):
        """Post a changelog embed to the specified channel"""
        
        # Sample changelog data - in a real implementation, this would come from a config file or database
        changelog_data = {
            "version": "v2.1.0" if not test else "v2.1.0 (Test)",
            "date": datetime.now().strftime("%B %d, %Y"),
            "changes": [
                {
                    "category": "🆕 New Features",
                    "items": [
                        "Enhanced ticket system with dropdown role selection",
                        "Added comprehensive `/commands` command listing",
                        "Implemented automatic changelog posting system",
                        "Added support for all guild roles in ticket configuration"
                    ]
                },
                {
                    "category": "🔧 Improvements", 
                    "items": [
                        "Fixed Discord API errors in ticket setup",
                        "Improved role selection interface with visual indicators",
                        "Enhanced error handling throughout the bot",
                        "Optimized command syncing process"
                    ]
                },
                {
                    "category": "🐛 Bug Fixes",
                    "items": [
                        "Resolved 'application did not respond' errors",
                        "Fixed dropdown validation issues",
                        "Corrected command loading conflicts",
                        "Improved database connection stability"
                    ]
                }
            ]
        }
        
        # Create changelog embed
        embed = discord.Embed(
            title=f"📋 NexGuard Bot Changelog - {changelog_data['version']}",
            description=f"**Release Date:** {changelog_data['date']}\n\nLatest updates and improvements to NexGuard Bot:",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # Add changelog sections
        for section in changelog_data["changes"]:
            value = "\n".join([f"• {item}" for item in section["items"]])
            embed.add_field(
                name=section["category"],
                value=value,
                inline=False
            )
            
        # Add footer
        embed.add_field(
            name="📊 Bot Statistics",
            value=f"• **Guilds:** {len(self.bot.guilds)}\n• **Users:** {sum(guild.member_count for guild in self.bot.guilds)}\n• **Commands:** 31\n• **Uptime:** Since restart",
            inline=False
        )
        
        if test:
            embed.add_field(
                name="🧪 Test Mode",
                value="This is a test changelog post. Automatic posts will be sent when the bot restarts.",
                inline=False
            )
            
        embed.set_footer(text=f"NexGuard Bot • {guild.name}")
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        
        try:
            await channel.send(embed=embed)
            logger.info(f"Changelog posted to #{channel.name} in {guild.name}")
        except discord.Forbidden:
            logger.error(f"Cannot send changelog to #{channel.name} in {guild.name} - missing permissions")
        except Exception as e:
            logger.error(f"Error sending changelog to #{channel.name} in {guild.name}: {e}")

async def setup(bot):
    await bot.add_cog(ChangelogCog(bot))