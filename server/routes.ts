import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertTestimonialSchema, insertFeedbackSchema } from "@shared/schema";
import fetch from "node-fetch";
import { emailService } from "./lib/emailService";
import fs from "fs";
import path from "path";
import PDFDocument from "pdfkit";



function generateQuickStartGuide(): string {
  return `# NexGuard Quick Start Guide
Version 2.3.2 | ${new Date().toLocaleDateString()}

## Table of Contents
1. Introduction
2. Bot Invitation & Setup
3. Essential First Commands
4. Basic Configuration
5. Testing Your Setup
6. Next Steps

## 1. Introduction

Welcome to NexGuard, a professional Discord bot management system with 60+ commands across 8 specialized categories. This guide will help you get started quickly with the essential features.

### What NexGuard Offers:
- Professional ticket system with persistent panels
- Advanced moderation with AutoMod
- Server statistics and analytics
- Role management and reaction roles
- Event logging and audit trails
- Auto-reply system
- Webhook integration

## 2. Bot Invitation & Setup

### Step 1: Invite the Bot
1. Use this invitation link: https://discord.com/oauth2/authorize?client_id=1389775821794705429&permissions=8&scope=bot%20applications.commands
2. Select your server from the dropdown
3. Ensure all permissions are checked (Administrator recommended)
4. Click "Authorize"

### Step 2: Verify Bot Status
Run \`/ping\` to ensure the bot is responsive.

### Required Permissions:
- Administrator (recommended) OR
- Manage Channels, Manage Roles, Manage Messages, Send Messages, Embed Links, Attach Files, Read Message History, Use Slash Commands

## 3. Essential First Commands

### Check Available Commands
\`/commands\` - View all 60 available commands organized by category

### Get Help
\`/help <command>\` - Get detailed information about any command

### Bot Information
\`/botinfo\` - View bot statistics and system information

## 4. Basic Configuration

### Set Up Admin Roles
\`/modrole add @Admin\` - Add admin roles for management access
\`/modrole list\` - View configured moderator roles

### Configure Basic AutoMod
\`/automod-config\` - Access AutoMod settings panel
- Enable spam protection
- Set up basic word filtering
- Configure automated punishments

### Create Your First Ticket Panel
\`/ticket-panel action:create title:"Support" description:"Click for help"\`
\`/ticket-panel action:deploy\` - Deploy all ticket panels

## 5. Testing Your Setup

### Test AutoMod
Try sending spam messages to verify AutoMod is working

### Test Ticket System
Click your ticket panel to create a test ticket
Use \`/close\` to close the ticket

### Test Moderation
\`/timeout @user 10m Reason\` - Test timeout functionality

## 6. Next Steps

### Recommended Setup Order:
1. Configure AutoMod settings
2. Set up ticket categories and panels
3. Add reaction roles
4. Configure server statistics
5. Set up event logging

### Advanced Features to Explore:
- Server analytics dashboard
- Custom auto-replies
- Advanced moderation logs
- Webhook integrations

### Get Support:
Join our support server: https://discord.gg/wpjZMPXaRT

---
© 2025 NexGuard. All rights reserved.`;
}

function generateAutoModGuide(): string {
  return `# NexGuard AutoMod Setup Guide
Version 2.3.2 | ${new Date().toLocaleDateString()}

## Table of Contents
1. AutoMod Overview
2. Initial Configuration
3. Spam Protection
4. Word Filtering
5. Link Management
6. Caps Lock Protection
7. Advanced Settings
8. Troubleshooting

## 1. AutoMod Overview

NexGuard's AutoMod system provides comprehensive automated moderation with multiple protection layers including spam detection, content filtering, and behavioral analysis.

### Key Features:
- Real-time spam detection
- Customizable word filtering
- Link whitelist/blacklist system
- Caps lock percentage limits
- Automated punishment system
- Bypass roles for staff
- Detailed logging

## 2. Initial Configuration

### Access AutoMod Settings
\`/automod-config\` - Opens the AutoMod configuration panel

### Basic Setup Steps:
1. Enable AutoMod system
2. Set moderator bypass roles
3. Configure logging channel
4. Set default punishment levels

### Essential Commands:
- \`/automod-status\` - Check system health
- \`/automod-test\` - Test current configuration
- \`/automod-bypass @role\` - Add bypass roles

## 3. Spam Protection

### Configuration Options:
- **Message Limit**: Max messages per time window (default: 5)
- **Time Window**: Seconds to count messages (default: 10)
- **Punishment**: warn/timeout/kick/ban

### Setup Example:
\`\`\`
/automod-config spam_protection:enabled
Max Messages: 5
Time Window: 10 seconds
Action: timeout
Duration: 5 minutes
\`\`\`

### Advanced Spam Detection:
- Duplicate message detection
- Rapid message analysis
- Pattern recognition
- User behavior tracking

## 4. Word Filtering

### Bad Word Lists:
- Default profanity filter
- Custom word lists
- Severity levels (mild/moderate/severe)
- Context-aware filtering

### Configuration:
\`\`\`
/automod-config word_filter:enabled
Action: delete_and_warn
Notify Mods: true
Custom Words: [word1, word2, word3]
\`\`\`

### Filter Actions:
- **Delete**: Remove message only
- **Warn**: Delete + warn user
- **Timeout**: Delete + timeout user
- **Escalate**: Progressive punishments

## 5. Link Management

### Link Filtering Options:
- Block all links
- Whitelist mode (only approved domains)
- Blacklist mode (block specific domains)
- Bypass for trusted roles

### Setup Whitelist:
\`\`\`
/automod-config link_filter:whitelist
Allowed Domains:
- discord.com
- youtube.com
- your-website.com
\`\`\`

### Anti-Phishing:
- Automatic malicious link detection
- Real-time URL analysis
- Domain reputation checking

## 6. Caps Lock Protection

### Configuration:
- **Percentage Threshold**: % of caps allowed (default: 70%)
- **Minimum Length**: Min message length to check (default: 10)
- **Action**: warn/delete/timeout

### Example Setup:
\`\`\`
Caps Limit: 70%
Minimum Length: 15 characters
Action: warn
\`\`\`

## 7. Advanced Settings

### Punishment Escalation:
1. First offense: Warning
2. Second offense: 5-minute timeout
3. Third offense: 1-hour timeout
4. Fourth offense: Temporary ban

### Custom Triggers:
- Emoji spam detection
- Mention spam protection
- Zalgo text filtering
- Excessive formatting

### Integration Settings:
- Webhook notifications
- Staff alert system
- Appeal process setup
- Evidence collection

## 8. Troubleshooting

### Common Issues:

**AutoMod not working:**
- Check bot permissions
- Verify AutoMod is enabled
- Review bypass roles
- Test with \`/automod-test\`

**False positives:**
- Adjust sensitivity settings
- Add bypass roles for staff
- Review word filter lists
- Check context settings

**Performance issues:**
- Review filter complexity
- Check server load
- Optimize trigger patterns
- Monitor response times

### Monitoring Commands:
- \`/automod-stats\` - View statistics
- \`/automod-logs\` - Recent actions
- \`/automod-appeals\` - Manage appeals

### Best Practices:
1. Start with conservative settings
2. Monitor for false positives
3. Regular review and adjustment
4. Train staff on bypass procedures
5. Maintain clear appeal process

---
For advanced configuration and custom setups, join our support server.
© 2025 NexGuard. All rights reserved.`;
}

