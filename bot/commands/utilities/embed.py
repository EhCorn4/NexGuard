import discord
from discord.ext import commands
from discord import app_commands
import json
import logging
from typing import Optional, Literal

logger = logging.getLogger(__name__)

class ActionButton(discord.ui.Button):
    def __init__(self, button_data: dict):
        style_map = {
            "primary": discord.ButtonStyle.primary,
            "secondary": discord.ButtonStyle.secondary,
            "success": discord.ButtonStyle.success,
            "danger": discord.ButtonStyle.danger,
            "link": discord.ButtonStyle.link
        }
        
        super().__init__(
            label=button_data.get("label", "Button"),
            style=style_map.get(button_data.get("style", "primary"), discord.ButtonStyle.primary),
            emoji=button_data.get("emoji"),
            url=button_data.get("url") if button_data.get("style") == "link" else None,
            disabled=button_data.get("disabled", False)
        )
        
        self.button_data = button_data
    
    async def callback(self, interaction: discord.Interaction):
        action = self.button_data.get("action")
        
        if action == "open_ticket":
            # Check if ticket system is available
            ticket_cog = interaction.client.get_cog('TicketCog')
            if ticket_cog:
                await ticket_cog.ticket_command(interaction)
            else:
                await interaction.response.send_message("❌ Ticket system is not available.", ephemeral=True)
        
        elif action == "custom_message":
            message = self.button_data.get("message", "Button clicked!")
            await interaction.response.send_message(message, ephemeral=True)
        
        elif action == "role_toggle":
            role_id = self.button_data.get("role_id")
            if role_id:
                role = interaction.guild.get_role(role_id)
                if role:
                    if role in interaction.user.roles:
                        await interaction.user.remove_roles(role)
                        await interaction.response.send_message(f"✅ Removed {role.name} role!", ephemeral=True)
                    else:
                        await interaction.user.add_roles(role)
                        await interaction.response.send_message(f"✅ Added {role.name} role!", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Role not found.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Role not configured.", ephemeral=True)
        
        else:
            await interaction.response.send_message("Button clicked!", ephemeral=True)

class EmbedActionView(discord.ui.View):
    def __init__(self, embed_dict: dict):
        super().__init__(timeout=300)
        self.embed_dict = embed_dict
        
        # Add action buttons if specified
        if "action_buttons" in embed_dict:
            for button_data in embed_dict["action_buttons"]:
                self.add_item(ActionButton(button_data))

class EmbedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='embed', description='Create a custom embed with all options')
    @app_commands.describe(
        title="The embed title",
        description="The main embed description",
        color="Embed color (hex like #FF0000 or name like red)",
        thumbnail="Thumbnail image URL",
        image="Main image URL",
        footer="Footer text",
        author="Author name",
        field_name="Field name (optional)",
        field_value="Field value (optional)",
        field_inline="Make field inline (optional)",
        button_label="Action button label (optional)",
        button_action="Action button type (optional)",
        button_style="Button style (optional)",
        channel="Channel to send embed to (optional)"
    )
    async def embed_builder(
        self,
        interaction: discord.Interaction,
        title: str = None,
        description: str = None,
        color: str = None,
        thumbnail: str = None,
        image: str = None,
        footer: str = None,
        author: str = None,
        field_name: str = None,
        field_value: str = None,
        field_inline: bool = False,
        button_label: str = None,
        button_action: Literal["open_ticket", "custom_message", "role_toggle"] = None,
        button_style: Literal["primary", "secondary", "success", "danger"] = "primary",
        channel: discord.TextChannel = None
    ):
        """Create a custom embed with all options in slash command"""
        
        # Validate inputs
        if not title and not description:
            await interaction.response.send_message("❌ You must provide at least a title or description.", ephemeral=True)
            return
        
        # Parse color
        embed_color = discord.Color.blue()  # default
        if color:
            color_value = color.strip()
            if color_value.startswith('#'):
                try:
                    embed_color = discord.Color(int(color_value[1:], 16))
                except ValueError:
                    embed_color = discord.Color.blue()
            else:
                # Color name mapping
                color_map = {
                    'red': discord.Color.red(),
                    'blue': discord.Color.blue(),
                    'green': discord.Color.green(),
                    'yellow': discord.Color.yellow(),
                    'purple': discord.Color.purple(),
                    'orange': discord.Color.orange(),
                    'gold': discord.Color.gold(),
                    'pink': discord.Color.magenta(),
                    'black': discord.Color.from_rgb(0, 0, 0),
                    'white': discord.Color.from_rgb(255, 255, 255),
                    'grey': discord.Color.light_grey(),
                    'gray': discord.Color.light_grey(),
                    'blurple': discord.Color.blurple(),
                    'greyple': discord.Color.greyple()
                }
                embed_color = color_map.get(color_value.lower(), discord.Color.blue())
        
        # Create embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=embed_color,
            timestamp=discord.utils.utcnow()
        )
        
        # Add optional components
        if author:
            embed.set_author(name=author)
        
        if thumbnail:
            try:
                embed.set_thumbnail(url=thumbnail)
            except (discord.HTTPException, ValueError) as e:
                logger.warning(f"Failed to set thumbnail URL: {e}")
        
        if image:
            try:
                embed.set_image(url=image)
            except (discord.HTTPException, ValueError) as e:
                logger.warning(f"Failed to set image URL: {e}")
        
        if footer:
            embed.set_footer(text=footer)
        
        if field_name and field_value:
            embed.add_field(name=field_name, value=field_value, inline=field_inline)
        
        # Create embed dict for action buttons
        embed_dict = embed.to_dict()
        
        # Add action button if specified
        if button_label and button_action:
            embed_dict["action_buttons"] = [{
                "label": button_label,
                "action": button_action,
                "style": button_style,
                "emoji": "🎫" if button_action == "open_ticket" else None
            }]
        
        # Create action view
        view = EmbedActionView(embed_dict) if "action_buttons" in embed_dict else None
        
        # Send embed
        try:
            if channel:
                await channel.send(embed=embed, view=view)
                await interaction.response.send_message(f"✅ Embed sent to {channel.mention}!", ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, view=view)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating embed: {str(e)}", ephemeral=True)
        
        logger.info(f"Embed created by {interaction.user} in {interaction.guild.name}")
        
    @app_commands.command(name='embed-json', description='Create an embed from JSON code')
    @app_commands.describe(
        json_code="The JSON code for the embed",
        channel="Channel to send the embed to (optional)"
    )
    async def embed_from_json(self, interaction: discord.Interaction, json_code: str, channel: discord.TextChannel = None):
        """Create an embed from JSON code"""
        
        try:
            embed_dict = json.loads(json_code)
            embed = discord.Embed.from_dict(embed_dict)
            
            # Create action view if buttons are specified
            view = EmbedActionView(embed_dict) if "action_buttons" in embed_dict else None
            
            if channel:
                await channel.send(embed=embed, view=view)
                await interaction.response.send_message(f"✅ Embed sent to {channel.mention}!", ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, view=view)
                
        except json.JSONDecodeError:
            await interaction.response.send_message("❌ Invalid JSON format. Please check your JSON syntax.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating embed from JSON: {str(e)}", ephemeral=True)
        
        logger.info(f"Embed from JSON created by {interaction.user} in {interaction.guild.name}")
        
    @app_commands.command(name='embed-help', description='Get help and examples for using the embed builder')
    async def embed_help(self, interaction: discord.Interaction):
        """Get help and examples for using the embed builder"""
        
        embed = discord.Embed(
            title="📝 Embed Builder Help",
            description="Learn how to create beautiful embeds with action buttons!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🚀 Basic Usage",
            value="Use `/embed` with parameters to create embeds instantly. Only title or description is required.",
            inline=False
        )
        
        embed.add_field(
            name="🎨 Color Options",
            value="Use hex colors (`#FF0000`) or names (`red`, `blue`, `green`, `yellow`, `purple`, `orange`, `gold`, `pink`, `black`, `white`, `grey`, `blurple`, `greyple`)",
            inline=False
        )
        
        embed.add_field(
            name="🔘 Action Buttons",
            value="**open_ticket**: Creates a support ticket\n**custom_message**: Shows a custom message\n**role_toggle**: Adds/removes a role (requires role ID in JSON)",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Button Styles",
            value="**primary**: Blue button\n**secondary**: Grey button\n**success**: Green button\n**danger**: Red button",
            inline=False
        )
        
        embed.add_field(
            name="📝 Example Commands",
            value="```/embed title:Welcome description:Click below to open a ticket! button_label:Open Ticket button_action:open_ticket button_style:success```",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Advanced Features",
            value="• **JSON Support**: Use `/embed-json` for complex embeds\n• **Multiple Fields**: Add one field per command\n• **Images**: Add thumbnail and main images\n• **Custom Author**: Set author name",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Permissions",
            value="Everyone can use the embed builder! No special permissions needed.",
            inline=False
        )
        
        embed.set_footer(text="Use /embed to get started!")
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(EmbedCog(bot))