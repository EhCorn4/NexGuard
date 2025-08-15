#!/usr/bin/env python3
"""
Simple script to get all guild IDs that NexGuard is currently connected to
"""
import asyncio
import discord
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def get_guild_ids():
    """Get all guild IDs the bot is connected to"""
    
    # Create bot instance with minimal intents
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"✅ {bot.user.name} is connected to {len(bot.guilds)} guilds")
        print("\n📋 Guild List:")
        print("-" * 60)
        
        for i, guild in enumerate(bot.guilds, 1):
            print(f"{i:2d}. {guild.name}")
            print(f"    Guild ID: {guild.id}")
            print(f"    Members: {guild.member_count}")
            print(f"    Owner: {guild.owner}")
            print("-" * 60)
        
        print(f"\n📊 Summary:")
        print(f"Total Guilds: {len(bot.guilds)}")
        print(f"Total Members: {sum(guild.member_count for guild in bot.guilds if guild.member_count)}")
        
        # Create a simple list of just the IDs
        print(f"\n🔢 Guild IDs Only:")
        guild_ids = [str(guild.id) for guild in bot.guilds]
        print(", ".join(guild_ids))
        
        await bot.close()
    
    try:
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("❌ DISCORD_TOKEN not found in environment variables")
            return
            
        await bot.start(token)
    except Exception as e:
        print(f"❌ Error connecting to Discord: {e}")

if __name__ == "__main__":
    asyncio.run(get_guild_ids())