function generateTicketGuide(): string {
  return `# NexGuard Ticket System Guide
Version 2.3.2 | ${new Date().toLocaleDateString()}

## Table of Contents
1. System Overview
2. Creating Ticket Panels
3. Panel Management
4. Ticket Categories
5. Staff Management
6. Advanced Features
7. Best Practices

## 1. System Overview

NexGuard's ticket system provides professional support management with persistent panels, automatic transcripts, and comprehensive staff tools.

### Key Features:
- Persistent interactive panels
- Automatic channel creation
- Staff claim/close system
- Transcript generation
- Category-based organization
- Permission management
- Analytics tracking

### System Benefits:
- TicketsBot.net-style functionality
- Survives bot restarts
- Professional appearance
- Scalable for any server size

## 2. Creating Ticket Panels

### Basic Panel Creation:
\`\`\`
/ticket-panel action:create
Title: "General Support"
Description: "Click the button below for help"
Category: "Support Tickets"
Button Text: "Create Ticket"
\`\`\`

### Panel Types:
- **General Support**: Basic help requests
- **Bug Reports**: Technical issues
- **Appeals**: Ban/punishment appeals
- **Staff Applications**: Role applications
- **Custom**: Specialized categories

### Deployment:
\`/ticket-panel action:deploy\` - Make panels live and interactive

## 3. Panel Management

### View Existing Panels:
\`/ticket-panel action:list\` - Shows all created panels

### Panel Configuration:
- **Title**: Display name
- **Description**: Help text
- **Category**: Channel category for tickets
- **Emoji**: Button emoji
- **Color**: Embed color
- **Permissions**: Who can create tickets

### Panel Actions:
- \`action:edit\` - Modify existing panel
- \`action:delete\` - Remove panel
- \`action:refresh\` - Update interactive components

## 4. Ticket Categories

### Category Setup:
1. Create Discord category channels
2. Set proper permissions
3. Assign to ticket panels
4. Configure staff access

### Permission Template:
\`\`\`
Category Permissions:
@everyone: View Channel (❌)
@Support Staff: View/Send Messages (✅)
Bot: Manage Channels (✅)
\`\`\`

### Category Types:
- **Public**: Visible to ticket creator + staff
- **Private**: Staff only
- **Restricted**: Specific role access

## 5. Staff Management

### Essential Commands:
- \`/claim\` - Claim ticket for personal handling
- \`/close\` - Close ticket with optional reason
- \`/add @user\` - Add user to ticket
- \`/remove @user\` - Remove user from ticket
- \`/rename <name>\` - Rename ticket channel

### Ticket Controls:
Each ticket includes interactive buttons:
- 🔒 **Close**: Close ticket with transcript
- 🙌 **Claim**: Assign to staff member
- ➕ **Add**: Add users to ticket
- 📝 **Rename**: Change channel name

### Staff Permissions:
- View all tickets
- Close any ticket
- Add/remove users
- Access transcripts
- View analytics

## 6. Advanced Features

### Automatic Transcripts:
- Generated on ticket close
- Sent to user via DM
- Stored in staff channel
- Includes full conversation history

### Channel Naming:
Format: \`{panel}-{username}\`
Examples:
- support-johnsmith
- appeals-alice123
- bugs-developer42

### Custom Variables:
Use in panel descriptions:
- \`{user.mention}\` - User mention
- \`{user.name}\` - Username
- \`{guild.name}\` - Server name
- \`{timestamp}\` - Current time

### Analytics:
- Ticket volume tracking
- Response time metrics
- Staff performance
- Category popularity

## 7. Best Practices

### Panel Design:
- Clear, concise titles
- Helpful descriptions
- Appropriate emojis
- Professional appearance

### Category Organization:
- Logical grouping
- Clear permissions
- Proper naming
- Staff accessibility

### Staff Training:
- Response procedures
- Escalation protocols
- Documentation standards
- Customer service skills

### Performance Optimization:
- Regular cleanup of old tickets
- Archive closed tickets
- Monitor response times
- Review staff workload

### Troubleshooting:

**Panels not working:**
- Check bot permissions
- Verify deployment status
- Review category permissions
- Test with \`/ticket-panel action:test\`

**Tickets not creating:**
- Verify category exists
- Check permission settings
- Ensure bot can create channels
- Review role hierarchy

### Maintenance Commands:
- \`/ticket-stats\` - View ticket statistics
- \`/ticket-cleanup\` - Remove old tickets
- \`/ticket-archive\` - Archive closed tickets
- \`/ticket-restore\` - Restore archived tickets

### Integration Options:
- Webhook notifications
- External ticketing systems
- CRM integration
- Analytics export

---
For advanced customization and enterprise features, contact our support team.
© 2025 NexGuard. All rights reserved.`;
}

