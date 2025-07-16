#!/usr/bin/env python3
"""
NexGuard Bot Download Package Creator
Creates a complete downloadable package of all bot files in proper structure
"""

import os
import shutil
import zipfile
import json
from datetime import datetime

def create_download_package():
    """Create a complete download package of NexGuard bot files"""
    
    # Create package directory
    package_name = f"nexguard-bot-v2.3.2-{datetime.now().strftime('%Y%m%d')}"
    package_dir = f"downloads/{package_name}"
    
    # Clean up any existing package
    if os.path.exists("downloads"):
        shutil.rmtree("downloads")
    
    os.makedirs(package_dir, exist_ok=True)
    
    # Copy ALL current core bot files
    core_files = [
        "main.py",
        "app.py", 
        "run.py",
        "pyproject.toml",
        "uv.lock",
        "runtime.txt",
        "Procfile",
        "deploy.sh",
        "start.sh",
        "replit.md",
        "AI_WELCOME_GUIDE.md",
        "AUTOMOD_GUIDE.md",
        "AUTOREPLY_GUIDE.md",
        "DEPLOYMENT.md",
        "DEPLOYMENT_FIXES.md",
        "README.md",
        "deployment_test.py",
        "download_server.py",
        "create_download_package.py"
    ]
    
    for file in core_files:
        if os.path.exists(file):
            shutil.copy2(file, package_dir)
            print(f"Copied: {file}")
    
    # Copy nexguard directory structure with all current files
    if os.path.exists("nexguard"):
        shutil.copytree("nexguard", f"{package_dir}/nexguard")
        print("Copied: nexguard/ directory")
    
    # Copy dashboard with current files
    if os.path.exists("dashboard"):
        shutil.copytree("dashboard", f"{package_dir}/dashboard")
        print("Copied: dashboard/ directory")
    
    # Copy additional files that might exist
    additional_files = [
        "nexguard.log",
        "generated-icon.png",
        "install.sh"
    ]
    
    for file in additional_files:
        if os.path.exists(file):
            shutil.copy2(file, package_dir)
            print(f"Copied: {file}")
    
    # Create setup files
    create_setup_files(package_dir)
    
    # Create ZIP archive
    zip_path = f"{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    print(f"Package created: {zip_path}")
    print(f"Package size: {os.path.getsize(zip_path) / (1024*1024):.2f} MB")
    
    return zip_path

