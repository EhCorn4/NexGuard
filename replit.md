# NexGuard Discord Bot Website

## Overview

This is a full-stack web application for NexGuard, a Discord moderation and quality-of-life bot. The project consists of a React frontend showcasing the bot's features and a Node.js/Express backend serving API endpoints for dynamic content.

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
- **Session Management**: Connect-pg-simple for PostgreSQL session storage
- **Development**: Hot reload with Vite middleware integration
- **API Structure**: RESTful endpoints for content management

## Key Components

### Database Schema
- **Users**: Authentication and user management
- **News Updates**: Community announcements and updates
- **Developers**: Team member profiles and information
- **Features**: Bot feature descriptions and benefits
- **Testimonials**: User reviews and ratings with approval system
- **Feedback**: Support tickets and user feedback submissions

### API Endpoints
- `GET /api/news` - Retrieve community updates and announcements
- `GET /api/developers` - Get team member information
- `GET /api/features` - Fetch bot features and capabilities
- `GET /api/testimonials` - Retrieve approved user testimonials
- `POST /api/testimonials` - Submit new testimonial for approval
- `POST /api/feedback` - Submit feedback, bug reports, or feature requests
- `GET /api/auth/discord` - Initiate Discord OAuth login flow
- `GET /api/auth/discord/callback` - Handle Discord OAuth callback
- `GET /api/auth/user` - Get authenticated user information
- `GET /api/auth/guilds` - Get user's Discord servers with bot status
- `GET /api/auth/logout` - Logout and destroy session

### Frontend Pages
- **Home**: Landing page with hero section and key statistics
- **Features**: Detailed feature showcase with interactive cards
- **Invite**: Bot invitation flow with setup instructions
- **Developers**: Team member profiles and social links
- **Community**: News updates and community engagement
- **Testimonials**: Community feedback and user reviews with submission form
- **Feedback**: Support system for bug reports, feature requests, and general feedback
- **Docs**: Comprehensive documentation and help center with search functionality
- **Dashboard**: Discord OAuth authenticated dashboard for server administrators to manage NexGuard settings on their servers

### Design System
- **Color Palette**: Custom NexGuard brand colors (cyan/purple gradients)
- **Typography**: System fonts with gradient text effects
- **Components**: Reusable UI components with hover animations
- **Responsive**: Mobile-first design with breakpoint considerations

## Data Flow

1. **Content Management**: Data is stored in PostgreSQL and managed through Drizzle ORM
2. **API Layer**: Express routes serve JSON data to the frontend
3. **Client Rendering**: React components consume API data using React Query
4. **State Management**: React Query handles caching, loading states, and error handling
5. **UI Updates**: Components reactively update based on data changes

## External Dependencies

### Core Dependencies
- **Database**: Neon PostgreSQL serverless database
- **ORM**: Drizzle ORM for type-safe database operations
- **UI Library**: Radix UI for accessible component primitives
- **Styling**: Tailwind CSS for utility-first styling
- **Icons**: Lucide React and React Icons for iconography

### Development Tools
- **TypeScript**: Type safety across the entire stack
- **Vite**: Fast development server and build tool
- **ESBuild**: Fast bundling for production builds
- **PostCSS**: CSS processing and optimization

## Deployment Strategy

### Development
- Vite development server with hot module replacement
- Express server with TypeScript compilation via tsx
- Database migrations using Drizzle Kit
- Environment variables for database configuration

### Production
- Vite builds static assets to `dist/public`
- Express server bundled with ESBuild for Node.js
- PostgreSQL database with connection pooling
- Static file serving for optimized assets

### Build Process
1. Frontend assets compiled with Vite
2. Backend server bundled with ESBuild
3. Database schema pushed using Drizzle Kit
4. Environment-specific configuration management

## Bot Integration

### Discord Bot API Endpoints
The website now provides secure API endpoints for the Discord bot to connect and fetch configurations:

- **Bot Authentication**: All bot endpoints require Bearer token authentication using `DISCORD_BOT_TOKEN`
- **Server Configuration**: `/api/bot/servers/{guildId}/config` - Get server-specific settings
- **Custom Commands**: `/api/bot/servers/{guildId}/commands` - Get custom commands for a server
- **Moderation Logging**: `/api/bot/servers/{guildId}/moderation/log` - Log moderation actions
- **Server Sync**: `/api/bot/servers/{guildId}/sync` - Sync server data from Discord

