import { users, newsUpdates, developers, features, testimonials, feedback, type User, type InsertUser, type NewsUpdate, type Developer, type Feature, type Testimonial, type InsertTestimonial, type Feedback, type InsertFeedback } from "@shared/schema";
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
  createTestimonial(testimonial: InsertTestimonial): Promise<Testimonial>;
  getFeedback(): Promise<Feedback[]>;
  createFeedback(feedback: InsertFeedback): Promise<Feedback>;
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
    
    try {
      this.initializeData();
      console.log('Storage initialized successfully');
    } catch (error) {
      console.error('Error initializing storage:', error);
    }
  }

  private initializeData() {
    // Initialize news updates
    this.newsUpdates.set(1, {
      id: 1,
      title: "NexGuard v2.3.2 Released",
      content: "We're excited to announce the release of NexGuard v2.3.2! This update includes improved moderation tools, enhanced security features, and better performance optimizations.",
      category: "Updates",
      publishedAt: new Date('2024-01-15'),
      likes: 45,
      comments: 12,
    });

    this.newsUpdates.set(2, {
      id: 2,
      title: "New Anti-Spam Protection",
      content: "Our latest anti-spam protection system is now live! It provides real-time detection and automatic response to spam attacks, keeping your server clean and safe.",
      category: "Features",
      publishedAt: new Date('2024-01-10'),
      likes: 38,
      comments: 8,
    });

    this.newsUpdates.set(3, {
      id: 3,
      title: "Community Spotlight: BlueLine RolePlay",
      content: "We're featuring BlueLine RolePlay this month! They've been using NexGuard to maintain order in their 500+ member community with great success.",
      category: "Community",
      publishedAt: new Date('2024-01-05'),
      likes: 67,
      comments: 23,
    });

    this.currentNewsId = 4;

    // Initialize developers
    this.developers.set(1, {
      id: 1,
      name: "Caleb Weston",
      role: "Lead Developer",
      bio: "Passionate full-stack developer with expertise in Discord bot development, web technologies, and system architecture. Leading NexGuard's development with a focus on creating robust, scalable solutions for Discord communities.",
      githubUrl: "https://github.com/calebweston",
      twitterUrl: "https://twitter.com/calebweston",
      linkedinUrl: "https://linkedin.com/in/calebweston",
      location: "United States",
      experience: "5+ years of experience in software development, specializing in Discord bot development, web applications, and community management tools.",
      skills: ["JavaScript", "TypeScript", "Node.js", "React", "Discord.js", "PostgreSQL", "Docker", "AWS", "Python", "Express.js"],
      specialties: ["Discord Bot Development", "Full-Stack Web Development", "Database Architecture", "API Design", "Community Management Tools"],
      achievements: ["Built and maintained NexGuard serving 100+ Discord servers", "Developed advanced moderation systems", "Created comprehensive ticket management solutions", "Implemented real-time monitoring and analytics"],
      projects: ["NexGuard Discord Bot", "Advanced Moderation Dashboard", "Custom Command System", "Real-time Analytics Platform"],
      education: "Computer Science",
      email: "caleb@nexguard.com",
      discord: "calebweston",
      website: "https://calebweston.dev",
      yearsOfExperience: 5,
    });

    this.currentDevId = 2;

    // Initialize features
    this.features.set(1, {
      id: 1,
      title: "Advanced Moderation",
      description: "Comprehensive moderation tools including auto-moderation, warning systems, and customizable punishment workflows.",
      icon: "shield",
      benefits: ["Automated rule enforcement", "Customizable warning system", "Detailed moderation logs", "Role-based permissions"],
    });

    this.features.set(2, {
      id: 2,
      title: "Ticket System",
      description: "Professional support ticket system with categories, priorities, and staff assignment capabilities.",
      icon: "ticket",
      benefits: ["Organized support workflow", "Staff assignment", "Ticket categories", "Response time tracking"],
    });

    this.features.set(3, {
      id: 3,
      title: "Custom Commands",
      description: "Create and manage custom commands with variables, permissions, and advanced response options.",
      icon: "command",
      benefits: ["Unlimited custom commands", "Variable support", "Permission controls", "Rich embed responses"],
    });

    this.features.set(4, {
      id: 4,
      title: "Welcome System",
      description: "Automated welcome messages, role assignment, and member verification for new server members.",
      icon: "users",
      benefits: ["Automated greetings", "Role assignment", "Member verification", "Customizable messages"],
    });

    this.currentFeatureId = 5;

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
  }

  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    for (const user of this.users.values()) {
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

  async createTestimonial(testimonial: InsertTestimonial): Promise<Testimonial> {
    const newTestimonial: Testimonial = {
      id: this.currentTestimonialId++,
      ...testimonial,
      createdAt: new Date(),
    };
    this.testimonialsData.set(newTestimonial.id, newTestimonial);
    return newTestimonial;
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
    };
    this.feedbackData.set(newFeedback.id, newFeedback);
    return newFeedback;
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

  async createTestimonial(testimonial: InsertTestimonial): Promise<Testimonial> {
    const result = await db.insert(testimonials).values(testimonial).returning();
    return result[0];
  }

  async getFeedback(): Promise<Feedback[]> {
    return await db.select().from(feedback).orderBy(desc(feedback.createdAt));
  }

  async createFeedback(feedbackData: InsertFeedback): Promise<Feedback> {
    const result = await db.insert(feedback).values(feedbackData).returning();
    return result[0];
  }
}

// Use in-memory storage for development, database for production
export const storage = new MemStorage();