function generateAnalyticsGuide(): string {
  return `# NexGuard Analytics & Logging Guide
Version 2.3.2 | ${new Date().toLocaleDateString()}

## Table of Contents
1. Analytics Overview
2. Server Statistics
3. Event Logging
4. Performance Monitoring
5. Data Visualization
6. Export & Reporting
7. Privacy & Compliance

## 1. Analytics Overview

NexGuard provides comprehensive analytics and logging capabilities for data-driven server management and detailed audit trails.

### Key Components:
- Real-time server statistics
- Comprehensive event logging
- Performance monitoring
- User activity tracking
- Command usage analytics
- Moderation insights

### Benefits:
- Evidence-based decisions
- Performance optimization
- Compliance documentation
- Trend identification
- Staff accountability

## 2. Server Statistics

### Live Statistics Channels:
Display real-time server metrics in voice channel names:

\`\`\`
/serverstats add type:member_count
Channel: 👥 Members: 1,234

/serverstats add type:channel_count  
Channel: 💬 Channels: 56

/serverstats add type:role_count
Channel: 🏷️ Roles: 23

/serverstats add type:boost_count
Channel: 🚀 Boosts: 12
\`\`\`

### Available Metrics:
- **Member Count**: Total server members
- **Online Count**: Currently online members
- **Channel Count**: Total channels
- **Role Count**: Total roles
- **Boost Level**: Server boost tier
- **Bot Count**: Number of bots

### Management Commands:
- \`/serverstats list\` - View configured stats
- \`/serverstats remove <id>\` - Remove stat channel
- \`/serverstats force-update\` - Manual update
- \`/serverstats cleanup\` - Remove orphaned entries

## 3. Event Logging

### Log Categories:

**Member Events:**
- Joins and leaves
- Role changes
- Nickname updates
- Profile modifications

**Message Events:**
- Message deletions
- Message edits
- Bulk deletions
- Attachment handling

**Channel Events:**
- Channel creation/deletion
- Permission changes
- Topic modifications
- Channel moves

**Server Events:**
- Role management
- Server settings changes
- Invite creation/deletion
- Emoji/sticker changes

### Setup Event Logging:
\`\`\`
/eventlog setup
Log Channel: #audit-logs
Events: all
Format: detailed
Webhook: enabled
\`\`\`

### Log Formats:
- **Simple**: Basic event information
- **Detailed**: Full context and metadata
- **Minimal**: Essential data only
- **Custom**: User-defined format

## 4. Performance Monitoring

### Bot Performance:
- Command response times
- Memory usage tracking
- Database query performance
- API latency monitoring

### Server Health:
- Message frequency analysis
- User activity patterns
- Channel usage statistics
- Peak usage identification

### Monitoring Commands:
\`\`\`
/analytics performance
/analytics health-check
/analytics resource-usage
/analytics bottlenecks
\`\`\`

## 5. Data Visualization

### Analytics Dashboard:
Access via \`/analytics dashboard\`

**Overview Metrics:**
- Daily active users
- Message volume trends
- Command usage patterns
- Moderation action frequency

**Interactive Charts:**
- Time-series data
- Comparison graphs
- Heat maps
- Distribution charts

### Report Generation:
- Daily summaries
- Weekly reports
- Monthly analysis
- Custom date ranges

## 6. Export & Reporting

### Data Export Options:
\`\`\`
/analytics export
Format: CSV/JSON/PDF
Date Range: custom
Categories: selected
Destination: DM/Channel
\`\`\`

### Report Types:
- **Activity Reports**: User and channel activity
- **Moderation Reports**: Enforcement actions
- **Performance Reports**: Bot and server metrics
- **Compliance Reports**: Audit trail documentation

### Automated Reporting:
- Scheduled daily/weekly reports
- Alert thresholds
- Trend notifications
- Performance warnings

## 7. Privacy & Compliance

### Data Collection:
- Server metadata only
- No private message content
- Anonymized user patterns
- Configurable retention periods

### GDPR Compliance:
- Data portability
- Right to deletion
- Processing transparency
- Consent management

### Security Features:
- Encrypted data storage
- Access logging
- Role-based permissions
- Audit trail protection

### Data Retention:
\`\`\`
/analytics retention
Event Logs: 90 days
Performance Data: 30 days
Statistics: 1 year
Custom: configurable
\`\`\`

### Best Practices:

**Setup Recommendations:**
1. Configure essential event logging first
2. Set up server statistics for visibility
3. Establish reporting schedules
4. Train staff on data interpretation

**Performance Optimization:**
- Regular data cleanup
- Optimize query patterns
- Monitor resource usage
- Schedule maintenance windows

**Security Considerations:**
- Restrict analytics access
- Implement data retention policies
- Regular audit reviews
- Secure export procedures

### Troubleshooting:

**Missing Data:**
- Check logging permissions
- Verify channel configuration
- Review retention settings
- Validate event filters

**Performance Issues:**
- Optimize data queries
- Reduce logging frequency
- Archive old data
- Monitor resource usage

### Advanced Features:
- Custom metric creation
- External integrations
- API access for automation
- Machine learning insights

---
Analytics enable informed decision-making and transparent server governance.
© 2025 NexGuard. All rights reserved.`;
}