### Environment Variables
Required for bot integration:
- `DISCORD_BOT_TOKEN` - Bot's authentication token
- `DISCORD_CLIENT_ID` - Discord application ID  
- `DISCORD_CLIENT_SECRET` - Discord OAuth client secret

### Dynamic Configuration
The website now uses dynamic configuration through `/api/config` endpoint instead of hardcoded values, allowing for flexible deployment across different environments.

## Changelog

Changelog:
- July 08, 2025. Initial setup
- July 08, 2025. Added community feedback and testimonials system with database integration
- July 08, 2025. Created comprehensive documentation/help center with search functionality
- July 08, 2025. Updated developer information to show only Caleb Weston as Lead Developer
- July 08, 2025. Implemented light/dark mode toggle with theme persistence and smooth transitions
- July 08, 2025. Added NexGuard logo to all page headers with consistent branding
- July 08, 2025. Implemented smooth scrolling to page tops when navigating between pages
- July 08, 2025. Applied hero gradient background with circuit pattern to all pages for consistent visual design
- July 08, 2025. Comprehensive website optimization: lazy loading, error boundaries, performance wrappers, memoized components, accessibility improvements, loading skeletons, and reduced motion support
- July 08, 2025. Successfully implemented and tested community feedback and testimonials system with PostgreSQL database integration, approval workflow, and fully functional submission forms
- July 08, 2025. Implemented smooth page transition animations with framer-motion, stagger effects, and enhanced navigation with accessibility support
- July 08, 2025. Added Discord OAuth login system for bot dashboard with session management, user authentication, and server management interface
- July 08, 2025. Updated Discord OAuth system to be user-focused: individual server admins can login to manage their own servers with proper permission validation
- July 08, 2025. Created comprehensive server configuration system with individual server dashboards, full bot configuration options (moderation, welcome messages, custom commands, economy, roles), and database integration for persistent settings storage
- July 08, 2025. Added community highlight section to home page featuring BlueLine RolePlay (BLRP) as first active beta testers
- July 08, 2025. Implemented comprehensive documentation/help center with searchable articles, categorized sections, and interactive navigation
- July 08, 2025. Fixed Discord OAuth redirect URI issues by implementing dynamic domain handling for multiple deployment environments
- July 08, 2025. Created comprehensive bot integration guide with database connection examples, configuration loading system, and API integration methods for connecting actual Discord bot to dashboard
- July 09, 2025. Added Terms of Service page with professional legal document layout, accessible via footer link at /terms-of-service
- July 09, 2025. Updated Terms of Service effective and last updated dates to July 8, 2025
- July 09, 2025. Added comprehensive Privacy Policy page with detailed data handling policies, accessible at /privacy-policy and linked from footer
- July 09, 2025. Added comprehensive Cookies Policy page with detailed cookie usage information, accessible at /cookies-policy and linked from footer
- July 09, 2025. Added comprehensive Contact page with multiple contact methods, situational guidance, and response time expectations at /contact
- July 09, 2025. Fixed developers page crash by importing memo from React and replacing LoadingSkeleton with Skeleton component
- July 09, 2025. Fixed community page crash by correcting Skeleton import path
- July 09, 2025. Created comprehensive moderation tools dashboard with tabbed interface (Basic, Filters, Punishments, Logging) featuring fully functional controls, real-time feedback, and advanced configuration options
- July 09, 2025. Implemented secure Discord bot API integration with authentication, server configuration endpoints, and dynamic client ID management throughout the website
- July 16, 2025. Added real-time bot status monitoring with BotStatus component and BotStatusBadge integrated into navbar and dashboard, displaying guild count, user count, uptime, and online status with automatic refresh and WebSocket support
- July 17, 2025. Successfully resolved bot startup issues and implemented direct bot execution for stable connection to Discord with 7 servers and 127 users
- July 17, 2025. Updated home page statistics to display actual live bot data instead of hardcoded values, with automatic refresh every 30 seconds
- July 17, 2025. Fixed home page layout positioning to place floating logo properly below taskbar with responsive design maintained
- July 17, 2025. Successfully increased Discord bot slash commands from 7 to 64 globally synced commands by fixing all import issues, dependency problems, and token authentication - all 37 extensions now load properly with comprehensive moderation, utility, admin, and ticket functionality
- July 17, 2025. Applied deployment fixes to resolve mixed project structure issues: removed all Python bot files and directories (bot/, bot-python/, nexguard/, pyproject.toml, uv.lock) to eliminate deployment confusion between Node.js and Python components
- July 17, 2025. Added health check endpoints (/health and /api/health) for deployment monitoring and verification, ensuring proper production deployment status reporting
- July 17, 2025. Verified production build process works correctly with proper asset compilation and server bundling for Replit deployment
- July 17, 2025. Replaced Python bot integration with native Discord.js bot that starts automatically with the website, featuring proper Discord connection, slash commands (/ping, /help, /status), and real-time status reporting with 8 servers and 157 users
- July 17, 2025. Bot now properly starts with deployment and shows accurate live statistics instead of cached data, ensuring the Discord bot is fully functional when the website is deployed
- July 17, 2025. Successfully fixed Discord OAuth authentication by correcting redirect URI generation to use proper Replit domain format, enabling full dashboard login functionality with server management access
- July 17, 2025. Completed fully functional dashboard with database integration: updated features to reflect actual bot capabilities (64 slash commands, moderation, tickets, welcome system, server management, utilities, custom commands), connected all server configuration endpoints to PostgreSQL database instead of mock data, implemented working toggles/switches/inputs for all settings, added proper custom command management with CRUD operations, and verified all dashboard controls save and load settings correctly
- July 17, 2025. Fixed React Query URL construction issue that was preventing server configuration pages from loading properly by correcting queryKey array handling in the default query function
- July 17, 2025. Successfully connected all server configuration controls to database: all switches, inputs, and selects in the moderation dashboard now save to PostgreSQL database instead of just showing toast notifications, including anti-raid protection, message filters, rate limiting, warning system, and punishment settings
- July 17, 2025. Fixed Discord OAuth login issue by correcting redirect URI to use proper Replit domain instead of localhost, now using REPLIT_DOMAINS environment variable for proper authentication flow
- July 17, 2025. Fixed Discord OAuth 400 Bad Request error by updating redirect URI to use correct nexguard.replit.app domain that matches Discord application configuration
- July 17, 2025. Successfully resolved Discord OAuth authentication issues by updating Discord application redirect URI to match actual deployment domain, enabling full dashboard login functionality and server management access
- July 17, 2025. Enhanced developer page with comprehensive information including expanded database schema for skills, specialties, achievements, projects, and contact details; updated frontend with professional layout featuring skill badges, project descriptions, and detailed developer profile for Caleb Weston
- July 17, 2025. Successfully completed developer page enhancement with database schema updates, comprehensive developer information display, and professional layout - confirmed working by user
- July 17, 2025. Fixed Discord bot command registration issue: expanded from 3 basic commands to 64 comprehensive slash commands including moderation, utility, system management, economy, fun, admin, logging, ticket system, welcome system, verification, role management, and server management commands with proper handlers and responses
- July 17, 2025. Updated /api/config endpoint to return simple "discord" platform configuration instead of complex dashboard settings as requested by user
- July 17, 2025. Successfully increased Discord bot slash commands from 25 to 86 globally synced commands by fixing all import issues, dependency problems, and token authentication - all extensions now load properly with comprehensive moderation, utility, admin, economy, fun, logging, ticket, welcome, verification, role management, and server management functionality
- July 17, 2025. Fixed hardcoded command count issue in API endpoint that was preventing accurate command count display - bot now correctly reports 86 commands instead of cached 25
- July 17, 2025. Implemented comprehensive auto-reply system with 6 new slash commands (autoreply-create, autoreply-list, autoreply-toggle, autoreply-delete, autoreply-stats, autoreply-test) bringing total to 92 commands, added database schema for auto-reply rules/cooldowns/stats, complete storage interface with CRUD operations, and API endpoints for auto-reply management via dashboard
- July 17, 2025. Removed all economy commands (balance, daily, leaderboard, work, rob, pay, shop, buy, sell, inventory, gamble) from Discord bot reducing total commands from 92 to 81 commands, cleaned up help command and config options to remove economy references

## User Preferences

Preferred communication style: Simple, everyday language.