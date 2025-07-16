#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test token reading
token = os.getenv('DISCORD_TOKEN') or os.getenv('DISCORD_BOT_TOKEN')
print(f"Token exists: {token is not None}")
print(f"Token type: {type(token)}")

if token:
    print(f"Token length: {len(token)}")
    print(f"Token starts with: {token[:10]}...")
    print(f"Token ends with: ...{token[-10:]}")
    
    # Check if it looks like a valid Discord token
    if len(token) >= 50 and '.' in token:
        print("Token format looks correct for Discord bot token")
    else:
        print("Token format seems incorrect for Discord bot token")
else:
    print("No token found in environment variables")