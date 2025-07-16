import discord
from discord.ext import commands
import sqlite3
import logging

logger = logging.getLogger(__name__)

class PermissionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(name='permissions', aliases=['perms'])
    @commands.has_permissions(manage_guild=True)
    async def permissions(self, ctx):
        """Manage command permissions"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🔒 Permission Management",
                description="Manage who can use specific commands",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Available Commands",
                value="`permissions view` - View current permissions\n"
                      "`permissions allow <role/user> <command>` - Allow access\n"
                      "`permissions deny <role/user> <command>` - Deny access\n"
                      "`permissions reset <command>` - Reset to default\n"
                      "`permissions list` - List all commands",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    @permissions.command(name='view')
    async def view_permissions(self, ctx, *, command_name=None):
        """View permissions for a command"""
        if command_name is None:
            embed = discord.Embed(
                title="❌ Error",
                description="Please specify a command to view permissions for.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # Check if command exists
        command = self.bot.get_command(command_name)
        if not command:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Command `{command_name}` not found.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            
            # Create permissions table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_permissions (
                    guild_id INTEGER,
                    command_name TEXT,
                    entity_id INTEGER,
                    entity_type TEXT,
                    allowed BOOLEAN,
                    PRIMARY KEY (guild_id, command_name, entity_id)
                )
            ''')
            
            cursor.execute('''
                SELECT entity_id, entity_type, allowed FROM command_permissions
                WHERE guild_id = ? AND command_name = ?
            ''', (ctx.guild.id, command_name))
            
            permissions = cursor.fetchall()
            conn.close()
            
            embed = discord.Embed(
                title=f"🔒 Permissions for `{command_name}`",
                color=discord.Color.blue()
            )
            
            if not permissions:
                embed.description = "No custom permissions set. Using default Discord permissions."
            else:
                allowed = []
                denied = []
                
                for entity_id, entity_type, is_allowed in permissions:
                    if entity_type == "role":
                        entity = ctx.guild.get_role(entity_id)
                        name = entity.mention if entity else f"Deleted Role ({entity_id})"
                    else:
                        entity = ctx.guild.get_member(entity_id)
                        name = entity.mention if entity else f"Unknown User ({entity_id})"
                    
                    if is_allowed:
                        allowed.append(name)
                    else:
                        denied.append(name)
                
                if allowed:
                    embed.add_field(
                        name="✅ Allowed",
                        value="\n".join(allowed),
                        inline=False
                    )
                
                if denied:
                    embed.add_field(
                        name="❌ Denied",
                        value="\n".join(denied),
                        inline=False
                    )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error(f"Error viewing permissions: {e}")
    
    @permissions.command(name='allow')
    async def allow_permission(self, ctx, target, *, command_name):
        """Allow a role or user to use a command"""
        # Parse target
        role = None
        member = None
        
        if target.startswith('<@&') and target.endswith('>'):
            # Role mention
            role_id = int(target[3:-1])
            role = ctx.guild.get_role(role_id)
            if not role:
                embed = discord.Embed(
                    title="❌ Error",
                    description="Role not found.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
        elif target.startswith('<@') and target.endswith('>'):
            # User mention
            user_id = int(target[2:-1].replace('!', ''))
            member = ctx.guild.get_member(user_id)
            if not member:
                embed = discord.Embed(
                    title="❌ Error",
                    description="Member not found.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
        else:
            # Try to find by name
            role = discord.utils.get(ctx.guild.roles, name=target)
            if not role:
                member = discord.utils.get(ctx.guild.members, name=target)
                if not member:
                    embed = discord.Embed(
                        title="❌ Error",
                        description="Role or member not found.",
                        color=discord.Color.red()
                    )
                    return await ctx.send(embed=embed)
        
        # Check if command exists
        command = self.bot.get_command(command_name)
        if not command:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Command `{command_name}` not found.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            
            if role:
                entity_id = role.id
                entity_type = "role"
                entity_name = role.name
            else:
                entity_id = member.id
                entity_type = "user"
                entity_name = member.display_name
            
            cursor.execute('''
                INSERT OR REPLACE INTO command_permissions
                (guild_id, command_name, entity_id, entity_type, allowed)
                VALUES (?, ?, ?, ?, ?)
            ''', (ctx.guild.id, command_name, entity_id, entity_type, True))
            
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="✅ Permission Granted",
                description=f"**{entity_name}** can now use the `{command_name}` command.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error(f"Error allowing permission: {e}")
    
    @permissions.command(name='deny')
    async def deny_permission(self, ctx, target, *, command_name):
        """Deny a role or user from using a command"""
        # Similar logic to allow_permission but with allowed=False
        # [Implementation similar to allow_permission with allowed=False]
        pass
    
    @permissions.command(name='reset')
    async def reset_permissions(self, ctx, *, command_name):
        """Reset permissions for a command to default"""
        command = self.bot.get_command(command_name)
        if not command:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Command `{command_name}` not found.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        try:
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM command_permissions
                WHERE guild_id = ? AND command_name = ?
            ''', (ctx.guild.id, command_name))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="✅ Permissions Reset",
                description=f"Permissions for `{command_name}` have been reset to default.\n"
                           f"Removed {deleted_count} custom permission(s).",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error(f"Error resetting permissions: {e}")
    
    @permissions.command(name='list')
    async def list_commands(self, ctx):
        """List all available commands"""
        commands_list = []
        
        for command in self.bot.commands:
            if not command.hidden:
                commands_list.append(f"`{command.name}` - {command.help or 'No description'}")
        
        # Split into chunks for multiple embeds if needed
        chunks = [commands_list[i:i+10] for i in range(0, len(commands_list), 10)]
        
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title=f"📋 Available Commands ({i+1}/{len(chunks)})",
                description="\n".join(chunk),
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
    
    @permissions.error
    async def permissions_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You need the `Manage Server` permission to manage command permissions.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PermissionsCog(bot))
