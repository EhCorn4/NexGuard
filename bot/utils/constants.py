"""
Constants for NexGuard Discord Bot
Centralized constants to reduce hardcoded strings and improve maintainability
"""

# Emoji constants
class Emojis:
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    LOADING = "🔄"
    TICKET = "🎫"
    LOCK = "🔒"
    UNLOCK = "🔓"
    TRASH = "🗑️"
    HAMMER = "🔨"
    SHIELD = "🛡️"
    ROBOT = "🤖"
    PENCIL = "✏️"
    MEGAPHONE = "📢"
    THUMBS_UP = "👍"
    THUMBS_DOWN = "👎"
    WAVE = "👋"
    CROWN = "👑"
    GEAR = "⚙️"
    BELL = "🔔"
    MUTE = "🔇"
    UNMUTE = "🔊"
    BAN = "🚫"
    KICK = "🦵"
    TIMEOUT = "⏰"
    SLOWMODE = "🐌"
    PURGE = "🧹"
    LOGS = "📝"
    STATS = "📊"
    HELP = "❓"
    PING = "🏓"
    ONLINE = "🟢"
    OFFLINE = "🔴"
    IDLE = "🟡"
    DND = "⛔"

# Color constants
class Colors:
    SUCCESS = 0x00ff00
    ERROR = 0xff0000
    WARNING = 0xffff00
    INFO = 0x0099ff
    DEFAULT = 0x7289da
    PURPLE = 0x9966cc
    ORANGE = 0xff9900
    PINK = 0xff69b4
    GOLD = 0xffd700
    SILVER = 0xc0c0c0
    BLACK = 0x000000
    WHITE = 0xffffff
    GREY = 0x808080
    DARK_GREY = 0x36393f
    LIGHT_GREY = 0x99aab5
    BLURPLE = 0x7289da
    GREYPLE = 0x99aab5

# Message constants
class Messages:
    PERMISSION_DENIED = "You don't have permission to use this command."
    COMMAND_ERROR = "An error occurred while executing this command."
    SETUP_COMPLETE = "Setup completed successfully!"
    INVALID_USER = "Invalid user specified."
    INVALID_CHANNEL = "Invalid channel specified."
    INVALID_ROLE = "Invalid role specified."
    NO_REASON_PROVIDED = "No reason provided."
    MEMBER_NOT_FOUND = "Member not found in this server."
    MISSING_PERMISSIONS = "I don't have the required permissions to perform this action."
    RATE_LIMITED = "You're being rate limited. Please try again later."
    MAINTENANCE_MODE = "This feature is currently under maintenance."
    FEATURE_DISABLED = "This feature is currently disabled."
    INVALID_ARGUMENT = "Invalid argument provided."
    COMMAND_COOLDOWN = "This command is on cooldown."
    DM_ONLY = "This command can only be used in direct messages."
    GUILD_ONLY = "This command can only be used in servers."
    OWNER_ONLY = "This command can only be used by the bot owner."
    BOT_MISSING_PERMISSIONS = "I'm missing the following permissions: {permissions}"
    USER_MISSING_PERMISSIONS = "You're missing the following permissions: {permissions}"

# Database constants
class Database:
    DEFAULT_PREFIX = "!"
    MAX_WARNINGS = 5
    MAX_MESSAGE_LENGTH = 2000
    MAX_EMBED_FIELD_LENGTH = 1024
    MAX_EMBED_DESCRIPTION_LENGTH = 4096
    MAX_EMBED_TITLE_LENGTH = 256
    MAX_EMBED_FOOTER_LENGTH = 2048
    MAX_EMBED_AUTHOR_LENGTH = 256
    LOG_CLEANUP_DAYS = 30
    CONNECTION_TIMEOUT = 30

# Limits and constraints
class Limits:
    MAX_SLOWMODE_SECONDS = 21600  # 6 hours
    MAX_TIMEOUT_SECONDS = 2419200  # 28 days
    MAX_PURGE_MESSAGES = 100
    MAX_WARNINGS_PER_USER = 10
    MAX_MUTES_PER_USER = 5
    MAX_TICKETS_PER_USER = 3
    MAX_AUTOROLES = 10
    MAX_PING_ROLES = 5
    MAX_CUSTOM_COMMANDS = 50
    MAX_EMBED_FIELDS = 25
    MAX_BUTTON_ROWS = 5
    MAX_BUTTONS_PER_ROW = 5
    MAX_SELECT_OPTIONS = 25
    MAX_CONVERSATION_LENGTH = 10  # For AI assistant
    MAX_AI_TOKENS = 400
    MAX_WELCOME_MESSAGE_LENGTH = 1500

