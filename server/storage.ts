import { 
  users, newsUpdates, developers, features, testimonials, feedback, 
  botStatus, commands, changelogs, tickets, moderationLogs, channelAnalytics,
  type User, type UpsertUser, type InsertUser,
  type NewsUpdate, type Developer, type Feature, 
  type Testimonial, type InsertTestimonial,
  type Feedback, type InsertFeedback,
  type BotStatus, type Command, type InsertCommand,
  type Changelog, type InsertChangelog,
  type Ticket, type InsertTicket,
  type ModerationLog, type InsertModerationLog
} from "@shared/schema";
import { db } from "./db";
import { eq, desc } from "drizzle-orm";

// Interface for storage operations
export interface IStorage {
  // Discord Auth user operations - mandatory for Discord Auth
  getUser(id: string): Promise<User | undefined>;
  upsertUser(user: UpsertUser): Promise<User>;
  
  // Legacy user operations
  getUserByUsername?(username: string): Promise<User | undefined>;
  createUser?(user: InsertUser): Promise<User>;
  
  // Content operations
  getNews(): Promise<NewsUpdate[]>;
  getDevelopers(): Promise<Developer[]>;
  getFeatures(): Promise<Feature[]>;
  getTestimonials(): Promise<Testimonial[]>;
  getApprovedTestimonials(): Promise<Testimonial[]>;
  createTestimonial(testimonial: InsertTestimonial): Promise<Testimonial>;
  approveTestimonial(id: number): Promise<Testimonial | null>;
  rejectTestimonial(id: number): Promise<boolean>;
  getFeedback(): Promise<Feedback[]>;
  createFeedback(feedbackData: InsertFeedback): Promise<Feedback>;
  
  // Bot operations
  getBotStatus(): Promise<BotStatus | null>;
  updateBotStatus(statusData: Partial<BotStatus>): Promise<void>;
  getCommands(): Promise<Command[]>;
  createCommand(command: InsertCommand): Promise<Command>;
  getChangelogs(): Promise<Changelog[]>;
  createChangelog(changelog: InsertChangelog): Promise<Changelog>;
  getTickets(): Promise<Ticket[]>;
  createTicket(ticket: InsertTicket): Promise<Ticket>;
  getModerationLogs(): Promise<ModerationLog[]>;
  createModerationLog(log: InsertModerationLog): Promise<ModerationLog>;
  
  // Analytics operations
  getAnalyticsOverview(): Promise<any>;
  getServerAnalytics(guildId: string, timeRange: string): Promise<any>;
  getMessageAnalytics(guildId: string, timeRange: string): Promise<any>;
  getCommandAnalytics(guildId: string, timeRange: string): Promise<any>;
  getUserActivity(guildId: string): Promise<any>;
  getChannelAnalytics(guildId: string): Promise<any>;
}

export class DatabaseStorage implements IStorage {
  // Discord Auth user methods - mandatory for Discord Auth
  async getUser(id: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user;
  }

  async upsertUser(userData: UpsertUser): Promise<User> {
    const [user] = await db
      .insert(users)
      .values(userData)
      .onConflictDoUpdate({
        target: users.id,
        set: {
          ...userData,
          updatedAt: new Date(),
        },
      })
      .returning();
    return user;
  }

