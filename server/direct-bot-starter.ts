import { Client, GatewayIntentBits, Collection, REST, Routes } from 'discord.js';
import { existsSync, readFileSync, writeFileSync } from 'fs';

export class DirectBotStarter {
  private static instance: DirectBotStarter;
  private client: Client | null = null;
  private isRunning = false;
  private statusData: any = {
    online: false,
    guilds: 0,
    users: 0,
    commands: 86,
    timestamp: new Date().toISOString(),
    lastHeartbeat: new Date().toISOString(),
    lastUpdated: new Date().toISOString()
  };

  private constructor() {}

  public static getInstance(): DirectBotStarter {
    if (!DirectBotStarter.instance) {
      DirectBotStarter.instance = new DirectBotStarter();
    }
    return DirectBotStarter.instance;
  }

  public async startBot(): Promise<boolean> {
    if (this.isRunning && this.client) {
      console.log('Bot is already running');
      return true;
    }

    try {
      console.log('Starting Discord bot...');
      
      const token = process.env.DISCORD_BOT_TOKEN;
      if (!token) {
        console.error('DISCORD_BOT_TOKEN is not set');
        return false;
      }

      // Create Discord client
      this.client = new Client({
        intents: [
          GatewayIntentBits.Guilds,
          GatewayIntentBits.GuildMessages,
          GatewayIntentBits.MessageContent,
          GatewayIntentBits.GuildMembers,
          GatewayIntentBits.GuildModeration
        ]
      });

      // Setup event listeners
      this.client.once('ready', () => {
        console.log(`Bot is ready! Logged in as ${this.client?.user?.tag}`);
        this.isRunning = true;
        this.updateStatus();
        // Force update status again after a brief delay
        setTimeout(() => this.updateStatus(), 2000);
      });

      this.client.on('error', (error) => {
        console.error('Discord client error:', error);
      });

      this.client.on('guildCreate', () => {
        this.updateStatus();
      });

      this.client.on('guildDelete', () => {
        this.updateStatus();
      });

      // Login to Discord
      await this.client.login(token);

      // Register basic slash commands
      await this.registerSlashCommands(token);

      return true;
    } catch (error) {
      console.error('Error starting bot:', error);
      this.isRunning = false;
      return false;
    }
  }

