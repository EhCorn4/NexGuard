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
    commands: 0,
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
        {
          name: 'ping',
          description: 'Replies with Pong!',
        },
        {
          name: 'help',
          description: 'Shows help information',
        },
        {
          name: 'status',
          description: 'Shows bot status',
        }
      ];

      const rest = new REST({ version: '10' }).setToken(token);

      console.log('Started refreshing application (/) commands.');
      await rest.put(
        Routes.applicationCommands(clientId),
        { body: commands },
      );

      console.log('Successfully reloaded application (/) commands.');

      // Setup command handlers
      this.client?.on('interactionCreate', async (interaction) => {
        if (!interaction.isChatInputCommand()) return;

        const { commandName } = interaction;

        if (commandName === 'ping') {
          await interaction.reply('Pong!');
        } else if (commandName === 'help') {
          await interaction.reply('NexGuard Bot - Visit https://nexguard.tech for more information!');
        } else if (commandName === 'status') {
          const status = this.getStatus();
          await interaction.reply(`Bot Status: ${status.online ? 'Online' : 'Offline'}\nServers: ${status.guilds}\nUsers: ${status.users}`);
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
      commands: 3, // ping, help, status
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
        commands: 3, // ping, help, status
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