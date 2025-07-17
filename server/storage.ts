import { users, newsUpdates, developers, features, testimonials, feedback, serverConfigs, customCommands, type User, type InsertUser, type NewsUpdate, type Developer, type Feature, type Testimonial, type InsertTestimonial, type Feedback, type InsertFeedback, type ServerConfig, type InsertServerConfig, type CustomCommand, type InsertCustomCommand } from "@shared/schema";
import { db } from "./db";
import { eq, desc } from "drizzle-orm";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  getNewsUpdates(): Promise<NewsUpdate[]>;
  getDevelopers(): Promise<Developer[]>;
  getFeatures(): Promise<Feature[]>;
  getTestimonials(): Promise<Testimonial[]>;
  createTestimonial(testimonial: InsertTestimonial): Promise<Testimonial>;
  createFeedback(feedback: InsertFeedback): Promise<Feedback>;
  
  // Server configuration methods
  getServerConfig(guildId: string): Promise<ServerConfig | undefined>;
  createServerConfig(config: InsertServerConfig): Promise<ServerConfig>;
  updateServerConfig(guildId: string, config: Partial<ServerConfig>): Promise<ServerConfig>;
  
  // Custom commands methods
  getCustomCommands(guildId: string): Promise<CustomCommand[]>;
  createCustomCommand(command: InsertCustomCommand): Promise<CustomCommand>;
  updateCustomCommand(id: number, command: Partial<CustomCommand>): Promise<CustomCommand>;
  deleteCustomCommand(id: number): Promise<boolean>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private newsUpdates: Map<number, NewsUpdate>;
  private developers: Map<number, Developer>;
  private features: Map<number, Feature>;
  private testimonialsData: Map<number, Testimonial>;
  private feedbackData: Map<number, Feedback>;
  private currentUserId: number;
  private currentNewsId: number;
  private currentDevId: number;
  private currentFeatureId: number;
  private currentTestimonialId: number;
  private currentFeedbackId: number;

  constructor() {
    this.users = new Map();
    this.newsUpdates = new Map();
    this.developers = new Map();
    this.features = new Map();
    this.testimonialsData = new Map();
    this.feedbackData = new Map();
    this.currentUserId = 1;
    this.currentNewsId = 1;
    this.currentDevId = 1;
    this.currentFeatureId = 1;
    this.currentTestimonialId = 1;
    this.currentFeedbackId = 1;
    
    this.initializeData();
  }

  private initializeData() {
    // Initialize developers
    const devs: Developer[] = [
      {
        id: 7,
        name: "Caleb Weston",
        role: "Lead Developer & Founder",
        bio: "Passionate full-stack developer with 3+ years of experience in web development, Discord bot development, and server management. Created NexGuard to provide comprehensive moderation solutions for Discord communities.",
        githubUrl: "https://github.com/calebweston",
        twitterUrl: "https://twitter.com/calebweston",
        linkedinUrl: "https://linkedin.com/in/calebweston",
        location: "United States",
        experience: "3+ years in full-stack development with expertise in Discord bot architecture, database design, and scalable web applications",
        skills: [
          "JavaScript/TypeScript",
          "Node.js",
          "Discord.js",
          "React",
          "PostgreSQL",
          "Express.js",
          "Docker",
          "Git/GitHub",
          "API Development",
          "Database Design",
          "Server Administration",
          "Web Development"
        ],
        specialties: [
          "Discord Bot Development",
          "Server Moderation Systems",
          "Database Optimization",
          "API Architecture",
          "Real-time Applications",
          "Community Management Tools"
        ],
        achievements: [
          "Successfully deployed NexGuard to 8+ Discord servers",
          "Developed 64+ slash commands for comprehensive server management",
          "Created advanced moderation system with AI-powered spam detection",
          "Built secure OAuth2 authentication system",
          "Implemented real-time dashboard with PostgreSQL integration",
          "Designed scalable bot architecture handling 157+ users"
        ],
        projects: [
          "NexGuard Discord Bot - Advanced moderation and management bot",
          "NexGuard Web Dashboard - Full-stack admin panel with OAuth2",
          "Custom Command System - Dynamic command creation and management",
          "Anti-Raid Protection - Automated server protection system",
          "Economy System - Currency and rewards management",
          "Ticket System - Support ticket automation"
        ],
        education: "Self-taught developer with continuous learning through practical projects and modern web technologies",
        email: "nexguards@gmail.com",
        discord: "calebweston",
        website: "https://nexguard.replit.app",
        yearsOfExperience: 3
      }
    ];

    // Initialize features based on actual bot capabilities
    const feats: Feature[] = [
      {
        id: 1,
        title: "Advanced Moderation System",
        description: "Comprehensive moderation tools with spam protection, profanity filtering, and automated punishments to maintain server quality.",
        icon: "shield",
        benefits: ["Anti-spam protection", "Profanity filter", "Link protection", "Automated warnings & timeouts", "Mass join raid protection"]
      },
      {
        id: 2,
        title: "Custom Commands",
        description: "Create unlimited custom commands for your server with dynamic responses and variable support.",
        icon: "terminal",
        benefits: ["Unlimited custom commands", "Dynamic responses", "Variable substitution", "Permission-based access", "Easy management via dashboard"]
      },
      {
        id: 3,
        title: "Welcome & Leave Messages",
        description: "Customizable welcome and goodbye messages to create a friendly atmosphere for new members.",
        icon: "user-plus",
        benefits: ["Custom welcome messages", "Goodbye notifications", "Channel-specific messages", "Variable support", "Rich embed formatting"]
      },
      {
        id: 4,
        title: "Auto-Role Assignment",
        description: "Automatically assign roles to new members and manage role hierarchies with ease.",
        icon: "users",
        benefits: ["Auto-role on join", "Muted role management", "Role hierarchy support", "Permission integration", "Bulk role operations"]
      },
      {
        id: 5,
        title: "Comprehensive Logging",
        description: "Track all moderation actions and server events with detailed audit logs and monitoring.",
        icon: "file-text",
        benefits: ["Moderation action logs", "Audit trail tracking", "Channel-specific logging", "Export capabilities", "Real-time monitoring"]
      },
      {
        id: 6,
        title: "Web Dashboard",
        description: "Intuitive web-based control panel with Discord OAuth for secure server management from anywhere.",
        icon: "monitor",
        benefits: ["Discord OAuth login", "Real-time configuration", "Server-specific settings", "Live bot status", "Mobile-friendly interface"]
      },
      {
        id: 7,
        title: "Economy System",
        description: "Engaging economy features with daily rewards and currency management to boost community interaction.",
        icon: "coins",
        benefits: ["Daily reward system", "Currency management", "Balance tracking", "Configurable rewards", "Economy statistics"]
      },
      {
        id: 8,
        title: "Slash Commands",
        description: "Modern Discord slash commands for quick access to all bot features with autocomplete and validation.",
        icon: "slash",
        benefits: ["64+ slash commands", "Autocomplete support", "Input validation", "Permission checking", "Context-aware responses"]
      }
    ];

    // Initialize news updates
    const news: NewsUpdate[] = [
      {
        id: 1,
        title: "AI-Powered Spam Detection",
        content: "Our new machine learning algorithm can now detect sophisticated spam patterns with 99.2% accuracy, providing better protection for your server.",
        category: "NEW FEATURE",
        publishedAt: new Date("2024-01-15"),
        likes: 127,
        comments: 23
      },
      {
        id: 2,
        title: "100K+ Servers Milestone",
        content: "We've reached an incredible milestone! Thank you to all 100,000+ servers and their communities for trusting NexGuard with their moderation needs.",
        category: "COMMUNITY",
        publishedAt: new Date("2024-01-12"),
        likes: 892,
        comments: 156
      },
      {
        id: 3,
        title: "Dashboard 2.0 Released",
        content: "Our completely redesigned web dashboard offers a more intuitive experience with advanced analytics and one-click configuration templates.",
        category: "UPDATE",
        publishedAt: new Date("2024-01-10"),
        likes: 324,
        comments: 67
      },
      {
        id: 4,
        title: "Enhanced Raid Protection",
        content: "New anti-raid features include IP tracking, join pattern analysis, and automatic lockdown capabilities to protect against coordinated attacks.",
        category: "SECURITY",
        publishedAt: new Date("2024-01-08"),
        likes: 456,
        comments: 89
      },
      {
        id: 5,
        title: "New Mini-Games Added",
        content: "Keep your community engaged with our new collection of mini-games including trivia, word games, and interactive challenges.",
        category: "GAMES",
        publishedAt: new Date("2024-01-05"),
        likes: 278,
        comments: 45
      },
      {
        id: 6,
        title: "Server of the Month",
        content: "Congratulations to \"TechHub Community\" for being our featured server! Their innovative use of NexGuard's features creates an amazing experience.",
        category: "FEATURED",
        publishedAt: new Date("2024-01-03"),
        likes: 189,
        comments: 34
      }
    ];

    devs.forEach(dev => this.developers.set(dev.id, dev));
    feats.forEach(feat => this.features.set(feat.id, feat));
    news.forEach(update => this.newsUpdates.set(update.id, update));

    this.currentDevId = devs.length + 1;
    this.currentFeatureId = feats.length + 1;
    this.currentNewsId = news.length + 1;
  }

  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentUserId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async getNewsUpdates(): Promise<NewsUpdate[]> {
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
      .filter(t => t.isApproved)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  async createTestimonial(insertTestimonial: InsertTestimonial): Promise<Testimonial> {
    const id = this.currentTestimonialId++;
    const testimonial: Testimonial = {
      ...insertTestimonial,
      id,
      isApproved: false,
      createdAt: new Date()
    };
    this.testimonialsData.set(id, testimonial);
    return testimonial;
  }

  async createFeedback(insertFeedback: InsertFeedback): Promise<Feedback> {
    const id = this.currentFeedbackId++;
    const feedback: Feedback = {
      ...insertFeedback,
      id,
      status: "pending",
      createdAt: new Date()
    };
    this.feedbackData.set(id, feedback);
    return feedback;
  }
}

