# Complete Guide to NexGuard Ticket Panels

## Overview

NexGuard's ticket system provides comprehensive support management with permanent interactive panels, customizable categories, and professional staff workflows. This guide covers everything you need to know about creating and managing ticket panels.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Your First Panel](#creating-your-first-panel)
3. [Panel Configuration](#panel-configuration)
4. [Managing Panels](#managing-panels)
5. [Ticket Management](#ticket-management)
6. [Advanced Features](#advanced-features)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites
- NexGuard bot must be added to your server with appropriate permissions
- Administrator or staff role with manage channels/messages permissions
- A dedicated category for tickets (recommended)

### Basic Concepts
- **Ticket Panel**: An interactive embed with buttons that users click to create tickets
- **Support Categories**: Different types of support (general, billing, technical, etc.)
- **Staff Assignment**: Specific roles or users assigned to handle tickets
- **Permanent Views**: Panels persist through bot restarts

---

## Creating Your First Panel

### Step 1: Create a Ticket Panel

Use the `/ticket-panel` command to start creating your panel:

```
/ticket-panel create panel_id:support title:General Support
```

**Parameters:**
- `panel_id`: Unique identifier (letters, numbers, hyphens only)
- `title`: Display name for your panel
- `category_id`: (Optional) Category where tickets will be created
- `support_team_ids`: (Optional) Roles that can manage these tickets

### Step 2: Configure Panel Appearance

Customize your panel with embed options:

```
/ticket-panel edit panel_id:support 
  panel_embed_title:🎫 Support Center
  panel_embed_description:Click the button below to create a support ticket
  ticket_embed_title:Support Ticket Created
```

### Step 3: Deploy the Panel

Deploy your configured panel to a channel:

```
/ticket-panel deploy panel_id:support channel:#support
```

---

## Panel Configuration

### Basic Settings

| Setting | Description | Example |
|---------|-------------|---------|
| `panel_id` | Unique identifier | `general-support` |
| `title` | Panel display name | `General Support` |
| `category_id` | Target category ID | `123456789012345678` |
| `support_team_ids` | Staff role IDs | `987654321098765432,876543210987654321` |

### Embed Customization

#### Panel Embed (What users see)
```
panel_embed_header: Header text above the panel
panel_embed_title: Main title of the panel
panel_embed_description: Instructions for users
```

#### Ticket Embed (Created when ticket opens)
```
ticket_embed_header: Header for new tickets
ticket_embed_title: Title for ticket notifications
ticket_embed_description: Welcome message for ticket creators
```

### Example Complete Configuration

```
/ticket-panel edit panel_id:billing
  title:Billing Support
  category_id:123456789012345678
  support_team_ids:987654321098765432
  panel_embed_header:💰 BILLING DEPARTMENT
  panel_embed_title:Billing & Payment Support
  panel_embed_description:Having issues with payments, subscriptions, or billing? Click below to get help from our billing team.
  ticket_embed_header:💰 Billing Support Ticket
  ticket_embed_title:Billing Team Notified
  ticket_embed_description:Our billing specialists will assist you shortly. Please provide your account details and describe your issue.
```

---

## Managing Panels

### List All Panels
```
/ticket-panel list
```
Shows all panels in your server with their configuration.

### Edit Existing Panels
```
/ticket-panel edit panel_id:support title:Updated Support
```
Modify any panel setting without affecting deployed panels.

### Delete Panels
```
/ticket-panel delete panel_id:old-panel
```
Permanently removes a panel configuration.

### Check Panel Information
```
/ticket-info panel_id:support
```
View detailed configuration for a specific panel.

---

## Ticket Management

### User Commands

#### Creating Tickets
Users click the panel button or use:
```
/ticket create category:support message:I need help with...
```

#### Managing Their Tickets
```
/close-request          # Request ticket closure
/rename new-name         # Rename their ticket channel
```

### Staff Commands

#### Ticket Control
```
/close                   # Close any ticket
/claim                   # Claim ticket for yourself
/add @user              # Add user to ticket
/rename new-name        # Rename ticket channel
```

#### Information Commands
```
/ticket-list            # List all active tickets
/ticket-logs            # View ticket history
```

---

## Advanced Features

### Multiple Panel Types

Create specialized panels for different support areas:

#### Technical Support Panel
```
/ticket-panel create panel_id:technical title:Technical Support
  category_id:tech-category-id
  support_team_ids:tech-role-id
  panel_embed_title:🔧 Technical Support
  panel_embed_description:Experiencing technical issues? Our developers can help.
```

#### Billing Support Panel
```
/ticket-panel create panel_id:billing title:Billing Support
  category_id:billing-category-id
  support_team_ids:billing-role-id
  panel_embed_title:💰 Billing Support
  panel_embed_description:Questions about payments or subscriptions? Contact our billing team.
```

#### General Inquiries Panel
```
/ticket-panel create panel_id:general title:General Inquiries
  category_id:general-category-id
  support_team_ids:staff-role-id
  panel_embed_title:💬 General Support
  panel_embed_description:Have a question or need assistance? We're here to help.
```

### Channel Naming Convention

Tickets automatically use the format: `{panel_id}-{username}`

Examples:
- `support-john` (from support panel)
- `billing-sarah` (from billing panel)
- `technical-mike` (from technical panel)

### Permission System

#### Staff Permissions
- Users with `Manage Messages` permission
- Users with designated support roles
- Can use all ticket management commands

#### User Permissions
- Ticket creators can rename their own tickets
- Anyone in a ticket can request closure
- Cannot claim or force-close tickets

---

## Best Practices

### Server Setup

1. **Create Dedicated Categories**
   - One category per ticket type
   - Clear naming convention
   - Proper permission setup

2. **Role Configuration**
   - Separate roles for different support teams
   - Clear role hierarchy
   - Appropriate permissions

3. **Channel Organization**
   - Dedicated panel deployment channels
   - Archive categories for closed tickets
   - Staff-only management channels

### Panel Design

1. **Clear Descriptions**
   - Explain what each panel is for
   - Include expected response times
   - Set user expectations

2. **Visual Consistency**
   - Use consistent embed colors
   - Maintain branding standards
   - Clear call-to-action buttons

3. **Logical Categorization**
   - Don't create too many panel types
   - Make categories obviously different
   - Consider user journey

### Operational Guidelines

1. **Staff Training**
   - Ensure staff know all commands
   - Establish response time standards
   - Create escalation procedures

2. **Regular Maintenance**
   - Monitor panel performance
   - Update descriptions as needed
   - Clean up old configurations

3. **Performance Monitoring**
   - Track ticket volume
   - Monitor response times
   - Gather user feedback

---

## Troubleshooting

### Common Issues

#### Panel Not Responding
**Problem**: Users click button but nothing happens
**Solutions**:
- Check bot permissions in target category
- Verify category_id is correct
- Ensure bot can create channels
- Restart panel deployment

#### Commands Not Working in Tickets
**Problem**: `/close-request` or other commands fail
**Solutions**:
- Verify channel follows naming convention
- Check for NexGuard control buttons in channel
- Ensure proper ticket channel detection
- Use `/ticket-info` to verify ticket status

#### Permissions Issues
**Problem**: Staff can't manage tickets
**Solutions**:
- Verify support role assignments
- Check `support_team_ids` configuration
- Ensure roles have proper permissions
- Test with `/ticket-list` command

#### Panel Disappeared After Restart
**Problem**: Panel buttons stop working after bot restart
**Solutions**:
- NexGuard automatically restores panels
- Check logs for restoration messages
- Redeploy panel if needed
- Verify panel configuration with `/ticket-panel list`

### Error Messages

#### "This command can only be used in ticket channels"
- Channel name doesn't match ticket format
- Missing NexGuard control buttons
- Check channel topic for ticket keywords
- Use proper ticket channel naming

#### "You don't have permission to use this command"
- User lacks required role
- Not in designated support team
- Check `support_team_ids` configuration
- Verify role assignments

#### "Panel not found"
- Incorrect `panel_id` 
- Panel was deleted
- Check spelling and use `/ticket-panel list`

### Support Resources

For additional help:
1. Use `/help <command>` for specific command details
2. Contact NexGuard support team
3. Check bot status and permissions
4. Review server audit logs for permission issues

---

## Command Reference

### Panel Management
| Command | Description |
|---------|-------------|
| `/ticket-panel create` | Create new ticket panel |
| `/ticket-panel edit` | Modify panel configuration |
| `/ticket-panel deploy` | Deploy panel to channel |
| `/ticket-panel list` | List all panels |
| `/ticket-panel delete` | Remove panel configuration |

### Ticket Management
| Command | Description |
|---------|-------------|
| `/ticket-info` | View ticket/panel information |
| `/ticket-list` | List active tickets |
| `/ticket-logs` | View ticket history |
| `/close` | Close ticket (staff) |
| `/close-request` | Request closure (users) |
| `/claim` | Claim ticket (staff) |
| `/add` | Add user to ticket |
| `/rename` | Rename ticket channel |

---

**NexGuard Ticket System v2.3.2**  
*Complete enterprise-level ticket management for Discord communities*