#!/bin/bash

# Kill any existing bot processes
pkill -f "python3.*index.py" || true

# Start the bot in the background
cd bot
nohup python3 index.py > /tmp/nexguard_bot.log 2>&1 &

# Store the PID
echo $! > /tmp/nexguard_bot.pid

echo "Bot started with PID: $!"