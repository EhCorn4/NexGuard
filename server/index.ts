import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";
// import { NexGuardBot } from "./bot/index";
import { spawn } from 'child_process';

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…";
      }

      log(logLine);
    }
  });

  next();
});

(async () => {
  const server = await registerRoutes(app);

  app.use((err: any, req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";

    console.error('=== Server Error Handler ===');
    console.error('Error:', message);
    console.error('Stack:', err.stack);
    console.error('Request URL:', req.url);
    console.error('Request Method:', req.method);
    console.error('Request Headers:', req.headers);
    console.error('Request Body:', req.body);
    console.error('Status Code:', status);
    console.error('=====================================');

    res.status(status).json({ 
      error: message,
      timestamp: new Date().toISOString(),
      url: req.url,
      method: req.method
    });
  });

  // importantly only setup vite in development and after
  // setting up all the other routes so the catch-all route
  // doesn't interfere with the other routes
  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  // Start the Python Discord bot
  let pythonBot: any = null;
  
  function startPythonBot() {
    console.log('🚀 Starting Python NexGuard Bot...');
    pythonBot = spawn('python', ['server/bot_python/bot.py'], {
      stdio: 'inherit',
      env: process.env
    });
    
    pythonBot.on('close', (code: number) => {
      console.log(`Python bot process exited with code ${code}`);
      if (code !== 0) {
        console.log('Restarting Python bot in 5 seconds...');
        setTimeout(startPythonBot, 5000);
      }
    });
    
    pythonBot.on('error', (error: Error) => {
      console.error('Python bot error:', error);
    });
  }
  
  startPythonBot();

  // ALWAYS serve the app on port 5000
  // this serves both the API and the client.
  // It is the only port that is not firewalled.
  const port = 5000;
  server.listen({
    port,
    host: "0.0.0.0",
    reusePort: true,
  }, () => {
    log(`serving on port ${port}`);
  });

  // Graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\n🛑 Shutting down gracefully...');
    if (pythonBot) {
      pythonBot.kill('SIGINT');
    }
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\n🛑 Shutting down gracefully...');
    if (pythonBot) {
      pythonBot.kill('SIGTERM');
    }
    process.exit(0);
  });
})();
