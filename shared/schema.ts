import { pgTable, text, serial, integer, timestamp, boolean, unique } from "drizzle-orm/pg-core";
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

// Analytics tables
export const serverAnalytics = pgTable("server_analytics", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  timestamp: timestamp("timestamp").defaultNow().notNull(),
  memberCount: integer("member_count").default(0),
  onlineMembers: integer("online_members").default(0),
  messagesPerHour: integer("messages_per_hour").default(0),
  commandsExecuted: integer("commands_executed").default(0),
  newJoins: integer("new_joins").default(0),
  newLeaves: integer("new_leaves").default(0),
  voiceMembers: integer("voice_members").default(0),
});

export const messageAnalytics = pgTable("message_analytics", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  channelId: text("channel_id").notNull(),
  userId: text("user_id").notNull(),
  messageCount: integer("message_count").default(1),
  timestamp: timestamp("timestamp").defaultNow().notNull(),
  hour: integer("hour").notNull(), // 0-23 for hourly grouping
});

export const commandAnalytics = pgTable("command_analytics", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  commandName: text("command_name").notNull(),
  userId: text("user_id").notNull(),
  timestamp: timestamp("timestamp").defaultNow().notNull(),
  success: boolean("success").default(true),
});

export const userActivity = pgTable("user_activity", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  userId: text("user_id").notNull(),
  username: text("username").notNull(),
  lastActive: timestamp("last_active").defaultNow().notNull(),
  messageCount: integer("message_count").default(0),
  commandCount: integer("command_count").default(0),
  voiceMinutes: integer("voice_minutes").default(0),
});

export const channelAnalytics = pgTable("channel_analytics", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  channelId: text("channel_id").notNull(),
  channelName: text("channel_name").notNull(),
  channelType: text("channel_type").notNull(), // text, voice, category
  messageCount: integer("message_count").default(0),
  activeUsers: integer("active_users").default(0),
  lastActivity: timestamp("last_activity").defaultNow().notNull(),
});

