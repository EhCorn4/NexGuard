import { Button } from '@/components/ui/button';
import { useSimpleAuth } from '@/hooks/useSimpleAuth';
import { SimpleDashboard } from '@/components/dashboard/simple-dashboard';
import { ArrowRight, Lock, Shield, Brain, Activity } from 'lucide-react';

export default function Dashboard() {
  const { isAuthenticated, isLoading: authLoading, user } = useSimpleAuth();
  
  console.log('Dashboard - Auth status:', { isAuthenticated, authLoading, user });
  
  // Show loading state while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-800 pt-24 flex items-center justify-center">
        <div className="text-white text-xl">Loading NexGuard Dashboard...</div>
      </div>
    );
  }

  // Show authenticated dashboard
  if (isAuthenticated) {
    return <SimpleDashboard />;
  }

  // Show login prompt for unauthenticated users
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-800 pt-24">
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center">
          <div className="bg-gray-800/50 p-8 rounded-lg border border-gray-700 backdrop-blur-sm">
            <Lock className="w-16 h-16 text-cyan-400 mx-auto mb-6" />
            <h1 className="text-4xl font-bold text-white mb-4">
              NexGuard Dashboard Access Required
            </h1>
            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
              Sign in with your Discord account to access the NexGuard Dashboard 
              and manage your Discord bot settings, monitor servers, and view analytics.
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