import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, Shield, Users, Server } from 'lucide-react';

interface BotStatus {
  id: number;
  isOnline: boolean;
  guildsCount: number;
  usersCount: number;
  uptime: string;
  version: string;
}

export function SimpleDashboard() {
  const { data: botStatus, isLoading } = useQuery<BotStatus>({
    queryKey: ['/api/bot/status'],
    refetchInterval: 15000,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-800 pt-24">
        <div className="max-w-7xl mx-auto px-4 py-16">
          <div className="text-center text-white">
            <h1 className="text-4xl font-bold mb-4">Loading Security Dashboard...</h1>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-800 pt-24">
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">
              NexGuard Security Dashboard
            </span>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Real-time monitoring and threat intelligence for Discord server protection
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Bot Status</CardTitle>
              <Activity className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {botStatus?.isOnline ? (
                  <Badge variant="default" className="bg-green-600">Online</Badge>
                ) : (
                  <Badge variant="destructive">Offline</Badge>
                )}
              </div>
              <p className="text-xs text-gray-400">
                Version {botStatus?.version || 'Unknown'}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Protected Servers</CardTitle>
              <Server className="h-4 w-4 text-cyan-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{botStatus?.guildsCount || 0}</div>
              <p className="text-xs text-gray-400">
                Discord servers protected
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Protected Users</CardTitle>
              <Users className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{botStatus?.usersCount || 0}</div>
              <p className="text-xs text-gray-400">
                Users under protection
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Security Level</CardTitle>
              <Shield className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                <Badge variant="default" className="bg-yellow-600">High</Badge>
              </div>
              <p className="text-xs text-gray-400">
                Threat monitoring active
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">System Status</CardTitle>
            </CardHeader>
            <CardContent className="text-gray-300">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span>Bot Uptime</span>
                  <span className="text-green-400">{botStatus?.uptime || 'Unknown'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>AI Threat Detection</span>
                  <Badge className="bg-green-600">Active</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span>Cross-Server Intelligence</span>
                  <Badge className="bg-green-600">Operational</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span>Real-time Monitoring</span>
                  <Badge className="bg-green-600">Enabled</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Recent Activity</CardTitle>
            </CardHeader>
            <CardContent className="text-gray-300">
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-sm">Discord authentication successful</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                  <span className="text-sm">Bot connected to {botStatus?.guildsCount || 0} servers</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                  <span className="text-sm">Threat monitoring systems active</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                  <span className="text-sm">Performance alerts configured</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}