import requests
import os
import discord
from discord.ext import commands

# NexGuard API Integration
class NexGuardAPI:
    def __init__(self):
        self.base_url = os.getenv('NEXGUARD_API_URL', 'https://ed8c2fad-d762-4890-ab60-2ba13bfca210-00-1mxalymkn4j67.janeway.replit.dev')
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def get_server_config(self, guild_id):
        try:
            response = requests.get(f'{self.base_url}/api/bot/servers/{guild_id}/config', headers=self.headers)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f'Config fetch error: {e}')
            return None
    
    def get_custom_commands(self, guild_id):
        try:
            response = requests.get(f'{self.base_url}/api/bot/servers/{guild_id}/commands', headers=self.headers)
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f'Commands fetch error: {e}')
            return []
    
    def create_custom_command(self, guild_id, name, response_text, created_by):
        try:
            response = requests.post(f'{self.base_url}/api/bot/servers/{guild_id}/commands', 
                                   json={'name': name, 'response': response_text, 'createdBy': created_by},
                                   headers=self.headers)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f'Command creation error: {e}')
            return None
    
    def log_moderation(self, guild_id, action_type, user_id, moderator_id, reason):
        try:
            requests.post(f'{self.base_url}/api/bot/servers/{guild_id}/moderation/log', 
                         json={'type': action_type, 'userId': user_id, 'moderatorId': moderator_id, 'reason': reason},
                         headers=self.headers)
            print(f'Logged {action_type} action for user {user_id}')
        except Exception as e:
            print(f'Moderation log error: {e}')

# Initialize
nexguard = NexGuardAPI()
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to NexGuard!')
    
    # Load configs for all servers
    for guild in bot.guilds:
        config = nexguard.get_server_config(str(guild.id))
        if config:
            print(f'✅ Loaded config for {guild.name}: Moderation={config.get("moderationEnabled", False)}')
        else:
            print(f'⚠️ No config found for {guild.name}, using defaults')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Check for custom commands
    commands = nexguard.get_custom_commands(str(message.guild.id))
    for cmd in commands:
        if message.content == f'!{cmd["name"]}':
            await message.reply(cmd["response"])
            return
    
    await bot.process_commands(message)

# Example moderation commands
@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    """Warn a user and log it to NexGuard dashboard"""
    nexguard.log_moderation(str(ctx.guild.id), 'warn', str(member.id), str(ctx.author.id), reason)
    await ctx.send(f'⚠️ {member.mention} has been warned for: {reason}')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason="No reason provided"):
    """Mute a user and log it to NexGuard dashboard"""
    nexguard.log_moderation(str(ctx.guild.id), 'mute', str(member.id), str(ctx.author.id), reason)
    await ctx.send(f'🔇 {member.mention} has been muted for: {reason}')

@bot.command()
@commands.has_permissions(manage_guild=True)
async def addcmd(ctx, name, *, response):
    """Add a custom command via Discord"""
    result = nexguard.create_custom_command(str(ctx.guild.id), name, response, str(ctx.author.id))
    if result:
        await ctx.send(f'✅ Custom command `!{name}` has been added!')
    else:
        await ctx.send(f'❌ Failed to create command `!{name}`')

@bot.command()
@commands.has_permissions(manage_guild=True)
async def config(ctx):
    """Show current server configuration"""
    config = nexguard.get_server_config(str(ctx.guild.id))
    if config:
        embed = discord.Embed(title="NexGuard Server Configuration", color=0x00d4ff)
        embed.add_field(name="Moderation", value="✅ Enabled" if config.get("moderationEnabled") else "❌ Disabled", inline=True)
        embed.add_field(name="Auto-Mod", value="✅ Enabled" if config.get("autoModEnabled") else "❌ Disabled", inline=True)
        embed.add_field(name="Spam Protection", value="✅ Enabled" if config.get("spamProtection") else "❌ Disabled", inline=True)
        embed.add_field(name="Welcome Messages", value="✅ Enabled" if config.get("welcomeEnabled") else "❌ Disabled", inline=True)
        embed.add_field(name="Custom Commands", value="✅ Enabled" if config.get("customCommandsEnabled") else "❌ Disabled", inline=True)
        embed.add_field(name="Dashboard", value="[Configure Settings](https://ed8c2fad-d762-4890-ab60-2ba13bfca210-00-1mxalymkn4j67.janeway.replit.dev/dashboard)", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Could not fetch server configuration")

# Run the bot
bot.run(os.getenv('DISCORD_BOT_TOKEN'))