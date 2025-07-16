import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertTestimonialSchema, insertFeedbackSchema } from "@shared/schema";
import { botManager } from "./bot-manager";
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
    const errorText = await response.text();
    console.error('Discord OAuth error:', response.status, errorText);
    throw new Error(`Failed to exchange code for token: ${response.status} ${errorText}`);
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
    console.log('Auth check - Session:', !!req.session?.user);
    if (!req.session.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    next();
  };

  // Middleware to check if user can manage a specific guild
  const requireGuildAdmin = (req: any, res: any, next: any) => {
    const { guildId } = req.params;
    const userGuilds = req.session.guilds || [];
    
    console.log('Guild check - Guild ID:', guildId);
    console.log('User guilds:', userGuilds.map((g: any) => ({ id: g.id, name: g.name })));
    
    const guild = userGuilds.find((g: any) => g.id === guildId);
    if (!guild) {
      return res.status(404).json({ error: 'Server not found or you do not have access' });
    }

    const permissions = parseInt(guild.permissions);
    const MANAGE_GUILD = 0x20;
    const ADMINISTRATOR = 0x8;
    
    console.log('Guild permissions check:', { owner: guild.owner, permissions, hasManageGuild: !!(permissions & MANAGE_GUILD), hasAdmin: !!(permissions & ADMINISTRATOR) });
    
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
        id: 1,
        guildId,
        guildName: req.guild.name,
        ownerId: req.guild.owner_id || req.session.user.id,
        
        // Moderation Settings
        moderationEnabled: true,
        autoModEnabled: true,
        spamProtection: true,
        linkProtection: false,
        profanityFilter: true,
        
        // Logging Settings
        modLogChannel: null,
        auditLogChannel: null,
        
        // Welcome/Leave Settings
        welcomeEnabled: false,
        welcomeChannel: null,
        welcomeMessage: "Welcome to {server}, {user}!",
        leaveEnabled: false,
        leaveChannel: null,
        leaveMessage: "{user} has left the server.",
        
        // Role Settings
        autoRoleEnabled: false,
        autoRoleId: null,
        mutedRoleId: null,
        
        // Economy Settings
        economyEnabled: false,
        dailyReward: 100,
        
        // Custom Commands
        customCommandsEnabled: true,
        maxCustomCommands: 20,
        
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
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

  app.get('/api/servers/:guildId/commands', requireAuth, requireGuildAdmin, async (req, res) => {
    const { guildId } = req.params;
    
    try {
      // This would fetch custom commands from your database
      const commands = [
        {
          id: 1,
          guildId,
          name: 'rules',
          response: 'Please follow our server rules:\n1. Be respectful\n2. No spam\n3. Keep discussions on topic',
          createdBy: req.session.user.id,
          createdAt: new Date().toISOString(),
        },
        {
          id: 2,
          guildId,
          name: 'discord',
          response: 'Join our Discord community at https://discord.gg/example',
          createdBy: req.session.user.id,
          createdAt: new Date().toISOString(),
        }
      ];
      
      res.json(commands);
    } catch (error) {
      console.error('Error fetching commands:', error);
      res.status(500).json({ error: 'Failed to fetch commands' });
    }
  });

  app.post('/api/servers/:guildId/commands', requireAuth, requireGuildAdmin, async (req, res) => {
    const { guildId } = req.params;
    const { name, response } = req.body;
    
    try {
      // This would create a new command in your database
      const command = {
        id: Date.now(), // Simple ID for demo
        guildId,
        name,
        response,
        createdBy: req.session.user.id,
        createdAt: new Date().toISOString(),
      };
      
      res.status(201).json(command);
    } catch (error) {
      console.error('Error creating command:', error);
      res.status(500).json({ error: 'Failed to create command' });
    }
  });

  app.delete('/api/servers/:guildId/commands/:commandId', requireAuth, requireGuildAdmin, async (req, res) => {
    const { guildId, commandId } = req.params;
    
    try {
      // This would delete the command from your database
      res.json({ success: true, message: 'Command deleted successfully' });
    } catch (error) {
      console.error('Error deleting command:', error);
      res.status(500).json({ error: 'Failed to delete command' });
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

  // Bot Authentication Middleware
  const requireBotAuth = (req: any, res: any, next: any) => {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Bot authentication required' });
    }
    
    const token = authHeader.substring(7);
    if (token !== process.env.DISCORD_BOT_TOKEN) {
      return res.status(401).json({ error: 'Invalid bot token' });
    }
    
    next();
  };

  // Bot API Endpoints - Secure endpoints for your Discord bot
  app.get('/api/bot/servers/:guildId/config', requireBotAuth, async (req, res) => {
    const { guildId } = req.params;
    
    try {
      // Get server configuration from database
      const config = await storage.getServerConfig(guildId);
      
      if (!config) {
        // Return default configuration if none exists
        const defaultConfig = {
          guildId,
          moderationEnabled: false,
          autoModEnabled: false,
          spamProtection: false,
          linkProtection: false,
          profanityFilter: false,
          welcomeEnabled: false,
          welcomeChannel: null,
          welcomeMessage: "Welcome to {server}, {user}!",
          leaveEnabled: false,
          leaveChannel: null,
          leaveMessage: "{user} has left the server.",
          autoRoleEnabled: false,
          autoRoleId: null,
          mutedRoleId: null,
          economyEnabled: false,
          dailyReward: 100,
          customCommandsEnabled: true,
          maxCustomCommands: 20,
          modLogChannel: null,
          auditLogChannel: null
        };
        return res.json(defaultConfig);
      }
      
      res.json(config);
    } catch (error) {
      console.error('Bot API - Error fetching server config:', error);
      res.status(500).json({ error: 'Failed to fetch server configuration' });
    }
  });

  app.get('/api/bot/servers/:guildId/commands', requireBotAuth, async (req, res) => {
    const { guildId } = req.params;
    
    try {
      const commands = await storage.getCustomCommands(guildId);
      res.json(commands);
    } catch (error) {
      console.error('Bot API - Error fetching commands:', error);
      res.status(500).json({ error: 'Failed to fetch commands' });
    }
  });

  app.post('/api/bot/servers/:guildId/commands', requireBotAuth, async (req, res) => {
    const { guildId } = req.params;
    const { name, response, createdBy } = req.body;
    
    try {
      const command = await storage.createCustomCommand({
        guildId,
        name,
        response,
        createdBy
      });
      res.json(command);
    } catch (error) {
      console.error('Bot API - Error creating command:', error);
      res.status(500).json({ error: 'Failed to create command' });
    }
  });

  app.post('/api/bot/servers/:guildId/moderation/log', requireBotAuth, async (req, res) => {
    const { guildId } = req.params;
    const { type, userId, moderatorId, reason, duration } = req.body;
    
    try {
      // Log moderation action to database
      // This would typically store in a moderation_logs table
      console.log('Moderation log:', { guildId, type, userId, moderatorId, reason, duration });
      
      res.json({ success: true, message: 'Moderation action logged' });
    } catch (error) {
      console.error('Bot API - Error logging moderation:', error);
      res.status(500).json({ error: 'Failed to log moderation action' });
    }
  });

  app.post('/api/bot/servers/:guildId/sync', requireBotAuth, async (req, res) => {
    const { guildId } = req.params;
    const { channels, roles, members } = req.body;
    
    try {
      // Sync server data from Discord bot
      // This would update server information in the database
      console.log('Server sync:', { guildId, channelCount: channels?.length, roleCount: roles?.length, memberCount: members?.length });
      
      res.json({ success: true, message: 'Server data synchronized' });
    } catch (error) {
      console.error('Bot API - Error syncing server data:', error);
      res.status(500).json({ error: 'Failed to sync server data' });
    }
  });

  // Bot status endpoint
  app.get("/api/bot/status", (req, res) => {
    try {
      // Get real bot status from bot manager
      const botStatus = botManager.getStatus();
      
      const response = {
        online: botStatus.online,
        guilds: botStatus.guilds,
        users: botStatus.users,
        uptime: botStatus.uptime,
        commands: botStatus.online ? 25 : 0,
        lastHeartbeat: new Date(),
        version: '2.3.2',
        lastUpdated: botStatus.lastUpdated
      };
      
      res.json(response);
    } catch (error) {
      console.error('Error fetching bot status:', error);
      res.status(500).json({ error: 'Failed to fetch bot status' });
    }
  });

  // Bot management endpoints
  app.post("/api/bot/start", async (req, res) => {
    try {
      const success = await botManager.startBot();
      res.json({ success, message: success ? 'Bot started' : 'Failed to start bot' });
    } catch (error) {
      console.error('Error starting bot:', error);
      res.status(500).json({ error: 'Failed to start bot' });
    }
  });

  app.post("/api/bot/stop", async (req, res) => {
    try {
      const success = await botManager.stopBot();
      res.json({ success, message: success ? 'Bot stopped' : 'Failed to stop bot' });
    } catch (error) {
      console.error('Error stopping bot:', error);
      res.status(500).json({ error: 'Failed to stop bot' });
    }
  });

  app.post("/api/bot/restart", async (req, res) => {
    try {
      const success = await botManager.restart();
      res.json({ success, message: success ? 'Bot restarted' : 'Failed to restart bot' });
    } catch (error) {
      console.error('Error restarting bot:', error);
      res.status(500).json({ error: 'Failed to restart bot' });
    }
  });

  app.post("/api/bot/status", requireBotAuth, (req, res) => {
    try {
      const status = req.body;
      // Store bot status in memory or database
      console.log('Bot status update:', status);
      res.json({ success: true });
    } catch (error) {
      console.error('Error updating bot status:', error);
      res.status(500).json({ error: 'Failed to update bot status' });
    }
  });

  // Configuration endpoint for frontend
  app.get("/api/config", (req, res) => {
    res.json({
      discordClientId: process.env.DISCORD_CLIENT_ID || "1389775821794705429",
      discordInviteUrl: `https://discord.com/oauth2/authorize?client_id=${process.env.DISCORD_CLIENT_ID || "1389775821794705429"}&permissions=8&scope=bot`,
      supportServerUrl: "https://discord.gg/wpjZMPXaRT"
    });
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
