import discord
from discord.ext import commands
import sqlite3
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MemberLogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log member joins and handle auto-role"""
        try:
            # Log to database
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO member_logs (guild_id, user_id, action, additional_info)
                VALUES (?, ?, ?, ?)
            ''', (
                member.guild.id,
                member.id,
                'JOIN',
                json.dumps({
                    'username': str(member),
                    'account_created': member.created_at.isoformat(),
                    'avatar_url': str(member.display_avatar.url)
                })
            ))
            conn.commit()
            
            # Get guild settings
            cursor.execute('SELECT log_channel, welcome_channel, auto_role, member_logs FROM guild_settings WHERE guild_id = ?', 
                         (member.guild.id,))
            result = cursor.fetchone()
            conn.close()
            
            log_channel_id, welcome_channel_id, auto_role_id, member_logs_enabled = result if result else (None, None, None, 1)
            
            # Handle auto-role
            if auto_role_id:
                auto_role = member.guild.get_role(auto_role_id)
                if auto_role and auto_role < member.guild.me.top_role:
                    try:
                        await member.add_roles(auto_role, reason="Auto-role on join")
                        logger.info(f"Added auto-role {auto_role.name} to {member} in {member.guild.name}")
                    except discord.Forbidden:
                        logger.warning(f"Cannot add auto-role to {member} in {member.guild.name}: Missing permissions")
                    except Exception as e:
                        logger.error(f"Error adding auto-role: {e}")
            
            # Send welcome message
            if welcome_channel_id:
                welcome_channel = member.guild.get_channel(welcome_channel_id)
                if welcome_channel:
                    embed = discord.Embed(
                        title="👋 Welcome!",
                        description=f"Welcome to **{member.guild.name}**, {member.mention}!",
                        color=discord.Color.green(),
                        timestamp=datetime.utcnow()
                    )
                    
                    embed.add_field(
                        name="Account Created",
                        value=f"<t:{int(member.created_at.timestamp())}:R>",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="Member Count",
                        value=f"{member.guild.member_count}",
                        inline=True
                    )
                    
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text=f"ID: {member.id}")
                    
                    try:
                        await welcome_channel.send(embed=embed)
                    except discord.Forbidden:
                        logger.warning(f"Cannot send welcome message in {member.guild.name}: Missing permissions")
            
            # Log to log channel
            if log_channel_id and member_logs_enabled:
                log_channel = member.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="📥 Member Joined",
                        color=discord.Color.green(),
                        timestamp=datetime.utcnow()
                    )
                    
                    embed.add_field(
                        name="User",
                        value=f"{member} (`{member.id}`)",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="Account Created",
                        value=f"<t:{int(member.created_at.timestamp())}:R>",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="Member Count",
                        value=f"{member.guild.member_count}",
                        inline=True
                    )
                    
                    # Check account age
                    account_age = (datetime.utcnow() - member.created_at).days
                    if account_age < 7:
                        embed.add_field(
                            name="⚠️ New Account",
                            value=f"Account is only {account_age} days old",
                            inline=False
                        )
                    
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text=f"User ID: {member.id}")
                    
                    try:
                        await log_channel.send(embed=embed)
                    except discord.Forbidden:
                        logger.warning(f"Cannot send join log in {member.guild.name}: Missing permissions")
            
        except Exception as e:
            logger.error(f"Error logging member join: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log member leaves"""
        try:
            # Log to database
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO member_logs (guild_id, user_id, action, additional_info)
                VALUES (?, ?, ?, ?)
            ''', (
                member.guild.id,
                member.id,
                'LEAVE',
                json.dumps({
                    'username': str(member),
                    'roles': [role.name for role in member.roles if role.name != '@everyone'],
                    'joined_at': member.joined_at.isoformat() if member.joined_at else None
                })
            ))
            
            # Get log channel
            cursor.execute('SELECT log_channel FROM guild_settings WHERE guild_id = ?', (member.guild.id,))
            result = cursor.fetchone()
            conn.commit()
            conn.close()
            
            if result and result[0]:
                log_channel = member.guild.get_channel(result[0])
                if log_channel:
                    embed = discord.Embed(
                        title="📤 Member Left",
                        color=discord.Color.red(),
                        timestamp=datetime.utcnow()
                    )
                    
                    embed.add_field(
                        name="User",
                        value=f"{member} (`{member.id}`)",
                        inline=True
                    )
                    
                    if member.joined_at:
                        embed.add_field(
                            name="Joined",
                            value=f"<t:{int(member.joined_at.timestamp())}:R>",
                            inline=True
                        )
                    
                    embed.add_field(
                        name="Member Count",
                        value=f"{member.guild.member_count}",
                        inline=True
                    )
                    
                    # Show roles if any
                    roles = [role.name for role in member.roles if role.name != '@everyone']
                    if roles:
                        embed.add_field(
                            name="Roles",
                            value=", ".join(roles[:10]),  # Limit to first 10 roles
                            inline=False
                        )
                    
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text=f"User ID: {member.id}")
                    
                    try:
                        await log_channel.send(embed=embed)
                    except discord.Forbidden:
                        logger.warning(f"Cannot send leave log in {member.guild.name}: Missing permissions")
            
        except Exception as e:
            logger.error(f"Error logging member leave: {e}")
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Log member updates (role changes, nickname changes, etc.)"""
        try:
            # Check what changed
            changes = []
            
            # Nickname change
            if before.nick != after.nick:
                changes.append({
                    'type': 'nickname',
                    'before': before.nick,
                    'after': after.nick
                })
            
            # Role changes
            before_roles = set(before.roles)
            after_roles = set(after.roles)
            
            added_roles = after_roles - before_roles
            removed_roles = before_roles - after_roles
            
            if added_roles:
                changes.append({
                    'type': 'roles_added',
                    'roles': [role.name for role in added_roles]
                })
            
            if removed_roles:
                changes.append({
                    'type': 'roles_removed',
                    'roles': [role.name for role in removed_roles]
                })
            
            if not changes:
                return  # No relevant changes
            
            # Log to database
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO member_logs (guild_id, user_id, action, additional_info)
                VALUES (?, ?, ?, ?)
            ''', (
                after.guild.id,
                after.id,
                'UPDATE',
                json.dumps({
                    'changes': changes,
                    'username': str(after)
                })
            ))
            
            # Get log channel
            cursor.execute('SELECT log_channel FROM guild_settings WHERE guild_id = ?', (after.guild.id,))
            result = cursor.fetchone()
            conn.commit()
            conn.close()
            
            if result and result[0]:
                log_channel = after.guild.get_channel(result[0])
                if log_channel:
                    embed = discord.Embed(
                        title="👤 Member Updated",
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )
                    
                    embed.add_field(
                        name="User",
                        value=f"{after} (`{after.id}`)",
                        inline=True
                    )
                    
                    # Show changes
                    for change in changes:
                        if change['type'] == 'nickname':
                            embed.add_field(
                                name="Nickname Changed",
                                value=f"**Before:** {change['before'] or 'None'}\n**After:** {change['after'] or 'None'}",
                                inline=False
                            )
                        elif change['type'] == 'roles_added':
                            embed.add_field(
                                name="✅ Roles Added",
                                value=", ".join(change['roles']),
                                inline=False
                            )
                        elif change['type'] == 'roles_removed':
                            embed.add_field(
                                name="❌ Roles Removed",
                                value=", ".join(change['roles']),
                                inline=False
                            )
                    
                    embed.set_thumbnail(url=after.display_avatar.url)
                    embed.set_footer(text=f"User ID: {after.id}")
                    
                    try:
                        await log_channel.send(embed=embed)
                    except discord.Forbidden:
                        logger.warning(f"Cannot send update log in {after.guild.name}: Missing permissions")
            
        except Exception as e:
            logger.error(f"Error logging member update: {e}")
    
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        """Log user updates (username, avatar, etc.)"""
        try:
            changes = []
            
            # Username change
            if before.name != after.name:
                changes.append({
                    'type': 'username',
                    'before': before.name,
                    'after': after.name
                })
            
            # Avatar change
            if before.avatar != after.avatar:
                changes.append({
                    'type': 'avatar',
                    'before': str(before.display_avatar.url),
                    'after': str(after.display_avatar.url)
                })
            
            if not changes:
                return
            
            # Log to all mutual guilds
            for guild in self.bot.guilds:
                if guild.get_member(after.id):
                    try:
                        # Log to database
                        conn = sqlite3.connect(self.bot.db_path)
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO member_logs (guild_id, user_id, action, additional_info)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            guild.id,
                            after.id,
                            'USER_UPDATE',
                            json.dumps({
                                'changes': changes,
                                'username': str(after)
                            })
                        ))
                        
                        # Get log channel
                        cursor.execute('SELECT log_channel FROM guild_settings WHERE guild_id = ?', (guild.id,))
                        result = cursor.fetchone()
                        conn.commit()
                        conn.close()
                        
                        if result and result[0]:
                            log_channel = guild.get_channel(result[0])
                            if log_channel:
                                embed = discord.Embed(
                                    title="👤 User Updated",
                                    color=discord.Color.blue(),
                                    timestamp=datetime.utcnow()
                                )
                                
                                embed.add_field(
                                    name="User",
                                    value=f"{after} (`{after.id}`)",
                                    inline=True
                                )
                                
                                # Show changes
                                for change in changes:
                                    if change['type'] == 'username':
                                        embed.add_field(
                                            name="Username Changed",
                                            value=f"**Before:** {change['before']}\n**After:** {change['after']}",
                                            inline=False
                                        )
                                    elif change['type'] == 'avatar':
                                        embed.add_field(
                                            name="Avatar Changed",
                                            value="User updated their avatar",
                                            inline=False
                                        )
                                
                                embed.set_thumbnail(url=after.display_avatar.url)
                                embed.set_footer(text=f"User ID: {after.id}")
                                
                                try:
                                    await log_channel.send(embed=embed)
                                except discord.Forbidden:
                                    pass
                    
                    except Exception as e:
                        logger.error(f"Error logging user update for guild {guild.name}: {e}")
            
        except Exception as e:
            logger.error(f"Error logging user update: {e}")

async def setup(bot):
    await bot.add_cog(MemberLogCog(bot))
