import { SlashCommandBuilder, PermissionFlagsBits } from 'discord.js';
import { db } from '../../db';
import { changelogs, commands } from '@shared/schema';
import { desc, eq } from 'drizzle-orm';

export const utilityCommands = [
  {
    data: new SlashCommandBuilder()
      .setName('ping')
      .setDescription('Check the bot\'s latency'),
    category: 'utility',
    permissions: [],
    usage: '/ping',
    async execute(interaction: any) {
      const sent = await interaction.reply({ content: 'Pinging...', fetchReply: true });
      const latency = sent.createdTimestamp - interaction.createdTimestamp;
      
      await interaction.editReply({
        content: `🏓 Pong! Latency: ${latency}ms | API Latency: ${Math.round(interaction.client.ws.ping)}ms`
      });
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('userinfo')
      .setDescription('Get information about a user')
      .addUserOption(option =>
        option.setName('user')
          .setDescription('The user to get info about')
          .setRequired(false)
      ),
    category: 'utility',
    permissions: [],
    usage: '/userinfo [user]',
    async execute(interaction: any) {
      const user = interaction.options.getUser('user') || interaction.user;
      const member = await interaction.guild.members.fetch(user.id);
      
      const embed = {
        title: `👤 User Information - ${user.tag}`,
        color: 0x00FFFF,
        thumbnail: {
          url: user.displayAvatarURL(),
        },
        fields: [
          { name: 'Username', value: user.tag, inline: true },
          { name: 'ID', value: user.id, inline: true },
          { name: 'Bot', value: user.bot ? 'Yes' : 'No', inline: true },
          { name: 'Account Created', value: user.createdAt.toDateString(), inline: true },
          { name: 'Joined Server', value: member.joinedAt?.toDateString() || 'Unknown', inline: true },
          { name: 'Roles', value: member.roles.cache.filter(role => role.name !== '@everyone').map(role => role.name).join(', ') || 'None', inline: false },
        ],
        footer: {
          text: 'User Information',
        },
        timestamp: new Date().toISOString(),
      };
      
      await interaction.reply({ embeds: [embed] });
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('serverinfo')
      .setDescription('Get information about the server'),
    category: 'utility',
    permissions: [],
    usage: '/serverinfo',
    async execute(interaction: any) {
      const guild = interaction.guild;
      const owner = await guild.fetchOwner();
      
      const embed = {
        title: `🏠 Server Information - ${guild.name}`,
        color: 0x00FFFF,
        thumbnail: {
          url: guild.iconURL() || '',
        },
        fields: [
          { name: 'Server Name', value: guild.name, inline: true },
          { name: 'Server ID', value: guild.id, inline: true },
          { name: 'Owner', value: owner.user.tag, inline: true },
          { name: 'Member Count', value: guild.memberCount.toString(), inline: true },
          { name: 'Created', value: guild.createdAt.toDateString(), inline: true },
          { name: 'Verification Level', value: guild.verificationLevel.toString(), inline: true },
          { name: 'Channels', value: guild.channels.cache.size.toString(), inline: true },
          { name: 'Roles', value: guild.roles.cache.size.toString(), inline: true },
          { name: 'Emojis', value: guild.emojis.cache.size.toString(), inline: true },
        ],
        footer: {
          text: 'Server Information',
        },
        timestamp: new Date().toISOString(),
      };
      
      await interaction.reply({ embeds: [embed] });
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('avatar')
      .setDescription('Get a user\'s avatar')
      .addUserOption(option =>
        option.setName('user')
          .setDescription('The user to get avatar from')
          .setRequired(false)
      ),
    category: 'utility',
    permissions: [],
    usage: '/avatar [user]',
    async execute(interaction: any) {
      const user = interaction.options.getUser('user') || interaction.user;
      
      const embed = {
        title: `🖼️ Avatar - ${user.tag}`,
        color: 0x00FFFF,
        image: {
          url: user.displayAvatarURL({ size: 1024 }),
        },
        footer: {
          text: 'Avatar Image',
        },
        timestamp: new Date().toISOString(),
      };
      
      await interaction.reply({ embeds: [embed] });
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('changelog')
      .setDescription('View the bot\'s changelog')
      .addStringOption(option =>
        option.setName('version')
          .setDescription('Specific version to view')
          .setRequired(false)
      ),
    category: 'utility',
    permissions: [],
    usage: '/changelog [version]',
    async execute(interaction: any) {
      const version = interaction.options.getString('version');
      
      try {
        let changelogData;
        
        if (version) {
          // Get specific version
          [changelogData] = await db.select()
            .from(changelogs)
            .where(eq(changelogs.version, version))
            .limit(1);
        } else {
          // Get latest version
          [changelogData] = await db.select()
            .from(changelogs)
            .orderBy(desc(changelogs.releaseDate))
            .limit(1);
        }
        
        if (!changelogData) {
          await interaction.reply({
            content: '❌ Changelog not found.',
            ephemeral: true
          });
          return;
        }
        
        const typeEmoji = {
          major: '🚀',
          minor: '✨',
          patch: '🐛',
          hotfix: '🔥'
        }[changelogData.type] || '📝';
        
        const embed = {
          title: `${typeEmoji} Changelog - Version ${changelogData.version}`,
          description: changelogData.description,
          color: 0x00FFFF,
          fields: [
            {
              name: 'Changes',
              value: changelogData.changes.map((change: string) => `• ${change}`).join('\n'),
              inline: false
            },
            {
              name: 'Type',
              value: changelogData.type.toUpperCase(),
              inline: true
            },
            {
              name: 'Release Date',
              value: new Date(changelogData.releaseDate).toLocaleDateString(),
              inline: true
            },
          ],
          footer: {
            text: `NexGuard Bot v${changelogData.version}`,
          },
          timestamp: new Date(changelogData.releaseDate).toISOString(),
        };
        
        await interaction.reply({ embeds: [embed] });
      } catch (error) {
        console.error('Error fetching changelog:', error);
        await interaction.reply({
          content: '❌ Failed to fetch changelog.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('uptime')
      .setDescription('Check the bot\'s uptime'),
    category: 'utility',
    permissions: [],
    usage: '/uptime',
    async execute(interaction: any) {
      const uptime = process.uptime();
      const days = Math.floor(uptime / 86400);
      const hours = Math.floor((uptime % 86400) / 3600);
      const minutes = Math.floor((uptime % 3600) / 60);
      const seconds = Math.floor(uptime % 60);
      
      const embed = {
        title: '⏰ Bot Uptime',
        color: 0x00FFFF,
        fields: [
          {
            name: 'Current Uptime',
            value: `${days}d ${hours}h ${minutes}m ${seconds}s`,
            inline: true
          },
          {
            name: 'Status',
            value: '🟢 Online',
            inline: true
          },
        ],
        footer: {
          text: 'Bot Uptime',
        },
        timestamp: new Date().toISOString(),
      };
      
      await interaction.reply({ embeds: [embed] });
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('help')
      .setDescription('Get help with bot commands')
      .addStringOption(option =>
        option.setName('command')
          .setDescription('Get help with a specific command')
          .setRequired(false)
      ),
    category: 'utility',
    permissions: [],
    usage: '/help [command]',
    async execute(interaction: any) {
      const commandName = interaction.options.getString('command');
      
      if (commandName) {
        // Get help for specific command
        const command = interaction.client.commands.get(commandName);
        if (!command) {
          await interaction.reply({
            content: '❌ Command not found.',
            ephemeral: true
          });
          return;
        }
        
        const embed = {
          title: `📖 Help - /${commandName}`,
          color: 0x00FFFF,
          fields: [
            { name: 'Description', value: command.data.description, inline: false },
            { name: 'Usage', value: command.usage || `/${commandName}`, inline: false },
            { name: 'Category', value: command.category, inline: true },
            { name: 'Permissions', value: command.permissions?.join(', ') || 'None', inline: true },
          ],
        };
        
        await interaction.reply({ embeds: [embed] });
      } else {
        // General help
        const embed = {
          title: '📚 NexGuard Bot - Help',
          description: 'Here are all available commands organized by category:',
          color: 0x00FFFF,
          fields: [
            {
              name: '⚙️ Admin Commands',
              value: '`/setprefix` - Set command prefix\n`/configure` - Configure server settings\n`/serverstats` - View server statistics\n`/announcement` - Send announcements',
              inline: false
            },
            {
              name: '🛡️ Moderation Commands',
              value: '`/warn` - Warn a user\n`/mute` - Mute a user\n`/kick` - Kick a user\n`/ban` - Ban a user\n`/unban` - Unban a user\n`/clear` - Clear messages',
              inline: false
            },
            {
              name: '🎫 Ticket Commands',
              value: '`/ticket` - Create a support ticket\n`/closeticket` - Close a ticket\n`/ticketinfo` - Get ticket information\n`/tickets` - List all tickets',
              inline: false
            },
            {
              name: '🔧 Utility Commands',
              value: '`/ping` - Check bot latency\n`/userinfo` - Get user information\n`/serverinfo` - Get server information\n`/avatar` - Get user avatar\n`/changelog` - View bot changelog\n`/uptime` - Check bot uptime\n`/ai` - Ask the AI assistant\n`/commands` - List all bot commands\n`/embed` - Create custom embeds\n`/botstats` - View detailed bot statistics',
              inline: false
            },
          ],
          footer: {
            text: 'Use /help <command> for detailed information about a specific command',
          },
        };
        
        await interaction.reply({ embeds: [embed] });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('ai')
      .setDescription('Ask the AI assistant a question')
      .addStringOption(option =>
        option.setName('question')
          .setDescription('Your question for the AI assistant')
          .setRequired(true)
      ),
    category: 'utility',
    permissions: [],
    usage: '/ai <question>',
    async execute(interaction: any) {
      const question = interaction.options.getString('question');
      
      await interaction.deferReply();
      
      try {
        // Simple AI responses for demonstration
        const responses = [
          "I'm here to help! While I can't provide real-time AI responses in this demo, I can help with bot commands and server management.",
          "That's an interesting question! For now, I can assist with NexGuard bot features and Discord server management.",
          "I'm designed to help with moderation and server management. For complex queries, consider using specialized AI services.",
          "Thanks for asking! I'm focused on helping with Discord server administration and bot functionality.",
          "I appreciate your question! My primary function is to assist with server moderation and bot management."
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        
        const embed = {
          title: '🤖 AI Assistant',
          color: 0x00FFFF,
          fields: [
            { name: 'Your Question', value: question, inline: false },
            { name: 'AI Response', value: randomResponse, inline: false },
          ],
          footer: {
            text: 'AI Assistant Response',
          },
          timestamp: new Date().toISOString(),
        };
        
        await interaction.editReply({ embeds: [embed] });
      } catch (error) {
        console.error('Error with AI assistant:', error);
        await interaction.editReply({
          content: '❌ Failed to process AI request. Please try again.',
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('commands')
      .setDescription('List all available bot commands')
      .addStringOption(option =>
        option.setName('category')
          .setDescription('Filter by command category')
          .setRequired(false)
          .addChoices(
            { name: 'Admin', value: 'admin' },
            { name: 'Moderation', value: 'moderation' },
            { name: 'Ticket', value: 'ticket' },
            { name: 'Utility', value: 'utility' }
          )
      ),
    category: 'utility',
    permissions: [],
    usage: '/commands [category]',
    async execute(interaction: any) {
      const category = interaction.options.getString('category');
      
      try {
        let commandsData;
        
        if (category) {
          commandsData = await db.select()
            .from(commands)
            .where(eq(commands.category, category));
        } else {
          commandsData = await db.select()
            .from(commands);
        }
        
        if (commandsData.length === 0) {
          await interaction.reply({
            content: '❌ No commands found for the specified category.',
            ephemeral: true
          });
          return;
        }
        
        // Group commands by category
        const groupedCommands = commandsData.reduce((acc, cmd) => {
          if (!acc[cmd.category]) {
            acc[cmd.category] = [];
          }
          acc[cmd.category].push(cmd);
          return acc;
        }, {} as Record<string, typeof commandsData>);
        
        const embed = {
          title: `📋 Bot Commands${category ? ` - ${category.toUpperCase()}` : ''}`,
          color: 0x00FFFF,
          fields: [],
          footer: {
            text: `Total Commands: ${commandsData.length}`,
          },
          timestamp: new Date().toISOString(),
        };
        
        // Add fields for each category
        for (const [cat, cmds] of Object.entries(groupedCommands)) {
          const categoryEmoji = {
            admin: '⚙️',
            moderation: '🛡️',
            ticket: '🎫',
            utility: '🔧'
          }[cat] || '📝';
          
          const commandList = cmds.map(cmd => 
            `\`/${cmd.name}\` - ${cmd.description}`
          ).join('\n');
          
          embed.fields.push({
            name: `${categoryEmoji} ${cat.toUpperCase()} Commands`,
            value: commandList.length > 1024 ? commandList.substring(0, 1021) + '...' : commandList,
            inline: false
          });
        }
        
        await interaction.reply({ embeds: [embed] });
      } catch (error) {
        console.error('Error fetching commands:', error);
        await interaction.reply({
          content: '❌ Failed to fetch commands. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('embed')
      .setDescription('Create a custom embed message')
      .addStringOption(option =>
        option.setName('title')
          .setDescription('Embed title')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('description')
          .setDescription('Embed description')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('color')
          .setDescription('Embed color (hex code, e.g., #FF0000)')
          .setRequired(false)
      )
      .addStringOption(option =>
        option.setName('footer')
          .setDescription('Footer text')
          .setRequired(false)
      )
      .addStringOption(option =>
        option.setName('thumbnail')
          .setDescription('Thumbnail URL')
          .setRequired(false)
      )
      .addStringOption(option =>
        option.setName('image')
          .setDescription('Image URL')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ManageMessages),
    category: 'utility',
    permissions: ['MANAGE_MESSAGES'],
    usage: '/embed <title> <description> [color] [footer] [thumbnail] [image]',
    async execute(interaction: any) {
      const title = interaction.options.getString('title');
      const description = interaction.options.getString('description');
      const color = interaction.options.getString('color');
      const footer = interaction.options.getString('footer');
      const thumbnail = interaction.options.getString('thumbnail');
      const image = interaction.options.getString('image');
      
      try {
        let embedColor = 0x00FFFF; // Default color
        
        if (color) {
          // Parse hex color
          const hexColor = color.replace('#', '');
          if (/^[0-9A-F]{6}$/i.test(hexColor)) {
            embedColor = parseInt(hexColor, 16);
          }
        }
        
        const embed = {
          title: title,
          description: description,
          color: embedColor,
          timestamp: new Date().toISOString(),
        };
        
        if (footer) {
          embed.footer = {
            text: footer,
          };
        }
        
        if (thumbnail) {
          embed.thumbnail = {
            url: thumbnail,
          };
        }
        
        if (image) {
          embed.image = {
            url: image,
          };
        }
        
        await interaction.reply({ embeds: [embed] });
      } catch (error) {
        console.error('Error creating embed:', error);
        await interaction.reply({
          content: '❌ Failed to create embed. Please check your inputs and try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('botstats')
      .setDescription('View detailed bot statistics'),
    category: 'utility',
    permissions: [],
    usage: '/botstats',
    async execute(interaction: any) {
      try {
        const client = interaction.client;
        const guildsCount = client.guilds.cache.size;
        const usersCount = client.guilds.cache.reduce((acc, guild) => acc + guild.memberCount, 0);
        const channelsCount = client.channels.cache.size;
        
        // Memory usage
        const memoryUsage = process.memoryUsage();
        const memoryUsed = Math.round(memoryUsage.heapUsed / 1024 / 1024);
        const memoryTotal = Math.round(memoryUsage.heapTotal / 1024 / 1024);
        
        // Uptime
        const uptime = process.uptime();
        const days = Math.floor(uptime / 86400);
        const hours = Math.floor((uptime % 86400) / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);
        
        // Bot information
        const embed = {
          title: '📊 Bot Statistics',
          color: 0x00FFFF,
          thumbnail: {
            url: client.user.displayAvatarURL(),
          },
          fields: [
            { name: '🏠 Servers', value: guildsCount.toString(), inline: true },
            { name: '👥 Users', value: usersCount.toString(), inline: true },
            { name: '📺 Channels', value: channelsCount.toString(), inline: true },
            { name: '⏰ Uptime', value: `${days}d ${hours}h ${minutes}m`, inline: true },
            { name: '💾 Memory Usage', value: `${memoryUsed}MB / ${memoryTotal}MB`, inline: true },
            { name: '🏓 Ping', value: `${Math.round(client.ws.ping)}ms`, inline: true },
            { name: '🔧 Node.js Version', value: process.version, inline: true },
            { name: '📚 Discord.js Version', value: require('discord.js').version, inline: true },
            { name: '🤖 Bot Version', value: '2.3.2', inline: true },
          ],
          footer: {
            text: 'Bot Statistics',
          },
          timestamp: new Date().toISOString(),
        };
        
        await interaction.reply({ embeds: [embed] });
      } catch (error) {
        console.error('Error fetching bot stats:', error);
        await interaction.reply({
          content: '❌ Failed to fetch bot statistics. Please try again.',
          ephemeral: true
        });
      }
    }
  },
];