import { users, newsUpdates, developers, features, type User, type InsertUser, type NewsUpdate, type Developer, type Feature } from "@shared/schema";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  getNewsUpdates(): Promise<NewsUpdate[]>;
  getDevelopers(): Promise<Developer[]>;
  getFeatures(): Promise<Feature[]>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private newsUpdates: Map<number, NewsUpdate>;
  private developers: Map<number, Developer>;
  private features: Map<number, Feature>;
  private currentUserId: number;
  private currentNewsId: number;
  private currentDevId: number;
  private currentFeatureId: number;

  constructor() {
    this.users = new Map();
    this.newsUpdates = new Map();
    this.developers = new Map();
    this.features = new Map();
    this.currentUserId = 1;
    this.currentNewsId = 1;
    this.currentDevId = 1;
    this.currentFeatureId = 1;
    
    this.initializeData();
  }

  private initializeData() {
    // Initialize developers
    const devs: Developer[] = [
      {
        id: 1,
        name: "Alex Rivera",
        role: "Lead Developer",
        bio: "Full-stack developer with 5+ years of experience in Discord bot development and server management.",
        githubUrl: "https://github.com/alexrivera",
        twitterUrl: "https://twitter.com/alexrivera",
        linkedinUrl: "https://linkedin.com/in/alexrivera"
      },
      {
        id: 2,
        name: "Sarah Chen",
        role: "Backend Engineer",
        bio: "Specialized in scalable bot architecture and database optimization for high-traffic Discord servers.",
        githubUrl: "https://github.com/sarahchen",
        twitterUrl: "https://twitter.com/sarahchen",
        linkedinUrl: "https://linkedin.com/in/sarahchen"
      },
      {
        id: 3,
        name: "Marcus Johnson",
        role: "UX/UI Designer",
        bio: "Creates intuitive user interfaces and seamless user experiences for Discord bot interactions.",
        githubUrl: "https://github.com/marcusj",
        twitterUrl: "https://twitter.com/marcusj",
        linkedinUrl: "https://linkedin.com/in/marcusj"
      }
    ];

    // Initialize features
    const feats: Feature[] = [
      {
        id: 1,
        title: "Advanced Moderation",
        description: "Automated rule enforcement, smart spam detection, and customizable punishment systems to keep your server clean.",
        icon: "gavel",
        benefits: ["Auto-moderation with AI detection", "Customizable warning system", "Raid protection & anti-spam", "Temporary bans & mutes"]
      },
      {
        id: 2,
        title: "Server Analytics",
        description: "Comprehensive insights into your server's activity, member engagement, and moderation statistics.",
        icon: "chart-line",
        benefits: ["Member activity tracking", "Detailed moderation logs", "Channel usage statistics", "Growth analytics"]
      },
      {
        id: 3,
        title: "Role Management",
        description: "Automated role assignment, reaction roles, and advanced permission management for seamless server organization.",
        icon: "users",
        benefits: ["Reaction role system", "Auto-role assignment", "Permission templates", "Role hierarchy management"]
      },
      {
        id: 4,
        title: "Smart Notifications",
        description: "Customizable notification system for server events, moderation actions, and important updates.",
        icon: "bell",
        benefits: ["Welcome & goodbye messages", "Moderation alerts", "Custom event notifications", "Scheduled announcements"]
      },
      {
        id: 5,
        title: "Entertainment & Games",
        description: "Engaging mini-games, trivia, and interactive features to keep your community active and entertained.",
        icon: "gamepad",
        benefits: ["Interactive games & trivia", "Economy system", "Leaderboards", "Custom commands"]
      },
      {
        id: 6,
        title: "Easy Configuration",
        description: "Intuitive web dashboard and slash commands make setup and management effortless for any server size.",
        icon: "cog",
        benefits: ["Web-based dashboard", "Slash command interface", "One-click setup templates", "Backup & restore settings"]
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
}

export const storage = new MemStorage();
