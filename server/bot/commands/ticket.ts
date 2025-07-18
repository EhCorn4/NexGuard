import { SlashCommandBuilder, PermissionFlagsBits, ChannelType } from 'discord.js';
import { db } from '../../db';
import { tickets } from '@shared/schema';
import { eq } from 'drizzle-orm';

export const ticketCommands = [
  {
    data: new SlashCommandBuilder()
      .setName('ticket')
      .setDescription('Create a support ticket')
      .addStringOption(option =>
        option.setName('subject')
          .setDescription('The subject of your ticket')
          .setRequired(true)
      )
      .addStringOption(option =>
        option.setName('category')
          .setDescription('The category of your ticket')
          .setRequired(true)
          .addChoices(
            { name: 'General Support', value: 'general' },
            { name: 'Bug Report', value: 'bug' },
            { name: 'Feature Request', value: 'feature' },
            { name: 'Billing Issue', value: 'billing' },
            { name: 'Technical Issue', value: 'technical' }
          )
      )
      .addStringOption(option =>
        option.setName('priority')
          .setDescription('The priority of your ticket')
          .setRequired(false)
          .addChoices(
            { name: 'Low', value: 'low' },
            { name: 'Medium', value: 'medium' },
            { name: 'High', value: 'high' },
            { name: 'Urgent', value: 'urgent' }
          )
      ),
    category: 'ticket',
    permissions: [],
    usage: '/ticket <subject> <category> [priority]',
    async execute(interaction: any) {
      const subject = interaction.options.getString('subject');
      const category = interaction.options.getString('category');
      const priority = interaction.options.getString('priority') || 'medium';
      
      try {
        await interaction.deferReply({ ephemeral: true });
        
        // Generate unique ticket ID
        const ticketCount = await db.select().from(tickets).where(eq(tickets.guildId, interaction.guild.id));
        const ticketId = `TICKET-${String(ticketCount.length + 1).padStart(3, '0')}`;
        
        // Create ticket channel
        const ticketChannel = await interaction.guild.channels.create({
          name: `ticket-${ticketId.toLowerCase()}`,
          type: ChannelType.GuildText,
          topic: `Support ticket: ${subject}`,
          parent: null, // You can set a category here
          permissionOverwrites: [
            {
              id: interaction.guild.id,
              deny: ['ViewChannel'],
            },
            {
              id: interaction.user.id,
              allow: ['ViewChannel', 'SendMessages', 'ReadMessageHistory'],
            },
          ],
        });
        
        // Store ticket in database
        await db.insert(tickets).values({
          ticketId,
          guildId: interaction.guild.id,
          channelId: ticketChannel.id,
          userId: interaction.user.id,
          username: interaction.user.tag,
          subject,
          category,
          priority,
          status: 'open',
          createdAt: new Date(),
          updatedAt: new Date(),
        });
        
        // Send welcome message in ticket channel
        const welcomeEmbed = {
          title: `🎫 Ticket ${ticketId}`,
          description: `Welcome to your support ticket, ${interaction.user}!`,
          color: 0x00FFFF,
          fields: [
            { name: 'Subject', value: subject, inline: true },
            { name: 'Category', value: category, inline: true },
            { name: 'Priority', value: priority, inline: true },
            { name: 'Status', value: 'Open', inline: true },
            { name: 'Created by', value: interaction.user.tag, inline: true },
            { name: 'Created at', value: new Date().toLocaleString(), inline: true },
          ],
          footer: {
            text: 'A staff member will be with you shortly. Please describe your issue in detail.',
          },
        };
        
        await ticketChannel.send({ embeds: [welcomeEmbed] });
        
        await interaction.editReply({
          content: `✅ Ticket created successfully! Please check ${ticketChannel} for your support ticket.`
        });
      } catch (error) {
        console.error('Error creating ticket:', error);
        await interaction.editReply({
          content: '❌ Failed to create ticket. Please try again or contact an administrator.'
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('closeticket')
      .setDescription('Close a support ticket')
      .addStringOption(option =>
        option.setName('reason')
          .setDescription('Reason for closing the ticket')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ManageChannels),
    category: 'ticket',
    permissions: ['MANAGE_CHANNELS'],
    usage: '/closeticket [reason]',
    async execute(interaction: any) {
      const reason = interaction.options.getString('reason') || 'No reason provided';
      
      try {
        // Check if this is a ticket channel
        const [ticket] = await db.select()
          .from(tickets)
          .where(eq(tickets.channelId, interaction.channel.id))
          .limit(1);
        
        if (!ticket) {
          await interaction.reply({
            content: '❌ This command can only be used in ticket channels.',
            ephemeral: true
          });
          return;
        }
        
        // Update ticket status
        await db.update(tickets)
          .set({ 
            status: 'closed',
            closedAt: new Date(),
            updatedAt: new Date()
          })
          .where(eq(tickets.id, ticket.id));
        
        const closeEmbed = {
          title: '🔒 Ticket Closed',
          description: `Ticket ${ticket.ticketId} has been closed.`,
          color: 0xFF0000,
          fields: [
            { name: 'Closed by', value: interaction.user.tag, inline: true },
            { name: 'Reason', value: reason, inline: true },
            { name: 'Closed at', value: new Date().toLocaleString(), inline: true },
          ],
          footer: {
            text: 'This channel will be deleted in 30 seconds.',
          },
        };
        
        await interaction.reply({ embeds: [closeEmbed] });
        
        // Delete the channel after 30 seconds
        setTimeout(async () => {
          try {
            await interaction.channel.delete();
          } catch (error) {
            console.error('Error deleting ticket channel:', error);
          }
        }, 30000);
        
      } catch (error) {
        console.error('Error closing ticket:', error);
        await interaction.reply({
          content: '❌ Failed to close ticket. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('ticketinfo')
      .setDescription('Get information about a ticket')
      .addStringOption(option =>
        option.setName('ticket_id')
          .setDescription('The ticket ID to lookup')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ManageChannels),
    category: 'ticket',
    permissions: ['MANAGE_CHANNELS'],
    usage: '/ticketinfo [ticket_id]',
    async execute(interaction: any) {
      const ticketId = interaction.options.getString('ticket_id');
      
      try {
        let ticket;
        
        if (ticketId) {
          // Look up specific ticket
          [ticket] = await db.select()
            .from(tickets)
            .where(eq(tickets.ticketId, ticketId))
            .limit(1);
        } else {
          // Get current channel ticket
          [ticket] = await db.select()
            .from(tickets)
            .where(eq(tickets.channelId, interaction.channel.id))
            .limit(1);
        }
        
        if (!ticket) {
          await interaction.reply({
            content: '❌ Ticket not found.',
            ephemeral: true
          });
          return;
        }
        
        const statusEmoji = ticket.status === 'open' ? '🟢' : '🔴';
        const priorityEmoji = {
          low: '🔵',
          medium: '🟡',
          high: '🟠',
          urgent: '🔴'
        }[ticket.priority as string] || '🟡';
        
        const embed = {
          title: `🎫 Ticket Information - ${ticket.ticketId}`,
          color: ticket.status === 'open' ? 0x00FF00 : 0xFF0000,
          fields: [
            { name: 'Subject', value: ticket.subject, inline: true },
            { name: 'Category', value: ticket.category, inline: true },
            { name: 'Priority', value: `${priorityEmoji} ${ticket.priority}`, inline: true },
            { name: 'Status', value: `${statusEmoji} ${ticket.status}`, inline: true },
            { name: 'Created by', value: ticket.username, inline: true },
            { name: 'User ID', value: ticket.userId, inline: true },
            { name: 'Created at', value: new Date(ticket.createdAt).toLocaleString(), inline: true },
            { name: 'Updated at', value: new Date(ticket.updatedAt).toLocaleString(), inline: true },
          ],
          footer: {
            text: `Ticket ID: ${ticket.ticketId} | Channel ID: ${ticket.channelId}`,
          },
        };
        
        if (ticket.closedAt) {
          embed.fields.push({
            name: 'Closed at',
            value: new Date(ticket.closedAt).toLocaleString(),
            inline: true
          });
        }
        
        if (ticket.assignedTo) {
          embed.fields.push({
            name: 'Assigned to',
            value: ticket.assignedTo,
            inline: true
          });
        }
        
        await interaction.reply({ embeds: [embed] });
      } catch (error) {
        console.error('Error fetching ticket info:', error);
        await interaction.reply({
          content: '❌ Failed to fetch ticket information.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('tickets')
      .setDescription('List all tickets')
      .addStringOption(option =>
        option.setName('status')
          .setDescription('Filter by status')
          .setRequired(false)
          .addChoices(
            { name: 'Open', value: 'open' },
            { name: 'Closed', value: 'closed' },
            { name: 'All', value: 'all' }
          )
      )
      .addUserOption(option =>
        option.setName('user')
          .setDescription('Filter by user')
          .setRequired(false)
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ManageChannels),
    category: 'ticket',
    permissions: ['MANAGE_CHANNELS'],
    usage: '/tickets [status] [user]',
    async execute(interaction: any) {
      const status = interaction.options.getString('status') || 'all';
      const user = interaction.options.getUser('user');
      
      try {
        let query = db.select().from(tickets).where(eq(tickets.guildId, interaction.guild.id));
        
        // Apply filters
        if (status !== 'all') {
          query = query.where(eq(tickets.status, status));
        }
        
        if (user) {
          query = query.where(eq(tickets.userId, user.id));
        }
        
        const ticketsList = await query.limit(10).orderBy(tickets.createdAt);
        
        if (ticketsList.length === 0) {
          await interaction.reply({
            content: '📋 No tickets found matching your criteria.',
            ephemeral: true
          });
          return;
        }
        
        const embed = {
          title: '🎫 Tickets List',
          description: `Found ${ticketsList.length} ticket(s)`,
          color: 0x00FFFF,
          fields: ticketsList.map(ticket => ({
            name: `${ticket.ticketId} - ${ticket.subject}`,
            value: `**User:** ${ticket.username}\n**Status:** ${ticket.status}\n**Priority:** ${ticket.priority}\n**Category:** ${ticket.category}\n**Created:** ${new Date(ticket.createdAt).toLocaleDateString()}`,
            inline: false
          })),
          footer: {
            text: 'Use /ticketinfo <ticket_id> for more details',
          },
        };
        
        await interaction.reply({ embeds: [embed] });
      } catch (error) {
        console.error('Error fetching tickets:', error);
        await interaction.reply({
          content: '❌ Failed to fetch tickets list.',
          ephemeral: true
        });
      }
    }
  },
];