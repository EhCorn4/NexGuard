import { Client, GatewayIntentBits, Collection, REST, Routes } from 'discord.js';
import { storage } from '../storage';
import { db } from '../db';
import { commands, guilds } from '@shared/schema';

// Import command handlers
import { adminCommands } from './commands/admin';
import { moderationCommands } from './commands/moderation';
import { ticketCommands } from './commands/ticket';
import { utilityCommands } from './commands/utility';

class NexGuardBot {
  public client: Client;
  public commands: Collection<string, any>;
  private startTime: number;

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
    this.setupEventHandlers();
  }

  private setupEventHandlers() {
    this.client.once('ready', () => {
      console.log(`✅ NexGuard Bot is online as ${this.client.user?.tag}`);
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
      await rest.put(
        Routes.applicationCommands(this.client.user!.id),
        { body: allCommands.map(cmd => cmd.data.toJSON()) }
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
      // Get welcome settings from database
      const settings = await storage.getGuildSettings(member.guild.id);
      const welcomeSettings = settings.welcome || {};
      
      if (!welcomeSettings.enabled || !welcomeSettings.channelId) {
        return;
      }

      const channel = member.guild.channels.cache.get(welcomeSettings.channelId);
      if (!channel) {
        return;
      }

      // Replace placeholders in welcome message
      let welcomeMessage = welcomeSettings.message || 'Welcome to {server}, {user}!';
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
      if (welcomeSettings.type === 'embed') {
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

  public async stop() {
    console.log('🛑 Stopping NexGuard Bot...');
    
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

    this.client.destroy();
  }
}

export { NexGuardBot };