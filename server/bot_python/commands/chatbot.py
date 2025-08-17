import discord
from discord.ext import commands
import openai
import asyncio
import json
import logging
from typing import Dict, List, Optional

# Set up logging
logger = logging.getLogger(__name__)

class ChatBot(commands.Cog):
    """AI Chatbot system for natural conversations with users"""
    
    def __init__(self, bot):
        self.bot = bot
        self.openai_client = openai.AsyncOpenAI(api_key=self.bot.openai_api_key)
        
        # Store conversation history per user (in memory for now)
        self.conversations: Dict[int, List[dict]] = {}
        
        # Bot personality and system prompt
        self.system_prompt = """You are NexGuard, a friendly and helpful Discord moderation bot with personality. You are:
        - Helpful and knowledgeable about Discord, moderation, and general topics
        - Friendly but professional 
        - Concise in responses (keep under 2000 characters for Discord)
        - Able to help with server management, Discord features, and general questions
        - Created to help Discord communities stay safe and organized
        
        You should be conversational and engaging, but remember you're a Discord bot assistant."""
        
        logger.info("🤖 AI Chatbot system initialized")

    def get_conversation_history(self, user_id: int, max_messages: int = 10) -> List[dict]:
        """Get recent conversation history for a user"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        # Return last N messages
        return self.conversations[user_id][-max_messages:] if self.conversations[user_id] else []

    def add_to_conversation(self, user_id: int, role: str, content: str):
        """Add a message to user's conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({
            "role": role,
            "content": content
        })
        
        # Keep only last 20 messages to manage memory
        if len(self.conversations[user_id]) > 20:
            self.conversations[user_id] = self.conversations[user_id][-20:]

    async def get_ai_response(self, user_id: int, user_message: str, username: str) -> str:
        """Get AI response using OpenAI"""
        try:
            # Add user message to conversation
            self.add_to_conversation(user_id, "user", user_message)
            
            # Build messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history
            conversation_history = self.get_conversation_history(user_id)
            messages.extend(conversation_history)
            
            # Get response from OpenAI
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=800,  # Keep responses reasonable for Discord
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Add AI response to conversation
            self.add_to_conversation(user_id, "assistant", ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Sorry, I'm having trouble thinking right now. Please try again in a moment!"

    @discord.app_commands.command(name="chat", description="Have a conversation with NexGuard AI")
    @discord.app_commands.describe(message="What would you like to talk about?")
    async def chat_command(self, interaction: discord.Interaction, message: str):
        """Chat with the AI using a slash command"""
        
        # Defer response since AI might take a moment
        await interaction.response.defer(ephemeral=False)
        
        try:
            # Get AI response
            ai_response = await self.get_ai_response(
                interaction.user.id, 
                message, 
                interaction.user.display_name
            )
            
            # Create embed for the response
            embed = discord.Embed(
                title="💬 NexGuard AI Chat",
                color=0x5865F2
            )
            embed.add_field(
                name=f"You asked:",
                value=message[:1000] + ("..." if len(message) > 1000 else ""),
                inline=False
            )
            embed.add_field(
                name="NexGuard responds:",
                value=ai_response,
                inline=False
            )
            embed.set_footer(text="AI Chat Assistant")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Chat command error: {e}")
            await interaction.followup.send(
                "Sorry, I encountered an error while processing your message. Please try again!",
                ephemeral=True
            )

    @discord.app_commands.command(name="clear-chat", description="Clear your chat history with NexGuard AI")
    async def clear_chat(self, interaction: discord.Interaction):
        """Clear user's conversation history"""
        
        if interaction.user.id in self.conversations:
            del self.conversations[interaction.user.id]
            await interaction.response.send_message(
                "✅ Your chat history has been cleared! Starting fresh.", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "You don't have any chat history to clear.", 
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for mentions, DMs, and keywords to respond with AI"""
        
        # Ignore bot messages
        if message.author.bot:
            return
            
        # Check if bot was mentioned, it's a DM, or contains trigger keywords
        bot_mentioned = self.bot.user in message.mentions
        is_dm = isinstance(message.channel, discord.DMChannel)
        
        # Check for trigger keywords (case insensitive)
        trigger_keywords = ["nexguard", "nex"]
        message_lower = message.content.lower()
        contains_keyword = any(keyword in message_lower for keyword in trigger_keywords)
        
        if bot_mentioned or is_dm or contains_keyword:
            # Don't respond to commands
            if message.content.startswith(('/', '!', '?', '.')):
                return
                
            try:
                # Show typing indicator
                async with message.channel.typing():
                    # Clean the message content for AI processing
                    clean_content = message.content
                    # Remove bot mentions
                    clean_content = clean_content.replace(f'<@{self.bot.user.id}>', '').strip()
                    # Remove trigger keywords if that's how they started the conversation
                    for keyword in trigger_keywords:
                        clean_content = clean_content.replace(keyword, '').strip()
                    
                    # Get AI response
                    ai_response = await self.get_ai_response(
                        message.author.id,
                        clean_content,
                        message.author.display_name
                    )
                    
                    # Send response
                    if len(ai_response) > 2000:
                        # Split long messages
                        chunks = [ai_response[i:i+1900] for i in range(0, len(ai_response), 1900)]
                        for chunk in chunks:
                            await message.reply(chunk)
                    else:
                        await message.reply(ai_response)
                        
            except Exception as e:
                logger.error(f"Auto-chat error: {e}")
                await message.reply("Sorry, I'm having trouble understanding right now. Try using `/chat` instead!")

    @discord.app_commands.command(name="set-personality", description="Change NexGuard's chatbot personality (Admin only)")
    @discord.app_commands.describe(personality="New personality description for the chatbot")
    async def set_personality(self, interaction: discord.Interaction, personality: str):
        """Allow admins to customize the bot's personality"""
        
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Only administrators can change my personality!", 
                ephemeral=True
            )
            return
            
        self.system_prompt = f"""You are NexGuard, a Discord moderation bot. Your personality: {personality}

        Keep responses under 2000 characters for Discord. You help with Discord moderation and general questions."""
        
        await interaction.response.send_message(
            f"✅ My personality has been updated! I am now: {personality[:200]}{'...' if len(personality) > 200 else ''}",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(ChatBot(bot))