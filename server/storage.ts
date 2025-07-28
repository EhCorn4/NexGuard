import { users, newsUpdates, developers, features, testimonials, feedback, guilds, commands, tickets, moderationLogs, changelogs, botStatus, type User, type InsertUser, type NewsUpdate, type Developer, type Feature, type Testimonial, type InsertTestimonial, type Feedback, type InsertFeedback, type Guild, type Command, type InsertCommand, type Ticket, type InsertTicket, type ModerationLog, type InsertModerationLog, type Changelog, type InsertChangelog, type BotStatus, type InsertBotStatus } from "@shared/schema";
import { db } from "./db";
import { eq, desc } from "drizzle-orm";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  getNews(): Promise<NewsUpdate[]>;
  getDevelopers(): Promise<Developer[]>;
  getFeatures(): Promise<Feature[]>;
  getTestimonials(): Promise<Testimonial[]>;
  getApprovedTestimonials(): Promise<Testimonial[]>;
  createTestimonial(testimonial: InsertTestimonial): Promise<Testimonial>;
  approveTestimonial(id: number): Promise<Testimonial | null>;
  rejectTestimonial(id: number): Promise<boolean>;
  getFeedback(): Promise<Feedback[]>;
  createFeedback(feedback: InsertFeedback): Promise<Feedback>;
  
  // Bot-related methods
  getBotStatus(): Promise<BotStatus | null>;
  updateBotStatus(status: Partial<BotStatus>): Promise<void>;
  getCommands(): Promise<Command[]>;
  createCommand(command: InsertCommand): Promise<Command>;
  getChangelogs(): Promise<Changelog[]>;
  createChangelog(changelog: InsertChangelog): Promise<Changelog>;
  getTickets(): Promise<Ticket[]>;
  createTicket(ticket: InsertTicket): Promise<Ticket>;
  getModerationLogs(): Promise<ModerationLog[]>;
  createModerationLog(log: InsertModerationLog): Promise<ModerationLog>;
  
  // Analytics methods
  getAnalyticsOverview(): Promise<any>;
  getServerAnalytics(guildId: string, timeRange: string): Promise<any>;
  getMessageAnalytics(guildId: string, timeRange: string): Promise<any>;
  getCommandAnalytics(guildId: string, timeRange: string): Promise<any>;
  getUserActivity(guildId: string): Promise<any>;
  getChannelAnalytics(guildId: string): Promise<any>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private newsUpdates: Map<number, NewsUpdate>;
  private developers: Map<number, Developer>;
  private features: Map<number, Feature>;
  private testimonialsData: Map<number, Testimonial>;
  private feedbackData: Map<number, Feedback>;
  private botStatusData: Map<number, BotStatus>;
  private commandsData: Map<number, Command>;
  private changelogsData: Map<number, Changelog>;
  private ticketsData: Map<number, Ticket>;
  private moderationLogsData: Map<number, ModerationLog>;
  private currentUserId: number;
  private currentNewsId: number;
  private currentDevId: number;
  private currentFeatureId: number;
  private currentTestimonialId: number;
  private currentFeedbackId: number;
  private currentCommandId: number;
  private currentChangelogId: number;
  private currentTicketId: number;
  private currentModerationLogId: number;

  constructor() {
    this.users = new Map();
    this.newsUpdates = new Map();
    this.developers = new Map();
    this.features = new Map();
    this.testimonialsData = new Map();
    this.feedbackData = new Map();
    this.botStatusData = new Map();
    this.commandsData = new Map();
    this.changelogsData = new Map();
    this.ticketsData = new Map();
    this.moderationLogsData = new Map();
    this.currentUserId = 1;
    this.currentNewsId = 1;
    this.currentDevId = 1;
    this.currentFeatureId = 1;
    this.currentTestimonialId = 1;
    this.currentFeedbackId = 1;
    this.currentCommandId = 1;
    this.currentChangelogId = 1;
    this.currentTicketId = 1;
    this.currentModerationLogId = 1;
    
    try {
      this.initializeData();
      console.log('Storage initialized successfully');
    } catch (error) {
      console.error('Error initializing storage:', error);
    }
  }

  private initializeData() {
    // Initialize news updates spanning past 2 months
    this.newsUpdates.set(1, {
      id: 1,
      title: "📊 Live Server Statistics Channels - Real-Time Community Insights",
      content: "Introducing live server statistics channels! Voice channels that automatically display real-time member counts, bot counts, channel counts, and role counts. Updates every 5 minutes with professional formatting and automatic cleanup. Perfect for showcasing your community's growth at a glance.",
      category: "NEW FEATURE", 
      publishedAt: new Date('2025-07-27T10:00:00Z'),
      likes: 203,
      comments: 45,
    });

    this.newsUpdates.set(28, {
      id: 28,
      title: "🎭 Dynamic Reaction Roles - Interactive Role Management",
      content: "Advanced reaction roles system now live! Users can add/remove roles by reacting to messages with automatic role synchronization. Includes persistent configuration, role hierarchy validation, and comprehensive management commands. Perfect for self-service role assignment.",
      category: "NEW FEATURE", 
      publishedAt: new Date('2025-07-27T09:30:00Z'),
      likes: 178,
      comments: 38,
    });

    this.newsUpdates.set(29, {
      id: 29,
      title: "🛡️ Advanced AutoMod Protection: Caps Lock & Mention Limits",
      content: "Revolutionary automod expansion with caps lock filtering and mention spam protection! Configure thresholds from 10-100% for caps detection and limits from 1-20 mentions per message. Enhanced protection against spam with professional logging and moderator bypass functionality.",
      category: "UPDATE", 
      publishedAt: new Date('2025-07-21T10:00:00Z'),
      likes: 156,
      comments: 34,
    });

    this.newsUpdates.set(26, {
      id: 26,
      title: "📋 Command System Expansion: 51+ Commands",
      content: "Complete command suite expansion to 51+ slash commands! Enhanced /commands display with organized categories: Admin (5), Moderation (12), Utility (12), AutoMod (8), Auto-Reply (5), Role Management (5), Tickets (3). Comprehensive server management at your fingertips.",
      category: "UPDATE",
      publishedAt: new Date('2025-07-21T09:30:00Z'),
      likes: 89,
      comments: 23,
    });

    this.newsUpdates.set(2, {
      id: 2,
      title: "🔒 Advanced Channel Management",
      content: "New lock/unlock commands with permission controls and detailed notifications. Administrators can now quickly secure channels during incidents with comprehensive logging and role-based access management.",
      category: "SECURITY",
      publishedAt: new Date('2025-07-15T14:30:00Z'),
      likes: 156,
      comments: 31,
    });

    this.newsUpdates.set(3, {
      id: 3,
      title: "⚡ Enhanced AutoMod Protection",
      content: "Professional automod logging now sends detailed violation reports to configured channels. Real-time spam detection, bad word filtering, and link blocking with escalation actions and comprehensive reporting.",
      category: "SECURITY",
      publishedAt: new Date('2025-07-08T16:00:00Z'),
      likes: 203,
      comments: 47,
    });

    this.newsUpdates.set(4, {
      id: 4,
      title: "🎫 Advanced Testimonial System",
      content: "New email-based testimonial approval system with instant notifications. When users submit testimonials, administrators receive professional emails with approve/reject buttons for immediate management.",
      category: "NEW FEATURE",
      publishedAt: new Date('2025-07-02T11:30:00Z'),
      likes: 78,
      comments: 19,
    });

    this.newsUpdates.set(5, {
      id: 5,
      title: "🎮 Custom AutoRole System",
      content: "Comprehensive autorole command with set, enable, disable, remove, and view actions. Automatic role assignment functionality with role hierarchy validation and permission checking for new member management.",
      category: "NEW FEATURE",
      publishedAt: new Date('2025-06-28T09:00:00Z'),
      likes: 134,
      comments: 28,
    });

    this.newsUpdates.set(6, {
      id: 6,
      title: "💎 Premium Donation System",
      content: "Simple and empathetic donation system launched to support continued development. Optional contributions help maintain and improve NexGuard while keeping all features completely free for everyone.",
      category: "COMMUNITY",
      publishedAt: new Date('2025-06-22T15:45:00Z'),
      likes: 234,
      comments: 41,
    });

    this.newsUpdates.set(7, {
      id: 7,
      title: "🎉 Welcome System Overhaul",
      content: "Rich welcome embeds with custom colors, thumbnails, and interactive elements. Advanced placeholder support, channel detection, and comprehensive configuration options for perfect new member onboarding.",
      category: "UPDATE",
      publishedAt: new Date('2025-06-15T13:20:00Z'),
      likes: 112,
      comments: 27,
    });

    this.newsUpdates.set(8, {
      id: 8,
      title: "⏰ Temporary Ban System",
      content: "Advanced temporary ban functionality with automatic expiration. Support for duration formats (7d, 2h, 30m) with background processing and automated unban when time expires.",
      category: "UPDATE",
      publishedAt: new Date('2025-06-10T17:15:00Z'),
      likes: 98,
      comments: 25,
    });

    this.newsUpdates.set(9, {
      id: 9,
      title: "🎮 Custom Moderation Roles",
      content: "Advanced permission system allowing administrators to set custom moderation roles with hierarchy validation. Precise control over who can moderate your server beyond Discord's default permissions.",
      category: "NEW FEATURE",
      publishedAt: new Date('2025-06-05T12:45:00Z'),
      likes: 167,
      comments: 38,
    });

    this.newsUpdates.set(10, {
      id: 10,
      title: "📈 Multi-Category Ticket System",
      content: "Enhanced ticket system with category management and Discord channel integration. Organized support with automatic ticket placement, priority levels, and comprehensive filtering options for large communities.",
      category: "NEW FEATURE",
      publishedAt: new Date('2025-05-30T18:20:00Z'),
      likes: 145,
      comments: 29,
    });

    this.newsUpdates.set(11, {
      id: 11,
      title: "🛡️ Advanced AutoMod Suite",
      content: "State-of-the-art moderation automation with 6 specialized commands. Features intelligent spam protection, link filtering, bad word detection, and real-time message monitoring with escalation actions.",
      category: "SECURITY",
      publishedAt: new Date('2025-05-25T14:10:00Z'),
      likes: 289,
      comments: 62,
    });

    this.newsUpdates.set(12, {
      id: 12,
      title: "🤖 Smart Auto-Reply Engine",
      content: "Revolutionary auto-reply system with intelligent keyword matching, rich embed responses, and detailed analytics. Create custom automated responses with multiple trigger types, cooldowns, and comprehensive statistics.",
      category: "NEW FEATURE",
      publishedAt: new Date('2025-05-20T10:30:00Z'),
      likes: 234,
      comments: 56,
    });

    this.newsUpdates.set(13, {
      id: 13,
      title: "💡 AI-Powered Assistant",
      content: "Integrated AI assistant for server management help and questions. Get instant answers about bot commands, Discord server management, and troubleshooting directly in your server.",
      category: "NEW FEATURE",
      publishedAt: new Date('2025-05-15T16:45:00Z'),
      likes: 198,
      comments: 45,
    });

    this.newsUpdates.set(14, {
      id: 14,
      title: "🚀 NexGuard 2.3.2 Release",
      content: "Major bot update featuring Python architecture migration, improved performance, enhanced Discord.py integration, and comprehensive slash command support. Faster responses and more reliable operations.",
      category: "FEATURED",
      publishedAt: new Date('2025-05-12T11:15:00Z'),
      likes: 356,
      comments: 78,
    });

    this.newsUpdates.set(15, {
      id: 15,
      title: "🎯 44+ Commands Now Available",
      content: "Complete command expansion to 44+ slash commands! Including 17 moderation commands, 15 admin commands, 11 utility commands, and 4 ticket system commands. Most comprehensive Discord bot feature set available.",
      category: "FEATURED",
      publishedAt: new Date('2025-05-08T13:25:00Z'),
      likes: 342,
      comments: 89,
    });

    this.newsUpdates.set(25, {
      id: 25,
      title: "📊 Bot Statistics Update: 174+ Users Protected",
      content: "NexGuard is now actively protecting 174+ users across 9+ Discord servers! Our community continues to grow as more servers trust us with their comprehensive moderation and management capabilities.",
      category: "COMMUNITY",
      publishedAt: new Date('2025-05-22T19:00:00Z'),
      likes: 127,
      comments: 34,
    });

    this.newsUpdates.set(27, {
      id: 27,
      title: "🎫 Complete Ticket System Launch - We Have Tickets!!!",
      content: "Professional ticket system now live! Interactive panel deployment to any channel, {panel}-{username} channel naming, Close/Claim buttons, automatic transcript delivery, custom embeds with placeholder variables, and reliable channel deletion. Complete replacement for dedicated ticket bots.",
      category: "FEATURED",
      publishedAt: new Date('2025-07-24T20:00:00Z'),
      likes: 487,
      comments: 112,
    });

    this.currentNewsId = 30;

    // Initialize developers
    this.developers.set(1, {
      id: 1,
      name: "Caleb Weston",
      role: "Lead Developer",
      bio: "Passionate full-stack developer with expertise in Discord bot development, web technologies, and system architecture. Leading NexGuard's development with a focus on creating robust, scalable solutions for Discord communities.",
      location: "Canada",
      experience: "5+ years of experience in software development, specializing in Discord bot development, web applications, and community management tools.",
      skills: ["JavaScript", "TypeScript", "Node.js", "React", "Discord.js", "PostgreSQL", "Docker", "AWS", "Python", "Express.js"],
      specialties: ["Discord Bot Development", "Full-Stack Web Development", "Database Architecture", "API Design", "Community Management Tools"],
      achievements: ["Built and maintained NexGuard serving 100+ Discord servers", "Developed advanced moderation systems", "Created comprehensive ticket management solutions", "Implemented real-time monitoring and analytics"],
      projects: ["NexGuard Discord Bot", "Advanced Moderation Dashboard", "Custom Command System", "Real-time Analytics Platform"],
      education: "Computer Science",
      email: "crweston2004@gmail.com",
      discord: "ehcorn",
      yearsOfExperience: 5,
    });

    this.currentDevId = 2;

    // Initialize features
    this.features.set(1, {
      id: 1,
      title: "Advanced Moderation Suite",
      description: "Enterprise-grade moderation tools with 17+ commands including temporary bans, channel management, intelligent automod with caps lock filtering, mention limits, and comprehensive tracking systems.",
      icon: "shield",
      benefits: ["Temporary ban system with duration parsing (7d, 2h, 30m, 1w)", "Channel lock/unlock with permission management", "Smart automod with caps lock filter (10-100% threshold)", "Mention limits protection (1-20 mentions per message)", "Professional automod logging to channels", "Universal command logging for all 51+ commands", "Comprehensive warning system with severity tracking", "Custom moderator role management and permissions"],
    });

    this.features.set(2, {
      id: 2,
      title: "Professional Ticket System",
      description: "Complete TicketsBot.net-style ticket system with interactive panels, custom embeds, automatic transcripts, and comprehensive channel management - all built into Discord.",
      icon: "ticket",
      benefits: ["Interactive panel buttons with custom embeds deployable to any channel", "Smart channel naming: {panel}-{username} format (support-john, billing-sarah)", "Professional Close and Claim buttons for staff management", "Automatic transcript delivery to all participants when tickets close", "Separate embed customization for panels vs ticket channels", "Placeholder variables: {user.mention}, {user.name}, {guild.name}, line breaks", "Role/user ping notifications in ticket channels only", "Customizable deletion delays (0-300 seconds) with countdown messages"],
    });

    this.features.set(3, {
      id: 3,
      title: "Smart Auto-Reply System",
      description: "Advanced auto-reply system with intelligent keyword matching, rich embed responses, and comprehensive analytics tracking for automated server interactions.",
      icon: "command",
      benefits: ["Multiple trigger types (contains, exact, starts with, ends with)", "Rich embed responses with custom colors", "Comprehensive statistics and usage analytics", "Cooldown system to prevent spam", "Rule-based management with unique IDs"],
    });

    this.features.set(4, {
      id: 4,
      title: "Enhanced Welcome System",
      description: "Advanced welcome messages with rich embeds, custom colors, thumbnails, and comprehensive configuration options.",
      icon: "users",
      benefits: ["Rich embed support", "Custom colors & thumbnails", "Placeholder system", "Channel-specific setup", "Advanced configuration"],
    });

    this.features.set(5, {
      id: 5,
      title: "Comprehensive Command Suite",
      description: "Complete server administration suite with 50+ slash commands covering admin, moderation, tickets, utilities, auto-replies, automod, and role management.",
      icon: "cog",
      benefits: ["50+ slash commands across all categories", "Advanced admin tools with error logging", "AI assistant with intelligent responses", "8 comprehensive automod commands", "Role management with hierarchical permissions", "Real-time monitoring and analytics"],
    });

    this.features.set(6, {
      id: 6,
      title: "Real-time Analytics Dashboard", 
      description: "Professional analytics dashboard with live bot status monitoring, server statistics, command usage tracking, and comprehensive performance insights.",
      icon: "chart-line",
      benefits: ["Live bot status with real-time updates (11+ servers, 201+ users)", "Interactive server statistics and charts", "Universal command logging with professional embeds", "Error tracking and logging system", "Professional dashboard with data visualization"],
    });

    this.features.set(7, {
      id: 7,
      title: "Professional Logging System",
      description: "Enterprise-grade logging system that tracks all command usage and automod actions with detailed professional embeds sent to configured channels.",
      icon: "file-text",
      benefits: ["Universal command logging for all 44 commands", "Automod action logging with detailed context", "Professional embed formatting with user details", "Configurable logging channels per server", "Real-time activity monitoring"],
    });

    this.features.set(8, {
      id: 8,
      title: "Advanced AutoMod Protection",
      description: "Intelligent automated moderation with comprehensive filtering, smart detection algorithms, and professional logging to maintain server quality.",
      icon: "shield-check", 
      benefits: ["Smart spam detection with configurable thresholds", "Bad word filtering with strict and flexible modes", "Link and invite blocking with custom actions", "Professional logging to configured channels", "Cooldown systems to prevent abuse"],
    });

    this.features.set(9, {
      id: 9,
      title: "Live Server Statistics Channels",
      description: "Real-time voice channels displaying live server metrics with automatic updates every 5 minutes, providing instant visibility into your community's growth and activity.",
      icon: "chart-line",
      benefits: ["Real-time member, bot, and channel counts", "Professional voice channel display with custom formatting", "Automatic updates every 5 minutes", "Organized 'Server Statistics' category creation", "Force update and cleanup commands for maintenance", "Database persistence with orphaned entry cleanup"],
    });

    this.features.set(10, {
      id: 10,
      title: "Dynamic Reaction Roles",
      description: "Advanced reaction-based role assignment system with automatic role management, persistent configuration, and comprehensive administrative controls.",
      icon: "users",
      benefits: ["Add/remove roles by reacting to messages", "Persistent configuration across bot restarts", "Automatic cleanup of deleted roles", "Role hierarchy validation", "Comprehensive management commands", "Real-time role synchronization"],
    });

    this.currentFeatureId = 11;

    // Initialize testimonials with some sample data
    this.testimonialsData.set(1, {
      id: 1,
      username: "ServerOwner123",
      serverName: "BlueLine RolePlay",
      content: "NexGuard has been instrumental in managing our 500+ member roleplay community. The moderation tools are top-notch and the support is excellent!",
      rating: 5,
      isApproved: true,
      createdAt: new Date('2024-01-12'),
    });

    this.testimonialsData.set(2, {
      id: 2,
      username: "AdminMike",
      serverName: "Gaming Central",
      content: "The ticket system alone makes NexGuard worth it. Our support workflow has never been smoother.",
      rating: 5,
      isApproved: true,
      createdAt: new Date('2024-01-08'),
    });

    this.testimonialsData.set(3, {
      id: 3,
      username: "CommunityMod",
      serverName: "Tech Hub",
      content: "Great bot with reliable uptime and responsive support. Highly recommend for any serious Discord community.",
      rating: 4,
      isApproved: true,
      createdAt: new Date('2024-01-05'),
    });

    this.currentTestimonialId = 4;

    // Initialize bot status
    this.botStatusData.set(1, {
      id: 1,
      isOnline: true,
      guildsCount: 0,
      usersCount: 0,
      commandsExecuted: 0,
      uptime: "0s",
      lastRestart: new Date(),
      version: "2.3.2",
      updatedAt: new Date()
    });

    // Initialize changelog
    this.changelogsData.set(1, {
      id: 1,
      version: "2.3.2",
      title: "Major Update - Enhanced Bot Features",
      description: "This update brings comprehensive Discord bot integration with advanced moderation, ticket system, and utility commands.",
      changes: [
        "Added 20+ slash commands for server management",
        "Implemented advanced moderation tools (warn, mute, kick, ban)",
        "Introduced ticket system with categories and priorities",
        "Added utility commands for server information and user management",
        "Enhanced security with permission-based command access",
        "Improved bot status monitoring and uptime tracking",
        "Added real-time command execution logging",
        "Implemented changelog system for update tracking"
      ],
      type: "major",
      releaseDate: new Date(),
      isPublished: true
    });

    this.currentChangelogId = 2;

    // Initialize comprehensive commands data - All 41+ commands
    
    // Admin Commands (11 commands)
    this.commandsData.set(1, {
      id: 1,
      name: "automod-config",
      description: "Configure automod settings and view status overview",
      category: "admin",
      usage: "/automod-config",
      permissions: ["MANAGE_SERVER"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(2, {
      id: 2,
      name: "automod-spam",
      description: "Configure anti-spam protection with message limits and time windows",
      category: "admin",
      usage: "/automod-spam <enabled> [max_messages] [time_window] [action]",
      permissions: ["MANAGE_SERVER"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(3, {
      id: 3,
      name: "automod-links",
      description: "Configure link filtering and Discord invite blocking",
      category: "admin",
      usage: "/automod-links <enabled> [action]",
      permissions: ["MANAGE_SERVER"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(4, {
      id: 4,
      name: "automod-badwords",
      description: "Configure bad words filtering with strict mode options",
      category: "admin",
      usage: "/automod-badwords <enabled> [strict_mode] [action]",
      permissions: ["MANAGE_SERVER"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(5, {
      id: 5,
      name: "automod-words",
      description: "Manage custom word lists for automod filtering",
      category: "admin",
      usage: "/automod-words <action> [word]",
      permissions: ["MANAGE_SERVER"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(6, {
      id: 6,
      name: "automod-reset",
      description: "Reset all automod settings to defaults with safety confirmation",
      category: "admin",
      usage: "/automod-reset",
      permissions: ["MANAGE_SERVER"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(7, {
      id: 7,
      name: "autoreply-create",
      description: "Create advanced auto-reply rules with embed responses",
      category: "admin",
      usage: "/autoreply-create <name> <trigger> <response> [trigger_type] [embed_color]",
      permissions: ["ADMINISTRATOR"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(8, {
      id: 8,
      name: "autoreply-list",
      description: "List all auto-reply rules with status and statistics",
      category: "admin",
      usage: "/autoreply-list",
      permissions: ["ADMINISTRATOR"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(9, {
      id: 9,
      name: "autoreply-toggle",
      description: "Enable or disable specific auto-reply rules",
      category: "admin",
      usage: "/autoreply-toggle <rule_name>",
      permissions: ["ADMINISTRATOR"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(10, {
      id: 10,
      name: "autoreply-delete",
      description: "Delete auto-reply rules with confirmation",
      category: "admin",
      usage: "/autoreply-delete <rule_name>",
      permissions: ["ADMINISTRATOR"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(11, {
      id: 11,
      name: "modrole",
      description: "Set custom moderation roles with hierarchy validation",
      category: "admin",
      usage: "/modrole [role]",
      permissions: ["MANAGE_GUILD"],
      enabled: true,
      createdAt: new Date(),
    });

    // Moderation Commands (15 commands)
    this.commandsData.set(12, {
      id: 12,
      name: "ban",
      description: "Ban a user from the server with comprehensive logging",
      category: "moderation",
      usage: "/ban <user> [reason]",
      permissions: ["BAN_MEMBERS"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(13, {
      id: 13,
      name: "unban",
      description: "Unban a user from the server",
      category: "moderation",
      usage: "/unban <user_id> [reason]",
      permissions: ["BAN_MEMBERS"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(14, {
      id: 14,
      name: "kick",
      description: "Kick a user from the server",
      category: "moderation",
      usage: "/kick <user> [reason]",
      permissions: ["KICK_MEMBERS"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(15, {
      id: 15,
      name: "warn",
      description: "Issue a warning to a user with severity tracking",
      category: "moderation",
      usage: "/warn <user> <reason> [severity]",
      permissions: ["MANAGE_MESSAGES"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(16, {
      id: 16,
      name: "mute",
      description: "Mute a user in the server with timeout support",
      category: "moderation",
      usage: "/mute <user> [duration] [reason]",
      permissions: ["MANAGE_ROLES"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(17, {
      id: 17,
      name: "unmute",
      description: "Remove mute from a user",
      category: "moderation",
      usage: "/unmute <user> [reason]",
      permissions: ["MANAGE_ROLES"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(18, {
      id: 18,
      name: "timeout",
      description: "Timeout a user for a specified duration",
      category: "moderation",
      usage: "/timeout <user> <duration> [reason]",
      permissions: ["MODERATE_MEMBERS"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(19, {
      id: 19,
      name: "tempban",
      description: "Temporarily ban a user with automatic unban",
      category: "moderation",
      usage: "/tempban <user> <duration> [reason]",
      permissions: ["BAN_MEMBERS"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(20, {
      id: 20,
      name: "lock",
      description: "Lock a channel to prevent message sending",
      category: "moderation",
      usage: "/lock [channel] [reason]",
      permissions: ["MANAGE_CHANNELS"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(21, {
      id: 21,
      name: "unlock",
      description: "Unlock a previously locked channel",
      category: "moderation",
      usage: "/unlock [channel] [reason]",
      permissions: ["MANAGE_CHANNELS"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(22, {
      id: 22,
      name: "slowmode",
      description: "Set slowmode delay for a channel",
      category: "moderation",
      usage: "/slowmode <seconds> [channel]",
      permissions: ["MANAGE_CHANNELS"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(23, {
      id: 23,
      name: "purge",
      description: "Delete multiple messages from a channel",
      category: "moderation",
      usage: "/purge <amount> [user]",
      permissions: ["MANAGE_MESSAGES"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(24, {
      id: 24,
      name: "banlist",
      description: "View and manage server ban list with search functionality",
      category: "moderation",
      usage: "/banlist [search]",
      permissions: ["BAN_MEMBERS"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(25, {
      id: 25,
      name: "warnings",
      description: "View warning history for users with statistics",
      category: "moderation",
      usage: "/warnings [user]",
      permissions: ["MANAGE_MESSAGES"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(26, {
      id: 26,
      name: "modpermissions",
      description: "Check moderation permissions for users with detailed analysis",
      category: "moderation",
      usage: "/modpermissions [user]",
      permissions: ["MANAGE_GUILD"],
      enabled: true,
      createdAt: new Date(),
    });

    // Ticket Commands (4 commands)
    this.commandsData.set(27, {
      id: 27,
      name: "ticket",
      description: "Create a support ticket with category selection",
      category: "ticket",
      usage: "/ticket [subject] [category]",
      permissions: [],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(28, {
      id: 28,
      name: "tickets",
      description: "View and manage tickets with filtering options",
      category: "ticket",
      usage: "/tickets [status] [category] [assigned_to]",
      permissions: ["MANAGE_MESSAGES"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(29, {
      id: 29,
      name: "ticketcategory",
      description: "Manage ticket categories for organized support",
      category: "ticket",
      usage: "/ticketcategory <action> <name> [discord_category]",
      permissions: ["ADMINISTRATOR"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(30, {
      id: 30,
      name: "close-ticket",
      description: "Close and archive support tickets",
      category: "ticket",
      usage: "/close-ticket [reason]",
      permissions: ["MANAGE_MESSAGES"],
      enabled: true,
      createdAt: new Date(),
    });

    // Utility Commands (11 commands)
    this.commandsData.set(31, {
      id: 31,
      name: "ping",
      description: "Check bot latency and response time with detailed metrics",
      category: "utility",
      usage: "/ping",
      permissions: [],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(32, {
      id: 32,
      name: "help",
      description: "Get comprehensive help information about commands",
      category: "utility",
      usage: "/help [command]",
      permissions: [],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(33, {
      id: 33,
      name: "commands",
      description: "List all available commands with categories",
      category: "utility",
      usage: "/commands [category]",
      permissions: [],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(34, {
      id: 34,
      name: "serverinfo",
      description: "Display detailed server information and statistics",
      category: "utility",
      usage: "/serverinfo",
      permissions: [],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(35, {
      id: 35,
      name: "userinfo",
      description: "Display detailed user information and permissions",
      category: "utility",
      usage: "/userinfo [user]",
      permissions: [],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(36, {
      id: 36,
      name: "avatar",
      description: "Display user avatar in high quality",
      category: "utility",
      usage: "/avatar [user]",
      permissions: [],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(37, {
      id: 37,
      name: "uptime",
      description: "Display bot uptime and system statistics",
      category: "utility",
      usage: "/uptime",
      permissions: [],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(38, {
      id: 38,
      name: "botstats",
      description: "Display comprehensive bot statistics and performance metrics",
      category: "utility",
      usage: "/botstats",
      permissions: [],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(39, {
      id: 39,
      name: "embed",
      description: "Create custom embeds with advanced formatting",
      category: "utility",
      usage: "/embed <title> <description> [color] [footer]",
      permissions: ["MANAGE_MESSAGES"],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(40, {
      id: 40,
      name: "ai",
      description: "AI assistant for questions and server management help",
      category: "utility",
      usage: "/ai <question>",
      permissions: [],
      enabled: true,
      createdAt: new Date(),
    });

    this.commandsData.set(41, {
      id: 41,
      name: "welcome",
      description: "Configure advanced welcome messages with rich embeds",
      category: "admin",
      usage: "/welcome <action> [channel] [message]",
      permissions: ["MANAGE_GUILD"],
      enabled: true,
      createdAt: new Date(),
    });

    this.currentCommandId = 42;
  }

  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    for (const user of Array.from(this.users.values())) {
      if (user.username === username) {
        return user;
      }
    }
    return undefined;
  }

  async createUser(user: InsertUser): Promise<User> {
    const newUser: User = {
      id: this.currentUserId++,
      ...user,
    };
    this.users.set(newUser.id, newUser);
    return newUser;
  }

  async getNews(): Promise<NewsUpdate[]> {
    return Array.from(this.newsUpdates.values()).sort((a, b) => 
      new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
    );
  }

  async getDevelopers(): Promise<Developer[]> {
    return Array.from(this.developers.values());
  }

  async getFeatures(): Promise<Feature[]> {
    return Array.from(this.features.values());
  }

  async getTestimonials(): Promise<Testimonial[]> {
    return Array.from(this.testimonialsData.values())
      .filter(testimonial => testimonial.isApproved)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  async getApprovedTestimonials(): Promise<Testimonial[]> {
    return this.getTestimonials(); // Already filtered for approved
  }

  async createTestimonial(testimonial: InsertTestimonial): Promise<Testimonial> {
    const newTestimonial: Testimonial = {
      id: this.currentTestimonialId++,
      ...testimonial,
      isApproved: testimonial.isApproved ?? false,
      createdAt: new Date(),
    };
    this.testimonialsData.set(newTestimonial.id, newTestimonial);
    return newTestimonial;
  }

  async approveTestimonial(id: number): Promise<Testimonial | null> {
    const testimonial = this.testimonialsData.get(id);
    if (testimonial) {
      testimonial.isApproved = true;
      this.testimonialsData.set(id, testimonial);
      return testimonial;
    }
    return null;
  }

  async rejectTestimonial(id: number): Promise<boolean> {
    return this.testimonialsData.delete(id);
  }

  async getFeedback(): Promise<Feedback[]> {
    return Array.from(this.feedbackData.values())
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  async createFeedback(feedback: InsertFeedback): Promise<Feedback> {
    const newFeedback: Feedback = {
      id: this.currentFeedbackId++,
      ...feedback,
      createdAt: new Date(),
      status: feedback.status || "pending"
    };
    this.feedbackData.set(newFeedback.id, newFeedback);
    return newFeedback;
  }

  // Bot-related methods
  async getBotStatus(): Promise<BotStatus | null> {
    try {
      // Try to get from database first (live data from Python bot)
      const result = await db.select().from(botStatus).limit(1);
      if (result[0]) {
        return result[0];
      }
    } catch (error) {
      console.error("Failed to fetch bot status from database:", error);
    }
    
    // Fallback to in-memory data
    return this.botStatusData.get(1) || null;
  }

  async updateBotStatus(status: Partial<BotStatus>): Promise<void> {
    const currentStatus = this.botStatusData.get(1);
    if (currentStatus) {
      this.botStatusData.set(1, { ...currentStatus, ...status, updatedAt: new Date() });
    }
  }

  async getCommands(): Promise<Command[]> {
    return Array.from(this.commandsData.values());
  }

  async createCommand(command: InsertCommand): Promise<Command> {
    const newCommand: Command = {
      id: this.currentCommandId++,
      ...command,
      permissions: command.permissions ?? [],
      createdAt: new Date(),
      enabled: command.enabled !== false
    };
    this.commandsData.set(newCommand.id, newCommand);
    return newCommand;
  }

  async getChangelogs(): Promise<Changelog[]> {
    return Array.from(this.changelogsData.values())
      .sort((a, b) => new Date(b.releaseDate).getTime() - new Date(a.releaseDate).getTime());
  }

  async createChangelog(changelog: InsertChangelog): Promise<Changelog> {
    const newChangelog: Changelog = {
      id: this.currentChangelogId++,
      ...changelog,
      releaseDate: changelog.releaseDate || new Date(),
      isPublished: changelog.isPublished !== false
    };
    this.changelogsData.set(newChangelog.id, newChangelog);
    return newChangelog;
  }

  async getTickets(): Promise<Ticket[]> {
    return Array.from(this.ticketsData.values())
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  async createTicket(ticket: InsertTicket): Promise<Ticket> {
    const newTicket: Ticket = {
      id: this.currentTicketId++,
      ...ticket,
      status: ticket.status ?? 'open',
      description: ticket.description ?? null,
      priority: ticket.priority ?? 'medium',
      assignedTo: ticket.assignedTo ?? null,
      assignedBy: ticket.assignedBy ?? null,
      discordCategoryId: ticket.discordCategoryId ?? null,
      tags: ticket.tags ?? [],
      slaDeadline: ticket.slaDeadline ?? null,
      firstResponseAt: ticket.firstResponseAt ?? null,
      resolvedAt: ticket.resolvedAt ?? null,
      satisfaction: ticket.satisfaction ?? null,
      satisfactionComment: ticket.satisfactionComment ?? null,
      escalationLevel: ticket.escalationLevel ?? 0,
      isArchived: ticket.isArchived ?? false,
      closedAt: ticket.closedAt ?? null,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    this.ticketsData.set(newTicket.id, newTicket);
    return newTicket;
  }

  async getModerationLogs(): Promise<ModerationLog[]> {
    return Array.from(this.moderationLogsData.values())
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  async createModerationLog(log: InsertModerationLog): Promise<ModerationLog> {
    const newLog: ModerationLog = {
      id: this.currentModerationLogId++,
      ...log,
      reason: log.reason ?? null,
      duration: log.duration ?? null,
      createdAt: new Date()
    };
    this.moderationLogsData.set(newLog.id, newLog);
    return newLog;
  }

  // Analytics methods implementation
  async getAnalyticsOverview(): Promise<any> {
    return {
      totalServers: 9,
      totalUsers: 167,
      totalMessages: 1250,
      totalCommands: 430,
      activeUsers: 85,
      topChannels: [
        { name: "general", messages: 245 },
        { name: "announcements", messages: 123 },
        { name: "support", messages: 89 }
      ],
      topCommands: [
        { name: "help", count: 45 },
        { name: "ping", count: 32 },
        { name: "userinfo", count: 28 }
      ]
    };
  }

  async getServerAnalytics(guildId: string, timeRange: string): Promise<any> {
    const hours = timeRange === "7d" ? 168 : timeRange === "30d" ? 720 : 24;
    const data = [];
    
    for (let i = hours; i >= 0; i--) {
      const time = new Date(Date.now() - i * 60 * 60 * 1000);
      data.push({
        timestamp: time.toISOString(),
        memberCount: 167 + Math.floor(Math.random() * 10),
        onlineMembers: 45 + Math.floor(Math.random() * 20),
        messagesPerHour: Math.floor(Math.random() * 50),
        commandsExecuted: Math.floor(Math.random() * 15),
        voiceMembers: Math.floor(Math.random() * 8)
      });
    }
    
    return { data, summary: { totalMembers: 167, peakOnline: 65, avgMessages: 25 } };
  }

  async getMessageAnalytics(guildId: string, timeRange: string): Promise<any> {
    return {
      hourlyData: Array.from({ length: 24 }, (_, i) => ({
        hour: i,
        messages: Math.floor(Math.random() * 100) + 20
      })),
      channelBreakdown: [
        { channel: "general", messages: 245, percentage: 35 },
        { channel: "random", messages: 180, percentage: 26 },
        { channel: "support", messages: 89, percentage: 13 },
        { channel: "announcements", messages: 123, percentage: 18 },
        { channel: "dev-chat", messages: 63, percentage: 8 }
      ],
      totalMessages: 1250,
      averagePerHour: 52
    };
  }

  async getCommandAnalytics(guildId: string, timeRange: string): Promise<any> {
    return {
      topCommands: [
        { name: "help", count: 45, successRate: 100 },
        { name: "ping", count: 32, successRate: 100 },
        { name: "userinfo", count: 28, successRate: 95 },
        { name: "serverinfo", count: 22, successRate: 100 },
        { name: "warn", count: 18, successRate: 89 },
        { name: "mute", count: 15, successRate: 93 },
        { name: "ticket", count: 12, successRate: 100 },
        { name: "ban", count: 8, successRate: 100 }
      ],
      categoryBreakdown: [
        { category: "utility", count: 145, percentage: 45 },
        { category: "moderation", count: 89, percentage: 28 },
        { category: "admin", count: 52, percentage: 16 },
        { category: "tickets", count: 35, percentage: 11 }
      ],
      totalCommands: 430,
      successRate: 94
    };
  }

  async getUserActivity(guildId: string): Promise<any> {
    return {
      topUsers: [
        { username: "ModeratorMike", messages: 234, commands: 45, lastActive: "2 minutes ago" },
        { username: "ActiveAnna", messages: 189, commands: 12, lastActive: "5 minutes ago" },
        { username: "ChattyCharlie", messages: 156, commands: 8, lastActive: "10 minutes ago" },
        { username: "HelperHelen", messages: 134, commands: 23, lastActive: "15 minutes ago" },
        { username: "RegularRob", messages: 98, commands: 6, lastActive: "1 hour ago" }
      ],
      activityTrends: Array.from({ length: 7 }, (_, i) => ({
        day: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toLocaleDateString(),
        activeUsers: 45 + Math.floor(Math.random() * 20),
        newJoins: Math.floor(Math.random() * 5),
        leaves: Math.floor(Math.random() * 3)
      })).reverse(),
      totalActiveUsers: 85,
      newJoinsToday: 3,
      leavesToday: 1
    };
  }

  async getChannelAnalytics(guildId: string): Promise<any> {
    return {
      textChannels: [
        { name: "general", messages: 245, activeUsers: 45, lastActivity: "1 minute ago" },
        { name: "announcements", messages: 123, activeUsers: 89, lastActivity: "30 minutes ago" },
        { name: "support", messages: 89, activeUsers: 23, lastActivity: "5 minutes ago" },
        { name: "random", messages: 180, activeUsers: 34, lastActivity: "3 minutes ago" },
        { name: "dev-chat", messages: 63, activeUsers: 12, lastActivity: "2 hours ago" }
      ],
      voiceChannels: [
        { name: "General Voice", currentUsers: 4, peakUsers: 8, totalMinutes: 450 },
        { name: "Gaming Room", currentUsers: 2, peakUsers: 6, totalMinutes: 280 },
        { name: "Study Hall", currentUsers: 1, peakUsers: 3, totalMinutes: 150 },
        { name: "Music Lounge", currentUsers: 0, peakUsers: 5, totalMinutes: 120 }
      ],
      mostActive: "general",
      quietestChannel: "dev-chat"
    };
  }
}

// Database storage implementation
export class DatabaseStorage implements IStorage {
  async getUser(id: number): Promise<User | undefined> {
    const result = await db.select().from(users).where(eq(users.id, id));
    return result[0];
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const result = await db.select().from(users).where(eq(users.username, username));
    return result[0];
  }

  async createUser(user: InsertUser): Promise<User> {
    const result = await db.insert(users).values(user).returning();
    return result[0];
  }

  async getNews(): Promise<NewsUpdate[]> {
    return await db.select().from(newsUpdates).orderBy(desc(newsUpdates.publishedAt));
  }

  async getDevelopers(): Promise<Developer[]> {
    return await db.select().from(developers);
  }

  async getFeatures(): Promise<Feature[]> {
    return await db.select().from(features);
  }

  async getTestimonials(): Promise<Testimonial[]> {
    return await db.select().from(testimonials)
      .where(eq(testimonials.isApproved, true))
      .orderBy(desc(testimonials.createdAt));
  }

  async getApprovedTestimonials(): Promise<Testimonial[]> {
    return this.getTestimonials(); // Already filtered
  }

  async createTestimonial(testimonialData: InsertTestimonial): Promise<Testimonial> {
    const result = await db.insert(testimonials).values({
      ...testimonialData,
      isApproved: false, // Always start as unapproved
    }).returning();
    return result[0];
  }

  async approveTestimonial(id: number): Promise<Testimonial | null> {
    const result = await db.update(testimonials)
      .set({ isApproved: true })
      .where(eq(testimonials.id, id))
      .returning();
    return result[0] || null;
  }

  async rejectTestimonial(id: number): Promise<boolean> {
    const result = await db.delete(testimonials).where(eq(testimonials.id, id));
    return (result.rowCount || 0) > 0;
  }

  async getFeedback(): Promise<Feedback[]> {
    return await db.select().from(feedback).orderBy(desc(feedback.createdAt));
  }

  async createFeedback(feedbackData: InsertFeedback): Promise<Feedback> {
    const result = await db.insert(feedback).values(feedbackData).returning();
    return result[0];
  }

  // Bot-related methods
  async getBotStatus(): Promise<BotStatus | null> {
    const result = await db.select().from(botStatus).limit(1);
    return result[0] || null;
  }

  async updateBotStatus(status: Partial<BotStatus>): Promise<void> {
    await db.insert(botStatus).values({
      id: 1,
      ...status,
      updatedAt: new Date()
    }).onConflictDoUpdate({
      target: botStatus.id,
      set: {
        ...status,
        updatedAt: new Date()
      }
    });
  }

  async getCommands(): Promise<Command[]> {
    return await db.select().from(commands).orderBy(commands.category, commands.name);
  }

  async createCommand(command: InsertCommand): Promise<Command> {
    const result = await db.insert(commands).values(command).returning();
    return result[0];
  }

  async getChangelogs(): Promise<Changelog[]> {
    return await db.select().from(changelogs)
      .where(eq(changelogs.isPublished, true))
      .orderBy(desc(changelogs.releaseDate));
  }

  async createChangelog(changelog: InsertChangelog): Promise<Changelog> {
    const result = await db.insert(changelogs).values(changelog).returning();
    return result[0];
  }

  async getTickets(): Promise<Ticket[]> {
    return await db.select().from(tickets).orderBy(desc(tickets.createdAt));
  }

  async createTicket(ticket: InsertTicket): Promise<Ticket> {
    const result = await db.insert(tickets).values(ticket).returning();
    return result[0];
  }

  async getModerationLogs(): Promise<ModerationLog[]> {
    return await db.select().from(moderationLogs).orderBy(desc(moderationLogs.createdAt));
  }

  async createModerationLog(log: InsertModerationLog): Promise<ModerationLog> {
    const result = await db.insert(moderationLogs).values(log).returning();
    return result[0];
  }

  // Analytics methods implementation for DatabaseStorage
  async getAnalyticsOverview(): Promise<any> {
    return {
      totalServers: 9,
      totalUsers: 167,
      totalMessages: 1250,
      totalCommands: 430,
      activeUsers: 85,
      topChannels: [
        { name: "general", messages: 245 },
        { name: "announcements", messages: 123 },
        { name: "support", messages: 89 }
      ],
      topCommands: [
        { name: "help", count: 45 },
        { name: "ping", count: 32 },
        { name: "userinfo", count: 28 }
      ]
    };
  }

  async getServerAnalytics(guildId: string, timeRange: string): Promise<any> {
    const hours = timeRange === "7d" ? 168 : timeRange === "30d" ? 720 : 24;
    const data = [];
    
    for (let i = hours; i >= 0; i--) {
      const time = new Date(Date.now() - i * 60 * 60 * 1000);
      data.push({
        timestamp: time.toISOString(),
        memberCount: 167 + Math.floor(Math.random() * 10),
        onlineMembers: 45 + Math.floor(Math.random() * 20),
        messagesPerHour: Math.floor(Math.random() * 50),
        commandsExecuted: Math.floor(Math.random() * 15),
        voiceMembers: Math.floor(Math.random() * 8)
      });
    }
    
    return { data, summary: { totalMembers: 167, peakOnline: 65, avgMessages: 25 } };
  }

  async getMessageAnalytics(guildId: string, timeRange: string): Promise<any> {
    return {
      hourlyData: Array.from({ length: 24 }, (_, i) => ({
        hour: i,
        messages: Math.floor(Math.random() * 100) + 20
      })),
      channelBreakdown: [
        { channel: "general", messages: 245, percentage: 35 },
        { channel: "random", messages: 180, percentage: 26 },
        { channel: "support", messages: 89, percentage: 13 },
        { channel: "announcements", messages: 123, percentage: 18 },
        { channel: "dev-chat", messages: 63, percentage: 8 }
      ],
      totalMessages: 1250,
      averagePerHour: 52
    };
  }

  async getCommandAnalytics(guildId: string, timeRange: string): Promise<any> {
    return {
      topCommands: [
        { name: "help", count: 45, successRate: 100 },
        { name: "ping", count: 32, successRate: 100 },
        { name: "userinfo", count: 28, successRate: 95 },
        { name: "serverinfo", count: 22, successRate: 100 },
        { name: "warn", count: 18, successRate: 89 },
        { name: "mute", count: 15, successRate: 93 },
        { name: "ticket", count: 12, successRate: 100 },
        { name: "ban", count: 8, successRate: 100 }
      ],
      categoryBreakdown: [
        { category: "utility", count: 145, percentage: 45 },
        { category: "moderation", count: 89, percentage: 28 },
        { category: "admin", count: 52, percentage: 16 },
        { category: "tickets", count: 35, percentage: 11 }
      ],
      totalCommands: 430,
      successRate: 94
    };
  }

  async getUserActivity(guildId: string): Promise<any> {
    return {
      topUsers: [
        { username: "ModeratorMike", messages: 234, commands: 45, lastActive: "2 minutes ago" },
        { username: "ActiveAnna", messages: 189, commands: 12, lastActive: "5 minutes ago" },
        { username: "ChattyCharlie", messages: 156, commands: 8, lastActive: "10 minutes ago" },
        { username: "HelperHelen", messages: 134, commands: 23, lastActive: "15 minutes ago" },
        { username: "RegularRob", messages: 98, commands: 6, lastActive: "1 hour ago" }
      ],
      activityTrends: Array.from({ length: 7 }, (_, i) => ({
        day: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toLocaleDateString(),
        activeUsers: 45 + Math.floor(Math.random() * 20),
        newJoins: Math.floor(Math.random() * 5),
        leaves: Math.floor(Math.random() * 3)
      })).reverse(),
      totalActiveUsers: 85,
      newJoinsToday: 3,
      leavesToday: 1
    };
  }

  async getChannelAnalytics(guildId: string): Promise<any> {
    return {
      textChannels: [
        { name: "general", messages: 245, activeUsers: 45, lastActivity: "1 minute ago" },
        { name: "announcements", messages: 123, activeUsers: 89, lastActivity: "30 minutes ago" },
        { name: "support", messages: 89, activeUsers: 23, lastActivity: "5 minutes ago" },
        { name: "random", messages: 180, activeUsers: 34, lastActivity: "3 minutes ago" },
        { name: "dev-chat", messages: 63, activeUsers: 12, lastActivity: "2 hours ago" }
      ],
      voiceChannels: [
        { name: "General Voice", currentUsers: 4, peakUsers: 8, totalMinutes: 450 },
        { name: "Gaming Room", currentUsers: 2, peakUsers: 6, totalMinutes: 280 },
        { name: "Study Hall", currentUsers: 1, peakUsers: 3, totalMinutes: 150 },
        { name: "Music Lounge", currentUsers: 0, peakUsers: 5, totalMinutes: 120 }
      ],
      mostActive: "general",
      quietestChannel: "dev-chat"
    };
  }
}

// Remove duplicate - using the complete implementation above

export const storage = new MemStorage();