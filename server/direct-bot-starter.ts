import { Client, GatewayIntentBits, Collection, REST, Routes } from 'discord.js';
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { pythonBotCommands } from './python-bot-commands';

export class DirectBotStarter {
  private static instance: DirectBotStarter;
  private client: Client | null = null;
  private isRunning = false;
  private statusData: any = {
    online: false,
    guilds: 0,
    users: 0,
    commands: 43, // Commands from actual Python bot files
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
          GatewayIntentBits.GuildMessageReactions,
          GatewayIntentBits.GuildVoiceStates,
          GatewayIntentBits.GuildPresences,
          GatewayIntentBits.GuildModeration,
          GatewayIntentBits.GuildWebhooks,
          GatewayIntentBits.GuildIntegrations,
          GatewayIntentBits.GuildInvites,
          GatewayIntentBits.DirectMessages,
          GatewayIntentBits.DirectMessageReactions,
          GatewayIntentBits.DirectMessageTyping,
          GatewayIntentBits.GuildScheduledEvents,
          GatewayIntentBits.AutoModerationConfiguration,
          GatewayIntentBits.AutoModerationExecution
        ]
      });

      // Set up event listeners
      this.client.once('ready', () => {
        console.log(`Bot is ready! Logged in as ${this.client!.user!.tag}`);
        this.isRunning = true;
        this.statusData.online = true;
        this.statusData.timestamp = new Date().toISOString();
        this.updateStatus();
      });

      this.client.on('guildCreate', () => {
        this.updateStatus();
      });

      this.client.on('guildDelete', () => {
        this.updateStatus();
      });

      // Login to Discord
      await this.client.login(token);

      // Register slash commands
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

      // Commands based on the actual Python bot files provided
      const commands = pythonBotCommands;

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
              { name: 'Moderation', value: '`/ban` `/kick` `/mute` `/unmute` `/warn` `/warnings` `/purge` `/purgebot` `/unban` `/banlist` `/mutelist` `/timeout` `/untimeout` `/slowmode` `/lock` `/unlock`', inline: false },
              { name: 'Utility', value: '`/userinfo` `/avatar` `/serverinfo` `/commands` `/embed` `/embed-help` `/embed-json`', inline: false },
              { name: 'Admin', value: '`/prefix` `/resetprefix` `/modrole` `/resetmodrole` `/logging` `/changelog` `/changelog-test` `/changelog-disable`', inline: false },
              { name: 'Tickets', value: '`/ticket` `/ticket-setup` `/ticket-panel` `/ticket-close` `/ticket-info` `/ticket-list` `/ticket-stats` `/ticket-cleanup` `/ticket-embed` `/ticket-enhanced` `/transcript`', inline: false },
            ],
            timestamp: new Date(),
            footer: { text: 'NexGuard Bot' }
          };
          await interaction.reply({ embeds: [helpEmbed] });
        } else {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure bot settings.');
        }
      });

    } catch (error) {
      console.error('Error registering slash commands:', error);
    }
  }

  public async stopBot(): Promise<boolean> {
    if (!this.isRunning || !this.client) return true;
    
    console.log('Stopping Discord bot...');
    this.client.destroy();
    this.client = null;
    this.isRunning = false;
    this.statusData.online = false;
    this.statusData.guilds = 0;
    this.statusData.users = 0;
    this.statusData.lastUpdated = new Date().toISOString();
    console.log('Bot stopped');
    return true;
  }

  public async restart(): Promise<boolean> {
    try {
      console.log('Restarting Discord bot...');
      await this.stopBot();
      // Wait a moment before starting again
      await new Promise(resolve => setTimeout(resolve, 1000));
      return await this.startBot();
    } catch (error) {
      console.error('Error restarting bot:', error);
      return false;
    }
  }

  public getStatus(): any {
    return this.statusData;
  }

  private updateStatus(): void {
    if (!this.client) return;
    
    this.statusData.online = this.isRunning;
    this.statusData.guilds = this.client.guilds.cache.size;
    this.statusData.users = this.client.users.cache.size;
    this.statusData.lastUpdated = new Date().toISOString();
    this.statusData.lastHeartbeat = new Date().toISOString();
    this.statusData.timestamp = new Date().toISOString();
  }
}

// Export singleton instance for backward compatibility
export const directBotStarter = DirectBotStarter.getInstance();