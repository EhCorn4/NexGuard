import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, ExternalLink, Key, Settings } from "lucide-react";

export function AuthNotice() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl bg-slate-800/50 border-slate-700">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-yellow-500/20">
            <Key className="h-6 w-6 text-yellow-500" />
          </div>
          <CardTitle className="text-2xl font-bold text-white">
            Server Admin Login Setup Required
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <Alert className="border-yellow-500/20 bg-yellow-500/10">
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
            <AlertDescription className="text-yellow-200">
              Discord OAuth authentication is not configured. To enable server admin login for the dashboard, you need to provide your Discord application credentials.
            </AlertDescription>
          </Alert>
          
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-white mb-3">Setup Instructions:</h3>
              <ol className="space-y-2 text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 bg-cyan-500 text-white text-sm rounded-full">1</span>
                  <span>Go to the Discord Developer Portal</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 bg-cyan-500 text-white text-sm rounded-full">2</span>
                  <span>Select your NexGuard application (or create one)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 bg-cyan-500 text-white text-sm rounded-full">3</span>
                  <span>Go to the OAuth2 section and copy the Client Secret</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 bg-cyan-500 text-white text-sm rounded-full">4</span>
                  <span>Add the Client Secret to your environment variables</span>
                </li>
              </ol>
            </div>

            <div className="bg-slate-700/50 rounded-lg p-4">
              <h4 className="font-semibold text-white mb-2">Required Environment Variables:</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <code className="bg-slate-600 px-2 py-1 rounded text-cyan-400">DISCORD_CLIENT_SECRET</code>
                  <span className="text-gray-400">Your Discord application's client secret</span>
                </div>
                <div className="flex items-center gap-2">
                  <code className="bg-slate-600 px-2 py-1 rounded text-green-400">SESSION_SECRET</code>
                  <span className="text-gray-400">✓ Already configured</span>
                </div>
              </div>
            </div>

            <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
              <h4 className="font-semibold text-white mb-2">Discord OAuth Setup Required:</h4>
              <div className="text-sm text-gray-300 space-y-2">
                <p>The Discord Client Secret is configured, but you need to add the redirect URI to your Discord application:</p>
                <ol className="space-y-1 ml-4">
                  <li>1. Go to Discord Developer Portal</li>
                  <li>2. Select your NexGuard application</li>
                  <li>3. Click on "OAuth2" in the left sidebar</li>
                  <li>4. Look for "Redirects" section (may be under "OAuth2 &gt; General")</li>
                  <li>5. Click "Add Redirect" and paste:</li>
                </ol>
                <div className="bg-slate-600 p-2 rounded text-xs text-green-400 break-all font-mono">
                  {window.location.origin}/api/auth/discord/callback
                </div>
                <p className="text-yellow-400">⚠️ If you don't see "Redirects", try OAuth2 &gt; URL Generator first</p>
                <p className="text-gray-400 text-xs">Alternative: Some applications show redirects in the "General Information" tab</p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <Button
                onClick={() => window.open('https://discord.com/developers/applications', '_blank')}
                className="flex-1 bg-[#5865F2] hover:bg-[#4752C4] text-white border-0"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                Discord Developer Portal
              </Button>
              <Button
                onClick={() => window.location.href = '/api/auth/discord'}
                variant="outline"
                className="flex-1 border-slate-600 text-gray-300 hover:bg-slate-700"
              >
                <Settings className="w-4 h-4 mr-2" />
                Test Configuration
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}