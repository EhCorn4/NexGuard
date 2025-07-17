import { pgTable, text, serial, integer, timestamp, boolean } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const newsUpdates = pgTable("news_updates", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  content: text("content").notNull(),
  category: text("category").notNull(),
  publishedAt: timestamp("published_at").notNull(),
  likes: integer("likes").default(0),
  comments: integer("comments").default(0),
});

export const developers = pgTable("developers", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  role: text("role").notNull(),
  bio: text("bio").notNull(),
  githubUrl: text("github_url"),
  twitterUrl: text("twitter_url"),
  linkedinUrl: text("linkedin_url"),
  location: text("location"),
  experience: text("experience"),
  skills: text("skills").array(),
  specialties: text("specialties").array(),
  achievements: text("achievements").array(),
  projects: text("projects").array(),
  education: text("education"),
  email: text("email"),
  discord: text("discord"),
  website: text("website"),
  yearsOfExperience: integer("years_of_experience"),
});

export const features = pgTable("features", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  icon: text("icon").notNull(),
  benefits: text("benefits").array(),
});

export const testimonials = pgTable("testimonials", {
  id: serial("id").primaryKey(),
  username: text("username").notNull(),
  serverName: text("server_name").notNull(),
  content: text("content").notNull(),
  rating: integer("rating").notNull(), // 1-5 stars
  isApproved: boolean("is_approved").default(false).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const feedback = pgTable("feedback", {
  id: serial("id").primaryKey(),
  username: text("username").notNull(),
  email: text("email").notNull(),
  subject: text("subject").notNull(),
  message: text("message").notNull(),
  type: text("type").notNull(), // "bug", "feature", "general"
  status: text("status").default("pending").notNull(), // "pending", "reviewed", "resolved"
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const serverConfigs = pgTable("server_configs", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull().unique(),
  guildName: text("guild_name").notNull(),
  ownerId: text("owner_id").notNull(),
  
  // Moderation Settings
  moderationEnabled: boolean("moderation_enabled").default(true),
  autoModEnabled: boolean("auto_mod_enabled").default(true),
  spamProtection: boolean("spam_protection").default(true),
  linkProtection: boolean("link_protection").default(false),
  profanityFilter: boolean("profanity_filter").default(true),
  
  // Advanced Moderation Settings
  maxWarnings: integer("max_warnings").default(3),
  warningExpireDays: integer("warning_expire_days").default(30),
  antiRaidEnabled: boolean("anti_raid_enabled").default(true),
  massJoinThreshold: integer("mass_join_threshold").default(5),
  slowmodeEnabled: boolean("slowmode_enabled").default(false),
  slowmodeSeconds: integer("slowmode_seconds").default(5),
  capsFilter: boolean("caps_filter").default(false),
  capsThreshold: integer("caps_threshold").default(70),
  duplicateMessageFilter: boolean("duplicate_message_filter").default(true),
  mentionSpamFilter: boolean("mention_spam_filter").default(true),
  maxMentions: integer("max_mentions").default(5),
  wordFilter: boolean("word_filter").default(true),
  wordFilterList: text("word_filter_list").array(),
  
  // Punishment Settings
  warnAction: text("warn_action").default("warn"), // "warn", "mute", "kick", "ban"
  muteAction: text("mute_action").default("mute"), // "mute", "kick", "ban"
  kickAction: text("kick_action").default("kick"), // "kick", "ban"
  banAction: text("ban_action").default("ban"), // "ban", "tempban"
  tempbanDuration: integer("tempban_duration").default(24), // hours
  
  // Automod Thresholds
  spamMessageCount: integer("spam_message_count").default(5),
  spamTimeWindow: integer("spam_time_window").default(10), // seconds
  raidJoinTimeWindow: integer("raid_join_time_window").default(60), // seconds
  
  // Logging Settings
  modLogChannel: text("mod_log_channel"),
  auditLogChannel: text("audit_log_channel"),
  
  // Welcome/Leave Settings
  welcomeEnabled: boolean("welcome_enabled").default(false),
  welcomeChannel: text("welcome_channel"),
  welcomeMessage: text("welcome_message"),
  leaveEnabled: boolean("leave_enabled").default(false),
  leaveChannel: text("leave_channel"),
  leaveMessage: text("leave_message"),
  
  // Role Settings
  autoRoleEnabled: boolean("auto_role_enabled").default(false),
  autoRoleId: text("auto_role_id"),
  mutedRoleId: text("muted_role_id"),
  
  // Economy Settings
  economyEnabled: boolean("economy_enabled").default(false),
  dailyReward: integer("daily_reward").default(100),
  
  // Custom Commands
  customCommandsEnabled: boolean("custom_commands_enabled").default(true),
  maxCustomCommands: integer("max_custom_commands").default(10),
  
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const customCommands = pgTable("custom_commands", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  name: text("name").notNull(),
  response: text("response").notNull(),
  createdBy: text("created_by").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertNewsUpdateSchema = createInsertSchema(newsUpdates).omit({
  id: true,
  likes: true,
  comments: true,
});

export const insertDeveloperSchema = createInsertSchema(developers).omit({
  id: true,
});

export const insertFeatureSchema = createInsertSchema(features).omit({
  id: true,
});

export const insertTestimonialSchema = createInsertSchema(testimonials).omit({
  id: true,
  isApproved: true,
  createdAt: true,
});

export const insertFeedbackSchema = createInsertSchema(feedback).omit({
  id: true,
  status: true,
  createdAt: true,
});

export const insertServerConfigSchema = createInsertSchema(serverConfigs).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const insertCustomCommandSchema = createInsertSchema(customCommands).omit({
  id: true,
  createdAt: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
export type NewsUpdate = typeof newsUpdates.$inferSelect;
export type Developer = typeof developers.$inferSelect;
export type Feature = typeof features.$inferSelect;
export type Testimonial = typeof testimonials.$inferSelect;
export type Feedback = typeof feedback.$inferSelect;
export type ServerConfig = typeof serverConfigs.$inferSelect;
export type CustomCommand = typeof customCommands.$inferSelect;
export type InsertNewsUpdate = z.infer<typeof insertNewsUpdateSchema>;
export type InsertDeveloper = z.infer<typeof insertDeveloperSchema>;
export type InsertFeature = z.infer<typeof insertFeatureSchema>;
export type InsertTestimonial = z.infer<typeof insertTestimonialSchema>;
export type InsertFeedback = z.infer<typeof insertFeedbackSchema>;
export type InsertServerConfig = z.infer<typeof insertServerConfigSchema>;
export type InsertCustomCommand = z.infer<typeof insertCustomCommandSchema>;
