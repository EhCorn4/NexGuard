# NexGuard Auto-Reply System Guide

## Overview

The NexGuard Auto-Reply system provides intelligent, keyword-based automatic responses to user messages. This system has been completely debugged and optimized to prevent false triggers while maintaining high responsiveness to relevant queries.

## Recent Updates (v2.3.2)

- **Fixed Broad Keyword Issue**: Resolved problem where bot responded to every message
- **Smart Keyword Filtering**: Implemented specific phrase matching instead of common words
- **Enhanced Database Management**: Improved rule creation and management
- **Better Error Handling**: Added comprehensive error logging and recovery
- **Optimized Performance**: Reduced false positives and improved response accuracy

## Features

### Core Functionality
- **Smart Keyword Detection**: 4 match types (contains, exact, starts_with, ends_with)
- **Rich Embed Responses**: Customizable embeds with titles, descriptions, colors, and footers
- **Cooldown System**: Per-rule cooldown management to prevent spam
- **Message Filtering**: Automatically ignores links, GIFs, attachments, embeds, and system messages
- **Permission Controls**: Admin/moderator-only access with proper authentication

### Available Commands
- `/autoreply-create` - Create new auto-reply rules
- `/autoreply-list` - View all existing rules
- `/autoreply-toggle` - Enable/disable specific rules
- `/autoreply-delete` - Remove unwanted rules
- `/autoreply-stats` - View usage statistics

## Best Practices for Rule Creation

### ✅ Good Keyword Examples
- `"discord invite"` - Specific phrase for invite requests
- `"server rules"` - Clear request for rules information
- `"need help"` - Specific support request
- `"how do i join"` - Complete question phrase
- `"what is the server ip"` - Full question with context

### ❌ Avoid These Keywords
- `"i"` - Too common, matches every message with "i"
- `"can"` - Too general, matches many unrelated messages
- `"server"` - Too broad, triggers on many topics
- `"help"` - Single word, too vague
- `"the"` - Common word, causes false triggers

### Match Type Guidelines

**Contains**: Use for longer, unique phrases
```
Keywords: "discord invite link", "how to join server"
Match Type: contains
```

**Exact**: Use for specific questions or commands
```
Keywords: "rules", "ip", "discord"
Match Type: exact
```

**Starts With**: Use for command-like patterns
```
Keywords: "!help", "?rules", "/invite"
Match Type: starts_with
```

**Ends With**: Use for specific endings
```
Keywords: "server?", "help please"
Match Type: ends_with
```

## Example Auto-Reply Rules

### Discord Invite Link Rule
```json
{
  "name": "Discord Invite Link",
  "keywords": "discord invite,invite link,server invite,join link",
  "match_type": "contains",
  "response": {
    "title": "🔗 Discord Invite Link",
    "description": "**To get our server invite:**\n1. Ask a staff member\n2. Check announcements\n3. Use boost perks if available",
    "color": "#5865F2",
    "footer": "Contact staff for invite link"
  },
  "cooldown": 60
}
```

### Server Rules Rule
```json
{
  "name": "Server Rules",
  "keywords": "server rules,what are the rules,rules please",
  "match_type": "contains",
  "response": {
    "title": "📋 Server Rules",
    "description": "**Follow these rules:**\n1. Be respectful\n2. No spam\n3. Use appropriate channels\n4. No NSFW content\n5. Follow Discord ToS",
    "color": "#ff6b6b",
    "footer": "Check rules channel for details"
  },
  "cooldown": 60
}
```

### Support Help Rule
```json
{
  "name": "Support Help",
  "keywords": "need help,need support,help me,support please",
  "match_type": "contains",
  "response": {
    "title": "🎯 Need Help?",
    "description": "**I can help with:**\n• Server rules\n• Bot commands\n• Technical issues\n• General questions\n\n**Contact staff for:**\n• Ban appeals\n• Reports\n• Admin support",
    "color": "#00ff00",
    "footer": "NexGuard Support"
  },
  "cooldown": 45
}
```

## Command Usage

### Creating Rules
```
/autoreply-create
  name: "Rule Name"
  keywords: "keyword1,keyword2,keyword3"
  match_type: contains
  title: "Response Title"
  description: "Response description"
  color: "#5865F2"
  footer: "Footer text"
  cooldown: 60
```

### Managing Rules
```
/autoreply-list           # View all rules
/autoreply-toggle id:1    # Enable/disable rule
/autoreply-delete id:1    # Remove rule
/autoreply-stats          # View statistics
```

## Database Schema

### autoreply_rules Table
```sql
CREATE TABLE autoreply_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT NOT NULL,
    name TEXT NOT NULL,
    keywords TEXT NOT NULL,
    response_data TEXT NOT NULL,
    match_type TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    cooldown INTEGER DEFAULT 60,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### autoreply_cooldowns Table
```sql
CREATE TABLE autoreply_cooldowns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT NOT NULL,
    rule_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    last_triggered DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES autoreply_rules (id)
);
```

### autoreply_stats Table
```sql
CREATE TABLE autoreply_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT NOT NULL,
    rule_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES autoreply_rules (id)
);
```

## Troubleshooting

### Common Issues

**Rule not triggering:**
- Check if keywords are too specific
- Verify rule is enabled
- Ensure match type is appropriate
- Check cooldown settings

**Rule triggering too often:**
- Make keywords more specific
- Increase cooldown time
- Consider changing match type from "contains" to "exact"

**False positives:**
- Avoid common words like "i", "can", "the"
- Use longer, more specific phrases
- Consider using "exact" match type

### Debug Commands
```
/autoreply-stats          # Check trigger frequency
/autoreply-list           # Verify rule configuration
/autoreply-toggle id:X    # Temporarily disable problematic rules
```

## Performance Optimization

### Message Filtering
The system automatically filters out:
- Bot messages
- System messages (joins, boosts, etc.)
- Messages with only attachments
- Messages with only embeds
- Messages with only links
- Messages starting with command prefixes

### Cooldown Management
- Default cooldown: 60 seconds
- Minimum recommended: 30 seconds
- Maximum recommended: 300 seconds
- Per-user, per-channel, per-rule tracking

## Security Considerations

- Only administrators can create/modify rules
- All rule changes are logged
- Rate limiting prevents abuse
- Input validation prevents malicious content
- Database queries use parameterized statements

## Integration with Dashboard

The auto-reply system integrates with the NexGuard web dashboard:
- View all rules in a web interface
- Create rules through forms
- Monitor statistics and usage
- Export/import rule configurations
- Real-time trigger monitoring

## Future Enhancements

- AI-powered keyword suggestion
- Advanced pattern matching
- Multi-language support
- Voice message transcription
- Integration with other bot features
- Custom embed templates
- Scheduled auto-replies
- Conditional logic rules

## Support

For issues or questions about the auto-reply system:
1. Check this guide for common solutions
2. Review the troubleshooting section
3. Contact the development team
4. Submit bug reports through the dashboard

---

*Last updated: July 16, 2025*
*Version: 2.3.2*