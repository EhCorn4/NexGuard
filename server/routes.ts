import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertTestimonialSchema, insertFeedbackSchema } from "@shared/schema";
import session from "express-session";
import connectPg from "connect-pg-simple";

// Discord OAuth Configuration
const DISCORD_CLIENT_ID = process.env.DISCORD_CLIENT_ID || "1389775821794705429";
const DISCORD_CLIENT_SECRET = process.env.DISCORD_CLIENT_SECRET;

// Function to get the correct redirect URI based on request
function getDiscordRedirectUri(req: any) {
  // Hardcoded for debugging - this should match exactly what's in Discord settings
  const hardcodedUri = 'https://ed8c2fad-d762-4890-ab60-2ba13bfca210-00-1mxalymkn4j67.janeway.replit.dev/api/auth/discord/callback';
  
  console.log('=== DEBUG: Using hardcoded redirect URI ===');
  console.log('Hardcoded URI:', hardcodedUri);
  
  return hardcodedUri;
}

// Session configuration for Discord OAuth
function setupSession(app: Express) {
  const pgStore = connectPg(session);
  const sessionStore = new pgStore({
    conString: process.env.DATABASE_URL,
    createTableIfMissing: true,
    ttl: 7 * 24 * 60 * 60 * 1000, // 1 week
  });

  app.use(session({
    secret: process.env.SESSION_SECRET || 'nexguard-development-secret',
    store: sessionStore,
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 7 * 24 * 60 * 60 * 1000, // 1 week
    },
  }));
}

// Discord API helper functions
async function exchangeCodeForToken(code: string, redirectUri: string) {
  const response = await fetch('https://discord.com/api/oauth2/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      client_id: DISCORD_CLIENT_ID,
      client_secret: DISCORD_CLIENT_SECRET!,
      grant_type: 'authorization_code',
      code,
      redirect_uri: redirectUri,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to exchange code for token');
  }

  return await response.json();
}

async function getDiscordUser(accessToken: string) {
  const response = await fetch('https://discord.com/api/users/@me', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to get Discord user');
  }

  return await response.json();
}

async function getDiscordGuilds(accessToken: string) {
  const response = await fetch('https://discord.com/api/users/@me/guilds', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to get Discord guilds');
  }

  const guilds = await response.json();
  
  // Filter guilds where user has admin permissions
  const filteredGuilds = guilds.filter((guild: any) => {
    const permissions = BigInt(guild.permissions);
    const MANAGE_GUILD = BigInt(0x20);
    const ADMINISTRATOR = BigInt(0x8);
    const MANAGE_CHANNELS = BigInt(0x10);
    const MANAGE_ROLES = BigInt(0x10000000);
    
    // Check if user is owner or has any admin-level permissions
    const hasAdminPerms = guild.owner || 
                         (permissions & ADMINISTRATOR) !== BigInt(0) ||
                         (permissions & MANAGE_GUILD) !== BigInt(0) ||
                         (permissions & MANAGE_CHANNELS) !== BigInt(0) ||
                         (permissions & MANAGE_ROLES) !== BigInt(0);
    
    console.log(`Guild ${guild.name} (${guild.id}): owner=${guild.owner}, permissions=${permissions.toString()}, hasAdminPerms=${hasAdminPerms}`);
    
    return hasAdminPerms;
  });

  console.log(`Filtered ${filteredGuilds.length} guilds out of ${guilds.length} total`);
  return filteredGuilds;
}

async function checkBotInGuild(guildId: string) {
  // This would typically check if the bot is in the guild
  // For now, we'll simulate this check
  return Math.random() > 0.5; // Random for demo purposes
}

