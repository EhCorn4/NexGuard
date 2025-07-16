#!/usr/bin/env python3
"""
Application entry point for NexGuard Discord Bot
This is an alternative entry point that can be used for deployment
"""

import os
import sys
import asyncio
import logging

# Ensure the current directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging for deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def run_application():
    """Run the NexGuard Discord Bot application"""
    try:
        # Import and run the main application
        from main import main
        
        print("🚀 Starting NexGuard Discord Bot...")
        print(f"📡 HTTP health check server will be available on port {os.getenv('PORT', 5000)}")
        
        # Check if Discord token is available
        if os.getenv('DISCORD_TOKEN'):
            print("✅ Discord token found - full bot functionality enabled")
        else:
            print("⚠️  No Discord token - running in HTTP-only mode for health checks")
        
        # Run the main application
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_application()