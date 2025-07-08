# Discord OAuth - Immediate Fix Required

## The Problem
You're getting "Invalid OAuth2 redirect_uri" because the redirect URI in your Discord application doesn't match what the code is generating.

## The Exact Fix

**Step 1: Go to Discord Developer Portal**
1. Visit: https://discord.com/developers/applications
2. Click on your NexGuard application (ID: 1389775821794705429)
3. Go to **OAuth2 → General**

**Step 2: Add This Exact Redirect URI**
In the "Redirects" section, add this exact URL:
```
https://ed8c2fad-d762-4890-ab60-2ba13bfca210-00-1mxalymkn4j67.janeway.replit.dev/api/auth/discord/callback
```

**Step 3: Save Changes**
Click "Save Changes" at the bottom of the page.

**Step 4: Test**
Go back to your dashboard and try the "Server Login" button again.

## Current Status
- ✅ Code is working correctly
- ✅ Environment variables are configured
- ❌ Discord application redirect URI needs to be added
- ✅ Domain is: `ed8c2fad-d762-4890-ab60-2ba13bfca210-00-1mxalymkn4j67.janeway.replit.dev`

## If It Still Doesn't Work
1. Double-check the redirect URI matches exactly (no extra spaces, characters, or trailing slashes)
2. Make sure you clicked "Save Changes" in Discord
3. Try clearing your browser cache
4. Let me know what error message you get