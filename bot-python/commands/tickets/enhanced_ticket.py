"""
Enhanced Ticket System for NexGuard Discord Bot
Simplified version with additional fields but no categories or priorities
"""

import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import asyncio
from datetime import datetime
import logging
import json
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class EnhancedTicketModal(discord.ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Create Support Ticket", timeout=300)
        self.bot = bot
        
        # Subject input
        self.subject = discord.ui.TextInput(
            label="Subject",
            placeholder="Brief description of your issue...",
            required=True,
            max_length=100
        )
        
        # Description input
        self.description = discord.ui.TextInput(
            label="Description",
            placeholder="Detailed description of your issue or request...",
            required=True,
            style=discord.TextStyle.paragraph,
            max_length=1000
        )
        
        # Additional information
        self.additional_info = discord.ui.TextInput(
            label="Additional Information",
            placeholder="Any additional details that might help us assist you...",
            required=False,
            style=discord.TextStyle.paragraph,
            max_length=500
        )
        
        self.add_item(self.subject)
        self.add_item(self.description)
        self.add_item(self.additional_info)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            
            logger.info(f"Ticket creation started by {interaction.user} in {interaction.guild.name}")
            
            # Get next ticket number
            conn = sqlite3.connect(self.bot.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(ticket_number) FROM tickets WHERE guild_id = ?', (interaction.guild.id,))
            result = cursor.fetchone()
            ticket_number = (result[0] or 0) + 1
            
            logger.info(f"Assigned ticket number: {ticket_number}")
            
            # Get ticket configuration
            cursor.execute('SELECT ping_roles FROM ticket_config WHERE guild_id = ?', (interaction.guild.id,))
            config_result = cursor.fetchone()
            ping_roles = []
            if config_result and config_result[0]:
                try:
                    ping_roles = json.loads(config_result[0])
                except (json.JSONDecodeError, TypeError):
                    ping_roles = []
            
            # Create ticket category
            guild = interaction.guild
            category_name = "Support Tickets"
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                try:
                    category = await guild.create_category(
                        name=category_name,
                        reason="Creating support ticket category"
                    )
                except discord.Forbidden:
                    embed = discord.Embed(
                        title="❌ Permission Error",
                        description="I don't have permission to create categories. Please ask an administrator to give me the necessary permissions.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
            
            # Create ticket channel
            channel_name = f"🎫ticket-{ticket_number:04d}"
            
            # Set up permissions
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            
            # Add ping roles permissions
            for role_id in ping_roles:
                role = guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            try:
                channel = await category.create_text_channel(
                    name=channel_name,
                    overwrites=overwrites,
                    reason=f"Support ticket created by {interaction.user}"
                )
            except discord.Forbidden:
                embed = discord.Embed(
                    title="❌ Permission Error",
                    description="I don't have permission to create channels. Please ask an administrator to give me the necessary permissions.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Create additional info text
            additional_text = f"\n\n**Additional Information:**\n{self.additional_info.value}" if self.additional_info.value else ""
            
            # Save ticket to database
            cursor.execute('''
                INSERT INTO tickets (guild_id, channel_id, user_id, ticket_number, subject, description, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                guild.id, channel.id, interaction.user.id, ticket_number, 
                self.subject.value, self.description.value + additional_text, 
                "open", datetime.utcnow().isoformat()
            ))
            conn.commit()
            conn.close()
            
            # Create ticket embed
            embed = discord.Embed(
                title=f"🎫 Support Ticket #{ticket_number:04d}",
                description=f"**Subject:** {self.subject.value}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📝 Description",
                value=self.description.value,
                inline=False
            )
            
            if self.additional_info.value:
                embed.add_field(
                    name="ℹ️ Additional Information",
                    value=self.additional_info.value,
                    inline=False
                )
            
            embed.add_field(
                name="👤 Created by",
                value=interaction.user.mention,
                inline=True
            )
            
            embed.add_field(
                name="🕒 Created at",
                value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
                inline=True
            )
            
            embed.set_footer(text=f"Ticket ID: {ticket_number:04d}")
            
            # Create control buttons
            view = TicketControlView(self.bot, ticket_number)
            
            # Send ticket message
            ping_text = ""
            if ping_roles:
                role_mentions = []
                for role_id in ping_roles:
                    role = guild.get_role(role_id)
                    if role:
                        role_mentions.append(role.mention)
                if role_mentions:
                    ping_text = f"📢 {' '.join(role_mentions)}"
            
            await channel.send(
                content=ping_text,
                embed=embed,
                view=view
            )
            
            # Send confirmation to user
            confirmation_embed = discord.Embed(
                title="✅ Ticket Created Successfully",
                description=f"Your support ticket has been created in {channel.mention}",
                color=discord.Color.green()
            )
            confirmation_embed.add_field(
                name="Ticket Number",
                value=f"#{ticket_number:04d}",
                inline=True
            )
            confirmation_embed.add_field(
                name="Subject",
                value=self.subject.value,
                inline=True
            )
            
            await interaction.followup.send(embed=confirmation_embed, ephemeral=True)
            
            logger.info(f"Enhanced ticket #{ticket_number:04d} created by {interaction.user} in {guild.name}")
            
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}", exc_info=True)
            
            # Send error message to user
            error_embed = discord.Embed(
                title="❌ Error Creating Ticket",
                description=f"An error occurred while creating your ticket. Please try again or contact an administrator.\n\nError: {str(e)}",
                color=discord.Color.red()
            )
            
            try:
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            except discord.InteractionResponded:
                # If followup fails, try response
                try:
                    await interaction.response.send_message(embed=error_embed, ephemeral=True)
                except discord.InteractionResponded:
                    # Interaction was already responded to
                    pass

class TicketControlView(discord.ui.View):
    def __init__(self, bot, ticket_number):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_number = ticket_number
    
    @discord.ui.button(label='🔒 Close Ticket', style=discord.ButtonStyle.danger, custom_id='close_ticket')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check permissions
        if not await self.check_ticket_permissions(interaction.user, interaction.guild):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to close this ticket.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Show close confirmation modal
        modal = CloseTicketModal(self.bot, self.ticket_number)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='ℹ️ Ticket Info', style=discord.ButtonStyle.secondary, custom_id='ticket_info')
    async def ticket_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get ticket info
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, subject, description, created_at FROM tickets 
            WHERE guild_id = ? AND ticket_number = ?
        ''', (interaction.guild.id, self.ticket_number))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            embed = discord.Embed(
                title="❌ Ticket Not Found",
                description="This ticket could not be found in the database.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        user_id, subject, description, created_at = result
        user = interaction.guild.get_member(user_id)
        
        embed = discord.Embed(
            title=f"🎫 Ticket #{self.ticket_number:04d} Information",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Subject", value=subject, inline=False)
        embed.add_field(name="Description", value=description[:500] + ("..." if len(description) > 500 else ""), inline=False)
        embed.add_field(name="Created by", value=user.mention if user else "Unknown User", inline=True)
        embed.add_field(name="Created", value=f"<t:{int(datetime.fromisoformat(created_at).timestamp())}:F>", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def check_ticket_permissions(self, user, guild):
        """Check if user has ticket management permissions"""
        if user.guild_permissions.administrator:
            return True
        
        # Check if user has a configured moderator role
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT moderator_role FROM guild_settings WHERE guild_id = ?', (guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            mod_role = guild.get_role(result[0])
            if mod_role and mod_role in user.roles:
                return True
        
        return False

class CloseTicketModal(discord.ui.Modal):
    def __init__(self, bot, ticket_number):
        super().__init__(title="Close Ticket", timeout=300)
        self.bot = bot
        self.ticket_number = ticket_number
        
        self.reason = discord.ui.TextInput(
            label="Reason for closing (optional)",
            placeholder="Why is this ticket being closed?",
            required=False,
            style=discord.TextStyle.paragraph,
            max_length=500
        )
        
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # Update ticket in database
        conn = sqlite3.connect(self.bot.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tickets 
            SET status = 'closed', closed_at = ?, closed_by = ?
            WHERE guild_id = ? AND ticket_number = ?
        ''', (datetime.utcnow().isoformat(), interaction.user.id, interaction.guild.id, self.ticket_number))
        conn.commit()
        conn.close()
        
        # Send closing message
        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"This ticket has been closed by {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        if self.reason.value:
            embed.add_field(name="Reason", value=self.reason.value, inline=False)
        
        embed.add_field(name="Ticket Number", value=f"#{self.ticket_number:04d}", inline=True)
        embed.add_field(name="Closed by", value=interaction.user.mention, inline=True)
        
        await interaction.followup.send(embed=embed)
        
        # Archive the channel after 10 seconds
        await asyncio.sleep(10)
        try:
            await interaction.channel.delete(reason=f"Ticket #{self.ticket_number:04d} closed by {interaction.user}")
        except discord.NotFound:
            pass
        except discord.Forbidden:
            pass
        
        logger.info(f"Ticket #{self.ticket_number:04d} closed by {interaction.user} in {interaction.guild.name}")