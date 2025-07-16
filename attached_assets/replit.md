# NexGuard Discord Bot

## Overview

NexGuard is a comprehensive Discord moderation bot built with Python using the discord.py library. The bot provides advanced moderation features, server management tools, and utility commands with a focus on reliability and ease of use. **Now fully converted to modern Discord slash commands** for better user experience and discoverability.

## Recent Changes (July 16, 2025)

- **AUTO-REPLY SYSTEM FULLY DEBUGGED AND OPTIMIZED**: Complete keyword-based auto-reply system with embed responses
- **FIXED BROAD KEYWORD ISSUE**: Resolved problem where bot responded to every message due to overly general keywords
- **PROPER RULE CREATION**: Implemented guidelines for creating specific, targeted auto-reply rules
- **EXAMPLE RULES CREATED**: Discord invite link, server rules, and support help rules with specific keywords
- **INTELLIGENT KEYWORD FILTERING**: Uses specific phrases instead of common words to prevent false triggers
- **5 NEW AUTO-REPLY COMMANDS**: /autoreply-create, /autoreply-list, /autoreply-toggle, /autoreply-delete, /autoreply-stats
- **SMART KEYWORD DETECTION**: 4 match types (contains, exact, starts_with, ends_with) with case-insensitive scanning
- **INTELLIGENT MESSAGE FILTERING**: Auto-reply ignores links, GIFs, attachments, embeds, and system messages
- **CUSTOM EMBED RESPONSES**: Rich embed replies with customizable colors, titles, descriptions, and footers
- **COOLDOWN SYSTEM**: Per-rule cooldown management to prevent spam and abuse
- **DASHBOARD INTEGRATION**: Auto-reply API endpoints for web-based rule management
- **COMPREHENSIVE LOGGING**: Complete audit trail of auto-reply triggers and rule modifications
- **ENHANCED COMMAND COUNT**: Bot now has 64 slash commands (up from 59) with auto-reply functionality
- **PERMISSION SYSTEM**: Admin/moderator-only access with proper slash command authentication
- **DATABASE OPTIMIZATION**: Auto-reply tables with efficient indexing and query performance

## Previous Changes (July 14, 2025)

- **BOT-DASHBOARD INTEGRATION COMPLETE**: Full API connectivity between Discord bot and web dashboard
- **AUTHENTICATION SYSTEM IMPLEMENTED**: Secure bot token authentication for all API endpoints
- **API ENDPOINTS OPERATIONAL**: All 7 API endpoints now functional with proper authentication validation
- **REAL-TIME SYNCHRONIZATION**: Bot communicates with dashboard API using correct DISCORD_TOKEN environment variable
- **DASHBOARD COMMANDS WORKING**: 4 new slash commands (/config, /addcmd, /dashboard, /sync-config) integrated with API
- **ENHANCED COMMAND COUNT**: Bot now has 59 slash commands (up from 55) with dashboard integration features
- **UNIFIED MANAGEMENT**: Users can now manage bot settings from both Discord commands and web dashboard seamlessly
- **SECURITY IMPROVEMENTS**: Token validation system prevents unauthorized API access

## Previous Changes (July 11, 2025)

