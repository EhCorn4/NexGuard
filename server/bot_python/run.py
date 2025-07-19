#!/usr/bin/env python3

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the bot
from server.bot_python.bot import main

if __name__ == "__main__":
    print("🚀 Starting NexGuard Python Bot...")
    asyncio.run(main())