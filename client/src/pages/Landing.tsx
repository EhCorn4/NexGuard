import { ArrowRight, Shield, Zap, Users } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-800 pt-24">
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-white mb-6">
            Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">NexGuard</span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Professional Discord bot management system with advanced security, threat intelligence, 
            and comprehensive server protection across 18 Discord servers.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Button 
              onClick={() => window.location.href = '/api/auth/discord'}
              className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white px-8 py-4 text-lg"
            >
              Access Security Dashboard <ArrowRight className="ml-2" size={20} />
            </Button>
            <Button 
              onClick={() => window.location.href = '/features'}
              variant="outline" 
              className="border-gray-300 text-gray-300 hover:bg-gray-800 px-8 py-4 text-lg"
            >
              Learn More
            </Button>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mt-16">
            <div className="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
              <Shield className="w-12 h-12 text-cyan-400 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold text-white mb-2">Advanced Security</h3>
              <p className="text-gray-400">
                AI-powered threat detection and real-time security monitoring across all protected servers.
              </p>
            </div>
            
            <div className="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
              <Zap className="w-12 h-12 text-purple-400 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold text-white mb-2">67+ Commands</h3>
              <p className="text-gray-400">
                Comprehensive command suite covering moderation, administration, tickets, and analytics.
              </p>
            </div>
            
            <div className="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
              <Users className="w-12 h-12 text-green-400 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold text-white mb-2">949 Users Protected</h3>
              <p className="text-gray-400">
                Actively protecting Discord communities with real-time threat intelligence.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}