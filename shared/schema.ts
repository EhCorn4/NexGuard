import { pgTable, text, serial, integer, timestamp } from "drizzle-orm/pg-core";
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
});

export const features = pgTable("features", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  icon: text("icon").notNull(),
  benefits: text("benefits").array(),
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

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
export type NewsUpdate = typeof newsUpdates.$inferSelect;
export type Developer = typeof developers.$inferSelect;
export type Feature = typeof features.$inferSelect;
export type InsertNewsUpdate = z.infer<typeof insertNewsUpdateSchema>;
export type InsertDeveloper = z.infer<typeof insertDeveloperSchema>;
export type InsertFeature = z.infer<typeof insertFeatureSchema>;
