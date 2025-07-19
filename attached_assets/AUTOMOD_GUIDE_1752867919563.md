# NexGuard AutoMod System Guide

## Overview

NexGuard now includes a comprehensive AutoMod system that automatically detects and handles various types of unwanted content and behaviors in your Discord server. The system is highly configurable and includes multiple protection layers.

## AutoMod Features

### 🚫 Spam Protection
- **Message Rate Limiting**: Detects users sending too many messages in a short time
- **Configurable Thresholds**: Set max messages and time windows
- **Smart Detection**: Tracks message history per user
- **Actions**: Delete, warn, or timeout users

### 🔗 Link Filtering
- **Discord Invite Blocking**: Automatically blocks Discord server invites
- **URL Filtering**: Optional blocking of all URLs
- **Pattern Recognition**: Advanced regex patterns for link detection
- **Whitelist Support**: Coming soon - ability to whitelist trusted domains

### 🤬 Bad Words Filter
- **Built-in Dictionary**: Common inappropriate words included
- **Custom Word Lists**: Add your own words to filter
- **Strict Mode**: Choose between exact word matching or substring detection
- **Smart Detection**: Handles various spelling variations

### 🔠 Caps Lock Detection
- **Percentage-based**: Detects messages with excessive capital letters
- **Configurable Threshold**: Set the caps percentage limit (default 70%)
- **Minimum Length**: Only check messages above a certain length
- **Context Aware**: Ignores short messages and common abbreviations

### 📢 Mention Limits
- **User Mention Limits**: Prevent mass user mentions
- **Role Mention Limits**: Separate limits for role mentions
- **Escalation**: Progressive punishment for repeat offenders
- **Exception Handling**: Moderators are exempt from limits

## Slash Commands

### Main Configuration Commands

#### `/automod config`
Opens an interactive configuration panel where you can select which AutoMod features to configure.

#### `/automod status`
Shows the current status of all AutoMod features for your server.

#### `/automod reset`
Resets all AutoMod settings to default (disabled).

### Feature-Specific Commands

#### `/automod-spam`
Configure spam protection settings:
- `enabled`: Enable/disable spam protection
- `max_messages`: Maximum messages allowed (1-20)
- `time_window`: Time window in seconds (1-60)
- `action`: Action to take (delete/warn/timeout)

#### `/automod-links`
Configure link filtering settings:
- `enabled`: Enable/disable link filtering
- `block_invites`: Block Discord invites
- `block_urls`: Block all URLs
- `action`: Action to take (delete/warn/timeout)

#### `/automod-badwords`
Configure bad words filter:
- `enabled`: Enable/disable bad words filter
- `strict`: Use strict mode (exact word match)
- `action`: Action to take (delete/warn/timeout)

#### `/automod-words`
Manage custom bad words list:
- `add <word>`: Add a word to the filter
- `remove <word>`: Remove a word from the filter
- `list`: Show all custom words
- `clear`: Clear all custom words

## Action Types

### Delete
- Removes the offending message
- Logs the action in the database
- Sends notification to log channel

### Warn
- Deletes the message
- Issues an official warning to the user
- Adds warning to user's record
- Sends DM to user (if possible)
- Logs to moderation channel

### Timeout
- Deletes the message
- Times out the user for 5 minutes
- Sends DM notification to user
- Logs the action with full details

## Setting Up AutoMod

### Step 1: Configure Logging
Before enabling AutoMod, set up a log channel:
```
/logging set type:moderation action:enable channel:#mod-logs
```

### Step 2: Basic Setup
Start with the configuration panel:
```
/automod config
```

### Step 3: Enable Features
Enable and configure individual features:
```
/automod-spam enabled:true max_messages:5 time_window:5 action:delete
/automod-links enabled:true block_invites:true action:warn
/automod-badwords enabled:true strict:false action:timeout
```

### Step 4: Customize Word Filter
Add custom words to the filter:
```
/automod-words action:add word:badword1
/automod-words action:add word:badword2
```

### Step 5: Test and Monitor
Monitor the log channel for AutoMod actions and adjust settings as needed.

## Best Practices

### Recommended Settings for Different Server Types

#### Small Community Server (< 100 members)
- **Spam**: 5 messages per 5 seconds, action: delete
- **Links**: Block invites only, action: warn
- **Bad Words**: Enabled with custom words, action: warn
- **Caps**: 80% threshold, action: delete
- **Mentions**: 3 user mentions, 1 role mention, action: delete

#### Medium Server (100-1000 members)
- **Spam**: 4 messages per 5 seconds, action: warn
- **Links**: Block invites and suspicious URLs, action: timeout
- **Bad Words**: Strict mode enabled, action: timeout
- **Caps**: 70% threshold, action: warn
- **Mentions**: 5 user mentions, 2 role mentions, action: warn

#### Large Server (1000+ members)
- **Spam**: 3 messages per 5 seconds, action: timeout
- **Links**: Block all URLs except whitelisted, action: timeout
- **Bad Words**: Comprehensive custom list, action: timeout
- **Caps**: 60% threshold, action: timeout
- **Mentions**: 3 user mentions, 1 role mention, action: timeout

### General Tips

1. **Start Conservative**: Begin with less strict settings and adjust based on your server's needs
2. **Monitor Regularly**: Check the log channel to see AutoMod actions and false positives
3. **Educate Staff**: Make sure moderators understand the AutoMod system
4. **Regular Updates**: Add new words to the filter as needed
5. **Exception Roles**: Consider creating bypass roles for trusted members

## Troubleshooting

### AutoMod Not Working
1. Check if the feature is enabled: `/automod status`
2. Verify bot permissions (Manage Messages, Timeout Members)
3. Check if log channel is configured: `/logging status`
4. Ensure the bot role is above user roles in the hierarchy

### False Positives
1. Review and adjust threshold settings
2. Add exceptions to word filter
3. Use less strict settings for new servers
4. Consider using warning actions instead of immediate timeouts

### Performance Issues
1. Monitor message processing speed
2. Adjust spam detection windows
3. Optimize custom word lists (remove duplicates)
4. Consider disabling less critical features during high activity

## Database Structure

AutoMod settings are stored in the `guild_settings` table under the `automod_settings` column as JSON data. The structure includes:

```json
{
  "spam": {
    "enabled": true,
    "max_messages": 5,
    "time_window": 5,
    "action": "delete"
  },
  "links": {
    "enabled": true,
    "block_invites": true,
    "block_urls": false,
    "action": "warn"
  },
  "badwords": {
    "enabled": true,
    "strict": false,
    "action": "timeout",
    "custom_words": ["word1", "word2"]
  },
  "caps": {
    "enabled": true,
    "threshold": 70,
    "min_length": 10,
    "action": "delete"
  },
  "mentions": {
    "enabled": true,
    "max_mentions": 5,
    "max_role_mentions": 2,
    "action": "delete"
  }
}
```

## Integration with Other Features

### Works With
- ✅ Logging system (all actions are logged)
- ✅ Warning system (warn actions add to user warnings)
- ✅ Moderation role system (moderators are exempt)
- ✅ Timeout system (timeout actions use Discord timeouts)

### Future Enhancements
- 🔄 Whitelist system for trusted domains
- 🔄 User reputation system
- 🔄 Advanced AI-based content detection
- 🔄 Custom punishment escalation
- 🔄 Integration with external moderation services

## Support

If you encounter issues with the AutoMod system:
1. Check this guide for common solutions
2. Review the bot logs for error messages
3. Test with a small configuration first
4. Contact support with specific error details

The AutoMod system is designed to be powerful yet easy to use. Start with basic settings and gradually customize based on your server's unique needs.