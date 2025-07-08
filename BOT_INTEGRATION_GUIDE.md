# Connecting Your NexGuard Bot to the Dashboard

## Overview
To connect your actual Discord bot to this dashboard, you need to establish communication between the bot and the website's backend. This enables real-time configuration updates and status monitoring.

## Integration Methods

### Method 1: Database Integration (Recommended)
Both your bot and the dashboard use the same PostgreSQL database to store and retrieve configuration data.

**Bot Side Setup:**
1. Configure your bot to connect to the same PostgreSQL database
2. Use the same database schema (from `shared/schema.ts`)
3. Update bot settings by reading from the `server_configs` table
4. Store custom commands in the `custom_commands` table

**Database Connection for Bot:**
```javascript
// In your bot's code
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL // Same as dashboard
});

// Read server configuration
async function getServerConfig(guildId) {
  const result = await pool.query(
    'SELECT * FROM server_configs WHERE guild_id = $1',
    [guildId]
  );
  return result.rows[0];
}

// Update configuration when changed via dashboard
async function updateBotSettings(guildId) {
  const config = await getServerConfig(guildId);
  // Apply configuration to your bot
  // Update welcome messages, moderation settings, etc.
}
```

### Method 2: REST API Integration
Create API endpoints that your bot can call to get configuration updates.

**Dashboard API Endpoints (already implemented):**
- `GET /api/server-config/:guildId` - Get server configuration
- `PUT /api/server-config/:guildId` - Update server configuration
- `GET /api/custom-commands/:guildId` - Get custom commands
- `POST /api/custom-commands` - Create custom command

**Bot Side Implementation:**
```javascript
// In your bot's code
async function fetchServerConfig(guildId) {
  const response = await fetch(`${DASHBOARD_URL}/api/server-config/${guildId}`);
  return await response.json();
}

// Listen for configuration changes
setInterval(async () => {
  for (const guild of bot.guilds.cache.values()) {
    const config = await fetchServerConfig(guild.id);
    await applyConfiguration(guild.id, config);
  }
}, 30000); // Check every 30 seconds
```

### Method 3: WebSocket Integration (Real-time)
For real-time updates when users change settings on the dashboard.

## Current Database Schema
The dashboard uses these tables for bot configuration:

**server_configs table:**
- `guild_id` - Discord server ID
- `moderation_enabled` - Enable/disable moderation
- `auto_mod_enabled` - Auto-moderation settings
- `welcome_enabled` - Welcome message settings
- `welcome_channel` - Welcome channel ID
- `welcome_message` - Custom welcome message
- `economy_enabled` - Economy system toggle
- `daily_reward` - Daily reward amount
- And many more configuration options...

**custom_commands table:**
- `guild_id` - Discord server ID
- `name` - Command name
- `response` - Command response
- `created_by` - User who created it

## Implementation Steps

### Step 1: Database Connection
1. Use the same `DATABASE_URL` environment variable in your bot
2. Connect to the PostgreSQL database
3. Query the `server_configs` table for each guild

### Step 2: Configuration Loading
```javascript
// Example bot integration
class NexGuardBot {
  constructor() {
    this.configs = new Map();
    this.loadConfigurations();
  }

  async loadConfigurations() {
    const result = await pool.query('SELECT * FROM server_configs');
    for (const config of result.rows) {
      this.configs.set(config.guild_id, config);
    }
  }

  async onMessage(message) {
    const config = this.configs.get(message.guild.id);
    if (!config) return;

    // Apply moderation settings
    if (config.moderation_enabled && config.auto_mod_enabled) {
      await this.moderateMessage(message, config);
    }

    // Check custom commands
    if (config.custom_commands_enabled) {
      await this.handleCustomCommands(message, config);
    }
  }

  async onGuildMemberAdd(member) {
    const config = this.configs.get(member.guild.id);
    if (config?.welcome_enabled && config.welcome_channel) {
      const channel = member.guild.channels.cache.get(config.welcome_channel);
      if (channel) {
        await channel.send(config.welcome_message || 'Welcome to the server!');
      }
    }
  }
}
```

### Step 3: Real-time Updates
Listen for configuration changes and update bot behavior immediately:

```javascript
// Check for configuration updates
setInterval(async () => {
  await this.loadConfigurations();
}, 10000); // Check every 10 seconds

// Or use database triggers/notifications for real-time updates
```

## Testing the Integration

1. **Update Settings**: Change settings on the dashboard
2. **Verify Database**: Check that changes are saved to the database
3. **Bot Response**: Ensure your bot picks up the changes
4. **Test Features**: Test welcome messages, moderation, custom commands

## Security Considerations

- Use the same authentication for bot API calls
- Validate all configuration data before applying
- Implement rate limiting for API calls
- Use environment variables for sensitive data

## Next Steps

1. Set up database connection in your bot
2. Implement configuration loading system
3. Test with a simple feature (like welcome messages)
4. Gradually add more complex features
5. Set up real-time updates for instant configuration changes

Would you like me to help you implement any specific part of this integration?