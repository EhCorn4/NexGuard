"""
Permission checks for NexGuard commands
"""

import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import logging

logger = logging.getLogger(__name__)

def is_moderator():
    """Check if user is a moderator"""
    async def predicate(interaction: discord.Interaction):
        # Check if user has administrator permissions
        if interaction.user.guild_permissions.administrator:
            return True
        
        # Check if user has manage guild permissions
        if interaction.user.guild_permissions.manage_guild:
            return True
        
        # Check if user has a moderator role from database
        try:
            conn = sqlite3.connect("nexguard/database/nexguard.db")
            cursor = conn.cursor()
            cursor.execute('SELECT mod_role_id FROM guild_settings WHERE guild_id = ?', (interaction.guild.id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                mod_role = interaction.guild.get_role(result[0])
                if mod_role and mod_role in interaction.user.roles:
                    return True
        except Exception as e:
            logger.error(f"Error checking moderator role: {e}")
        
        return False
    
    return app_commands.check(predicate)