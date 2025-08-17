# 🎉 New Feature: `/botlogs` - Automated Logging Setup!

## 📋 What's New?

**NexGuard now features one-command logging setup!** The new `/botlogs` command automatically creates and configures all your server's logging channels with full eventlog integration.

## 🚀 Key Features

### **✨ One-Command Setup**
- Creates a professional "Bot Logs" category
- Sets up all 7 specialized logging channels
- Automatically configures eventlog system integration

### **📁 Complete Channel Organization**
The command creates these channels with proper topics and configuration:
- 📋 `#general-logs` - General bot events and command usage
- 👥 `#member-logs` - Member joins, leaves, and profile updates  
- 💬 `#message-logs` - Message edits, deletions, and events
- 🔊 `#voice-logs` - Voice channel joins, leaves, and events
- 🏗️ `#channel-logs` - Channel creation, deletion, and modifications
- 🎭 `#role-logs` - Role creation, deletion, and permission changes
- 🛡️ `#moderation-logs` - Moderation actions and automod events

### **⚙️ Full EventLog Integration**
- Works seamlessly with existing `/eventlog` commands
- Use `/eventlog view` to see all configurations
- Modify individual channels with `/eventlog set`

## 🎯 How to Use

### **Quick Setup (Recommended)**
```
/botlogs setup
```
Creates everything automatically with proper permissions and configuration.

### **View Current Setup**
```
/botlogs view
```
Shows all configured channels and their status.

### **Clean Removal**
```
/botlogs cleanup
```
Removes all logging channels and clears configurations.

## 🔧 Requirements

- **Administrator permissions** required
- Bot needs "Manage Channels" permission
- Works in any server size

## 💡 Benefits

### **For New Servers**
- Get professional logging setup in seconds
- No manual channel creation needed
- Consistent naming and organization

### **For Existing Servers**
- Detects and configures existing channels
- Seamless integration with current setup
- No disruption to ongoing operations

### **For Administrators**
- Saves 10+ minutes of manual setup
- Professional categorization and naming
- Immediate access to comprehensive logging

## 🔗 Integration Notes

- Fully compatible with all existing NexGuard features
- Works with `/eventlog`, `/settings`, and other admin commands
- Maintains all current logging functionality
- Supports custom modifications after setup

## 📈 Perfect For

- **New server setups** - Get logging ready instantly
- **Server migrations** - Quickly establish logging on new servers  
- **Bulk configuration** - Set up multiple servers efficiently
- **Professional servers** - Maintain organized, comprehensive logs

---

**Ready to streamline your server logging?** 
Try `/botlogs setup` today and experience automated excellence!

*Command added in NexGuard v2.1 - August 17, 2025*