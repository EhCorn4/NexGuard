import { SlashCommandBuilder, PermissionFlagsBits } from 'discord.js';
import { db } from '../../db';
import { moderationLogs, guilds, banList, warnHistory } from '@shared/schema';
import { eq, desc, and, count, sum } from 'drizzle-orm';

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

        // Add to warn history with severity based on reason
        const severity = reason.toLowerCase().includes('severe') ? 'severe' : 
                        reason.toLowerCase().includes('high') ? 'high' : 
                        reason.toLowerCase().includes('low') ? 'low' : 'medium';
        
        const points = severity === 'severe' ? 3 : severity === 'high' ? 2 : 1;
        
        await db.insert(warnHistory).values({
          guildId: interaction.guild.id,
          userId: user.id,
          username: user.tag,
          moderatorId: interaction.user.id,
          moderatorName: interaction.user.tag,
          reason,
          severity,
          points,
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
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

        // Add to ban list
        await db.insert(banList).values({
          guildId: interaction.guild.id,
          userId: user.id,
          username: user.tag,
          moderatorId: interaction.user.id,
          moderatorName: interaction.user.tag,
          reason,
          banType: 'permanent',
          isActive: true,
          appealable: true,
          createdAt: new Date(),
          updatedAt: new Date(),
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

  {
    data: new SlashCommandBuilder()
      .setName('banlist')
      .setDescription('Manage server ban list')
      .addSubcommand(subcommand =>
        subcommand
          .setName('view')
          .setDescription('View the server ban list')
          .addIntegerOption(option =>
            option.setName('page')
              .setDescription('Page number (default: 1)')
              .setRequired(false)
              .setMinValue(1)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('search')
          .setDescription('Search for a banned user')
          .addStringOption(option =>
            option.setName('query')
              .setDescription('Username or User ID to search for')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('appeal')
          .setDescription('Handle ban appeal')
          .addStringOption(option =>
            option.setName('user_id')
              .setDescription('User ID to handle appeal for')
              .setRequired(true)
          )
          .addStringOption(option =>
            option.setName('action')
              .setDescription('Appeal action')
              .setRequired(true)
              .addChoices(
                { name: 'Approve', value: 'approve' },
                { name: 'Deny', value: 'deny' }
              )
          )
          .addStringOption(option =>
            option.setName('reason')
              .setDescription('Reason for appeal decision')
              .setRequired(false)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('remove')
          .setDescription('Remove a ban from the list')
          .addStringOption(option =>
            option.setName('user_id')
              .setDescription('User ID to remove from ban list')
              .setRequired(true)
          )
          .addStringOption(option =>
            option.setName('reason')
              .setDescription('Reason for removing the ban')
              .setRequired(false)
          )
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.BanMembers),
    category: 'moderation',
    permissions: ['BAN_MEMBERS'],
    usage: '/banlist <subcommand> [options]',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      
      try {
        switch (subcommand) {
          case 'view':
            const page = interaction.options.getInteger('page') || 1;
            const limit = 10;
            const offset = (page - 1) * limit;
            
            const [bans, totalCount] = await Promise.all([
              db.select()
                .from(banList)
                .where(and(eq(banList.guildId, interaction.guild.id), eq(banList.isActive, true)))
                .orderBy(desc(banList.createdAt))
                .limit(limit)
                .offset(offset),
              db.select({ count: count() })
                .from(banList)
                .where(and(eq(banList.guildId, interaction.guild.id), eq(banList.isActive, true)))
            ]);
            
            const totalPages = Math.ceil(totalCount[0].count / limit);
            
            if (bans.length === 0) {
              await interaction.reply({
                embeds: [{
                  title: '📋 Server Ban List',
                  description: 'No active bans found.',
                  color: 0x00FF00,
                  timestamp: new Date().toISOString(),
                }]
              });
              return;
            }
            
            const banFields = bans.map(ban => ({
              name: `${ban.username} (${ban.userId})`,
              value: `**Reason:** ${ban.reason || 'No reason provided'}\n**Moderator:** ${ban.moderatorName}\n**Date:** <t:${Math.floor(ban.createdAt.getTime() / 1000)}:R>\n**Type:** ${ban.banType}${ban.expiresAt ? `\n**Expires:** <t:${Math.floor(ban.expiresAt.getTime() / 1000)}:R>` : ''}`,
              inline: false
            }));
            
            await interaction.reply({
              embeds: [{
                title: '📋 Server Ban List',
                color: 0xFF0000,
                fields: banFields,
                footer: {
                  text: `Page ${page} of ${totalPages} | Total bans: ${totalCount[0].count}`
                },
                timestamp: new Date().toISOString(),
              }]
            });
            break;
            
          case 'search':
            const query = interaction.options.getString('query');
            
            const searchResults = await db.select()
              .from(banList)
              .where(and(
                eq(banList.guildId, interaction.guild.id),
                eq(banList.isActive, true),
                // Search by username or user ID
                query.includes('#') ? eq(banList.username, query) : eq(banList.userId, query)
              ));
            
            if (searchResults.length === 0) {
              await interaction.reply({
                embeds: [{
                  title: '🔍 Ban Search Results',
                  description: `No active bans found for "${query}".`,
                  color: 0x00FF00,
                  timestamp: new Date().toISOString(),
                }]
              });
              return;
            }
            
            const results = searchResults.map(ban => ({
              name: `${ban.username} (${ban.userId})`,
              value: `**Reason:** ${ban.reason || 'No reason provided'}\n**Moderator:** ${ban.moderatorName}\n**Date:** <t:${Math.floor(ban.createdAt.getTime() / 1000)}:F>\n**Type:** ${ban.banType}${ban.expiresAt ? `\n**Expires:** <t:${Math.floor(ban.expiresAt.getTime() / 1000)}:R>` : ''}`,
              inline: false
            }));
            
            await interaction.reply({
              embeds: [{
                title: '🔍 Ban Search Results',
                color: 0xFF0000,
                fields: results,
                timestamp: new Date().toISOString(),
              }]
            });
            break;
            
          case 'appeal':
            const appealUserId = interaction.options.getString('user_id');
            const appealAction = interaction.options.getString('action');
            const appealReason = interaction.options.getString('reason') || 'No reason provided';
            
            const [banToAppeal] = await db.select()
              .from(banList)
              .where(and(
                eq(banList.guildId, interaction.guild.id),
                eq(banList.userId, appealUserId),
                eq(banList.isActive, true)
              ))
              .limit(1);
            
            if (!banToAppeal) {
              await interaction.reply({
                content: '❌ No active ban found for this user.',
                ephemeral: true
              });
              return;
            }
            
            if (appealAction === 'approve') {
              await db.update(banList)
                .set({
                  isActive: false,
                  appealReason: appealReason,
                  appealedAt: new Date(),
                  updatedAt: new Date()
                })
                .where(eq(banList.id, banToAppeal.id));
              
              // Attempt to unban the user
              try {
                await interaction.guild.members.unban(appealUserId, `Ban appeal approved by ${interaction.user.tag}: ${appealReason}`);
              } catch (error) {
                console.error('Failed to unban user:', error);
              }
              
              await interaction.reply({
                embeds: [{
                  title: '✅ Ban Appeal Approved',
                  description: `Ban appeal for ${banToAppeal.username} has been approved.`,
                  color: 0x00FF00,
                  fields: [
                    { name: 'User', value: `${banToAppeal.username} (${banToAppeal.userId})`, inline: true },
                    { name: 'Approved by', value: interaction.user.tag, inline: true },
                    { name: 'Reason', value: appealReason, inline: false }
                  ],
                  timestamp: new Date().toISOString(),
                }]
              });
            } else {
              await db.update(banList)
                .set({
                  appealReason: appealReason,
                  appealedAt: new Date(),
                  updatedAt: new Date()
                })
                .where(eq(banList.id, banToAppeal.id));
              
              await interaction.reply({
                embeds: [{
                  title: '❌ Ban Appeal Denied',
                  description: `Ban appeal for ${banToAppeal.username} has been denied.`,
                  color: 0xFF0000,
                  fields: [
                    { name: 'User', value: `${banToAppeal.username} (${banToAppeal.userId})`, inline: true },
                    { name: 'Denied by', value: interaction.user.tag, inline: true },
                    { name: 'Reason', value: appealReason, inline: false }
                  ],
                  timestamp: new Date().toISOString(),
                }]
              });
            }
            break;
            
          case 'remove':
            const removeUserId = interaction.options.getString('user_id');
            const removeReason = interaction.options.getString('reason') || 'No reason provided';
            
            const [banToRemove] = await db.select()
              .from(banList)
              .where(and(
                eq(banList.guildId, interaction.guild.id),
                eq(banList.userId, removeUserId),
                eq(banList.isActive, true)
              ))
              .limit(1);
            
            if (!banToRemove) {
              await interaction.reply({
                content: '❌ No active ban found for this user.',
                ephemeral: true
              });
              return;
            }
            
            await db.update(banList)
              .set({
                isActive: false,
                updatedAt: new Date()
              })
              .where(eq(banList.id, banToRemove.id));
            
            await interaction.reply({
              embeds: [{
                title: '✅ Ban Removed',
                description: `Ban for ${banToRemove.username} has been removed from the ban list.`,
                color: 0x00FF00,
                fields: [
                  { name: 'User', value: `${banToRemove.username} (${banToRemove.userId})`, inline: true },
                  { name: 'Reason', value: removeReason, inline: false }
                ],
                timestamp: new Date().toISOString(),
              }]
            });
            break;
        }
      } catch (error) {
        console.error('Error managing ban list:', error);
        await interaction.reply({
          content: '❌ Failed to manage ban list. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('warnhistory')
      .setDescription('Manage warning history')
      .addSubcommand(subcommand =>
        subcommand
          .setName('view')
          .setDescription('View warning history for a user')
          .addUserOption(option =>
            option.setName('user')
              .setDescription('User to view warning history for')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('clear')
          .setDescription('Clear warning history for a user')
          .addUserOption(option =>
            option.setName('user')
              .setDescription('User to clear warning history for')
              .setRequired(true)
          )
          .addStringOption(option =>
            option.setName('reason')
              .setDescription('Reason for clearing warnings')
              .setRequired(false)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('remove')
          .setDescription('Remove a specific warning')
          .addIntegerOption(option =>
            option.setName('warning_id')
              .setDescription('Warning ID to remove')
              .setRequired(true)
          )
          .addStringOption(option =>
            option.setName('reason')
              .setDescription('Reason for removing the warning')
              .setRequired(false)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('stats')
          .setDescription('View server warning statistics')
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('top')
          .setDescription('View users with most warnings')
          .addIntegerOption(option =>
            option.setName('limit')
              .setDescription('Number of users to show (default: 10)')
              .setRequired(false)
              .setMinValue(1)
              .setMaxValue(25)
          )
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ModerateMembers),
    category: 'moderation',
    permissions: ['MODERATE_MEMBERS'],
    usage: '/warnhistory <subcommand> [options]',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      
      try {
        switch (subcommand) {
          case 'view':
            const user = interaction.options.getUser('user');
            
            const [warnings, totalPoints] = await Promise.all([
              db.select()
                .from(warnHistory)
                .where(and(
                  eq(warnHistory.guildId, interaction.guild.id),
                  eq(warnHistory.userId, user.id),
                  eq(warnHistory.isActive, true)
                ))
                .orderBy(desc(warnHistory.createdAt)),
              db.select({ total: sum(warnHistory.points) })
                .from(warnHistory)
                .where(and(
                  eq(warnHistory.guildId, interaction.guild.id),
                  eq(warnHistory.userId, user.id),
                  eq(warnHistory.isActive, true)
                ))
            ]);
            
            if (warnings.length === 0) {
              await interaction.reply({
                embeds: [{
                  title: '📋 Warning History',
                  description: `${user.tag} has no warnings.`,
                  color: 0x00FF00,
                  timestamp: new Date().toISOString(),
                }]
              });
              return;
            }
            
            const warningFields = warnings.slice(0, 10).map(warning => ({
              name: `Warning #${warning.id} - ${warning.severity.toUpperCase()}`,
              value: `**Reason:** ${warning.reason}\n**Moderator:** ${warning.moderatorName}\n**Points:** ${warning.points}\n**Date:** <t:${Math.floor(warning.createdAt.getTime() / 1000)}:R>${warning.expiresAt ? `\n**Expires:** <t:${Math.floor(warning.expiresAt.getTime() / 1000)}:R>` : ''}`,
              inline: false
            }));
            
            await interaction.reply({
              embeds: [{
                title: `📋 Warning History - ${user.tag}`,
                color: 0xFF0000,
                fields: warningFields,
                footer: {
                  text: `Total warnings: ${warnings.length} | Total points: ${totalPoints[0].total || 0}`
                },
                timestamp: new Date().toISOString(),
              }]
            });
            break;
            
          case 'clear':
            const clearUser = interaction.options.getUser('user');
            const clearReason = interaction.options.getString('reason') || 'No reason provided';
            
            const activeWarnings = await db.select()
              .from(warnHistory)
              .where(and(
                eq(warnHistory.guildId, interaction.guild.id),
                eq(warnHistory.userId, clearUser.id),
                eq(warnHistory.isActive, true)
              ));
            
            if (activeWarnings.length === 0) {
              await interaction.reply({
                content: '❌ No active warnings found for this user.',
                ephemeral: true
              });
              return;
            }
            
            await db.update(warnHistory)
              .set({
                isActive: false,
                updatedAt: new Date()
              })
              .where(and(
                eq(warnHistory.guildId, interaction.guild.id),
                eq(warnHistory.userId, clearUser.id),
                eq(warnHistory.isActive, true)
              ));
            
            await interaction.reply({
              embeds: [{
                title: '✅ Warning History Cleared',
                description: `All warnings for ${clearUser.tag} have been cleared.`,
                color: 0x00FF00,
                fields: [
                  { name: 'User', value: `${clearUser.tag} (${clearUser.id})`, inline: true },
                  { name: 'Cleared by', value: interaction.user.tag, inline: true },
                  { name: 'Warnings Cleared', value: activeWarnings.length.toString(), inline: true },
                  { name: 'Reason', value: clearReason, inline: false }
                ],
                timestamp: new Date().toISOString(),
              }]
            });
            break;
            
          case 'remove':
            const warningId = interaction.options.getInteger('warning_id');
            const removeReason = interaction.options.getString('reason') || 'No reason provided';
            
            const [warningToRemove] = await db.select()
              .from(warnHistory)
              .where(and(
                eq(warnHistory.guildId, interaction.guild.id),
                eq(warnHistory.id, warningId),
                eq(warnHistory.isActive, true)
              ))
              .limit(1);
            
            if (!warningToRemove) {
              await interaction.reply({
                content: '❌ Warning not found or already removed.',
                ephemeral: true
              });
              return;
            }
            
            await db.update(warnHistory)
              .set({
                isActive: false,
                updatedAt: new Date()
              })
              .where(eq(warnHistory.id, warningId));
            
            await interaction.reply({
              embeds: [{
                title: '✅ Warning Removed',
                description: `Warning #${warningId} has been removed.`,
                color: 0x00FF00,
                fields: [
                  { name: 'User', value: `${warningToRemove.username} (${warningToRemove.userId})`, inline: true },
                  { name: 'Original Reason', value: warningToRemove.reason, inline: false },
                  { name: 'Removal Reason', value: removeReason, inline: false }
                ],
                timestamp: new Date().toISOString(),
              }]
            });
            break;
            
          case 'stats':
            const [totalWarningsCount, activeWarningsCount, totalPointsSum] = await Promise.all([
              db.select({ count: count() })
                .from(warnHistory)
                .where(eq(warnHistory.guildId, interaction.guild.id)),
              db.select({ count: count() })
                .from(warnHistory)
                .where(and(eq(warnHistory.guildId, interaction.guild.id), eq(warnHistory.isActive, true))),
              db.select({ total: sum(warnHistory.points) })
                .from(warnHistory)
                .where(and(eq(warnHistory.guildId, interaction.guild.id), eq(warnHistory.isActive, true)))
            ]);
            
            await interaction.reply({
              embeds: [{
                title: '📊 Server Warning Statistics',
                color: 0x00FFFF,
                fields: [
                  { name: 'Total Warnings', value: totalWarningsCount[0].count.toString(), inline: true },
                  { name: 'Active Warnings', value: activeWarningsCount[0].count.toString(), inline: true },
                  { name: 'Total Points', value: (totalPointsSum[0].total || 0).toString(), inline: true },
                  { name: 'Expired/Removed', value: (totalWarningsCount[0].count - activeWarningsCount[0].count).toString(), inline: true }
                ],
                timestamp: new Date().toISOString(),
              }]
            });
            break;
            
          case 'top':
            const limit = interaction.options.getInteger('limit') || 10;
            
            const topWarnings = await db.select({
              userId: warnHistory.userId,
              username: warnHistory.username,
              count: count(),
              totalPoints: sum(warnHistory.points)
            })
            .from(warnHistory)
            .where(and(eq(warnHistory.guildId, interaction.guild.id), eq(warnHistory.isActive, true)))
            .groupBy(warnHistory.userId, warnHistory.username)
            .orderBy(desc(count()))
            .limit(limit);
            
            if (topWarnings.length === 0) {
              await interaction.reply({
                embeds: [{
                  title: '📋 Top Warning List',
                  description: 'No warnings found in this server.',
                  color: 0x00FF00,
                  timestamp: new Date().toISOString(),
                }]
              });
              return;
            }
            
            const topList = topWarnings.map((entry, index) => 
              `**${index + 1}.** ${entry.username} (${entry.userId})\n${entry.count} warnings • ${entry.totalPoints} points`
            ).join('\n\n');
            
            await interaction.reply({
              embeds: [{
                title: '📋 Top Warning List',
                description: topList,
                color: 0xFF0000,
                footer: {
                  text: `Showing top ${topWarnings.length} users with most warnings`
                },
                timestamp: new Date().toISOString(),
              }]
            });
            break;
        }
      } catch (error) {
        console.error('Error managing warning history:', error);
        await interaction.reply({
          content: '❌ Failed to manage warning history. Please try again.',
          ephemeral: true
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