# NexGuard Website

## Overview
NexGuard is a comprehensive Discord bot complemented by a professional website, designed to provide robust server management capabilities including advanced moderation, a full-featured ticket system, and various utility commands. The website acts as a central hub for users to monitor bot status, explore features, and access support, aiming to deliver a professional and reliable user experience for Discord server administrators with significant market potential.

## Recent Changes (v3.1.0 - August 29, 2025) ✅ COMPLETED
- **Unified Dashboard System**: Successfully merged server management and security dashboard into single tabbed interface for streamlined bot administration
- **Comprehensive Bot Configuration**: Built complete bot configuration API system with 70+ settings covering AutoMod, logging, welcome/goodbye, moderation roles, and security features
- **Real-Time Server Management**: Created server management interface with tabbed configuration sections allowing website toggles to directly modify bot database settings
- **Live Discord Integration**: Implemented channel and role selection dropdowns using real-time Discord server data with authentication-protected API endpoints
- **Advanced Configuration Coverage**: Complete bot setting management including general settings, moderation tools, AutoMod detection, feature toggles, and comprehensive logging options
- **Unified User Experience**: Integrated Overview, Server Configuration, and Analytics tabs in single dashboard eliminating need for separate /servers route
- **Database Communication Bridge**: Established shared PostgreSQL database as communication layer between Express server and Python Discord bot for instant configuration updates
- **Production Bot Integration**: Live system operational with 18 connected Discord servers and real-time configuration synchronization - successfully tested with actual Discord server management capabilities

## User Preferences
Preferred communication style: Simple, everyday language.

**Discord Announcement Style Preference:**
- Use comprehensive feature announcement format (not simple changelog style)
- Include sections: What's New, Key Features, How to Use, Requirements, Benefits, Integration Notes, Perfect For
- Add clear command examples with code blocks
- Use emoji headers and professional formatting
- End with call-to-action and role mention
- Structure like detailed feature documentation rather than brief changelog entries
- Reference example: botlogs feature announcement format

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
- **Authentication**: Discord OAuth 2.0 with user permission verification and server membership checking
- **Development**: Hot reload with Vite middleware integration
- **API Structure**: RESTful endpoints for content management, bot data, and external integrations
- **Security Infrastructure**: Anti-raid and anti-nuke protection systems with real-time monitoring
- **Monitoring Systems**: Performance monitoring, health alerts, and comprehensive logging
- **URL Mapping**: Custom redirect system supporting post-authentication deep linking

### Database Schema
- Core entities include Users, News Updates, Developers, Features, Testimonials, Feedback, Bot Status, Commands, Guilds, Tickets, Moderation Logs, Ban List, Warning History, Changelogs, Performance Metrics, Health Alerts, Anti-Raid Logs, Anti-Nuke Logs, Guild Backups, Threat Intelligence, Attack Patterns, Behavioral Profiles, Threat Alerts, and Cross-Server Intelligence.

### Bot Features
- **Comprehensive Command Suite**: 67 commands covering Admin, Moderation, Ticket, Utility, Security, Monitoring, and Threat Intelligence functionalities.
- **Admin**: Server configuration, logging setup, welcome messages, autoreply, automod, and role management.
- **Moderation**: Advanced ban/kick/warn, channel lock/unlock, timeout management, comprehensive logging.
- **Ticket System**: Multi-category support tickets with Discord integration, staff assignment, and button-based interaction. Supports renaming ticket channels and robust panel management.
- **Utility**: AI assistant (currently disabled), server/user info, embed builder, help system.
- **Intelligent Threat Analysis**: Enterprise-grade AI-powered security suite with machine learning threat scoring (0-100), behavioral pattern analysis, cross-server intelligence sharing, and predictive threat modeling. Advanced anti-raid and anti-nuke protection with real-time threat detection, automatic quarantine, and intelligent pattern recognition.
- **Monitoring & Alerts**: Real-time performance monitoring with CPU, memory, disk usage tracking. Comprehensive bot health alerts with uptime monitoring, error rate analysis, and multi-channel notification system.
- **External Integration**: Professional RESTful API endpoints for external integrations, third-party applications, and custom dashboard development with comprehensive bot data access.
- **Logging**: Universal command logging, advanced automod logging, and comprehensive event logging across 7 categories (members, messages, voice, channels, roles, moderation). Includes an automated `/botlogs` setup command.
- **Automation**: Advanced AutoMod (spam, bad words, links, caps lock, mention limits), Auto-reply system, Auto-role assignment.
- **Management**: Ban management with appeal system, warning system, custom moderation roles.
- **Live Features**: Real-time bot status monitoring, live server statistics channels, dynamic reaction roles.
- **Analytics System**: Real-time analytics data collection and display from PostgreSQL database queries for message, user, server, channel, and command activity.
- **Discord Changelog System**: Automated publishing of changelogs to Discord with professional embeds, handling long messages.
- **Documentation System**: Generation and distribution of comprehensive PDF guides for bot features.
- **Live Bot Statistics System**: Real-time Discord embeds showing bot usage stats (servers, users, uptime, commands, latency) with auto-updates every minute via `/stats-embed` slash command.

### Data Flow
- Data is served from Express API routes to the React frontend via React Query for reactive UI updates and efficient state management. Live statistics and analytics data are integrated dynamically across the website.

### Deployment Strategy
- **Development**: Vite and tsx for hot-reloaded local environment.
- **Production**: Vite builds static assets, Express server bundled with ESBuild, static file serving for optimized assets. Designed for 24/7 Discord bot connectivity in VM environments.

## External Dependencies

- **Database**: PostgreSQL with asyncpg
- **UI Libraries**: Radix UI, Tailwind CSS, Lucide React, React Icons, Framer Motion
- **Development Tools**: TypeScript, Vite, ESBuild, PostCSS
- **APIs**: OpenAI (currently disabled)
- **Payment**: PayPal (for donations)
- **PDF Generation**: pdfkit