import { LogOut, Shield, Activity, Server } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";

export default function UserHome() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-800 pt-24 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">
              Welcome back, {user?.firstName || 'User'}!
            </h1>
            <p className="text-gray-300">Manage your NexGuard protected servers</p>
          </div>
          
          <Button 
            onClick={() => window.location.href = '/api/logout'}
            variant="outline"
            className="border-gray-300 text-gray-300 hover:bg-gray-800"
          >
            <LogOut className="mr-2" size={16} />
            Sign Out
          </Button>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Shield className="mr-2 text-cyan-400" size={20} />
                Security Dashboard
              </CardTitle>
              <CardDescription className="text-gray-400">
                Monitor threat intelligence and security status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => window.location.href = '/dashboard'}
                className="w-full bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600"
              >
                Access Dashboard
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Activity className="mr-2 text-green-400" size={20} />
                Analytics
              </CardTitle>
              <CardDescription className="text-gray-400">
                View server analytics and usage statistics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => window.location.href = '/analytics'}
                variant="outline"
                className="w-full border-gray-600 text-gray-300 hover:bg-gray-700"
              >
                View Analytics
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Server className="mr-2 text-purple-400" size={20} />
                Bot Management
              </CardTitle>
              <CardDescription className="text-gray-400">
                Manage bot settings and configurations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => window.location.href = '/features'}
                variant="outline"
                className="w-full border-gray-600 text-gray-300 hover:bg-gray-700"
              >
                Manage Bot
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="bg-gray-800/30 p-6 rounded-lg border border-gray-700">
          <h2 className="text-2xl font-semibold text-white mb-4">Quick Stats</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-cyan-400">18</div>
              <div className="text-gray-400">Protected Servers</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-400">949</div>
              <div className="text-gray-400">Users Monitored</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-400">67</div>
              <div className="text-gray-400">Commands Available</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-400">24/7</div>
              <div className="text-gray-400">Active Monitoring</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}