function generateRoleGuide(): string {
  return `# NexGuard Role Management Guide
Version 2.3.2 | ${new Date().toLocaleDateString()}

## Table of Contents
1. Role System Overview
2. Reaction Roles
3. Auto-Role Assignment
4. Permission Management
5. Role Hierarchies
6. Advanced Configurations
7. Best Practices

## 1. Role System Overview

NexGuard provides comprehensive role management including reaction roles, auto-assignment, and sophisticated permission handling for organized server structure.

### Key Features:
- Interactive reaction roles
- Automatic role assignment
- Permission templates
- Role hierarchies
- Bulk role operations
- Activity-based roles

### Benefits:
- Streamlined onboarding
- Self-service role selection
- Organized permissions
- Reduced admin workload
- Enhanced user experience

## 2. Reaction Roles

### Basic Setup:
\`\`\`
/reactionrole create
Message: "React to get roles!"
Emoji: 🎮
Role: @Gamer
Description: "Gaming enthusiast"
\`\`\`

### Multi-Role Messages:
Create comprehensive role selection menus:
\`\`\`
React for your interests:
🎮 - Gamer
🎵 - Music Lover  
🎨 - Artist
📚 - Book Club
💻 - Developer
\`\`\`

### Role Categories:
- **Interest Roles**: Hobbies and preferences
- **Notification Roles**: Event announcements
- **Access Roles**: Channel permissions
- **Cosmetic Roles**: Colors and badges

### Management Commands:
- \`/reactionrole list\` - View all reaction roles
- \`/reactionrole edit <id>\` - Modify existing setup
- \`/reactionrole delete <id>\` - Remove reaction role
- \`/reactionrole refresh\` - Update all panels

## 3. Auto-Role Assignment

### New Member Roles:
Automatically assign roles when users join:
\`\`\`
/autorole add @Member
/autorole add @Newcomer
/autorole verify-required @Verified
\`\`\`

### Conditional Assignment:
- **Verification Required**: Assign after verification
- **Time-Based**: Assign after duration
- **Activity-Based**: Assign after participation
- **Bot Detection**: Special handling for bots

### Configuration Options:
\`\`\`
Auto-Role Settings:
Default Role: @Member
Verification Role: @Verified
Bot Role: @Bot
Delay: 5 minutes
Requirements: account_age > 7_days
\`\`\`

## 4. Permission Management

### Permission Templates:
Pre-configured permission sets for common roles:

**Staff Template:**
- Manage Messages
- Timeout Members
- View Audit Log
- Use Slash Commands

**Moderator Template:**
- Kick Members
- Ban Members
- Manage Channels
- Manage Roles (limited)

**VIP Template:**
- Priority Speaker
- Embed Links
- Use External Emojis
- Voice Activity

### Role Creation with Permissions:
\`\`\`
/role create name:"Support Staff"
template:staff
color:#3498db
hoist:true
mentionable:true
\`\`\`

## 5. Role Hierarchies

### Hierarchy Best Practices:
1. Owner/Admin at top
2. Staff roles by seniority
3. Special roles (VIP, Nitro Boosters)
4. General member roles
5. Punishment roles at bottom

### Position Management:
\`\`\`
/role position @Role 5
/role hierarchy view
/role reorder
\`\`\`

### Inheritance Rules:
- Higher roles inherit lower permissions
- Explicit denies override inherits
- Channel overrides server permissions
- Admin permission bypasses restrictions

## 6. Advanced Configurations

### Dynamic Roles:
Roles that change based on activity:
- **Activity Roles**: Based on message count
- **Voice Roles**: Based on voice time
- **Boost Roles**: Server booster recognition
- **Anniversary Roles**: Join date milestones

### Role Rewards:
\`\`\`
/role rewards setup
Messages: 100 → @Active
Voice Time: 10h → @Chatty
Boosts: 1 → @Supporter
Days: 30 → @Veteran
\`\`\`

### Temporary Roles:
- **Event Roles**: Auto-remove after events
- **Trial Roles**: Probationary periods
- **Punishment Roles**: Timed restrictions
- **Access Roles**: Limited duration access

### Custom Role Menus:
Create interactive role selection interfaces:
\`\`\`
/role menu create
Title: "Choose Your Roles"
Description: "Select roles that interest you"
Style: dropdown
Max_Selections: 3
Categories: gaming,music,art
\`\`\`

## 7. Best Practices

### Role Organization:
- Use clear, descriptive names
- Consistent color schemes
- Logical hierarchy structure
- Regular cleanup of unused roles

### Permission Strategy:
- Principle of least privilege
- Regular permission audits
- Document role purposes
- Test permission changes

### User Experience:
- Clear role descriptions
- Easy role selection process
- Visual role indicators
- Help documentation

### Security Considerations:
- Limit dangerous permissions
- Monitor role changes
- Audit permission grants
- Secure admin roles

### Maintenance:
- Regular role cleanup
- Update descriptions
- Review permission sets
- Monitor role usage

### Common Configurations:

**Gaming Server:**
- Game-specific roles
- Platform roles (PC, Console)
- Skill level roles
- Event participation roles

**Community Server:**
- Interest-based roles
- Location roles
- Age group roles
- Contribution level roles

**Business Server:**
- Department roles
- Project team roles
- Access level roles
- Expertise area roles

### Troubleshooting:

**Roles not working:**
- Check bot permissions
- Verify role hierarchy
- Review channel overrides
- Test with role debugger

**Permission conflicts:**
- Audit role permissions
- Check channel overrides
- Review inheritance chain
- Use permission calculator

### Monitoring:
- Track role assignment patterns
- Monitor permission usage
- Analyze user behavior
- Regular security reviews

---
Effective role management creates organized, secure, and user-friendly servers.
© 2025 NexGuard. All rights reserved.`;
}

