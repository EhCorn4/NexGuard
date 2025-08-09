# NexGuard Bot Changelog

## Version 2.3.0 - August 1, 2025

### Ticket System Major Fixes

#### 🔧 Fixed: Ticket Panel Edit Functionality
- **Issue**: `/ticket-panel action:edit` was returning "invalid action" error
- **Root Cause**: Missing edit action handler in ticket panel command processing
- **Solution**: Implemented complete panel editing system with selective field updates
- **Impact**: All ticket panel management actions now fully operational (create, edit, deploy, list, delete)

#### 🔧 Fixed: Ticket Control Button Persistence
- **Issue**: Close and claim buttons stopped working after bot restarts
- **Root Cause**: All ticket channels shared a single `TicketControlView` instance causing interaction conflicts
- **Solution**: Each ticket channel now gets its own control view instance with proper restoration on startup
- **Impact**: Buttons remain functional across bot restarts, enhanced reliability

#### 🔧 Enhanced: Ticket Close Permissions
- **Issue**: Only users with "Manage Messages" permission could close tickets
- **Root Cause**: Overly restrictive permission checks preventing ticket creators from closing their own tickets
- **Solution**: Removed permission restrictions for close functionality while maintaining staff-only claiming
- **Impact**: Anyone in a ticket channel can now close it using either the close button or `/close` command

### Technical Improvements

#### Database & Persistence
- Enhanced ticket channel detection to support custom panel names beyond hardcoded prefixes
- Added intelligent fallback detection using NexGuard control button custom IDs
- Improved view restoration system scanning for channels with `nexguard_close_ticket` and `nexguard_claim_ticket` buttons
- Individual control view instances prevent interaction timeouts and conflicts

#### Command Processing
- Selective field updates for panel editing - only changes specified parameters
- Existing values preserved for unspecified fields during edits
- Proper validation ensures panels exist before allowing edits
- Clear confirmation messages show what was updated

#### User Experience
- Transcript generation and automatic delivery to all ticket participants
- Customizable deletion delays (0-300 seconds) for ticket closure
- Support for placeholder variables in ticket embeds (`{user.mention}`, `{user.name}`, `{guild.name}`, `\n`)
- Universal newline support across all embed systems

### System Status
- **Bot Status**: Online across 12 guilds protecting 252 users
- **Commands**: 55 commands fully operational
- **Ticket Panels**: 19 permanent views restored across 3 guilds
- **Control Views**: Individual restoration system ensuring button functionality
- **Reliability**: Enterprise-level stability achieved

### Breaking Changes
None - all changes are backward compatible with existing ticket configurations.

### Migration Notes
No manual migration required. All fixes are automatically applied on bot restart.

---

## Previous Versions

### Version 2.2.0 - July 30, 2025
- Enhanced ticket channel detection for custom panel names
- Fixed "This command can only be used in ticket channels" error
- Added support for panel-username format recognition

### Version 2.1.0 - July 2025
- Implemented comprehensive ticket system with custom embeds
- Added support team role assignments and pinging
- Database-driven panel management system
- Persistent button functionality across restarts