"""
Helper utilities for NexGuard
"""

import discord
import logging

logger = logging.getLogger(__name__)

class EmbedBuilder:
    """Helper class for building Discord embeds"""
    
    @staticmethod
    def success(title, description):
        """Create a success embed"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=0x00ff00
        )
        return embed
    
    @staticmethod
    def error(title, description):
        """Create an error embed"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=0xff0000
        )
        return embed
    
    @staticmethod
    def warning(title, description):
        """Create a warning embed"""
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=0xff9900
        )
        return embed
    
    @staticmethod
    def info(title, description):
        """Create an info embed"""
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=0x5865f2
        )
        return embed