function generateCompleteGuide(): string {
  return `# NexGuard Complete Admin Guide
Version 2.3.2 | ${new Date().toLocaleDateString()}

## Table of Contents
1. Introduction & Setup
2. Command Categories Overview
3. Administrative Features
4. Moderation System
5. Ticket Management
6. AutoMod Configuration
7. Analytics & Logging
8. Role Management
9. Utility Features
10. Troubleshooting
11. Best Practices
12. Advanced Configurations

## 1. Introduction & Setup

### Welcome to NexGuard
NexGuard is a comprehensive Discord bot management system featuring 60+ commands across 8 specialized categories, designed for professional server administration.

### Initial Setup Checklist:
- [ ] Bot invitation with proper permissions
- [ ] Initial ping test (\`/ping\`)
- [ ] Admin role configuration
- [ ] Basic AutoMod setup
- [ ] First ticket panel creation
- [ ] Event logging configuration

### Essential Permissions:
Administrator permission recommended, or minimum:
- Manage Server
- Manage Channels
- Manage Roles
- Manage Messages
- Kick/Ban Members
- Create Instant Invite
- Use Slash Commands

## 2. Command Categories Overview

### Admin (8 commands):
Server configuration and management
- \`/modrole\` - Configure moderator roles
- \`/setup\` - Initial server setup
- \`/config\` - Bot configuration
- \`/permissions\` - Permission management

### Moderation (12 commands):
User moderation and punishment
- \`/timeout\`, \`/kick\`, \`/ban\` - User punishment
- \`/warn\`, \`/mute\` - Progressive discipline
- \`/modlogs\` - Moderation history
- \`/appeal\` - Appeal system

### Ticket System (15 commands):
Professional support management
- \`/ticket-panel\` - Create support panels
- \`/claim\`, \`/close\` - Ticket management
- \`/add\`, \`/remove\` - User management
- \`/transcript\` - Conversation logs

### Utility (10 commands):
General bot utilities
- \`/userinfo\`, \`/serverinfo\` - Information
- \`/avatar\`, \`/banner\` - Profile data
- \`/ping\`, \`/uptime\` - Bot status

### AutoMod (8 commands):
Automated moderation
- \`/automod-config\` - System configuration
- \`/automod-status\` - Health monitoring
- \`/automod-bypass\` - Role exemptions

### Auto-Reply (5 commands):
Automated responses
- \`/autoreply add\` - Create responses
- \`/autoreply list\` - View configurations
- \`/autoreply toggle\` - Enable/disable

### Event Logging (3 commands):
Server event tracking
- \`/eventlog setup\` - Configure logging
- \`/eventlog view\` - View logs
- \`/eventlog export\` - Data export

### Role Management (4 commands):
Role assignment and permissions
- \`/role\` - Role operations
- \`/reactionrole\` - Interactive roles
- \`/autorole\` - Automatic assignment

## 3. Administrative Features

### Server Configuration:
\`\`\`
/setup wizard
- Welcome messages
- Logging channels
- Staff roles
- Basic AutoMod
- Ticket categories
\`\`\`

### Moderator Roles:
\`\`\`
/modrole add @Moderator
/modrole add @Admin
/modrole list
/modrole remove @Role
\`\`\`

### Permission Management:
- Hierarchical role system
- Command-specific permissions
- Channel overrides
- Bypass configurations

## 4. Moderation System

### User Punishments:
\`\`\`
/timeout @user 10m Spamming
/warn @user Inappropriate language
/kick @user Repeatedly breaking rules
/ban @user 7d Serious violation
\`\`\`

### Moderation Logging:
- Automatic action logging
- Reason requirements
- Evidence attachment
- Appeal integration

### Progressive Discipline:
1. Verbal warning
2. Formal warning (\`/warn\`)
3. Temporary timeout
4. Temporary ban
5. Permanent ban

## 5. Ticket Management

### Panel Creation:
\`\`\`
/ticket-panel action:create
title:"General Support"
description:"Click for help"
category:"Support Tickets"
emoji:🎫
\`\`\`

### Ticket Operations:
- \`/claim\` - Assign to staff
- \`/add @user\` - Include additional users
- \`/close\` - Close with transcript
- \`/rename new-name\` - Rename channel

### Categories:
- General support
- Bug reports
- Ban appeals
- Staff applications
- Custom categories

## 6. AutoMod Configuration

### Spam Protection:
\`\`\`
/automod-config spam
max_messages: 5
time_window: 10s
action: timeout
duration: 5m
\`\`\`

### Content Filtering:
- Bad word detection
- Link filtering
- Caps lock limits
- Mention spam protection

### Bypass System:
\`\`\`
/automod-bypass add @Staff
/automod-bypass add @VIP
/automod-bypass list
\`\`\`

## 7. Analytics & Logging

### Server Statistics:
\`\`\`
/serverstats add member_count
/serverstats add channel_count
/serverstats add boost_count
\`\`\`

### Event Logging:
\`\`\`
/eventlog setup
channel: #audit-logs
events: all
format: detailed
\`\`\`

### Analytics Dashboard:
- User activity trends
- Command usage statistics
- Moderation insights
- Performance metrics

## 8. Role Management

### Reaction Roles:
\`\`\`
/reactionrole create
message: "React for roles!"
emoji: 🎮
role: @Gamer
\`\`\`

### Auto-Roles:
\`\`\`
/autorole add @Member
/autorole verification @Verified
/autorole bot @Bot
\`\`\`

### Role Hierarchies:
- Proper permission ordering
- Inheritance rules
- Security considerations

## 9. Utility Features

### Information Commands:
- \`/userinfo @user\` - User details
- \`/serverinfo\` - Server information
- \`/botinfo\` - Bot statistics
- \`/channelinfo #channel\` - Channel data

### System Monitoring:
- \`/ping\` - Response time
- \`/uptime\` - Online duration
- \`/health\` - System status

## 10. Troubleshooting

### Common Issues:

**Bot not responding:**
- Check permissions
- Verify bot online status
- Review role hierarchy
- Test with \`/ping\`

**Commands not working:**
- Check slash command permissions
- Verify bot can send messages
- Review channel permissions

**AutoMod false positives:**
- Adjust sensitivity settings
- Add bypass roles
- Review filter lists

### Diagnostic Commands:
- \`/debug permissions\`
- \`/debug config\`
- \`/debug automod\`
- \`/debug tickets\`

## 11. Best Practices

### Security:
- Regular permission audits
- Secure admin role management
- Monitor bot logs
- Update configurations regularly

### Performance:
- Regular database cleanup
- Monitor resource usage
- Optimize AutoMod settings
- Archive old tickets

### User Experience:
- Clear command documentation
- Helpful error messages
- Intuitive role systems
- Responsive support

### Documentation:
- Document custom configurations
- Maintain staff procedures
- Regular training updates
- Clear escalation paths

## 12. Advanced Configurations

### Webhook Integration:
- External system notifications
- Custom automation triggers
- Third-party integrations

### API Access:
- Custom dashboard development
- External data integration
- Automated reporting systems

### Enterprise Features:
- Multi-server management
- Centralized logging
- Advanced analytics
- Custom branding

### Backup & Recovery:
- Configuration backups
- Data export procedures
- Disaster recovery plans
- Migration assistance

---

## Support & Resources

### Getting Help:
- Support Server: https://discord.gg/wpjZMPXaRT
- Documentation: https://nexguard.org/docs
- Feature Requests: Support server feedback
- Bug Reports: Create ticket for technical issues

### Stay Updated:
- Follow announcement channels
- Review changelog regularly
- Test new features in development server
- Participate in beta programs

---
© 2025 NexGuard. Comprehensive Discord server management solution.
All rights reserved.`;
}

function generateDefaultGuide(title: string, description: string): string {
  return `# ${title}
Version 2.3.2 | ${new Date().toLocaleDateString()}

## Overview
${description}

This comprehensive guide covers all aspects of ${title.toLowerCase()} in NexGuard Discord Bot.

## Features
- Professional Discord server management
- 60+ specialized commands
- Enterprise-level functionality
- Real-time monitoring and analytics
- Comprehensive moderation tools
- Professional ticket system

## Getting Started
1. Ensure bot has proper permissions
2. Run initial setup commands
3. Configure essential features
4. Test functionality
5. Train staff on procedures

## Support
For detailed assistance, join our support server at https://discord.gg/wpjZMPXaRT

---
© 2025 NexGuard. All rights reserved.`;
}

