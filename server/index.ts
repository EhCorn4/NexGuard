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
  try {
    console.log('🔄 Initializing NexGuard Discord Bot Management System...');
    console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
    
    // Check for critical environment variables
    const criticalEnvVars = ['DATABASE_URL'];
    const missingCritical = criticalEnvVars.filter(varName => !process.env[varName]);
    
    if (missingCritical.length > 0) {
      console.error('❌ Missing critical environment variables:');
      missingCritical.forEach(varName => {
        console.error(`   - ${varName}`);
      });
      console.error('🛑 Server startup aborted. Please configure these variables.');
      process.exit(1);
    }
    
    console.log('📋 Registering API routes...');
    const server = await registerRoutes(app);
    console.log('✅ API routes registered successfully');

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

  // Start the Python Discord bot (only in development or when Python is available)
  let pythonBot: any = null;
  let isPythonAvailable = false;
  
  // Check Python availability
  const checkPythonAvailability = () => {
    return new Promise<boolean>((resolve) => {
      // Python runtime is available in Replit VM deployments with python-3.11 module
      // Removed deployment environment restriction to allow Discord bot in production
      
      const pythonCommand = process.env.NODE_ENV === 'production' ? 'python3' : 'python';
      const testProcess = spawn(pythonCommand, ['--version'], { 
        stdio: 'pipe',
        timeout: 5000 
      });
      
      testProcess.on('close', (code) => {
        if (code === 0) {
          console.log('✅ Python runtime detected');
          resolve(true);
        } else {
          console.log('⚠️  Python runtime not available (exit code:', code, ')');
          resolve(false);
        }
      });
      
      testProcess.on('error', (error) => {
        console.log('⚠️  Python runtime not available:', error.message);
        resolve(false);
      });
    });
  };
  
  const startPythonBot = async () => {
    // Check Python availability first
    isPythonAvailable = await checkPythonAvailability();
    
    if (!isPythonAvailable) {
      console.log('⚠️  Python bot disabled - runtime not available');
      console.log('   The web interface will still function normally');
      return;
    }
    
    console.log('🚀 Starting Python NexGuard Bot...');
    
    // Check for required environment variables
    const requiredEnvVars = ['DISCORD_BOT_TOKEN', 'DATABASE_URL'];
    const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
    
    if (missingVars.length > 0) {
      console.error('❌ Missing required environment variables for Python bot:');
      missingVars.forEach(varName => {
        console.error(`   - ${varName}`);
      });
      console.error('Bot startup aborted. Please configure these variables in your deployment secrets.');
      return;
    }
    
    // Use python3 in production environments where python might not be available
    const pythonCommand = process.env.NODE_ENV === 'production' ? 'python3' : 'python';
    
    try {
      pythonBot = spawn(pythonCommand, ['server/bot_python/run.py'], {
        stdio: 'inherit',
        env: process.env
      });
      
      pythonBot.on('close', (code: number) => {
        console.log(`🤖 Python bot process exited with code ${code}`);
        if (code !== 0 && isPythonAvailable) {
          console.log('⚠️  Bot crashed. Restarting in 5 seconds...');
          setTimeout(startPythonBot, 5000);
        } else {
          console.log('✅ Python bot shut down gracefully');
        }
      });
      
      pythonBot.on('error', (error: Error) => {
        console.error('❌ Python bot startup error:');
        console.error('   Error:', error.message);
        console.error('   Stack:', error.stack);
        if (isPythonAvailable) {
          console.error('⚠️  Retrying bot startup in 10 seconds...');
          setTimeout(startPythonBot, 10000);
        } else {
          console.log('⚠️  Python runtime no longer available, disabling bot');
        }
      });
    } catch (error) {
      console.error('❌ Failed to start Python bot:', error);
      isPythonAvailable = false;
    }
  };
  
  await startPythonBot();

  // Use PORT environment variable for deployment compatibility, default to 5000
  // this serves both the API and the client.
  // It is the only port that is not firewalled in development.
  const port = parseInt(process.env.PORT || "5000", 10);
  
  // Add error handling for server startup
  server.on('error', (error: any) => {
    console.error('=== Server Startup Error ===');
    console.error('Error Code:', error.code);
    console.error('Error Message:', error.message);
    console.error('Port:', port);
    console.error('Host: 0.0.0.0');
    console.error('Stack:', error.stack);
    console.error('===========================');
    
    if (error.code === 'EADDRINUSE') {
      console.error(`Port ${port} is already in use. Please try a different port or stop the conflicting process.`);
    }
    
    process.exit(1);
  });
  
  server.listen({
    port,
    host: "0.0.0.0",
    reusePort: true,
  }, () => {
    console.log(`🚀 NexGuard Discord Bot Management Server started successfully!`);
    console.log(`📍 Server listening on: http://0.0.0.0:${port}`);
    console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`🗄️  Database: ${process.env.DATABASE_URL ? 'Connected' : 'Not configured'}`);
    console.log(`🤖 Discord Bot: Starting...`);
    log(`serving on port ${port}`);
  });

    // Graceful shutdown handlers
    process.on('SIGINT', async () => {
      console.log('\n🛑 Shutting down gracefully...');
      if (pythonBot && isPythonAvailable) {
        console.log('🤖 Stopping Python bot...');
        pythonBot.kill('SIGINT');
        // Give the Python bot time to shut down gracefully
        await new Promise(resolve => setTimeout(resolve, 2000));
      } else {
        console.log('🤖 Python bot not running, skipping shutdown');
      }
      process.exit(0);
    });

    process.on('SIGTERM', async () => {
      console.log('\n🛑 Shutting down gracefully...');
      if (pythonBot && isPythonAvailable) {
        console.log('🤖 Stopping Python bot...');
        pythonBot.kill('SIGTERM');
        // Give the Python bot time to shut down gracefully
        await new Promise(resolve => setTimeout(resolve, 2000));
      } else {
        console.log('🤖 Python bot not running, skipping shutdown');
      }
      process.exit(0);
    });
    
  } catch (error) {
    console.error('❌ Critical error during server initialization:');
    console.error('Error:', error);
    console.error('Stack:', error instanceof Error ? error.stack : 'No stack trace available');
    console.error('🛑 Server startup failed');
    process.exit(1);
  }
})();
