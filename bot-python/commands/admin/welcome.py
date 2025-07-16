import discord
from discord.ext import commands
from discord import app_commands
import json
import sqlite3
import logging
import os
from openai import OpenAI
from datetime import datetime

logger = logging.getLogger(__name__)

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Initialize OpenAI client
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                self.ai_enabled = True
                logger.info("OpenAI client initialized successfully")
            else:
                self.ai_enabled = False
                logger.warning("OpenAI API key not found, AI features disabled")
        except Exception as e:
            self.ai_enabled = False
            logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def get_welcome_settings(self, guild_id: int) -> dict:
        """Get welcome settings for a guild"""
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT welcome_settings FROM guild_settings WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            try:
                return json.loads(result[0])
            except json.JSONDecodeError:
                return {}
        return {}
    
    def save_welcome_settings(self, guild_id: int, settings: dict):
        """Save welcome settings for a guild"""
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE guild_settings SET welcome_settings = ? WHERE guild_id = ?', 
                      (json.dumps(settings), guild_id))
        conn.commit()
        conn.close()
    
    @app_commands.command(name="welcome-setup", description="Configure AI-powered welcome messages")
    @app_commands.describe(
        channel="Channel where welcome messages will be sent",
        enabled="Enable or disable welcome messages",
        ai_personalization="Enable AI-powered personalized messages",
        tone="Tone for AI messages"
    )
    @app_commands.choices(
        tone=[
            app_commands.Choice(name="Friendly & Casual", value="friendly"),
            app_commands.Choice(name="Professional", value="professional"),
            app_commands.Choice(name="Enthusiastic", value="enthusiastic"),
            app_commands.Choice(name="Welcoming & Warm", value="warm"),
            app_commands.Choice(name="Gaming/Community", value="gaming")
        ]
    )
    async def welcome_setup(self, interaction: discord.Interaction,
                           channel: discord.TextChannel,
                           enabled: bool = True,
                           ai_personalization: bool = True,
                           tone: str = "friendly"):
        """Configure welcome message settings"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to configure welcome messages.", ephemeral=True)
            return
        
        # Check if AI is available
        if ai_personalization and not self.ai_enabled:
            await interaction.response.send_message("⚠️ AI personalization is not available (OpenAI API key missing). Using standard welcome messages.", ephemeral=True)
            ai_personalization = False
        
        # Create welcome settings
        welcome_settings = {
            'enabled': enabled,
            'channel_id': channel.id,
            'ai_personalization': ai_personalization,
            'tone': tone,
            'server_context': {
                'name': interaction.guild.name,
                'description': interaction.guild.description or "",
                'member_count': interaction.guild.member_count,
                'created_at': interaction.guild.created_at.isoformat()
            }
        }
        
        self.save_welcome_settings(interaction.guild.id, welcome_settings)
        
        embed = discord.Embed(
            title="🎉 Welcome System Configured",
            description="Welcome messages have been set up for your server!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Settings",
            value=(
                f"**Channel:** {channel.mention}\n"
                f"**Enabled:** {'✅' if enabled else '❌'}\n"
                f"**AI Personalization:** {'✅' if ai_personalization else '❌'}\n"
                f"**Tone:** {tone.title()}"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="welcome-template", description="Set a custom welcome message template")
    @app_commands.describe(
        template="Custom welcome message template (use {user}, {server}, {count} placeholders)"
    )
    async def welcome_template(self, interaction: discord.Interaction, template: str):
        """Set custom welcome message template"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to set welcome templates.", ephemeral=True)
            return
        
        settings = self.get_welcome_settings(interaction.guild.id)
        settings['custom_template'] = template
        self.save_welcome_settings(interaction.guild.id, settings)
        
        embed = discord.Embed(
            title="✅ Welcome Template Updated",
            description="Custom welcome message template has been saved.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Template",
            value=template,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="welcome-test", description="Test the welcome message system")
    async def welcome_test(self, interaction: discord.Interaction):
        """Test welcome message system"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to test welcome messages.", ephemeral=True)
            return
        
        settings = self.get_welcome_settings(interaction.guild.id)
        
        if not settings.get('enabled', False):
            await interaction.response.send_message("❌ Welcome messages are not enabled. Use `/welcome-setup` to configure them.", ephemeral=True)
            return
        
        # Generate test welcome message
        embed = await self.generate_welcome_message(interaction.user, settings)
        
        test_embed = discord.Embed(
            title="🧪 Welcome Message Test",
            description="Here's how the welcome message would look:",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=test_embed)
        
        # Send the actual welcome message
        channel = interaction.guild.get_channel(settings['channel_id'])
        if channel:
            await channel.send(embed=embed)
    
    @app_commands.command(name="welcome-stats", description="View welcome message statistics")
    async def welcome_stats(self, interaction: discord.Interaction):
        """View welcome message statistics"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to view welcome statistics.", ephemeral=True)
            return
        
        settings = self.get_welcome_settings(interaction.guild.id)
        
        embed = discord.Embed(
            title="📊 Welcome Message Statistics",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Status",
            value="✅ Enabled" if settings.get('enabled', False) else "❌ Disabled",
            inline=True
        )
        
        if settings.get('channel_id'):
            channel = interaction.guild.get_channel(settings['channel_id'])
            embed.add_field(
                name="Channel",
                value=channel.mention if channel else "Channel not found",
                inline=True
            )
        
        embed.add_field(
            name="AI Personalization",
            value="✅ Enabled" if settings.get('ai_personalization', False) else "❌ Disabled",
            inline=True
        )
        
        embed.add_field(
            name="Tone",
            value=settings.get('tone', 'friendly').title(),
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    async def generate_welcome_message(self, member: discord.Member, settings: dict) -> discord.Embed:
        """Generate welcome message for a member"""
        # Generate AI message if enabled
        if settings.get('ai_personalization', False) and self.ai_enabled and not member.bot:
            try:
                ai_message = await self.generate_ai_welcome(member, settings)
                if ai_message:
                    return self.format_welcome_embed(member, ai_message)
            except Exception as e:
                logger.error(f"AI welcome generation failed: {e}")
        
        # Generate standard welcome message
        message = self.generate_standard_welcome(member, settings)
        return self.format_welcome_embed(member, message)
    
    async def generate_ai_welcome(self, member: discord.Member, settings: dict) -> str:
        """Generate AI-powered welcome message"""
        tone = settings.get('tone', 'friendly')
        
        prompt = f"""Generate a personalized welcome message for a new Discord server member.

Server: {member.guild.name} ({member.guild.member_count} members)
Member: {member.name}
Tone: {tone}

Requirements:
- Keep it under 200 words
- Be genuine and welcoming
- Include server-specific references
- Make it feel personal but not overly familiar
- Use Discord-friendly formatting

Generate a warm, engaging welcome message."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a friendly Discord community manager creating personalized welcome messages."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def generate_standard_welcome(self, member: discord.Member, settings: dict) -> str:
        """Generate standard welcome message"""
        custom_template = settings.get('custom_template')
        
        if custom_template:
            return custom_template.format(
                user=member.mention,
                username=member.name,
                server=member.guild.name,
                count=member.guild.member_count
            )
        
        tone = settings.get('tone', 'friendly')
        
        messages = {
            'professional': f"Welcome to {member.guild.name}, {member.mention}! We're pleased to have you join our community.",
            'enthusiastic': f"🎉 Welcome to {member.guild.name}, {member.mention}! We're so excited to have you here!",
            'warm': f"A warm welcome to {member.guild.name}, {member.mention}! We're delighted you've joined our family.",
            'gaming': f"Player {member.mention} has joined the server! Welcome to {member.guild.name}! 🎮",
            'friendly': f"Hey there {member.mention}! Welcome to {member.guild.name}! 👋"
        }
        
        return messages.get(tone, messages['friendly'])
    
    def format_welcome_embed(self, member: discord.Member, message: str) -> discord.Embed:
        """Format welcome message as embed"""
        embed = discord.Embed(
            title=f"Welcome to {member.guild.name}! 🎉",
            description=message,
            color=discord.Color.green()
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.set_footer(
            text=f"Member #{member.guild.member_count} • {datetime.now().strftime('%B %d, %Y')}"
        )
        
        return embed

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))