# Automod constants
class AutoMod:
    DEFAULT_SPAM_LIMIT = 5
    DEFAULT_SPAM_WINDOW = 10
    DEFAULT_CAPS_THRESHOLD = 70
    DEFAULT_MENTION_LIMIT = 5
    DEFAULT_ROLE_MENTION_LIMIT = 2
    DEFAULT_LINK_WHITELIST = []
    DEFAULT_BADWORD_LIST = [
        "spam", "scam", "hack", "cheat", "bot", "fake", "virus", "malware"
    ]
    INVITE_PATTERNS = [
        r'discord\.gg/[a-zA-Z0-9]+',
        r'discordapp\.com/invite/[a-zA-Z0-9]+',
        r'discord\.com/invite/[a-zA-Z0-9]+',
        r'dsc\.gg/[a-zA-Z0-9]+',
        r'invite\.gg/[a-zA-Z0-9]+',
    ]
    URL_PATTERNS = [
        r'https?://[^\s]+',
        r'www\.[^\s]+',
        r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}',
    ]

# Ticket system constants
class Tickets:
    DEFAULT_CATEGORY_NAME = "Support Tickets"
    DEFAULT_PANEL_TITLE = "Support Ticket System"
    DEFAULT_PANEL_DESCRIPTION = "Need help? Create a support ticket and our team will assist you!"
    CHANNEL_NAME_FORMAT = "🎫ticket-{:04d}"
    MAX_SUBJECT_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_ADDITIONAL_INFO_LENGTH = 500
    AUTO_CLOSE_DELAY = 5  # seconds
    TICKET_TIMEOUT = 300  # seconds

# Welcome system constants
class Welcome:
    DEFAULT_TONE = "friendly"
    AVAILABLE_TONES = ["friendly", "professional", "enthusiastic", "warm", "gaming"]
    MAX_TEMPLATE_LENGTH = 1500
    DEFAULT_CHANNEL_NAME = "welcome"
    PLACEHOLDER_PATTERNS = [
        "{user}", "{user.mention}", "{user.name}", "{user.id}",
        "{server}", "{server.name}", "{server.id}", "{server.member_count}",
        "{channel}", "{channel.mention}", "{channel.name}", "{channel.id}",
        "{date}", "{time}", "{datetime}"
    ]

# Logging constants
class Logging:
    LOG_TYPES = [
        "message", "member", "moderation", "channel", "role", "server", "voice"
    ]
    DEFAULT_LOG_CHANNEL = "nexguard-logs"
    MAX_LOG_MESSAGE_LENGTH = 1800
    LOG_EMBED_LIMIT = 10
    LOG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_RETENTION_DAYS = 30

# Permissions
class Permissions:
    ADMINISTRATOR = "administrator"
    MANAGE_GUILD = "manage_guild"
    MANAGE_ROLES = "manage_roles"
    MANAGE_CHANNELS = "manage_channels"
    MANAGE_MESSAGES = "manage_messages"
    MANAGE_NICKNAMES = "manage_nicknames"
    KICK_MEMBERS = "kick_members"
    BAN_MEMBERS = "ban_members"
    MUTE_MEMBERS = "mute_members"
    DEAFEN_MEMBERS = "deafen_members"
    MOVE_MEMBERS = "move_members"
    VIEW_AUDIT_LOG = "view_audit_log"
    SEND_MESSAGES = "send_messages"
    EMBED_LINKS = "embed_links"
    ATTACH_FILES = "attach_files"
    READ_MESSAGE_HISTORY = "read_message_history"
    ADD_REACTIONS = "add_reactions"
    USE_EXTERNAL_EMOJIS = "use_external_emojis"
    CONNECT = "connect"
    SPEAK = "speak"
    STREAM = "stream"
    USE_VOICE_ACTIVATION = "use_voice_activation"

# API and rate limiting constants
class API:
    DISCORD_API_VERSION = 10
    DISCORD_CDN_URL = "https://cdn.discordapp.com"
    DISCORD_API_URL = "https://discord.com/api"
    OPENAI_API_URL = "https://api.openai.com/v1"
    OPENAI_MODEL = "gpt-4o"
    OPENAI_MAX_TOKENS = 4000
    OPENAI_TEMPERATURE = 0.7
    RATE_LIMIT_WINDOW = 60  # seconds
    RATE_LIMIT_MAX_REQUESTS = 100
    REQUEST_TIMEOUT = 30  # seconds

