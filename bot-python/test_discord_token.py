#!/usr/bin/env python3
import discord
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_token():
    token = os.getenv('DISCORD_BOT_TOKEN') or os.getenv('DISCORD_TOKEN')
    
    print(f"Testing token: {token[:20]}...")
    print(f"Token length: {len(token)}")
    
    # Create a minimal bot to test token
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f"SUCCESS: Bot logged in as {client.user}")
        print(f"Bot ID: {client.user.id}")
        print(f"Bot is in {len(client.guilds)} guilds")
        await client.close()
    
    try:
        await client.start(token)
    except Exception as e:
        print(f"ERROR: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    asyncio.run(test_token())