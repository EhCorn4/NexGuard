#!/bin/bash
# Simple script to start the bot in the background

# Kill any existing bot processes
pkill -f "python3.*bot_only.py"

# Clean up old status file
rm -f /tmp/nexguard_bot_status.json

# Start the bot in the background
cd bot-python
nohup python3 simple_bot.py > /tmp/nexguard_bot.log 2>&1 &
echo $! > /tmp/nexguard_bot.pid

# Give some time for startup
sleep 2

# Check if process is running
if ps -p $(cat /tmp/nexguard_bot.pid 2>/dev/null) > /dev/null 2>&1; then
    echo "Bot process started successfully"
    echo "PID: $(cat /tmp/nexguard_bot.pid)"
    echo "Log file: /tmp/nexguard_bot.log"
    exit 0
else
    echo "Failed to start bot process"
    exit 1
fi