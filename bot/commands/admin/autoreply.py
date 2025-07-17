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
from utils.helpers import EmbedBuilder
from utils.checks import is_moderator

logger = logging.getLogger(__name__)

class AutoReply(commands.Cog):
    """Auto-reply system for keyword detection and automated responses"""
    
    def __init__(self, bot):
        self.bot = bot
        self.setup_database()
    
    def setup_database(self):
        """Initialize auto-reply database tables"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            
            # Create auto-reply rules table
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS autoreply_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        keywords TEXT NOT NULL,
                        response_type TEXT DEFAULT 'embed',
                        response_data TEXT NOT NULL,
                        enabled BOOLEAN DEFAULT TRUE,
                        match_type TEXT DEFAULT 'contains',
                        cooldown INTEGER DEFAULT 10,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
            # Create auto-reply stats table
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS autoreply_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id TEXT NOT NULL,
                        rule_id INTEGER NOT NULL,
                        user_id TEXT NOT NULL,
                        channel_id TEXT NOT NULL,
                        triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (rule_id) REFERENCES autoreply_rules (id)
                    )
                ''')
                
            # Create auto-reply cooldowns table
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS autoreply_cooldowns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id TEXT NOT NULL,
                        rule_id INTEGER NOT NULL,
                        user_id TEXT NOT NULL,
                        channel_id TEXT NOT NULL,
                        last_triggered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (rule_id) REFERENCES autoreply_rules (id)
                    )
                ''')
                
            conn.commit()
            conn.close()
            logger.info("Auto-reply database tables initialized")
        except Exception as e:
            logger.error(f"Error setting up auto-reply database: {e}")
    
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
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.", 
                ephemeral=True
            )
            return
            return
        
        try:
            # Parse color
            if color.startswith('#'):
                embed_color = int(color[1:], 16)
            else:
                embed_color = getattr(COLORS, color.upper(), COLORS.INFO)
            
            # Validate match type
            valid_match_types = ['contains', 'exact', 'starts_with', 'ends_with']
            if match_type not in valid_match_types:
                await interaction.response.send_message(
                    f"{EMOJIS.ERROR} Invalid match type. Use: {', '.join(valid_match_types)}", 
                    ephemeral=True
                )
                return
            
            # Create response data
            response_data = {
                'title': title,
                'description': description,
                'color': embed_color,
                'timestamp': True,
                'footer': {'text': f'Auto-reply: {name}', 'icon_url': str(interaction.guild.icon) if interaction.guild.icon else None}
            }
            
            # Save to database
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO autoreply_rules 
                    (guild_id, name, keywords, response_data, match_type, cooldown)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    str(interaction.guild.id),
                    name,
                    keywords.lower(),
                    json.dumps(response_data),
                    match_type,
                    cooldown
                ))
                conn.commit()
            
            embed = discord.Embed(
                title=f"{EMOJIS.SUCCESS} Auto-Reply Rule Created",
                description=f"**Rule:** {name}\n**Keywords:** {keywords}\n**Match Type:** {match_type}\n**Cooldown:** {cooldown}s",
                color=COLORS.SUCCESS
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
            await interaction.response.send_message(
                f"{EMOJIS.ERROR} Failed to create auto-reply rule: {str(e)}", 
                ephemeral=True
            )
    
    @app_commands.command(name="autoreply-list", description="List all auto-reply rules")
    async def autoreply_list(self, interaction: discord.Interaction):
        """List all auto-reply rules for the guild"""
        if not await is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS.ERROR} You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, keywords, enabled, match_type, cooldown, created_at
                    FROM autoreply_rules 
                    WHERE guild_id = ?
                    ORDER BY created_at DESC
                ''', (str(interaction.guild.id),))
                
                rules = cursor.fetchall()
            
            if not rules:
                embed = discord.Embed(
                    title=f"{EMOJIS.INFO} Auto-Reply Rules",
                    description="No auto-reply rules found. Use `/autoreply-create` to create one.",
                    color=COLORS.INFO
                )
                await interaction.response.send_message(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"{EMOJIS.INFO} Auto-Reply Rules",
                description=f"Found {len(rules)} auto-reply rules:",
                color=COLORS.INFO
            )
            
            for rule in rules[:10]:  # Show first 10 rules
                status = f"{EMOJIS.SUCCESS} Enabled" if rule[3] else f"{EMOJIS.ERROR} Disabled"
                embed.add_field(
                    name=f"#{rule[0]} - {rule[1]}",
                    value=f"**Keywords:** {rule[2][:50]}{'...' if len(rule[2]) > 50 else ''}\n**Status:** {status}\n**Match:** {rule[4]} | **Cooldown:** {rule[5]}s",
                    inline=False
                )
            
            if len(rules) > 10:
                embed.set_footer(text=f"Showing 10 of {len(rules)} rules. Use /autoreply-manage to see more.")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing auto-reply rules: {e}")
            await interaction.response.send_message(
                f"{EMOJIS.ERROR} Failed to list auto-reply rules: {str(e)}", 
                ephemeral=True
            )
    
    @app_commands.command(name="autoreply-toggle", description="Enable or disable an auto-reply rule")
    @app_commands.describe(rule_id="ID of the auto-reply rule to toggle")
    async def autoreply_toggle(self, interaction: discord.Interaction, rule_id: int):
        """Toggle an auto-reply rule on/off"""
        if not await is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS.ERROR} You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check if rule exists
                cursor.execute('''
                    SELECT id, name, enabled FROM autoreply_rules 
                    WHERE id = ? AND guild_id = ?
                ''', (rule_id, str(interaction.guild.id)))
                
                rule = cursor.fetchone()
                if not rule:
                    await interaction.response.send_message(
                        f"{EMOJIS.ERROR} Auto-reply rule #{rule_id} not found.", 
                        ephemeral=True
                    )
                    return
                
                # Toggle the rule
                new_status = not rule[2]
                cursor.execute('''
                    UPDATE autoreply_rules 
                    SET enabled = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND guild_id = ?
                ''', (new_status, rule_id, str(interaction.guild.id)))
                
                conn.commit()
            
            status_text = "enabled" if new_status else "disabled"
            status_emoji = EMOJIS.SUCCESS if new_status else EMOJIS.ERROR
            
            embed = discord.Embed(
                title=f"{status_emoji} Auto-Reply Rule {status_text.title()}",
                description=f"Rule **{rule[1]}** (#{rule_id}) has been {status_text}.",
                color=COLORS.SUCCESS if new_status else COLORS.ERROR
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Auto-reply rule #{rule_id} {status_text} in guild {interaction.guild.id}")
            
        except Exception as e:
            logger.error(f"Error toggling auto-reply rule: {e}")
            await interaction.response.send_message(
                f"{EMOJIS.ERROR} Failed to toggle auto-reply rule: {str(e)}", 
                ephemeral=True
            )
    
    @app_commands.command(name="autoreply-delete", description="Delete an auto-reply rule")
    @app_commands.describe(rule_id="ID of the auto-reply rule to delete")
    async def autoreply_delete(self, interaction: discord.Interaction, rule_id: int):
        """Delete an auto-reply rule"""
        if not await is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS.ERROR} You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check if rule exists
                cursor.execute('''
                    SELECT id, name FROM autoreply_rules 
                    WHERE id = ? AND guild_id = ?
                ''', (rule_id, str(interaction.guild.id)))
                
                rule = cursor.fetchone()
                if not rule:
                    await interaction.response.send_message(
                        f"{EMOJIS.ERROR} Auto-reply rule #{rule_id} not found.", 
                        ephemeral=True
                    )
                    return
                
                # Delete the rule and related data
                cursor.execute('DELETE FROM autoreply_cooldowns WHERE rule_id = ?', (rule_id,))
                cursor.execute('DELETE FROM autoreply_stats WHERE rule_id = ?', (rule_id,))
                cursor.execute('DELETE FROM autoreply_rules WHERE id = ? AND guild_id = ?', (rule_id, str(interaction.guild.id)))
                
                conn.commit()
            
            embed = discord.Embed(
                title=f"{EMOJIS.SUCCESS} Auto-Reply Rule Deleted",
                description=f"Rule **{rule[1]}** (#{rule_id}) has been permanently deleted.",
                color=COLORS.ERROR
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Auto-reply rule #{rule_id} deleted in guild {interaction.guild.id}")
            
        except Exception as e:
            logger.error(f"Error deleting auto-reply rule: {e}")
            await interaction.response.send_message(
                f"{EMOJIS.ERROR} Failed to delete auto-reply rule: {str(e)}", 
                ephemeral=True
            )
    
    @app_commands.command(name="autoreply-stats", description="View auto-reply statistics")
    async def autoreply_stats(self, interaction: discord.Interaction):
        """View auto-reply statistics for the guild"""
        if not await is_admin_or_moderator(interaction):
            await interaction.response.send_message(
                f"{EMOJIS.ERROR} You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get total rules
                cursor.execute('SELECT COUNT(*) FROM autoreply_rules WHERE guild_id = ?', (str(interaction.guild.id),))
                total_rules = cursor.fetchone()[0]
                
                # Get enabled rules
                cursor.execute('SELECT COUNT(*) FROM autoreply_rules WHERE guild_id = ? AND enabled = TRUE', (str(interaction.guild.id),))
                enabled_rules = cursor.fetchone()[0]
                
                # Get total triggers today
                cursor.execute('''
                    SELECT COUNT(*) FROM autoreply_stats 
                    WHERE guild_id = ? AND DATE(triggered_at) = DATE('now')
                ''', (str(interaction.guild.id),))
                triggers_today = cursor.fetchone()[0]
                
                # Get most triggered rules
                cursor.execute('''
                    SELECT r.name, COUNT(s.id) as trigger_count
                    FROM autoreply_rules r
                    LEFT JOIN autoreply_stats s ON r.id = s.rule_id
                    WHERE r.guild_id = ?
                    GROUP BY r.id, r.name
                    ORDER BY trigger_count DESC
                    LIMIT 5
                ''', (str(interaction.guild.id),))
                
                top_rules = cursor.fetchall()
            
            embed = discord.Embed(
                title=f"{EMOJIS.INFO} Auto-Reply Statistics",
                color=COLORS.INFO
            )
            
            embed.add_field(
                name="📊 Overview",
                value=f"**Total Rules:** {total_rules}\n**Enabled Rules:** {enabled_rules}\n**Triggers Today:** {triggers_today}",
                inline=False
            )
            
            if top_rules:
                top_rules_text = "\n".join([f"**{rule[0]}:** {rule[1]} triggers" for rule in top_rules[:5]])
                embed.add_field(
                    name="🔥 Most Triggered Rules",
                    value=top_rules_text,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting auto-reply stats: {e}")
            await interaction.response.send_message(
                f"{EMOJIS.ERROR} Failed to get auto-reply stats: {str(e)}", 
                ephemeral=True
            )
    
    def check_cooldown(self, guild_id: str, rule_id: int, user_id: str, channel_id: str, cooldown_seconds: int) -> bool:
        """Check if a rule is on cooldown for a user/channel"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT last_triggered FROM autoreply_cooldowns
                    WHERE guild_id = ? AND rule_id = ? AND user_id = ? AND channel_id = ?
                ''', (guild_id, rule_id, user_id, channel_id))
                
                result = cursor.fetchone()
                if not result:
                    return False
                
                from datetime import datetime, timedelta
                last_triggered = datetime.fromisoformat(result[0])
                cooldown_end = last_triggered + timedelta(seconds=cooldown_seconds)
                
                return datetime.now() < cooldown_end
                
        except Exception as e:
            logger.error(f"Error checking cooldown: {e}")
            return False
    
    def update_cooldown(self, guild_id: str, rule_id: int, user_id: str, channel_id: str):
        """Update the cooldown for a rule"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO autoreply_cooldowns 
                    (guild_id, rule_id, user_id, channel_id, last_triggered)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (guild_id, rule_id, user_id, channel_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating cooldown: {e}")
    
    def log_trigger(self, guild_id: str, rule_id: int, user_id: str, channel_id: str):
        """Log an auto-reply trigger"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO autoreply_stats (guild_id, rule_id, user_id, channel_id)
                    VALUES (?, ?, ?, ?)
                ''', (guild_id, rule_id, user_id, channel_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging trigger: {e}")
    
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

async def setup(bot):
    await bot.add_cog(AutoReply(bot))