export async function registerRoutes(app: Express): Promise<Server> {
  // Setup session middleware
  setupSession(app);

  // Discord OAuth routes
  app.get('/api/auth/discord', (req, res) => {
    if (!DISCORD_CLIENT_SECRET) {
      // Redirect to dashboard with error state instead of returning JSON error
      return res.redirect('/dashboard?error=oauth_not_configured');
    }

    const redirectUri = getDiscordRedirectUri(req);
    console.log('=== Discord OAuth Debug ===');
    console.log('Request headers:', JSON.stringify(req.headers, null, 2));
    console.log('Generated redirect URI:', redirectUri);
    console.log('Expected redirect URI should be:', `https://${process.env.REPLIT_DOMAINS}/api/auth/discord/callback`);
    
    const params = new URLSearchParams({
      client_id: DISCORD_CLIENT_ID,
      redirect_uri: redirectUri,
      response_type: 'code',
      scope: 'identify guilds',
    });

    const authUrl = `https://discord.com/api/oauth2/authorize?${params}`;
    console.log('Full auth URL:', authUrl);
    res.redirect(authUrl);
  });

  app.get('/api/auth/discord/callback', async (req, res) => {
    const { code, error } = req.query;

    console.log('Discord callback received:', { code: code ? 'present' : 'missing', error });

    if (error) {
      console.error('Discord OAuth error in callback:', error);
      return res.redirect('/dashboard?error=discord_denied');
    }

    if (!code) {
      return res.redirect('/dashboard?error=no_code');
    }

    if (!DISCORD_CLIENT_SECRET) {
      return res.redirect('/dashboard?error=oauth_not_configured');
    }

    try {
      const redirectUri = getDiscordRedirectUri(req);
      const tokenData = await exchangeCodeForToken(code as string, redirectUri);
      const user = await getDiscordUser(tokenData.access_token);
      const guilds = await getDiscordGuilds(tokenData.access_token);

      // Store user session
      (req.session as any).user = {
        ...user,
        access_token: tokenData.access_token,
      };
      (req.session as any).guilds = guilds;

      // Force session save before redirect
      req.session.save((err) => {
        if (err) {
          console.error('Session save error:', err);
          return res.redirect('/dashboard?error=session_failed');
        }
        console.log('Discord OAuth successful, redirecting to dashboard');
        res.redirect('/dashboard');
      });
    } catch (error) {
      console.error('Discord OAuth error:', error);
      res.redirect('/dashboard?error=auth_failed');
    }
  });

  app.get('/api/auth/user', (req, res) => {
    if (!DISCORD_CLIENT_SECRET) {
      return res.status(500).json({ 
        error: 'Discord OAuth not configured. Please provide DISCORD_CLIENT_SECRET in environment variables.' 
      });
    }

    const user = (req.session as any)?.user;
    console.log('Session user:', user ? 'exists' : 'not found');
    if (!user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    res.json(user);
  });

  app.get('/api/auth/guilds', async (req, res) => {
    try {
      const user = (req.session as any)?.user;
      if (!user || !user.access_token) {
        return res.status(401).json({ error: 'Not authenticated' });
      }

      // Get fresh guilds from Discord API
      const guilds = await getDiscordGuilds(user.access_token);
      
      // Add bot presence information to guilds
      const guildsWithBotInfo = await Promise.all(
        guilds.map(async (guild: any) => ({
          ...guild,
          hasBot: await checkBotInGuild(guild.id),
        }))
      );

      console.log(`Returning ${guildsWithBotInfo.length} guilds to client`);
      res.json(guildsWithBotInfo);
    } catch (error) {
      console.error('Error fetching guilds:', error);
      res.status(500).json({ error: 'Failed to fetch guilds' });
    }
  });

  // Debug endpoint to show all guilds (unfiltered)
  app.get('/api/auth/guilds/debug', async (req, res) => {
    try {
      const user = (req.session as any)?.user;
      if (!user || !user.access_token) {
        return res.status(401).json({ error: 'Not authenticated' });
      }

      // Get raw guilds from Discord API without filtering
      const response = await fetch('https://discord.com/api/users/@me/guilds', {
        headers: {
          Authorization: `Bearer ${user.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to get Discord guilds');
      }

      const allGuilds = await response.json();
      
      // Add permission analysis
      const guildsWithAnalysis = allGuilds.map((guild: any) => {
        const permissions = BigInt(guild.permissions);
        const MANAGE_GUILD = BigInt(0x20);
        const ADMINISTRATOR = BigInt(0x8);
        const MANAGE_CHANNELS = BigInt(0x10);
        const MANAGE_ROLES = BigInt(0x10000000);
        
        return {
          ...guild,
          permissionAnalysis: {
            owner: guild.owner,
            permissions: permissions.toString(),
            hasAdministrator: (permissions & ADMINISTRATOR) !== BigInt(0),
            hasManageGuild: (permissions & MANAGE_GUILD) !== BigInt(0),
            hasManageChannels: (permissions & MANAGE_CHANNELS) !== BigInt(0),
            hasManageRoles: (permissions & MANAGE_ROLES) !== BigInt(0),
          }
        };
      });

      res.json(guildsWithAnalysis);
    } catch (error) {
      console.error('Error fetching debug guilds:', error);
      res.status(500).json({ error: 'Failed to fetch guilds' });
    }
  });

  app.get('/api/auth/logout', (req, res) => {
    req.session.destroy((err) => {
      if (err) {
        console.error('Session destruction error:', err);
      }
      res.redirect('/');
    });
  });

  // Middleware to check if user is authenticated
  const requireAuth = (req: any, res: any, next: any) => {
    if (!req.session.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    next();
  };

  // Middleware to check if user can manage a specific guild
  const requireGuildAdmin = (req: any, res: any, next: any) => {
    const { guildId } = req.params;
    const userGuilds = req.session.guilds || [];
    
    const guild = userGuilds.find((g: any) => g.id === guildId);
    if (!guild) {
      return res.status(404).json({ error: 'Guild not found' });
    }

    const permissions = parseInt(guild.permissions);
    const MANAGE_GUILD = 0x20;
    const ADMINISTRATOR = 0x8;
    
    if (!guild.owner && !(permissions & MANAGE_GUILD) && !(permissions & ADMINISTRATOR)) {
      return res.status(403).json({ error: 'Insufficient permissions to manage this server' });
    }
    
    req.guild = guild;
    next();
  };

  // Server-specific management endpoints
  app.get('/api/servers/:guildId/config', requireAuth, requireGuildAdmin, async (req, res) => {
    const { guildId } = req.params;
    
    try {
      // This would fetch server-specific configuration from your database
      const serverConfig = {
        guildId,
        name: req.guild.name,
        autoModeration: {
          enabled: true,
          badWordsFilter: true,
          spamProtection: true,
          raidProtection: false,
        },
        moderation: {
          logChannel: null,
          muteRole: null,
          autoDelete: true,
        },
        permissions: {
          modRole: null,
          adminRole: null,
        }
      };
      
      res.json(serverConfig);
    } catch (error) {
      console.error('Error fetching server config:', error);
      res.status(500).json({ error: 'Failed to fetch server configuration' });
    }
  });

  app.put('/api/servers/:guildId/config', requireAuth, requireGuildAdmin, async (req, res) => {
    const { guildId } = req.params;
    const config = req.body;
    
    try {
      // This would update server-specific configuration in your database
      // For now, just return the updated config
      res.json({ 
        success: true, 
        message: 'Server configuration updated successfully',
        config 
      });
    } catch (error) {
      console.error('Error updating server config:', error);
      res.status(500).json({ error: 'Failed to update server configuration' });
    }
  });

  app.get('/api/servers/:guildId/moderation/logs', requireAuth, requireGuildAdmin, async (req, res) => {
    const { guildId } = req.params;
    
    try {
      // This would fetch moderation logs from your database
      const logs = [
        {
          id: 1,
          type: 'warn',
          user: { id: '123456789', username: 'example_user' },
          moderator: { id: '987654321', username: 'moderator' },
          reason: 'Spam in general chat',
          timestamp: new Date().toISOString(),
        },
        {
          id: 2,
          type: 'timeout',
          user: { id: '111222333', username: 'another_user' },
          moderator: { id: '987654321', username: 'moderator' },
          reason: 'Inappropriate language',
          duration: '1 hour',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
        }
      ];
      
      res.json(logs);
    } catch (error) {
      console.error('Error fetching moderation logs:', error);
      res.status(500).json({ error: 'Failed to fetch moderation logs' });
    }
  });

  // API routes for NexGuard website
  app.get("/api/news", async (req, res) => {
    try {
      const news = await storage.getNewsUpdates();
      res.json(news);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch news updates" });
    }
  });

  app.get("/api/developers", async (req, res) => {
    try {
      const developers = await storage.getDevelopers();
      res.json(developers);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch developers" });
    }
  });

  app.get("/api/features", async (req, res) => {
    try {
      const features = await storage.getFeatures();
      res.json(features);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch features" });
    }
  });

  app.get("/api/testimonials", async (req, res) => {
    try {
      const testimonials = await storage.getTestimonials();
      res.json(testimonials);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch testimonials" });
    }
  });

  app.post("/api/testimonials", async (req, res) => {
    try {
      const validatedData = insertTestimonialSchema.parse(req.body);
      const testimonial = await storage.createTestimonial(validatedData);
      res.status(201).json(testimonial);
    } catch (error) {
      res.status(400).json({ message: "Invalid testimonial data" });
    }
  });

  app.post("/api/feedback", async (req, res) => {
    try {
      const validatedData = insertFeedbackSchema.parse(req.body);
      const feedback = await storage.createFeedback(validatedData);
      res.status(201).json(feedback);
    } catch (error) {
      res.status(400).json({ message: "Invalid feedback data" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
