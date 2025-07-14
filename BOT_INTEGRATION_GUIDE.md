# Discord Bot Integration Guide

## Overview
This guide will help you connect your Discord bot to the NexGuard dashboard so it can fetch server configurations and manage settings in real-time.

## Prerequisites
- Your Discord bot is already created and has the token
- Bot ID: 1389775821794705429
- Website backend is running with the API endpoints

## Step 1: Install Required Dependencies

Add these to your Discord bot project:

```bash
# For Node.js bots
npm install axios dotenv

# For Python bots
pip install requests python-dotenv

# For other languages, use equivalent HTTP client libraries
```

## Step 2: Environment Variables

Add these to your bot's environment:

```env
# Your bot's token (you already have this)
DISCORD_BOT_TOKEN=your_bot_token_here

# Website API endpoint
NEXGUARD_API_URL=https://your-replit-domain.replit.app

# Alternative for local development
# NEXGUARD_API_URL=http://localhost:5000
```

## Step 3: Bot Integration Code Examples

### Node.js/JavaScript Example

```javascript
const axios = require('axios');

class NexGuardAPI {
    constructor() {
        this.baseURL = process.env.NEXGUARD_API_URL || 'https://your-domain.replit.app';
        this.token = process.env.DISCORD_BOT_TOKEN;
    }

    async getServerConfig(guildId) {
        try {
            const response = await axios.get(`${this.baseURL}/api/bot/servers/${guildId}/config`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching server config:', error.response?.data || error.message);
            return null;
        }
    }

    async getCustomCommands(guildId) {
        try {
            const response = await axios.get(`${this.baseURL}/api/bot/servers/${guildId}/commands`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching custom commands:', error.response?.data || error.message);
            return [];
        }
    }

    async createCustomCommand(guildId, name, response, createdBy) {
        try {
            const result = await axios.post(`${this.baseURL}/api/bot/servers/${guildId}/commands`, {
                name,
                response,
                createdBy
            }, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });
            return result.data;
        } catch (error) {
            console.error('Error creating custom command:', error.response?.data || error.message);
            return null;
        }
    }

    async logModerationAction(guildId, type, userId, moderatorId, reason, duration = null) {
        try {
            await axios.post(`${this.baseURL}/api/bot/servers/${guildId}/moderation/log`, {
                type,
                userId,
                moderatorId,
                reason,
                duration
            }, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });
        } catch (error) {
            console.error('Error logging moderation action:', error.response?.data || error.message);
        }
    }
}

// Usage in your bot
const nexguardAPI = new NexGuardAPI();

// Example: Load server configuration when bot joins a server
client.on('ready', async () => {
    console.log('Bot is ready!');
    
    // Load configurations for all servers
    for (const guild of client.guilds.cache.values()) {
        const config = await nexguardAPI.getServerConfig(guild.id);
        if (config) {
            console.log(`Loaded config for ${guild.name}:`, config);
        }
    }
});

// Example: Handle custom commands
client.on('messageCreate', async (message) => {
    if (message.author.bot) return;
    
    const commands = await nexguardAPI.getCustomCommands(message.guild.id);
    const customCommand = commands.find(cmd => message.content === `!${cmd.name}`);
    
    if (customCommand) {
        message.reply(customCommand.response);
    }
});
```

### Python Example

```python
import requests
import os
from typing import Optional, List, Dict

class NexGuardAPI:
    def __init__(self):
        self.base_url = os.getenv('NEXGUARD_API_URL', 'https://your-domain.replit.app')
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def get_server_config(self, guild_id: str) -> Optional[Dict]:
        try:
            response = requests.get(
                f'{self.base_url}/api/bot/servers/{guild_id}/config',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'Error fetching server config: {e}')
            return None
    
    def get_custom_commands(self, guild_id: str) -> List[Dict]:
        try:
            response = requests.get(
                f'{self.base_url}/api/bot/servers/{guild_id}/commands',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'Error fetching custom commands: {e}')
            return []
    
    def create_custom_command(self, guild_id: str, name: str, response: str, created_by: str) -> Optional[Dict]:
        try:
            result = requests.post(
                f'{self.base_url}/api/bot/servers/{guild_id}/commands',
                json={
                    'name': name,
                    'response': response,
                    'createdBy': created_by
                },
                headers=self.headers
            )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print(f'Error creating custom command: {e}')
            return None
    
    def log_moderation_action(self, guild_id: str, action_type: str, user_id: str, moderator_id: str, reason: str, duration: Optional[int] = None):
        try:
            requests.post(
                f'{self.base_url}/api/bot/servers/{guild_id}/moderation/log',
                json={
                    'type': action_type,
                    'userId': user_id,
                    'moderatorId': moderator_id,
                    'reason': reason,
                    'duration': duration
                },
                headers=self.headers
            )
        except requests.exceptions.RequestException as e:
            print(f'Error logging moderation action: {e}')

# Usage in your bot
nexguard_api = NexGuardAPI()

@bot.event
async def on_ready():
    print('Bot is ready!')
    
    # Load configurations for all servers
    for guild in bot.guilds:
        config = nexguard_api.get_server_config(str(guild.id))
        if config:
            print(f'Loaded config for {guild.name}: {config}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    commands = nexguard_api.get_custom_commands(str(message.guild.id))
    custom_command = next((cmd for cmd in commands if message.content == f"!{cmd['name']}"), None)
    
    if custom_command:
        await message.reply(custom_command['response'])
```

## Step 4: Integration Points

### 1. Server Configuration Loading
Load configuration when:
- Bot starts up
- Bot joins a new server
- Configuration is updated via dashboard

### 2. Custom Commands
- Load custom commands on startup
- Check for custom commands on each message
- Allow users to create commands via bot commands

### 3. Moderation Logging
Log actions for:
- Warnings, mutes, kicks, bans
- Automod actions
- Manual moderation actions

### 4. Real-time Updates (Optional)
Consider implementing webhooks or periodic polling to update configurations without restarting the bot.

## Step 5: Testing the Integration

1. Start your bot with the integration code
2. Check the console for configuration loading messages
3. Test custom commands creation and execution
4. Verify moderation logging works

## Step 6: Deployment Considerations

1. **Environment Variables**: Ensure all required variables are set in production
2. **Error Handling**: Implement proper error handling and fallbacks
3. **Rate Limiting**: Be mindful of API rate limits
4. **Caching**: Consider caching configurations to reduce API calls

## API Endpoints Reference

- `GET /api/bot/servers/{guildId}/config` - Get server configuration
- `GET /api/bot/servers/{guildId}/commands` - Get custom commands
- `POST /api/bot/servers/{guildId}/commands` - Create custom command
- `POST /api/bot/servers/{guildId}/moderation/log` - Log moderation action
- `POST /api/bot/servers/{guildId}/sync` - Sync server data

## Support

If you encounter issues:
1. Check your environment variables are correct
2. Verify the API endpoints are accessible
3. Check the console logs for detailed error messages
4. Ensure your bot token has the required permissions

Your dashboard is now ready to communicate with your Discord bot!