# File and path constants
class Files:
    DATABASE_FILE = "nexguard/database/nexguard.db"
    LOG_FILE = "nexguard.log"
    CONFIG_FILE = ".env"
    BACKUP_FOLDER = "backups"
    TEMP_FOLDER = "temp"
    TRANSCRIPT_FOLDER = "transcripts"
    MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB Discord limit
    ALLOWED_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp"]
    ALLOWED_FILE_EXTENSIONS = [".txt", ".log", ".json", ".csv", ".md"]

# Time constants (in seconds)
class Time:
    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    MONTH = 2592000  # 30 days
    YEAR = 31536000  # 365 days

# Status constants
class Status:
    ONLINE = "online"
    OFFLINE = "offline"
    IDLE = "idle"
    DND = "dnd"
    INVISIBLE = "invisible"

# Activity types
class ActivityType:
    PLAYING = "playing"
    STREAMING = "streaming"
    LISTENING = "listening"
    WATCHING = "watching"
    CUSTOM = "custom"
    COMPETING = "competing"

# Default settings
class Defaults:
    PREFIX = "!"
    EMBED_COLOR = Colors.DEFAULT
    TIMEOUT_DURATION = 300  # 5 minutes
    SLOWMODE_DURATION = 5  # 5 seconds
    PURGE_LIMIT = 100
    WARN_THRESHOLD = 3
    MUTE_DURATION = 3600  # 1 hour
    WELCOME_CHANNEL = "general"
    LOG_CHANNEL = "nexguard-logs"
    TICKET_CATEGORY = "Support Tickets"
    AUTOMOD_ENABLED = False
    AUTOROLE_ENABLED = False
    WELCOME_ENABLED = False
    LOGGING_ENABLED = True
    AI_ASSISTANT_ENABLED = True
    EMBED_TIMESTAMP = True
    EMBED_FOOTER = True
    BUTTON_TIMEOUT = 300  # 5 minutes
    MODAL_TIMEOUT = 300  # 5 minutes
    VIEW_TIMEOUT = 300  # 5 minutes

# Error messages
class Errors:
    GENERIC_ERROR = "An unexpected error occurred. Please try again later."
    DATABASE_ERROR = "Database connection failed. Please contact support."
    PERMISSION_ERROR = "Missing required permissions to perform this action."
    INVALID_INPUT = "Invalid input provided. Please check your arguments."
    RATE_LIMIT_ERROR = "Rate limit exceeded. Please wait before trying again."
    TIMEOUT_ERROR = "Operation timed out. Please try again."
    NOT_FOUND_ERROR = "The requested resource was not found."
    ALREADY_EXISTS_ERROR = "The resource already exists."
    FEATURE_DISABLED_ERROR = "This feature is currently disabled."
    MAINTENANCE_ERROR = "This feature is under maintenance."
    OPENAI_ERROR = "AI service is temporarily unavailable."
    DISCORD_ERROR = "Discord API error occurred."
    NETWORK_ERROR = "Network connection failed."
    FILE_ERROR = "File operation failed."
    PARSING_ERROR = "Failed to parse input data."
    VALIDATION_ERROR = "Input validation failed."

# Success messages
class Success:
    COMMAND_EXECUTED = "Command executed successfully."
    SETTINGS_UPDATED = "Settings updated successfully."
    USER_MODERATED = "User has been moderated successfully."
    CHANNEL_CREATED = "Channel created successfully."
    ROLE_ASSIGNED = "Role assigned successfully."
    MESSAGE_SENT = "Message sent successfully."
    DATA_EXPORTED = "Data exported successfully."
    BACKUP_CREATED = "Backup created successfully."
    FEATURE_ENABLED = "Feature enabled successfully."
    FEATURE_DISABLED = "Feature disabled successfully."
    CLEANUP_COMPLETED = "Cleanup completed successfully."
    SYNC_COMPLETED = "Synchronization completed successfully."
    SETUP_COMPLETED = "Setup completed successfully."
    INSTALLATION_COMPLETED = "Installation completed successfully."
    UPDATE_COMPLETED = "Update completed successfully."