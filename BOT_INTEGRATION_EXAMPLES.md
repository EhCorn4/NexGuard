# Bot Integration - Code Examples

## Database Connection Setup

### For Discord.js Bot
```javascript
// bot/database.js
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

class BotDatabase {
  async getServerConfig(guildId) {
    const result = await pool.query(
      'SELECT * FROM server_configs WHERE guild_id = $1',
      [guildId]
    );
    return result.rows[0];
  }
  
  async getCustomCommands(guildId) {
    const result = await pool.query(
      'SELECT * FROM custom_commands WHERE guild_id = $1',
      [guildId]
    );
    return result.rows;
  }
  
  async updateServerConfig(guildId, config) {
    await pool.query(
      `INSERT INTO server_configs (guild_id, moderation_enabled, welcome_enabled, welcome_channel, welcome_message)
       VALUES ($1, $2, $3, $4, $5)
       ON CONFLICT (guild_id) DO UPDATE SET
       moderation_enabled = $2, welcome_enabled = $3, welcome_channel = $4, welcome_message = $5`,
      [guildId, config.moderation_enabled, config.welcome_enabled, config.welcome_channel, config.welcome_message]
    );
  }
}

module.exports = { BotDatabase };
```

### For Discord.py Bot
```python
# bot/database.py
import asyncpg
import os

class BotDatabase:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(os.getenv('DATABASE_URL'))
    
    async def get_server_config(self, guild_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                'SELECT * FROM server_configs WHERE guild_id = $1',
                str(guild_id)
            )
    
    async def get_custom_commands(self, guild_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                'SELECT * FROM custom_commands WHERE guild_id = $1',
                str(guild_id)
            )
```

## Bot Implementation Examples

### Welcome Message System
```javascript
// bot/events/guildMemberAdd.js
const { BotDatabase } = require('../database');
const db = new BotDatabase();

module.exports = {
  name: 'guildMemberAdd',
  async execute(member) {
    const config = await db.getServerConfig(member.guild.id);
    
    if (!config || !config.welcome_enabled || !config.welcome_channel) {
      return;
    }
    
    const channel = member.guild.channels.cache.get(config.welcome_channel);
    if (!channel) return;
    
    const message = config.welcome_message || `Welcome to ${member.guild.name}, ${member.user}!`;
    await channel.send(message);
  }
};
```

### Custom Commands System
```javascript
// bot/events/messageCreate.js
const { BotDatabase } = require('../database');
const db = new BotDatabase();

module.exports = {
  name: 'messageCreate',
  async execute(message) {
    if (message.author.bot) return;
    
    const config = await db.getServerConfig(message.guild.id);
    if (!config || !config.custom_commands_enabled) return;
    
    const prefix = config.prefix || '!';
    if (!message.content.startsWith(prefix)) return;
    
    const commandName = message.content.slice(prefix.length).split(' ')[0];
    const customCommands = await db.getCustomCommands(message.guild.id);
    
    const command = customCommands.find(cmd => cmd.name === commandName);
    if (command) {
      await message.reply(command.response);
    }
  }
};
```

### Moderation System
```javascript
// bot/events/messageCreate.js (moderation part)
module.exports = {
  name: 'messageCreate',
  async execute(message) {
    if (message.author.bot) return;
    
    const config = await db.getServerConfig(message.guild.id);
    if (!config || !config.moderation_enabled) return;
    
    // Auto-moderation
    if (config.auto_mod_enabled) {
      if (config.profanity_filter && containsProfanity(message.content)) {
        await message.delete();
        await message.author.send('Your message was deleted for containing inappropriate content.');
      }
      
      if (config.spam_protection && isSpam(message)) {
        await message.delete();
        await message.author.timeout(5 * 60 * 1000, 'Spam protection');
      }
    }
  }
};
```

## Configuration Loading System

### Startup Configuration Loading
```javascript
// bot/index.js
const { Client, GatewayIntentBits } = require('discord.js');
const { BotDatabase } = require('./database');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers
  ]
});

const db = new BotDatabase();
const serverConfigs = new Map();

// Load all server configurations on startup
client.once('ready', async () => {
  console.log('Bot is ready!');
  await loadAllConfigurations();
});

async function loadAllConfigurations() {
  for (const guild of client.guilds.cache.values()) {
    const config = await db.getServerConfig(guild.id);
    if (config) {
      serverConfigs.set(guild.id, config);
    }
  }
}

// Refresh configurations periodically
setInterval(loadAllConfigurations, 30000); // Every 30 seconds
```

## API Integration (Alternative Method)

### REST API Calls from Bot
```javascript
// bot/api-client.js
const axios = require('axios');

class DashboardAPI {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }
  
  async getServerConfig(guildId) {
    try {
      const response = await axios.get(`${this.baseURL}/api/server-config/${guildId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch server config:', error);
      return null;
    }
  }
  
  async getCustomCommands(guildId) {
    try {
      const response = await axios.get(`${this.baseURL}/api/custom-commands/${guildId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch custom commands:', error);
      return [];
    }
  }
}

module.exports = { DashboardAPI };
```

## Environment Variables

Your bot needs these environment variables:
```env
DATABASE_URL=your_postgresql_connection_string
DISCORD_TOKEN=your_bot_token
DASHBOARD_URL=https://your-dashboard-url.com (if using API method)
```

## Quick Start Steps

1. **Set up database connection** in your bot using the same `DATABASE_URL`
2. **Create the database class** with methods to read server configs
3. **Update your bot's event handlers** to use the configuration data
4. **Test with welcome messages** as the simplest feature
5. **Add moderation features** that respect the dashboard settings
6. **Implement custom commands** that sync with the dashboard

The dashboard already has all the database tables and API endpoints set up, so your bot just needs to connect to the same database and read the configuration data.

Would you like me to help you implement any specific part of this integration?