export function registerRoutes(app: Express): Server {
  // News endpoints
  app.get("/api/news", async (req, res) => {
    try {
      const news = await storage.getNews();
      res.json(news);
    } catch (error) {
      console.error("Error fetching news:", error);
      res.status(500).json({ error: "Failed to fetch news" });
    }
  });

  // Developers endpoints
  app.get("/api/developers", async (req, res) => {
    try {
      const developers = await storage.getDevelopers();
      res.json(developers);
    } catch (error) {
      console.error("Error fetching developers:", error);
      res.status(500).json({ error: "Failed to fetch developers" });
    }
  });

  // Features endpoints
  app.get("/api/features", async (req, res) => {
    try {
      const features = await storage.getFeatures();
      res.json(features);
    } catch (error) {
      console.error("Error fetching features:", error);
      res.status(500).json({ error: "Failed to fetch features" });
    }
  });

  // Testimonials endpoints
  app.get("/api/testimonials", async (req, res) => {
    try {
      const testimonials = await storage.getTestimonials();
      res.json(testimonials);
    } catch (error) {
      console.error("Error fetching testimonials:", error);
      res.status(500).json({ error: "Failed to fetch testimonials" });
    }
  });

  app.post("/api/testimonials", async (req, res) => {
    try {
      const result = insertTestimonialSchema.safeParse(req.body);
      if (!result.success) {
        return res.status(400).json({ error: "Invalid testimonial data" });
      }
      
      const testimonial = await storage.createTestimonial(result.data);
      
      // Send email notification for new testimonial with approval links
      try {
        await emailService.sendTestimonialNotification({
          id: testimonial.id,
          name: testimonial.username,
          serverName: testimonial.serverName,
          rating: testimonial.rating,
          message: testimonial.content,
          approvalLink: `${process.env.REPL_SLUG ? `https://${process.env.REPL_SLUG}.${process.env.REPL_OWNER?.toLowerCase()}.repl.co` : 'http://localhost:5000'}/api/testimonials/approve/${testimonial.id}`,
          rejectLink: `${process.env.REPL_SLUG ? `https://${process.env.REPL_SLUG}.${process.env.REPL_OWNER?.toLowerCase()}.repl.co` : 'http://localhost:5000'}/api/testimonials/reject/${testimonial.id}`
        });
        console.log(`📧 Email notification sent for testimonial from ${testimonial.username} (ID: ${testimonial.id})`);
      } catch (emailError) {
        console.error('Failed to send testimonial email notification:', emailError);
        // Don't fail the request if email fails
      }
      
      res.json({ message: "Testimonial submitted for approval", id: testimonial.id });
    } catch (error) {
      console.error("Error creating testimonial:", error);
      res.status(500).json({ error: "Failed to create testimonial" });
    }
  });

  // Testimonial approval endpoints
  app.get("/api/testimonials/approve/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      if (isNaN(id)) {
        return res.status(400).json({ error: "Invalid testimonial ID" });
      }
      
      const testimonial = await storage.approveTestimonial(id);
      if (!testimonial) {
        return res.status(404).json({ error: "Testimonial not found" });
      }
      
      res.send(`
        <html>
          <head><title>Testimonial Approved</title></head>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px;">
            <div style="text-align: center; background: linear-gradient(135deg, #06b6d4, #8b5cf6); color: white; padding: 20px; border-radius: 10px;">
              <h1>✅ Testimonial Approved!</h1>
              <p>The testimonial from <strong>${testimonial.username}</strong> has been approved and is now live on the NexGuard website.</p>
              <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Server:</strong> ${testimonial.serverName}</p>
                <p><strong>Rating:</strong> ${'⭐'.repeat(testimonial.rating)}</p>
                <p><strong>Message:</strong> "${testimonial.content}"</p>
              </div>
              <a href="/" style="display: inline-block; background: white; color: #06b6d4; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px;">View Website</a>
            </div>
          </body>
        </html>
      `);
    } catch (error) {
      console.error("Error approving testimonial:", error);
      res.status(500).json({ error: "Failed to approve testimonial" });
    }
  });

  app.get("/api/testimonials/reject/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      if (isNaN(id)) {
        return res.status(400).json({ error: "Invalid testimonial ID" });
      }
      
      const success = await storage.rejectTestimonial(id);
      if (!success) {
        return res.status(404).json({ error: "Testimonial not found" });
      }
      
      res.send(`
        <html>
          <head><title>Testimonial Rejected</title></head>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px;">
            <div style="text-align: center; background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 20px; border-radius: 10px;">
              <h1>❌ Testimonial Rejected</h1>
              <p>The testimonial has been rejected and removed from the system.</p>
              <a href="/" style="display: inline-block; background: white; color: #ef4444; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px;">Return to Website</a>
            </div>
          </body>
        </html>
      `);
    } catch (error) {
      console.error("Error rejecting testimonial:", error);
      res.status(500).json({ error: "Failed to reject testimonial" });
    }
  });

  // Feedback endpoints
  app.get("/api/feedback", async (req, res) => {
    try {
      const feedback = await storage.getFeedback();
      res.json(feedback);
    } catch (error) {
      console.error("Error fetching feedback:", error);
      res.status(500).json({ error: "Failed to fetch feedback" });
    }
  });

  app.post("/api/feedback", async (req, res) => {
    try {
      const result = insertFeedbackSchema.safeParse(req.body);
      if (!result.success) {
        return res.status(400).json({ error: "Invalid feedback data" });
      }
      
      // Store feedback locally
      const feedback = await storage.createFeedback(result.data);
      
      // Send email notification for new feedback
      try {
        await emailService.sendFeedbackNotification({
          name: feedback.username,
          email: feedback.email || undefined,
          type: feedback.type,
          message: feedback.message
        });
        console.log(`📧 Email notification sent for feedback from ${feedback.username}`);
      } catch (emailError) {
        console.error('Failed to send feedback email notification:', emailError);
        // Don't fail the request if email fails
      }
      
      // Send feedback to NexGuard website
      const feedbackData = {
        id: feedback.id,
        username: feedback.username,
        email: feedback.email,
        subject: feedback.subject,
        message: feedback.message,
        type: feedback.type,
        status: feedback.status,
        submittedAt: feedback.createdAt,
        source: "website",
        userAgent: req.headers['user-agent'] || 'Unknown',
        timestamp: new Date().toISOString()
      };

      // Send to NexGuard central website (with error handling)
      let externalSubmissionStatus = "pending";
      try {
        // Create AbortController for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

        const nexguardResponse = await fetch('https://nexguard.org/api/feedback/submit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${process.env.NEXGUARD_API_KEY || 'dev-key'}`,
            'User-Agent': 'NexGuard-Bot-Website/2.3.2',
            'X-Source': 'discord-bot-website',
            'X-Bot-Version': '2.3.2'
          },
          body: JSON.stringify(feedbackData),
          signal: controller.signal
        } as any);

        clearTimeout(timeoutId);

        if (nexguardResponse.ok) {
          const nexguardResult = await nexguardResponse.json() as any;
          externalSubmissionStatus = "submitted";
          console.log(`✅ Feedback #${feedback.id} forwarded to NexGuard website:`, nexguardResult.id || 'success');
        } else {
          console.warn(`⚠️  Failed to forward feedback #${feedback.id} to NexGuard website:`, nexguardResponse.status);
          externalSubmissionStatus = "failed";
        }
      } catch (externalError: any) {
        console.warn(`⚠️  Network error forwarding feedback #${feedback.id} to NexGuard website:`, externalError.message);
        externalSubmissionStatus = "failed";
      }

      // Return success with submission status
      res.json({
        ...feedback,
        externalSubmissionStatus,
        message: externalSubmissionStatus === "submitted" 
          ? "Feedback submitted successfully to NexGuard website" 
          : "Feedback saved locally. External submission pending."
      });
    } catch (error) {
      console.error("Error creating feedback:", error);
      res.status(500).json({ error: "Failed to create feedback" });
    }
  });

  // Health check endpoints
  app.get("/health", (req, res) => {
    res.json({ status: "ok", timestamp: new Date().toISOString() });
  });

  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", timestamp: new Date().toISOString() });
  });

  // Configuration endpoint for frontend
  app.get("/api/config", (req, res) => {
    res.json({
      platform: "discord",
      status: "active",
      version: "2.3.2",
      discordInviteUrl: "https://discord.com/oauth2/authorize?client_id=1389775821794705429&permissions=8&scope=bot%20applications.commands",
      supportServerUrl: "https://discord.gg/wpjZMPXaRT"
    });
  });

  // Bot status endpoints
  app.get("/api/bot/status", async (req, res) => {
    try {
      const status = await storage.getBotStatus();
      res.json(status);
    } catch (error) {
      console.error("Error fetching bot status:", error);
      res.status(500).json({ error: "Failed to fetch bot status" });
    }
  });

  // Webhook endpoint for sending messages through the bot
  app.post("/webhook/send", async (req, res) => {
    try {
      const { channel_id, content, embed, api_key } = req.body;

      // Simple API key check (you can set WEBHOOK_API_KEY in your environment)
      const validApiKey = process.env.WEBHOOK_API_KEY || "nexguard-fun-webhook";
      if (!api_key || api_key !== validApiKey) {
        return res.status(401).json({ error: "Invalid API key", hint: "Set api_key parameter" });
      }

      if (!channel_id) {
        return res.status(400).json({ error: "channel_id is required" });
      }

      if (!content && !embed) {
        return res.status(400).json({ error: "Either content or embed is required" });
      }

      // Send message data to bot
      const messageData = {
        channel_id: channel_id,
        content: content,
        embed: embed
      };

      try {
        // Send to bot's internal webhook server
        const botResponse = await fetch('http://localhost:5001/api/bot/send-message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(messageData)
        });

        if (botResponse.ok) {
          const result = await botResponse.json();
          res.json({
            success: true,
            message: "Message sent successfully",
            data: result
          });
        } else {
          const error = await botResponse.text();
          res.status(500).json({
            error: "Bot delivery failed",
            details: error,
            message: "The webhook endpoint received your request but the bot couldn't deliver it"
          });
        }
      } catch (botError: any) {
        // Bot might not be running, return a helpful message
        console.log("🎭 Webhook message request (bot offline):", messageData);
        res.json({
          success: false,
          message: "Message received but bot is offline",
          preview: content || embed?.description || "Embed message",
          note: "Your message was processed but couldn't be delivered because NexGuard bot is not currently running"
        });
      }

    } catch (error) {
      console.error("Webhook error:", error);
      res.status(500).json({ error: "Internal server error" });
    }
  });

  app.get("/api/bot/commands", async (req, res) => {
    try {
      const commands = await storage.getCommands();
      res.json(commands);
    } catch (error) {
      console.error("Error fetching commands:", error);
      res.status(500).json({ error: "Failed to fetch commands" });
    }
  });

  app.get("/api/bot/changelog", async (req, res) => {
    try {
      const changelog = await storage.getChangelogs();
      res.json(changelog);
    } catch (error) {
      console.error("Error fetching changelog:", error);
      res.status(500).json({ error: "Failed to fetch changelog" });
    }
  });

  app.get("/api/bot/tickets", async (req, res) => {
    try {
      const tickets = await storage.getTickets();
      res.json(tickets);
    } catch (error) {
      console.error("Error fetching tickets:", error);
      res.status(500).json({ error: "Failed to fetch tickets" });
    }
  });

  app.get("/api/bot/moderation", async (req, res) => {
    try {
      const logs = await storage.getModerationLogs();
      res.json(logs);
    } catch (error) {
      console.error("Error fetching moderation logs:", error);
      res.status(500).json({ error: "Failed to fetch moderation logs" });
    }
  });

  // Analytics endpoints
  app.get("/api/analytics/overview", async (req, res) => {
    try {
      const analytics = await storage.getAnalyticsOverview();
      res.json(analytics);
    } catch (error) {
      console.error("Error fetching analytics overview:", error);
      res.status(500).json({ error: "Failed to fetch analytics overview" });
    }
  });

  app.get("/api/analytics/server/:guildId", async (req, res) => {
    try {
      const { guildId } = req.params;
      const { timeRange = "24h" } = req.query;
      const analytics = await storage.getServerAnalytics(guildId, timeRange as string);
      res.json(analytics);
    } catch (error) {
      console.error("Error fetching server analytics:", error);
      res.status(500).json({ error: "Failed to fetch server analytics" });
    }
  });

  app.get("/api/analytics/messages/:guildId", async (req, res) => {
    try {
      const { guildId } = req.params;
      const { timeRange = "24h" } = req.query;
      const analytics = await storage.getMessageAnalytics(guildId, timeRange as string);
      res.json(analytics);
    } catch (error) {
      console.error("Error fetching message analytics:", error);
      res.status(500).json({ error: "Failed to fetch message analytics" });
    }
  });

  app.get("/api/analytics/commands/:guildId", async (req, res) => {
    try {
      const { guildId } = req.params;
      const { timeRange = "24h" } = req.query;
      const analytics = await storage.getCommandAnalytics(guildId, timeRange as string);
      res.json(analytics);
    } catch (error) {
      console.error("Error fetching command analytics:", error);
      res.status(500).json({ error: "Failed to fetch command analytics" });
    }
  });

  app.get("/api/analytics/users/:guildId", async (req, res) => {
    try {
      const { guildId } = req.params;
      const analytics = await storage.getUserActivity(guildId);
      res.json(analytics);
    } catch (error) {
      console.error("Error fetching user activity:", error);
      res.status(500).json({ error: "Failed to fetch user activity" });
    }
  });

  app.get("/api/analytics/channels/:guildId", async (req, res) => {
    try {
      const { guildId } = req.params;
      const analytics = await storage.getChannelAnalytics(guildId);
      res.json(analytics);
    } catch (error) {
      console.error("Error fetching channel analytics:", error);
      res.status(500).json({ error: "Failed to fetch channel analytics" });
    }
  });

  // Guide download endpoints
  app.get("/api/guides/download/:guideType", async (req, res) => {
    try {
      const { guideType } = req.params;
      
      // Define available guides with their metadata
      const guides = {
        quickstart: {
          filename: "NexGuard_Quick_Start_Guide.pdf",
          title: "NexGuard Quick Start Guide",
          description: "Essential setup steps for new users"
        },
        automod: {
          filename: "NexGuard_AutoMod_Setup_Guide.pdf", 
          title: "AutoMod Setup Guide",
          description: "Configure advanced automated moderation"
        },
        tickets: {
          filename: "NexGuard_Ticket_System_Guide.pdf",
          title: "Ticket System Guide", 
          description: "Professional support ticket configuration"
        },
        analytics: {
          filename: "NexGuard_Analytics_Logging_Guide.pdf",
          title: "Analytics & Logging Guide",
          description: "Server statistics and event logging setup"
        },
        roles: {
          filename: "NexGuard_Role_Management_Guide.pdf",
          title: "Role Management Guide",
          description: "Configure reaction roles and permissions"
        },
        complete: {
          filename: "NexGuard_Complete_Admin_Guide.pdf",
          title: "Complete Admin Guide",
          description: "Comprehensive guide covering all features"
        }
      };

      const guide = guides[guideType as keyof typeof guides];
      if (!guide) {
        return res.status(404).json({ error: "Guide not found" });
      }

      // Create comprehensive guide content based on guide type
      let content = '';
      
      try {
        switch (guide.title) {
          case "NexGuard Quick Start Guide":
            content = generateQuickStartGuide();
            break;
          case "AutoMod Setup Guide":
            content = generateAutoModGuide();
            break;
          case "Ticket System Guide":
            content = generateTicketGuide();
            break;
          case "Analytics & Logging Guide":
            content = generateAnalyticsGuide();
            break;
          case "Role Management Guide":
            content = generateRoleGuide();
            break;
          case "Complete Admin Guide":
            content = generateCompleteGuide();
            break;
          default:
            content = generateDefaultGuide(guide.title, guide.description);
        }
      } catch (error) {
        console.error("Error generating guide content:", error);
        content = `# ${guide.title}\n\nError generating guide content. Please try again later.`;
      }

      // Generate PDF with comprehensive content
      const doc = new PDFDocument({ margin: 50 });
      const chunks: Buffer[] = [];

      doc.on('data', (chunk) => chunks.push(chunk));
      doc.on('end', () => {
        const result = Buffer.concat(chunks);
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', `attachment; filename="${guide.filename}"`);
        res.send(result);
      });

      // Add title
      doc.fontSize(22).fillColor('#00CED1').text(guide.title, { align: 'center' });
      doc.moveDown();

      // Parse and add content
      const lines = content.split('\n');
      for (const line of lines) {
        // Check if we need a new page
        if (doc.y > doc.page.height - 80) {
          doc.addPage();
        }

        if (line.startsWith('# ')) {
          // Skip main title as we already added it
          continue;
        } else if (line.startsWith('## ')) {
          // Section headers
          doc.moveDown(0.5);
          doc.fontSize(16).fillColor('#2D3748').text(line.substring(3));
          doc.moveDown(0.3);
        } else if (line.startsWith('### ')) {
          // Subsection headers
          doc.moveDown(0.3);
          doc.fontSize(14).fillColor('#4A5568').text(line.substring(4));
          doc.moveDown(0.2);
        } else if (line.startsWith('- ') || line.startsWith('* ')) {
          // Bullet points
          doc.fontSize(11).fillColor('#4A5568').text('• ' + line.substring(2), { 
            indent: 20,
            paragraphGap: 3
          });
        } else if (line.startsWith('```')) {
          // Skip code block markers and add some spacing
          doc.moveDown(0.3);
        } else if (line.trim() && !line.startsWith('#') && !line.includes('```')) {
          // Regular text
          doc.fontSize(11).fillColor('#4A5568').text(line, {
            paragraphGap: 2
          });
        } else if (line.trim() === '') {
          // Empty lines
          doc.moveDown(0.2);
        }
      }

      // Add footer
      const pageRange = doc.bufferedPageRange();
      for (let i = pageRange.start; i < pageRange.start + pageRange.count; i++) {
        doc.switchToPage(i);
        doc.fontSize(8).fillColor('#A0AEC0').text(
          `© 2025 NexGuard - Page ${i - pageRange.start + 1} of ${pageRange.count}`,
          50,
          doc.page.height - 30,
          { align: 'center' }
        );
      }

      doc.end();
      
    } catch (error) {
      console.error("Error serving guide:", error);
      res.status(500).json({ error: "Failed to serve guide" });
    }
  });

  app.get("/api/guides/download/templates/:templateType", async (req, res) => {
    try {
      const { templateType } = req.params;
      
      const templates = {
        autoreply: {
          filename: "autoreply_templates.json",
          content: {
            version: "2.3.2",
            description: "AutoReply templates for common Discord server responses",
            templates: [
              {
                id: "welcome",
                name: "Welcome Message Template",
                trigger: "welcome",
                response: "Welcome to {guild.name}, {user.mention}! Please read our rules in #rules channel.",
                enabled: true
              },
              {
                id: "faq_help",
                name: "FAQ Help Response", 
                trigger: "how to get help",
                response: "For support, please create a ticket using `/ticket create` or check our FAQ at https://nexguard.org/faq",
                enabled: true
              },
              {
                id: "rules_reminder",
                name: "Rules Reminder",
                trigger: "rules",
                response: "Please remember to follow our server rules. You can view them in #rules channel.",
                enabled: true
              }
            ]
          }
        },
        automod: {
          filename: "automod_config_templates.json",
          content: {
            version: "2.3.2", 
            description: "AutoMod configuration templates for different server types",
            configs: [
              {
                id: "gaming_server",
                name: "Gaming Server Configuration",
                settings: {
                  spam_protection: {
                    enabled: true,
                    max_messages: 5,
                    time_window: 10,
                    punishment: "timeout"
                  },
                  bad_words: {
                    enabled: true,
                    action: "delete",
                    notify_mods: true
                  },
                  caps_limit: {
                    enabled: true,
                    percentage: 70,
                    action: "warn"
                  }
                }
              },
              {
                id: "professional_server", 
                name: "Professional/Business Server",
                settings: {
                  spam_protection: {
                    enabled: true,
                    max_messages: 3,
                    time_window: 15,
                    punishment: "timeout"
                  },
                  link_filtering: {
                    enabled: true,
                    whitelist_only: true,
                    allowed_domains: ["company.com", "linkedin.com"]
                  },
                  profanity_filter: {
                    enabled: true,
                    strictness: "high",
                    action: "delete_and_warn"
                  }
                }
              }
            ]
          }
        }
      };

      const template = templates[templateType as keyof typeof templates];
      if (!template) {
        return res.status(404).json({ error: "Template not found" });
      }

      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Content-Disposition', `attachment; filename="${template.filename}"`);
      
      res.json(template.content);
      
    } catch (error) {
      console.error("Error serving template:", error);
      res.status(500).json({ error: "Failed to serve template" });
    }
  });

  // Health check
  app.get("/health", (req, res) => {
    res.json({ status: "ok", timestamp: new Date().toISOString() });
  });

  const httpServer = createServer(app);
  return httpServer;
}