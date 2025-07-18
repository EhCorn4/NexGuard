import { SlashCommandBuilder, PermissionFlagsBits } from 'discord.js';
import { db } from '../../db';
import { changelogs } from '@shared/schema';
import { desc } from 'drizzle-orm';

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
          text: `Requested by ${interaction.user.tag}`,
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
          text: `Requested by ${interaction.user.tag}`,
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
          text: `Requested by ${interaction.user.tag}`,
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
          text: `Requested by ${interaction.user.tag}`,
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
              value: '`/ping` - Check bot latency\n`/userinfo` - Get user information\n`/serverinfo` - Get server information\n`/avatar` - Get user avatar\n`/changelog` - View bot changelog\n`/uptime` - Check bot uptime',
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
];