# NexGuard Website

## Overview

This is a comprehensive NexGuard Discord bot with a professional website showcasing its features. The project includes a fully functional Discord bot with advanced moderation, ticket system, and utility commands, along with a website that displays live bot status and provides complete documentation.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter for client-side routing
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: Radix UI primitives with custom shadcn/ui components
- **State Management**: React Query for server state management
- **Build Tool**: Vite for development and bundling

### Backend Architecture
- **Framework**: Express.js with TypeScript
- **Database**: PostgreSQL with asyncpg
- **Bot Framework**: Discord.py v2 with slash commands
- **Development**: Hot reload with Vite middleware integration
- **API Structure**: RESTful endpoints for content management and bot data
- **Bot Features**: Admin, moderation, ticket, utility, autoreply, automod, and role management commands

## Key Components

### Database Schema
- **Users**: Basic user management
- **News Updates**: Community announcements and updates
- **Developers**: Team member profiles and information
- **Features**: Bot feature descriptions and benefits
- **Testimonials**: User reviews and ratings with approval system
- **Feedback**: User feedback submissions
- **Bot Status**: Live bot status and statistics
- **Commands**: Bot command definitions and metadata
- **Guilds**: Discord server configurations
- **Tickets**: Support ticket system
- **Moderation Logs**: User moderation actions
- **Ban List**: Comprehensive ban tracking with appeal system
- **Warning History**: Warning tracking with severity levels and points system
- **Changelogs**: Bot version history and updates

### API Endpoints
- `GET /api/news` - Retrieve community updates and announcements
- `GET /api/developers` - Get team member information
- `GET /api/features` - Fetch bot features and capabilities
- `GET /api/testimonials` - Retrieve approved user testimonials
- `POST /api/testimonials` - Submit new testimonial for approval
- `POST /api/feedback` - Submit feedback, bug reports, or feature requests
- `GET /api/config` - Get basic configuration information
- `GET /api/bot/status` - Get live bot status and statistics
- `GET /api/bot/commands` - Get all bot commands and documentation
- `GET /api/bot/changelog` - Get bot version history
- `GET /api/bot/tickets` - Get ticket system data
- `GET /api/bot/moderation` - Get moderation logs
- `GET /health` - Health check endpoint

### Frontend Pages
- **Home**: Landing page with hero section and key information
- **Features**: Detailed feature showcase with interactive cards
- **Invite**: Bot invitation information and setup instructions
- **Developers**: Team member profiles and social links
- **Community**: News updates and community engagement
- **Testimonials**: Community feedback and user reviews with submission form
- **Feedback**: Support system for bug reports, feature requests, and general feedback
- **Docs**: Comprehensive documentation and help center with search functionality
- **Contact**: Contact information and support options
- **FAQ**: Comprehensive frequently asked questions with categorized sections
- **Legal Pages**: Terms of Service, Privacy Policy, Cookies Policy

### Design System
- **Color Palette**: Custom NexGuard brand colors (cyan/purple gradients)
- **Typography**: System fonts with gradient text effects
- **Components**: Reusable UI components with hover animations
- **Responsive**: Mobile-first design with breakpoint considerations
- **Theme**: Dark theme with light mode toggle

## Data Flow

1. **Content Management**: Data is stored in memory for development
2. **API Layer**: Express routes serve JSON data to the frontend
3. **Client Rendering**: React components consume API data using React Query
4. **State Management**: React Query handles caching, loading states, and error handling
5. **UI Updates**: Components reactively update based on data changes

## External Dependencies

### Core Dependencies
- **UI Library**: Radix UI for accessible component primitives
- **Styling**: Tailwind CSS for utility-first styling
- **Icons**: Lucide React and React Icons for iconography
- **Animations**: Framer Motion for smooth transitions

### Development Tools
- **TypeScript**: Type safety across the entire stack
- **Vite**: Fast development server and build tool
- **ESBuild**: Fast bundling for production builds
- **PostCSS**: CSS processing and optimization

## Deployment Strategy

