import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertTestimonialSchema, insertFeedbackSchema } from "@shared/schema";
import { directBotStarter } from "./direct-bot-starter";
import session from "express-session";
import connectPg from "connect-pg-simple";

// Discord OAuth Configuration
const DISCORD_CLIENT_ID = process.env.DISCORD_CLIENT_ID || "1389775821794705429";
const DISCORD_CLIENT_SECRET = process.env.DISCORD_CLIENT_SECRET;

// Function to get the correct redirect URI based on environment
function getDiscordRedirectUri(req: any) {
  // Check for Replit environment variables
  const replitDomain = process.env.REPLIT_DOMAINS;
  
  if (replitDomain) {
    // Use the first domain from REPLIT_DOMAINS
    const domain = replitDomain.split(',')[0];
    const redirectUri = `https://${domain}/api/auth/discord/callback`;
    return redirectUri;
  }
  
  // Fallback to request headers
  const host = req.get('x-forwarded-host') || req.get('host');
  const protocol = req.get('x-forwarded-proto') || req.protocol || 'https';
  
  // If running on Replit, use https
  const finalProtocol = host && host.includes('replit.dev') ? 'https' : protocol;
  
  // Build the redirect URI using the actual host
  const redirectUri = `${finalProtocol}://${host}/api/auth/discord/callback`;
  
  return redirectUri;
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
    name: 'nexguard.sid',
    cookie: {
      httpOnly: true,
      secure: false, // Set to false for development
      maxAge: 7 * 24 * 60 * 60 * 1000, // 1 week
      sameSite: 'lax', // Add sameSite attribute
    },
  }));
  
  console.log('Session middleware configured');
}

