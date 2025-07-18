import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ticket", description="Create a support ticket")
    @app_commands.describe(
        subject="Subject of the ticket",
        description="Detailed description of the issue",
        category="Category of the ticket",
        priority="Priority level"
    )
    @app_commands.choices(
        category=[
            app_commands.Choice(name="General Support", value="general"),
            app_commands.Choice(name="Technical Issue", value="technical"),
            app_commands.Choice(name="Bug Report", value="bug"),
            app_commands.Choice(name="Feature Request", value="feature"),
            app_commands.Choice(name="Account Issue", value="account"),
            app_commands.Choice(name="Other", value="other")
        ],
        priority=[
            app_commands.Choice(name="Low", value="low"),
            app_commands.Choice(name="Medium", value="medium"),
            app_commands.Choice(name="High", value="high"),
            app_commands.Choice(name="Urgent", value="urgent")
        ]
    )
    async def ticket(self, interaction: discord.Interaction, subject: str, description: str, category: str = "general", priority: str = "medium"):
        """Create a support ticket"""
        try:
            # Generate unique ticket ID
            ticket_id = str(uuid.uuid4())[:8]
            
            # Create ticket channel
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            # Add staff role permissions if configured
            config = await self.bot.get_guild_config(str(interaction.guild.id))
            if config.get('mod_role_id'):
                try:
                    mod_role = interaction.guild.get_role(int(config['mod_role_id']))
                    if mod_role:
                        overwrites[mod_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                except:
                    pass
            
            # Create the channel
            channel = await interaction.guild.create_text_channel(
                name=f"ticket-{ticket_id}",
                overwrites=overwrites,
                category=None,  # You can set a category if needed
                reason=f"Support ticket created by {interaction.user.name}"
            )
            
            # Store ticket in database
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO tickets (ticket_id, guild_id, channel_id, user_id, username, category, subject, description, priority, status)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """, ticket_id, str(interaction.guild.id), str(channel.id), str(interaction.user.id), 
                    interaction.user.name, category, subject, description, priority, "open")
            
            # Create ticket embed
            embed = discord.Embed(
                title=f"🎫 Support Ticket - {ticket_id}",
                description=f"**Subject:** {subject}\n**Description:** {description}",
                color=0x00FFFF,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Category", value=category.title(), inline=True)
            embed.add_field(name="Priority", value=priority.title(), inline=True)
            embed.add_field(name="Status", value="Open", inline=True)
            
            embed.add_field(name="Created by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Created at", value=discord.utils.format_dt(datetime.utcnow(), "F"), inline=True)
            embed.add_field(name="Ticket ID", value=ticket_id, inline=True)
            
            embed.set_footer(text="Support staff will be with you shortly. Please provide any additional information that might help.")
            
            # Send embed to ticket channel
            await channel.send(f"{interaction.user.mention}", embed=embed)
            
            # Send confirmation to user
            await interaction.response.send_message(
                f"✅ Support ticket created! Please check {channel.mention} for further assistance.",
                ephemeral=True
            )
            
            logger.info(f"Created ticket {ticket_id} for user {interaction.user.name} in guild {interaction.guild.name}")
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await interaction.response.send_message("❌ Failed to create ticket. Please try again.", ephemeral=True)
    
    @app_commands.command(name="ticketinfo", description="Get information about a ticket")
    @app_commands.describe(ticket_id="The ID of the ticket to get information about")
    async def ticketinfo(self, interaction: discord.Interaction, ticket_id: str):
        """Get information about a ticket"""
        try:
            if not self.bot.db_pool:
                await interaction.response.send_message("❌ Database not available.", ephemeral=True)
                return
            
            async with self.bot.db_pool.acquire() as conn:
                ticket = await conn.fetchrow("""
                    SELECT * FROM tickets WHERE ticket_id = $1 AND guild_id = $2
                """, ticket_id, str(interaction.guild.id))
                
                if not ticket:
                    await interaction.response.send_message("❌ Ticket not found.", ephemeral=True)
                    return
                
                embed = discord.Embed(
                    title=f"🎫 Ticket Information - {ticket_id}",
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(name="Subject", value=ticket['subject'], inline=False)
                embed.add_field(name="Description", value=ticket['description'] or "No description", inline=False)
                
                embed.add_field(name="Category", value=ticket['category'].title(), inline=True)
                embed.add_field(name="Priority", value=ticket['priority'].title(), inline=True)
                embed.add_field(name="Status", value=ticket['status'].title(), inline=True)
                
                embed.add_field(name="Created by", value=f"<@{ticket['user_id']}>", inline=True)
                embed.add_field(name="Created at", value=discord.utils.format_dt(ticket['created_at'], "F"), inline=True)
                
                if ticket['assigned_to']:
                    embed.add_field(name="Assigned to", value=f"<@{ticket['assigned_to']}>", inline=True)
                
                if ticket['closed_at']:
                    embed.add_field(name="Closed at", value=discord.utils.format_dt(ticket['closed_at'], "F"), inline=True)
                
                channel = self.bot.get_channel(int(ticket['channel_id']))
                if channel:
                    embed.add_field(name="Channel", value=channel.mention, inline=True)
                
                await interaction.response.send_message(embed=embed)
                
        except Exception as e:
            logger.error(f"Error getting ticket info: {e}")
            await interaction.response.send_message("❌ Failed to get ticket information.", ephemeral=True)
    
    @app_commands.command(name="ticketmanage", description="Manage tickets (staff only)")
    @app_commands.describe(
        action="Action to perform",
        ticket_id="The ID of the ticket",
        user="User to assign ticket to (for assign action)",
        reason="Reason for the action"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Close", value="close"),
        app_commands.Choice(name="Assign", value="assign"),
        app_commands.Choice(name="Escalate", value="escalate"),
        app_commands.Choice(name="Archive", value="archive")
    ])
    async def ticketmanage(self, interaction: discord.Interaction, action: str, ticket_id: str, user: discord.Member = None, reason: str = None):
        """Manage tickets (staff only)"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You don't have permission to manage tickets.", ephemeral=True)
            return
        
        try:
            if not self.bot.db_pool:
                await interaction.response.send_message("❌ Database not available.", ephemeral=True)
                return
            
            async with self.bot.db_pool.acquire() as conn:
                ticket = await conn.fetchrow("""
                    SELECT * FROM tickets WHERE ticket_id = $1 AND guild_id = $2
                """, ticket_id, str(interaction.guild.id))
                
                if not ticket:
                    await interaction.response.send_message("❌ Ticket not found.", ephemeral=True)
                    return
                
                if action == "close":
                    # Close the ticket
                    await conn.execute("""
                        UPDATE tickets SET status = 'closed', closed_at = $1, updated_at = $2
                        WHERE ticket_id = $3 AND guild_id = $4
                    """, datetime.utcnow(), datetime.utcnow(), ticket_id, str(interaction.guild.id))
                    
                    # Archive the channel
                    channel = self.bot.get_channel(int(ticket['channel_id']))
                    if channel:
                        await channel.edit(name=f"closed-{ticket_id}")
                        
                        embed = discord.Embed(
                            title="🔒 Ticket Closed",
                            description=f"This ticket has been closed by {interaction.user.mention}.",
                            color=0xFF0000,
                            timestamp=datetime.utcnow()
                        )
                        
                        if reason:
                            embed.add_field(name="Reason", value=reason, inline=False)
                        
                        embed.add_field(name="Closed by", value=interaction.user.mention, inline=True)
                        embed.add_field(name="Closed at", value=discord.utils.format_dt(datetime.utcnow(), "F"), inline=True)
                        
                        await channel.send(embed=embed)
                    
                    await interaction.response.send_message(f"✅ Ticket {ticket_id} has been closed.", ephemeral=True)
                    
                elif action == "assign":
                    if not user:
                        await interaction.response.send_message("❌ Please specify a user to assign the ticket to.", ephemeral=True)
                        return
                    
                    # Assign the ticket
                    await conn.execute("""
                        UPDATE tickets SET assigned_to = $1, assigned_by = $2, updated_at = $3
                        WHERE ticket_id = $4 AND guild_id = $5
                    """, str(user.id), str(interaction.user.id), datetime.utcnow(), ticket_id, str(interaction.guild.id))
                    
                    # Add user to channel permissions
                    channel = self.bot.get_channel(int(ticket['channel_id']))
                    if channel:
                        await channel.set_permissions(user, read_messages=True, send_messages=True)
                        
                        embed = discord.Embed(
                            title="👤 Ticket Assigned",
                            description=f"This ticket has been assigned to {user.mention}.",
                            color=0x00FF00,
                            timestamp=datetime.utcnow()
                        )
                        
                        embed.add_field(name="Assigned by", value=interaction.user.mention, inline=True)
                        embed.add_field(name="Assigned at", value=discord.utils.format_dt(datetime.utcnow(), "F"), inline=True)
                        
                        await channel.send(f"{user.mention}", embed=embed)
                    
                    await interaction.response.send_message(f"✅ Ticket {ticket_id} has been assigned to {user.mention}.", ephemeral=True)
                    
                elif action == "escalate":
                    # Escalate the ticket
                    new_escalation = (ticket.get('escalation_level', 0) or 0) + 1
                    await conn.execute("""
                        UPDATE tickets SET escalation_level = $1, updated_at = $2
                        WHERE ticket_id = $3 AND guild_id = $4
                    """, new_escalation, datetime.utcnow(), ticket_id, str(interaction.guild.id))
                    
                    channel = self.bot.get_channel(int(ticket['channel_id']))
                    if channel:
                        embed = discord.Embed(
                            title="⚠️ Ticket Escalated",
                            description=f"This ticket has been escalated to level {new_escalation}.",
                            color=0xFFFF00,
                            timestamp=datetime.utcnow()
                        )
                        
                        embed.add_field(name="Escalated by", value=interaction.user.mention, inline=True)
                        embed.add_field(name="Escalation Level", value=f"Level {new_escalation}", inline=True)
                        
                        if reason:
                            embed.add_field(name="Reason", value=reason, inline=False)
                        
                        await channel.send(embed=embed)
                    
                    await interaction.response.send_message(f"✅ Ticket {ticket_id} has been escalated to level {new_escalation}.", ephemeral=True)
                    
                elif action == "archive":
                    # Archive the ticket
                    await conn.execute("""
                        UPDATE tickets SET is_archived = TRUE, updated_at = $1
                        WHERE ticket_id = $2 AND guild_id = $3
                    """, datetime.utcnow(), ticket_id, str(interaction.guild.id))
                    
                    # Delete the channel
                    channel = self.bot.get_channel(int(ticket['channel_id']))
                    if channel:
                        await channel.delete(reason=f"Ticket {ticket_id} archived by {interaction.user.name}")
                    
                    await interaction.response.send_message(f"✅ Ticket {ticket_id} has been archived and the channel deleted.", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error managing ticket: {e}")
            await interaction.response.send_message("❌ Failed to manage ticket. Please try again.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketCommands(bot))