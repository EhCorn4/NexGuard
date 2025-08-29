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

export async function setupDiscordAuth(app: Express) {
  app.set("trust proxy", 1);
  app.use(getSession());
  app.use(passport.initialize());
  app.use(passport.session());

  console.log('Setting up Discord authentication...');

  // Determine the correct callback URL for both development and production
  const getCallbackURL = () => {
    // In production deployments, use REPL_SLUG for the domain
    if (process.env.NODE_ENV === 'production' && process.env.REPL_SLUG) {
      return `https://${process.env.REPL_SLUG}.replit.app/api/auth/discord/callback`;
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
        });
        
        console.log('Discord user upserted:', user.id);
        return done(null, { ...user, accessToken, refreshToken });
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