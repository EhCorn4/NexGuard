#!/bin/bash

# NexGuard Discord Bot Deployment Script
# This script ensures proper deployment with HTTP health checks

echo "=== NexGuard Discord Bot Deployment ==="
echo "Timestamp: $(date)"
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

# Check for required environment variables
if [ -z "$DISCORD_TOKEN" ]; then
    echo "WARNING: DISCORD_TOKEN environment variable not set"
    echo "Bot will start in HTTP-only mode for health checks"
else
    echo "✓ Discord token found (length: ${#DISCORD_TOKEN})"
fi

# Set PORT if not already set
if [ -z "$PORT" ]; then
    export PORT=5000
    echo "✓ PORT set to default: 5000"
else
    echo "✓ PORT configured: $PORT"
fi

# Start the application
echo "Starting NexGuard Discord Bot..."
echo "HTTP health check server will be available at: http://0.0.0.0:$PORT"

# Execute the main application
exec python main.py