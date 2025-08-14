# NexGuard Update: New Ticket Rename Command

**NEW FEATURE: /rename Command for Tickets**

We've added a new `/rename` command that allows you to rename ticket channels for better organization and clarity.

**Who Can Use It:**
- Staff members (with appropriate permissions)
- Ticket creators (can rename their own tickets)

**How It Works:**
- Use `/rename new-name` in any ticket channel
- The command preserves ticket prefixes (support-oldname becomes support-newname)
- Only allows valid characters (letters, numbers, hyphens)
- Prevents duplicate channel names

**Benefits:**
- Better ticket organization
- Clearer channel naming for complex issues
- Flexible management for both staff and users
- Professional logging of all rename actions

**Examples:**
- `/rename urgent-billing` - Renames to support-urgent-billing
- `/rename john-smith` - Changes user name in ticket
- `/rename resolved-issue` - Marks ticket status in name

**Technical Details:**
- Enhanced channel detection ensures the command works in all valid ticket channels
- Smart permission system prevents unauthorized access
- Automatic format preservation maintains consistency
- Complete audit trail for all rename operations

This brings our total command count to **56 commands** across our comprehensive ticket management system.

**Questions?** Contact our support team or use the existing ticket system for assistance.

---
*NexGuard Development Team*