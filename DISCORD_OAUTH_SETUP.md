# Discord OAuth Setup - Quick Fix Guide

## Current Issue
Discord OAuth redirect is failing because the redirect URI in your Discord application doesn't match the current Replit domain.

## Immediate Action Required

### Step 1: Update Discord Application Settings
1. Go to: https://discord.com/developers/applications
2. Select your NexGuard application (ID: 1389775821794705429)
3. Navigate to OAuth2 → General
4. Add this redirect URI to the "Redirects" section:
   ```
   https://ed8c2fad-d762-4890-ab60-2ba13bfca210-00-1mxalymkn4j67.janeway.replit.dev/api/auth/discord/callback
   ```
5. Save changes

### Step 2: Test Authentication
1. Go to your website dashboard
2. Click "Server Login" 
3. You should be redirected to Discord for authorization
4. After approval, you'll return to the dashboard with your server list

## Current Configuration Status
- ✅ Client ID: 1389775821794705429
- ✅ Client Secret: Configured in Replit Secrets
- ❌ Redirect URI: Needs update in Discord settings
- ✅ Scopes: identify, guilds
- ✅ Code implementation: Working correctly

## If You Still Have Issues
The application will show specific error messages in the URL:
- `?error=discord_denied` - You clicked "Cancel" on Discord
- `?error=no_code` - Discord didn't provide authorization code
- `?error=oauth_not_configured` - Discord client secret missing
- `?error=auth_failed` - Token exchange failed

## Note for Production
When deploying to production, you'll need to add the production domain redirect URI to your Discord application settings as well.