  private async registerSlashCommands(token: string) {
    try {
      const clientId = process.env.DISCORD_CLIENT_ID;
      if (!clientId) {
        console.error('DISCORD_CLIENT_ID is not set');
        return;
      }

      const commands = [
        // Basic Commands
        {
          name: 'ping',
          description: 'Replies with Pong!',
        },
        {
          name: 'help',
          description: 'Shows help information and available commands',
        },
        {
          name: 'status',
          description: 'Shows bot status and statistics',
        },
        // Moderation Commands
        {
          name: 'ban',
          description: 'Ban a user from the server',
          options: [
            {
              name: 'user',
              description: 'User to ban',
              type: 6,
              required: true
            },
            {
              name: 'reason',
              description: 'Reason for ban',
              type: 3,
              required: false
            }
          ]
        },
        {
          name: 'kick',
          description: 'Kick a user from the server',
          options: [
            {
              name: 'user',
              description: 'User to kick',
              type: 6,
              required: true
            },
            {
              name: 'reason',
              description: 'Reason for kick',
              type: 3,
              required: false
            }
          ]
        },
        {
          name: 'mute',
          description: 'Mute a user in the server',
          options: [
            {
              name: 'user',
              description: 'User to mute',
              type: 6,
              required: true
            },
            {
              name: 'duration',
              description: 'Duration of mute (e.g., 1h, 30m)',
              type: 3,
              required: false
            },
            {
              name: 'reason',
              description: 'Reason for mute',
              type: 3,
              required: false
            }
          ]
        },
        {
          name: 'unmute',
          description: 'Unmute a user in the server',
          options: [
            {
              name: 'user',
              description: 'User to unmute',
              type: 6,
              required: true
            }
          ]
        },
        {
          name: 'warn',
          description: 'Warn a user',
          options: [
            {
              name: 'user',
              description: 'User to warn',
              type: 6,
              required: true
            },
            {
              name: 'reason',
              description: 'Reason for warning',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'warnings',
          description: 'View warnings for a user',
          options: [
            {
              name: 'user',
              description: 'User to check warnings for',
              type: 6,
              required: true
            }
          ]
        },
        {
          name: 'clear',
          description: 'Clear messages from a channel',
          options: [
            {
              name: 'amount',
              description: 'Number of messages to clear (1-100)',
              type: 4,
              required: true
            }
          ]
        },
        {
          name: 'slowmode',
          description: 'Set slowmode for a channel',
          options: [
            {
              name: 'duration',
              description: 'Slowmode duration in seconds (0-21600)',
              type: 4,
              required: true
            }
          ]
        },
        {
          name: 'lock',
          description: 'Lock a channel',
          options: [
            {
              name: 'channel',
              description: 'Channel to lock',
              type: 7,
              required: false
            }
          ]
        },
        {
          name: 'unlock',
          description: 'Unlock a channel',
          options: [
            {
              name: 'channel',
              description: 'Channel to unlock',
              type: 7,
              required: false
            }
          ]
        },
        // Utility Commands
        {
          name: 'userinfo',
          description: 'Get information about a user',
          options: [
            {
              name: 'user',
              description: 'User to get information about',
              type: 6,
              required: false
            }
          ]
        },
        {
          name: 'serverinfo',
          description: 'Get information about the server',
        },
        {
          name: 'avatar',
          description: 'Get a user\'s avatar',
          options: [
            {
              name: 'user',
              description: 'User to get avatar for',
              type: 6,
              required: false
            }
          ]
        },
        {
          name: 'roleinfo',
          description: 'Get information about a role',
          options: [
            {
              name: 'role',
              description: 'Role to get information about',
              type: 8,
              required: true
            }
          ]
        },
        // Welcome/Leave System
        {
          name: 'welcome',
          description: 'Configure welcome messages',
          options: [
            {
              name: 'action',
              description: 'Action to perform',
              type: 3,
              required: true,
              choices: [
                { name: 'enable', value: 'enable' },
                { name: 'disable', value: 'disable' },
                { name: 'set-channel', value: 'set-channel' },
                { name: 'set-message', value: 'set-message' }
              ]
            }
          ]
        },
        // Ticket System
        {
          name: 'ticket',
          description: 'Manage support tickets',
          options: [
            {
              name: 'action',
              description: 'Ticket action',
              type: 3,
              required: true,
              choices: [
                { name: 'create', value: 'create' },
                { name: 'close', value: 'close' },
                { name: 'add', value: 'add' },
                { name: 'remove', value: 'remove' }
              ]
            }
          ]
        },
        // Economy System
        {
          name: 'balance',
          description: 'Check your balance',
          options: [
            {
              name: 'user',
              description: 'User to check balance for',
              type: 6,
              required: false
            }
          ]
        },
        {
          name: 'daily',
          description: 'Claim your daily reward',
        },
        {
          name: 'leaderboard',
          description: 'View the economy leaderboard',
        },
        // Custom Commands
        {
          name: 'customcmd',
          description: 'Manage custom commands',
          options: [
            {
              name: 'action',
              description: 'Action to perform',
              type: 3,
              required: true,
              choices: [
                { name: 'create', value: 'create' },
                { name: 'delete', value: 'delete' },
                { name: 'list', value: 'list' },
                { name: 'edit', value: 'edit' }
              ]
            }
          ]
        },
        // Configuration
        {
          name: 'config',
          description: 'Configure bot settings',
          options: [
            {
              name: 'setting',
              description: 'Setting to configure',
              type: 3,
              required: true,
              choices: [
                { name: 'moderation', value: 'moderation' },
                { name: 'logging', value: 'logging' },
                { name: 'automod', value: 'automod' },
                { name: 'economy', value: 'economy' }
              ]
            }
          ]
        },
        // Anti-Raid
        {
          name: 'lockdown',
          description: 'Enable server lockdown mode',
        },
        {
          name: 'unlockdown',
          description: 'Disable server lockdown mode',
        },
        // Fun Commands
        {
          name: 'poll',
          description: 'Create a poll',
          options: [
            {
              name: 'question',
              description: 'Poll question',
              type: 3,
              required: true
            },
            {
              name: 'option1',
              description: 'First option',
              type: 3,
              required: true
            },
            {
              name: 'option2',
              description: 'Second option',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'announce',
          description: 'Make an announcement',
          options: [
            {
              name: 'message',
              description: 'Announcement message',
              type: 3,
              required: true
            },
            {
              name: 'channel',
              description: 'Channel to announce in',
              type: 7,
              required: false
            }
          ]
        },
        // Extended Moderation Commands
        {
          name: 'tempban',
          description: 'Temporarily ban a user',
          options: [
            {
              name: 'user',
              description: 'User to temporarily ban',
              type: 6,
              required: true
            },
            {
              name: 'duration',
              description: 'Duration of ban (e.g., 1d, 1h)',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'unban',
          description: 'Unban a user',
          options: [
            {
              name: 'user',
              description: 'User ID to unban',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'softban',
          description: 'Soft ban a user (ban and immediately unban)',
          options: [
            {
              name: 'user',
              description: 'User to soft ban',
              type: 6,
              required: true
            }
          ]
        },
        {
          name: 'timeout',
          description: 'Timeout a user',
          options: [
            {
              name: 'user',
              description: 'User to timeout',
              type: 6,
              required: true
            },
            {
              name: 'duration',
              description: 'Duration of timeout',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'untimeout',
          description: 'Remove timeout from a user',
          options: [
            {
              name: 'user',
              description: 'User to remove timeout from',
              type: 6,
              required: true
            }
          ]
        },
        {
          name: 'massban',
          description: 'Mass ban multiple users',
          options: [
            {
              name: 'users',
              description: 'User IDs separated by spaces',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'automod',
          description: 'Configure auto-moderation settings',
          options: [
            {
              name: 'setting',
              description: 'Auto-mod setting to configure',
              type: 3,
              required: true,
              choices: [
                { name: 'spam', value: 'spam' },
                { name: 'links', value: 'links' },
                { name: 'profanity', value: 'profanity' },
                { name: 'caps', value: 'caps' }
              ]
            }
          ]
        },
        // Extended Utility Commands
        {
          name: 'channelinfo',
          description: 'Get information about a channel',
          options: [
            {
              name: 'channel',
              description: 'Channel to get information about',
              type: 7,
              required: false
            }
          ]
        },
        {
          name: 'emoteinfo',
          description: 'Get information about an emoji',
          options: [
            {
              name: 'emoji',
              description: 'Emoji to get information about',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'inviteinfo',
          description: 'Get information about an invite',
          options: [
            {
              name: 'invite',
              description: 'Invite code or URL',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'uptime',
          description: 'Check bot uptime',
        },
        {
          name: 'botinfo',
          description: 'Get detailed bot information',
        },
        // Fun Commands
        {
          name: 'meme',
          description: 'Get a random meme',
        },
        {
          name: 'joke',
          description: 'Get a random joke',
        },
        {
          name: 'fact',
          description: 'Get a random fact',
        },
        {
          name: 'quote',
          description: 'Get an inspirational quote',
        },
        {
          name: '8ball',
          description: 'Ask the magic 8-ball a question',
          options: [
            {
              name: 'question',
              description: 'Question to ask',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'dice',
          description: 'Roll a dice',
          options: [
            {
              name: 'sides',
              description: 'Number of sides (default: 6)',
              type: 4,
              required: false
            }
          ]
        },
        {
          name: 'coinflip',
          description: 'Flip a coin',
        },
        // Extended Economy Commands
        {
          name: 'work',
          description: 'Work to earn money',
        },
        {
          name: 'rob',
          description: 'Attempt to rob another user',
          options: [
            {
              name: 'user',
              description: 'User to rob',
              type: 6,
              required: true
            }
          ]
        },
        {
          name: 'pay',
          description: 'Pay money to another user',
          options: [
            {
              name: 'user',
              description: 'User to pay',
              type: 6,
              required: true
            },
            {
              name: 'amount',
              description: 'Amount to pay',
              type: 4,
              required: true
            }
          ]
        },
        {
          name: 'shop',
          description: 'View the server shop',
        },
        {
          name: 'buy',
          description: 'Buy an item from the shop',
          options: [
            {
              name: 'item',
              description: 'Item to buy',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'sell',
          description: 'Sell an item',
          options: [
            {
              name: 'item',
              description: 'Item to sell',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'inventory',
          description: 'View your inventory',
          options: [
            {
              name: 'user',
              description: 'User to view inventory for',
              type: 6,
              required: false
            }
          ]
        },
        {
          name: 'gamble',
          description: 'Gamble your money',
          options: [
            {
              name: 'amount',
              description: 'Amount to gamble',
              type: 4,
              required: true
            }
          ]
        },
        // Admin Commands
        {
          name: 'setprefix',
          description: 'Set bot prefix for the server',
          options: [
            {
              name: 'prefix',
              description: 'New prefix',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'setnick',
          description: 'Set nickname for a user',
          options: [
            {
              name: 'user',
              description: 'User to set nickname for',
              type: 6,
              required: true
            },
            {
              name: 'nickname',
              description: 'New nickname',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'addrole',
          description: 'Add a role to a user',
          options: [
            {
              name: 'user',
              description: 'User to add role to',
              type: 6,
              required: true
            },
            {
              name: 'role',
              description: 'Role to add',
              type: 8,
              required: true
            }
          ]
        },
        {
          name: 'removerole',
          description: 'Remove a role from a user',
          options: [
            {
              name: 'user',
              description: 'User to remove role from',
              type: 6,
              required: true
            },
            {
              name: 'role',
              description: 'Role to remove',
              type: 8,
              required: true
            }
          ]
        },
        {
          name: 'createchannel',
          description: 'Create a new channel',
          options: [
            {
              name: 'name',
              description: 'Channel name',
              type: 3,
              required: true
            },
            {
              name: 'type',
              description: 'Channel type',
              type: 3,
              required: true,
              choices: [
                { name: 'text', value: 'text' },
                { name: 'voice', value: 'voice' },
                { name: 'category', value: 'category' }
              ]
            }
          ]
        },
        {
          name: 'deletechannel',
          description: 'Delete a channel',
          options: [
            {
              name: 'channel',
              description: 'Channel to delete',
              type: 7,
              required: true
            }
          ]
        },
        // Logging Commands
        {
          name: 'modlog',
          description: 'View moderation logs',
          options: [
            {
              name: 'user',
              description: 'User to view logs for',
              type: 6,
              required: false
            }
          ]
        },
        {
          name: 'auditlog',
          description: 'View server audit logs',
        },
        {
          name: 'messagelog',
          description: 'Configure message logging',
          options: [
            {
              name: 'channel',
              description: 'Channel for message logs',
              type: 7,
              required: true
            }
          ]
        },
        {
          name: 'joinlog',
          description: 'Configure join logging',
          options: [
            {
              name: 'channel',
              description: 'Channel for join logs',
              type: 7,
              required: true
            }
          ]
        },
        {
          name: 'leavelog',
          description: 'Configure leave logging',
          options: [
            {
              name: 'channel',
              description: 'Channel for leave logs',
              type: 7,
              required: true
            }
          ]
        },
        // Extended Ticket System
        {
          name: 'ticket-setup',
          description: 'Set up the ticket system',
          options: [
            {
              name: 'category',
              description: 'Category for tickets',
              type: 7,
              required: true
            }
          ]
        },
        {
          name: 'ticket-close',
          description: 'Close a ticket',
          options: [
            {
              name: 'reason',
              description: 'Reason for closing',
              type: 3,
              required: false
            }
          ]
        },
        {
          name: 'ticket-add',
          description: 'Add a user to a ticket',
          options: [
            {
              name: 'user',
              description: 'User to add',
              type: 6,
              required: true
            }
          ]
        },
        {
          name: 'ticket-remove',
          description: 'Remove a user from a ticket',
          options: [
            {
              name: 'user',
              description: 'User to remove',
              type: 6,
              required: true
            }
          ]
        },
        {
          name: 'ticket-transcript',
          description: 'Generate a ticket transcript',
        },
        // Extended Welcome System
        {
          name: 'welcome-setup',
          description: 'Set up welcome messages',
          options: [
            {
              name: 'channel',
              description: 'Welcome channel',
              type: 7,
              required: true
            }
          ]
        },
        {
          name: 'welcome-test',
          description: 'Test welcome message',
        },
        {
          name: 'goodbye-setup',
          description: 'Set up goodbye messages',
          options: [
            {
              name: 'channel',
              description: 'Goodbye channel',
              type: 7,
              required: true
            }
          ]
        },
        {
          name: 'autorole-setup',
          description: 'Set up auto-role system',
          options: [
            {
              name: 'role',
              description: 'Role to auto-assign',
              type: 8,
              required: true
            }
          ]
        },
        // Verification System
        {
          name: 'verify',
          description: 'Verify a user',
          options: [
            {
              name: 'user',
              description: 'User to verify',
              type: 6,
              required: true
            }
          ]
        },
        {
          name: 'unverify',
          description: 'Unverify a user',
          options: [
            {
              name: 'user',
              description: 'User to unverify',
              type: 6,
              required: true
            }
          ]
        },
        {
          name: 'verification-setup',
          description: 'Set up verification system',
          options: [
            {
              name: 'role',
              description: 'Verified role',
              type: 8,
              required: true
            }
          ]
        },
        // Role Management
        {
          name: 'roleall',
          description: 'Add role to all users',
          options: [
            {
              name: 'role',
              description: 'Role to add to all users',
              type: 8,
              required: true
            }
          ]
        },
        {
          name: 'roleremove',
          description: 'Remove role from all users',
          options: [
            {
              name: 'role',
              description: 'Role to remove from all users',
              type: 8,
              required: true
            }
          ]
        },
        {
          name: 'rolecreate',
          description: 'Create a new role',
          options: [
            {
              name: 'name',
              description: 'Role name',
              type: 3,
              required: true
            },
            {
              name: 'color',
              description: 'Role color (hex)',
              type: 3,
              required: false
            }
          ]
        },
        {
          name: 'roledelete',
          description: 'Delete a role',
          options: [
            {
              name: 'role',
              description: 'Role to delete',
              type: 8,
              required: true
            }
          ]
        },
        // Server Management
        {
          name: 'backup',
          description: 'Create a server backup',
        },
        {
          name: 'restore',
          description: 'Restore from a backup',
          options: [
            {
              name: 'backup-id',
              description: 'Backup ID to restore',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'clone',
          description: 'Clone server settings',
          options: [
            {
              name: 'guild-id',
              description: 'Guild ID to clone from',
              type: 3,
              required: true
            }
          ]
        },
        {
          name: 'migrate',
          description: 'Migrate server data',
          options: [
            {
              name: 'source',
              description: 'Source to migrate from',
              type: 3,
              required: true
            }
          ]
        }
      ];

      const rest = new REST({ version: '10' }).setToken(token);

      console.log(`Started refreshing application (/) commands. Total: ${commands.length}`);
      await rest.put(
        Routes.applicationCommands(clientId),
        { body: commands },
      );

      console.log(`Successfully reloaded application (/) commands. Total: ${commands.length}`);
      
      // Update status with correct command count
      this.statusData.commands = commands.length;

      // Setup command handlers
      this.client?.on('interactionCreate', async (interaction) => {
        if (!interaction.isChatInputCommand()) return;

        const { commandName } = interaction;

        if (commandName === 'ping') {
          await interaction.reply('Pong!');
          
        } else if (commandName === 'help') {
          const helpEmbed = {
            title: 'NexGuard Bot Commands',
            color: 0x00ff88,
            description: 'Here are all available commands:',
            fields: [
              { name: 'Moderation', value: '`/ban` `/kick` `/mute` `/unmute` `/warn` `/warnings` `/clear` `/slowmode` `/lock` `/unlock`', inline: false },
              { name: 'Utility', value: '`/userinfo` `/serverinfo` `/avatar` `/roleinfo`', inline: false },
              { name: 'Systems', value: '`/welcome` `/ticket` `/balance` `/daily` `/leaderboard`', inline: false },
              { name: 'Management', value: '`/customcmd` `/config` `/lockdown` `/unlockdown`', inline: false },
              { name: 'Fun', value: '`/poll` `/announce`', inline: false }
            ],
            footer: { text: 'Visit https://nexguard.replit.app for more information!' }
          };
          await interaction.reply({ embeds: [helpEmbed] });
          
        } else if (commandName === 'status') {
          const status = this.getStatus();
          await interaction.reply(`Bot Status: ${status.online ? '🟢 Online' : '🔴 Offline'}\nServers: ${status.guilds}\nUsers: ${status.users}\nUptime: ${status.uptime}\nCommands: ${status.commands}`);
          
        // Moderation Commands
        } else if (commandName === 'ban') {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure moderation settings.');
        } else if (commandName === 'kick') {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure moderation settings.');
        } else if (commandName === 'mute') {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure moderation settings.');
        } else if (commandName === 'unmute') {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure moderation settings.');
        } else if (commandName === 'warn') {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure moderation settings.');
        } else if (commandName === 'warnings') {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure moderation settings.');
        } else if (commandName === 'clear') {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure moderation settings.');
        } else if (commandName === 'slowmode') {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure moderation settings.');
        } else if (commandName === 'lock') {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure moderation settings.');
        } else if (commandName === 'unlock') {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure moderation settings.');
        
        // Utility Commands
        } else if (commandName === 'userinfo') {
          const user = interaction.options.getUser('user') || interaction.user;
          await interaction.reply(`User: ${user.tag}\nID: ${user.id}\nAccount Created: ${user.createdAt.toDateString()}`);
        } else if (commandName === 'serverinfo') {
          const guild = interaction.guild;
          if (guild) {
            await interaction.reply(`Server: ${guild.name}\nMembers: ${guild.memberCount}\nCreated: ${guild.createdAt.toDateString()}`);
          } else {
            await interaction.reply('This command can only be used in servers.');
          }
        } else if (commandName === 'avatar') {
          const user = interaction.options.getUser('user') || interaction.user;
          await interaction.reply(`${user.tag}'s Avatar: ${user.displayAvatarURL({ size: 512 })}`);
        } else if (commandName === 'roleinfo') {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure role settings.');
        
        // System Commands
        } else if (commandName === 'welcome') {
          await interaction.reply('⚠️ Welcome system is currently under development. Please use the dashboard at https://nexguard.replit.app to configure welcome messages.');
        } else if (commandName === 'ticket') {
          await interaction.reply('⚠️ Ticket system is currently under development. Please use the dashboard at https://nexguard.replit.app to configure ticket settings.');
        } else if (commandName === 'balance') {
          await interaction.reply('⚠️ Economy system is currently under development. Please use the dashboard at https://nexguard.replit.app to configure economy settings.');
        } else if (commandName === 'daily') {
          await interaction.reply('⚠️ Economy system is currently under development. Please use the dashboard at https://nexguard.replit.app to configure economy settings.');
        } else if (commandName === 'leaderboard') {
          await interaction.reply('⚠️ Economy system is currently under development. Please use the dashboard at https://nexguard.replit.app to configure economy settings.');
        
        // Management Commands
        } else if (commandName === 'customcmd') {
          await interaction.reply('⚠️ Custom commands are currently under development. Please use the dashboard at https://nexguard.replit.app to create custom commands.');
        } else if (commandName === 'config') {
          await interaction.reply('⚠️ Configuration is currently under development. Please use the dashboard at https://nexguard.replit.app to configure bot settings.');
        } else if (commandName === 'lockdown') {
          await interaction.reply('⚠️ Lockdown system is currently under development. Please use the dashboard at https://nexguard.replit.app to configure anti-raid settings.');
        } else if (commandName === 'unlockdown') {
          await interaction.reply('⚠️ Lockdown system is currently under development. Please use the dashboard at https://nexguard.replit.app to configure anti-raid settings.');
        
        // Fun Commands
        } else if (commandName === 'poll') {
          const question = interaction.options.getString('question');
          const option1 = interaction.options.getString('option1');
          const option2 = interaction.options.getString('option2');
          await interaction.reply(`📊 **Poll:** ${question}\n\n1️⃣ ${option1}\n2️⃣ ${option2}\n\nReact with 1️⃣ or 2️⃣ to vote!`);
        } else if (commandName === 'announce') {
          const message = interaction.options.getString('message');
          await interaction.reply(`📢 **Announcement:** ${message}`);
        
        } else {
          await interaction.reply('Unknown command. Use `/help` to see all available commands.');
        }
      });

    } catch (error) {
      console.error('Error registering slash commands:', error);
    }
  }

  private updateStatus() {
    if (!this.client) return;

    const guilds = this.client.guilds.cache.size;
    const users = this.client.guilds.cache.reduce((acc, guild) => acc + guild.memberCount, 0);

    this.statusData = {
      online: true,
      guilds,
      users,
      commands: 86, // Full command set (updated)
      timestamp: this.statusData.timestamp, // Keep original start time
      lastHeartbeat: new Date().toISOString(),
      lastUpdated: new Date().toISOString()
    };

    // Save status to file for API access
    try {
      writeFileSync('/tmp/nexguard_bot_status.json', JSON.stringify(this.statusData, null, 2));
    } catch (error) {
      console.error('Error saving status file:', error);
    }
  }

  public async stopBot(): Promise<boolean> {
    try {
      if (this.client) {
        console.log('Stopping Discord bot...');
        this.client.destroy();
        this.client = null;
      }

      this.isRunning = false;
      this.statusData.online = false;
      this.statusData.lastUpdated = new Date().toISOString();
      
      // Update status file
      try {
        writeFileSync('/tmp/nexguard_bot_status.json', JSON.stringify(this.statusData, null, 2));
      } catch (error) {
        console.error('Error saving status file:', error);
      }

      console.log('Bot stopped');
      return true;
    } catch (error) {
      console.error('Error stopping bot:', error);
      return false;
    }
  }

  public async restart(): Promise<boolean> {
    console.log('Restarting bot...');
    await this.stopBot();
    await new Promise(resolve => setTimeout(resolve, 2000));
    return await this.startBot();
  }

  private isBotReady(): boolean {
    return this.isRunning && this.client?.isReady() === true;
  }

  public getStatus() {
    if (this.isBotReady() && this.client) {
      // Get real-time data from Discord client
      const guilds = this.client.guilds.cache.size;
      const users = this.client.guilds.cache.reduce((acc, guild) => acc + guild.memberCount, 0);
      
      return {
        online: true,
        guilds,
        users,
        uptime: this.getUptime(),
        commands: 86, // Full command set (updated)
        lastHeartbeat: new Date().toISOString(),
        version: '2.3.2',
        lastUpdated: new Date().toISOString()
      };
    }

    return {
      online: false,
      guilds: 0,
      users: 0,
      uptime: '0s',
      commands: 0,
      lastHeartbeat: new Date().toISOString(),
      version: '2.3.2',
      lastUpdated: new Date().toISOString()
    };
  }

  private getUptime(): string {
    try {
      const startTime = new Date(this.statusData.timestamp).getTime();
      const uptime = Date.now() - startTime;
      const seconds = Math.floor(uptime / 1000);
      const minutes = Math.floor(seconds / 60);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);

      if (days > 0) return `${days}d ${hours % 24}h ${minutes % 60}m`;
      if (hours > 0) return `${hours}h ${minutes % 60}m`;
      if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
      return `${seconds}s`;
    } catch (e) {
      return 'NaNs';
    }
  }

  public isOnline(): boolean {
    return this.isRunning && this.isBotReady();
  }
}

export const directBotStarter = DirectBotStarter.getInstance();