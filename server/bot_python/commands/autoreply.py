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

class AutoReply(commands.Cog):
    """Auto-reply system for keyword detection and automated responses"""
    
    def __init__(self, bot):
        self.bot = bot
    
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
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        if not self.bot.db_pool:
            await interaction.response.send_message("❌ Database connection not available.", ephemeral=True)
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
            
            # Create response data
            response_data = {
                'title': title,
                'description': description,
                'color': embed_color,
                'timestamp': True,
                'footer': {
                    'text': f'Auto-reply: {name}', 
                    'icon_url': str(interaction.guild.icon) if interaction.guild.icon else None
                }
            }
            
            # Save to database
            async with self.bot.db_pool.acquire() as conn:
                # Check if name already exists
                existing = await conn.fetchrow(
                    "SELECT id FROM autoreply_rules WHERE guild_id = $1 AND LOWER(name) = LOWER($2)",
                    str(interaction.guild.id), name
                )
                
                if existing:
                    await interaction.response.send_message(f"❌ Auto-reply rule with name '{name}' already exists.", ephemeral=True)
                    return
                
                await conn.execute("""
                    INSERT INTO autoreply_rules 
                    (guild_id, name, keywords, response_data, match_type, cooldown)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, 
                str(interaction.guild.id),
                name,
                keywords.lower(),
                json.dumps(response_data),
                match_type,
                cooldown
                )
            
            embed = discord.Embed(
                title="✅ Auto-Reply Rule Created",
                description=f"**Rule:** {name}\n**Keywords:** {keywords}\n**Match Type:** {match_type}\n**Cooldown:** {cooldown}s",
                color=0x00FF00
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
                f"❌ Failed to create auto-reply rule: {str(e)}", 
                ephemeral=True
            )
    
    @app_commands.command(name="autoreply-list", description="List all auto-reply rules")
    async def autoreply_list(self, interaction: discord.Interaction):
        """List all auto-reply rules for the guild"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        if not self.bot.db_pool:
            await interaction.response.send_message("❌ Database connection not available.", ephemeral=True)
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                rules = await conn.fetch("""
                    SELECT id, name, keywords, enabled, match_type, cooldown, created_at
                    FROM autoreply_rules 
                    WHERE guild_id = $1
                    ORDER BY created_at DESC
                """, str(interaction.guild.id))
            
            if not rules:
                embed = discord.Embed(
                    title="📝 Auto-Reply Rules",
                    description="No auto-reply rules found. Use `/autoreply-create` to create one.",
                    color=0x00FFFF
                )
                await interaction.response.send_message(embed=embed)
                return
            
            embed = discord.Embed(
                title="📝 Auto-Reply Rules",
                description=f"Found {len(rules)} auto-reply rules:",
                color=0x00FFFF
            )
            
            for rule in rules[:10]:  # Show first 10 rules
                status = "✅ Enabled" if rule['enabled'] else "❌ Disabled"
                embed.add_field(
                    name=f"#{rule['id']} - {rule['name']}",
                    value=f"**Keywords:** {rule['keywords'][:50]}{'...' if len(rule['keywords']) > 50 else ''}\n**Status:** {status}\n**Match:** {rule['match_type']} | **Cooldown:** {rule['cooldown']}s",
                    inline=False
                )
            
            if len(rules) > 10:
                embed.set_footer(text=f"Showing 10 of {len(rules)} rules. Use commands to manage specific rules.")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing auto-reply rules: {e}")
            await interaction.response.send_message(
                f"❌ Failed to list auto-reply rules: {str(e)}", 
                ephemeral=True
            )
    
    @app_commands.command(name="autoreply-toggle", description="Enable or disable an auto-reply rule")
    @app_commands.describe(rule_id="ID of the auto-reply rule to toggle")
    async def autoreply_toggle(self, interaction: discord.Interaction, rule_id: int):
        """Toggle an auto-reply rule on/off"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        if not self.bot.db_pool:
            await interaction.response.send_message("❌ Database connection not available.", ephemeral=True)
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Check if rule exists
                rule = await conn.fetchrow("""
                    SELECT id, name, enabled FROM autoreply_rules 
                    WHERE id = $1 AND guild_id = $2
                """, rule_id, str(interaction.guild.id))
                
                if not rule:
                    await interaction.response.send_message(
                        f"❌ Auto-reply rule #{rule_id} not found.", 
                        ephemeral=True
                    )
                    return
                
                # Toggle the rule
                new_status = not rule['enabled']
                await conn.execute("""
                    UPDATE autoreply_rules 
                    SET enabled = $1, updated_at = NOW()
                    WHERE id = $2 AND guild_id = $3
                """, new_status, rule_id, str(interaction.guild.id))
            
            status_text = "enabled" if new_status else "disabled"
            status_emoji = "✅" if new_status else "❌"
            
            embed = discord.Embed(
                title=f"{status_emoji} Auto-Reply Rule {status_text.title()}",
                description=f"Rule **{rule['name']}** (#{rule_id}) has been {status_text}.",
                color=0x00FF00 if new_status else 0xFF0000
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Auto-reply rule #{rule_id} {status_text} in guild {interaction.guild.id}")
            
        except Exception as e:
            logger.error(f"Error toggling auto-reply rule: {e}")
            await interaction.response.send_message(
                f"❌ Failed to toggle auto-reply rule: {str(e)}", 
                ephemeral=True
            )
    
    @app_commands.command(name="autoreply-delete", description="Delete an auto-reply rule")
    @app_commands.describe(rule_id="ID of the auto-reply rule to delete")
    async def autoreply_delete(self, interaction: discord.Interaction, rule_id: int):
        """Delete an auto-reply rule"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        if not self.bot.db_pool:
            await interaction.response.send_message("❌ Database connection not available.", ephemeral=True)
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Check if rule exists
                rule = await conn.fetchrow("""
                    SELECT id, name FROM autoreply_rules 
                    WHERE id = $1 AND guild_id = $2
                """, rule_id, str(interaction.guild.id))
                
                if not rule:
                    await interaction.response.send_message(
                        f"❌ Auto-reply rule #{rule_id} not found.", 
                        ephemeral=True
                    )
                    return
                
                # Delete the rule and related data
                await conn.execute('DELETE FROM autoreply_cooldowns WHERE rule_id = $1', rule_id)
                await conn.execute('DELETE FROM autoreply_stats WHERE rule_id = $1', rule_id)
                await conn.execute('DELETE FROM autoreply_rules WHERE id = $1 AND guild_id = $2', 
                                 rule_id, str(interaction.guild.id))
            
            embed = discord.Embed(
                title="✅ Auto-Reply Rule Deleted",
                description=f"Rule **{rule['name']}** (#{rule_id}) has been permanently deleted.",
                color=0xFF0000
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Auto-reply rule #{rule_id} deleted in guild {interaction.guild.id}")
            
        except Exception as e:
            logger.error(f"Error deleting auto-reply rule: {e}")
            await interaction.response.send_message(
                f"❌ Failed to delete auto-reply rule: {str(e)}", 
                ephemeral=True
            )
    
    @app_commands.command(name="autoreply-stats", description="View auto-reply statistics")
    async def autoreply_stats(self, interaction: discord.Interaction):
        """View auto-reply statistics for the guild"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.", 
                ephemeral=True
            )
            return
        
        if not self.bot.db_pool:
            await interaction.response.send_message("❌ Database connection not available.", ephemeral=True)
            return
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Get total rules
                total_rules = await conn.fetchval(
                    'SELECT COUNT(*) FROM autoreply_rules WHERE guild_id = $1', 
                    str(interaction.guild.id)
                )
                
                # Get enabled rules
                enabled_rules = await conn.fetchval(
                    'SELECT COUNT(*) FROM autoreply_rules WHERE guild_id = $1 AND enabled = TRUE', 
                    str(interaction.guild.id)
                )
                
                # Get total triggers today
                triggers_today = await conn.fetchval("""
                    SELECT COUNT(*) FROM autoreply_stats 
                    WHERE guild_id = $1 AND triggered_at >= CURRENT_DATE
                """, str(interaction.guild.id))
                
                # Get most triggered rules
                top_rules = await conn.fetch("""
                    SELECT r.name, COUNT(s.id) as trigger_count
                    FROM autoreply_rules r
                    LEFT JOIN autoreply_stats s ON r.id = s.rule_id
                    WHERE r.guild_id = $1
                    GROUP BY r.id, r.name
                    ORDER BY trigger_count DESC
                    LIMIT 5
                """, str(interaction.guild.id))
            
            embed = discord.Embed(
                title="📊 Auto-Reply Statistics",
                color=0x00FFFF
            )
            
            embed.add_field(
                name="📊 Overview",
                value=f"**Total Rules:** {total_rules}\n**Enabled Rules:** {enabled_rules}\n**Triggers Today:** {triggers_today}",
                inline=False
            )
            
            if top_rules:
                top_rules_text = "\n".join([f"**{rule['name']}:** {rule['trigger_count']} triggers" for rule in top_rules[:5]])
                embed.add_field(
                    name="🔥 Most Triggered Rules",
                    value=top_rules_text,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting auto-reply stats: {e}")
            await interaction.response.send_message(
                f"❌ Failed to get auto-reply stats: {str(e)}", 
                ephemeral=True
            )
    
    async def check_cooldown(self, guild_id: str, rule_id: int, user_id: str, channel_id: str, cooldown_seconds: int) -> bool:
        """Check if a rule is on cooldown for a user/channel"""
        if not self.bot.db_pool:
            return False
            
        try:
            async with self.bot.db_pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT last_triggered FROM autoreply_cooldowns
                    WHERE guild_id = $1 AND rule_id = $2 AND user_id = $3 AND channel_id = $4
                """, guild_id, rule_id, user_id, channel_id)
                
                if not result:
                    return False
                
                last_triggered = result['last_triggered']
                cooldown_end = last_triggered + timedelta(seconds=cooldown_seconds)
                
                return datetime.now() < cooldown_end
                
        except Exception as e:
            logger.error(f"Error checking cooldown: {e}")
            return False
    
    async def update_cooldown(self, guild_id: str, rule_id: int, user_id: str, channel_id: str):
        """Update the cooldown for a rule"""
        if not self.bot.db_pool:
            return
            
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO autoreply_cooldowns 
                    (guild_id, rule_id, user_id, channel_id, last_triggered)
                    VALUES ($1, $2, $3, $4, NOW())
                    ON CONFLICT (guild_id, rule_id, user_id, channel_id) 
                    DO UPDATE SET last_triggered = NOW()
                """, guild_id, rule_id, user_id, channel_id)
        except Exception as e:
            logger.error(f"Error updating cooldown: {e}")
    
    async def log_trigger(self, guild_id: str, rule_id: int, user_id: str, channel_id: str):
        """Log an auto-reply trigger"""
        if not self.bot.db_pool:
            return
            
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO autoreply_stats (guild_id, rule_id, user_id, channel_id)
                    VALUES ($1, $2, $3, $4)
                """, guild_id, rule_id, user_id, channel_id)
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
                if keyword == message_lower.strip():
                    return True
            elif match_type == 'starts_with':
                if message_lower.startswith(keyword):
                    return True
            elif match_type == 'ends_with':
                if message_lower.endswith(keyword):
                    return True
        
        return False
    
    async def process_auto_replies(self, message):
        """Process message for auto-reply triggers"""
        if not message.guild or not self.bot.db_pool:
            return
        
        try:
            guild_id = str(message.guild.id)
            user_id = str(message.author.id)
            channel_id = str(message.channel.id)
            
            async with self.bot.db_pool.acquire() as conn:
                # Get all enabled auto-reply rules for this guild
                rules = await conn.fetch("""
                    SELECT id, name, keywords, response_data, match_type, cooldown
                    FROM autoreply_rules 
                    WHERE guild_id = $1 AND enabled = TRUE
                    ORDER BY id
                """, guild_id)
                
                for rule in rules:
                    # Check if message matches keywords
                    if self.check_message_for_keywords(message.content, rule['keywords'], rule['match_type']):
                        # Check cooldown
                        if await self.check_cooldown(guild_id, rule['id'], user_id, channel_id, rule['cooldown']):
                            continue  # Skip if on cooldown
                        
                        # Parse response data
                        response_data = json.loads(rule['response_data'])
                        
                        # Create embed
                        embed = discord.Embed(
                            title=response_data['title'],
                            description=response_data['description'],
                            color=response_data['color']
                        )
                        
                        if response_data.get('timestamp'):
                            embed.timestamp = datetime.utcnow()
                        
                        if response_data.get('footer'):
                            footer = response_data['footer']
                            embed.set_footer(text=footer['text'], icon_url=footer.get('icon_url'))
                        
                        # Send the auto-reply
                        await message.reply(embed=embed)
                        
                        # Update cooldown and log trigger
                        await self.update_cooldown(guild_id, rule['id'], user_id, channel_id)
                        await self.log_trigger(guild_id, rule['id'], user_id, channel_id)
                        
                        logger.info(f"Auto-reply triggered: '{rule['name']}' in {message.guild.name}")
                        return  # Only respond to first match
                        
        except Exception as e:
            logger.error(f"Error processing auto-replies: {e}")

async def setup(bot):
    await bot.add_cog(AutoReply(bot))