  // Legacy user operations
  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user;
  }

  async createUser(userData: InsertUser): Promise<User> {
    const [user] = await db.insert(users).values(userData).returning();
    return user;
  }

  // Content operations
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
    return await db.select().from(testimonials).orderBy(desc(testimonials.createdAt));
  }

  async getApprovedTestimonials(): Promise<Testimonial[]> {
    return await db.select().from(testimonials);
  }

  async createTestimonial(testimonial: InsertTestimonial): Promise<Testimonial> {
    const [newTestimonial] = await db.insert(testimonials).values(testimonial).returning();
    return newTestimonial;
  }

  async approveTestimonial(id: number): Promise<Testimonial | null> {
    const [testimonial] = await db.select().from(testimonials).where(eq(testimonials.id, id));
    return testimonial || null;
  }

  async rejectTestimonial(id: number): Promise<boolean> {
    return true;
  }

  async getFeedback(): Promise<Feedback[]> {
    return await db.select().from(feedback);
  }

  async createFeedback(feedbackData: InsertFeedback): Promise<Feedback> {
    const [newFeedback] = await db.insert(feedback).values(feedbackData).returning();
    return newFeedback;
  }

  // Bot operations
  async getBotStatus(): Promise<BotStatus | null> {
    const [status] = await db.select().from(botStatus).limit(1);
    return status || null;
  }

  async updateBotStatus(statusData: Partial<BotStatus>): Promise<void> {
    await db.insert(botStatus).values(statusData as any).onConflictDoUpdate({
      target: botStatus.id,
      set: { ...statusData, updatedAt: new Date() }
    });
  }

  async getCommands(): Promise<Command[]> {
    return await db.select().from(commands);
  }

  async createCommand(command: InsertCommand): Promise<Command> {
    const [newCommand] = await db.insert(commands).values(command).returning();
    return newCommand;
  }

  async getChangelogs(): Promise<Changelog[]> {
    return await db.select().from(changelogs).orderBy(desc(changelogs.release_date));
  }

  async createChangelog(changelog: InsertChangelog): Promise<Changelog> {
    const [newChangelog] = await db.insert(changelogs).values(changelog).returning();
    return newChangelog;
  }

  async getTickets(): Promise<Ticket[]> {
    return await db.select().from(tickets);
  }

  async createTicket(ticket: InsertTicket): Promise<Ticket> {
    const [newTicket] = await db.insert(tickets).values(ticket).returning();
    return newTicket;
  }

  async getModerationLogs(): Promise<ModerationLog[]> {
    return await db.select().from(moderationLogs);
  }

  async createModerationLog(log: InsertModerationLog): Promise<ModerationLog> {
    const [newLog] = await db.insert(moderationLogs).values(log).returning();
    return newLog;
  }

  // Analytics operations (simplified for now)
  async getAnalyticsOverview(): Promise<any> {
    return {
      totalServers: 18,
      totalUsers: 949,
      totalMessages: 0,
      totalCommands: 0,
      activeUsers: 0,
      topChannels: [],
      topCommands: []
    };
  }

  async getServerAnalytics(guildId: string, timeRange: string): Promise<any> {
    return { data: [], summary: { totalMembers: 0, peakOnline: 0, avgMessages: 0 } };
  }

  async getMessageAnalytics(guildId: string, timeRange: string): Promise<any> {
    return {
      hourlyData: [],
      channelBreakdown: [],
      totalMessages: 0,
      averagePerHour: 0
    };
  }

  async getCommandAnalytics(guildId: string, timeRange: string): Promise<any> {
    return {
      topCommands: [],
      categoryBreakdown: [],
      totalCommands: 0,
      successRate: 100
    };
  }

  async getUserActivity(guildId: string): Promise<any> {
    return {
      topUsers: [],
      activityTrends: [],
      totalActiveUsers: 0,
      newJoinsToday: 0,
      leavesToday: 0
    };
  }

  async getChannelAnalytics(guildId: string): Promise<any> {
    try {
      const channels = await db
        .select()
        .from(channelAnalytics)
        .where(eq(channelAnalytics.guildId, guildId))
        .orderBy(desc(channelAnalytics.messageCount));
    
    // Separate text and voice channels
    const textChannels = channels
      .filter(channel => channel.channelType === 'text')
      .map(channel => ({
        id: channel.channelId,
        name: channel.channelName,
        messageCount: channel.messageCount,
        activeUsers: channel.activeUsers,
        lastActivity: channel.lastActivity,
        activityScore: this.calculateActivityScore(channel)
      }));
    
    const voiceChannels = channels
      .filter(channel => channel.channelType === 'voice')
      .map(channel => ({
        id: channel.channelId,
        name: channel.channelName,
        activeUsers: channel.activeUsers,
        lastActivity: channel.lastActivity,
        activityScore: this.calculateActivityScore(channel)
      }));
    
    // Find most and least active channels
    const mostActiveChannel = channels.reduce((prev, current) => 
      (current.messageCount || 0) > (prev.messageCount || 0) ? current : prev
    , channels[0] || { channelName: 'N/A' });
    
    const quietestChannel = channels.reduce((prev, current) => 
      (current.messageCount || 0) < (prev.messageCount || 0) ? current : prev
    , channels[channels.length - 1] || { channelName: 'N/A' });
    
    // Calculate summary statistics
    const totalMessages = channels.reduce((sum, channel) => sum + (channel.messageCount || 0), 0);
    const totalActiveUsers = channels.reduce((sum, channel) => sum + (channel.activeUsers || 0), 0);
    const avgMessagesPerChannel = channels.length > 0 ? Math.round(totalMessages / channels.length) : 0;
    
      return {
        textChannels,
        voiceChannels,
        mostActiveChannel: mostActiveChannel.channelName,
        quietestChannel: quietestChannel.channelName,
        summary: {
          totalChannels: channels.length,
          totalMessages,
          totalActiveUsers,
          avgMessagesPerChannel,
          textChannelCount: textChannels.length,
          voiceChannelCount: voiceChannels.length
        }
      };
    } catch (error) {
      console.error(`Failed to fetch channel analytics for guild ${guildId}:`, error);
      return {
        textChannels: [],
        voiceChannels: [],
        mostActiveChannel: 'N/A',
        quietestChannel: 'N/A',
        summary: {
          totalChannels: 0,
          totalMessages: 0,
          totalActiveUsers: 0,
          avgMessagesPerChannel: 0,
          textChannelCount: 0,
          voiceChannelCount: 0
        }
      };
    }
  }

  private calculateActivityScore(channel: any): number {
    const messageWeight = 0.6;
    const userWeight = 0.3;
    const recentActivityWeight = 0.1;
    
    const messages = channel.messageCount || 0;
    const users = channel.activeUsers || 0;
    const daysSinceActivity = channel.lastActivity 
      ? Math.max(0, Math.min(30, (Date.now() - new Date(channel.lastActivity).getTime()) / (1000 * 60 * 60 * 24)))
      : 30;
    
    const recentActivityScore = Math.max(0, 100 - (daysSinceActivity * 3.33)); // 0-100 scale
    
    return Math.round(
      (messages * messageWeight) + 
      (users * userWeight * 10) + 
      (recentActivityScore * recentActivityWeight)
    );
  }
}

export const storage = new DatabaseStorage();