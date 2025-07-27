import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
from typing import Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class ReactionRolesCog(commands.Cog):
    """Reaction roles system for automatic role assignment"""
    
    def __init__(self, bot):
        self.bot = bot
        self.reaction_roles = {}  # Cache for quick lookups
        
    async def cog_load(self):
        """Load reaction roles from database on startup"""
        await self.load_reaction_roles()
        logger.info("Reaction roles system initialized")
    
    async def load_reaction_roles(self):
        """Load all reaction roles from database into cache"""
        if not hasattr(self.bot, 'db_pool') or not self.bot.db_pool:
            return
            
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Ensure reaction_roles table exists
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS reaction_roles (
                        id SERIAL PRIMARY KEY,
                        guild_id TEXT NOT NULL,
                        channel_id TEXT NOT NULL,
                        message_id TEXT NOT NULL,
                        emoji TEXT NOT NULL,
                        role_id TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(message_id, emoji)
                    )
                """)
                
                # Load all reaction roles
                rows = await conn.fetch("SELECT * FROM reaction_roles")
                
                for row in rows:
                    guild_id = row['guild_id']
                    message_id = row['message_id']
                    
                    if guild_id not in self.reaction_roles:
                        self.reaction_roles[guild_id] = {}
                    if message_id not in self.reaction_roles[guild_id]:
                        self.reaction_roles[guild_id][message_id] = {}
                    
                    self.reaction_roles[guild_id][message_id][row['emoji']] = {
                        'role_id': row['role_id'],
                        'channel_id': row['channel_id']
                    }
                
                logger.info(f"Loaded {len(rows)} reaction roles across {len(self.reaction_roles)} guilds")
                
        except Exception as e:
            logger.error(f"Error loading reaction roles: {e}")
    
    @app_commands.command(name="reaction-roles", description="Manage reaction roles system")
    @app_commands.describe(
        action="Action to perform",
        message_id="Message ID to add reactions to",
        emoji="Emoji to react with",
        role="Role to assign when reacted",
        channel="Channel containing the message (optional)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="list", value="list"),
        app_commands.Choice(name="clear", value="clear")
    ])
    async def reaction_roles(
        self,
        interaction: discord.Interaction,
        action: str,
        message_id: str = None,
        emoji: str = None,
        role: discord.Role = None,
        channel: discord.TextChannel = None
    ):
        """Manage reaction roles"""
        
        # Check permissions
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("❌ You need Manage Roles permissions to use this command.", ephemeral=True)
            return
        
        if not hasattr(self.bot, 'db_pool') or not self.bot.db_pool:
            await interaction.response.send_message("❌ Database not available.", ephemeral=True)
            return
        
        # Defer response to prevent timeout
        await interaction.response.defer(ephemeral=True)
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                if action == "add":
                    if not all([message_id, emoji, role]):
                        await interaction.followup.send("❌ Message ID, emoji, and role are required for adding reaction roles.", ephemeral=True)
                        return
                    
                    # Find the message
                    message = None
                    target_channel = channel or interaction.channel
                    
                    try:
                        message = await target_channel.fetch_message(int(message_id))
                    except (discord.NotFound, ValueError):
                        await interaction.followup.send("❌ Message not found in the specified channel.", ephemeral=True)
                        return
                    
                    # Check if bot can manage the role
                    if role >= interaction.guild.me.top_role:
                        await interaction.followup.send("❌ I cannot assign this role as it's higher than my highest role.", ephemeral=True)
                        return
                    
                    # Add to database
                    try:
                        await conn.execute("""
                            INSERT INTO reaction_roles (guild_id, channel_id, message_id, emoji, role_id)
                            VALUES ($1, $2, $3, $4, $5)
                            ON CONFLICT (message_id, emoji) DO UPDATE SET
                            role_id = EXCLUDED.role_id
                        """, str(interaction.guild.id), str(target_channel.id), message_id, emoji, str(role.id))
                        
                        # Add to cache
                        guild_id = str(interaction.guild.id)
                        if guild_id not in self.reaction_roles:
                            self.reaction_roles[guild_id] = {}
                        if message_id not in self.reaction_roles[guild_id]:
                            self.reaction_roles[guild_id][message_id] = {}
                        
                        self.reaction_roles[guild_id][message_id][emoji] = {
                            'role_id': str(role.id),
                            'channel_id': str(target_channel.id)
                        }
                        
                        # Add reaction to message
                        try:
                            await message.add_reaction(emoji)
                        except discord.HTTPException:
                            pass  # Reaction might already exist or be invalid
                        
                        embed = discord.Embed(
                            title="✅ Reaction Role Added",
                            description=f"Reaction role setup successfully!",
                            color=0x00ff00,
                            timestamp=datetime.utcnow()
                        )
                        embed.add_field(name="Message", value=f"[Jump to Message]({message.jump_url})", inline=True)
                        embed.add_field(name="Emoji", value=emoji, inline=True)
                        embed.add_field(name="Role", value=role.mention, inline=True)
                        
                        await interaction.followup.send(embed=embed, ephemeral=True)
                        
                    except Exception as e:
                        logger.error(f"Error adding reaction role: {e}")
                        await interaction.followup.send("❌ Error adding reaction role to database.", ephemeral=True)
                
                elif action == "remove":
                    if not all([message_id, emoji]):
                        await interaction.followup.send("❌ Message ID and emoji are required for removing reaction roles.", ephemeral=True)
                        return
                    
                    # Remove from database
                    result = await conn.execute("""
                        DELETE FROM reaction_roles 
                        WHERE guild_id = $1 AND message_id = $2 AND emoji = $3
                    """, str(interaction.guild.id), message_id, emoji)
                    
                    if result == "DELETE 0":
                        await interaction.followup.send("❌ No reaction role found with those parameters.", ephemeral=True)
                        return
                    
                    # Remove from cache
                    guild_id = str(interaction.guild.id)
                    if (guild_id in self.reaction_roles and 
                        message_id in self.reaction_roles[guild_id] and
                        emoji in self.reaction_roles[guild_id][message_id]):
                        del self.reaction_roles[guild_id][message_id][emoji]
                        
                        if not self.reaction_roles[guild_id][message_id]:
                            del self.reaction_roles[guild_id][message_id]
                        if not self.reaction_roles[guild_id]:
                            del self.reaction_roles[guild_id]
                    
                    embed = discord.Embed(
                        title="🗑️ Reaction Role Removed",
                        description=f"Reaction role for {emoji} on message `{message_id}` has been removed.",
                        color=0xff0000,
                        timestamp=datetime.utcnow()
                    )
                    
                    await interaction.followup.send(embed=embed, ephemeral=True)
                
                elif action == "list":
                    rows = await conn.fetch("""
                        SELECT * FROM reaction_roles 
                        WHERE guild_id = $1 
                        ORDER BY created_at DESC
                    """, str(interaction.guild.id))
                    
                    if not rows:
                        await interaction.followup.send("❌ No reaction roles configured in this server.", ephemeral=True)
                        return
                    
                    embed = discord.Embed(
                        title="📋 Reaction Roles",
                        description=f"Found {len(rows)} reaction role(s)",
                        color=0x5865F2,
                        timestamp=datetime.utcnow()
                    )
                    
                    for row in rows[:10]:  # Limit to 10 for embed limits
                        channel = interaction.guild.get_channel(int(row['channel_id']))
                        role = interaction.guild.get_role(int(row['role_id']))
                        
                        channel_name = channel.mention if channel else "Deleted Channel"
                        role_name = role.mention if role else "Deleted Role"
                        
                        embed.add_field(
                            name=f"{row['emoji']} → {role_name}",
                            value=f"**Channel:** {channel_name}\n**Message ID:** `{row['message_id']}`",
                            inline=True
                        )
                    
                    if len(rows) > 10:
                        embed.set_footer(text=f"Showing 10 of {len(rows)} reaction roles")
                    
                    await interaction.followup.send(embed=embed, ephemeral=True)
                
                elif action == "clear":
                    if not message_id:
                        await interaction.followup.send("❌ Message ID is required for clearing reaction roles.", ephemeral=True)
                        return
                    
                    # Remove all reaction roles for a message
                    result = await conn.execute("""
                        DELETE FROM reaction_roles 
                        WHERE guild_id = $1 AND message_id = $2
                    """, str(interaction.guild.id), message_id)
                    
                    count = int(result.split()[-1]) if result.startswith("DELETE") else 0
                    
                    if count == 0:
                        await interaction.followup.send("❌ No reaction roles found for that message.", ephemeral=True)
                        return
                    
                    # Remove from cache
                    guild_id = str(interaction.guild.id)
                    if (guild_id in self.reaction_roles and 
                        message_id in self.reaction_roles[guild_id]):
                        del self.reaction_roles[guild_id][message_id]
                        if not self.reaction_roles[guild_id]:
                            del self.reaction_roles[guild_id]
                    
                    embed = discord.Embed(
                        title="🧹 Reaction Roles Cleared",
                        description=f"Removed {count} reaction role(s) from message `{message_id}`.",
                        color=0xff9900,
                        timestamp=datetime.utcnow()
                    )
                    
                    await interaction.followup.send(embed=embed, ephemeral=True)
                
                else:
                    await interaction.followup.send("❌ Invalid action.", ephemeral=True)
                    
        except Exception as e:
            logger.error(f"Error in reaction roles command: {e}")
            await interaction.followup.send("❌ An error occurred while processing the command.", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reaction additions for role assignment"""
        await self.handle_reaction(payload, add_role=True)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Handle reaction removals for role removal"""
        await self.handle_reaction(payload, add_role=False)
    
    async def handle_reaction(self, payload, add_role: bool):
        """Handle reaction role assignment/removal"""
        if payload.user_id == self.bot.user.id:
            return  # Ignore bot's own reactions
        
        guild_id = str(payload.guild_id)
        message_id = str(payload.message_id)
        emoji_str = str(payload.emoji)
        
        # Check if this is a configured reaction role
        if (guild_id not in self.reaction_roles or 
            message_id not in self.reaction_roles[guild_id] or
            emoji_str not in self.reaction_roles[guild_id][message_id]):
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        role_id = int(self.reaction_roles[guild_id][message_id][emoji_str]['role_id'])
        role = guild.get_role(role_id)
        
        if not role:
            # Role was deleted, remove from database
            try:
                if hasattr(self.bot, 'db_pool') and self.bot.db_pool:
                    async with self.bot.db_pool.acquire() as conn:
                        await conn.execute("""
                            DELETE FROM reaction_roles 
                            WHERE guild_id = $1 AND message_id = $2 AND emoji = $3
                        """, guild_id, message_id, emoji_str)
                    
                    # Remove from cache
                    del self.reaction_roles[guild_id][message_id][emoji_str]
                    if not self.reaction_roles[guild_id][message_id]:
                        del self.reaction_roles[guild_id][message_id]
                    if not self.reaction_roles[guild_id]:
                        del self.reaction_roles[guild_id]
            except Exception as e:
                logger.error(f"Error cleaning up deleted role: {e}")
            return
        
        # Check if bot can manage the role
        if role >= guild.me.top_role:
            return
        
        try:
            if add_role:
                if role not in member.roles:
                    await member.add_roles(role, reason="Reaction role assignment")
                    logger.info(f"Added role {role.name} to {member} via reaction role")
            else:
                if role in member.roles:
                    await member.remove_roles(role, reason="Reaction role removal")
                    logger.info(f"Removed role {role.name} from {member} via reaction role")
        except discord.Forbidden:
            logger.warning(f"Missing permissions to assign/remove role {role.name}")
        except discord.HTTPException as e:
            logger.error(f"Error handling reaction role: {e}")

async def setup(bot):
    await bot.add_cog(ReactionRolesCog(bot))