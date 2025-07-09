# Discord Bot Integration Setup

## Bot Requirements
Your Discord bot needs these capabilities to work with the website:

### Required Environment Variables
```env
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here
```

### Bot Permissions Needed
- Administrator (recommended) OR specific permissions:
  - Manage Messages
  - Manage Roles
  - Manage Channels
  - Read Message History
  - Send Messages
  - Use Slash Commands

## API Endpoints for Your Bot

### 1. Get Server Configuration
```
GET /api/bot/servers/{guild_id}/config
Headers: Authorization: Bearer {BOT_TOKEN}
```

### 2. Get Custom Commands
```
GET /api/bot/servers/{guild_id}/commands
Headers: Authorization: Bearer {BOT_TOKEN}
```

### 3. Log Moderation Action
```
POST /api/bot/servers/{guild_id}/moderation/log
Headers: Authorization: Bearer {BOT_TOKEN}
Body: {
  type: "warn" | "ban" | "kick" | "timeout",
  userId: string,
  moderatorId: string,
  reason: string,
  duration?: string
}
```

## Integration Code Examples

### Node.js (discord.js) Example
```javascript
const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages]
});

// Get server config from website
async function getServerConfig(guildId) {
  try {
    const response = await axios.get(`http://localhost:5000/api/bot/servers/${guildId}/config`, {
      headers: {
        'Authorization': `Bearer ${process.env.DISCORD_BOT_TOKEN}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch server config:', error);
    return null;
  }
}

// Example: Check if moderation is enabled
client.on('messageCreate', async (message) => {
  if (message.author.bot) return;
  
  const config = await getServerConfig(message.guild.id);
  if (config?.moderationEnabled) {
    // Apply moderation rules
    if (config.spamProtection) {
      // Check for spam
    }
    if (config.profanityFilter) {
      // Check for profanity
    }
  }
});
```

### Python (discord.py) Example
```python
import discord
import aiohttp
import os

client = discord.Client()

async def get_server_config(guild_id):
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization': f'Bearer {os.getenv("DISCORD_BOT_TOKEN")}'}
        async with session.get(f'http://localhost:5000/api/bot/servers/{guild_id}/config', headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
    return None

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    config = await get_server_config(message.guild.id)
    if config and config.get('moderationEnabled'):
        # Apply moderation rules
        pass
```

## Next Steps
1. Provide your bot token and client ID
2. I'll create the secure bot API endpoints
3. You integrate the API calls into your bot
4. Test the integration

## Security Notes
- Bot tokens are stored as environment variables
- API endpoints require bot authentication
- All communication should use HTTPS in production