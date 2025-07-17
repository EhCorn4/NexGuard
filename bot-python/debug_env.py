#!/usr/bin/env python3
import os
import sys

print("=== Environment Debug ===")
print(f"DISCORD_BOT_TOKEN length: {len(os.environ.get('DISCORD_BOT_TOKEN', ''))}")
print(f"DISCORD_TOKEN length: {len(os.environ.get('DISCORD_TOKEN', ''))}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Test the token selection logic from bot_only.py
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN') or os.getenv('DISCORD_TOKEN')
print(f"Selected token length: {len(DISCORD_TOKEN) if DISCORD_TOKEN else 0}")
if DISCORD_TOKEN:
    print(f"Token starts with: {DISCORD_TOKEN[:10]}...")
else:
    print("No token found!")