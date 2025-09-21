// Static features data for NexGuard bot
export interface FeatureUI {
  slug: string;
  title: string;
  description: string;
  icon: string;
  benefits: string[];
}

export const FEATURES: FeatureUI[] = [
  {
    slug: "advanced-moderation",
    title: "Advanced Moderation & Auto-Filtering",
    description: "Automated content filtering with 26 pre-configured bad words, smart spam detection, and customizable punishment systems to keep your server clean and family-friendly.",
    icon: "gavel",
    benefits: ["Automated bad word filtering", "Smart spam detection", "Customizable punishments", "Real-time protection"]
  },
  {
    slug: "live-server-stats",
    title: "Live Server Statistics",
    description: "Real-time Discord embeds showing server activity, member counts, bot uptime, and command usage statistics that update automatically every minute.",
    icon: "activity",
    benefits: ["Real-time server stats", "Auto-updating embeds", "Member count tracking", "Bot performance metrics"]
  },
  {
    slug: "reaction-roles",
    title: "Reaction Roles & Auto-Assignment",
    description: "Advanced role management with button-based reaction roles, automatic role assignment for new members, and comprehensive permission templates.",
    icon: "users",
    benefits: ["Button-based reaction roles", "Automatic role assignment", "Permission templates", "Member management"]
  },
  {
    slug: "event-logging",
    title: "Comprehensive Event Logging",
    description: "Professional audit trail with 7 logging categories covering member, message, voice, channel, role, and moderation events with detailed Discord embeds.",
    icon: "book",
    benefits: ["7 logging categories", "Professional audit trail", "Detailed Discord embeds", "Complete event tracking"]
  },
  {
    slug: "ai-assistant",
    title: "AI Assistant & Advanced Commands",
    description: "Intelligent chatbot assistance powered by OpenAI integration, plus 67+ slash commands covering administration, moderation, utilities, and server management.",
    icon: "bot",
    benefits: ["AI-powered assistance", "67+ slash commands", "Administration tools", "Server utilities"]
  },
  {
    slug: "web-dashboard",
    title: "Professional Web Dashboard",
    description: "Comprehensive web-based management interface with real-time server configuration, Discord integration, and bulk import functionality for effortless administration.",
    icon: "monitor",
    benefits: ["Web-based management", "Real-time configuration", "Discord integration", "Bulk operations"]
  },
  {
    slug: "enterprise-security",
    title: "Enterprise Security Suite",
    description: "Military-grade anti-nuke protection, threat intelligence, and behavioral analysis that automatically quarantines attackers and protects your server from raids and nukes.",
    icon: "shield",
    benefits: ["Anti-nuke protection", "Threat intelligence", "Behavioral analysis", "Automatic quarantine"]
  },
  {
    slug: "ticket-system",
    title: "Professional Ticket System",
    description: "Comprehensive support management with persistent panels, smart routing, staff assignment, and complete Discord integration for professional customer service.",
    icon: "ticket",
    benefits: ["Persistent ticket panels", "Smart routing system", "Staff assignment", "Professional support"]
  },
  {
    slug: "server-analytics",
    title: "Live Server Analytics",
    description: "Real-time insights into server activity, member engagement, growth patterns, and comprehensive moderation statistics with beautiful charts and reports.",
    icon: "chart-bar",
    benefits: ["Real-time insights", "Member engagement tracking", "Growth pattern analysis", "Beautiful reports"]
  },
  {
    slug: "performance-monitoring",
    title: "Performance Monitoring",
    description: "Enterprise-grade bot health monitoring with CPU, memory, and disk usage tracking plus automated alerts for optimal performance.",
    icon: "gauge",
    benefits: ["Health monitoring", "Resource tracking", "Automated alerts", "Performance optimization"]
  },
  {
    slug: "api-integration",
    title: "External API Integration",
    description: "Professional RESTful API endpoints for third-party integrations, custom dashboard development, and external applications.",
    icon: "api",
    benefits: ["RESTful API endpoints", "Third-party integrations", "Custom dashboards", "External applications"]
  },
  {
    slug: "discord-publishing",
    title: "Automated Discord Publishing",
    description: "Professional changelog publishing system that automatically distributes updates to Discord with beautiful embeds, handling long messages and multiple channels seamlessly.",
    icon: "megaphone",
    benefits: ["Automated publishing", "Beautiful embeds", "Multi-channel support", "Long message handling"]
  },
  {
    slug: "cross-server-intelligence",
    title: "Real-Time Cross-Server Intelligence",
    description: "Advanced threat intelligence system that shares behavioral patterns, attack signatures, and security insights across all connected servers for enhanced protection.",
    icon: "network",
    benefits: ["Cross-server intelligence", "Behavioral patterns", "Attack signatures", "Enhanced protection"]
  }
];

export const FEATURES_COUNT = FEATURES.length;
export const COMMANDS_COUNT = "67+";
export const SERVERS_COUNT = "20+";