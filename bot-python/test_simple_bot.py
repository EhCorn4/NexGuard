#!/usr/bin/env python3
import discord
import os
import asyncio
import sys

async def test_simple_bot():
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    print(f"Testing with token: {token[:20]}...")
    print(f"Token format check: {len(token)} chars, {len(token.split('.'))} parts")
    
    # Test with minimal intents first
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = discord.Client(intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"✓ Bot connected as {bot.user}")
        print(f"✓ Bot ID: {bot.user.id}")
        print(f"✓ In {len(bot.guilds)} guilds")
        for guild in bot.guilds:
            print(f"  - {guild.name} (ID: {guild.id})")
        await bot.close()
    
    @bot.event
    async def on_error(event, *args, **kwargs):
        print(f"Error in {event}: {args}")
    
    try:
        await bot.start(token)
    except discord.LoginFailure as e:
        print(f"✗ Login failed: {e}")
        print("This usually means:")
        print("1. Token is invalid/expired")
        print("2. Bot doesn't have proper permissions")
        print("3. Token format is incorrect")
        return False
    except Exception as e:
        print(f"✗ Other error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_simple_bot())
    sys.exit(0 if success else 1)