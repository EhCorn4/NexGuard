import passport from "passport";
import { Strategy as DiscordStrategy } from "passport-discord";
import session from "express-session";
import type { Express, RequestHandler } from "express";
import connectPg from "connect-pg-simple";
import { storage } from "./storage";

if (!process.env.DISCORD_CLIENT_ID || !process.env.DISCORD_CLIENT_SECRET) {
  throw new Error("Discord OAuth credentials not provided");
}

export function getSession() {
  const sessionTtl = 7 * 24 * 60 * 60 * 1000; // 1 week
  const pgStore = connectPg(session);
  const sessionStore = new pgStore({
    conString: process.env.DATABASE_URL,
    createTableIfMissing: false,
    ttl: sessionTtl,
    tableName: "sessions",
  });
  
  return session({
    secret: process.env.SESSION_SECRET!,
    store: sessionStore,
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      secure: true,
      maxAge: sessionTtl,
    },
  });
}

// Discord API helper function to get user's admin guilds
export async function getUserAdminGuilds(userId: string, accessToken: string) {
  const response = await fetch('https://discord.com/api/v10/users/@me/guilds', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'User-Agent': 'NexGuard Bot (https://nexguard.com, 1.0)'
    }
  });

  if (!response.ok) {
    throw new Error(`Discord API error: ${response.status}`);
  }

  const guilds = await response.json();
  
  // Filter to only guilds where user has Administrator permission (permission bit 3)
  const adminGuilds = guilds.filter((guild: any) => {
    const hasAdmin = (parseInt(guild.permissions) & 0x8) === 0x8; // Administrator permission
    const isOwner = guild.owner === true;
    return hasAdmin || isOwner;
  });

  console.log(`User ${userId} has admin access to ${adminGuilds.length}/${guilds.length} guilds`);

  // Get bot guilds to mark which ones have the bot and get accurate member counts
  const { BotConfigService } = await import('./api/botConfig');
  const botGuilds = await BotConfigService.getBotGuilds();
  const botGuildIds = new Set(botGuilds.map(g => g.id));
  const memberCountMap = new Map(botGuilds.map(g => [g.id, g.member_count]));

  console.log(`User ${userId} has admin access to ${adminGuilds.length} total admin guilds`);
  console.log(`Bot is present in ${botGuilds.length} guilds`);

  // Return ALL admin guilds, marking which ones have the bot
  return adminGuilds.map((guild: any) => {
    const hasBot = botGuildIds.has(guild.id);
    return {
      id: guild.id,
      name: guild.name,
      icon: guild.icon,
      member_count: hasBot ? (memberCountMap.get(guild.id) || 0) : (guild.approximate_member_count || 0),
      channel_count: 0,
      hasBot: hasBot,
      permissions: guild.permissions
    };
  });
}

export async function setupDiscordAuth(app: Express) {
  app.set("trust proxy", 1);
  app.use(getSession());
  app.use(passport.initialize());
  app.use(passport.session());

  console.log('Setting up Discord authentication...');

  // Determine the correct callback URL for both development and production
  const getCallbackURL = () => {
    // Check if we're in production deployment based on hostname
    if (process.env.NODE_ENV === 'production' || process.env.REPLIT_DEPLOYMENT === 'true') {
      return 'https://nexguard.replit.app/api/auth/discord/callback';
    }
    
    // In development, use REPLIT_DOMAINS
    if (process.env.REPLIT_DOMAINS) {
      return `https://${process.env.REPLIT_DOMAINS.split(',')[0]}/api/auth/discord/callback`;
    }
    
    // Fallback to relative URL
    return "/api/auth/discord/callback";
  };

  const callbackURL = getCallbackURL();
  console.log('Discord callback URL:', callbackURL);

  const strategy = new DiscordStrategy(
    {
      clientID: process.env.DISCORD_CLIENT_ID!,
      clientSecret: process.env.DISCORD_CLIENT_SECRET!,
      callbackURL,
      scope: ["identify", "email", "guilds"],
    },
    async (accessToken: string, refreshToken: string, profile: any, done: any) => {
      try {
        console.log('Discord OAuth callback - Profile:', profile.id, profile.username);
        
        // Upsert user in database
        const user = await storage.upsertUser({
          id: profile.id,
          username: profile.username,
          discriminator: profile.discriminator || "0",
          email: profile.email,
          avatar: profile.avatar,
          verified: profile.verified || false,
          locale: profile.locale,
          mfaEnabled: profile.mfa_enabled || false,
          accessToken: accessToken,
          refreshToken: refreshToken,
        });
        
        console.log('Discord user upserted:', user.id);
        return done(null, user);
      } catch (error) {
        console.error('Discord auth error:', error);
        return done(error, null);
      }
    }
  );

  passport.use(strategy);
  console.log('Discord strategy registered');

  passport.serializeUser((user: any, done) => {
    console.log('Serializing user:', user.id);
    done(null, user.id);
  });

  passport.deserializeUser(async (id: any, done) => {
    try {
      console.log('Deserializing user:', id);
      // Handle both Discord users and legacy sessions
      if (typeof id === 'object' && (id as any).claims) {
        // Legacy Replit session - clear it
        console.log('Clearing legacy Replit session');
        return done(null, false);
      }
      const user = await storage.getUser(String(id));
      done(null, user);
    } catch (error) {
      console.error('Error deserializing user:', error);
      done(null, false);
    }
  });

  // Auth routes with URL mapping support
  app.get("/api/auth/discord", (req, res, next) => {
    // Store return URL in session for post-auth redirect
    const returnTo = req.query.returnTo as string || '/dashboard';
    (req.session as any).returnTo = returnTo;
    console.log('Discord auth initiated, return URL:', returnTo);
    passport.authenticate("discord")(req, res, next);
  });

  app.get("/api/auth/discord/callback", 
    passport.authenticate("discord", { failureRedirect: "/?error=auth_failed" }),
    (req, res) => {
      console.log('Discord auth successful');
      const returnTo = (req.session as any).returnTo || '/dashboard';
      delete (req.session as any).returnTo; // Clean up
      console.log('Redirecting to:', returnTo + '?auth=success');
      res.redirect(returnTo + '?auth=success');
    }
  );

  app.get("/api/logout", (req, res) => {
    console.log('Logging out user');
    req.logout((err) => {
      if (err) {
        console.error('Logout error:', err);
        return res.status(500).json({ error: 'Logout failed' });
      }
      res.redirect("/");
    });
  });
}

export const isAuthenticated: RequestHandler = (req, res, next) => {
  console.log('Auth check - isAuthenticated:', req.isAuthenticated());
  console.log('Auth check - user:', req.user ? 'Present' : 'None');
  
  if (req.isAuthenticated() && req.user) {
    return next();
  }
  
  return res.status(401).json({ message: "Unauthorized" });
};