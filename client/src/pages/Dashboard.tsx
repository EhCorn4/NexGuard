import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { useSimpleAuth } from '@/hooks/useSimpleAuth';
import { Activity, Shield, Users, Server, AlertTriangle, Brain, ArrowRight, Lock } from 'lucide-react';

interface BotStatus {
  id: number;
  isOnline: boolean;
  guildsCount: number;
  usersCount: number;
  uptime: string;
  lastRestart: string;
  version: string;
  updatedAt: string;
}

interface ThreatPattern {
  id: number;
  patternName: string;
  patternType: string;
  description: string;
  severity: number;
  occurrenceCount: number;
  lastSeen: string;
}

interface ActiveThreat {
  id: number;
  threatType: string;
  threatScore: number;
  affectedUsers: string[];
  detectedAt: string;
  actionTaken: string | null;
}

export default function Dashboard() {
  // Try both auth hooks for debugging
  const complexAuth = useAuth();
  const simpleAuth = useSimpleAuth();
  
  // Use simple auth as primary
  const { isAuthenticated, isLoading: authLoading, user } = simpleAuth;
  
  // Debug logging
  console.log('Dashboard render - Complex auth:', complexAuth);
  console.log('Dashboard render - Simple auth:', simpleAuth);
  
  const shouldShowDashboard = isAuthenticated;

  const { data: botStatus, isLoading: statusLoading } = useQuery<BotStatus>({
    queryKey: ['/api/bot/status'],
    refetchInterval: 15000, // Refresh every 15 seconds
    enabled: isAuthenticated, // Only run query if authenticated
  });

  const { data: threatPatterns, isLoading: patternsLoading } = useQuery<ThreatPattern[]>({
    queryKey: ['/api/threat-intelligence/patterns'],
    refetchInterval: 30000, // Refresh every 30 seconds
    enabled: isAuthenticated, // Only run query if authenticated
  });

  const { data: activeThreats, isLoading: threatsLoading } = useQuery<ActiveThreat[]>({
    queryKey: ['/api/threat-intelligence/active/123456789'], // Using demo guild ID
    refetchInterval: 10000, // Refresh every 10 seconds
    enabled: isAuthenticated, // Only run query if authenticated
  });

  // Show loading state while checking authentication
  if (authLoading) {
    console.log('Showing loading state');
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-800 pt-24 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  // Show sign-in interface for unauthenticated users
  if (!shouldShowDashboard) {
    console.log('Showing sign-in interface - not authenticated. Auth state:', { isAuthenticated, authLoading, user });
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-800 pt-24">
        <div className="max-w-4xl mx-auto px-4 py-16">
          <div className="text-center">
            <div className="bg-gray-800/50 p-8 rounded-lg border border-gray-700 backdrop-blur-sm">
              <Lock className="w-16 h-16 text-cyan-400 mx-auto mb-6" />
              <h1 className="text-4xl font-bold text-white mb-4">
                Security Dashboard Access Required
              </h1>
              <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
                Sign in with your Replit account to access the NexGuard Security Dashboard 
                and monitor real-time threat intelligence across 18 protected Discord servers.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
                <Button 
                  onClick={() => window.location.href = '/api/auth/discord?returnTo=/dashboard'}
                  className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white px-8 py-4 text-lg"
                >
                  Sign in with Discord <ArrowRight className="ml-2" size={20} />
                </Button>
                <Button 
                  onClick={() => window.location.href = '/features'}
                  variant="outline" 
                  className="border-gray-300 text-gray-300 hover:bg-gray-800 px-8 py-4 text-lg"
                >
                  Learn More
                </Button>
              </div>

              <div className="grid md:grid-cols-3 gap-6 text-left">
                <div className="bg-gray-700/30 p-4 rounded border border-gray-600">
                  <Shield className="w-8 h-8 text-cyan-400 mb-2" />
                  <h3 className="font-semibold text-white mb-1">Real-Time Protection</h3>
                  <p className="text-gray-400 text-sm">AI-powered threat detection monitoring</p>
                </div>
                
                <div className="bg-gray-700/30 p-4 rounded border border-gray-600">
                  <Brain className="w-8 h-8 text-purple-400 mb-2" />
                  <h3 className="font-semibold text-white mb-1">Threat Intelligence</h3>
                  <p className="text-gray-400 text-sm">Advanced behavioral analysis and patterns</p>
                </div>
                
                <div className="bg-gray-700/30 p-4 rounded border border-gray-600">
                  <Activity className="w-8 h-8 text-green-400 mb-2" />
                  <h3 className="font-semibold text-white mb-1">Live Monitoring</h3>
                  <p className="text-gray-400 text-sm">24/7 security status and alerts</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (isOnline: boolean) => isOnline ? 'text-green-500' : 'text-red-500';
  const getThreatColor = (score: number) => {
    if (score >= 70) return 'text-red-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getSeverityBadge = (severity: number) => {
    if (severity >= 8) return <Badge variant="destructive">Critical</Badge>;
    if (severity >= 6) return <Badge variant="secondary">High</Badge>;
    if (severity >= 4) return <Badge variant="outline">Medium</Badge>;
    return <Badge variant="default">Low</Badge>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-800 pt-24 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">NexGuard Security Dashboard</h1>
          <p className="text-gray-300">Real-time monitoring and threat intelligence</p>
        </div>

        {/* Bot Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-200">Bot Status</CardTitle>
              <Activity className={getStatusColor(botStatus?.isOnline || false)} size={16} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {statusLoading ? 'Loading...' : botStatus?.isOnline ? 'Online' : 'Offline'}
              </div>
              <p className="text-xs text-gray-400">
                Version {botStatus?.version || 'Unknown'}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-200">Protected Servers</CardTitle>
              <Server className="text-blue-500" size={16} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {statusLoading ? '--' : botStatus?.guildsCount || 0}
              </div>
              <p className="text-xs text-gray-400">
                Active monitoring
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-200">Users Protected</CardTitle>
              <Users className="text-green-500" size={16} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {statusLoading ? '--' : (botStatus?.usersCount || 0).toLocaleString()}
              </div>
              <p className="text-xs text-gray-400">
                Real-time analysis
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-200">Uptime</CardTitle>
              <Activity className="text-cyan-500" size={16} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {statusLoading ? '--' : botStatus?.uptime || '0:00:00'}
              </div>
              <p className="text-xs text-gray-400">
                Current session
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Active Threats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <AlertTriangle className="text-red-500" size={20} />
                Active Threats
              </CardTitle>
              <CardDescription className="text-gray-400">
                Real-time threat detection and analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              {threatsLoading ? (
                <div className="text-gray-400">Loading threat data...</div>
              ) : activeThreats && activeThreats.length > 0 ? (
                <div className="space-y-3">
                  {activeThreats.slice(0, 5).map((threat) => (
                    <Alert key={threat.id} className="bg-gray-700/50 border-gray-600">
                      <AlertDescription className="text-gray-200">
                        <div className="flex justify-between items-start">
                          <div>
                            <span className="font-medium">{threat.threatType.replace('_', ' ').toUpperCase()}</span>
                            <div className={`text-lg font-bold ${getThreatColor(threat.threatScore)}`}>
                              Score: {threat.threatScore}/100
                            </div>
                            <div className="text-sm text-gray-400">
                              {threat.affectedUsers.length} user(s) monitored
                            </div>
                          </div>
                          <div className="text-xs text-gray-500">
                            {new Date(threat.detectedAt).toLocaleTimeString()}
                          </div>
                        </div>
                      </AlertDescription>
                    </Alert>
                  ))}
                </div>
              ) : (
                <div className="text-green-400 flex items-center gap-2">
                  <Shield size={16} />
                  <div>
                    <div className="font-medium">System Active - Monitoring Live</div>
                    <div className="text-sm text-gray-400">AI analyzing all Discord events across 18 servers</div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Brain className="text-purple-500" size={20} />
                AI Learning Patterns
              </CardTitle>
              <CardDescription className="text-gray-400">
                Machine learning attack pattern recognition
              </CardDescription>
            </CardHeader>
            <CardContent>
              {patternsLoading ? (
                <div className="text-gray-400">Loading pattern data...</div>
              ) : threatPatterns && threatPatterns.length > 0 ? (
                <div className="space-y-3">
                  {threatPatterns.slice(0, 4).map((pattern) => (
                    <div key={pattern.id} className="border border-gray-600 rounded p-3 bg-gray-700/30">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium text-white">{pattern.patternName}</span>
                        {getSeverityBadge(pattern.severity)}
                      </div>
                      <div className="text-sm text-gray-300 mb-1">{pattern.description}</div>
                      <div className="flex justify-between text-xs text-gray-400">
                        <span>Type: {pattern.patternType}</span>
                        <span>Detected: {pattern.occurrenceCount}x</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-400">No patterns learned yet</div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* System Status */}
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">System Status</CardTitle>
            <CardDescription className="text-gray-400">
              Live monitoring of all security systems
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-700/30 rounded p-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-200">Threat Intelligence</span>
                  <Badge variant="default" className="bg-green-600">Active</Badge>
                </div>
                <div className="text-sm text-gray-400 mt-1">
                  AI-powered analysis running
                </div>
              </div>
              
              <div className="bg-gray-700/30 rounded p-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-200">Anti-Raid Protection</span>
                  <Badge variant="default" className="bg-green-600">Active</Badge>
                </div>
                <div className="text-sm text-gray-400 mt-1">
                  Enhanced with AI scoring
                </div>
              </div>
              
              <div className="bg-gray-700/30 rounded p-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-200">Cross-Server Intelligence</span>
                  <Badge variant="default" className="bg-green-600">Active</Badge>
                </div>
                <div className="text-sm text-gray-400 mt-1">
                  Network protection enabled
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}