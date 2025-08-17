# NexGuard Website

## Overview
NexGuard is a comprehensive Discord bot paired with a professional website to showcase its features and provide documentation. The project aims to offer a robust solution for Discord server management, including advanced moderation, a full-fledged ticket system, and various utility commands. The website serves as a central hub for users to monitor bot status, explore features, and access support, contributing to a professional and reliable user experience with significant market potential for Discord server administrators.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: Radix UI primitives and shadcn/ui components
- **State Management**: React Query
- **Build Tool**: Vite
- **UI/UX Decisions**: Custom NexGuard brand colors (cyan/purple gradients), system fonts with gradient text effects, reusable UI components with hover animations, mobile-first responsive design, dark theme with light mode toggle.

### Backend
- **Framework**: Express.js with TypeScript
- **Bot Framework**: Discord.py v2 with slash commands
- **Development**: Hot reload with Vite middleware integration
- **API Structure**: RESTful endpoints for content management and bot data.

### Database Schema
- Core entities include Users, News Updates, Developers, Features, Testimonials, Feedback, Bot Status, Commands, Guilds, Tickets, Moderation Logs, Ban List, Warning History, and Changelogs.

### Bot Features
- **Comprehensive Command Suite**: 55+ commands covering Admin, Moderation, Ticket, and Utility functionalities.
- **Admin**: Server configuration, logging setup, welcome messages, autoreply, automod, and role management.
- **Moderation**: Advanced ban/kick/warn, channel lock/unlock, timeout management, comprehensive logging.
- **Ticket System**: Multi-category support tickets with Discord integration, staff assignment, and button-based interaction.
- **Utility**: AI assistant (disabled), server/user info, embed builder, help system.
- **Logging**: Universal command logging, advanced automod logging, and comprehensive event logging across 7 categories (members, messages, voice, channels, roles, moderation).
- **Automation**: Advanced AutoMod (spam, bad words, links, caps lock, mention limits), Auto-reply system, Auto-role assignment.
- **Management**: Ban management with appeal system, warning system, custom moderation roles.
- **Live Features**: Real-time bot status monitoring, live server statistics channels, dynamic reaction roles.

### Data Flow
- Data is served from Express API routes (in-memory for development) to React frontend via React Query, ensuring reactive UI updates and efficient state management.

### Deployment Strategy
- **Development**: Vite and tsx for hot-reloaded local environment.
- **Production**: Vite builds static assets, Express server bundled with ESBuild, static file serving for optimized assets.

## External Dependencies

- **Database**: PostgreSQL with asyncpg
- **UI Libraries**: Radix UI, Tailwind CSS, Lucide React, React Icons, Framer Motion
- **Development Tools**: TypeScript, Vite, ESBuild, PostCSS
- **APIs**: OpenAI (for AI assistant, currently disabled)
- **Payment**: PayPal (for donations)

## Documentation

- **TICKET_PANEL_GUIDE.md**: Complete guide for creating and managing ticket panels
- **CHANGELOG.md**: Detailed change history and version notes
- **ticket_rename_announcement.md**: Discord announcement for new rename feature
- **ticket_fixes_announcement.md**: Documentation of recent ticket system improvements

## Recent Updates

### August 1, 2025: Major Ticket System Overhaul
- **FIXED**: Ticket panel edit functionality - resolved "invalid action" error in `/ticket-panel` command
- **FIXED**: Ticket control button persistence - buttons now work after bot restarts with individual view instances
- **ENHANCED**: Ticket close permissions - anyone in ticket channel can now close tickets, not just staff
- Added complete panel editing system with selective field updates and existing value preservation
- Individual control view restoration prevents interaction conflicts and timeouts
- All ticket panel management actions (create, edit, deploy, list, delete) fully operational

### July 30, 2025: Ticket Channel Detection Enhancement  
- Enhanced ticket channel detection to support custom panel names beyond hardcoded prefixes
- Added intelligent fallback detection using ticket control buttons in message history
- Fixed "This command can only be used in ticket channels" error for all valid ticket channels
- Ticket system now recognizes any channel with dash format (panel-username) or NexGuard control buttons