- **VERSION 2.3.1 COMPREHENSIVE CODE REVIEW & OPTIMIZATION**: Complete codebase analysis and security hardening
- **SECURITY IMPROVEMENTS**: Fixed all bare `except:` statements with proper exception handling
- **DATABASE STANDARDIZATION**: Created comprehensive `database_helper.py` with centralized connection management
- **CONSTANTS ORGANIZATION**: Added `constants.py` with 300+ centralized constants for emojis, colors, and messages
- **ERROR HANDLING ENHANCEMENT**: Improved error handling with specific exception types and logging
- **CODE QUALITY IMPROVEMENTS**: Addressed 53 files with 14,129 lines of code, standardized 91 database connections
- **SECURITY HARDENING**: Verified no SQL injection vulnerabilities, proper parameterized queries throughout
- **PERFORMANCE OPTIMIZATION**: Reduced hardcoded values, improved async/await patterns, eliminated potential issues
- **VERSION 2.3.0 AI ASSISTANT INTEGRATION**: Added comprehensive ChatGPT-powered AI assistant using OpenAI GPT-4o
- **CONVERSATIONAL AI**: Interactive AI chat with conversation memory and context awareness
- **3 NEW AI COMMANDS**: `/ai` for questions, `/ai-clear` for conversation reset, `/ai-status` for system info
- **SMART CONVERSATION MANAGEMENT**: Automatic conversation trimming and memory optimization
- **INTERACTIVE CONTROLS**: Follow-up questions and conversation management with Discord buttons
- **GUILD CONTEXT AWARENESS**: AI responses include server-specific context for better relevance
- **PRIVACY OPTIONS**: Public or private AI responses with ephemeral message support
- **COMPREHENSIVE OPTIMIZATION**: Achieved 16.6% overall code reduction (11,405 → 9,510 lines) while maintaining all 52 slash commands
- **VERSION 2.2.2 SIMPLIFIED TICKET SYSTEM**: Streamlined ticket creation with single green button interface
- **SINGLE BUTTON DESIGN**: Simplified `/ticket-panel` and `/ticket-embed` to show one green "Create Ticket" button
- **REMOVED COMPLEXITY**: Eliminated categories and priority levels for cleaner user experience
- **ENHANCED TICKET MODAL**: Simplified form with Subject, Description, and Additional Information fields
- **PERSISTENT BUTTON INTERACTIONS**: Buttons work permanently with custom IDs for reliable user interactions
- **CHANNEL SELECTION**: Ability to place ticket panels in specific channels for better organization
- **COLOR CUSTOMIZATION**: Support for hex codes and named colors for personalized embed appearance
- **FOOTER CUSTOMIZATION**: Custom footer text and branding options for ticket embeds
- **STREAMLINED USER EXPERIENCE**: Clean, simple ticket creation interface without overwhelming options
- **VERSION 2.2.0 ENHANCED TICKET SYSTEM**: Complete ticket system overhaul with advanced features
- **PRIORITY LEVELS**: Four priority levels (Low, Medium, High, Critical) with visual indicators
- **TICKET CATEGORIES**: Six categories (Bug Report, Feature Request, General Support, Account Issues, Technical Support, Billing)
- **STAFF ASSIGNMENT**: Automatic and manual ticket assignment to staff members
- **TICKET ANALYTICS**: Comprehensive analytics dashboard with category/priority breakdowns
- **ENHANCED DATABASE**: New columns for priority, category, assignment, and additional metadata
- **TICKET MANAGEMENT**: Advanced commands for priority changes, assignments, and cleanup
- **VISUAL INDICATORS**: Priority emojis in channel names and enhanced embed displays
- **RESPONSE TIME TRACKING**: Automatic calculation of average response times
- **INTERNAL NOTES**: Staff-only notes system for ticket management
- **TICKET TEMPLATES**: Category-specific forms with customized fields
- **VERSION 2.1.0 AUTOROLE SYSTEM**: Complete automatic role assignment with dropdown configuration
- **INTERACTIVE ROLE SELECTION**: Visual dropdown menu with role type indicators and member counts
- **AUTOROLE STATISTICS**: Comprehensive analytics and recent activity tracking
- **ADMIN CONTROLS**: Easy enable/disable, testing, and configuration management
- **AUTOMATIC ASSIGNMENT**: Instant role assignment on member join with permission validation
- **EVENT LOGGING**: All autorole actions logged for transparency and audit trail
- **PERMISSION CHECKS**: Role hierarchy validation and bot permission checking
- **VERSION 2.0.0 MEGA-UPDATE**: Complete NexGuard feature suite with comprehensive changelog
- **DOWNLOAD PACKAGE CREATED**: Complete bot package with all files in proper structure (0.31 MB)
- **INTEGRATED DOWNLOAD SYSTEM**: Added /bot and /download endpoints to main HTTP server
- **WEB DASHBOARD FOUNDATION**: Created Flask-based dashboard infrastructure for server management
- **COMPLETE PACKAGE STRUCTURE**: All bot files, documentation, and setup scripts included
- **AUTOMATED INSTALLATION**: install.sh script for easy setup and configuration
- **COMPREHENSIVE DOCUMENTATION**: README.md with complete setup instructions and feature overview
- **PRODUCTION-READY PACKAGE**: All deployment configurations and environment examples included
- Added 5 new moderation commands: unban, unmute, timeout, slowmode, lock/unlock
- Added 3 new utility commands: userinfo, serverinfo, avatar
- **Added comprehensive ticket system with modal forms, auto-channel creation, and transcripts**
- **Enhanced ticket setup with dropdown role selection showing ALL guild roles**
- **Fixed Discord API errors in /ticket-setup command that caused "application did not respond"**
- **Implemented two-step setup process: separate interfaces for text configuration and role selection**
- **Added comprehensive changelog system with automatic posting on bot restart**
- **Created advanced embed builder with interactive forms and customization options**
- **Fixed embed action buttons to properly integrate with ticket system**
- **Added detailed /help command with comprehensive command documentation**
- **Created /modrole system for role-based moderation permissions**
- **Implemented dynamic activity rotation system showing "Defending [server name]"**
- **Fixed database schema migration for custom moderation roles**
- **Added server-specific bot activity that updates based on recent interactions**
- **Created comprehensive Discord logging system with granular controls**
- **Added /logging command for configuring 7 different log types**
- **Implemented channel, role, server, and voice activity logging**
- **DEPLOYMENT ISSUES FULLY RESOLVED**: Complete deployment configuration with HTTP health checks
- **Enhanced main.py entry point**: Robust concurrent Discord bot + HTTP server architecture
- **Multiple deployment entry points**: main.py, app.py, run.py, and deploy.sh for different scenarios
- **Production-ready health endpoints**: /, /health, /status with proper error handling and bot statistics
- **Advanced deployment configuration**: Procfile, runtime.txt, pyproject.toml properly configured
- **Comprehensive error handling**: HTTP server continues running even if Discord bot fails
- **Port configuration**: Dynamic PORT detection with deployment platform compatibility
- **Deployment documentation**: DEPLOYMENT_FIXES.md with complete troubleshooting guide
- **ADVANCED AUTOMOD SYSTEM**: Complete automoderation engine with 5 detection types
- **Spam Protection**: Configurable rate limiting with message history tracking
- **Link Filtering**: Discord invite blocking and URL filtering with pattern recognition
- **Bad Words Filter**: Built-in dictionary + custom word lists with strict/lenient modes
- **Caps Lock Detection**: Percentage-based caps filtering with configurable thresholds
- **Mention Limits**: Separate limits for user and role mentions with smart detection
- **Punishment Escalation**: Progressive actions (delete, warn, timeout) with database logging
- **5 new automod commands**: /automod-spam, /automod-links, /automod-badwords, /automod-words
- **Interactive Configuration**: /automod config panel for easy setup and management
- **Enhanced database schema**: Added automod_settings JSON column for flexible configuration
- **Comprehensive documentation**: AUTOMOD_GUIDE.md with setup instructions and best practices
- **AI-POWERED WELCOME SYSTEM**: Intelligent personalized welcome messages using OpenAI GPT-4o
- **Dynamic Welcome Generation**: Context-aware messages based on server culture and member profiles
- **5 Welcome Tone Styles**: Friendly, Professional, Enthusiastic, Warm, and Gaming personalities
- **Custom Template System**: Flexible message templates with placeholder support
- **Welcome Analytics**: Statistics, testing, and performance monitoring
- **AI Integration**: OpenAI API integration with smart fallback to quality standard messages
- **4 new welcome commands**: /welcome-setup, /welcome-template, /welcome-test, /welcome-stats
- **Enhanced member events**: Automatic AI welcome message generation on member join
- **Comprehensive documentation**: AI_WELCOME_GUIDE.md with setup instructions and best practices
- Enhanced command descriptions and parameter validation
- Improved error handling and user feedback
- Bot now supports 55 different slash commands across multiple categories
- **AI Assistant Integration**: ChatGPT-powered conversational AI with memory and context awareness

