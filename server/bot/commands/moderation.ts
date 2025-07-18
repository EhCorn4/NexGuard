import { SlashCommandBuilder, PermissionFlagsBits } from 'discord.js';
import { db } from '../../db';
import { moderationLogs, guilds } from '@shared/schema';
import { eq } from 'drizzle-orm';

export const moderationCommands = [
  {
    data: new SlashCommandBuilder()
      .setName('warn')
      .setDescription('Warn a user')
      .addUserOption(option =>
        option.setName('user')
          .setDescription('The user to warn')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('reason')
          .setDescription('The reason for the warning')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ModerateMembers),
    category: 'moderation',
    permissions: ['MODERATE_MEMBERS'],
    usage: '/warn <user> [reason]',
    async execute(interaction: any) {
      const user = interaction.options.getUser('user');
      const reason = interaction.options.getString('reason') || 'No reason provided';
      
      try {
        // Log the warning
        await db.insert(moderationLogs).values({
          guildId: interaction.guild.id,
          userId: user.id,
          moderatorId: interaction.user.id,
          action: 'warn',
          reason,
          createdAt: new Date(),
        });

        const embed = {
          title: '⚠️ User Warned',
          color: 0xFFFF00,
          fields: [
            { name: 'User', value: `${user.tag} (${user.id})`, inline: true },
            { name: 'Moderator', value: `${interaction.user.tag}`, inline: true },
            { name: 'Reason', value: reason, inline: false },
          ],
          timestamp: new Date().toISOString(),
        };

        await interaction.reply({ embeds: [embed] });

        // Try to DM the user
        try {
          await user.send({
            embeds: [{
              title: '⚠️ Warning Received',
              description: `You have been warned in **${interaction.guild.name}**`,
              color: 0xFFFF00,
              fields: [
                { name: 'Reason', value: reason, inline: false },
                { name: 'Moderator', value: interaction.user.tag, inline: true },
              ],
              timestamp: new Date().toISOString(),
            }]
          });
        } catch (dmError) {
          console.log('Could not DM user about warning');
        }
      } catch (error) {
        console.error('Error warning user:', error);
        await interaction.reply({
          content: '❌ Failed to warn user. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('mute')
      .setDescription('Mute a user')
      .addUserOption(option =>
        option.setName('user')
          .setDescription('The user to mute')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('duration')
          .setDescription('Duration (e.g., 10m, 1h, 1d)')
          .setRequired(false)
      )
      .addStringOption(option =>
        option.setName('reason')
          .setDescription('The reason for the mute')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ModerateMembers),
    category: 'moderation',
    permissions: ['MODERATE_MEMBERS'],
    usage: '/mute <user> [duration] [reason]',
    async execute(interaction: any) {
      const user = interaction.options.getUser('user');
      const duration = interaction.options.getString('duration') || '10m';
      const reason = interaction.options.getString('reason') || 'No reason provided';
      
      try {
        const member = await interaction.guild.members.fetch(user.id);
        
        // Parse duration
        const durationMs = parseDuration(duration);
        
        // Apply timeout
        await member.timeout(durationMs, reason);
        
        // Log the mute
        await db.insert(moderationLogs).values({
          guildId: interaction.guild.id,
          userId: user.id,
          moderatorId: interaction.user.id,
          action: 'mute',
          reason,
          duration,
          createdAt: new Date(),
        });

        const embed = {
          title: '🔇 User Muted',
          color: 0xFF8C00,
          fields: [
            { name: 'User', value: `${user.tag} (${user.id})`, inline: true },
            { name: 'Duration', value: duration, inline: true },
            { name: 'Moderator', value: `${interaction.user.tag}`, inline: true },
            { name: 'Reason', value: reason, inline: false },
          ],
          timestamp: new Date().toISOString(),
        };

        await interaction.reply({ embeds: [embed] });

        // Try to DM the user
        try {
          await user.send({
            embeds: [{
              title: '🔇 You Have Been Muted',
              description: `You have been muted in **${interaction.guild.name}**`,
              color: 0xFF8C00,
              fields: [
                { name: 'Duration', value: duration, inline: true },
                { name: 'Reason', value: reason, inline: false },
                { name: 'Moderator', value: interaction.user.tag, inline: true },
              ],
              timestamp: new Date().toISOString(),
            }]
          });
        } catch (dmError) {
          console.log('Could not DM user about mute');
        }
      } catch (error) {
        console.error('Error muting user:', error);
        await interaction.reply({
          content: '❌ Failed to mute user. Please check permissions and try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('kick')
      .setDescription('Kick a user from the server')
      .addUserOption(option =>
        option.setName('user')
          .setDescription('The user to kick')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('reason')
          .setDescription('The reason for the kick')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.KickMembers),
    category: 'moderation',
    permissions: ['KICK_MEMBERS'],
    usage: '/kick <user> [reason]',
    async execute(interaction: any) {
      const user = interaction.options.getUser('user');
      const reason = interaction.options.getString('reason') || 'No reason provided';
      
      try {
        const member = await interaction.guild.members.fetch(user.id);
        
        // Try to DM the user before kicking
        try {
          await user.send({
            embeds: [{
              title: '👢 You Have Been Kicked',
              description: `You have been kicked from **${interaction.guild.name}**`,
              color: 0xFF4500,
              fields: [
                { name: 'Reason', value: reason, inline: false },
                { name: 'Moderator', value: interaction.user.tag, inline: true },
              ],
              timestamp: new Date().toISOString(),
            }]
          });
        } catch (dmError) {
          console.log('Could not DM user about kick');
        }
        
        // Kick the user
        await member.kick(reason);
        
        // Log the kick
        await db.insert(moderationLogs).values({
          guildId: interaction.guild.id,
          userId: user.id,
          moderatorId: interaction.user.id,
          action: 'kick',
          reason,
          createdAt: new Date(),
        });

        const embed = {
          title: '👢 User Kicked',
          color: 0xFF4500,
          fields: [
            { name: 'User', value: `${user.tag} (${user.id})`, inline: true },
            { name: 'Moderator', value: `${interaction.user.tag}`, inline: true },
            { name: 'Reason', value: reason, inline: false },
          ],
          timestamp: new Date().toISOString(),
        };

        await interaction.reply({ embeds: [embed] });
      } catch (error) {
        console.error('Error kicking user:', error);
        await interaction.reply({
          content: '❌ Failed to kick user. Please check permissions and try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('ban')
      .setDescription('Ban a user from the server')
      .addUserOption(option =>
        option.setName('user')
          .setDescription('The user to ban')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('reason')
          .setDescription('The reason for the ban')
          .setRequired(false)
      )
      .addIntegerOption(option =>
        option.setName('delete_days')
          .setDescription('Days of messages to delete (0-7)')
          .setRequired(false)
          .setMinValue(0)
          .setMaxValue(7)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.BanMembers),
    category: 'moderation',
    permissions: ['BAN_MEMBERS'],
    usage: '/ban <user> [reason] [delete_days]',
    async execute(interaction: any) {
      const user = interaction.options.getUser('user');
      const reason = interaction.options.getString('reason') || 'No reason provided';
      const deleteDays = interaction.options.getInteger('delete_days') || 0;
      
      try {
        // Try to DM the user before banning
        try {
          await user.send({
            embeds: [{
              title: '🔨 You Have Been Banned',
              description: `You have been banned from **${interaction.guild.name}**`,
              color: 0xFF0000,
              fields: [
                { name: 'Reason', value: reason, inline: false },
                { name: 'Moderator', value: interaction.user.tag, inline: true },
              ],
              timestamp: new Date().toISOString(),
            }]
          });
        } catch (dmError) {
          console.log('Could not DM user about ban');
        }
        
        // Ban the user
        await interaction.guild.members.ban(user.id, { 
          reason,
          deleteMessageDays: deleteDays
        });
        
        // Log the ban
        await db.insert(moderationLogs).values({
          guildId: interaction.guild.id,
          userId: user.id,
          moderatorId: interaction.user.id,
          action: 'ban',
          reason,
          createdAt: new Date(),
        });

        const embed = {
          title: '🔨 User Banned',
          color: 0xFF0000,
          fields: [
            { name: 'User', value: `${user.tag} (${user.id})`, inline: true },
            { name: 'Moderator', value: `${interaction.user.tag}`, inline: true },
            { name: 'Messages Deleted', value: `${deleteDays} days`, inline: true },
            { name: 'Reason', value: reason, inline: false },
          ],
          timestamp: new Date().toISOString(),
        };

        await interaction.reply({ embeds: [embed] });
      } catch (error) {
        console.error('Error banning user:', error);
        await interaction.reply({
          content: '❌ Failed to ban user. Please check permissions and try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('unban')
      .setDescription('Unban a user from the server')
      .addStringOption(option =>
        option.setName('user_id')
          .setDescription('The user ID to unban')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('reason')
          .setDescription('The reason for the unban')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.BanMembers),
    category: 'moderation',
    permissions: ['BAN_MEMBERS'],
    usage: '/unban <user_id> [reason]',
    async execute(interaction: any) {
      const userId = interaction.options.getString('user_id');
      const reason = interaction.options.getString('reason') || 'No reason provided';
      
      try {
        // Unban the user
        await interaction.guild.members.unban(userId, reason);
        
        // Log the unban
        await db.insert(moderationLogs).values({
          guildId: interaction.guild.id,
          userId: userId,
          moderatorId: interaction.user.id,
          action: 'unban',
          reason,
          createdAt: new Date(),
        });

        const embed = {
          title: '🔓 User Unbanned',
          color: 0x00FF00,
          fields: [
            { name: 'User ID', value: userId, inline: true },
            { name: 'Moderator', value: `${interaction.user.tag}`, inline: true },
            { name: 'Reason', value: reason, inline: false },
          ],
          timestamp: new Date().toISOString(),
        };

        await interaction.reply({ embeds: [embed] });
      } catch (error) {
        console.error('Error unbanning user:', error);
        await interaction.reply({
          content: '❌ Failed to unban user. Please check the user ID and try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('clear')
      .setDescription('Clear messages from a channel')
      .addIntegerOption(option =>
        option.setName('amount')
          .setDescription('Number of messages to delete (1-100)')
          .setRequired(true)
          .setMinValue(1)
          .setMaxValue(100)
      )
      .addUserOption(option =>
        option.setName('user')
          .setDescription('Only delete messages from this user')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ManageMessages),
    category: 'moderation',
    permissions: ['MANAGE_MESSAGES'],
    usage: '/clear <amount> [user]',
    async execute(interaction: any) {
      const amount = interaction.options.getInteger('amount');
      const user = interaction.options.getUser('user');
      
      try {
        await interaction.deferReply({ ephemeral: true });
        
        const messages = await interaction.channel.messages.fetch({ limit: amount });
        
        let messagesToDelete = messages;
        if (user) {
          messagesToDelete = messages.filter((msg: any) => msg.author.id === user.id);
        }
        
        await interaction.channel.bulkDelete(messagesToDelete);
        
        await interaction.editReply({
          content: `✅ Successfully deleted ${messagesToDelete.size} messages${user ? ` from ${user.tag}` : ''}.`
        });
      } catch (error) {
        console.error('Error clearing messages:', error);
        await interaction.editReply({
          content: '❌ Failed to clear messages. Messages might be too old or I lack permissions.'
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
    category: 'moderation',
    permissions: ['MANAGE_ROLES'],
    usage: '/modrole <add/remove/list> [role]',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      
      try {
        // Get or create server configuration
        let guildConfig = await db.select()
          .from(guilds)
          .where(eq(guilds.id, interaction.guild.id))
          .limit(1);
        
        if (guildConfig.length === 0) {
          await db.insert(guilds).values({
            id: interaction.guild.id,
            name: interaction.guild.name,
            memberCount: interaction.guild.memberCount,
            settings: JSON.stringify({ moderatorRoles: [] }),
            updatedAt: new Date(),
          });
          guildConfig = [{ 
            id: interaction.guild.id, 
            name: interaction.guild.name, 
            memberCount: interaction.guild.memberCount,
            settings: JSON.stringify({ moderatorRoles: [] }),
            updatedAt: new Date()
          }];
        }

        const settings = JSON.parse(guildConfig[0].settings || '{}');
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
      .setName('tempban')
      .setDescription('Temporarily ban a user from the server')
      .addUserOption(option =>
        option.setName('user')
          .setDescription('The user to temporarily ban')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('duration')
          .setDescription('Duration (e.g., 1d, 1w, 1m)')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('reason')
          .setDescription('The reason for the temporary ban')
          .setRequired(false)
      )
      .addIntegerOption(option =>
        option.setName('delete_days')
          .setDescription('Days of messages to delete (0-7)')
          .setRequired(false)
          .setMinValue(0)
          .setMaxValue(7)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.BanMembers),
    category: 'moderation',
    permissions: ['BAN_MEMBERS'],
    usage: '/tempban <user> <duration> [reason] [delete_days]',
    async execute(interaction: any) {
      const user = interaction.options.getUser('user');
      const duration = interaction.options.getString('duration');
      const reason = interaction.options.getString('reason') || 'No reason provided';
      const deleteDays = interaction.options.getInteger('delete_days') || 0;
      
      try {
        // Parse duration
        const durationMs = parseDuration(duration);
        const unbanDate = new Date(Date.now() + durationMs);
        
        // Try to DM the user before banning
        try {
          await user.send({
            embeds: [{
              title: '⏱️ You Have Been Temporarily Banned',
              description: `You have been temporarily banned from **${interaction.guild.name}**`,
              color: 0xFF6600,
              fields: [
                { name: 'Duration', value: duration, inline: true },
                { name: 'Unban Date', value: `<t:${Math.floor(unbanDate.getTime() / 1000)}:F>`, inline: true },
                { name: 'Reason', value: reason, inline: false },
                { name: 'Moderator', value: interaction.user.tag, inline: true },
              ],
              timestamp: new Date().toISOString(),
            }]
          });
        } catch (dmError) {
          console.log('Could not DM user about temporary ban');
        }
        
        // Ban the user
        await interaction.guild.members.ban(user.id, { 
          reason: `Temporary ban: ${reason}`,
          deleteMessageDays: deleteDays
        });
        
        // Log the temporary ban
        await db.insert(moderationLogs).values({
          guildId: interaction.guild.id,
          userId: user.id,
          moderatorId: interaction.user.id,
          action: 'tempban',
          reason,
          duration,
          createdAt: new Date(),
        });

        // Schedule unban (in a real implementation, you'd want to use a job queue)
        setTimeout(async () => {
          try {
            await interaction.guild.members.unban(user.id, 'Temporary ban expired');
            
            // Log the automatic unban
            await db.insert(moderationLogs).values({
              guildId: interaction.guild.id,
              userId: user.id,
              moderatorId: interaction.client.user.id,
              action: 'unban',
              reason: 'Temporary ban expired',
              createdAt: new Date(),
            });
          } catch (unbanError) {
            console.error('Failed to automatically unban user:', unbanError);
          }
        }, durationMs);

        const embed = {
          title: '⏱️ User Temporarily Banned',
          color: 0xFF6600,
          fields: [
            { name: 'User', value: `${user.tag} (${user.id})`, inline: true },
            { name: 'Duration', value: duration, inline: true },
            { name: 'Moderator', value: `${interaction.user.tag}`, inline: true },
            { name: 'Unban Date', value: `<t:${Math.floor(unbanDate.getTime() / 1000)}:F>`, inline: true },
            { name: 'Messages Deleted', value: `${deleteDays} days`, inline: true },
            { name: 'Reason', value: reason, inline: false },
          ],
          timestamp: new Date().toISOString(),
        };

        await interaction.reply({ embeds: [embed] });
      } catch (error) {
        console.error('Error temporarily banning user:', error);
        await interaction.reply({
          content: '❌ Failed to temporarily ban user. Please check permissions and try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('unmute')
      .setDescription('Remove timeout from a user')
      .addUserOption(option =>
        option.setName('user')
          .setDescription('The user to unmute')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('reason')
          .setDescription('The reason for unmuting')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ModerateMembers),
    category: 'moderation',
    permissions: ['MODERATE_MEMBERS'],
    usage: '/unmute <user> [reason]',
    async execute(interaction: any) {
      const user = interaction.options.getUser('user');
      const reason = interaction.options.getString('reason') || 'No reason provided';
      
      try {
        const member = await interaction.guild.members.fetch(user.id);
        
        if (!member.isCommunicationDisabled()) {
          await interaction.reply({
            content: '❌ This user is not currently muted.',
            ephemeral: true
          });
          return;
        }
        
        // Remove timeout
        await member.timeout(null, reason);
        
        // Log the unmute
        await db.insert(moderationLogs).values({
          guildId: interaction.guild.id,
          userId: user.id,
          moderatorId: interaction.user.id,
          action: 'unmute',
          reason,
          createdAt: new Date(),
        });

        const embed = {
          title: '🔊 User Unmuted',
          color: 0x00FF00,
          fields: [
            { name: 'User', value: `${user.tag} (${user.id})`, inline: true },
            { name: 'Moderator', value: `${interaction.user.tag}`, inline: true },
            { name: 'Reason', value: reason, inline: false },
          ],
          timestamp: new Date().toISOString(),
        };

        await interaction.reply({ embeds: [embed] });

        // Try to DM the user
        try {
          await user.send({
            embeds: [{
              title: '🔊 You Have Been Unmuted',
              description: `You have been unmuted in **${interaction.guild.name}**`,
              color: 0x00FF00,
              fields: [
                { name: 'Reason', value: reason, inline: false },
                { name: 'Moderator', value: interaction.user.tag, inline: true },
              ],
              timestamp: new Date().toISOString(),
            }]
          });
        } catch (dmError) {
          console.log('Could not DM user about unmute');
        }
      } catch (error) {
        console.error('Error unmuting user:', error);
        await interaction.reply({
          content: '❌ Failed to unmute user. Please check permissions and try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('timeout')
      .setDescription('Timeout a user for a specified duration')
      .addUserOption(option =>
        option.setName('user')
          .setDescription('The user to timeout')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('duration')
          .setDescription('Duration (e.g., 10m, 1h, 1d)')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('reason')
          .setDescription('The reason for the timeout')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ModerateMembers),
    category: 'moderation',
    permissions: ['MODERATE_MEMBERS'],
    usage: '/timeout <user> <duration> [reason]',
    async execute(interaction: any) {
      const user = interaction.options.getUser('user');
      const duration = interaction.options.getString('duration');
      const reason = interaction.options.getString('reason') || 'No reason provided';
      
      try {
        const member = await interaction.guild.members.fetch(user.id);
        
        // Parse duration
        const durationMs = parseDuration(duration);
        const timeoutEnd = new Date(Date.now() + durationMs);
        
        // Apply timeout
        await member.timeout(durationMs, reason);
        
        // Log the timeout
        await db.insert(moderationLogs).values({
          guildId: interaction.guild.id,
          userId: user.id,
          moderatorId: interaction.user.id,
          action: 'timeout',
          reason,
          duration,
          createdAt: new Date(),
        });

        const embed = {
          title: '⏰ User Timed Out',
          color: 0xFF8C00,
          fields: [
            { name: 'User', value: `${user.tag} (${user.id})`, inline: true },
            { name: 'Duration', value: duration, inline: true },
            { name: 'Moderator', value: `${interaction.user.tag}`, inline: true },
            { name: 'Timeout Ends', value: `<t:${Math.floor(timeoutEnd.getTime() / 1000)}:F>`, inline: true },
            { name: 'Reason', value: reason, inline: false },
          ],
          timestamp: new Date().toISOString(),
        };

        await interaction.reply({ embeds: [embed] });

        // Try to DM the user
        try {
          await user.send({
            embeds: [{
              title: '⏰ You Have Been Timed Out',
              description: `You have been timed out in **${interaction.guild.name}**`,
              color: 0xFF8C00,
              fields: [
                { name: 'Duration', value: duration, inline: true },
                { name: 'Ends At', value: `<t:${Math.floor(timeoutEnd.getTime() / 1000)}:F>`, inline: true },
                { name: 'Reason', value: reason, inline: false },
                { name: 'Moderator', value: interaction.user.tag, inline: true },
              ],
              timestamp: new Date().toISOString(),
            }]
          });
        } catch (dmError) {
          console.log('Could not DM user about timeout');
        }
      } catch (error) {
        console.error('Error timing out user:', error);
        await interaction.reply({
          content: '❌ Failed to timeout user. Please check permissions and try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('lock')
      .setDescription('Lock a channel to prevent messages')
      .addChannelOption(option =>
        option.setName('channel')
          .setDescription('The channel to lock (defaults to current channel)')
          .setRequired(false)
      )
      .addStringOption(option =>
        option.setName('reason')
          .setDescription('The reason for locking the channel')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ManageChannels),
    category: 'moderation',
    permissions: ['MANAGE_CHANNELS'],
    usage: '/lock [channel] [reason]',
    async execute(interaction: any) {
      const channel = interaction.options.getChannel('channel') || interaction.channel;
      const reason = interaction.options.getString('reason') || 'No reason provided';
      
      try {
        // Get everyone role
        const everyoneRole = interaction.guild.roles.everyone;
        
        // Remove send messages permission for everyone
        await channel.permissionOverwrites.edit(everyoneRole, {
          SendMessages: false
        });
        
        // Log the lock
        await db.insert(moderationLogs).values({
          guildId: interaction.guild.id,
          userId: interaction.user.id,
          moderatorId: interaction.user.id,
          action: 'lock',
          reason: `Channel locked: ${reason}`,
          createdAt: new Date(),
        });

        const embed = {
          title: '🔒 Channel Locked',
          color: 0xFF0000,
          fields: [
            { name: 'Channel', value: `${channel.name}`, inline: true },
            { name: 'Moderator', value: `${interaction.user.tag}`, inline: true },
            { name: 'Reason', value: reason, inline: false },
          ],
          timestamp: new Date().toISOString(),
        };

        await interaction.reply({ embeds: [embed] });
        
        // Send a message to the locked channel
        await channel.send({
          embeds: [{
            title: '🔒 Channel Locked',
            description: `This channel has been locked by ${interaction.user.tag}`,
            color: 0xFF0000,
            fields: [
              { name: 'Reason', value: reason, inline: false },
            ],
            timestamp: new Date().toISOString(),
          }]
        });
      } catch (error) {
        console.error('Error locking channel:', error);
        await interaction.reply({
          content: '❌ Failed to lock channel. Please check permissions and try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('unlock')
      .setDescription('Unlock a channel to allow messages')
      .addChannelOption(option =>
        option.setName('channel')
          .setDescription('The channel to unlock (defaults to current channel)')
          .setRequired(false)
      )
      .addStringOption(option =>
        option.setName('reason')
          .setDescription('The reason for unlocking the channel')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ManageChannels),
    category: 'moderation',
    permissions: ['MANAGE_CHANNELS'],
    usage: '/unlock [channel] [reason]',
    async execute(interaction: any) {
      const channel = interaction.options.getChannel('channel') || interaction.channel;
      const reason = interaction.options.getString('reason') || 'No reason provided';
      
      try {
        // Get everyone role
        const everyoneRole = interaction.guild.roles.everyone;
        
        // Restore send messages permission for everyone
        await channel.permissionOverwrites.edit(everyoneRole, {
          SendMessages: null
        });
        
        // Log the unlock
        await db.insert(moderationLogs).values({
          guildId: interaction.guild.id,
          userId: interaction.user.id,
          moderatorId: interaction.user.id,
          action: 'unlock',
          reason: `Channel unlocked: ${reason}`,
          createdAt: new Date(),
        });

        const embed = {
          title: '🔓 Channel Unlocked',
          color: 0x00FF00,
          fields: [
            { name: 'Channel', value: `${channel.name}`, inline: true },
            { name: 'Moderator', value: `${interaction.user.tag}`, inline: true },
            { name: 'Reason', value: reason, inline: false },
          ],
          timestamp: new Date().toISOString(),
        };

        await interaction.reply({ embeds: [embed] });
        
        // Send a message to the unlocked channel
        await channel.send({
          embeds: [{
            title: '🔓 Channel Unlocked',
            description: `This channel has been unlocked by ${interaction.user.tag}`,
            color: 0x00FF00,
            fields: [
              { name: 'Reason', value: reason, inline: false },
            ],
            timestamp: new Date().toISOString(),
          }]
        });
      } catch (error) {
        console.error('Error unlocking channel:', error);
        await interaction.reply({
          content: '❌ Failed to unlock channel. Please check permissions and try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('slowmode')
      .setDescription('Set slowmode for a channel')
      .addIntegerOption(option =>
        option.setName('seconds')
          .setDescription('Slowmode duration in seconds (0-21600, 0 to disable)')
          .setRequired(true)
          .setMinValue(0)
          .setMaxValue(21600)
      )
      .addChannelOption(option =>
        option.setName('channel')
          .setDescription('The channel to set slowmode for (defaults to current channel)')
          .setRequired(false)
      )
      .addStringOption(option =>
        option.setName('reason')
          .setDescription('The reason for setting slowmode')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ManageChannels),
    category: 'moderation',
    permissions: ['MANAGE_CHANNELS'],
    usage: '/slowmode <seconds> [channel] [reason]',
    async execute(interaction: any) {
      const seconds = interaction.options.getInteger('seconds');
      const channel = interaction.options.getChannel('channel') || interaction.channel;
      const reason = interaction.options.getString('reason') || 'No reason provided';
      
      try {
        // Set slowmode
        await channel.setRateLimitPerUser(seconds, reason);
        
        // Log the slowmode change
        await db.insert(moderationLogs).values({
          guildId: interaction.guild.id,
          userId: interaction.user.id,
          moderatorId: interaction.user.id,
          action: 'slowmode',
          reason: `Slowmode set to ${seconds}s: ${reason}`,
          createdAt: new Date(),
        });

        const embed = {
          title: seconds === 0 ? '⚡ Slowmode Disabled' : '🐌 Slowmode Enabled',
          color: seconds === 0 ? 0x00FF00 : 0xFFFF00,
          fields: [
            { name: 'Channel', value: `${channel.name}`, inline: true },
            { name: 'Duration', value: seconds === 0 ? 'Disabled' : `${seconds} seconds`, inline: true },
            { name: 'Moderator', value: `${interaction.user.tag}`, inline: true },
            { name: 'Reason', value: reason, inline: false },
          ],
          timestamp: new Date().toISOString(),
        };

        await interaction.reply({ embeds: [embed] });
      } catch (error) {
        console.error('Error setting slowmode:', error);
        await interaction.reply({
          content: '❌ Failed to set slowmode. Please check permissions and try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('purge')
      .setDescription('Purge messages from a channel with filters')
      .addIntegerOption(option =>
        option.setName('amount')
          .setDescription('Number of messages to check (1-100)')
          .setRequired(true)
          .setMinValue(1)
          .setMaxValue(100)
      )
      .addUserOption(option =>
        option.setName('user')
          .setDescription('Only delete messages from this user')
          .setRequired(false)
      )
      .addStringOption(option =>
        option.setName('filter')
          .setDescription('Filter type for messages to delete')
          .setRequired(false)
          .addChoices(
            { name: 'Bots', value: 'bots' },
            { name: 'Embeds', value: 'embeds' },
            { name: 'Files', value: 'files' },
            { name: 'Images', value: 'images' },
            { name: 'Links', value: 'links' }
          )
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ManageMessages),
    category: 'moderation',
    permissions: ['MANAGE_MESSAGES'],
    usage: '/purge <amount> [user] [filter]',
    async execute(interaction: any) {
      const amount = interaction.options.getInteger('amount');
      const user = interaction.options.getUser('user');
      const filter = interaction.options.getString('filter');
      
      try {
        await interaction.deferReply({ ephemeral: true });
        
        const messages = await interaction.channel.messages.fetch({ limit: amount });
        
        let messagesToDelete = messages;
        
        if (user) {
          messagesToDelete = messages.filter((msg: any) => msg.author.id === user.id);
        }
        
        if (filter) {
          messagesToDelete = messagesToDelete.filter((msg: any) => {
            switch (filter) {
              case 'bots':
                return msg.author.bot;
              case 'embeds':
                return msg.embeds.length > 0;
              case 'files':
                return msg.attachments.size > 0;
              case 'images':
                return msg.attachments.some((att: any) => att.contentType?.startsWith('image/'));
              case 'links':
                return msg.content.includes('http://') || msg.content.includes('https://');
              default:
                return true;
            }
          });
        }
        
        if (messagesToDelete.size === 0) {
          await interaction.editReply({
            content: '❌ No messages found matching the criteria.'
          });
          return;
        }
        
        await interaction.channel.bulkDelete(messagesToDelete);
        
        // Log the purge
        await db.insert(moderationLogs).values({
          guildId: interaction.guild.id,
          userId: interaction.user.id,
          moderatorId: interaction.user.id,
          action: 'purge',
          reason: `Purged ${messagesToDelete.size} messages${user ? ` from ${user.tag}` : ''}${filter ? ` with filter: ${filter}` : ''}`,
          createdAt: new Date(),
        });
        
        await interaction.editReply({
          content: `✅ Successfully purged ${messagesToDelete.size} messages${user ? ` from ${user.tag}` : ''}${filter ? ` with filter: ${filter}` : ''}.`
        });
      } catch (error) {
        console.error('Error purging messages:', error);
        await interaction.editReply({
          content: '❌ Failed to purge messages. Messages might be too old or I lack permissions.'
        });
      }
    }
  },
];

function parseDuration(duration: string): number {
  const match = duration.match(/^(\d+)([smhd])$/);
  if (!match) return 600000; // Default 10 minutes
  
  const value = parseInt(match[1]);
  const unit = match[2];
  
  switch (unit) {
    case 's': return value * 1000;
    case 'm': return value * 60 * 1000;
    case 'h': return value * 60 * 60 * 1000;
    case 'd': return value * 24 * 60 * 60 * 1000;
    default: return 600000; // Default 10 minutes
  }
}