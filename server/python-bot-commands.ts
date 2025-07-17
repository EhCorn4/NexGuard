// Commands based on the actual Python bot files provided
export const pythonBotCommands = [
  // Core Commands
  {
    name: 'ping',
    description: 'Check the bot\'s latency and connection status',
  },
  {
    name: 'help',
    description: 'Show available commands and their usage',
  },
  
  // Moderation Commands
  {
    name: 'ban',
    description: 'Ban a member from the server',
    options: [
      {
        name: 'member',
        description: 'The member to ban',
        type: 6,
        required: true
      },
      {
        name: 'reason',
        description: 'The reason for the ban',
        type: 3,
        required: false
      }
    ]
  },
  {
    name: 'kick',
    description: 'Kick a member from the server',
    options: [
      {
        name: 'member',
        description: 'The member to kick',
        type: 6,
        required: true
      },
      {
        name: 'reason',
        description: 'The reason for the kick',
        type: 3,
        required: false
      }
    ]
  },
  {
    name: 'mute',
    description: 'Mute a member in the server',
    options: [
      {
        name: 'member',
        description: 'The member to mute',
        type: 6,
        required: true
      },
      {
        name: 'duration',
        description: 'Duration of the mute (e.g., 1h, 30m)',
        type: 3,
        required: false
      },
      {
        name: 'reason',
        description: 'The reason for the mute',
        type: 3,
        required: false
      }
    ]
  },
  {
    name: 'unmute',
    description: 'Unmute a member in the server',
    options: [
      {
        name: 'member',
        description: 'The member to unmute',
        type: 6,
        required: true
      }
    ]
  },
  {
    name: 'warn',
    description: 'Warn a member',
    options: [
      {
        name: 'member',
        description: 'The member to warn',
        type: 6,
        required: true
      },
      {
        name: 'reason',
        description: 'The reason for the warning',
        type: 3,
        required: true
      }
    ]
  },
  {
    name: 'warnings',
    description: 'View warnings for a member',
    options: [
      {
        name: 'member',
        description: 'The member to check warnings for',
        type: 6,
        required: true
      }
    ]
  },
  {
    name: 'purge',
    description: 'Delete multiple messages from the channel',
    options: [
      {
        name: 'amount',
        description: 'Number of messages to delete (1-100)',
        type: 4,
        required: true
      },
      {
        name: 'member',
        description: 'Only delete messages from this member',
        type: 6,
        required: false
      }
    ]
  },
  {
    name: 'purgebot',
    description: 'Delete bot messages from the channel',
    options: [
      {
        name: 'amount',
        description: 'Number of messages to check (1-100)',
        type: 4,
        required: false
      }
    ]
  },
  {
    name: 'unban',
    description: 'Unban a user from the server',
    options: [
      {
        name: 'user_id',
        description: 'The user ID to unban',
        type: 3,
        required: true
      },
      {
        name: 'reason',
        description: 'The reason for the unban',
        type: 3,
        required: false
      }
    ]
  },
  {
    name: 'banlist',
    description: 'Show the list of banned users',
  },
  {
    name: 'mutelist',
    description: 'Show the list of muted users',
  },
  {
    name: 'timeout',
    description: 'Timeout a member for a specified duration',
    options: [
      {
        name: 'member',
        description: 'The member to timeout',
        type: 6,
        required: true
      },
      {
        name: 'duration',
        description: 'Duration of the timeout (e.g., 1h, 30m)',
        type: 3,
        required: true
      },
      {
        name: 'reason',
        description: 'The reason for the timeout',
        type: 3,
        required: false
      }
    ]
  },
  {
    name: 'untimeout',
    description: 'Remove timeout from a member',
    options: [
      {
        name: 'member',
        description: 'The member to remove timeout from',
        type: 6,
        required: true
      }
    ]
  },
  {
    name: 'slowmode',
    description: 'Set slowmode for the current channel',
    options: [
      {
        name: 'seconds',
        description: 'Slowmode duration in seconds (0 to disable)',
        type: 4,
        required: true
      }
    ]
  },
  {
    name: 'lock',
    description: 'Lock a channel to prevent messages',
    options: [
      {
        name: 'channel',
        description: 'Channel to lock (current channel if not specified)',
        type: 7,
        required: false
      },
      {
        name: 'reason',
        description: 'Reason for locking the channel',
        type: 3,
        required: false
      }
    ]
  },
  {
    name: 'unlock',
    description: 'Unlock a channel to allow messages',
    options: [
      {
        name: 'channel',
        description: 'Channel to unlock (current channel if not specified)',
        type: 7,
        required: false
      }
    ]
  },
  
  // Utility Commands
  {
    name: 'userinfo',
    description: 'Get information about a user',
    options: [
      {
        name: 'user',
        description: 'The user to get information about',
        type: 6,
        required: false
      }
    ]
  },
  {
    name: 'avatar',
    description: 'Get a user\'s avatar',
    options: [
      {
        name: 'user',
        description: 'The user to get avatar for',
        type: 6,
        required: false
      }
    ]
  },
  {
    name: 'serverinfo',
    description: 'Get information about the server',
  },
  {
    name: 'commands',
    description: 'List all available commands',
  },
  {
    name: 'embed',
    description: 'Create a custom embed message',
    options: [
      {
        name: 'title',
        description: 'Embed title',
        type: 3,
        required: true
      },
      {
        name: 'description',
        description: 'Embed description',
        type: 3,
        required: true
      },
      {
        name: 'color',
        description: 'Embed color (hex code)',
        type: 3,
        required: false
      }
    ]
  },
  {
    name: 'embed-help',
    description: 'Get help with creating embeds',
  },
  {
    name: 'embed-json',
    description: 'Create an embed from JSON',
    options: [
      {
        name: 'json',
        description: 'JSON string for the embed',
        type: 3,
        required: true
      }
    ]
  },
  
  // Admin Commands
  {
    name: 'prefix',
    description: 'Set the bot prefix for this server',
    options: [
      {
        name: 'new_prefix',
        description: 'The new prefix to set',
        type: 3,
        required: true
      }
    ]
  },
  {
    name: 'resetprefix',
    description: 'Reset the bot prefix to default (!)',
  },
  {
    name: 'modrole',
    description: 'Set the moderator role',
    options: [
      {
        name: 'role',
        description: 'The role to set as moderator role',
        type: 8,
        required: true
      }
    ]
  },
  {
    name: 'resetmodrole',
    description: 'Reset the moderator role',
  },
  {
    name: 'logging',
    description: 'Configure server logging',
    options: [
      {
        name: 'action',
        description: 'Logging action to configure',
        type: 3,
        required: true,
        choices: [
          { name: 'setup', value: 'setup' },
          { name: 'disable', value: 'disable' },
          { name: 'channel', value: 'channel' }
        ]
      },
      {
        name: 'channel',
        description: 'Channel for logging',
        type: 7,
        required: false
      }
    ]
  },
  {
    name: 'changelog',
    description: 'View the bot changelog',
  },
  {
    name: 'changelog-test',
    description: 'Test changelog functionality',
  },
  {
    name: 'changelog-disable',
    description: 'Disable changelog notifications',
  },
  
  // Ticket System Commands
  {
    name: 'ticket',
    description: 'Create a support ticket',
  },
  {
    name: 'ticket-setup',
    description: 'Set up the ticket system',
    options: [
      {
        name: 'category',
        description: 'Category for ticket channels',
        type: 7,
        required: true
      },
      {
        name: 'ping_roles',
        description: 'Roles to ping when tickets are created',
        type: 3,
        required: false
      }
    ]
  },
  {
    name: 'ticket-panel',
    description: 'Create a ticket panel',
    options: [
      {
        name: 'channel',
        description: 'Channel to send the panel to',
        type: 7,
        required: false
      }
    ]
  },
  {
    name: 'ticket-close',
    description: 'Close the current ticket',
    options: [
      {
        name: 'reason',
        description: 'Reason for closing the ticket',
        type: 3,
        required: false
      }
    ]
  },
  {
    name: 'ticket-info',
    description: 'Get information about the current ticket',
  },
  {
    name: 'ticket-list',
    description: 'List all open tickets',
  },
  {
    name: 'ticket-stats',
    description: 'View ticket statistics',
  },
  {
    name: 'ticket-cleanup',
    description: 'Clean up old closed tickets',
  },
  {
    name: 'ticket-embed',
    description: 'Create a ticket embed panel',
  },
  {
    name: 'ticket-enhanced',
    description: 'Enhanced ticket creation with more options',
  },
  {
    name: 'transcript',
    description: 'Generate a transcript of the current channel',
  }
];