import { SlashCommandBuilder, PermissionFlagsBits, ChannelType } from 'discord.js';
import { db } from '../../db';
import { tickets, ticketNotes, ticketTemplates, guilds } from '@shared/schema';
import { eq, desc, and, count, avg, sql } from 'drizzle-orm';

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
        option.setName('description')
          .setDescription('Detailed description of your issue')
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
            { name: 'Urgent', value: 'urgent' },
            { name: 'Critical', value: 'critical' }
          )
      ),
    category: 'ticket',
    permissions: [],
    usage: '/ticket <subject> <description> <category> [priority]',
    async execute(interaction: any) {
      const subject = interaction.options.getString('subject');
      const description = interaction.options.getString('description');
      const category = interaction.options.getString('category');
      const priority = interaction.options.getString('priority') || 'medium';
      
      try {
        await interaction.deferReply({ ephemeral: true });
        
        // Check if tickets are enabled
        const [guildSettings] = await db.select()
          .from(guilds)
          .where(eq(guilds.id, interaction.guild.id))
          .limit(1);
        
        if (!guildSettings?.ticketEnabled) {
          await interaction.editReply({
            content: '❌ Ticket system is disabled for this server.',
          });
          return;
        }
        
        // Generate unique ticket ID
        const ticketCount = await db.select().from(tickets).where(eq(tickets.guildId, interaction.guild.id));
        const ticketId = `TICKET-${String(ticketCount.length + 1).padStart(3, '0')}`;
        
        // Calculate SLA deadline based on priority
        const slaHours = { low: 72, medium: 48, high: 24, urgent: 8, critical: 4 };
        const slaDeadline = new Date(Date.now() + (slaHours[priority] || 48) * 60 * 60 * 1000);
        
        // Create ticket channel
        const ticketChannel = await interaction.guild.channels.create({
          name: `ticket-${ticketId.toLowerCase()}`,
          type: ChannelType.GuildText,
          topic: `Support ticket: ${subject}`,
          parent: null,
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
        
        // Add staff permissions
        if (guildSettings.adminRoleId) {
          await ticketChannel.permissionOverwrites.edit(guildSettings.adminRoleId, {
            ViewChannel: true,
            SendMessages: true,
            ReadMessageHistory: true,
            ManageMessages: true,
          });
        }
        
        if (guildSettings.moderatorRoleId) {
          await ticketChannel.permissionOverwrites.edit(guildSettings.moderatorRoleId, {
            ViewChannel: true,
            SendMessages: true,
            ReadMessageHistory: true,
          });
        }
        
        // Store ticket in database
        const [newTicket] = await db.insert(tickets).values({
          ticketId,
          guildId: interaction.guild.id,
          channelId: ticketChannel.id,
          userId: interaction.user.id,
          username: interaction.user.tag,
          subject,
          description,
          category,
          priority,
          status: 'open',
          slaDeadline,
          createdAt: new Date(),
          updatedAt: new Date(),
        }).returning();
        
        // Send welcome message in ticket channel
        const priorityEmojis = { low: '🟢', medium: '🟡', high: '🟠', urgent: '🔴', critical: '🔥' };
        const welcomeEmbed = {
          title: `🎫 Ticket ${ticketId}`,
          description: `Welcome to your support ticket, ${interaction.user}!`,
          color: 0x00FFFF,
          fields: [
            { name: 'Subject', value: subject, inline: true },
            { name: 'Category', value: category, inline: true },
            { name: 'Priority', value: `${priorityEmojis[priority]} ${priority.toUpperCase()}`, inline: true },
            { name: 'Status', value: '🟢 Open', inline: true },
            { name: 'SLA Deadline', value: `<t:${Math.floor(slaDeadline.getTime() / 1000)}:R>`, inline: true },
            { name: 'Description', value: description, inline: false },
          ],
          footer: {
            text: 'A staff member will be with you shortly. Please provide any additional details below.',
          },
          timestamp: new Date().toISOString(),
        };
        
        await ticketChannel.send({ embeds: [welcomeEmbed] });
        
        // Log ticket creation
        await db.insert(ticketNotes).values({
          ticketId: newTicket.ticketId,
          guildId: interaction.guild.id,
          authorId: interaction.user.id,
          authorName: interaction.user.tag,
          content: `Ticket created: ${subject}`,
          isInternal: false,
          noteType: 'status_change',
          createdAt: new Date(),
        });
        
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
      .setName('ticketmanage')
      .setDescription('Manage support tickets')
      .addSubcommand(subcommand =>
        subcommand
          .setName('assign')
          .setDescription('Assign a ticket to a staff member')
          .addUserOption(option =>
            option.setName('user')
              .setDescription('Staff member to assign the ticket to')
              .setRequired(true)
          )
          .addStringOption(option =>
            option.setName('reason')
              .setDescription('Reason for assignment')
              .setRequired(false)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('status')
          .setDescription('Change ticket status')
          .addStringOption(option =>
            option.setName('status')
              .setDescription('New status for the ticket')
              .setRequired(true)
              .addChoices(
                { name: 'Open', value: 'open' },
                { name: 'In Progress', value: 'in-progress' },
                { name: 'Pending', value: 'pending' },
                { name: 'Resolved', value: 'resolved' },
                { name: 'Closed', value: 'closed' }
              )
          )
          .addStringOption(option =>
            option.setName('reason')
              .setDescription('Reason for status change')
              .setRequired(false)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('priority')
          .setDescription('Change ticket priority')
          .addStringOption(option =>
            option.setName('priority')
              .setDescription('New priority for the ticket')
              .setRequired(true)
              .addChoices(
                { name: 'Low', value: 'low' },
                { name: 'Medium', value: 'medium' },
                { name: 'High', value: 'high' },
                { name: 'Urgent', value: 'urgent' },
                { name: 'Critical', value: 'critical' }
              )
          )
          .addStringOption(option =>
            option.setName('reason')
              .setDescription('Reason for priority change')
              .setRequired(false)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('note')
          .setDescription('Add an internal note to the ticket')
          .addStringOption(option =>
            option.setName('note')
              .setDescription('Internal note content')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('escalate')
          .setDescription('Escalate the ticket to higher level')
          .addStringOption(option =>
            option.setName('reason')
              .setDescription('Reason for escalation')
              .setRequired(true)
          )
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('info')
          .setDescription('Get detailed information about the ticket')
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ManageMessages),
    category: 'ticket',
    permissions: ['MANAGE_MESSAGES'],
    usage: '/ticketmanage <subcommand> [options]',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      
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
        
        switch (subcommand) {
          case 'assign':
            const assignUser = interaction.options.getUser('user');
            const assignReason = interaction.options.getString('reason') || 'No reason provided';
            
            await db.update(tickets)
              .set({
                assignedTo: assignUser.id,
                assignedBy: interaction.user.id,
                status: 'in-progress',
                updatedAt: new Date()
              })
              .where(eq(tickets.id, ticket.id));
            
            await db.insert(ticketNotes).values({
              ticketId: ticket.ticketId,
              guildId: interaction.guild.id,
              authorId: interaction.user.id,
              authorName: interaction.user.tag,
              content: `Ticket assigned to ${assignUser.tag} - ${assignReason}`,
              isInternal: true,
              noteType: 'assignment',
              createdAt: new Date(),
            });
            
            await interaction.reply({
              embeds: [{
                title: '✅ Ticket Assigned',
                description: `Ticket has been assigned to ${assignUser}`,
                color: 0x00FF00,
                fields: [
                  { name: 'Reason', value: assignReason, inline: true },
                  { name: 'Status', value: '🔄 In Progress', inline: true }
                ],
                timestamp: new Date().toISOString(),
              }]
            });
            break;
            
          case 'status':
            const newStatus = interaction.options.getString('status');
            const statusReason = interaction.options.getString('reason') || 'No reason provided';
            
            const statusEmojis = {
              'open': '🟢',
              'in-progress': '🔄',
              'pending': '🟡',
              'resolved': '✅',
              'closed': '🔴'
            };
            
            const updateData: any = {
              status: newStatus,
              updatedAt: new Date()
            };
            
            if (newStatus === 'resolved') {
              updateData.resolvedAt = new Date();
            } else if (newStatus === 'closed') {
              updateData.closedAt = new Date();
            }
            
            await db.update(tickets)
              .set(updateData)
              .where(eq(tickets.id, ticket.id));
            
            await db.insert(ticketNotes).values({
              ticketId: ticket.ticketId,
              guildId: interaction.guild.id,
              authorId: interaction.user.id,
              authorName: interaction.user.tag,
              content: `Status changed to ${newStatus} - ${statusReason}`,
              isInternal: true,
              noteType: 'status_change',
              createdAt: new Date(),
            });
            
            await interaction.reply({
              embeds: [{
                title: '✅ Status Updated',
                description: `Ticket status changed to ${statusEmojis[newStatus]} ${newStatus.toUpperCase()}`,
                color: 0x00FF00,
                fields: [
                  { name: 'Reason', value: statusReason, inline: true },
                  { name: 'Previous Status', value: ticket.status, inline: true }
                ],
                timestamp: new Date().toISOString(),
              }]
            });
            break;
            
          case 'priority':
            const newPriority = interaction.options.getString('priority');
            const priorityReason = interaction.options.getString('reason') || 'No reason provided';
            
            const priorityEmojis = { low: '🟢', medium: '🟡', high: '🟠', urgent: '🔴', critical: '🔥' };
            
            await db.update(tickets)
              .set({
                priority: newPriority,
                updatedAt: new Date()
              })
              .where(eq(tickets.id, ticket.id));
            
            await db.insert(ticketNotes).values({
              ticketId: ticket.ticketId,
              guildId: interaction.guild.id,
              authorId: interaction.user.id,
              authorName: interaction.user.tag,
              content: `Priority changed to ${newPriority} - ${priorityReason}`,
              isInternal: true,
              noteType: 'status_change',
              createdAt: new Date(),
            });
            
            await interaction.reply({
              embeds: [{
                title: '✅ Priority Updated',
                description: `Ticket priority changed to ${priorityEmojis[newPriority]} ${newPriority.toUpperCase()}`,
                color: 0x00FF00,
                fields: [
                  { name: 'Reason', value: priorityReason, inline: true },
                  { name: 'Previous Priority', value: ticket.priority, inline: true }
                ],
                timestamp: new Date().toISOString(),
              }]
            });
            break;
            
          case 'note':
            const noteContent = interaction.options.getString('note');
            
            await db.insert(ticketNotes).values({
              ticketId: ticket.ticketId,
              guildId: interaction.guild.id,
              authorId: interaction.user.id,
              authorName: interaction.user.tag,
              content: noteContent,
              isInternal: true,
              noteType: 'message',
              createdAt: new Date(),
            });
            
            await interaction.reply({
              embeds: [{
                title: '📝 Internal Note Added',
                description: noteContent,
                color: 0x0099FF,
                fields: [
                  { name: 'Visibility', value: 'Internal Only', inline: true }
                ],
                timestamp: new Date().toISOString(),
              }],
              ephemeral: true
            });
            break;
            
          case 'escalate':
            const escalateReason = interaction.options.getString('reason');
            const newEscalationLevel = (ticket.escalationLevel || 0) + 1;
            
            await db.update(tickets)
              .set({
                escalationLevel: newEscalationLevel,
                priority: 'urgent',
                updatedAt: new Date()
              })
              .where(eq(tickets.id, ticket.id));
            
            await db.insert(ticketNotes).values({
              ticketId: ticket.ticketId,
              guildId: interaction.guild.id,
              authorId: interaction.user.id,
              authorName: interaction.user.tag,
              content: `Ticket escalated to level ${newEscalationLevel} - ${escalateReason}`,
              isInternal: true,
              noteType: 'escalation',
              createdAt: new Date(),
            });
            
            const escalationLevels = {
              0: 'Normal',
              1: 'Escalated',
              2: 'Manager Level',
              3: 'Director Level'
            };
            
            await interaction.reply({
              embeds: [{
                title: '🚨 Ticket Escalated',
                description: `Ticket escalated to ${escalationLevels[newEscalationLevel]} and priority set to URGENT`,
                color: 0xFF0000,
                fields: [
                  { name: 'Escalation Level', value: `Level ${newEscalationLevel}`, inline: true },
                  { name: 'Reason', value: escalateReason, inline: false }
                ],
                timestamp: new Date().toISOString(),
              }]
            });
            break;
            
          case 'info':
            const ticketNotesList = await db.select()
              .from(ticketNotes)
              .where(eq(ticketNotes.ticketId, ticket.ticketId))
              .orderBy(desc(ticketNotes.createdAt));
            
            const statusEmojis2 = {
              'open': '🟢',
              'in-progress': '🔄',
              'pending': '🟡',
              'resolved': '✅',
              'closed': '🔴'
            };
            
            const priorityEmojis2 = { low: '🟢', medium: '🟡', high: '🟠', urgent: '🔴', critical: '🔥' };
            
            const assignedUser = ticket.assignedTo ? `<@${ticket.assignedTo}>` : 'Unassigned';
            const escalationLevel = ticket.escalationLevel || 0;
            
            await interaction.reply({
              embeds: [{
                title: `🎫 Ticket Information - ${ticket.ticketId}`,
                color: 0x00FFFF,
                fields: [
                  { name: 'Subject', value: ticket.subject, inline: true },
                  { name: 'Category', value: ticket.category, inline: true },
                  { name: 'Status', value: `${statusEmojis2[ticket.status]} ${ticket.status.toUpperCase()}`, inline: true },
                  { name: 'Priority', value: `${priorityEmojis2[ticket.priority]} ${ticket.priority.toUpperCase()}`, inline: true },
                  { name: 'Assigned To', value: assignedUser, inline: true },
                  { name: 'Escalation Level', value: `Level ${escalationLevel}`, inline: true },

                  { name: 'Created at', value: `<t:${Math.floor(ticket.createdAt.getTime() / 1000)}:F>`, inline: true },
                  { name: 'Last Updated', value: `<t:${Math.floor(ticket.updatedAt.getTime() / 1000)}:R>`, inline: true },
                  { name: 'Description', value: ticket.description || 'No description provided', inline: false }
                ],
                timestamp: new Date().toISOString(),
              }],
              ephemeral: true
            });
            
            if (ticketNotesList.length > 0) {
              const recentNotes = ticketNotesList.slice(0, 5);
              const notesText = recentNotes.map(note => 
                `**${note.authorName}** (${note.isInternal ? '🔒 Internal' : '📢 Public'}) - <t:${Math.floor(note.createdAt.getTime() / 1000)}:R>\n${note.content}`
              ).join('\n\n');
              
              await interaction.followUp({
                embeds: [{
                  title: '📝 Recent Activity',
                  description: notesText,
                  color: 0x0099FF,
                  footer: {
                    text: `Showing ${recentNotes.length} of ${ticketNotesList.length} total notes`
                  }
                }],
                ephemeral: true
              });
            }
            break;
        }
      } catch (error) {
        console.error('Error managing ticket:', error);
        await interaction.reply({
          content: '❌ Failed to manage ticket. Please try again.',
          ephemeral: true
        });
      }
    }
  },

  {
    data: new SlashCommandBuilder()
      .setName('ticketanalytics')
      .setDescription('View ticket analytics and reports')
      .addSubcommand(subcommand =>
        subcommand
          .setName('overview')
          .setDescription('Get overview of ticket statistics')
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('staff')
          .setDescription('Get staff performance statistics')
      )
      .addSubcommand(subcommand =>
        subcommand
          .setName('sla')
          .setDescription('Get SLA compliance statistics')
      )
      .setDefaultMemberPermissions(PermissionFlagsBits.ManageGuild),
    category: 'ticket',
    permissions: ['MANAGE_GUILD'],
    usage: '/ticketanalytics <subcommand>',
    async execute(interaction: any) {
      const subcommand = interaction.options.getSubcommand();
      
      try {
        await interaction.deferReply();
        
        switch (subcommand) {
          case 'overview':
            const totalTickets = await db.select({ count: count() })
              .from(tickets)
              .where(eq(tickets.guildId, interaction.guild.id));
            
            const openTickets = await db.select({ count: count() })
              .from(tickets)
              .where(and(eq(tickets.guildId, interaction.guild.id), eq(tickets.status, 'open')));
            
            const closedTickets = await db.select({ count: count() })
              .from(tickets)
              .where(and(eq(tickets.guildId, interaction.guild.id), eq(tickets.status, 'closed')));
            
            const avgSatisfaction = await db.select({ avg: avg(tickets.satisfaction) })
              .from(tickets)
              .where(and(eq(tickets.guildId, interaction.guild.id), sql`${tickets.satisfaction} IS NOT NULL`));
            
            await interaction.editReply({
              embeds: [{
                title: '📊 Ticket Analytics Overview',
                color: 0x00FFFF,
                fields: [
                  { name: 'Total Tickets', value: totalTickets[0].count.toString(), inline: true },
                  { name: 'Open Tickets', value: openTickets[0].count.toString(), inline: true },
                  { name: 'Closed Tickets', value: closedTickets[0].count.toString(), inline: true },
                  { name: 'Average Satisfaction', value: avgSatisfaction[0].avg ? `${parseFloat(avgSatisfaction[0].avg).toFixed(1)}/5 ⭐` : 'N/A', inline: true },
                  { name: 'Resolution Rate', value: totalTickets[0].count > 0 ? `${((closedTickets[0].count / totalTickets[0].count) * 100).toFixed(1)}%` : '0%', inline: true }
                ],
                timestamp: new Date().toISOString(),
              }]
            });
            break;
            
          case 'staff':
            const staffStats = await db.select({
              assignedTo: tickets.assignedTo,
              count: count(),
              avgSatisfaction: avg(tickets.satisfaction)
            })
            .from(tickets)
            .where(and(eq(tickets.guildId, interaction.guild.id), sql`${tickets.assignedTo} IS NOT NULL`))
            .groupBy(tickets.assignedTo);
            
            const staffText = staffStats.map(stat => 
              `<@${stat.assignedTo}>: ${stat.count} tickets, ${stat.avgSatisfaction ? `${parseFloat(stat.avgSatisfaction).toFixed(1)}/5 ⭐` : 'N/A'}`
            ).join('\n');
            
            await interaction.editReply({
              embeds: [{
                title: '👥 Staff Performance',
                description: staffText || 'No staff performance data available',
                color: 0x00FFFF,
                timestamp: new Date().toISOString(),
              }]
            });
            break;
            
          case 'sla':
            const slaStats = await db.select({
              priority: tickets.priority,
              total: count(),
              onTime: count(sql`CASE WHEN ${tickets.resolvedAt} <= ${tickets.slaDeadline} THEN 1 END`)
            })
            .from(tickets)
            .where(and(eq(tickets.guildId, interaction.guild.id), sql`${tickets.resolvedAt} IS NOT NULL`))
            .groupBy(tickets.priority);
            
            const slaText = slaStats.map(stat => 
              `${stat.priority.toUpperCase()}: ${stat.onTime || 0}/${stat.total} (${((stat.onTime || 0) / stat.total * 100).toFixed(1)}%)`
            ).join('\n');
            
            await interaction.editReply({
              embeds: [{
                title: '📈 SLA Compliance',
                description: slaText || 'No SLA data available',
                color: 0x00FFFF,
                timestamp: new Date().toISOString(),
              }]
            });
            break;
        }
      } catch (error) {
        console.error('Error getting ticket analytics:', error);
        await interaction.editReply({
          content: '❌ Failed to get ticket analytics. Please try again.'
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