### August 14, 2025: Enhanced Documentation and Features
- **ADDED**: `/rename` command for ticket channels with smart permissions
- **FEATURE**: Staff and ticket creators can rename channels with format preservation
- **ENHANCED**: Professional logging system for all rename operations
- **VALIDATION**: Channel name validation with duplicate prevention and character filtering
- **DOCUMENTATION**: Complete Ticket Panel Guide (TICKET_PANEL_GUIDE.md) with comprehensive setup instructions
- **UPDATED**: `/help` command now displays all 56 commands across 8 categories
- Command count increased to 56 with comprehensive ticket management capabilities

### August 15, 2025: Comprehensive Guides System Implementation
- **CREATED**: 6 comprehensive downloadable PDF guides with 12-85 pages of detailed content each
- **GUIDES**: Quick Start, AutoMod Setup, Ticket System, Analytics & Logging, Role Management, Complete Admin
- **CONTENT**: Real step-by-step instructions, configuration examples, troubleshooting sections, and best practices
- **REMOVED**: Video tutorials from guides section as requested
- **IMPLEMENTED**: Proper PDF generation using pdfkit library with professional formatting
- **FEATURES**: Working downloads, proper headers/footers, NexGuard branding, and comprehensive documentation
- **CONFIRMED**: User successfully accessed guides on website - all download functionality working properly
- **ENHANCED**: Ticket System Guide expanded to 1000+ lines with enterprise-level content
- **ENHANCED**: Analytics & Logging Guide expanded to 700+ lines with comprehensive monitoring systems
- **COMPLETED**: Systematic website updates across all pages with current statistics and dates
- **UPDATED**: All pages now reflect current bot status: 457+ users, 17+ servers, 60+ commands
- **REVERTED**: Legal document dates back to July 8, 2025 (Privacy Policy, Terms of Service)
- **FIXED**: Critical server syntax error in routes.ts preventing startup - server fully operational
- **UPDATED**: All PDF guide dates updated to August 2025 from dynamic date generation
- **ENHANCED**: "Approve & Close" button in `/request-close` command now automatically closes tickets with full transcript generation
- **UPDATED**: Default ticket close time changed to 10 seconds for "Approve & Close" button

### August 17, 2025: Bot Logs Automation System
- **ADDED**: `/botlogs` command for automatic comprehensive logging setup
- **FEATURE**: One-command setup creates "Bot Logs" category with all 7 log channels
- **AUTOMATION**: Automatically configures general, member, message, voice, channel, role, and moderation logs
- **MANAGEMENT**: View current logging configuration and cleanup options
- **ENHANCEMENT**: Intelligent channel detection prevents duplicates and configures existing channels
- **STREAMLINED**: Eliminates manual setup of individual log channels for new servers
- **PERMISSIONS**: Admin-only command with proper permission checks and error handling
- **INTEGRATION**: Full compatibility with existing `/eventlog` command system

### August 17, 2025: Comprehensive Author Information Removal
- **MODIFIED**: Systematically removed all author/creator information from Discord bot embeds
- **SCOPE**: Comprehensive changes across both TypeScript and Python Discord bot implementations
- **REMOVED**: All "Added by", "Created by", "Requested by", "Set by", "Enabled by", "Disabled by", "Removed by", "Set up by", "Cleaned up by", "Configured by", "Broadcast by", "Clicked by" fields from embeds
- **REMOVED**: All user avatar displays and user mentions in embed footers that showed interaction.user information
- **ENHANCED**: Embeds now focus purely on functional information without revealing who performed actions
- **PRIVACY**: Improved user privacy by anonymizing all Discord bot embed interactions
- **CONSISTENCY**: Standardized embed behavior across all 61+ bot commands and administrative functions
- **MAINTAINED**: All essential functionality and information while removing personal identification data

### Current System Status
- Bot online across 16 guilds protecting 490+ users
- 61 commands fully operational with enhanced logging automation
- 21+ permanent ticket panel views restored across 5 guilds  
- Individual ticket control view restoration system implemented
- Complete enterprise-level reliability achieved
- Website fully updated with current statistics and information
- All 6 comprehensive PDF guides operational and accessible