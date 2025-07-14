# Discord OAuth Quick Fix

## 🔍 Current Issue
The OAuth token exchange is failing because Discord is rejecting the redirect URI. This happens when the redirect URI in your Discord application doesn't exactly match what the code is sending.

## 📋 Exact Steps to Fix

### 1. Go to Discord Developer Portal
- Visit: https://discord.com/developers/applications
- Select your application (ID: 1389775821794705429)

### 2. Navigate to OAuth2 Section
- Click "OAuth2" in the left sidebar
- Look for "Redirects" section

### 3. Add This EXACT URI
```
https://ed8c2fad-d762-4890-ab60-2ba13bfca210-00-1mxalymkn4j67.janeway.replit.dev/api/auth/discord/callback
```

### 4. Important Notes
- ✅ Must be HTTPS (not HTTP)
- ✅ Must include the full domain
- ✅ Must end with `/api/auth/discord/callback`
- ✅ Case-sensitive
- ✅ No trailing slash

### 5. Required OAuth2 Scopes
Make sure these scopes are also selected:
- `identify` - Get user information
- `guilds` - Get user's Discord servers

### 6. Test the Fix
After adding the redirect URI:
1. Save the Discord application settings
2. Try logging in through the dashboard
3. You should be redirected to Discord, then back to the dashboard successfully

## 🚨 Common Mistakes
- Adding HTTP instead of HTTPS
- Missing the full domain name
- Adding extra slashes or characters
- Not saving the Discord application settings

## 🔄 Alternative: Use Bot Commands
While fixing OAuth, you can still use the bot integration:
- `!config` - Shows current settings
- `!addcmd name response` - Add custom commands
- `!warn @user reason` - Warn users (logs to dashboard)
- `!mute @user reason` - Mute users (logs to dashboard)

The bot integration works 100% regardless of OAuth status.