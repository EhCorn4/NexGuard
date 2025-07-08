import { db } from "./db";
import { newsUpdates, developers, features } from "@shared/schema";

async function seedDatabase() {
  console.log("Starting database seeding...");

  try {
    // Clear existing data
    await db.delete(newsUpdates);
    await db.delete(developers);
    await db.delete(features);

    // Insert developers
    await db.insert(developers).values([
      {
        name: "Caleb Weston",
        role: "Lead Developer",
        bio: "3+ years experience in Coding and website development",
        githubUrl: "https://github.com/calebweston",
        twitterUrl: "https://twitter.com/calebweston",
        linkedinUrl: "https://linkedin.com/in/calebweston"
      }
    ]);

    // Insert features
    await db.insert(features).values([
      {
        title: "Advanced Moderation",
        description: "Automated rule enforcement, smart spam detection, and customizable punishment systems to keep your server clean.",
        icon: "gavel",
        benefits: ["Auto-moderation with AI detection", "Customizable warning system", "Raid protection & anti-spam", "Temporary bans & mutes"]
      },
      {
        title: "Server Analytics",
        description: "Comprehensive insights into your server's activity, member engagement, and moderation statistics.",
        icon: "chart-line",
        benefits: ["Member activity tracking", "Detailed moderation logs", "Channel usage statistics", "Growth analytics"]
      },
      {
        title: "Role Management",
        description: "Automated role assignment, reaction roles, and advanced permission management for seamless server organization.",
        icon: "users",
        benefits: ["Reaction role system", "Auto-role assignment", "Permission templates", "Role hierarchy management"]
      },
      {
        title: "Smart Notifications",
        description: "Customizable notification system for server events, moderation actions, and important updates.",
        icon: "bell",
        benefits: ["Welcome & goodbye messages", "Moderation alerts", "Custom event notifications", "Scheduled announcements"]
      },
      {
        title: "Entertainment & Games",
        description: "Engaging mini-games, trivia, and interactive features to keep your community active and entertained.",
        icon: "gamepad",
        benefits: ["Interactive games & trivia", "Economy system", "Leaderboards", "Custom commands"]
      },
      {
        title: "Easy Configuration",
        description: "Intuitive web dashboard and slash commands make setup and management effortless for any server size.",
        icon: "cog",
        benefits: ["Web-based dashboard", "Slash command interface", "One-click setup templates", "Backup & restore settings"]
      }
    ]);

    // Insert news updates
    await db.insert(newsUpdates).values([
      {
        title: "AI-Powered Spam Detection",
        content: "Our new machine learning algorithm can now detect sophisticated spam patterns with 99.2% accuracy, providing better protection for your server.",
        category: "NEW FEATURE",
        publishedAt: new Date("2024-01-15"),
        likes: 127,
        comments: 23
      },
      {
        title: "100K+ Servers Milestone",
        content: "We've reached an incredible milestone! Thank you to all 100,000+ servers and their communities for trusting NexGuard with their moderation needs.",
        category: "COMMUNITY",
        publishedAt: new Date("2024-01-12"),
        likes: 892,
        comments: 156
      },
      {
        title: "Dashboard 2.0 Released",
        content: "Our completely redesigned web dashboard offers a more intuitive experience with advanced analytics and one-click configuration templates.",
        category: "UPDATE",
        publishedAt: new Date("2024-01-10"),
        likes: 324,
        comments: 67
      },
      {
        title: "Enhanced Raid Protection",
        content: "New anti-raid features include IP tracking, join pattern analysis, and automatic lockdown capabilities to protect against coordinated attacks.",
        category: "SECURITY",
        publishedAt: new Date("2024-01-08"),
        likes: 456,
        comments: 89
      },
      {
        title: "New Mini-Games Added",
        content: "Keep your community engaged with our new collection of mini-games including trivia, word games, and interactive challenges.",
        category: "GAMES",
        publishedAt: new Date("2024-01-05"),
        likes: 278,
        comments: 45
      },
      {
        title: "Server of the Month",
        content: "Congratulations to \"TechHub Community\" for being our featured server! Their innovative use of NexGuard's features creates an amazing experience.",
        category: "FEATURED",
        publishedAt: new Date("2024-01-03"),
        likes: 189,
        comments: 34
      }
    ]);

    console.log("Database seeding completed successfully!");
  } catch (error) {
    console.error("Error seeding database:", error);
    throw error;
  }
}

seedDatabase().catch(console.error);