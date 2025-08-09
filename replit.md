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

### Current System Status
- Bot online across 12 guilds protecting 252 users
- 55 commands fully operational with enhanced ticket system
- 19 permanent ticket panel views restored across 3 guilds  
- Individual ticket control view restoration system implemented
- Complete enterprise-level reliability achieved