import { SlashCommandBuilder, PermissionFlagsBits } from 'discord.js';
import { db } from '../../db';
import { moderationLogs } from '@shared/schema';

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