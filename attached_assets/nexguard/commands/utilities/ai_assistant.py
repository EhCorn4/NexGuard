"""
AI Assistant Command for NexGuard Discord Bot
Provides ChatGPT-powered AI assistant functionality using OpenAI API
"""

import discord
from discord.ext import commands
from discord import app_commands
import openai
import os
import asyncio
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AIAssistantCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.openai_client = None
        self.setup_openai()
        
        # Conversation memory (limited to prevent token overflow)
        self.conversations: Dict[int, list] = {}
        self.max_conversation_length = 10
        
    def setup_openai(self):
        """Initialize OpenAI client"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully for AI Assistant")
            else:
                logger.warning("OPENAI_API_KEY not found - AI Assistant will not work")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.openai_client = None

    def get_conversation_history(self, user_id: int) -> list:
        """Get conversation history for a user"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        return self.conversations[user_id]

    def add_to_conversation(self, user_id: int, role: str, content: str):
        """Add message to conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({"role": role, "content": content})
        
        # Trim conversation if it gets too long
        if len(self.conversations[user_id]) > self.max_conversation_length:
            # Keep system message and recent messages
            system_msg = None
            if self.conversations[user_id][0]["role"] == "system":
                system_msg = self.conversations[user_id][0]
                self.conversations[user_id] = self.conversations[user_id][1:]
            
            # Keep only recent messages
            self.conversations[user_id] = self.conversations[user_id][-(self.max_conversation_length-1):]
            
            if system_msg:
                self.conversations[user_id].insert(0, system_msg)

    def clear_conversation(self, user_id: int):
        """Clear conversation history for a user"""
        if user_id in self.conversations:
            del self.conversations[user_id]

    async def generate_ai_response(self, messages: list, guild_context: str = None) -> str:
        """Generate AI response using OpenAI"""
        if not self.openai_client:
            return "❌ AI Assistant is not configured. Please contact an administrator."
        
        try:
            # Prepare system message with context
            system_message = {
                "role": "system",
                "content": f"""You are NexGuard AI Assistant, a helpful Discord bot assistant. 
                
Guidelines:
- Be helpful, friendly, and concise
- Keep responses under 1500 characters (Discord limit)
- Use Discord markdown for formatting when appropriate
- You're integrated into a Discord server management bot
- Be respectful and appropriate for Discord communities
- If asked about server-specific information you don't have, suggest using bot commands
{f"- Current server context: {guild_context}" if guild_context else ""}