### Ticket System Features:
- **Enhanced Setup Interface**: `/ticket-setup` with dropdown role selection showing ALL guild roles
- **Visual Role Selection**: Dropdown shows user roles (👤) vs bot roles (🤖) with member counts
- **Two-Step Configuration**: Separate interfaces for text customization and role selection
- **Simple User Command**: `/ticket` provides direct ticket creation without needing to find the panel
- **Modal Forms**: Users fill out detailed forms with subject and description
- **Auto-Channel Creation**: Private channels created automatically with proper permissions
- **Role-Based Access**: Configurable support roles get pinged and can view/manage tickets
- **Ticket Management**: Close, view info, and track statistics
- **Transcript Generation**: Full conversation history export to text files
- **Database Integration**: SQLite storage for persistent ticket tracking and configuration
- **Admin Tools**: List tickets, cleanup deleted channels, detailed statistics

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture
- **Framework**: discord.py (Discord API wrapper)
- **Database**: SQLite with custom database manager
- **Structure**: Modular cog-based architecture
- **Logging**: Comprehensive logging system with file and console output
- **Configuration**: Environment variables with .env file support

### Key Design Decisions
- **SQLite Database**: Chosen for simplicity and portability, avoiding external database dependencies
- **Modular Cogs**: Commands organized into separate cogs for better maintainability and organization
- **Permission System**: Role-based permissions with hierarchical checking
- **Event-Driven Logging**: Automatic logging of member joins/leaves and message events

