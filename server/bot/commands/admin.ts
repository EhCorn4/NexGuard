import { SlashCommandBuilder, PermissionFlagsBits } from 'discord.js';
import { db } from '../../db';
import { guilds, moderationLogs } from '@shared/schema';
import { eq } from 'drizzle-orm';

export const adminCommands = [
  {
    data: new SlashCommandBuilder()
      .setName('setprefix')
      .setDescription('Set the command prefix for this server')
      .addStringOption(option =>
        option.setName('prefix')
          .setDescription('The new prefix')
          .setRequired(true)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    category: 'admin',
    permissions: ['ADMINISTRATOR'],
    usage: '/setprefix <prefix>',
    async execute(interaction: any) {
      const prefix = interaction.options.getString('prefix');
      
      try {
        await db.update(guilds)
          .set({ prefix, updatedAt: new Date() })
          .where(eq(guilds.id, interaction.guild.id));
        
        await interaction.reply({
          content: `✅ Server prefix updated to: \`${prefix}\``,
          ephemeral: true
        });
      } catch (error) {
        console.error('Error updating prefix:', error);
        await interaction.reply({
          content: '❌ Failed to update prefix. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('configure')
      .setDescription('Configure server settings')
      .addSubcommand(subcommand =>
        subcommand
          .setName('moderation')
          .setDescription('Toggle moderation features')
          .addBooleanOption(option =>
            option.setName('enabled')
              .setDescription('Enable or disable moderation')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('tickets')
          .setDescription('Toggle ticket system')
          .addBooleanOption(option =>
            option.setName('enabled')
              .setDescription('Enable or disable ticket system')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('roles')
          .setDescription('Set important roles')
          .addRoleOption(option =>
            option.setName('admin')
              .setDescription('Admin role')
          )
          .addRoleOption(option =>
            option.setName('moderator')
              .setDescription('Moderator role')
          )
          .addRoleOption(option =>
            option.setName('mute')
              .setDescription('Mute role')
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('channels')
          .setDescription('Set important channels')
          .addChannelOption(option =>
            option.setName('logs')
              .setDescription('Log channel')
          )
          .addChannelOption(option =>
            option.setName('welcome')
              .setDescription('Welcome channel')
          )
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    category: 'admin',
    permissions: ['ADMINISTRATOR'],
    usage: '/configure <subcommand> <options>',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      
      try {
        switch (subcommand) {
          case 'moderation':
            const moderationEnabled = interaction.options.getBoolean('enabled');
            await db.update(guilds)
              .set({ moderationEnabled, updatedAt: new Date() })
              .where(eq(guilds.id, interaction.guild.id));
            
            await interaction.reply({
              content: `✅ Moderation ${moderationEnabled ? 'enabled' : 'disabled'} for this server.`,
              ephemeral: true
            });
            break;

          case 'tickets':
            const ticketEnabled = interaction.options.getBoolean('enabled');
            await db.update(guilds)
              .set({ ticketEnabled, updatedAt: new Date() })
              .where(eq(guilds.id, interaction.guild.id));
            
            await interaction.reply({
              content: `✅ Ticket system ${ticketEnabled ? 'enabled' : 'disabled'} for this server.`,
              ephemeral: true
            });
            break;

          case 'roles':
            const adminRole = interaction.options.getRole('admin');
            const moderatorRole = interaction.options.getRole('moderator');
            const muteRole = interaction.options.getRole('mute');
            
            const roleUpdates: any = { updatedAt: new Date() };
            if (adminRole) roleUpdates.adminRoleId = adminRole.id;
            if (moderatorRole) roleUpdates.moderatorRoleId = moderatorRole.id;
            if (muteRole) roleUpdates.muteRoleId = muteRole.id;
            
            await db.update(guilds)
              .set(roleUpdates)
              .where(eq(guilds.id, interaction.guild.id));
            
            await interaction.reply({
              content: `✅ Server roles updated successfully.`,
              ephemeral: true
            });
            break;

          case 'channels':
            const logChannel = interaction.options.getChannel('logs');
            const welcomeChannel = interaction.options.getChannel('welcome');
            
            const channelUpdates: any = { updatedAt: new Date() };
            if (logChannel) channelUpdates.logChannelId = logChannel.id;
            if (welcomeChannel) channelUpdates.welcomeChannelId = welcomeChannel.id;
            
            await db.update(guilds)
              .set(channelUpdates)
              .where(eq(guilds.id, interaction.guild.id));
            
            await interaction.reply({
              content: `✅ Server channels updated successfully.`,
              ephemeral: true
            });
            break;
        }
      } catch (error) {
        console.error('Error configuring server:', error);
        await interaction.reply({
          content: '❌ Failed to update configuration. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('serverstats')
      .setDescription('View server statistics')
      .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    category: 'admin',
    permissions: ['ADMINISTRATOR'],
    usage: '/serverstats',
    async execute(interaction: any) {
      const guild = interaction.guild;
      
      try {
        const [serverConfig] = await db.select()
          .from(guilds)
          .where(eq(guilds.id, guild.id))
          .limit(1);

        const totalChannels = guild.channels.cache.size;
        const textChannels = guild.channels.cache.filter((c: any) => c.type === 0).size;
        const voiceChannels = guild.channels.cache.filter((c: any) => c.type === 2).size;
        const categories = guild.channels.cache.filter((c: any) => c.type === 4).size;
        const roles = guild.roles.cache.size;
        const emojis = guild.emojis.cache.size;

        const embed = {
          title: `📊 Server Statistics - ${guild.name}`,
          color: 0x00FFFF,
          fields: [
            { name: '👥 Members', value: `${guild.memberCount}`, inline: true },
            { name: '💬 Text Channels', value: `${textChannels}`, inline: true },
            { name: '🔊 Voice Channels', value: `${voiceChannels}`, inline: true },
            { name: '📁 Categories', value: `${categories}`, inline: true },
            { name: '🏷️ Roles', value: `${roles}`, inline: true },
            { name: '😀 Emojis', value: `${emojis}`, inline: true },
            { name: '🔧 Prefix', value: `${serverConfig?.prefix || '!'}`, inline: true },
            { name: '🛡️ Moderation', value: `${serverConfig?.moderationEnabled ? '✅' : '❌'}`, inline: true },
            { name: '🎫 Tickets', value: `${serverConfig?.ticketEnabled ? '✅' : '❌'}`, inline: true },
          ],
          timestamp: new Date().toISOString(),
          footer: {
            text: `Server ID: ${guild.id}`,
          },
        };

        await interaction.reply({ embeds: [embed] });
      } catch (error) {
        console.error('Error fetching server stats:', error);
        await interaction.reply({
          content: '❌ Failed to fetch server statistics.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('announcement')
      .setDescription('Send an announcement to a channel')
      .addChannelOption(option =>
        option.setName('channel')
          .setDescription('The channel to send the announcement to')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('message')
          .setDescription('The announcement message')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('title')
          .setDescription('The announcement title')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    category: 'admin',
    permissions: ['ADMINISTRATOR'],
    usage: '/announcement <channel> <message> [title]',
    async execute(interaction: any) {
      const channel = interaction.options.getChannel('channel');
      const message = interaction.options.getString('message');
      const title = interaction.options.getString('title');
      
      try {
        const embed = {
          title: title || '📢 Announcement',
          description: message,
          color: 0x00FFFF,
          timestamp: new Date().toISOString(),
          footer: {
            text: `Announcement by ${interaction.user.tag}`,
            icon_url: interaction.user.displayAvatarURL(),
          },
        };

        await channel.send({ embeds: [embed] });
        
        await interaction.reply({
          content: `✅ Announcement sent to ${channel}`,
          ephemeral: true
        });
      } catch (error) {
        console.error('Error sending announcement:', error);
        await interaction.reply({
          content: '❌ Failed to send announcement. Please check channel permissions.',
          ephemeral: true
        });
      }
    }
  },
];