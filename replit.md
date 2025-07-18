# NexGuard Website

## Overview

This is a clean, professional website for NexGuard, showcasing the bot's features and providing information to potential users. The project has been streamlined to focus on the core website functionality without any bot integration or dashboard features.

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
- **Database**: In-memory storage for development
- **Development**: Hot reload with Vite middleware integration
- **API Structure**: RESTful endpoints for content management

## Key Components

### Database Schema
- **Users**: Basic user management
- **News Updates**: Community announcements and updates
- **Developers**: Team member profiles and information
- **Features**: Bot feature descriptions and benefits
- **Testimonials**: User reviews and ratings with approval system
- **Feedback**: User feedback submissions

### API Endpoints
- `GET /api/news` - Retrieve community updates and announcements
- `GET /api/developers` - Get team member information
- `GET /api/features` - Fetch bot features and capabilities
- `GET /api/testimonials` - Retrieve approved user testimonials
- `POST /api/testimonials` - Submit new testimonial for approval
- `POST /api/feedback` - Submit feedback, bug reports, or feature requests
- `GET /api/config` - Get basic configuration information
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

## Removed Features

All bot integration and dashboard functionality has been removed:
- Discord bot integration
- Discord OAuth authentication
- Server configuration dashboards
- Bot status monitoring
- Real-time bot statistics
- Custom command management
- Auto-reply systems
- Moderation tools dashboard

## Current Status

The website is now a clean, static presentation site that:
- Showcases NexGuard's features and capabilities
- Provides information about the development team
- Allows users to submit testimonials and feedback
- Includes comprehensive documentation
- Maintains professional branding and design
- Offers excellent user experience with smooth animations

## Changelog

- July 18, 2025: Complete cleanup and removal of all bot and dashboard functionality
- July 18, 2025: Streamlined to focus on core website presentation
- July 18, 2025: Removed Discord OAuth, bot status monitoring, and dashboard components
- July 18, 2025: Cleaned up database schema and API endpoints
- July 18, 2025: Updated navigation and removed dashboard links
- July 18, 2025: Simplified architecture for better maintainability

## User Preferences

Preferred communication style: Simple, everyday language.