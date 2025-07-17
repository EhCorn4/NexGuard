import discord
from discord.ext import commands
from discord import app_commands
import json
import sqlite3
import logging
import os
from openai import OpenAI

logger = logging.getLogger(__name__)

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Initialize OpenAI client
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
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
    
    @app_commands.command(name="welcome-setup", description="Configure AI-powered welcome messages for your server")
    @app_commands.describe(
        channel="Channel where welcome messages will be sent",
        enabled="Enable or disable welcome messages",
        ai_personalization="Enable AI-powered personalized messages",
        tone="Tone for AI messages",
        include_rules="Include server rules in welcome message",
        include_roles="Mention available roles to new members"
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
                           tone: str = "friendly",
                           include_rules: bool = True,
                           include_roles: bool = True):
        """Configure welcome message settings"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to configure welcome messages.", ephemeral=True)
            return
        
        # Check if AI is available
        if ai_personalization and not self.ai_enabled:
            await interaction.response.send_message("⚠️ AI personalization is not available (OpenAI API key missing). Using standard welcome messages.", ephemeral=True)
            ai_personalization = False
        
        # Get current settings
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT welcome_settings FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
        result = cursor.fetchone()
        
        # Create welcome settings
        welcome_settings = {
            'enabled': enabled,
            'channel_id': channel.id,
            'ai_personalization': ai_personalization,
            'tone': tone,
            'include_rules': include_rules,
            'include_roles': include_roles,
            'custom_message': None,
            'server_context': {
                'name': interaction.guild.name,
                'description': interaction.guild.description or "",
                'member_count': interaction.guild.member_count,
                'created_at': interaction.guild.created_at.isoformat()
            }
        }
        
        # Save settings
        cursor.execute('UPDATE guild_settings SET welcome_settings = ? WHERE guild_id = ?', 
                      (json.dumps(welcome_settings), interaction.guild.id))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="🎉 Welcome System Configured",
            description="AI-powered welcome messages have been set up for your server!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Settings",
            value=(
                f"**Channel:** {channel.mention}\n"
                f"**Enabled:** {'✅' if enabled else '❌'}\n"
                f"**AI Personalization:** {'✅' if ai_personalization else '❌'}\n"
                f"**Tone:** {tone.title()}\n"
                f"**Include Rules:** {'✅' if include_rules else '❌'}\n"
                f"**Include Roles:** {'✅' if include_roles else '❌'}"
            ),
            inline=False
        )
        
        if ai_personalization:
            embed.add_field(
                name="🤖 AI Features",
                value=(
                    "• Personalized messages based on user profile\n"
                    "• Server-specific context integration\n"
                    "• Dynamic content generation\n"
                    "• Tone adaptation based on server culture"
                ),
                inline=False
            )
        
        embed.add_field(
            name="Next Steps",
            value=(
                f"Use `/welcome-test` to preview messages\n"
                f"Use `/welcome-template` to set custom templates\n"
                f"Use `/welcome-stats` to view performance"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="welcome-template", description="Set custom welcome message templates")
    @app_commands.describe(
        template_type="Type of template to configure",
        message="Custom message template (use {user}, {server}, {count} placeholders)"
    )
    @app_commands.choices(
        template_type=[
            app_commands.Choice(name="Standard Welcome", value="standard"),
            app_commands.Choice(name="AI Enhancement Context", value="ai_context"),
            app_commands.Choice(name="Rules Reminder", value="rules"),
            app_commands.Choice(name="Role Information", value="roles")
        ]
    )
    async def welcome_template(self, interaction: discord.Interaction,
                              template_type: str,
                              message: str):
        """Set custom welcome templates"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to configure templates.", ephemeral=True)
            return
        
        # Get current settings
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT welcome_settings FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            await interaction.response.send_message("❌ Please run `/welcome-setup` first to configure the welcome system.", ephemeral=True)
            return
        
        try:
            settings = json.loads(result[0])
        except json.JSONDecodeError:
            settings = {}
        
        # Initialize templates if not exists
        if 'templates' not in settings:
            settings['templates'] = {}
        
        settings['templates'][template_type] = message
        
        # Save settings
        cursor.execute('UPDATE guild_settings SET welcome_settings = ? WHERE guild_id = ?', 
                      (json.dumps(settings), interaction.guild.id))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="📝 Template Updated",
            description=f"Custom template for '{template_type}' has been saved.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Template Preview",
            value=f"```{message[:500]}{'...' if len(message) > 500 else ''}```",
            inline=False
        )
        
        embed.add_field(
            name="Available Placeholders",
            value=(
                "`{user}` - Member mention\n"
                "`{username}` - Member username\n"
                "`{server}` - Server name\n"
                "`{count}` - Member count\n"
                "`{created}` - Account creation date"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="welcome-test", description="Test the welcome message system")
    @app_commands.describe(
        target_user="User to test welcome message for (defaults to you)"
    )
    async def welcome_test(self, interaction: discord.Interaction,
                          target_user: discord.Member = None):
        """Test welcome message generation"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to test welcome messages.", ephemeral=True)
            return
        
        if target_user is None:
            target_user = interaction.user
        
        await interaction.response.defer()
        
        # Generate welcome message
        welcome_message = await self.generate_welcome_message(target_user, test_mode=True)
        
        if welcome_message:
            embed = discord.Embed(
                title="🧪 Welcome Message Test",
                description="Here's how the welcome message would look:",
                color=discord.Color.blue()
            )
            
            if isinstance(welcome_message, discord.Embed):
                # If it's an embed, show it as a preview
                embed.add_field(
                    name="Generated Embed Title",
                    value=welcome_message.title,
                    inline=False
                )
                embed.add_field(
                    name="Generated Embed Description",
                    value=welcome_message.description[:1000] + ("..." if len(welcome_message.description) > 1000 else ""),
                    inline=False
                )
            else:
                # If it's text, show it directly
                embed.add_field(
                    name="Generated Message",
                    value=welcome_message[:1000] + ("..." if len(welcome_message) > 1000 else ""),
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Welcome system is not configured. Please run `/welcome-setup` first.")
    
    @app_commands.command(name="welcome-stats", description="View welcome message statistics")
    async def welcome_stats(self, interaction: discord.Interaction):
        """Show welcome message statistics"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Server' permission to view statistics.", ephemeral=True)
            return
        
        # Get welcome stats from database
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        
        # Get recent joins (last 30 days)
        cursor.execute('''
            SELECT COUNT(*) FROM member_logs 
            WHERE guild_id = ? AND action = 'join' 
            AND timestamp > datetime('now', '-30 days')
        ''', (interaction.guild.id,))
        recent_joins = cursor.fetchone()[0]
        
        # Get welcome settings
        cursor.execute('SELECT welcome_settings FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
        result = cursor.fetchone()
        
        conn.close()
        
        embed = discord.Embed(
            title="📊 Welcome System Statistics",
            description="Performance metrics for your welcome system",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Recent Activity (30 days)",
            value=f"**New Members:** {recent_joins}",
            inline=True
        )
        
        if result and result[0]:
            try:
                settings = json.loads(result[0])
                embed.add_field(
                    name="Current Settings",
                    value=(
                        f"**Status:** {'✅ Enabled' if settings.get('enabled', False) else '❌ Disabled'}\n"
                        f"**AI Personalization:** {'✅' if settings.get('ai_personalization', False) else '❌'}\n"
                        f"**Tone:** {settings.get('tone', 'Not set').title()}"
                    ),
                    inline=True
                )
                
                if 'channel_id' in settings:
                    channel = self.bot.get_channel(settings['channel_id'])
                    embed.add_field(
                        name="Welcome Channel",
                        value=f"<#{settings['channel_id']}>" if channel else "Channel not found",
                        inline=True
                    )
            except json.JSONDecodeError:
                embed.add_field(
                    name="Settings",
                    value="❌ Configuration error",
                    inline=True
                )
        else:
            embed.add_field(
                name="Status",
                value="❌ Welcome system not configured",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    async def generate_welcome_message(self, member: discord.Member, test_mode: bool = False):
        """Generate personalized welcome message using AI"""
        
        # Get welcome settings
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT welcome_settings FROM guild_settings WHERE guild_id = ?', (member.guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0]:
            return None
        
        try:
            settings = json.loads(result[0])
        except json.JSONDecodeError:
            return None
        
        if not settings.get('enabled', False):
            return None
        
        # Gather member context
        member_context = {
            'username': member.name,
            'display_name': member.display_name,
            'account_age_days': (discord.utils.utcnow() - member.created_at).days,
            'avatar_url': str(member.avatar.url) if member.avatar else None,
            'joined_at': member.joined_at.isoformat() if member.joined_at else None,
            'is_bot': member.bot
        }
        
        # Gather server context
        server_context = settings.get('server_context', {})
        server_context.update({
            'current_member_count': member.guild.member_count,
            'boost_level': member.guild.premium_tier,
            'verification_level': str(member.guild.verification_level),
            'has_rules': bool(member.guild.rules_channel),
            'channel_count': len(member.guild.channels)
        })
        
        # Generate AI message if enabled
        if settings.get('ai_personalization', False) and self.ai_enabled and not member.bot:
            try:
                ai_message = await self.generate_ai_welcome(member_context, server_context, settings)
                if ai_message:
                    return self.format_welcome_embed(member, ai_message, settings)
            except Exception as e:
                logger.error(f"AI welcome generation failed: {e}")
                # Fall back to standard message
        
        # Generate standard welcome message
        standard_message = self.generate_standard_welcome(member, settings)
        return self.format_welcome_embed(member, standard_message, settings)
    
    async def generate_ai_welcome(self, member_context, server_context, settings):
        """Generate AI-powered welcome message"""
        
        tone = settings.get('tone', 'friendly')
        include_rules = settings.get('include_rules', True)
        include_roles = settings.get('include_roles', True)
        
        # Create context prompt
        prompt = f"""Generate a personalized welcome message for a new Discord server member.

Server Context:
- Name: {server_context.get('name', 'Unknown')}
- Member Count: {server_context.get('current_member_count', 0)}
- Description: {server_context.get('description', 'A Discord community')}
- Boost Level: {server_context.get('boost_level', 0)}

Member Context:
- Username: {member_context['username']}
- Account Age: {member_context['account_age_days']} days
- Display Name: {member_context['display_name']}

Requirements:
- Tone: {tone}
- Keep it under 300 words
- Be genuine and welcoming
- Include server-specific references when appropriate
{"- Mention checking server rules" if include_rules else ""}
{"- Suggest exploring available roles" if include_roles else ""}
- Make it feel personal but not overly familiar
- Use Discord-friendly formatting (bold, italics when appropriate)

Generate a warm, engaging welcome message that makes the new member feel valued and informed about the community."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                messages=[
                    {"role": "system", "content": "You are a friendly Discord community manager creating personalized welcome messages. Be warm, helpful, and engaging while keeping messages concise."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def generate_standard_welcome(self, member: discord.Member, settings):
        """Generate standard welcome message"""
        
        templates = settings.get('templates', {})
        custom_template = templates.get('standard')
        
        if custom_template:
            # Use custom template
            message = custom_template.format(
                user=member.mention,
                username=member.name,
                server=member.guild.name,
                count=member.guild.member_count,
                created=member.created_at.strftime("%B %Y")
            )
        else:
            # Default template
            tone = settings.get('tone', 'friendly')
            
            if tone == 'professional':
                message = f"Welcome to {member.guild.name}, {member.mention}! We're pleased to have you join our community of {member.guild.member_count} members."
            elif tone == 'enthusiastic':
                message = f"🎉 Welcome to {member.guild.name}, {member.mention}! We're so excited to have you here! You're member #{member.guild.member_count}!"
            elif tone == 'warm':
                message = f"A warm welcome to {member.guild.name}, {member.mention}! We're delighted you've joined our family of {member.guild.member_count} members. Make yourself at home!"
            elif tone == 'gaming':
                message = f"Player {member.mention} has joined the server! Welcome to {member.guild.name}! 🎮 You're our {member.guild.member_count}th member!"
            else:  # friendly
                message = f"Hey there {member.mention}! Welcome to {member.guild.name}! 👋 Great to have you as our {member.guild.member_count}th member!"
        
        # Add additional info based on settings
        additions = []
        
        if settings.get('include_rules', True) and member.guild.rules_channel:
            additions.append(f"📋 Please check out {member.guild.rules_channel.mention} to get familiar with our guidelines.")
        
        if settings.get('include_roles', True):
            # Find a roles channel or mention role commands
            roles_info = "💼 Explore our roles to get access to different channels and activities!"
            additions.append(roles_info)
        
        if additions:
            message += "\n\n" + "\n".join(additions)
        
        return message
    
    def format_welcome_embed(self, member: discord.Member, message: str, settings):
        """Format welcome message as embed"""
        
        embed = discord.Embed(
            title=f"Welcome to {member.guild.name}! 🎉",
            description=message,
            color=discord.Color.green()
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.set_footer(
            text=f"Member #{member.guild.member_count} • Joined {discord.utils.utcnow().strftime('%B %d, %Y')}",
            icon_url=member.guild.icon.url if member.guild.icon else None
        )
        
        return embed

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))