## Key Components

### Bot Core (`index.py`)
- Main bot class inheriting from `commands.Bot`
- Database initialization and connection management
- Dynamic prefix system supporting per-guild customization
- Comprehensive error handling and logging setup

### Database Layer (`database/persistent_db.py`)
- SQLite database manager with connection pooling
- Tables for guild settings, warnings, mutes, member logs, message logs, and permissions
- Automatic table creation and schema management

### Command Structure
- **Moderation**: Ban, kick, mute, warn, purge, unban, unmute, timeout, slowmode, lock/unlock (slash commands)
- **Administration**: Prefix management, moderation role configuration, changelog system configuration, Discord logging setup (slash commands)
- **AutoMod**: Comprehensive automoderation with spam, links, bad words, caps, and mention detection (slash commands)
- **Auto-Reply**: Keyword-based automatic responses with 4 match types, custom embeds, cooldown system, and rule management (slash commands)
- **Utilities**: Ping, user info, server info, avatar display, detailed help system, embed builder, AI assistant (slash commands)
- **Tickets**: Advanced ticket system with modal forms, auto-channel creation, transcripts (slash commands)
- **Welcome System**: AI-powered personalized welcome messages with 5 tone styles and custom templates (slash commands)
- **Changelog**: Automatic changelog posting with channel configuration (slash commands)
- **Embed Builder**: Interactive embed creation with JSON support and customization (slash commands)
- **Modern Interface**: All commands use Discord's native slash command system for better discoverability

### Event System
- **Member Events**: Join/leave logging with auto-role assignment
- **Message Events**: Edit/delete logging with database persistence
- **Ready Event**: Bot initialization, changelog posting, and dynamic activity rotation
- **Activity Rotation**: Dynamic server-specific activity showing "Defending [server name]" based on recent interaction activity
- **Discord Logging**: Comprehensive logging system with 7 configurable log types (message, member, moderation, channel, role, server, voice events)

### Permission System
- Custom permission checks for moderator and admin roles
- Role hierarchy validation with configurable moderation roles
- Command-specific permission overrides
- `/modrole` system for setting minimum role requirements

## Data Flow

### Command Processing
1. Message received → Prefix check → Command parsing
2. Permission validation → Role hierarchy check
3. Command execution → Database logging → Response generation

### Event Handling
1. Discord event triggered → Event listener activated
2. Data extraction and validation → Database storage
3. Log channel notification (if configured)

### Database Operations
1. Connection establishment → Query execution
2. Data validation and sanitization → Transaction commit
3. Connection cleanup and error handling

### Discord Logging System
1. Event detection → Permission/setting check
2. Log formatting and embed creation → Database storage
3. Channel delivery with error handling

## External Dependencies

### Core Libraries
- `discord.py`: Discord API interaction
- `python-dotenv`: Environment variable management
- `sqlite3`: Database operations (built-in)
- `asyncio`: Asynchronous operations
- `logging`: Comprehensive logging system
- `openai`: OpenAI API integration for AI-powered features

### Optional Features
- Environment-based configuration
- JSON-based embed creation
- Changelog system with version tracking
- AI-powered welcome message generation

## Deployment Strategy

### Development Setup
- Local SQLite database file
- Environment variables for bot token and configuration
- File-based logging with rotation support

### Production Deployment (Fixed)
- **Hybrid Application**: Discord bot + HTTP health check server running simultaneously
- **Health Endpoints**: `/` and `/health` for deployment health checks
- **Status Endpoint**: `/status` provides bot statistics in JSON format
- **Port Configuration**: Serves HTTP on port 5000 for Replit deployment compatibility
- **Dual-Purpose main.py**: Entry point handles both Discord connection and HTTP server

### Production Considerations
- Database file persistence across restarts
- Log file management and rotation
- Environment variable security
- Bot token protection
- HTTP server for deployment health checks

### Scalability Notes
- Single-file SQLite database suitable for small to medium servers
- Modular cog system allows easy feature addition/removal
- Event-driven architecture supports high message volumes
- Connection pooling ready for database upgrades
- HTTP server minimal overhead for deployment compatibility

### Configuration Management
- Guild-specific settings stored in database
- Dynamic prefix system with fallback defaults
- Per-guild role and channel configurations
- Permission overrides at command level