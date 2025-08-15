import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertTestimonialSchema, insertFeedbackSchema } from "@shared/schema";
import fetch from "node-fetch";
import { emailService } from "./lib/emailService";
import fs from "fs";
import path from "path";

// Helper function to generate sample PDF content
function generateSampleGuideContent(title: string, description: string): Buffer {
  // This creates a simple PDF-like content for demonstration
  // In a real implementation, you would use a PDF library like pdfkit or serve actual PDF files
  const content = `%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 200
>>
stream
BT
/F1 12 Tf
50 750 Td
(${title}) Tj
0 -20 Td
(${description}) Tj
0 -40 Td
(This is a sample guide document for NexGuard Discord Bot.) Tj
0 -20 Td
(For the complete guide, please visit https://nexguard.org/docs) Tj
0 -40 Td
(Created: ${new Date().toLocaleDateString()}) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000173 00000 n 
0000000301 00000 n 
0000000380 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
456
%%EOF`;

  return Buffer.from(content, 'utf-8');
}

export function registerRoutes(app: Express): Server {
  // News endpoints
  app.get("/api/news", async (req, res) => {
    try {
      const news = await storage.getNews();
      res.json(news);
    } catch (error) {
      console.error("Error fetching news:", error);
      res.status(500).json({ error: "Failed to fetch news" });
    }
  });

  // Developers endpoints
  app.get("/api/developers", async (req, res) => {
    try {
      const developers = await storage.getDevelopers();
      res.json(developers);
    } catch (error) {
      console.error("Error fetching developers:", error);
      res.status(500).json({ error: "Failed to fetch developers" });
    }
  });

  // Features endpoints
  app.get("/api/features", async (req, res) => {
    try {
      const features = await storage.getFeatures();
      res.json(features);
    } catch (error) {
      console.error("Error fetching features:", error);
      res.status(500).json({ error: "Failed to fetch features" });
    }
  });

  // Testimonials endpoints
  app.get("/api/testimonials", async (req, res) => {
    try {
      const testimonials = await storage.getTestimonials();
      res.json(testimonials);
    } catch (error) {
      console.error("Error fetching testimonials:", error);
      res.status(500).json({ error: "Failed to fetch testimonials" });
    }
  });

  app.post("/api/testimonials", async (req, res) => {
    try {
      const result = insertTestimonialSchema.safeParse(req.body);
      if (!result.success) {
        return res.status(400).json({ error: "Invalid testimonial data" });
      }
      
      const testimonial = await storage.createTestimonial(result.data);
      
      // Send email notification for new testimonial with approval links
      try {
        await emailService.sendTestimonialNotification({
          id: testimonial.id,
          name: testimonial.username,
          serverName: testimonial.serverName,
          rating: testimonial.rating,
          message: testimonial.content,
          approvalLink: `${process.env.REPL_SLUG ? `https://${process.env.REPL_SLUG}.${process.env.REPL_OWNER?.toLowerCase()}.repl.co` : 'http://localhost:5000'}/api/testimonials/approve/${testimonial.id}`,
          rejectLink: `${process.env.REPL_SLUG ? `https://${process.env.REPL_SLUG}.${process.env.REPL_OWNER?.toLowerCase()}.repl.co` : 'http://localhost:5000'}/api/testimonials/reject/${testimonial.id}`
        });
        console.log(`📧 Email notification sent for testimonial from ${testimonial.username} (ID: ${testimonial.id})`);
      } catch (emailError) {
        console.error('Failed to send testimonial email notification:', emailError);
        // Don't fail the request if email fails
      }
      
      res.json({ message: "Testimonial submitted for approval", id: testimonial.id });
    } catch (error) {
      console.error("Error creating testimonial:", error);
      res.status(500).json({ error: "Failed to create testimonial" });
    }
  });

  // Testimonial approval endpoints
  app.get("/api/testimonials/approve/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      if (isNaN(id)) {
        return res.status(400).json({ error: "Invalid testimonial ID" });
      }
      
      const testimonial = await storage.approveTestimonial(id);
      if (!testimonial) {
        return res.status(404).json({ error: "Testimonial not found" });
      }
      
      res.send(`
        <html>
          <head><title>Testimonial Approved</title></head>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px;">
            <div style="text-align: center; background: linear-gradient(135deg, #06b6d4, #8b5cf6); color: white; padding: 20px; border-radius: 10px;">
              <h1>✅ Testimonial Approved!</h1>
              <p>The testimonial from <strong>${testimonial.username}</strong> has been approved and is now live on the NexGuard website.</p>
              <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Server:</strong> ${testimonial.serverName}</p>
                <p><strong>Rating:</strong> ${'⭐'.repeat(testimonial.rating)}</p>
                <p><strong>Message:</strong> "${testimonial.content}"</p>
              </div>
              <a href="/" style="display: inline-block; background: white; color: #06b6d4; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px;">View Website</a>
            </div>
          </body>
        </html>
      `);
    } catch (error) {
      console.error("Error approving testimonial:", error);
      res.status(500).json({ error: "Failed to approve testimonial" });
    }
  });

  app.get("/api/testimonials/reject/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      if (isNaN(id)) {
        return res.status(400).json({ error: "Invalid testimonial ID" });
      }
      
      const success = await storage.rejectTestimonial(id);
      if (!success) {
        return res.status(404).json({ error: "Testimonial not found" });
      }
      
      res.send(`
        <html>
          <head><title>Testimonial Rejected</title></head>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px;">
            <div style="text-align: center; background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 20px; border-radius: 10px;">
              <h1>❌ Testimonial Rejected</h1>
              <p>The testimonial has been rejected and removed from the system.</p>
              <a href="/" style="display: inline-block; background: white; color: #ef4444; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px;">Return to Website</a>
            </div>
          </body>
        </html>
      `);
    } catch (error) {
      console.error("Error rejecting testimonial:", error);
      res.status(500).json({ error: "Failed to reject testimonial" });
    }
  });

  // Feedback endpoints
  app.get("/api/feedback", async (req, res) => {
    try {
      const feedback = await storage.getFeedback();
      res.json(feedback);
    } catch (error) {
      console.error("Error fetching feedback:", error);
      res.status(500).json({ error: "Failed to fetch feedback" });
    }
  });

  app.post("/api/feedback", async (req, res) => {
    try {
      const result = insertFeedbackSchema.safeParse(req.body);
      if (!result.success) {
        return res.status(400).json({ error: "Invalid feedback data" });
      }
      
      // Store feedback locally
      const feedback = await storage.createFeedback(result.data);
      
      // Send email notification for new feedback
      try {
        await emailService.sendFeedbackNotification({
          name: feedback.username,
          email: feedback.email || undefined,
          type: feedback.type,
          message: feedback.message
        });
        console.log(`📧 Email notification sent for feedback from ${feedback.username}`);
      } catch (emailError) {
        console.error('Failed to send feedback email notification:', emailError);
        // Don't fail the request if email fails
      }
      
      // Send feedback to NexGuard website
      const feedbackData = {
        id: feedback.id,
        username: feedback.username,
        email: feedback.email,
        subject: feedback.subject,
        message: feedback.message,
        type: feedback.type,
        status: feedback.status,
        submittedAt: feedback.createdAt,
        source: "website",
        userAgent: req.headers['user-agent'] || 'Unknown',
        timestamp: new Date().toISOString()
      };

      // Send to NexGuard central website (with error handling)
      let externalSubmissionStatus = "pending";
      try {
        // Create AbortController for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

        const nexguardResponse = await fetch('https://nexguard.org/api/feedback/submit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${process.env.NEXGUARD_API_KEY || 'dev-key'}`,
            'User-Agent': 'NexGuard-Bot-Website/2.3.2',
            'X-Source': 'discord-bot-website',
            'X-Bot-Version': '2.3.2'
          },
          body: JSON.stringify(feedbackData),
          signal: controller.signal
        } as any);

        clearTimeout(timeoutId);

        if (nexguardResponse.ok) {
          const nexguardResult = await nexguardResponse.json() as any;
          externalSubmissionStatus = "submitted";
          console.log(`✅ Feedback #${feedback.id} forwarded to NexGuard website:`, nexguardResult.id || 'success');
        } else {
          console.warn(`⚠️  Failed to forward feedback #${feedback.id} to NexGuard website:`, nexguardResponse.status);
          externalSubmissionStatus = "failed";
        }
      } catch (externalError: any) {
        console.warn(`⚠️  Network error forwarding feedback #${feedback.id} to NexGuard website:`, externalError.message);
        externalSubmissionStatus = "failed";
      }

      // Return success with submission status
      res.json({
        ...feedback,
        externalSubmissionStatus,
        message: externalSubmissionStatus === "submitted" 
          ? "Feedback submitted successfully to NexGuard website" 
          : "Feedback saved locally. External submission pending."
      });
    } catch (error) {
      console.error("Error creating feedback:", error);
      res.status(500).json({ error: "Failed to create feedback" });
    }
  });

  // Health check endpoints
  app.get("/health", (req, res) => {
    res.json({ status: "ok", timestamp: new Date().toISOString() });
  });

  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", timestamp: new Date().toISOString() });
  });

  // Configuration endpoint for frontend
  app.get("/api/config", (req, res) => {
    res.json({
      platform: "discord",
      status: "active",
      version: "2.3.2",
      discordInviteUrl: "https://discord.com/oauth2/authorize?client_id=1389775821794705429&permissions=8&scope=bot%20applications.commands",
      supportServerUrl: "https://discord.gg/wpjZMPXaRT"
    });
  });

  // Bot status endpoints
  app.get("/api/bot/status", async (req, res) => {
    try {
      const status = await storage.getBotStatus();
      res.json(status);
    } catch (error) {
      console.error("Error fetching bot status:", error);
      res.status(500).json({ error: "Failed to fetch bot status" });
    }
  });

  // Webhook endpoint for sending messages through the bot
  app.post("/webhook/send", async (req, res) => {
    try {
      const { channel_id, content, embed, api_key } = req.body;

      // Simple API key check (you can set WEBHOOK_API_KEY in your environment)
      const validApiKey = process.env.WEBHOOK_API_KEY || "nexguard-fun-webhook";
      if (!api_key || api_key !== validApiKey) {
        return res.status(401).json({ error: "Invalid API key", hint: "Set api_key parameter" });
      }

      if (!channel_id) {
        return res.status(400).json({ error: "channel_id is required" });
      }

      if (!content && !embed) {
        return res.status(400).json({ error: "Either content or embed is required" });
      }

      // Send message data to bot
      const messageData = {
        channel_id: channel_id,
        content: content,
        embed: embed
      };

      try {
        // Send to bot's internal webhook server
        const botResponse = await fetch('http://localhost:5001/api/bot/send-message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(messageData)
        });

        if (botResponse.ok) {
          const result = await botResponse.json();
          res.json({
            success: true,
            message: "Message sent successfully",
            data: result
          });
        } else {
          const error = await botResponse.text();
          res.status(500).json({
            error: "Bot delivery failed",
            details: error,
            message: "The webhook endpoint received your request but the bot couldn't deliver it"
          });
        }
      } catch (botError: any) {
        // Bot might not be running, return a helpful message
        console.log("🎭 Webhook message request (bot offline):", messageData);
        res.json({
          success: false,
          message: "Message received but bot is offline",
          preview: content || embed?.description || "Embed message",
          note: "Your message was processed but couldn't be delivered because NexGuard bot is not currently running"
        });
      }

    } catch (error) {
      console.error("Webhook error:", error);
      res.status(500).json({ error: "Internal server error" });
    }
  });

  app.get("/api/bot/commands", async (req, res) => {
    try {
      const commands = await storage.getCommands();
      res.json(commands);
    } catch (error) {
      console.error("Error fetching commands:", error);
      res.status(500).json({ error: "Failed to fetch commands" });
    }
  });

  app.get("/api/bot/changelog", async (req, res) => {
    try {
      const changelog = await storage.getChangelogs();
      res.json(changelog);
    } catch (error) {
      console.error("Error fetching changelog:", error);
      res.status(500).json({ error: "Failed to fetch changelog" });
    }
  });

  app.get("/api/bot/tickets", async (req, res) => {
    try {
      const tickets = await storage.getTickets();
      res.json(tickets);
    } catch (error) {
      console.error("Error fetching tickets:", error);
      res.status(500).json({ error: "Failed to fetch tickets" });
    }
  });

  app.get("/api/bot/moderation", async (req, res) => {
    try {
      const logs = await storage.getModerationLogs();
      res.json(logs);
    } catch (error) {
      console.error("Error fetching moderation logs:", error);
      res.status(500).json({ error: "Failed to fetch moderation logs" });
    }
  });

  // Analytics endpoints
  app.get("/api/analytics/overview", async (req, res) => {
    try {
      const analytics = await storage.getAnalyticsOverview();
      res.json(analytics);
    } catch (error) {
      console.error("Error fetching analytics overview:", error);
      res.status(500).json({ error: "Failed to fetch analytics overview" });
    }
  });

  app.get("/api/analytics/server/:guildId", async (req, res) => {
    try {
      const { guildId } = req.params;
      const { timeRange = "24h" } = req.query;
      const analytics = await storage.getServerAnalytics(guildId, timeRange as string);
      res.json(analytics);
    } catch (error) {
      console.error("Error fetching server analytics:", error);
      res.status(500).json({ error: "Failed to fetch server analytics" });
    }
  });

  app.get("/api/analytics/messages/:guildId", async (req, res) => {
    try {
      const { guildId } = req.params;
      const { timeRange = "24h" } = req.query;
      const analytics = await storage.getMessageAnalytics(guildId, timeRange as string);
      res.json(analytics);
    } catch (error) {
      console.error("Error fetching message analytics:", error);
      res.status(500).json({ error: "Failed to fetch message analytics" });
    }
  });

  app.get("/api/analytics/commands/:guildId", async (req, res) => {
    try {
      const { guildId } = req.params;
      const { timeRange = "24h" } = req.query;
      const analytics = await storage.getCommandAnalytics(guildId, timeRange as string);
      res.json(analytics);
    } catch (error) {
      console.error("Error fetching command analytics:", error);
      res.status(500).json({ error: "Failed to fetch command analytics" });
    }
  });

  app.get("/api/analytics/users/:guildId", async (req, res) => {
    try {
      const { guildId } = req.params;
      const analytics = await storage.getUserActivity(guildId);
      res.json(analytics);
    } catch (error) {
      console.error("Error fetching user activity:", error);
      res.status(500).json({ error: "Failed to fetch user activity" });
    }
  });

  app.get("/api/analytics/channels/:guildId", async (req, res) => {
    try {
      const { guildId } = req.params;
      const analytics = await storage.getChannelAnalytics(guildId);
      res.json(analytics);
    } catch (error) {
      console.error("Error fetching channel analytics:", error);
      res.status(500).json({ error: "Failed to fetch channel analytics" });
    }
  });

  // Guide download endpoints
  app.get("/api/guides/download/:guideType", async (req, res) => {
    try {
      const { guideType } = req.params;
      
      // Define available guides with their metadata
      const guides = {
        quickstart: {
          filename: "NexGuard_Quick_Start_Guide.pdf",
          title: "NexGuard Quick Start Guide",
          description: "Essential setup steps for new users"
        },
        automod: {
          filename: "NexGuard_AutoMod_Setup_Guide.pdf", 
          title: "AutoMod Setup Guide",
          description: "Configure advanced automated moderation"
        },
        tickets: {
          filename: "NexGuard_Ticket_System_Guide.pdf",
          title: "Ticket System Guide", 
          description: "Professional support ticket configuration"
        },
        analytics: {
          filename: "NexGuard_Analytics_Logging_Guide.pdf",
          title: "Analytics & Logging Guide",
          description: "Server statistics and event logging setup"
        },
        roles: {
          filename: "NexGuard_Role_Management_Guide.pdf",
          title: "Role Management Guide",
          description: "Configure reaction roles and permissions"
        },
        complete: {
          filename: "NexGuard_Complete_Admin_Guide.pdf",
          title: "Complete Admin Guide",
          description: "Comprehensive guide covering all features"
        }
      };

      const guide = guides[guideType as keyof typeof guides];
      if (!guide) {
        return res.status(404).json({ error: "Guide not found" });
      }

      // For now, generate a sample PDF content
      // In a real implementation, you would serve actual PDF files
      const pdfContent = generateSampleGuideContent(guide.title, guide.description);
      
      res.setHeader('Content-Type', 'application/pdf');
      res.setHeader('Content-Disposition', `attachment; filename="${guide.filename}"`);
      res.setHeader('Content-Length', Buffer.byteLength(pdfContent));
      
      res.send(pdfContent);
      
    } catch (error) {
      console.error("Error serving guide:", error);
      res.status(500).json({ error: "Failed to serve guide" });
    }
  });

  app.get("/api/guides/download/templates/:templateType", async (req, res) => {
    try {
      const { templateType } = req.params;
      
      const templates = {
        autoreply: {
          filename: "autoreply_templates.json",
          content: {
            version: "2.3.2",
            description: "AutoReply templates for common Discord server responses",
            templates: [
              {
                id: "welcome",
                name: "Welcome Message Template",
                trigger: "welcome",
                response: "Welcome to {guild.name}, {user.mention}! Please read our rules in #rules channel.",
                enabled: true
              },
              {
                id: "faq_help",
                name: "FAQ Help Response", 
                trigger: "how to get help",
                response: "For support, please create a ticket using `/ticket create` or check our FAQ at https://nexguard.org/faq",
                enabled: true
              },
              {
                id: "rules_reminder",
                name: "Rules Reminder",
                trigger: "rules",
                response: "Please remember to follow our server rules. You can view them in #rules channel.",
                enabled: true
              }
            ]
          }
        },
        automod: {
          filename: "automod_config_templates.json",
          content: {
            version: "2.3.2", 
            description: "AutoMod configuration templates for different server types",
            configs: [
              {
                id: "gaming_server",
                name: "Gaming Server Configuration",
                settings: {
                  spam_protection: {
                    enabled: true,
                    max_messages: 5,
                    time_window: 10,
                    punishment: "timeout"
                  },
                  bad_words: {
                    enabled: true,
                    action: "delete",
                    notify_mods: true
                  },
                  caps_limit: {
                    enabled: true,
                    percentage: 70,
                    action: "warn"
                  }
                }
              },
              {
                id: "professional_server", 
                name: "Professional/Business Server",
                settings: {
                  spam_protection: {
                    enabled: true,
                    max_messages: 3,
                    time_window: 15,
                    punishment: "timeout"
                  },
                  link_filtering: {
                    enabled: true,
                    whitelist_only: true,
                    allowed_domains: ["company.com", "linkedin.com"]
                  },
                  profanity_filter: {
                    enabled: true,
                    strictness: "high",
                    action: "delete_and_warn"
                  }
                }
              }
            ]
          }
        }
      };

      const template = templates[templateType as keyof typeof templates];
      if (!template) {
        return res.status(404).json({ error: "Template not found" });
      }

      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Content-Disposition', `attachment; filename="${template.filename}"`);
      
      res.json(template.content);
      
    } catch (error) {
      console.error("Error serving template:", error);
      res.status(500).json({ error: "Failed to serve template" });
    }
  });

  // Health check
  app.get("/health", (req, res) => {
    res.json({ status: "ok", timestamp: new Date().toISOString() });
  });

  const httpServer = createServer(app);
  return httpServer;
}