#!/usr/bin/env python3
"""
Simple startup check for bot - creates a status file when bot is ready
"""
import os
import time
import json
import asyncio
from datetime import datetime

def create_status_file(status="starting"):
    """Create a status file to indicate bot state"""
    status_data = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid()
    }
    
    with open("/tmp/nexguard_bot_status.json", "w") as f:
        json.dump(status_data, f, indent=2)

async def bot_ready_callback():
    """Called when bot is ready"""
    create_status_file("ready")
    print("Bot status file created - ready")

def check_bot_status():
    """Check if bot is ready based on status file"""
    try:
        with open("/tmp/nexguard_bot_status.json", "r") as f:
            status_data = json.load(f)
            return status_data.get("status") == "ready"
    except FileNotFoundError:
        return False

if __name__ == "__main__":
    create_status_file("starting")
    print("Bot startup check initialized")