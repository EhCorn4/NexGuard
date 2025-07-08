# Discord OAuth Setup Instructions

## Current Configuration Issue

The Discord OAuth is failing because the redirect URI in your Discord application doesn't match the current Replit domain.

## Required Discord Application Settings

1. **Go to Discord Developer Portal**: https://discord.com/developers/applications
2. **Select your NexGuard application**
3. **Go to OAuth2 > General**
4. **Add this exact redirect URI**:
   ```
   https://ed8c2fad-d762-4890-ab60-2ba13bfca210-00-1mxalymkn4j67.janeway.replit.dev/api/auth/discord/callback
   ```

## Your Current Settings Should Be:
- **Client ID**: 1389775821794705429
- **Client Secret**: [Already configured in Replit Secrets]
- **Redirect URI**: https://ed8c2fad-d762-4890-ab60-2ba13bfca210-00-1mxalymkn4j67.janeway.replit.dev/api/auth/discord/callback
- **Scopes**: identify, guilds

## After Adding the Redirect URI:
1. Save your Discord application settings
2. Test the login by clicking "Server Login" on the website
3. You should be redirected to Discord for authorization
4. After authorization, you'll return to the dashboard with your server list

## Note:
If you change the Replit domain or deploy to a different environment, you'll need to update the redirect URI in your Discord application settings accordingly.