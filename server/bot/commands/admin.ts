import { SlashCommandBuilder, PermissionFlagsBits } from 'discord.js';
import { db } from '../../db';
import { guilds, moderationLogs, changelogs } from '@shared/schema';
import { eq, desc } from 'drizzle-orm';

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

  {
    data: new SlashCommandBuilder()
      .setName('automod')
      .setDescription('Configure automod settings')
      .addSubcommand(subcommand =>
        subcommand
          .setName('enable')
          .setDescription('Enable automod features')
          .addStringOption(option =>
            option.setName('type')
              .setDescription('Type of automod to enable')
              .setRequired(true)
              .addChoices(
                { name: 'Spam Filter', value: 'spam' },
                { name: 'Bad Words', value: 'badwords' },
                { name: 'Caps Lock', value: 'caps' },
                { name: 'Links', value: 'links' },
                { name: 'Mentions', value: 'mentions' }
              )
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('disable')
          .setDescription('Disable automod features')
          .addStringOption(option =>
            option.setName('type')
              .setDescription('Type of automod to disable')
              .setRequired(true)
              .addChoices(
                { name: 'Spam Filter', value: 'spam' },
                { name: 'Bad Words', value: 'badwords' },
                { name: 'Caps Lock', value: 'caps' },
                { name: 'Links', value: 'links' },
                { name: 'Mentions', value: 'mentions' }
              )
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('settings')
          .setDescription('View automod settings')
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    category: 'admin',
    permissions: ['ADMINISTRATOR'],
    usage: '/automod <enable/disable/settings> [type]',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      const type = interaction.options.getString('type');
      
      try {
        const [guildConfig] = await db.select()
          .from(guilds)
          .where(eq(guilds.id, interaction.guild.id))
          .limit(1);

        const settings = JSON.parse(guildConfig?.settings || '{}');
        const automod = settings.automod || {};

        if (subcommand === 'enable') {
          automod[type] = true;
          settings.automod = automod;

          await db.update(guilds)
            .set({ settings: JSON.stringify(settings), updatedAt: new Date() })
            .where(eq(guilds.id, interaction.guild.id));

          await interaction.reply({
            content: `✅ Automod ${type} filter has been enabled.`,
            ephemeral: true
          });
        } else if (subcommand === 'disable') {
          automod[type] = false;
          settings.automod = automod;

          await db.update(guilds)
            .set({ settings: JSON.stringify(settings), updatedAt: new Date() })
            .where(eq(guilds.id, interaction.guild.id));

          await interaction.reply({
            content: `✅ Automod ${type} filter has been disabled.`,
            ephemeral: true
          });
        } else if (subcommand === 'settings') {
          const embed = {
            title: '⚙️ Automod Settings',
            color: 0x0099FF,
            fields: [
              { name: 'Spam Filter', value: automod.spam ? '✅ Enabled' : '❌ Disabled', inline: true },
              { name: 'Bad Words', value: automod.badwords ? '✅ Enabled' : '❌ Disabled', inline: true },
              { name: 'Caps Lock', value: automod.caps ? '✅ Enabled' : '❌ Disabled', inline: true },
              { name: 'Links', value: automod.links ? '✅ Enabled' : '❌ Disabled', inline: true },
              { name: 'Mentions', value: automod.mentions ? '✅ Enabled' : '❌ Disabled', inline: true },
            ],
            timestamp: new Date().toISOString(),
          };

          await interaction.reply({ embeds: [embed] });
        }
      } catch (error) {
        console.error('Error managing automod:', error);
        await interaction.reply({
          content: '❌ Failed to manage automod settings. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('autoreply')
      .setDescription('Manage automatic replies')
      .addSubcommand(subcommand =>
        subcommand
          .setName('add')
          .setDescription('Add an automatic reply')
          .addStringOption(option =>
            option.setName('trigger')
              .setDescription('The trigger word or phrase')
              .setRequired(true)
          )
          .addStringOption(option =>
            option.setName('response')
              .setDescription('The automatic response')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('remove')
          .setDescription('Remove an automatic reply')
          .addStringOption(option =>
            option.setName('trigger')
              .setDescription('The trigger to remove')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('list')
          .setDescription('List all automatic replies')
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    category: 'admin',
    permissions: ['ADMINISTRATOR'],
    usage: '/autoreply <add/remove/list> [trigger] [response]',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      const trigger = interaction.options.getString('trigger');
      const response = interaction.options.getString('response');
      
      try {
        const [guildConfig] = await db.select()
          .from(guilds)
          .where(eq(guilds.id, interaction.guild.id))
          .limit(1);

        const settings = JSON.parse(guildConfig?.settings || '{}');
        const autoreplies = settings.autoreplies || {};

        if (subcommand === 'add') {
          autoreplies[trigger.toLowerCase()] = response;
          settings.autoreplies = autoreplies;

          await db.update(guilds)
            .set({ settings: JSON.stringify(settings), updatedAt: new Date() })
            .where(eq(guilds.id, interaction.guild.id));

          await interaction.reply({
            content: `✅ Autoreply added: "${trigger}" → "${response}"`,
            ephemeral: true
          });
        } else if (subcommand === 'remove') {
          if (autoreplies[trigger.toLowerCase()]) {
            delete autoreplies[trigger.toLowerCase()];
            settings.autoreplies = autoreplies;

            await db.update(guilds)
              .set({ settings: JSON.stringify(settings), updatedAt: new Date() })
              .where(eq(guilds.id, interaction.guild.id));

            await interaction.reply({
              content: `✅ Autoreply removed for trigger: "${trigger}"`,
              ephemeral: true
            });
          } else {
            await interaction.reply({
              content: `❌ No autoreply found for trigger: "${trigger}"`,
              ephemeral: true
            });
          }
        } else if (subcommand === 'list') {
          const replyList = Object.entries(autoreplies).map(([key, value]) => `**${key}** → ${value}`).join('\n') || 'No autoreplies configured.';

          const embed = {
            title: '🤖 Automatic Replies',
            description: replyList,
            color: 0x0099FF,
            timestamp: new Date().toISOString(),
          };

          await interaction.reply({ embeds: [embed] });
        }
      } catch (error) {
        console.error('Error managing autoreplies:', error);
        await interaction.reply({
          content: '❌ Failed to manage autoreplies. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('autorole')
      .setDescription('Manage automatic role assignment')
      .addSubcommand(subcommand =>
        subcommand
          .setName('add')
          .setDescription('Add a role to be automatically assigned')
          .addRoleOption(option =>
            option.setName('role')
              .setDescription('The role to automatically assign')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('remove')
          .setDescription('Remove a role from automatic assignment')
          .addRoleOption(option =>
            option.setName('role')
              .setDescription('The role to remove from automatic assignment')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('list')
          .setDescription('List all automatic roles')
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    category: 'admin',
    permissions: ['ADMINISTRATOR'],
    usage: '/autorole <add/remove/list> [role]',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      const role = interaction.options.getRole('role');
      
      try {
        const [guildConfig] = await db.select()
          .from(guilds)
          .where(eq(guilds.id, interaction.guild.id))
          .limit(1);

        const settings = JSON.parse(guildConfig?.settings || '{}');
        const autoroles = settings.autoroles || [];

        if (subcommand === 'add') {
          if (!autoroles.includes(role.id)) {
            autoroles.push(role.id);
            settings.autoroles = autoroles;

            await db.update(guilds)
              .set({ settings: JSON.stringify(settings), updatedAt: new Date() })
              .where(eq(guilds.id, interaction.guild.id));

            await interaction.reply({
              content: `✅ <@&${role.id}> will now be automatically assigned to new members.`,
              ephemeral: true
            });
          } else {
            await interaction.reply({
              content: `❌ <@&${role.id}> is already set as an automatic role.`,
              ephemeral: true
            });
          }
        } else if (subcommand === 'remove') {
          const index = autoroles.indexOf(role.id);
          if (index > -1) {
            autoroles.splice(index, 1);
            settings.autoroles = autoroles;

            await db.update(guilds)
              .set({ settings: JSON.stringify(settings), updatedAt: new Date() })
              .where(eq(guilds.id, interaction.guild.id));

            await interaction.reply({
              content: `✅ <@&${role.id}> removed from automatic assignment.`,
              ephemeral: true
            });
          } else {
            await interaction.reply({
              content: `❌ <@&${role.id}> is not set as an automatic role.`,
              ephemeral: true
            });
          }
        } else if (subcommand === 'list') {
          const roleList = autoroles.map((roleId: string) => `<@&${roleId}>`).join('\n') || 'No automatic roles configured.';

          const embed = {
            title: '🎭 Automatic Roles',
            description: roleList,
            color: 0x0099FF,
            timestamp: new Date().toISOString(),
          };

          await interaction.reply({ embeds: [embed] });
        }
      } catch (error) {
        console.error('Error managing autoroles:', error);
        await interaction.reply({
          content: '❌ Failed to manage automatic roles. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('changelog')
      .setDescription('Manage bot changelog')
      .addSubcommand(subcommand =>
        subcommand
          .setName('add')
          .setDescription('Add a changelog entry')
          .addStringOption(option =>
            option.setName('version')
              .setDescription('Version number')
              .setRequired(true)
          )
          .addStringOption(option =>
            option.setName('changes')
              .setDescription('Description of changes')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('view')
          .setDescription('View recent changelog entries')
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    category: 'admin',
    permissions: ['ADMINISTRATOR'],
    usage: '/changelog <add/view> [version] [changes]',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      const version = interaction.options.getString('version');
      const changes = interaction.options.getString('changes');
      
      try {
        if (subcommand === 'add') {
          await db.insert(changelogs).values({
            version,
            changes,
            createdAt: new Date(),
          });

          await interaction.reply({
            content: `✅ Changelog entry added for version ${version}.`,
            ephemeral: true
          });
        } else if (subcommand === 'view') {
          const recentChanges = await db.select()
            .from(changelogs)
            .orderBy(desc(changelogs.createdAt))
            .limit(5);

          const changesList = recentChanges.map(change => 
            `**${change.version}** - ${change.changes}`
          ).join('\n') || 'No changelog entries found.';

          const embed = {
            title: '📝 Recent Changelog',
            description: changesList,
            color: 0x0099FF,
            timestamp: new Date().toISOString(),
          };

          await interaction.reply({ embeds: [embed] });
        }
      } catch (error) {
        console.error('Error managing changelog:', error);
        await interaction.reply({
          content: '❌ Failed to manage changelog. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('botlogging')
      .setDescription('Configure bot logging settings')
      .addSubcommand(subcommand =>
        subcommand
          .setName('enable')
          .setDescription('Enable bot logging')
          .addChannelOption(option =>
            option.setName('channel')
              .setDescription('The channel to send logs to')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('disable')
          .setDescription('Disable bot logging')
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('settings')
          .setDescription('View logging settings')
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    category: 'admin',
    permissions: ['ADMINISTRATOR'],
    usage: '/botlogging <enable/disable/settings> [channel]',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      const channel = interaction.options.getChannel('channel');
      
      try {
        const [guildConfig] = await db.select()
          .from(guilds)
          .where(eq(guilds.id, interaction.guild.id))
          .limit(1);

        const settings = JSON.parse(guildConfig?.settings || '{}');

        if (subcommand === 'enable') {
          settings.logging = {
            enabled: true,
            channelId: channel.id
          };

          await db.update(guilds)
            .set({ settings: JSON.stringify(settings), updatedAt: new Date() })
            .where(eq(guilds.id, interaction.guild.id));

          await interaction.reply({
            content: `✅ Bot logging enabled in ${channel}.`,
            ephemeral: true
          });
        } else if (subcommand === 'disable') {
          settings.logging = {
            enabled: false,
            channelId: null
          };

          await db.update(guilds)
            .set({ settings: JSON.stringify(settings), updatedAt: new Date() })
            .where(eq(guilds.id, interaction.guild.id));

          await interaction.reply({
            content: '✅ Bot logging disabled.',
            ephemeral: true
          });
        } else if (subcommand === 'settings') {
          const logging = settings.logging || { enabled: false };

          const embed = {
            title: '📊 Bot Logging Settings',
            color: 0x0099FF,
            fields: [
              { name: 'Status', value: logging.enabled ? '✅ Enabled' : '❌ Disabled', inline: true },
              { name: 'Channel', value: logging.channelId ? `<#${logging.channelId}>` : 'Not set', inline: true },
            ],
            timestamp: new Date().toISOString(),
          };

          await interaction.reply({ embeds: [embed] });
        }
      } catch (error) {
        console.error('Error managing bot logging:', error);
        await interaction.reply({
          content: '❌ Failed to manage bot logging. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('modrole')
      .setDescription('Manage moderator roles for the server')
      .addSubcommand(subcommand =>
        subcommand
          .setName('add')
          .setDescription('Add a role as a moderator role')
          .addRoleOption(option =>
            option.setName('role')
              .setDescription('The role to add as moderator')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('remove')
          .setDescription('Remove a role from moderator roles')
          .addRoleOption(option =>
            option.setName('role')
              .setDescription('The role to remove from moderators')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('list')
          .setDescription('List all current moderator roles')
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ManageRoles),
    category: 'admin',
    permissions: ['MANAGE_ROLES'],
    usage: '/modrole <add/remove/list> [role]',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      
      try {
        const [guildConfig] = await db.select()
          .from(guilds)
          .where(eq(guilds.id, interaction.guild.id))
          .limit(1);

        const settings = JSON.parse(guildConfig?.settings || '{}');
        const moderatorRoles = settings.moderatorRoles || [];

        if (subcommand === 'add') {
          const role = interaction.options.getRole('role');
          
          if (moderatorRoles.includes(role.id)) {
            await interaction.reply({
              content: `❌ <@&${role.id}> is already a moderator role.`,
              ephemeral: true
            });
            return;
          }

          moderatorRoles.push(role.id);
          settings.moderatorRoles = moderatorRoles;

          await db.update(guilds)
            .set({ 
              settings: JSON.stringify(settings),
              updatedAt: new Date()
            })
            .where(eq(guilds.id, interaction.guild.id));

          const embed = {
            title: '🛡️ Moderator Role Added',
            description: `<@&${role.id}> has been added as a moderator role.`,
            color: 0x00FF00,
            fields: [
              { name: 'Role', value: `${role.name} (${role.id})`, inline: true },
              { name: 'Added by', value: interaction.user.tag, inline: true },
              { name: 'Total Mod Roles', value: `${moderatorRoles.length}`, inline: true },
            ],
            timestamp: new Date().toISOString(),
          };

          await interaction.reply({ embeds: [embed] });
        } else if (subcommand === 'remove') {
          const role = interaction.options.getRole('role');
          
          if (!moderatorRoles.includes(role.id)) {
            await interaction.reply({
              content: `❌ <@&${role.id}> is not a moderator role.`,
              ephemeral: true
            });
            return;
          }

          const index = moderatorRoles.indexOf(role.id);
          moderatorRoles.splice(index, 1);
          settings.moderatorRoles = moderatorRoles;

          await db.update(guilds)
            .set({ 
              settings: JSON.stringify(settings),
              updatedAt: new Date()
            })
            .where(eq(guilds.id, interaction.guild.id));

          const embed = {
            title: '🛡️ Moderator Role Removed',
            description: `<@&${role.id}> has been removed from moderator roles.`,
            color: 0xFF0000,
            fields: [
              { name: 'Role', value: `${role.name} (${role.id})`, inline: true },
              { name: 'Removed by', value: interaction.user.tag, inline: true },
              { name: 'Total Mod Roles', value: `${moderatorRoles.length}`, inline: true },
            ],
            timestamp: new Date().toISOString(),
          };

          await interaction.reply({ embeds: [embed] });
        } else if (subcommand === 'list') {
          if (moderatorRoles.length === 0) {
            await interaction.reply({
              content: '📋 No moderator roles have been set up for this server.',
              ephemeral: true
            });
            return;
          }

          const roleList = moderatorRoles.map((roleId: string) => {
            const role = interaction.guild.roles.cache.get(roleId);
            return role ? `<@&${roleId}> (${role.name})` : `<@&${roleId}> (Role not found)`;
          }).join('\n');

          const embed = {
            title: '🛡️ Moderator Roles',
            description: roleList,
            color: 0x0099FF,
            fields: [
              { name: 'Total Roles', value: `${moderatorRoles.length}`, inline: true },
              { name: 'Server', value: interaction.guild.name, inline: true },
            ],
            timestamp: new Date().toISOString(),
          };

          await interaction.reply({ embeds: [embed] });
        }
      } catch (error) {
        console.error('Error managing moderator roles:', error);
        await interaction.reply({
          content: '❌ Failed to manage moderator roles. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('welcome')
      .setDescription('Configure welcome messages')
      .addSubcommand(subcommand =>
        subcommand
          .setName('enable')
          .setDescription('Enable welcome messages')
          .addChannelOption(option =>
            option.setName('channel')
              .setDescription('The channel to send welcome messages to')
              .setRequired(true)
          )
          .addStringOption(option =>
            option.setName('message')
              .setDescription('Welcome message (use {user} for mention, {server} for server name)')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('disable')
          .setDescription('Disable welcome messages')
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('settings')
          .setDescription('View welcome message settings')
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    category: 'admin',
    permissions: ['ADMINISTRATOR'],
    usage: '/welcome <enable/disable/settings> [channel] [message]',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      const channel = interaction.options.getChannel('channel');
      const message = interaction.options.getString('message');
      
      try {
        const [guildConfig] = await db.select()
          .from(guilds)
          .where(eq(guilds.id, interaction.guild.id))
          .limit(1);

        const settings = JSON.parse(guildConfig?.settings || '{}');

        if (subcommand === 'enable') {
          settings.welcome = {
            enabled: true,
            channelId: channel.id,
            message: message
          };

          await db.update(guilds)
            .set({ settings: JSON.stringify(settings), updatedAt: new Date() })
            .where(eq(guilds.id, interaction.guild.id));

          await interaction.reply({
            content: `✅ Welcome messages enabled in ${channel}.`,
            ephemeral: true
          });
        } else if (subcommand === 'disable') {
          settings.welcome = {
            enabled: false,
            channelId: null,
            message: null
          };

          await db.update(guilds)
            .set({ settings: JSON.stringify(settings), updatedAt: new Date() })
            .where(eq(guilds.id, interaction.guild.id));

          await interaction.reply({
            content: '✅ Welcome messages disabled.',
            ephemeral: true
          });
        } else if (subcommand === 'settings') {
          const welcome = settings.welcome || { enabled: false };

          const embed = {
            title: '👋 Welcome Message Settings',
            color: 0x0099FF,
            fields: [
              { name: 'Status', value: welcome.enabled ? '✅ Enabled' : '❌ Disabled', inline: true },
              { name: 'Channel', value: welcome.channelId ? `<#${welcome.channelId}>` : 'Not set', inline: true },
              { name: 'Message', value: welcome.message || 'Not set', inline: false },
            ],
            timestamp: new Date().toISOString(),
          };

          await interaction.reply({ embeds: [embed] });
        }
      } catch (error) {
        console.error('Error managing welcome messages:', error);
        await interaction.reply({
          content: '❌ Failed to manage welcome messages. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('settings')
      .setDescription('View and manage all server settings')
      .addSubcommand(subcommand =>
        subcommand
          .setName('view')
          .setDescription('View all current server settings')
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('reset')
          .setDescription('Reset all server settings to default')
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    category: 'admin',
    permissions: ['ADMINISTRATOR'],
    usage: '/settings <view/reset>',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      
      try {
        const [guildConfig] = await db.select()
          .from(guilds)
          .where(eq(guilds.id, interaction.guild.id))
          .limit(1);

        if (subcommand === 'view') {
          const settings = JSON.parse(guildConfig?.settings || '{}');
          const automod = settings.automod || {};
          const welcome = settings.welcome || {};
          const logging = settings.logging || {};

          const embed = {
            title: '⚙️ Server Settings',
            color: 0x0099FF,
            fields: [
              { name: 'Prefix', value: guildConfig?.prefix || '!', inline: true },
              { name: 'Moderation', value: guildConfig?.moderationEnabled ? '✅' : '❌', inline: true },
              { name: 'Tickets', value: guildConfig?.ticketEnabled ? '✅' : '❌', inline: true },
              { name: 'Welcome Messages', value: welcome.enabled ? '✅' : '❌', inline: true },
              { name: 'Bot Logging', value: logging.enabled ? '✅' : '❌', inline: true },
              { name: 'Automod Filters', value: Object.values(automod).some(v => v) ? '✅' : '❌', inline: true },
              { name: 'Moderator Roles', value: `${(settings.moderatorRoles || []).length}`, inline: true },
              { name: 'Auto Roles', value: `${(settings.autoroles || []).length}`, inline: true },
              { name: 'Auto Replies', value: `${Object.keys(settings.autoreplies || {}).length}`, inline: true },
            ],
            timestamp: new Date().toISOString(),
          };

          await interaction.reply({ embeds: [embed] });
        } else if (subcommand === 'reset') {
          await db.update(guilds)
            .set({ 
              settings: JSON.stringify({}),
              prefix: '!',
              moderationEnabled: false,
              ticketEnabled: false,
              updatedAt: new Date()
            })
            .where(eq(guilds.id, interaction.guild.id));

          await interaction.reply({
            content: '✅ All server settings have been reset to default.',
            ephemeral: true
          });
        }
      } catch (error) {
        console.error('Error managing settings:', error);
        await interaction.reply({
          content: '❌ Failed to manage server settings. Please try again.',
          ephemeral: true
        });
      }
    }
  },
];
