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
- **Database**: PostgreSQL with Drizzle ORM
- **Bot Framework**: Discord.js v14 with slash commands
- **Development**: Hot reload with Vite middleware integration
- **API Structure**: RESTful endpoints for content management and bot data
- **Bot Features**: Admin, moderation, ticket, and utility commands

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

NexGuard includes comprehensive Discord bot functionality:
- **Admin Commands**: Server configuration, prefix setting, announcements, statistics
- **Moderation Commands**: Warn, mute, kick, ban, unban, message clearing
- **Ticket System**: Support tickets with categories, priorities, and staff assignment
- **Utility Commands**: Server info, user info, ping, help, changelog, uptime
- **Real-time Status**: Live bot status monitoring and statistics
- **Database Integration**: Persistent storage for all bot data
- **Slash Commands**: Modern Discord slash command support
- **Permission System**: Role-based command access control

## Current Status

The system is a complete Discord bot with integrated website that:
- Fully functional Discord bot with 20+ commands
- Live bot status monitoring and statistics
- Professional website showcasing bot features
- Interactive documentation with command reference
- Support ticket system integration
- Moderation logging and analytics
- Real-time bot status updates
- Comprehensive setup guides and help system

## Changelog

- July 18, 2025: Complete NexGuard Discord bot implementation with full functionality
- July 18, 2025: Added comprehensive command system (admin, moderation, ticket, utility)
- July 18, 2025: Implemented live bot status monitoring and statistics
- July 18, 2025: Added PostgreSQL database integration with Drizzle ORM
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

## User Preferences

Preferred communication style: Simple, everyday language.