// Bot-related tables
export const guilds = pgTable("guilds", {
  id: text("id").primaryKey(), // Discord guild ID
  name: text("name").notNull(),
  memberCount: integer("member_count").default(0),
  prefix: text("prefix").default("!").notNull(),
  moderationEnabled: boolean("moderation_enabled").default(true).notNull(),
  ticketEnabled: boolean("ticket_enabled").default(true).notNull(),
  adminRoleId: text("admin_role_id"),
  moderatorRoleId: text("moderator_role_id"),
  muteRoleId: text("mute_role_id"),
  logChannelId: text("log_channel_id"),
  errorLogChannelId: text("error_log_channel_id"),
  errorLoggingEnabled: boolean("error_logging_enabled").default(false).notNull(),
  welcomeChannelId: text("welcome_channel_id"),
  welcomeEnabled: boolean("welcome_enabled").default(false).notNull(),
  welcomeMessage: text("welcome_message").default("Welcome to {server}, {user}! You are our #{member_count} member."),
  welcomeEmbed: boolean("welcome_embed").default(false).notNull(),
  welcomeEmbedTitle: text("welcome_embed_title").default("Welcome to {server}!"),
  welcomeEmbedDescription: text("welcome_embed_description").default("Hello {user}, welcome to **{server}**! We're glad you're here."),
  welcomeEmbedColor: text("welcome_embed_color").default("#00FFFF"),
  welcomeEmbedThumbnail: boolean("welcome_embed_thumbnail").default(true).notNull(),
  welcomeEmbedFooter: text("welcome_embed_footer").default("Member #{member_count}"),
  joinedAt: timestamp("joined_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const commands = pgTable("commands", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description").notNull(),
  category: text("category").notNull(), // "admin", "moderation", "ticket", "utility"
  usage: text("usage").notNull(),
  permissions: text("permissions").array().default([]).notNull(),
  enabled: boolean("enabled").default(true).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const ticketCategories = pgTable("ticket_categories", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  categoryName: text("category_name").notNull(),
  categoryId: text("category_id").notNull(), // Discord category ID
  description: text("description"),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const tickets = pgTable("tickets", {
  id: serial("id").primaryKey(),
  ticketId: text("ticket_id").notNull().unique(), // Custom ticket ID like "TICKET-001"
  guildId: text("guild_id").notNull(),
  channelId: text("channel_id").notNull(),
  discordCategoryId: text("discord_category_id"), // Discord category ID where ticket was created
  userId: text("user_id").notNull(),
  username: text("username").notNull(),
  subject: text("subject").notNull(),
  description: text("description"), // Detailed description of the issue
  category: text("category").notNull(), // "general", "bug", "feature", "billing", "technical"
  status: text("status").default("open").notNull(), // "open", "claimed", "in-progress", "pending", "resolved", "closed"
  priority: text("priority").default("medium").notNull(), // "low", "medium", "high", "urgent", "critical"
  assignedTo: text("assigned_to"),
  assignedBy: text("assigned_by"),
  claimedBy: text("claimed_by"), // Staff member who claimed the ticket
  claimedAt: timestamp("claimed_at"), // When ticket was claimed
  panelId: text("panel_id"), // Which panel was used to create this ticket
  formResponses: text("form_responses"), // JSON string of form responses
  transcriptUrl: text("transcript_url"), // URL to transcript after closing
  closeReason: text("close_reason"), // Reason for closing
  closedBy: text("closed_by"), // Who closed the ticket
  feedbackAt: timestamp("feedback_at"), // When user provided feedback
  tags: text("tags").array().default([]), // Custom tags for organization
  slaDeadline: timestamp("sla_deadline"), // SLA deadline for response/resolution
  firstResponseAt: timestamp("first_response_at"), // When staff first responded
  resolvedAt: timestamp("resolved_at"), // When marked as resolved
  satisfaction: integer("satisfaction"), // 1-5 rating from user
  satisfactionComment: text("satisfaction_comment"), // User feedback
  escalationLevel: integer("escalation_level").default(0), // 0=normal, 1=escalated, 2=manager, 3=director
  isArchived: boolean("is_archived").default(false).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  closedAt: timestamp("closed_at"),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// Ticket Panels - TicketsBot.net style reaction panels
export const ticketPanels = pgTable("ticket_panels", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  panelId: text("panel_id").notNull(), // Unique panel identifier
  title: text("title").notNull(),
  description: text("description"),
  emoji: text("emoji"), // Button emoji
  categoryId: text("category_id"), // Discord category to create tickets in
  supportTeamIds: text("support_team_ids"), // JSON array of role IDs that handle this panel
  welcomeMessage: text("welcome_message").default("Thank you for creating a ticket. Our team will assist you shortly."),
  hasForm: boolean("has_form").default(false), // Whether this panel has a form
  formQuestions: text("form_questions"), // JSON array of form questions
  isActive: boolean("is_active").default(true).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// Ticket Transcripts - Auto-saved conversation history
export const ticketTranscripts = pgTable("ticket_transcripts", {
  id: serial("id").primaryKey(),
  ticketId: text("ticket_id").notNull(),
  guildId: text("guild_id").notNull(),
  transcriptData: text("transcript_data").notNull(), // JSON string of all messages
  messageCount: integer("message_count").default(0),
  participantCount: integer("participant_count").default(0),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Support Teams - Different teams for different ticket types
export const supportTeams = pgTable("support_teams", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  teamName: text("team_name").notNull(),
  description: text("description"),
  roleIds: text("role_ids").notNull(), // JSON array of Discord role IDs
  permissions: text("permissions").default("[]"), // JSON array of permissions
  isActive: boolean("is_active").default(true).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const ticketNotes = pgTable("ticket_notes", {
  id: serial("id").primaryKey(),
  ticketId: text("ticket_id").notNull(),
  guildId: text("guild_id").notNull(),
  authorId: text("author_id").notNull(),
  authorName: text("author_name").notNull(),
  content: text("content").notNull(),
  isInternal: boolean("is_internal").default(false).notNull(), // Internal staff notes vs public messages
  noteType: text("note_type").default("message").notNull(), // "message", "status_change", "assignment", "escalation"
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const ticketTemplates = pgTable("ticket_templates", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  name: text("name").notNull(),
  category: text("category").notNull(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  priority: text("priority").default("medium").notNull(),
  autoAssignTo: text("auto_assign_to"), // Auto-assign to specific staff member
  tags: text("tags").array().default([]),
  isActive: boolean("is_active").default(true).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const moderationLogs = pgTable("moderation_logs", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  userId: text("user_id").notNull(),
  moderatorId: text("moderator_id").notNull(),
  action: text("action").notNull(), // "warn", "mute", "kick", "ban", "timeout"
  reason: text("reason"),
  duration: text("duration"), // For temporary actions
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const banList = pgTable("ban_list", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  userId: text("user_id").notNull(),
  username: text("username").notNull(),
  moderatorId: text("moderator_id").notNull(),
  moderatorName: text("moderator_name").notNull(),
  reason: text("reason"),
  banType: text("ban_type").default("permanent").notNull(), // "permanent", "temporary"
  duration: text("duration"), // For temporary bans
  expiresAt: timestamp("expires_at"), // When temporary ban expires
  isActive: boolean("is_active").default(true).notNull(),
  appealable: boolean("appealable").default(true).notNull(),
  appealReason: text("appeal_reason"),
  appealedAt: timestamp("appealed_at"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const warnHistory = pgTable("warn_history", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  userId: text("user_id").notNull(),
  username: text("username").notNull(),
  moderatorId: text("moderator_id").notNull(),
  moderatorName: text("moderator_name").notNull(),
  reason: text("reason").notNull(),
  severity: text("severity").default("medium").notNull(), // "low", "medium", "high", "severe"
  points: integer("points").default(1).notNull(), // Warning points system
  isActive: boolean("is_active").default(true).notNull(),
  expiresAt: timestamp("expires_at"), // When warning expires
  acknowledgedAt: timestamp("acknowledged_at"), // When user acknowledged
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const changelogs = pgTable("changelogs", {
  id: serial("id").primaryKey(),
  version: text("version").notNull().unique(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  changes: text("changes").array().notNull(),
  type: text("type").notNull(), // "major", "minor", "patch", "hotfix"
  releaseDate: timestamp("release_date").defaultNow().notNull(),
  isPublished: boolean("is_published").default(false).notNull(),
});

export const autoReplies = pgTable("auto_replies", {
  id: serial("id").primaryKey(),
  guildId: text("guild_id").notNull(),
  trigger: text("trigger").notNull(),
  response: text("response").notNull(),
  isActive: boolean("is_active").default(true).notNull(),
  createdBy: text("created_by").notNull(), // User ID who created the auto-reply
  createdByName: text("created_by_name").notNull(),
  triggerType: text("trigger_type").default("contains").notNull(), // "contains", "exact", "starts_with", "ends_with"
  caseSensitive: boolean("case_sensitive").default(false).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const botStatus = pgTable("bot_status", {
  id: serial("id").primaryKey(),
  isOnline: boolean("is_online").default(false).notNull(),
  guildsCount: integer("guilds_count").default(0),
  usersCount: integer("users_count").default(0),
  uptime: text("uptime").default("0").notNull(),
  lastRestart: timestamp("last_restart").defaultNow().notNull(),
  version: text("version").default("1.0.0").notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// Insert schemas
export const insertUserSchema = createInsertSchema(users);
export const insertNewsUpdateSchema = createInsertSchema(newsUpdates);
export const insertDeveloperSchema = createInsertSchema(developers);
export const insertFeatureSchema = createInsertSchema(features);
export const insertTestimonialSchema = createInsertSchema(testimonials);
export const insertFeedbackSchema = createInsertSchema(feedback);
export const insertGuildSchema = createInsertSchema(guilds);
export const insertCommandSchema = createInsertSchema(commands);
export const insertTicketSchema = createInsertSchema(tickets);
export const insertTicketNoteSchema = createInsertSchema(ticketNotes);
export const insertTicketTemplateSchema = createInsertSchema(ticketTemplates);
export const insertTicketPanelSchema = createInsertSchema(ticketPanels);
export const insertTicketTranscriptSchema = createInsertSchema(ticketTranscripts);
export const insertSupportTeamSchema = createInsertSchema(supportTeams);
export const insertModerationLogSchema = createInsertSchema(moderationLogs);
export const insertBanListSchema = createInsertSchema(banList);
export const insertWarnHistorySchema = createInsertSchema(warnHistory);
export const insertChangelogSchema = createInsertSchema(changelogs);
export const insertBotStatusSchema = createInsertSchema(botStatus);
export const insertServerAnalyticsSchema = createInsertSchema(serverAnalytics);
export const insertMessageAnalyticsSchema = createInsertSchema(messageAnalytics);
export const insertCommandAnalyticsSchema = createInsertSchema(commandAnalytics);
export const insertUserActivitySchema = createInsertSchema(userActivity);
export const insertChannelAnalyticsSchema = createInsertSchema(channelAnalytics);

// Select types
export type User = typeof users.$inferSelect;
export type NewsUpdate = typeof newsUpdates.$inferSelect;
export type Developer = typeof developers.$inferSelect;
export type Feature = typeof features.$inferSelect;
export type Testimonial = typeof testimonials.$inferSelect;
export type Feedback = typeof feedback.$inferSelect;
export type Guild = typeof guilds.$inferSelect;
export type Command = typeof commands.$inferSelect;
export type Ticket = typeof tickets.$inferSelect;
export type TicketNote = typeof ticketNotes.$inferSelect;
export type TicketTemplate = typeof ticketTemplates.$inferSelect;
export type TicketPanel = typeof ticketPanels.$inferSelect;
export type TicketTranscript = typeof ticketTranscripts.$inferSelect;
export type SupportTeam = typeof supportTeams.$inferSelect;
export type ModerationLog = typeof moderationLogs.$inferSelect;
export type BanList = typeof banList.$inferSelect;
export type WarnHistory = typeof warnHistory.$inferSelect;
export type Changelog = typeof changelogs.$inferSelect;
export type BotStatus = typeof botStatus.$inferSelect;
export type ServerAnalytics = typeof serverAnalytics.$inferSelect;
export type MessageAnalytics = typeof messageAnalytics.$inferSelect;
export type CommandAnalytics = typeof commandAnalytics.$inferSelect;
export type UserActivity = typeof userActivity.$inferSelect;
export type ChannelAnalytics = typeof channelAnalytics.$inferSelect;

// Insert types
export type InsertUser = z.infer<typeof insertUserSchema>;
export type InsertNewsUpdate = z.infer<typeof insertNewsUpdateSchema>;
export type InsertDeveloper = z.infer<typeof insertDeveloperSchema>;
export type InsertFeature = z.infer<typeof insertFeatureSchema>;
export type InsertTestimonial = z.infer<typeof insertTestimonialSchema>;
export type InsertFeedback = z.infer<typeof insertFeedbackSchema>;
export type InsertGuild = z.infer<typeof insertGuildSchema>;
export type InsertCommand = z.infer<typeof insertCommandSchema>;
export type InsertTicket = z.infer<typeof insertTicketSchema>;
export type InsertModerationLog = z.infer<typeof insertModerationLogSchema>;
export type InsertChangelog = z.infer<typeof insertChangelogSchema>;
export type InsertBotStatus = z.infer<typeof insertBotStatusSchema>;