export class DatabaseStorage implements IStorage {
  async getUser(id: number): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user || undefined;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user || undefined;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const [user] = await db
      .insert(users)
      .values(insertUser)
      .returning();
    return user;
  }

  async getNewsUpdates(): Promise<NewsUpdate[]> {
    return await db.select().from(newsUpdates);
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

  async createTestimonial(insertTestimonial: InsertTestimonial): Promise<Testimonial> {
    const [testimonial] = await db
      .insert(testimonials)
      .values(insertTestimonial)
      .returning();
    return testimonial;
  }

  async createFeedback(insertFeedback: InsertFeedback): Promise<Feedback> {
    const [feedbackResult] = await db
      .insert(feedback)
      .values(insertFeedback)
      .returning();
    return feedbackResult;
  }

  async getServerConfig(guildId: string): Promise<ServerConfig | undefined> {
    const [config] = await db.select().from(serverConfigs).where(eq(serverConfigs.guildId, guildId));
    return config;
  }

  async createServerConfig(config: InsertServerConfig): Promise<ServerConfig> {
    const [newConfig] = await db.insert(serverConfigs).values(config).returning();
    return newConfig;
  }

  async updateServerConfig(guildId: string, config: Partial<ServerConfig>): Promise<ServerConfig> {
    const [updatedConfig] = await db
      .update(serverConfigs)
      .set({ ...config, updatedAt: new Date() })
      .where(eq(serverConfigs.guildId, guildId))
      .returning();
    return updatedConfig;
  }

  async getCustomCommands(guildId: string): Promise<CustomCommand[]> {
    return await db.select().from(customCommands).where(eq(customCommands.guildId, guildId));
  }

  async createCustomCommand(command: InsertCustomCommand): Promise<CustomCommand> {
    const [newCommand] = await db.insert(customCommands).values(command).returning();
    return newCommand;
  }

  async updateCustomCommand(id: number, command: Partial<CustomCommand>): Promise<CustomCommand> {
    const [updatedCommand] = await db
      .update(customCommands)
      .set(command)
      .where(eq(customCommands.id, id))
      .returning();
    return updatedCommand;
  }

  async deleteCustomCommand(id: number): Promise<boolean> {
    const result = await db.delete(customCommands).where(eq(customCommands.id, id));
    return result.rowCount > 0;
  }
}

export const storage = new DatabaseStorage();