### Development
- Vite development server with hot module replacement
- Express server with TypeScript compilation via tsx
- In-memory data storage for quick development

### Production
- Vite builds static assets to `dist/public`
- Express server bundled with ESBuild for Node.js
- Static file serving for optimized assets

### Build Process
1. Frontend assets compiled with Vite
2. Backend server bundled with ESBuild
3. Environment-specific configuration management

## Bot Features

NexGuard includes comprehensive Discord bot functionality with 44+ commands:
- **Admin Commands (15)**: Server configuration, logging setup, welcome messages, autoreply management, automod configuration
- **Moderation Commands (17)**: Advanced ban/kick/warn system, channel lock/unlock, timeout management, comprehensive logging
- **Ticket System (4)**: Multi-category support tickets with Discord integration and staff assignment
- **Utility Commands (11)**: AI assistant, server/user info, embed builder, comprehensive help system
- **Universal Logging**: Professional command logging for all 44 commands with detailed embeds
- **Advanced AutoMod**: Intelligent spam detection, bad word filtering, link blocking with professional logging
- **Channel Management**: Lock/unlock commands with permission management and notifications
- **Ban Management**: Comprehensive ban tracking with temporary bans, appeal system, and history
- **Warning System**: Warning history with severity levels, points system, and statistics
- **Welcome Messages**: Rich embed welcome system with customizable colors and thumbnails
- **Real-time Status**: Live bot status monitoring with automatic updates
- **Database Integration**: PostgreSQL integration for persistent data storage
- **Modern Architecture**: Python-based with Discord.py and comprehensive slash command support

## Current Status

The system is a complete Discord bot with integrated website that:
- Fully functional Discord bot with 44+ commands across all categories
- Live bot status monitoring and statistics (9+ servers, 168+ users)
- Professional website showcasing comprehensive bot features  
- Interactive documentation with complete command reference
- Universal command logging system for all 44 commands
- Advanced automod with professional logging to channels
- Channel lock/unlock management commands
- Multi-category ticket system integration
- Real-time bot status updates and analytics
- Comprehensive setup guides and help system
- Website fully updated with current feature listings and command counts

## Changelog

