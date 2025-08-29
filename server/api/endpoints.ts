import { Router } from 'express';
import { z } from 'zod';

const router = Router();

// API Key validation middleware
const validateApiKey = (req: any, res: any, next: any) => {
  const apiKey = req.headers['x-api-key'] || req.query.api_key;
  
  // For development, allow without key. In production, validate against database
  if (process.env.NODE_ENV === 'production' && !apiKey) {
    return res.status(401).json({ 
      error: 'API key required',
      message: 'Include API key in X-API-Key header or api_key query parameter'
    });
  }
  
  next();
};

// Bot Statistics API
router.get('/v1/bot/stats', validateApiKey, async (req, res) => {
  try {
    // Get live bot status from your existing endpoint
    const response = await fetch('http://localhost:5000/api/bot/status');
    const botStatus = await response.json();
    
    res.json({
      success: true,
      data: {
        online: botStatus.isOnline,
        guilds: botStatus.guildsCount,
        users: botStatus.usersCount,
        uptime: botStatus.uptime,
        version: botStatus.version,
        latency: null, // Will be populated by bot when available
        commands: 62
      }
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: 'Failed to fetch bot statistics' 
    });
  }
});

// Server Information API
router.get('/v1/server/:guildId', validateApiKey, async (req, res) => {
  const guildIdSchema = z.string().regex(/^\d+$/, 'Invalid guild ID');
  
  try {
    const guildId = guildIdSchema.parse(req.params.guildId);
    
    // TODO: Implement guild data fetching from database
    res.json({
      success: true,
      data: {
        id: guildId,
        name: "Server Name",
        memberCount: 0,
        features: [],
        premiumTier: 0,
        joinedAt: new Date().toISOString()
      }
    });
  } catch (error) {
    res.status(400).json({ 
      success: false, 
      error: 'Invalid guild ID format' 
    });
  }
});

// Moderation Actions API
router.post('/v1/moderation/ban', validateApiKey, async (req, res) => {
  const banSchema = z.object({
    guildId: z.string(),
    userId: z.string(),
    reason: z.string().max(512),
    deleteMessageDays: z.number().min(0).max(7).optional()
  });

  try {
    const { guildId, userId, reason, deleteMessageDays } = banSchema.parse(req.body);
    
    // Send ban request to Discord bot via webhook
    const webhookResponse = await fetch('http://localhost:5001/api/bot/moderation/ban', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ guildId, userId, reason, deleteMessageDays })
    });
    
    if (webhookResponse.ok) {
      res.json({ 
        success: true, 
        message: 'Ban request sent to bot' 
      });
    } else {
      res.status(500).json({ 
        success: false, 
        error: 'Failed to execute ban' 
      });
    }
  } catch (error) {
    res.status(400).json({ 
      success: false, 
      error: 'Invalid request data' 
    });
  }
});

// Analytics API
router.get('/v1/analytics/:guildId', validateApiKey, async (req, res) => {
  const guildIdSchema = z.string().regex(/^\d+$/, 'Invalid guild ID');
  
  try {
    const guildId = guildIdSchema.parse(req.params.guildId);
    
    // TODO: Fetch analytics from database
    res.json({
      success: true,
      data: {
        messageCount: 0,
        activeUsers: 0,
        commandsUsed: 0,
        moderationActions: 0,
        ticketsCreated: 0
      }
    });
  } catch (error) {
    res.status(400).json({ 
      success: false, 
      error: 'Invalid guild ID format' 
    });
  }
});

// Performance Monitoring API
router.get('/v1/performance', validateApiKey, (req, res) => {
  const memoryUsage = process.memoryUsage();
  const cpuUsage = process.cpuUsage();
  
  res.json({
    success: true,
    data: {
      memory: {
        used: Math.round(memoryUsage.heapUsed / 1024 / 1024), // MB
        total: Math.round(memoryUsage.heapTotal / 1024 / 1024), // MB
        external: Math.round(memoryUsage.external / 1024 / 1024) // MB
      },
      cpu: {
        user: cpuUsage.user,
        system: cpuUsage.system
      },
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    }
  });
});

// Health Check API
router.get('/v1/health', (req, res) => {
  res.json({
    success: true,
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '2.5.1'
  });
});

export { router as apiEndpoints };