# NexGuard Discord Bot v2.0.0

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
