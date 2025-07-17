#!/usr/bin/env python3
"""
Alternative entry point for NexGuard Discord Bot - ensures proper startup
"""

import sys
import os
import asyncio
import logging

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import main function
from main import main

if __name__ == "__main__":
    print("Starting NexGuard Discord Bot...")
    print("Health check server will be available at http://localhost:5000")
    print("Discord bot will connect automatically if token is provided")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot shutdown requested.")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)