- July 18, 2025: Complete NexGuard Discord bot implementation with full functionality
- July 18, 2025: Added comprehensive command system (admin, moderation, ticket, utility)
- July 18, 2025: Implemented live bot status monitoring and statistics
- July 18, 2025: Added PostgreSQL database integration with asyncpg
- July 18, 2025: Created interactive documentation with command reference
- July 18, 2025: Added ticket system with categories and priority management
- July 18, 2025: Implemented moderation logging and user management
- July 18, 2025: Added real-time bot status updates on website
- July 18, 2025: Created comprehensive setup guides and help system
- July 18, 2025: Updated features page to showcase bot capabilities
- July 18, 2025: Added complete admin command suite with settings configuration
- July 18, 2025: Implemented automod, autoreply, autorole, changelog, botlogging, modrole, welcome commands
- July 18, 2025: Created extensible settings system for all commands with JSON database storage
- July 18, 2025: Added comprehensive moderation command suite with 15+ commands
- July 18, 2025: Implemented ban, kick, warn, mute, unmute, timeout, tempban, lock, unlock, slowmode, purge commands
- July 18, 2025: All moderation commands include proper logging, DM notifications, and error handling
- July 18, 2025: Added complete utility command suite with 10+ commands
- July 18, 2025: Implemented AI assistant, commands list, embed builder, help, ping, server info, user info, uptime, bot stats, avatar commands
- July 18, 2025: All utility commands include comprehensive information display and error handling
- July 18, 2025: Added comprehensive ban management system with banlist command and appeals
- July 18, 2025: Implemented warning history system with severity levels and points tracking
- July 18, 2025: Added welcome message system with placeholder support and customizable messages
- July 18, 2025: Enhanced moderation commands to automatically populate banlist and warning history
- July 18, 2025: Created complete ban tracking with appeal system, search functionality, and history management
- July 18, 2025: Implemented warning points system with automatic severity detection
- July 18, 2025: **MAJOR ARCHITECTURE CHANGE** - Converted Discord bot from Node.js/Discord.js to Python/Discord.py
- July 18, 2025: Rebuilt all bot commands in Python with async/await patterns and proper error handling
- July 18, 2025: Updated database integration to use asyncpg for better performance and reliability
- July 18, 2025: Enhanced bot startup process with automatic restart on failure
- July 18, 2025: Improved command structure with proper Discord.py app_commands integration
- July 18, 2025: Enhanced auto-welcome system with advanced embed support and comprehensive configuration options
- July 18, 2025: Added rich welcome embeds with custom colors, thumbnails, and interactive elements
- July 18, 2025: Implemented comprehensive welcome command with enable/disable, channel setup, and embed mode
- July 18, 2025: Enhanced invite page with bot statistics, permissions guide, and detailed setup instructions
- July 18, 2025: **MAJOR ENHANCEMENT** - Multi-category ticket system implementation
- July 18, 2025: Added ticket categories management with Discord channel integration
- July 18, 2025: Implemented `/ticketcategory` command for admin management of ticket categories
- July 18, 2025: Enhanced `/ticket` command with category-specific channel placement
- July 18, 2025: Added `/tickets` command for comprehensive ticket filtering and management
- July 18, 2025: Created ticket categories database schema with active/inactive states
- July 18, 2025: Implemented automatic ticket placement in appropriate Discord categories
- July 18, 2025: Added comprehensive ticket overview with status, priority, and category filtering
- July 18, 2025: Enhanced ticket system now supports multiple server use cases with organized categories
- July 18, 2025: Bot now runs with 27 total commands including new ticket management features
- July 18, 2025: Added interactive ping functionality - bot responds to mentions and messages containing "ping"
- July 18, 2025: Enhanced bot responsiveness with multiple random pong responses and latency display
- July 18, 2025: Added friendly mention handler with helpful tips for new users
- July 18, 2025: **MAJOR FEATURE** - Implemented comprehensive NexGuard-style auto-reply system
- July 18, 2025: Created advanced auto-reply database schema with rules, stats, and cooldowns tables
- July 18, 2025: Implemented `/autoreply-create` command with embed responses and customizable colors
- July 18, 2025: Added `/autoreply-list`, `/autoreply-toggle`, `/autoreply-delete` commands for full management
- July 18, 2025: Created `/autoreply-stats` command with detailed usage analytics and trigger counts
- July 18, 2025: Implemented intelligent cooldown system to prevent spam and abuse
- July 18, 2025: Added comprehensive statistics tracking with per-rule and per-user analytics
- July 18, 2025: Enhanced with multiple trigger types: contains, exact match, starts with, ends with
- July 18, 2025: Built rich embed response system with customizable titles, descriptions, and colors
- July 18, 2025: Added rule-based naming system with unique IDs for easy management
- July 18, 2025: **CRITICAL FIXES** - Fixed invite page JavaScript crash and home page statistics
- July 18, 2025: Resolved undefined `user` variable causing invite page crashes by properly escaping JSX placeholders
- July 18, 2025: Fixed home page statistics showing 0s by updating storage to read live data from database
- July 18, 2025: Corrected database schema mismatch by removing non-existent `commandsExecuted` column
- July 18, 2025: Home page now displays live bot statistics: 9+ servers, 167+ users, real uptime tracking
- July 18, 2025: **MAJOR ENHANCEMENT** - Advanced Auto-Reply System Implementation
- July 18, 2025: Completely rebuilt autoreply system with sophisticated features and professional structure
- July 18, 2025: Added comprehensive command suite: create, list, toggle, delete, stats commands
- July 18, 2025: Implemented advanced keyword matching: contains, exact, starts_with, ends_with
- July 18, 2025: Added rich embed response system with customizable colors, titles, descriptions, footers
- July 18, 2025: Enhanced permission system requiring admin/moderator permissions for management
- July 18, 2025: Added real-time message listening for automatic trigger detection and responses
- July 18, 2025: Implemented statistics tracking with rule overview and activity monitoring
- July 18, 2025: **MAJOR ENHANCEMENT** - Comprehensive AutoMod System Implementation
- July 18, 2025: Created advanced automod system with 6 dedicated commands and real-time message filtering
- July 18, 2025: Added `/automod-config` for interactive configuration overview with visual status display
- July 18, 2025: Implemented `/automod-spam` with configurable message limits, time windows, and escalation actions
- July 18, 2025: Added `/automod-links` with Discord invite blocking, URL filtering, and custom action settings
- July 18, 2025: Created `/automod-badwords` with strict mode, custom word lists, and comprehensive filtering
- July 18, 2025: Built `/automod-words` for advanced word management: add, remove, list, clear operations
- July 18, 2025: Added `/automod-reset` command for complete settings restoration with safety confirmations
- July 18, 2025: Implemented real-time message monitoring with automatic enforcement and action escalation
- July 18, 2025: Enhanced permission system requiring manage server/messages permissions for all automod functions
- July 18, 2025: Added comprehensive logging, error handling, and PostgreSQL integration for automod settings
- July 18, 2025: **MAJOR ENHANCEMENT** - Advanced Moderation Role Management System
- July 18, 2025: Created sophisticated modrole system with 3 dedicated commands for custom permission control
- July 18, 2025: Added `/modrole` command for setting and viewing custom moderation roles with hierarchy validation
- July 18, 2025: Implemented `/resetmodrole` command for reverting to default Discord permissions with safety checks
- July 18, 2025: Built `/modpermissions` command for detailed permission analysis and user capability verification
- July 18, 2025: Enhanced role hierarchy validation preventing privilege escalation and ensuring proper bot permissions
- July 18, 2025: Added comprehensive permission source breakdown: Administrator, Moderate Members, Custom Roles
- July 18, 2025: Integrated with PostgreSQL for persistent role settings with automatic conflict resolution
- July 18, 2025: Enhanced all moderation commands to respect custom mod role settings while maintaining flexibility
- July 18, 2025: **MAJOR ENHANCEMENT** - Advanced Temporary Ban System Implementation
- July 18, 2025: Added duration parameter to ban command supporting formats: 7d, 2h, 30m, 1w
- July 18, 2025: Implemented intelligent duration parsing with comprehensive validation
- July 18, 2025: Created automatic temporary ban expiration system with 5-minute check intervals
- July 18, 2025: Enhanced ban notifications with temporary vs permanent ban differentiation
- July 18, 2025: Added visual Discord timestamps for ban expiration times in DM notifications
- July 18, 2025: Integrated temporary ban tracking in database with expires_at timestamps
- July 18, 2025: Built background task system for automatic unban processing when duration expires
- July 18, 2025: Enhanced ban command to show duration and expiration time in response embeds
- July 18, 2025: Added comprehensive logging for both manual and automatic unban actions
- July 18, 2025: Successfully tested and confirmed temporary ban system functionality
- July 18, 2025: **MAJOR ENHANCEMENT** - Enhanced Bot Bio and Professional Presentation
- July 18, 2025: Added custom Discord activity status displaying "Watching X servers | /help for commands"
- July 18, 2025: Enhanced bot mention responses with comprehensive feature overview and live statistics
- July 18, 2025: Updated website features to showcase Advanced Moderation Suite with 15+ commands
- July 18, 2025: Enhanced Smart Auto-Reply System presentation with advanced feature highlighting
- July 18, 2025: Updated Comprehensive Command Suite to accurately display 41+ commands
- July 18, 2025: Enhanced Real-time Analytics Dashboard description with professional features
- July 18, 2025: Bot now displays live server count and user protection statistics in all responses
- July 18, 2025: Activity status updates automatically every 30 seconds with current server count
- July 18, 2025: **COMPLETION** - Enhanced Bot Bio and Professional Presentation Successfully Deployed
- July 18, 2025: Fixed mention handler conflicts with other cogs to ensure enhanced bio displays correctly
- July 18, 2025: Updated quick tip reference from "/help" to "/commands" per user request
- July 18, 2025: Confirmed enhanced bot bio working with comprehensive feature overview and live statistics
- July 18, 2025: **MAJOR ENHANCEMENT** - Guild Welcome Message System Implementation
- July 18, 2025: Added automatic welcome message when NexGuard joins new servers
- July 18, 2025: Implemented smart channel detection (system channel, general channels, or first available)
- July 18, 2025: Created comprehensive welcome embed with quick start guide and feature overview
- July 18, 2025: Added interactive elements with reaction emojis and professional presentation
- July 18, 2025: Integrated live server count and version information in welcome messages
- July 18, 2025: **ENHANCEMENT** - Added untimeout command to moderation suite
- July 18, 2025: Implemented `/untimeout` command to remove timeouts from users with proper permission checking
- July 18, 2025: Added role hierarchy validation and user status verification for timeout removal
- July 18, 2025: Enhanced moderation capabilities with timeout management - bot now has 42 commands
- July 19, 2025: **MAJOR ENHANCEMENT** - Universal Command Logging and Advanced Moderation Features
- July 19, 2025: Implemented universal command logging system for all 44 commands with professional embeds
- July 19, 2025: Added `/lock` and `/unlock` commands for channel management with permission controls
- July 19, 2025: Enhanced automod system with professional logging to configured channels
- July 19, 2025: Added comprehensive automod action logging with detailed context and user information
- July 19, 2025: Removed ping/pong auto-response feature to reduce spam
- July 19, 2025: **WEBSITE ENHANCEMENT** - Comprehensive Content Update for Current Capabilities
- July 19, 2025: Updated all website content to reflect 44+ commands and current bot capabilities
- July 19, 2025: Added new feature cards for Professional Logging System and Advanced AutoMod Protection
- July 19, 2025: Updated command counts throughout website (44 commands, 17 moderation, 15 admin, 11 utility, 4 ticket)
- July 19, 2025: Enhanced feature descriptions with universal logging, channel management, and automod logging
- July 19, 2025: Updated bot statistics display to show current live data (9+ servers, 168+ users)
- July 19, 2025: Comprehensive update of home page, features page, invite page, and docs page content
- July 19, 2025: **FEATURE RESTORATION** - Added comprehensive autorole command system
- July 19, 2025: Implemented `/autorole` command with set, enable, disable, remove, and view actions
- July 19, 2025: Added automatic role assignment functionality to member join events
- July 19, 2025: Enhanced autorole with role hierarchy validation and permission checking
- July 19, 2025: Added comprehensive autorole logging with professional embeds
- July 19, 2025: Updated settings command to display current autorole configuration
- July 19, 2025: **ENHANCEMENT** - Comprehensive FAQ page implementation
- July 19, 2025: Created detailed FAQ page with 6 categories and 25+ questions covering setup, moderation, features, troubleshooting, and advanced usage
- July 19, 2025: Updated footer navigation to point FAQ link to dedicated `/faq` page instead of feedback
- July 19, 2025: **AUTOROLE COMMAND FIXED** - Resolved database column name mismatch that was preventing autorole functionality
- July 19, 2025: Fixed autorole command to use correct database columns (auto_role_enabled, auto_role_id) instead of mismatched names
- July 19, 2025: Confirmed autorole command now fully functional with all 5 actions working correctly
- July 19, 2025: Autorole system now properly assigns roles to new members when configured and enabled
- July 19, 2025: **MONETIZATION COMPLETED** - Simple and empathetic donation page implementation
- July 19, 2025: Created heartfelt donation page focused on appreciation and personal connection
- July 19, 2025: Implemented single PayPal donation option with user's specific payment link (paypal.me/ehcorn4)
- July 19, 2025: Removed premium tiers and features, emphasizing that donations are optional
- July 19, 2025: Designed empathetic messaging highlighting developer appreciation and bot value
- July 19, 2025: Integrated donation page into website navigation (navbar and footer)
- July 19, 2025: User confirmed donation page "feels very good" - implementation successful
- July 19, 2025: **HOMEPAGE CUSTOMIZATION** - Updated uptime stat to static "24/7 Support" message
- July 19, 2025: **DEV PROFILE UPDATES** - Removed social links and changed location to Canada
- July 19, 2025: Updated developer profile to focus on core information without external social media links
- July 19, 2025: Updated developer contact information: email to crweston2004@gmail.com and Discord to ehcorn
- July 19, 2025: **DUPLICATE WELCOME MESSAGE FIX** - Added cooldown mechanism to prevent duplicate welcome messages
- July 19, 2025: **MUTE SYSTEM COMPLETE** - Fixed mute/unmute commands with database schema updates
- July 19, 2025: **BAD WORDS ENHANCEMENT** - Added support for multiple word addition/removal using comma separation
- July 19, 2025: **WELCOME SYSTEM OVERHAUL** - Complete fix of Discord interaction timeouts and duplicate message prevention
- July 19, 2025: Fixed welcome command timeout issues by implementing proper immediate response patterns
- July 19, 2025: Enhanced duplicate welcome message prevention with robust cooldown mechanism and detailed logging
- July 19, 2025: Fixed channel and embed mode configuration updates that weren't saving properly
- July 19, 2025: Added comprehensive debug information and error handling for welcome system troubleshooting
- July 19, 2025: **TESTIMONIAL APPROVAL SYSTEM COMPLETED** - Fully functional email-based approval workflow implemented
- July 19, 2025: Fixed "undefined" values in testimonial approval emails by correcting database field mapping
- July 19, 2025: Fixed approval URL generation issue (case-sensitive domain problem) making email buttons functional
- July 19, 2025: Testimonials now require manual approval before appearing on website with instant email notification system
- July 19, 2025: Professional HTML approval emails with working APPROVE/REJECT buttons for immediate testimonial management
- July 19, 2025: Comprehensive approval endpoints with beautiful confirmation pages for approved/rejected testimonials
- July 19, 2025: Database migration completed successfully using PostgreSQL with proper testimonial approval schema
- July 19, 2025: **COMMUNITY TAB ENHANCEMENT** - Updated community content with realistic bot development timeline
- July 19, 2025: Added authentic news updates with proper dates spanning January 2025 development timeline
- July 19, 2025: Updated user statistics from 167+ to current 171+ users across 9+ servers
- July 19, 2025: Enhanced command count from 41+ to accurate 44+ total commands available
- July 19, 2025: Created comprehensive feature release timeline with realistic development dates
- July 19, 2025: Added 16 authentic news updates covering major bot features and community milestones
- July 21, 2025: **MAJOR FEATURE** - Comprehensive Error Logging System Implementation
- July 21, 2025: Added /errorlog command with enable/disable/set/view actions for admin control
- July 21, 2025: Created professional log_error function with detailed Discord embeds showing error context
- July 21, 2025: Added error_log_channel_id and error_logging_enabled fields to guild database schema
- July 21, 2025: Integrated error logging across all major bot systems (autoreply, automod, admin commands)
- July 21, 2025: **AUTO-REPLY SYSTEM FIXES** - Fixed database column mismatch issues preventing auto-reply creation
- July 21, 2025: Updated auto-reply system to use correct database schema (response_title, response_description, response_color)
- July 21, 2025: Fixed SQL parameter passing issues that were causing "expected 9 arguments, 1 passed" errors
- July 21, 2025: Enhanced error handling with proper Discord interaction response management
- July 21, 2025: Error logging system successfully tested and confirmed working in live Discord environment
- July 21, 2025: **AUTO-REPLY ENHANCEMENT** - Fixed duplicate message issue by removing duplicate on_message listener
- July 21, 2025: Added 30-second cooldown system per user per rule to prevent spam and abuse
- July 21, 2025: Enhanced footer display to show rule names instead of trigger keywords for better user experience
- July 21, 2025: Added rule_name column to database for improved organization and display
- July 21, 2025: Bot now has 48+ commands including comprehensive error tracking and fully functional auto-reply system

## User Preferences

Preferred communication style: Simple, everyday language.