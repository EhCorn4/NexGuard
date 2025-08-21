import { Client, GatewayIntentBits, Collection, REST, Routes } from 'discord.js';
import { storage } from '../storage';
import { db } from '../db';
import { commands, guilds, botStatus } from '@shared/schema';
import { eq } from 'drizzle-orm';
import express from 'express';
import { ChangelogPublisher } from '../lib/changelogPublisher';

// Import command handlers
import { adminCommands } from './commands/admin';
import { moderationCommands } from './commands/moderation';
import { ticketCommands } from './commands/ticket';
import { utilityCommands } from './commands/utility';

class NexGuardBot {
  public client: Client;
  public commands: Collection<string, any>;
  private startTime: number;
  private changelogPublisher: ChangelogPublisher | null = null;
  private httpServer: express.Application;

  constructor() {
    this.client = new Client({
      intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildModeration,
        GatewayIntentBits.GuildVoiceStates,
      ],
    });

    this.commands = new Collection();
    this.startTime = Date.now();
    this.httpServer = express();
    this.setupEventHandlers();
    this.setupHTTPServer();
  }

  private setupEventHandlers() {
    this.client.once('ready', () => {
      console.log(`✅ NexGuard Bot is online as ${this.client.user?.tag}`);
      this.changelogPublisher = new ChangelogPublisher(this.client);
      console.log('📝 Changelog publisher initialized');
      this.updateBotStatus();
      this.registerCommands();
      
      // Update bot status every 30 seconds
      setInterval(() => this.updateBotStatus(), 30000);
    });

    this.client.on('guildCreate', async (guild) => {
      await this.handleGuildJoin(guild);
    });

    this.client.on('guildDelete', async (guild) => {
      await this.handleGuildLeave(guild);
    });

    this.client.on('guildMemberAdd', async (member) => {
      await this.handleWelcomeMessage(member);
    });

    this.client.on('interactionCreate', async (interaction) => {
      if (!interaction.isChatInputCommand()) return;

      const command = this.commands.get(interaction.commandName);
      if (!command) return;

      try {
        await command.execute(interaction);
      } catch (error) {
        console.error('Error executing command:', error);
        await interaction.reply({ 
          content: 'There was an error executing this command!', 
          ephemeral: true 
        });
      }
    });
  }

  private async registerCommands() {
    const allCommands = [
      ...adminCommands,
      ...moderationCommands,
      ...ticketCommands,
      ...utilityCommands,
    ];

    // Store commands in collection
    allCommands.forEach(command => {
      this.commands.set(command.data.name, command);
    });

    // Register slash commands with Discord
    const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN!);
    
    try {
      console.log('🔄 Refreshing slash commands...');
      
      // Clear existing commands first
      await rest.put(
        Routes.applicationCommands(this.client.user!.id),
        { body: [] }
      );
      console.log('🧹 Cleared existing commands');
      
      // Wait a moment before registering new commands
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Filter out duplicate commands by name
      const uniqueCommands = allCommands.filter((command, index, self) => 
        index === self.findIndex(c => c.data.name === command.data.name)
      );
      
      console.log(`📝 Registering ${uniqueCommands.length} unique commands...`);
      
      // Register new commands
      await rest.put(
        Routes.applicationCommands(this.client.user!.id),
        { body: uniqueCommands.map(cmd => cmd.data.toJSON()) }
      );
      console.log('✅ Slash commands registered successfully!');
    } catch (error) {
      console.error('Error registering slash commands:', error);
    }

    // Store commands in database
    await this.storeCommandsInDatabase(allCommands);
  }

  private async storeCommandsInDatabase(commandList: any[]) {
    for (const command of commandList) {
      try {
        await db.insert(commands).values({
          name: command.data.name,
          description: command.data.description,
          category: command.category,
          usage: command.usage || `/${command.data.name}`,
          permissions: command.permissions || [],
          enabled: true,
        }).onConflictDoUpdate({
          target: commands.name,
          set: {
            description: command.data.description,
            category: command.category,
            usage: command.usage || `/${command.data.name}`,
            permissions: command.permissions || [],
          }
        });
      } catch (error) {
        console.error(`Error storing command ${command.data.name}:`, error);
      }
    }
  }

  private async handleGuildJoin(guild: any) {
    try {
      await db.insert(guilds).values({
        id: guild.id,
        name: guild.name,
        memberCount: guild.memberCount,
        joinedAt: new Date(),
        updatedAt: new Date(),
      }).onConflictDoUpdate({
        target: guilds.id,
        set: {
          name: guild.name,
          memberCount: guild.memberCount,
          updatedAt: new Date(),
        }
      });
      
      console.log(`✅ Joined guild: ${guild.name} (${guild.id})`);
    } catch (error) {
      console.error('Error handling guild join:', error);
    }
  }

  private async handleGuildLeave(guild: any) {
    try {
      await db.delete(guilds).where(eq(guilds.id, guild.id));
      console.log(`❌ Left guild: ${guild.name} (${guild.id})`);
    } catch (error) {
      console.error('Error handling guild leave:', error);
    }
  }

  private async handleWelcomeMessage(member: any) {
    try {
      // Get guild settings from database
      const [guildData] = await db.select().from(guilds).where(eq(guilds.id, member.guild.id)).limit(1);
      if (!guildData || !guildData.welcomeEnabled) {
        return;
      }
      
      if (!guildData.welcomeChannelId) {
        return;
      }

      const channel = member.guild.channels.cache.get(guildData.welcomeChannelId);
      if (!channel) {
        return;
      }

      // Replace placeholders in welcome message
      let welcomeMessage = guildData.welcomeMessage || 'Welcome to {server}, {user}!';
      welcomeMessage = welcomeMessage
        .replace(/{user}/g, `<@${member.id}>`)
        .replace(/{server}/g, member.guild.name)
        .replace(/{member_count}/g, member.guild.memberCount.toString())
        .replace(/{username}/g, member.user.username)
        .replace(/{user_tag}/g, member.user.tag)
        .replace(/{user_id}/g, member.id)
        .replace(/{server_id}/g, member.guild.id)
        .replace(/{created_at}/g, member.user.createdAt.toDateString())
        .replace(/{joined_at}/g, member.joinedAt.toDateString());

      // Send welcome message
      const embed = {
        title: `Welcome to ${member.guild.name}!`,
        description: welcomeMessage,
        color: 0x00FF00,
        thumbnail: {
          url: member.user.displayAvatarURL({ dynamic: true })
        },
        fields: [
          {
            name: 'Account Created',
            value: `<t:${Math.floor(member.user.createdTimestamp / 1000)}:R>`,
            inline: true
          },
          {
            name: 'Member Count',
            value: member.guild.memberCount.toString(),
            inline: true
          }
        ],
        timestamp: new Date().toISOString(),
        footer: {
          text: `User ID: ${member.id}`
        }
      };

      // Send welcome message based on type
      if (guildData.welcomeEmbed) {
        await channel.send({ embeds: [embed] });
      } else {
        await channel.send(welcomeMessage);
      }

      console.log(`👋 Welcome message sent for ${member.user.tag} in ${member.guild.name}`);
    } catch (error) {
      console.error('Error sending welcome message:', error);
    }
  }

  private async updateBotStatus() {
    if (!this.client.user) return;

    const uptime = Date.now() - this.startTime;
    const guildsCount = this.client.guilds.cache.size;
    const usersCount = this.client.guilds.cache.reduce((acc, guild) => acc + guild.memberCount, 0);

    try {
      // Use storage interface instead of direct database calls
      await storage.updateBotStatus({
        isOnline: true,
        guildsCount,
        usersCount,
        uptime: this.formatUptime(uptime),
        version: '2.3.2',
        lastRestart: new Date(this.startTime),
      });
      
      console.log(`📊 Bot status updated: Online=true, Guilds=${guildsCount}, Users=${usersCount}`);
    } catch (error) {
      console.error('Error updating bot status:', error);
    }
  }

  private formatUptime(uptime: number): string {
    const seconds = Math.floor(uptime / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  }

  public async start() {
    try {
      await this.client.login(process.env.DISCORD_TOKEN);
    } catch (error) {
      console.error('❌ Failed to start bot:', error);
      // Update bot status to offline
      await db.insert(botStatus).values({
        id: 1,
        isOnline: false,
        updatedAt: new Date(),
      }).onConflictDoUpdate({
        target: botStatus.id,
        set: {
          isOnline: false,
          updatedAt: new Date(),
        }
      });
    }
  }

  private setupHTTPServer() {
    this.httpServer.use(express.json());
    
    // Publish latest changelog
    this.httpServer.post('/publish-changelog-latest', async (req, res) => {
      if (!this.changelogPublisher) {
        return res.status(503).json({
          error: 'Changelog publisher not initialized',
          message: 'Bot is not ready yet'
        });
      }

      try {
        const success = await this.changelogPublisher.publishLatestChangelog();
        if (success) {
          res.json({
            success: true,
            message: 'Latest changelog published successfully'
          });
        } else {
          res.status(404).json({
            error: 'No unpublished changelog found'
          });
        }
      } catch (error) {
        console.error('Error publishing latest changelog:', error);
        res.status(500).json({
          error: 'Failed to publish changelog',
          details: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    });

    // Publish specific version changelog
    this.httpServer.post('/publish-changelog-version', async (req, res) => {
      if (!this.changelogPublisher) {
        return res.status(503).json({
          error: 'Changelog publisher not initialized',
          message: 'Bot is not ready yet'
        });
      }

      const { version } = req.body;
      if (!version) {
        return res.status(400).json({
          error: 'Version is required'
        });
      }

      try {
        const success = await this.changelogPublisher.publishChangelogByVersion(version);
        if (success) {
          res.json({
            success: true,
            message: `Changelog v${version} published successfully`
          });
        } else {
          res.status(404).json({
            error: `Changelog for version ${version} not found`
          });
        }
      } catch (error) {
        console.error(`Error publishing changelog v${version}:`, error);
        res.status(500).json({
          error: 'Failed to publish changelog',
          details: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    });

    // Publish custom changelog
    this.httpServer.post('/publish-changelog-custom', async (req, res) => {
      if (!this.changelogPublisher) {
        return res.status(503).json({
          error: 'Changelog publisher not initialized',
          message: 'Bot is not ready yet'
        });
      }

      const { version, title, description, changes, type } = req.body;
      
      if (!version || !title || !description || !changes || !type) {
        return res.status(400).json({
          error: 'All fields are required',
          required: ['version', 'title', 'description', 'changes', 'type']
        });
      }

      try {
        const success = await this.changelogPublisher.publishCustomChangelog({
          version,
          title,
          description,
          changes,
          type
        });
        
        if (success) {
          res.json({
            success: true,
            message: `Custom changelog v${version} created and published successfully`
          });
        } else {
          res.status(500).json({
            error: 'Failed to create and publish custom changelog'
          });
        }
      } catch (error) {
        console.error('Error publishing custom changelog:', error);
        res.status(500).json({
          error: 'Failed to publish custom changelog',
          details: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    });

    // Health check endpoint
    this.httpServer.get('/health', (req, res) => {
      res.json({
        status: 'ok',
        bot: this.client.user?.tag || 'Not ready',
        changelogPublisher: this.changelogPublisher ? 'Ready' : 'Not ready'
      });
    });

    const PORT = process.env.BOT_HTTP_PORT || 3001;
    this.httpServer.listen(PORT, () => {
      console.log(`📡 Bot HTTP server listening on port ${PORT}`);
    });
  }

  public async stop() {
    console.log('🛑 Stopping NexGuard Bot...');
    
    // Update bot status to offline
    await storage.updateBotStatus({
      isOnline: false,
      guildsCount: 0,
      usersCount: 0,
      uptime: '0s',
      version: '2.3.2',
      lastRestart: new Date(),
    });
    
    this.client.destroy();
  }
}

export { NexGuardBot };