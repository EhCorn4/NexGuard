# Replit Discord Bot Integration - Simplified Guide

## Overview
Since you're using Replit for your bot, the integration is much simpler! Both your website and bot can share the same environment and database.

## Quick Setup for Replit Bots

### 1. Add Dependencies
In your bot's Replit project, add to your `requirements.txt` (Python) or `package.json` (Node.js):

**For Python:**
```txt
requests
python-dotenv
```

**For Node.js:**
```json
"dependencies": {
  "axios": "^1.6.0",
  "dotenv": "^16.0.0"
}
```

### 2. Environment Variables
Your bot already has access to these Replit Secrets:
- `DISCORD_BOT_TOKEN` (already set)
- `DISCORD_CLIENT_ID` (already set)
- `DISCORD_CLIENT_SECRET` (already set)

Add this new secret in your bot's Replit project:
- `NEXGUARD_API_URL` = `https://your-website-domain.replit.app`

### 3. Simple Integration Code

**For Python Discord.py Bot:**
```python
import requests
import os
import discord
from discord.ext import commands

# NexGuard API Integration
class NexGuardAPI:
    def __init__(self):
        self.base_url = os.getenv('NEXGUARD_API_URL', 'https://your-website-domain.replit.app')
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def get_server_config(self, guild_id):
        try:
            response = requests.get(f'{self.base_url}/api/bot/servers/{guild_id}/config', headers=self.headers)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f'Config fetch error: {e}')
            return None
    
    def get_custom_commands(self, guild_id):
        try:
            response = requests.get(f'{self.base_url}/api/bot/servers/{guild_id}/commands', headers=self.headers)
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f'Commands fetch error: {e}')
            return []
    
    def log_moderation(self, guild_id, action_type, user_id, moderator_id, reason):
        try:
            requests.post(f'{self.base_url}/api/bot/servers/{guild_id}/moderation/log', 
                         json={'type': action_type, 'userId': user_id, 'moderatorId': moderator_id, 'reason': reason},
                         headers=self.headers)
        except Exception as e:
            print(f'Moderation log error: {e}')

# Initialize
nexguard = NexGuardAPI()
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'{bot.user} is connected!')
    
    # Load configs for all servers
    for guild in bot.guilds:
        config = nexguard.get_server_config(str(guild.id))
        if config:
            print(f'Loaded config for {guild.name}: Moderation={config.get("moderationEnabled", False)}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Check for custom commands
    commands = nexguard.get_custom_commands(str(message.guild.id))
    for cmd in commands:
        if message.content == f'!{cmd["name"]}':
            await message.reply(cmd["response"])
            return
    
    await bot.process_commands(message)

# Example moderation command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    # Log to NexGuard dashboard
    nexguard.log_moderation(str(ctx.guild.id), 'warn', str(member.id), str(ctx.author.id), reason)
    
    await ctx.send(f'{member.mention} has been warned for: {reason}')

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
```

**For Node.js Discord.js Bot:**
```javascript
const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');
require('dotenv').config();

// NexGuard API Integration
class NexGuardAPI {
    constructor() {
        this.baseURL = process.env.NEXGUARD_API_URL || 'https://your-website-domain.replit.app';
        this.token = process.env.DISCORD_BOT_TOKEN;
        this.headers = {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    async getServerConfig(guildId) {
        try {
            const response = await axios.get(`${this.baseURL}/api/bot/servers/${guildId}/config`, { headers: this.headers });
            return response.data;
        } catch (error) {
            console.error('Config fetch error:', error.message);
            return null;
        }
    }

    async getCustomCommands(guildId) {
        try {
            const response = await axios.get(`${this.baseURL}/api/bot/servers/${guildId}/commands`, { headers: this.headers });
            return response.data;
        } catch (error) {
            console.error('Commands fetch error:', error.message);
            return [];
        }
    }

    async logModeration(guildId, type, userId, moderatorId, reason) {
        try {
            await axios.post(`${this.baseURL}/api/bot/servers/${guildId}/moderation/log`, {
                type, userId, moderatorId, reason
            }, { headers: this.headers });
        } catch (error) {
            console.error('Moderation log error:', error.message);
        }
    }
}

// Initialize
const nexguard = new NexGuardAPI();
const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent] });

client.once('ready', async () => {
    console.log(`${client.user.tag} is online!`);
    
    // Load configs for all servers
    for (const guild of client.guilds.cache.values()) {
        const config = await nexguard.getServerConfig(guild.id);
        if (config) {
            console.log(`Loaded config for ${guild.name}: Moderation=${config.moderationEnabled}`);
        }
    }
});

client.on('messageCreate', async (message) => {
    if (message.author.bot) return;
    
    // Check for custom commands
    const commands = await nexguard.getCustomCommands(message.guild.id);
    const customCommand = commands.find(cmd => message.content === `!${cmd.name}`);
    
    if (customCommand) {
        message.reply(customCommand.response);
        return;
    }
    
    // Example warn command
    if (message.content.startsWith('!warn')) {
        if (!message.member.permissions.has('MANAGE_MESSAGES')) return;
        
        const args = message.content.split(' ');
        const user = message.mentions.users.first();
        const reason = args.slice(2).join(' ') || 'No reason provided';
        
        if (user) {
            await nexguard.logModeration(message.guild.id, 'warn', user.id, message.author.id, reason);
            message.reply(`${user} has been warned for: ${reason}`);
        }
    }
});

client.login(process.env.DISCORD_BOT_TOKEN);
```

## 4. Testing the Integration

1. **Start your bot** with the new integration code
2. **Check the console** - you should see config loading messages
3. **Test custom commands** - create one in the dashboard, then use it in Discord
4. **Test moderation logging** - use a warn command and check if it appears in logs

## 5. Replit-Specific Benefits

- **Shared Environment**: Both projects can use the same database
- **Easy Deployment**: Both website and bot deploy automatically
- **Environment Variables**: Secrets are managed centrally
- **Real-time Updates**: Changes sync instantly

## 6. Next Steps

1. **Copy the integration code** into your bot's main file
2. **Update the `NEXGUARD_API_URL`** to match your website domain
3. **Test the connection** by running your bot
4. **Create custom commands** in the dashboard and test them in Discord

## 7. Advanced Features You Can Add

- **Auto-reload configs** when dashboard changes are made
- **Slash commands** that sync with the dashboard
- **Real-time moderation logs** displayed in Discord
- **Server stats** that update the dashboard

Your bot will now be fully connected to the NexGuard dashboard! The integration handles all the API communication automatically.