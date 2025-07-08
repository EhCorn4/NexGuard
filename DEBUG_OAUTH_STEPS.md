# Debug OAuth - Step by Step

## Current Status
I've temporarily hardcoded the redirect URI to:
```
https://ed8c2fad-d762-4890-ab60-2ba13bfca210-00-1mxalymkn4j67.janeway.replit.dev/api/auth/discord/callback
```

## What You Need to Do

### Step 1: Add the Redirect URI to Discord
1. Go to https://discord.com/developers/applications
2. Select your NexGuard application (ID: 1389775821794705429)
3. Go to **OAuth2 → General**
4. In the "Redirects" section, add this exact URI:
   ```
   https://ed8c2fad-d762-4890-ab60-2ba13bfca210-00-1mxalymkn4j67.janeway.replit.dev/api/auth/discord/callback
   ```
5. Click "Save Changes"

### Step 2: Test the Login
1. Go to your dashboard
2. Click "Server Login"
3. If it works, you'll be redirected to Discord
4. After authorizing, you'll be redirected back to your dashboard

### Step 3: Check the Console
When you click "Server Login", check the server console logs. You should see:
- "=== Discord OAuth Debug ==="
- The exact redirect URI being used
- The full Discord authorization URL

## If It Still Doesn't Work
1. Double-check the redirect URI in Discord matches exactly
2. Make sure you saved the changes in Discord
3. Try in an incognito/private browser window
4. Check the server logs for any error messages

## What I'm Looking For
The exact error message or what happens when you click "Server Login". This will help me determine if the issue is:
- Discord redirect URI configuration
- Code generation problem
- Something else entirely