// Discord API helper functions
async function exchangeCodeForToken(code: string, redirectUri: string) {
  console.log('=== OAuth Token Exchange ===');
  console.log('Client ID:', DISCORD_CLIENT_ID);
  console.log('Code:', code.substring(0, 10) + '...');
  console.log('Redirect URI:', redirectUri);
  console.log('Has Client Secret:', !!DISCORD_CLIENT_SECRET);
  
  const params = new URLSearchParams({
    client_id: DISCORD_CLIENT_ID,
    client_secret: DISCORD_CLIENT_SECRET!,
    grant_type: 'authorization_code',
    code,
    redirect_uri: redirectUri,
  });
  
  console.log('Request body length:', params.toString().length);
  
  const response = await fetch('https://discord.com/api/oauth2/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params,
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('Discord OAuth error:', response.status, errorText);
    console.error('Response headers:', Object.fromEntries(response.headers.entries()));
    throw new Error(`Failed to exchange code for token: ${response.status} ${errorText}`);
  }

  const tokenData = await response.json();
  console.log('Token exchange successful');
  return tokenData;
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
  // Setup session middleware for Discord OAuth
  setupSession(app);
  
  // Minimal logging for server routes
  app.use('/api/servers', (req, res, next) => {
    console.log(`${req.method} ${req.url} - User: ${req.session?.user?.id || 'none'}`);
    next();
  });

  // Discord OAuth routes
  app.get('/api/auth/discord', (req, res) => {
    if (!DISCORD_CLIENT_SECRET) {
      // Redirect to dashboard with error state instead of returning JSON error
      return res.redirect('/dashboard?error=oauth_not_configured');
    }

    const redirectUri = getDiscordRedirectUri(req);
    
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
      console.log('=== Storing Session Data ===');
      console.log('User ID:', user.id);
      console.log('Guilds count:', guilds.length);
      console.log('Session ID before save:', req.session.id);
      
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
        console.log('Session saved successfully');
        console.log('Session ID after save:', req.session.id);
        console.log('Discord OAuth successful, redirecting to dashboard');
        res.redirect('/dashboard');
      });
    } catch (error) {
      console.error('Discord OAuth error:', error);
      res.redirect('/dashboard?error=auth_failed');
    }
  });

  // Test session endpoint
  app.get('/api/test/session', (req, res) => {
    console.log('=== Session Test ===');
    console.log('Session exists:', !!req.session);
    console.log('Session ID:', req.session?.id);
    
    if (!req.session.views) {
      req.session.views = 0;
    }
    req.session.views++;
    
    res.json({
      sessionExists: !!req.session,
      sessionId: req.session.id,
      views: req.session.views,
      hasUser: !!req.session.user
    });
  });

  app.get('/api/auth/user', (req, res) => {
    if (!DISCORD_CLIENT_SECRET) {
      return res.status(500).json({ 
        error: 'Discord OAuth not configured. Please provide DISCORD_CLIENT_SECRET in environment variables.' 
      });
    }

    console.log('=== User Auth Check ===');
    console.log('Session exists:', !!req.session);
    console.log('Session ID:', req.session?.id);
    console.log('Session user exists:', !!req.session?.user);
    
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
    console.log('=== Auth Check Debug ===');
    console.log('Session exists:', !!req.session);
    console.log('Session ID:', req.session?.id);
    console.log('Session user exists:', !!req.session?.user);
    console.log('Session user ID:', req.session?.user?.id);
    console.log('Session guilds count:', req.session?.guilds?.length || 0);
    
    if (!req.session?.user) {
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
    
    console.log('=== Server Config Endpoint Hit ===');
    console.log('Guild ID:', guildId);
    console.log('User ID:', req.session?.user?.id);
    console.log('Guild from middleware:', req.guild?.name);
    
    try {
      // Try to get existing config from database
      let serverConfig = await storage.getServerConfig(guildId);
      
      // If no config exists, create a default one
      if (!serverConfig) {
        const defaultConfig = {
          guildId,
          guildName: req.guild.name,
          ownerId: req.guild.owner_id || req.session.user.id,
          
          // Moderation Settings
          moderationEnabled: true,
          autoModEnabled: true,
          spamProtection: true,
          linkProtection: false,
          profanityFilter: true,
          antiRaidEnabled: true,
          
          // Filter Settings
          capsFilter: false,
          duplicateMessageFilter: true,
          mentionSpamFilter: true,
          maxMentions: 5,
          
          // Rate Limiting
          slowmodeEnabled: false,
          slowmodeSeconds: 5,
          spamMessageCount: 5,
          
          // Warning System
          maxWarnings: 3,
          warningExpireDays: 30,
          warnAction: "warn",
          
          // Punishment Actions
          muteAction: "mute",
          kickAction: "kick",
          tempbanDuration: 24,
          
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
        };
        
        console.log('Creating new config for guild:', guildId);
        serverConfig = await storage.createServerConfig(defaultConfig);
      }
      
      console.log('Returning config for guild:', guildId);
      res.json(serverConfig);
    } catch (error) {
      console.error('Error fetching server config:', error);
      res.status(500).json({ error: 'Failed to fetch server configuration' });
    }
  });

  app.put('/api/servers/:guildId/config', requireAuth, requireGuildAdmin, async (req, res) => {
    const { guildId } = req.params;
    const updates = req.body;
    
    try {
      // Update server configuration in database
      const updatedConfig = await storage.updateServerConfig(guildId, updates);
      
      res.json({ 
        success: true, 
        message: 'Server configuration updated successfully',
        config: updatedConfig 
      });
    } catch (error) {
      console.error('Error updating server config:', error);
      res.status(500).json({ error: 'Failed to update server configuration' });
    }
  });

  app.get('/api/servers/:guildId/commands', requireAuth, requireGuildAdmin, async (req, res) => {
    const { guildId } = req.params;
    
    try {
      // Fetch custom commands from database
      const commands = await storage.getCustomCommands(guildId);
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
      // Create a new command in database
      const command = await storage.createCustomCommand({
        guildId,
        name,
        response,
        createdBy: req.session.user.id,
      });
      
      res.status(201).json(command);
    } catch (error) {
      console.error('Error creating command:', error);
      res.status(500).json({ error: 'Failed to create command' });
    }
  });

  app.delete('/api/servers/:guildId/commands/:commandId', requireAuth, requireGuildAdmin, async (req, res) => {
    const { guildId, commandId } = req.params;
    
    try {
      // Delete the command from database
      const deleted = await storage.deleteCustomCommand(parseInt(commandId));
      
      if (deleted) {
        res.json({ success: true, message: 'Command deleted successfully' });
      } else {
        res.status(404).json({ error: 'Command not found' });
      }
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
      const botStatus = directBotStarter.getStatus();
      
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
      console.log('Starting bot via API...');
      const success = await directBotStarter.startBot();
      console.log('Bot start result:', success);
      res.json({ success, message: success ? 'Bot started' : 'Failed to start bot' });
    } catch (error) {
      console.error('Error starting bot:', error);
      res.status(500).json({ error: 'Failed to start bot' });
    }
  });

  app.post("/api/bot/stop", async (req, res) => {
    try {
      const success = await directBotStarter.stopBot();
      res.json({ success, message: success ? 'Bot stopped' : 'Failed to stop bot' });
    } catch (error) {
      console.error('Error stopping bot:', error);
      res.status(500).json({ error: 'Failed to stop bot' });
    }
  });

  app.post("/api/bot/restart", async (req, res) => {
    try {
      const success = await directBotStarter.restart();
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

  // Add health check endpoint for deployment monitoring
  app.get('/health', (req, res) => {
    res.status(200).json({ 
      status: 'healthy', 
      timestamp: new Date().toISOString(),
      service: 'nexguard-website',
      version: '1.0.0'
    });
  });

  // Add simple root endpoint for deployment verification
  app.get('/api/health', (req, res) => {
    res.status(200).json({ 
      status: 'ok', 
      message: 'NexGuard API is running',
      timestamp: new Date().toISOString()
    });
  });

  const httpServer = createServer(app);
  return httpServer;
}
