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

## User Preferences

Preferred communication style: Simple, everyday language.