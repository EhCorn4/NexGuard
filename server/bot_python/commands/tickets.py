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
    
    async def get_ticket_categories(self, guild_id: str):
        """Get all ticket categories for a guild"""
        if not self.bot.db_pool:
            return []
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                categories = await conn.fetch("""
                    SELECT * FROM ticket_categories 
                    WHERE guild_id = $1 AND is_active = TRUE
                    ORDER BY category_name
                """, guild_id)
                return categories
        except Exception as e:
            logger.error(f"Error getting ticket categories: {e}")
            return []
    
    async def create_ticket_category(self, guild_id: str, category_name: str, category_id: str, description: str = None):
        """Create a new ticket category"""
        if not self.bot.db_pool:
            return False
        
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO ticket_categories (guild_id, category_name, category_id, description)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (guild_id, category_name) DO UPDATE SET
                        category_id = EXCLUDED.category_id,
                        description = EXCLUDED.description,
                        is_active = TRUE
                """, guild_id, category_name, category_id, description)
                return True
        except Exception as e:
            logger.error(f"Error creating ticket category: {e}")
            return False
    
    @app_commands.command(name="ticket", description="Create a support ticket")
    @app_commands.describe(
        subject="Subject of the ticket",
        description="Detailed description of the issue",
        category="Category of the ticket",
        priority="Priority level",
        ticket_category="Discord category to create the ticket in"
    )
    @app_commands.choices(
        category=[
            app_commands.Choice(name="General Support", value="general"),
            app_commands.Choice(name="Technical Issue", value="technical"),
            app_commands.Choice(name="Bug Report", value="bug"),
            app_commands.Choice(name="Feature Request", value="feature"),
            app_commands.Choice(name="Account Issue", value="account"),
            app_commands.Choice(name="Billing Issue", value="billing"),
            app_commands.Choice(name="Partnership", value="partnership"),
            app_commands.Choice(name="Other", value="other")
        ],
        priority=[
            app_commands.Choice(name="Low", value="low"),
            app_commands.Choice(name="Medium", value="medium"),
            app_commands.Choice(name="High", value="high"),
            app_commands.Choice(name="Urgent", value="urgent")
        ]
    )
    async def ticket(self, interaction: discord.Interaction, subject: str, description: str, category: str = "general", priority: str = "medium", ticket_category: discord.CategoryChannel = None):
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
            
            # Determine the Discord category to create the ticket in
            target_category = None
            if ticket_category:
                target_category = ticket_category
            else:
                # Try to find a category based on the ticket category type
                categories = await self.get_ticket_categories(str(interaction.guild.id))
                for cat in categories:
                    if cat['category_name'].lower() == category.lower():
                        target_category = interaction.guild.get_channel(int(cat['category_id']))
                        break
            
            # Create the channel with appropriate naming
            channel_name = f"{category}-{ticket_id}"
            if target_category:
                channel_name = f"{target_category.name.lower()}-{ticket_id}"
            
            channel = await interaction.guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                category=target_category,
                reason=f"Support ticket created by {interaction.user.name}"
            )
            
            # Store ticket in database
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO tickets (ticket_id, guild_id, channel_id, discord_category_id, user_id, username, category, subject, description, priority, status)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    """, ticket_id, str(interaction.guild.id), str(channel.id), str(target_category.id) if target_category else None,
                    str(interaction.user.id), interaction.user.name, category, subject, description, priority, "open")
            
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
            
            if target_category:
                embed.add_field(name="Category Location", value=target_category.name, inline=True)
            
            embed.set_footer(text="Support staff will be with you shortly. Please provide any additional information that might help.")
            
            # Send embed to ticket channel
            await channel.send(f"{interaction.user.mention}", embed=embed)
            
            # Send confirmation to user
            category_info = f" in {target_category.name}" if target_category else ""
            await interaction.response.send_message(
                f"✅ Support ticket created{category_info}! Please check {channel.mention} for further assistance.",
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

    @app_commands.command(name="ticketcategory", description="Manage ticket categories (Admin only)")
    @app_commands.describe(
        action="Action to perform",
        category_name="Name of the ticket category",
        discord_category="Discord category channel",
        description="Description of the ticket category"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove"),
        app_commands.Choice(name="List", value="list"),
        app_commands.Choice(name="Update", value="update")
    ])
    async def ticketcategory(self, interaction: discord.Interaction, action: str, category_name: str = None, discord_category: discord.CategoryChannel = None, description: str = None):
        """Manage ticket categories (Admin only)"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to manage ticket categories.", ephemeral=True)
            return
        
        try:
            guild_id = str(interaction.guild.id)
            
            if action == "add":
                if not category_name or not discord_category:
                    await interaction.response.send_message("❌ Please provide both category name and Discord category.", ephemeral=True)
                    return
                
                success = await self.create_ticket_category(guild_id, category_name, str(discord_category.id), description)
                if success:
                    await interaction.response.send_message(f"✅ Ticket category '{category_name}' added for {discord_category.mention}.", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Failed to add ticket category.", ephemeral=True)
            
            elif action == "remove":
                if not category_name:
                    await interaction.response.send_message("❌ Please provide a category name to remove.", ephemeral=True)
                    return
                
                if self.bot.db_pool:
                    async with self.bot.db_pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE ticket_categories SET is_active = FALSE
                            WHERE guild_id = $1 AND category_name = $2
                        """, guild_id, category_name)
                        await interaction.response.send_message(f"✅ Ticket category '{category_name}' removed.", ephemeral=True)
            
            elif action == "list":
                categories = await self.get_ticket_categories(guild_id)
                if not categories:
                    await interaction.response.send_message("❌ No ticket categories configured.", ephemeral=True)
                    return
                
                embed = discord.Embed(
                    title="🎫 Ticket Categories",
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                
                for category in categories:
                    discord_cat = interaction.guild.get_channel(int(category['category_id']))
                    cat_name = discord_cat.name if discord_cat else "Unknown Category"
                    
                    embed.add_field(
                        name=f"📁 {category['category_name']}",
                        value=f"**Discord Category:** {cat_name}\n**Description:** {category['description'] or 'No description'}\n**Created:** {discord.utils.format_dt(category['created_at'], 'R')}",
                        inline=False
                    )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            elif action == "update":
                if not category_name:
                    await interaction.response.send_message("❌ Please provide a category name to update.", ephemeral=True)
                    return
                
                if self.bot.db_pool:
                    async with self.bot.db_pool.acquire() as conn:
                        update_fields = []
                        params = [guild_id, category_name]
                        param_count = 2
                        
                        if discord_category:
                            param_count += 1
                            update_fields.append(f"category_id = ${param_count}")
                            params.append(str(discord_category.id))
                        
                        if description:
                            param_count += 1
                            update_fields.append(f"description = ${param_count}")
                            params.append(description)
                        
                        if update_fields:
                            query = f"""
                                UPDATE ticket_categories SET {', '.join(update_fields)}
                                WHERE guild_id = $1 AND category_name = $2
                            """
                            await conn.execute(query, *params)
                            await interaction.response.send_message(f"✅ Ticket category '{category_name}' updated.", ephemeral=True)
                        else:
                            await interaction.response.send_message("❌ No fields to update.", ephemeral=True)
                            
        except Exception as e:
            logger.error(f"Error managing ticket categories: {e}")
            await interaction.response.send_message("❌ Failed to manage ticket categories.", ephemeral=True)

    @app_commands.command(name="tickets", description="List all tickets with filtering options")
    @app_commands.describe(
        status="Filter by status",
        category="Filter by category",
        user="Filter by user",
        show_closed="Show closed tickets"
    )
    @app_commands.choices(
        status=[
            app_commands.Choice(name="Open", value="open"),
            app_commands.Choice(name="In Progress", value="in-progress"),
            app_commands.Choice(name="Pending", value="pending"),
            app_commands.Choice(name="Resolved", value="resolved"),
            app_commands.Choice(name="Closed", value="closed")
        ],
        category=[
            app_commands.Choice(name="General Support", value="general"),
            app_commands.Choice(name="Technical Issue", value="technical"),
            app_commands.Choice(name="Bug Report", value="bug"),
            app_commands.Choice(name="Feature Request", value="feature"),
            app_commands.Choice(name="Account Issue", value="account"),
            app_commands.Choice(name="Billing Issue", value="billing"),
            app_commands.Choice(name="Partnership", value="partnership"),
            app_commands.Choice(name="Other", value="other")
        ]
    )
    async def tickets(self, interaction: discord.Interaction, status: str = None, category: str = None, user: discord.Member = None, show_closed: bool = False):
        """List all tickets with filtering options"""
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You need Manage Channels permission to view tickets.", ephemeral=True)
            return
        
        try:
            if not self.bot.db_pool:
                await interaction.response.send_message("❌ Database not available.", ephemeral=True)
                return
            
            # Build query with filters
            query = "SELECT * FROM tickets WHERE guild_id = $1"
            params = [str(interaction.guild.id)]
            param_count = 1
            
            if status:
                param_count += 1
                query += f" AND status = ${param_count}"
                params.append(status)
            
            if category:
                param_count += 1
                query += f" AND category = ${param_count}"
                params.append(category)
            
            if user:
                param_count += 1
                query += f" AND user_id = ${param_count}"
                params.append(str(user.id))
            
            if not show_closed:
                query += " AND status != 'closed'"
            
            query += " ORDER BY created_at DESC LIMIT 10"
            
            async with self.bot.db_pool.acquire() as conn:
                tickets = await conn.fetch(query, *params)
                
                if not tickets:
                    await interaction.response.send_message("❌ No tickets found matching your criteria.", ephemeral=True)
                    return
                
                embed = discord.Embed(
                    title="🎫 Tickets Overview",
                    color=0x00FFFF,
                    timestamp=datetime.utcnow()
                )
                
                for ticket in tickets:
                    status_emoji = {
                        "open": "🔓",
                        "in-progress": "⏳",
                        "pending": "⏸️",
                        "resolved": "✅",
                        "closed": "🔒"
                    }.get(ticket['status'], "❓")
                    
                    priority_emoji = {
                        "low": "🟢",
                        "medium": "🟡",
                        "high": "🟠",
                        "urgent": "🔴"
                    }.get(ticket['priority'], "⚪")
                    
                    channel = self.bot.get_channel(int(ticket['channel_id']))
                    channel_info = channel.mention if channel else "Channel Deleted"
                    
                    embed.add_field(
                        name=f"{status_emoji} {ticket['ticket_id']} - {ticket['subject']}",
                        value=f"**User:** <@{ticket['user_id']}>\n**Category:** {ticket['category'].title()}\n**Priority:** {priority_emoji} {ticket['priority'].title()}\n**Status:** {ticket['status'].title()}\n**Channel:** {channel_info}\n**Created:** {discord.utils.format_dt(ticket['created_at'], 'R')}",
                        inline=False
                    )
                
                embed.set_footer(text=f"Showing {len(tickets)} tickets")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error listing tickets: {e}")
            await interaction.response.send_message("❌ Failed to list tickets.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketCommands(bot))