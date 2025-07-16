import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ServerInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='serverinfo', description='Get information about the server')
    async def serverinfo(self, interaction: discord.Interaction):
        """Get information about the server"""
        guild = interaction.guild
        
        embed = discord.Embed(
            title="🏰 Server Information",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Basic info
        embed.add_field(
            name="📋 Basic Info",
            value=f"**Name:** {guild.name}\n**ID:** `{guild.id}`\n**Owner:** {guild.owner.mention if guild.owner else 'Unknown'}",
            inline=False
        )
        
        # Server creation
        created = guild.created_at
        embed.add_field(
            name="📅 Created",
            value=f"<t:{int(created.timestamp())}:F>\n<t:{int(created.timestamp())}:R>",
            inline=True
        )
        
        # Member counts
        members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        bots = sum(1 for member in guild.members if member.bot)
        humans = members - bots
        
        embed.add_field(
            name="👥 Members",
            value=f"**Total:** {members}\n**Online:** {online_members}\n**Humans:** {humans}\n**Bots:** {bots}",
            inline=True
        )
        
        # Channels
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="📺 Channels",
            value=f"**Text:** {text_channels}\n**Voice:** {voice_channels}\n**Categories:** {categories}",
            inline=True
        )
        
        # Roles
        embed.add_field(
            name="🎭 Roles",
            value=f"**Count:** {len(guild.roles)}",
            inline=True
        )
        
        # Emojis
        regular_emojis = len([emoji for emoji in guild.emojis if not emoji.animated])
        animated_emojis = len([emoji for emoji in guild.emojis if emoji.animated])
        
        embed.add_field(
            name="😀 Emojis",
            value=f"**Regular:** {regular_emojis}\n**Animated:** {animated_emojis}",
            inline=True
        )
        
        # Boosts
        embed.add_field(
            name="💎 Boosts",
            value=f"**Level:** {guild.premium_tier}\n**Boosts:** {guild.premium_subscription_count}",
            inline=True
        )
        
        # Features
        if guild.features:
            features = []
            feature_names = {
                'COMMUNITY': 'Community Server',
                'PARTNERED': 'Partnered',
                'VERIFIED': 'Verified',
                'VANITY_URL': 'Vanity URL',
                'INVITE_SPLASH': 'Invite Splash',
                'BANNER': 'Banner',
                'ANIMATED_ICON': 'Animated Icon',
                'DISCOVERABLE': 'Discoverable',
                'FEATURABLE': 'Featurable',
                'WELCOME_SCREEN_ENABLED': 'Welcome Screen',
                'MEMBER_VERIFICATION_GATE_ENABLED': 'Member Verification',
                'PREVIEW_ENABLED': 'Preview Enabled'
            }
            
            for feature in guild.features:
                feature_name = feature_names.get(feature, feature.replace('_', ' ').title())
                features.append(feature_name)
            
            if features:
                embed.add_field(
                    name="✨ Features",
                    value=", ".join(features[:10]),  # Show first 10 features
                    inline=False
                )
        
        # Verification level
        verification_levels = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low",
            discord.VerificationLevel.medium: "Medium",
            discord.VerificationLevel.high: "High",
            discord.VerificationLevel.highest: "Highest"
        }
        
        embed.add_field(
            name="🔒 Security",
            value=f"**Verification:** {verification_levels.get(guild.verification_level, 'Unknown')}",
            inline=True
        )
        
        # Set banner if available
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        
        embed.set_footer(text=f"Requested by {interaction.user}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfoCog(bot))