Remember: You're an AI assistant within the NexGuard Discord bot."""
            }
            
            # Prepare messages with system context
            full_messages = [system_message] + messages
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=full_messages,
                max_tokens=350,  # Reduced to help with rate limits
                temperature=0.7,
                frequency_penalty=0.3,
                presence_penalty=0.3,
                timeout=30  # Add timeout to prevent hanging
            )
            
            return response.choices[0].message.content.strip()
            
        except openai.RateLimitError as e:
            logger.warning(f"OpenAI rate limit exceeded: {e}")
            return "⚠️ AI Assistant is currently rate limited. This happens when there are too many requests. Please wait a few minutes and try again."
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            if "insufficient_quota" in str(e).lower():
                return "❌ AI Assistant has exceeded its usage quota. Please contact an administrator to check the OpenAI API billing."
            elif "invalid_api_key" in str(e).lower():
                return "❌ AI Assistant API key is invalid. Please contact an administrator to update the OpenAI API key."
            else:
                return f"❌ AI Assistant API error: {str(e)[:100]}..."
        except Exception as e:
            logger.error(f"Unexpected error in AI response generation: {e}")
            return "❌ Something went wrong with the AI Assistant. Please try again or contact an administrator."

    @app_commands.command(name="ai", description="Ask the AI assistant a question")
    @app_commands.describe(
        question="Your question or message for the AI assistant",
        private="Whether to make the response private (only you can see it)"
    )
    async def ai_command(self, interaction: discord.Interaction, question: str, private: bool = False):
        """Main AI assistant command"""
        await interaction.response.defer(ephemeral=private)
        
        try:
            # Get conversation history
            user_id = interaction.user.id
            conversation = self.get_conversation_history(user_id)
            
            # Add user message to conversation
            self.add_to_conversation(user_id, "user", question)
            
            # Prepare guild context
            guild_context = None
            if interaction.guild:
                guild_context = f"Server: {interaction.guild.name} (ID: {interaction.guild.id})"
            
            # Generate AI response
            ai_response = await self.generate_ai_response(
                self.get_conversation_history(user_id),
                guild_context
            )
            
            # Add AI response to conversation
            self.add_to_conversation(user_id, "assistant", ai_response)
            
            # Create response embed
            embed = discord.Embed(
                title="🤖 NexGuard AI Assistant",
                description=ai_response,
                color=0x00ff00
            )
            embed.set_footer(text=f"Asked by {interaction.user.display_name}")
            
            # Add conversation controls
            view = AIConversationView(self, user_id)
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=private)
            
        except Exception as e:
            logger.error(f"Error in AI command: {e}")
            await interaction.followup.send(
                "❌ An error occurred while processing your request.",
                ephemeral=True
            )

    @app_commands.command(name="ai-clear", description="Clear your AI conversation history")
    async def ai_clear_command(self, interaction: discord.Interaction):
        """Clear conversation history"""
        user_id = interaction.user.id
        self.clear_conversation(user_id)
        
        embed = discord.Embed(
            title="🧹 Conversation Cleared",
            description="Your AI conversation history has been cleared.",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ai-status", description="Check AI assistant status and usage")
    async def ai_status_command(self, interaction: discord.Interaction):
        """Check AI assistant status"""
        embed = discord.Embed(
            title="🤖 AI Assistant Status",
            color=0x00ff00
        )
        
        # Check OpenAI status
        if self.openai_client:
            embed.add_field(name="Status", value="✅ Online", inline=True)
            embed.add_field(name="Model", value="GPT-4o", inline=True)
        else:
            embed.add_field(name="Status", value="❌ Offline", inline=True)
            embed.add_field(name="Issue", value="OpenAI API not configured", inline=True)
        
        # Conversation stats
        user_id = interaction.user.id
        conversation_length = len(self.get_conversation_history(user_id))
        embed.add_field(name="Your Conversation", value=f"{conversation_length} messages", inline=True)
        
        # Usage info
        embed.add_field(
            name="Usage",
            value="• Use `/ai` to ask questions\n• Use `/ai-clear` to reset conversation\n• Conversations are limited to 10 messages\n• If rate limited, wait a few minutes before trying again",
            inline=False
        )
        
        # Rate limiting info
        embed.add_field(
            name="Rate Limits",
            value="OpenAI has usage limits. If you see rate limit errors, please wait 1-2 minutes between requests.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class AIConversationView(discord.ui.View):
    """View for AI conversation controls"""
    
    def __init__(self, cog, user_id: int):
        super().__init__(timeout=300)
        self.cog = cog
        self.user_id = user_id
    
    @discord.ui.button(label="Clear History", style=discord.ButtonStyle.secondary, emoji="🧹")
    async def clear_history(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Clear conversation history button"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ You can only clear your own conversation history.",
                ephemeral=True
            )
            return
        
        self.cog.clear_conversation(self.user_id)
        await interaction.response.send_message(
            "🧹 Your conversation history has been cleared.",
            ephemeral=True
        )
    
    @discord.ui.button(label="Ask Follow-up", style=discord.ButtonStyle.primary, emoji="💬")
    async def ask_followup(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ask follow-up question button"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ You can only continue your own conversation.",
                ephemeral=True
            )
            return
        
        await interaction.response.send_modal(FollowUpModal(self.cog, self.user_id))


class FollowUpModal(discord.ui.Modal):
    """Modal for follow-up questions"""
    
    def __init__(self, cog, user_id: int):
        super().__init__(title="Ask Follow-up Question")
        self.cog = cog
        self.user_id = user_id
        
        self.question = discord.ui.TextInput(
            label="Your follow-up question",
            placeholder="Ask anything related to our conversation...",
            style=discord.TextStyle.paragraph,
            max_length=1000
        )
        self.add_item(self.question)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle follow-up question submission"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            question = self.question.value.strip()
            
            # Add user message to conversation
            self.cog.add_to_conversation(self.user_id, "user", question)
            
            # Prepare guild context
            guild_context = None
            if interaction.guild:
                guild_context = f"Server: {interaction.guild.name} (ID: {interaction.guild.id})"
            
            # Generate AI response
            ai_response = await self.cog.generate_ai_response(
                self.cog.get_conversation_history(self.user_id),
                guild_context
            )
            
            # Add AI response to conversation
            self.cog.add_to_conversation(self.user_id, "assistant", ai_response)
            
            # Create response embed
            embed = discord.Embed(
                title="🤖 NexGuard AI Assistant",
                description=ai_response,
                color=0x00ff00
            )
            embed.set_footer(text=f"Follow-up by {interaction.user.display_name}")
            
            # Add conversation controls
            view = AIConversationView(self.cog, self.user_id)
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in follow-up modal: {e}")
            await interaction.followup.send(
                "❌ An error occurred while processing your follow-up question.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(AIAssistantCog(bot))