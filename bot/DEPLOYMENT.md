# NexGuard Discord Bot - Deployment Guide

## Overview
This Discord bot is designed as a hybrid application that runs both a Discord bot and an HTTP health check server simultaneously for deployment compatibility.

## Application Architecture
- **Discord Bot**: Connects to Discord API and provides moderation/utility commands
- **HTTP Health Check Server**: Runs on port 5000 for deployment health checks
- **Database**: SQLite for persistent data storage

## Health Check Endpoints
- `/` - Basic health check endpoint
- `/health` - Alternative health check endpoint
- `/status` - Bot status with statistics (JSON response)

## Deployment Configuration

### Run Command
The application should be started with:
```bash
python main.py
```

### Environment Variables Required
- `DISCORD_TOKEN` - Your Discord bot token
- `PORT` - HTTP server port (defaults to 5000 if not set)

### Port Configuration
- **HTTP Server**: Port 5000 (configurable via PORT environment variable)
- **Discord Bot**: Uses Discord's WebSocket connection (no port needed)

## Deployment Verification
You can verify the deployment is working by:

1. **Health Check**: `curl https://your-domain.com/` should return "NexGuard Discord Bot is running!"
2. **Status Check**: `curl https://your-domain.com/status` should return JSON with bot statistics
3. **Discord Connection**: Bot should appear online in Discord

## Troubleshooting

### Common Issues
1. **Health checks failing**: Ensure PORT environment variable is set correctly
2. **Discord bot not connecting**: Verify DISCORD_TOKEN is set and valid
3. **Application not starting**: Check logs for specific error messages

### Logs
Application logs are written to:
- Console output (stdout)
- File: `nexguard.log`

## Files for Deployment
- `main.py` - Main application entry point
- `run.py` - Alternative startup script
- `start.sh` - Bash startup script
- `Procfile` - Process file for deployment platforms
- `runtime.txt` - Python runtime specification
- `pyproject.toml` - Python dependencies