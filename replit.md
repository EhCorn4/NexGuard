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

### Frontend Pages
- **Home**: Landing page with hero section and key statistics
- **Features**: Detailed feature showcase with interactive cards
- **Invite**: Bot invitation flow with setup instructions
- **Developers**: Team member profiles and social links
- **Community**: News updates and community engagement
- **Testimonials**: Community feedback and user reviews with submission form
- **Feedback**: Support system for bug reports, feature requests, and general feedback
- **Docs**: Comprehensive documentation and help center with search functionality

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

## User Preferences

Preferred communication style: Simple, everyday language.