def create_setup_files(package_dir):
    """Create setup and configuration files"""
    
    # Update package info
    package_info = {
        "name": "NexGuard Discord Bot",
        "version": "2.3.2",
        "description": "Advanced Discord moderation bot with AI-powered auto-reply system",
        "author": "NexGuard Development Team",
        "license": "MIT",
        "created": datetime.now().strftime('%Y-%m-%d'),
        "features": [
            "64 slash commands",
            "Auto-reply system with smart keyword detection",
            "Advanced moderation tools",
            "AI-powered welcome messages",
            "Ticket system with transcripts",
            "Autorole assignment",
            "Comprehensive logging",
            "Web dashboard interface",
            "PostgreSQL database support",
            "Deployment-ready configuration"
        ],
        "recent_updates": [
            "Fixed auto-reply system broad keyword issue",
            "Added proper auto-reply rule creation guidelines", 
            "Optimized keyword filtering for better performance",
            "Enhanced embed response system",
            "Improved cooldown management",
            "Better database error handling",
            "Updated all documentation and guides",
            "Complete package with latest stable code"
        ]
    }
    
    with open(f"{package_dir}/package_info.json", "w") as f:
        json.dump(package_info, f, indent=2)
    
    # Create README.md
    readme_content = """# NexGuard Discord Bot v2.0.0

A comprehensive Discord moderation bot with advanced AI-powered features, designed to provide complete server protection, intelligent management, and rich user engagement tools.

## Features

- **50 Slash Commands** across 6 major categories
- **AI-Powered Welcome System** with OpenAI GPT-4o integration
- **Advanced AutoMod** with 5 detection types (spam, links, bad words, caps, mentions)
- **Comprehensive Logging** with 7 configurable log types
- **Advanced Ticket System** with modal forms and transcripts
- **Production Deployment** with HTTP health checks
- **Web Dashboard** for server management
- **Role-Based Permissions** with hierarchy validation

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   Create a `.env` file with:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_secret_key_for_dashboard
   ```

3. **Run the Bot**:
   ```bash
   python main.py
   ```

4. **Access Dashboard**:
   - Bot runs on port 5000 (health checks)
   - Dashboard runs on port 8080
   - Visit http://localhost:8080 for web interface

## Command Categories

### Moderation (10 commands)
- `/ban`, `/kick`, `/mute`, `/warn`, `/purge`
- `/unban`, `/unmute`, `/timeout`, `/slowmode`, `/lock`

### Welcome System (4 commands)
- `/welcome-setup`, `/welcome-template`, `/welcome-test`, `/welcome-stats`

### AutoMod (5 commands)
- `/automod-spam`, `/automod-links`, `/automod-badwords`, `/automod-words`, `/automod config`

### Ticket System (3 commands)
- `/ticket`, `/ticket-setup`, `/ticket-manage`

### Utilities (15 commands)
- `/ping`, `/userinfo`, `/serverinfo`, `/help`, `/embed`, and more

### Administration (13 commands)
- `/prefix`, `/changelog`, `/modrole`, `/logging`, `/permissions`, and more

## Documentation

- **AI Welcome Guide**: `AI_WELCOME_GUIDE.md`
- **AutoMod Guide**: `AUTOMOD_GUIDE.md`
- **Deployment Guide**: `DEPLOYMENT.md`
- **Troubleshooting**: `DEPLOYMENT_FIXES.md`

## Database

The bot uses SQLite for data persistence with the following tables:
- Guild settings and configurations
- User warnings and moderation logs
- Ticket system data
- Message and member event logs
- AutoMod violation tracking

## Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
- Compatible with Replit, Heroku, Railway, and other platforms
- Uses dual-purpose architecture (Discord bot + HTTP server)
- Health checks available at `/` and `/health`
- Bot statistics at `/status`

### Environment Variables
- `DISCORD_TOKEN`: Your Discord bot token (required)
- `OPENAI_API_KEY`: OpenAI API key for AI features (optional)
- `SECRET_KEY`: Secret key for dashboard sessions (optional)
- `PORT`: HTTP server port (default: 5000)

## Support

For issues, suggestions, or contributions:
1. Check the documentation files
2. Review the troubleshooting guide
3. Use the `/help` command for command information
4. Contact the development team through Discord

## Version History

- **v2.0.0**: Complete feature suite with AI, AutoMod, Dashboard
- **v1.5.0**: AI-powered welcome system
- **v1.4.0**: Advanced AutoMod system
- **v1.3.0**: Production deployment infrastructure
- **v1.2.0**: Comprehensive logging system
- **v1.1.0**: Ticket system and enhanced commands
- **v1.0.0**: Initial release with core moderation

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""
    
    with open(f"{package_dir}/README.md", "w") as f:
        f.write(readme_content)
    
    # Create .env.example
    env_example = """# NexGuard Bot Configuration
# Copy this file to .env and fill in your values

# Discord Bot Token (Required)
DISCORD_TOKEN=your_discord_bot_token_here

# OpenAI API Key (Optional - for AI welcome messages)
OPENAI_API_KEY=your_openai_api_key_here

# Dashboard Secret Key (Optional - for web dashboard)
SECRET_KEY=your_secret_key_for_dashboard_sessions

# Port Configuration (Optional - defaults to 5000)
PORT=5000
"""
    
    with open(f"{package_dir}/.env.example", "w") as f:
        f.write(env_example)
    
    # Create installation script
    install_script = """#!/bin/bash
# NexGuard Bot Installation Script

echo "Setting up NexGuard Discord Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your Discord bot token and other settings."
fi

# Create database directory
mkdir -p nexguard/database

echo "Setup complete!"
echo "Next steps:"
echo "1. Edit .env file with your bot token"
echo "2. Run: python main.py"
echo "3. Access dashboard at: http://localhost:8080"
"""
    
    with open(f"{package_dir}/install.sh", "w") as f:
        f.write(install_script)
    
    # Make install script executable
    os.chmod(f"{package_dir}/install.sh", 0o755)
    
    # Create package info file
    package_info = {
        "name": "NexGuard Discord Bot",
        "version": "2.0.0",
        "description": "Comprehensive Discord moderation bot with AI-powered features",
        "created_date": datetime.now().isoformat(),
        "features": [
            "50 slash commands across 6 categories",
            "AI-powered welcome messages with OpenAI GPT-4o",
            "Advanced AutoMod with 5 detection types",
            "Comprehensive logging with 7 configurable types",
            "Advanced ticket system with modal forms",
            "Production deployment with health checks",
            "Web dashboard for server management",
            "Role-based permissions with hierarchy validation"
        ],
        "requirements": [
            "Python 3.8+",
            "Discord Bot Token",
            "OpenAI API Key (optional)",
            "SQLite (included with Python)"
        ],
        "ports": {
            "bot_health": 5000,
            "dashboard": 8080
        }
    }
    
    with open(f"{package_dir}/package_info.json", "w") as f:
        json.dump(package_info, f, indent=2)

if __name__ == "__main__":
    zip_path = create_download_package()
    print(f"\nDownload package ready: {zip_path}")