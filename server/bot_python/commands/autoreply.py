"""
NexGuard Auto-Reply System
Advanced keyword detection and automated embed responses
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Constants
COLORS = {
    'SUCCESS': 0x00FF00,
    'ERROR': 0xFF0000,
    'INFO': 0x00FFFF,
    'WARNING': 0xFFFF00
}

EMOJIS = {
    'SUCCESS': '✅',
    'ERROR': '❌',
    'INFO': 'ℹ️',
    'WARNING': '⚠️'
}

class AutoReply(commands.Cog):
    """Auto-reply system for keyword detection and automated responses"""
    
    def __init__(self, bot):
        self.bot = bot
        self.setup_database()
    
    def setup_database(self):
        """Initialize auto-reply database tables"""
        # Tables are defined in schema.ts and created via migrations
        logger.info("Auto-reply system initialized")
    
    async def is_admin_or_moderator(self, interaction: discord.Interaction) -> bool:
        """Check if user has admin or moderator permissions"""
        return (interaction.user.guild_permissions.administrator or 
                interaction.user.guild_permissions.manage_messages or
                interaction.user.guild_permissions.manage_guild)
    
    @app_commands.command(name="autoreply-create", description="Create a new auto-reply rule")
    @app_commands.describe(
        name="Name for this auto-reply rule",
        keywords="Keywords to trigger the response (comma-separated)",
        title="Embed title",
        description="Embed description",
        color="Embed color (hex code or color name)",
        match_type="How to match keywords (contains, exact, starts_with, ends_with)",
        cooldown="Cooldown in seconds before rule can trigger again"
    )
    @app_commands.choices(
        match_type=[
            app_commands.Choice(name="Contains", value="contains"),
            app_commands.Choice(name="Exact Match", value="exact"),
            app_commands.Choice(name="Starts With", value="starts_with"),
            app_commands.Choice(name="Ends With", value="ends_with")
        ]
    )
    async def autoreply_create(
        self, 
        interaction: discord.Interaction, 
        name: str, 
        keywords: str,
        title: str,
        description: str,
        color: str = "blue",
        match_type: str = "contains",
        cooldown: int = 10
    ):
        """Create a new auto-reply rule"""
        if not await self.is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        if not self.bot.db_pool:
            await interaction.response.send_message(f"{EMOJIS['ERROR']} Database connection not available.", ephemeral=True)
            return
        
        try:
            # Parse color
            if color.startswith('#'):
                embed_color = int(color[1:], 16)
            else:
                color_map = {
                    'red': 0xFF0000, 'green': 0x00FF00, 'blue': 0x0000FF,
                    'yellow': 0xFFFF00, 'purple': 0x800080, 'orange': 0xFFA500,
                    'cyan': 0x00FFFF, 'pink': 0xFFC0CB, 'white': 0xFFFFFF,
                    'black': 0x000000, 'gray': 0x808080, 'grey': 0x808080
                }
                embed_color = color_map.get(color.lower(), 0x00FFFF)
            
            # Validate match type
            valid_match_types = ['contains', 'exact', 'starts_with', 'ends_with']
            if match_type not in valid_match_types:
                await interaction.response.send_message(
                    f"{EMOJIS['ERROR']} Invalid match type. Use: {', '.join(valid_match_types)}", 
                    ephemeral=True
                )
                return
            
            # Note: response_data removed since we're using individual columns
            
            # Save to database using correct column names
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO auto_replies 
                    (guild_id, trigger, response_title, response_description, response_color, trigger_type, is_active, created_by_id, created_by_name)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ''', 
                    str(interaction.guild.id),
                    keywords.lower(),
                    title,
                    description,
                    str(embed_color),
                    match_type,
                    True,   # is_active
                    str(interaction.user.id),
                    interaction.user.display_name
                )
            
            embed = discord.Embed(
                title=f"{EMOJIS['SUCCESS']} Auto-Reply Rule Created",
                description=f"**Rule:** {name}\n**Keywords:** {keywords}\n**Match Type:** {match_type}\n**Cooldown:** {cooldown}s",
                color=COLORS['SUCCESS']
            )
            embed.add_field(
                name="Preview",
                value=f"**{title}**\n{description[:100]}{'...' if len(description) > 100 else ''}",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Auto-reply rule '{name}' created in guild {interaction.guild.id}")
            
        except Exception as e:
            logger.error(f"Error creating auto-reply rule: {e}")
            await self.bot.log_error(interaction.guild.id, "Auto-Reply Creation Error", str(e), "autoreply-create command")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"{EMOJIS['ERROR']} Failed to create auto-reply rule: {str(e)}", 
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"{EMOJIS['ERROR']} Failed to create auto-reply rule: {str(e)}", 
                    ephemeral=True
                )
    
    @app_commands.command(name="autoreply-list", description="List all auto-reply rules")
    async def autoreply_list(self, interaction: discord.Interaction):
        """List all auto-reply rules for the guild"""
        if not await self.is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        if not self.bot.db_pool:
            await interaction.response.send_message(f"{EMOJIS['ERROR']} Database connection not available.", ephemeral=True)
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                rules = await conn.fetch('''
                    SELECT id, trigger, is_active, trigger_type, created_at, created_by_name
                    FROM auto_replies 
                    WHERE guild_id = $1
                    ORDER BY created_at DESC
                    LIMIT 10
                ''', str(interaction.guild.id))
            
            if not rules:
                embed = discord.Embed(
                    title=f"{EMOJIS['INFO']} Auto-Reply Rules",
                    description="No auto-reply rules found. Use `/autoreply-create` to create one.",
                    color=COLORS['INFO']
                )
                await interaction.response.send_message(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"{EMOJIS['INFO']} Auto-Reply Rules",
                description=f"Found {len(rules)} auto-reply rules:",
                color=COLORS['INFO']
            )
            
            for rule in rules:
                status = f"{EMOJIS['SUCCESS']} Enabled" if rule['is_active'] else f"{EMOJIS['ERROR']} Disabled"
                embed.add_field(
                    name=f"#{rule['id']} - {rule['trigger'][:20]}{'...' if len(rule['trigger']) > 20 else ''}",
                    value=f"**Keywords:** {rule['trigger'][:50]}{'...' if len(rule['trigger']) > 50 else ''}\n**Status:** {status}\n**Match:** {rule['trigger_type']}\n**Created by:** {rule['created_by_name']}",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing auto-reply rules: {e}")
            await self.bot.log_error(interaction.guild.id, "Auto-Reply List Error", str(e), "autoreply-list command")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"{EMOJIS['ERROR']} Failed to list auto-reply rules: {str(e)}", 
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"{EMOJIS['ERROR']} Failed to list auto-reply rules: {str(e)}", 
                    ephemeral=True
                )
    
    @app_commands.command(name="autoreply-toggle", description="Enable or disable an auto-reply rule")
    @app_commands.describe(rule_id="ID of the auto-reply rule to toggle")
    async def autoreply_toggle(self, interaction: discord.Interaction, rule_id: int):
        """Toggle an auto-reply rule on/off"""
        if not await self.is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        if not self.bot.db_pool:
            await interaction.response.send_message(f"{EMOJIS['ERROR']} Database connection not available.", ephemeral=True)
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Check if rule exists
                rule = await conn.fetchrow('''
                    SELECT id, trigger, is_active FROM auto_replies 
                    WHERE id = $1 AND guild_id = $2
                ''', rule_id, str(interaction.guild.id))
                
                if not rule:
                    await interaction.response.send_message(
                        f"{EMOJIS['ERROR']} Auto-reply rule #{rule_id} not found.", 
                        ephemeral=True
                    )
                    return
                
                # Toggle the rule
                new_status = not rule['is_active']
                await conn.execute('''
                    UPDATE auto_replies 
                    SET is_active = $1, updated_at = NOW()
                    WHERE id = $2 AND guild_id = $3
                ''', new_status, rule_id, str(interaction.guild.id))
            
            status_text = "enabled" if new_status else "disabled"
            status_emoji = EMOJIS['SUCCESS'] if new_status else EMOJIS['ERROR']
            
            embed = discord.Embed(
                title=f"{status_emoji} Auto-Reply Rule {status_text.title()}",
                description=f"Rule **{rule['trigger'][:30]}{'...' if len(rule['trigger']) > 30 else ''}** (#{rule_id}) has been {status_text}.",
                color=COLORS['SUCCESS'] if new_status else COLORS['ERROR']
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Auto-reply rule #{rule_id} {status_text} in guild {interaction.guild.id}")
            
        except Exception as e:
            logger.error(f"Error toggling auto-reply rule: {e}")
            await self.bot.log_error(interaction.guild.id, "Auto-Reply Toggle Error", str(e), "autoreply-toggle command")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"{EMOJIS['ERROR']} Failed to toggle auto-reply rule: {str(e)}", 
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"{EMOJIS['ERROR']} Failed to toggle auto-reply rule: {str(e)}", 
                    ephemeral=True
                )
    
    @app_commands.command(name="autoreply-delete", description="Delete an auto-reply rule")
    @app_commands.describe(rule_id="ID of the auto-reply rule to delete")
    async def autoreply_delete(self, interaction: discord.Interaction, rule_id: int):
        """Delete an auto-reply rule"""
        if not await self.is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        if not self.bot.db_pool:
            await interaction.response.send_message(f"{EMOJIS['ERROR']} Database connection not available.", ephemeral=True)
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Check if rule exists
                rule = await conn.fetchrow('''
                    SELECT id, trigger FROM auto_replies 
                    WHERE id = $1 AND guild_id = $2
                ''', rule_id, str(interaction.guild.id))
                
                if not rule:
                    await interaction.response.send_message(
                        f"{EMOJIS['ERROR']} Auto-reply rule #{rule_id} not found.", 
                        ephemeral=True
                    )
                    return
                
                # Delete the rule
                await conn.execute('''
                    DELETE FROM auto_replies 
                    WHERE id = $1 AND guild_id = $2
                ''', rule_id, str(interaction.guild.id))
            
            embed = discord.Embed(
                title=f"{EMOJIS['SUCCESS']} Auto-Reply Rule Deleted",
                description=f"Rule **{rule['trigger'][:30]}{'...' if len(rule['trigger']) > 30 else ''}** (#{rule_id}) has been permanently deleted.",
                color=COLORS['ERROR']
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Auto-reply rule #{rule_id} deleted in guild {interaction.guild.id}")
            
        except Exception as e:
            logger.error(f"Error deleting auto-reply rule: {e}")
            await self.bot.log_error(interaction.guild.id, "Auto-Reply Delete Error", str(e), "autoreply-delete command")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"{EMOJIS['ERROR']} Failed to delete auto-reply rule: {str(e)}", 
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"{EMOJIS['ERROR']} Failed to delete auto-reply rule: {str(e)}", 
                    ephemeral=True
                )
    
    @app_commands.command(name="autoreply-stats", description="View auto-reply statistics")
    async def autoreply_stats(self, interaction: discord.Interaction):
        """View auto-reply statistics for the guild"""
        if not await self.is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS['ERROR']} You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        if not self.bot.db_pool:
            await interaction.response.send_message(f"{EMOJIS['ERROR']} Database connection not available.", ephemeral=True)
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Get total rules
                total_rules = await conn.fetchval('''
                    SELECT COUNT(*) FROM auto_replies WHERE guild_id = $1
                ''', str(interaction.guild.id))
                
                # Get enabled rules
                enabled_rules = await conn.fetchval('''
                    SELECT COUNT(*) FROM auto_replies WHERE guild_id = $1 AND is_active = true
                ''', str(interaction.guild.id))
                
                # Get recent activity (rules created in last 7 days)
                recent_activity = await conn.fetchval('''
                    SELECT COUNT(*) FROM auto_replies 
                    WHERE guild_id = $1 AND created_at > NOW() - INTERVAL '7 days'
                ''', str(interaction.guild.id))
            
            embed = discord.Embed(
                title=f"{EMOJIS['INFO']} Auto-Reply Statistics",
                color=COLORS['INFO']
            )
            
            embed.add_field(
                name="📊 Overview",
                value=f"**Total Rules:** {total_rules}\n**Enabled Rules:** {enabled_rules}\n**Recent Activity:** {recent_activity} rules created this week",
                inline=False
            )
            
            if total_rules > 0:
                embed.add_field(
                    name="💡 Tips",
                    value="• Use `/autoreply-list` to view all rules\n• Use `/autoreply-toggle` to enable/disable rules\n• Use `/autoreply-delete` to remove unwanted rules",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting auto-reply stats: {e}")
            await self.bot.log_error(interaction.guild.id, "Auto-Reply Stats Error", str(e), "autoreply-stats command")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"{EMOJIS['ERROR']} Failed to get auto-reply stats: {str(e)}", 
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"{EMOJIS['ERROR']} Failed to get auto-reply stats: {str(e)}", 
                    ephemeral=True
                )
    
    def check_message_for_keywords(self, message_content: str, keywords: str, match_type: str) -> bool:
        """Check if a message matches the keywords based on match type"""
        message_lower = message_content.lower()
        keyword_list = [kw.strip().lower() for kw in keywords.split(',')]
        
        for keyword in keyword_list:
            # Skip empty keywords
            if not keyword:
                continue
                
            if match_type == 'contains':
                if keyword in message_lower:
                    return True
            elif match_type == 'exact':
                if keyword == message_lower:
                    return True
            elif match_type == 'starts_with':
                if message_lower.startswith(keyword):
                    return True
            elif match_type == 'ends_with':
                if message_lower.endswith(keyword):
                    return True
        
        return False
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages for auto-reply triggers"""
        # Ignore messages from bots
        if message.author.bot:
            return
        
        # Ignore messages without guild
        if not message.guild:
            return
        
        # Ignore if no database connection
        if not self.bot.db_pool:
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Get all active auto-reply rules for this guild
                rules = await conn.fetch('''
                    SELECT id, trigger, response_title, response_description, response_color, trigger_type
                    FROM auto_replies 
                    WHERE guild_id = $1 AND is_active = true
                    ORDER BY created_at ASC
                ''', str(message.guild.id))
                
                for rule in rules:
                    # Check if message matches this rule
                    if self.check_message_for_keywords(message.content, rule['trigger'], rule['trigger_type']):
                        try:
                            # Create embed from database columns
                            embed_color = int(rule['response_color']) if rule['response_color'] else COLORS['INFO']
                            
                            embed = discord.Embed(
                                title=rule['response_title'] or 'Auto-Reply',
                                description=rule['response_description'] or 'No description provided',
                                color=embed_color,
                                timestamp=datetime.utcnow()
                            )
                            
                            embed.set_footer(
                                text=f'Auto-reply triggered by: {rule["trigger"]}',
                                icon_url=str(message.guild.icon) if message.guild.icon else None
                            )
                            
                            # Send the auto-reply
                            await message.channel.send(embed=embed)
                            
                            logger.info(f"Auto-reply triggered: '{rule['trigger'][:20]}...' in {message.guild.name}")
                            
                            # Only trigger the first matching rule
                            break
                            
                        except Exception as e:
                            logger.error(f"Error sending auto-reply: {e}")
                            
        except Exception as e:
            logger.error(f"Error processing auto-reply: {e}")
            await self.bot.log_error(message.guild.id, "Auto-Reply Message Processing Error", str(e), "on_message autoreply handler")

    async def process_auto_replies(self, message):
        """Process messages for auto-reply triggers"""
        if message.author.bot or not message.guild:
            return
        
        if not self.bot.db_pool:
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Get active auto-reply rules for this guild
                rules = await conn.fetch('''
                    SELECT id, trigger, response_title, response_description, response_color, trigger_type
                    FROM auto_replies 
                    WHERE guild_id = $1 AND is_active = true
                ''', str(message.guild.id))
                
                for rule in rules:
                    # Check if message matches trigger
                    content = message.content.lower()
                    trigger = rule['trigger'].lower()
                    
                    match_found = False
                    if rule['trigger_type'] == 'contains':
                        match_found = trigger in content
                    elif rule['trigger_type'] == 'exact':
                        match_found = content == trigger
                    elif rule['trigger_type'] == 'starts_with':
                        match_found = content.startswith(trigger)
                    elif rule['trigger_type'] == 'ends_with':
                        match_found = content.endswith(trigger)
                    
                    if match_found:
                        try:
                            # Create embed from database columns
                            embed_color = int(rule['response_color']) if rule['response_color'] else COLORS['INFO']
                            
                            embed = discord.Embed(
                                title=rule['response_title'] or 'Auto-Reply',
                                description=rule['response_description'] or 'Automated response triggered',
                                color=embed_color,
                                timestamp=datetime.utcnow()
                            )
                            
                            embed.set_footer(
                                text=f'Auto-reply triggered by: {rule["trigger"]}',
                                icon_url=str(message.guild.icon) if message.guild.icon else None
                            )
                            
                            await message.reply(embed=embed)
                            logger.info(f"Auto-reply triggered: '{rule['trigger'][:20]}...' in {message.guild.name}")
                            break  # Only trigger first matching rule
                            
                        except Exception as e:
                            logger.error(f"Error sending auto-reply: {e}")
                            await self.bot.log_error(message.guild.id, "Auto-Reply Error", str(e), f"Processing rule: {rule['trigger']}")
                        
                        break  # Only trigger one rule per message
                        
        except Exception as e:
            logger.error(f"Error processing auto-reply: {e}")
            await self.bot.log_error(message.guild.id, "Auto-Reply Processing Error", str(e), "process_auto_replies method")

async def setup(bot):
    await bot.add_cog(AutoReply(bot))