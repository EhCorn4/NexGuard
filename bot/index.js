import { Client, GatewayIntentBits, Collection } from 'discord.js';
import { WebSocketServer } from 'ws';
import cron from 'node-cron';
import fetch from 'node-fetch';

// Initialize Discord client
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildModeration,
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildPresences
  ]
});

// Bot status tracking
let botStatus = {
  online: false,
  guilds: 0,
  users: 0,
  uptime: 0,
  commands: 0,
  lastHeartbeat: new Date(),
  version: '2.3.2'
};

// API integration
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:5000';

class NexGuardAPI {
  constructor() {
    this.headers = {
      'Authorization': `Bearer ${process.env.DISCORD_BOT_TOKEN}`,
      'Content-Type': 'application/json'
    };
  }

  async getServerConfig(guildId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/bot/servers/${guildId}/config`, {
        headers: this.headers
      });
      return response.ok ? await response.json() : null;
    } catch (error) {
      console.error('Config fetch error:', error);
      return null;
    }
  }

  async getCustomCommands(guildId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/bot/servers/${guildId}/commands`, {
        headers: this.headers
      });
      return response.ok ? await response.json() : [];
    } catch (error) {
      console.error('Commands fetch error:', error);
      return [];
    }
  }

  async logModeration(guildId, actionType, userId, moderatorId, reason) {
    try {
      await fetch(`${API_BASE_URL}/api/bot/servers/${guildId}/moderation/log`, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify({
          type: actionType,
          userId,
          moderatorId,
          reason
        })
      });
    } catch (error) {
      console.error('Moderation log error:', error);
    }
  }

  async updateBotStatus(status) {
    try {
      await fetch(`${API_BASE_URL}/api/bot/status`, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(status)
      });
    } catch (error) {
      console.error('Status update error:', error);
    }
  }
}

const nexguardAPI = new NexGuardAPI();

// Bot events
client.once('ready', async () => {
  console.log(`✅ ${client.user.tag} is online!`);
  
  botStatus.online = true;
  botStatus.guilds = client.guilds.cache.size;
  botStatus.users = client.users.cache.size;
  botStatus.uptime = Date.now();
  botStatus.lastHeartbeat = new Date();

  // Update bot status every 30 seconds
  setInterval(async () => {
    botStatus.guilds = client.guilds.cache.size;
    botStatus.users = client.users.cache.size;
    botStatus.lastHeartbeat = new Date();
    await nexguardAPI.updateBotStatus(botStatus);
  }, 30000);

  // Load configurations for all servers
  for (const guild of client.guilds.cache.values()) {
    const config = await nexguardAPI.getServerConfig(guild.id);
    if (config) {
      console.log(`✅ Config loaded for ${guild.name}`);
    }
  }
});

client.on('messageCreate', async (message) => {
  if (message.author.bot) return;

  // Handle custom commands
  if (message.content.startsWith('!')) {
    const commandName = message.content.slice(1).split(' ')[0];
    const commands = await nexguardAPI.getCustomCommands(message.guild.id);
    
    const customCommand = commands.find(cmd => cmd.name === commandName);
    if (customCommand) {
      await message.reply(customCommand.response);
      botStatus.commands++;
      return;
    }
  }

  // Basic moderation example
  const config = await nexguardAPI.getServerConfig(message.guild.id);
  if (config?.profanityFilter) {
    const badWords = ['spam', 'scam']; // Example filter
    if (badWords.some(word => message.content.toLowerCase().includes(word))) {
      await message.delete();
      await nexguardAPI.logModeration(
        message.guild.id,
        'auto_delete',
        message.author.id,
        client.user.id,
        'Profanity filter triggered'
      );
    }
  }
});

client.on('guildCreate', (guild) => {
  console.log(`✅ Added to new guild: ${guild.name}`);
  botStatus.guilds = client.guilds.cache.size;
});

client.on('guildDelete', (guild) => {
  console.log(`❌ Removed from guild: ${guild.name}`);
  botStatus.guilds = client.guilds.cache.size;
});

// Error handling
client.on('error', (error) => {
  console.error('Discord client error:', error);
  botStatus.online = false;
});

// WebSocket server for real-time bot status
function setupWebSocket(server) {
  const wss = new WebSocketServer({ server, path: '/bot-status' });
  
  wss.on('connection', (ws) => {
    console.log('Bot status WebSocket connected');
    
    // Send current status immediately
    ws.send(JSON.stringify({
      type: 'status',
      data: botStatus
    }));
    
    // Send periodic updates
    const interval = setInterval(() => {
      if (ws.readyState === ws.OPEN) {
        ws.send(JSON.stringify({
          type: 'status',
          data: botStatus
        }));
      }
    }, 5000);
    
    ws.on('close', () => {
      clearInterval(interval);
      console.log('Bot status WebSocket disconnected');
    });
  });
}

// Start the bot
export async function startBot(server) {
  try {
    if (!process.env.DISCORD_BOT_TOKEN) {
      console.error('❌ DISCORD_BOT_TOKEN is required');
      return;
    }
    
    // Setup WebSocket for status updates
    setupWebSocket(server);
    
    // Start Discord bot
    await client.login(process.env.DISCORD_BOT_TOKEN);
    
    console.log('🚀 NexGuard Bot started successfully');
    return client;
  } catch (error) {
    console.error('❌ Failed to start bot:', error);
    botStatus.online = false;
  }
}

// Export bot status getter
export function getBotStatus() {
  return botStatus;
}

export { client };