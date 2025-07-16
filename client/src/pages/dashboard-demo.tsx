import React from "react";
import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StaggerContainer, StaggerItem } from "@/components/ui/stagger-container";
import { PageTransition } from "@/components/ui/page-transition";
import { BotStatus } from "@/components/ui/bot-status";
import { BotControl } from "@/components/ui/bot-control";
import { 
  Settings, 
  Shield, 
  Users, 
  MessageSquare, 
  Activity,
  Server,
  Bot,
  Crown,
  Zap
} from "lucide-react";

export default function DashboardDemo() {
  // Mock user data for demonstration
  const mockUser = {
    id: "123456789",
    username: "DemoUser",
    discriminator: "0001",
    avatar: null,
    globalName: "Demo User"
  };

  // Mock guild data for demonstration
  const mockGuilds = [
    {
      id: "guild1",
      name: "Test Server 1",
      icon: null,
      owner: true,
      permissions: "8",
      hasBot: true
    },
    {
      id: "guild2", 
      name: "Test Server 2",
      icon: null,
      owner: false,
      permissions: "8",
      hasBot: true
    }
  ];

  const [selectedGuild, setSelectedGuild] = React.useState<string | null>(null);

  const availableGuilds = mockGuilds.filter(guild => guild.hasBot);

  return (
    <PageTransition>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="container mx-auto px-4 py-8">
          <PageHeader 
            title="Server Management Dashboard (Demo)"
            description="Manage NexGuard settings for your Discord servers"
          />

          {/* User Info and Bot Status Header */}
          <StaggerContainer className="mb-8">
            <StaggerItem index={0}>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-slate-600 rounded-full flex items-center justify-center">
                        <Users className="w-6 h-6 text-gray-300" />
                      </div>
                      <div>
                        <h2 className="text-xl font-bold text-white">
                          {mockUser.globalName || mockUser.username}
                        </h2>
                        <p className="text-gray-400">
                          Server Administrator • @{mockUser.username}#{mockUser.discriminator}
                        </p>
                      </div>
                    </div>
                    <Badge variant="outline" className="border-orange-500 text-orange-500">
                      Demo Mode
                    </Badge>
                  </div>
                </CardHeader>
              </Card>
            </StaggerItem>
            
            <StaggerItem index={1}>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
                <BotStatus />
                <BotControl />
              </div>
            </StaggerItem>
          </StaggerContainer>

          {/* Server Selection */}
          <StaggerContainer className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
            {availableGuilds.map((guild, index) => (
              <StaggerItem key={guild.id} index={index}>
                <Card 
                  className={`bg-slate-800/50 border-slate-700 cursor-pointer hover:bg-slate-800/70 transition-all ${
                    selectedGuild === guild.id ? 'ring-2 ring-cyan-500' : ''
                  }`}
                  onClick={() => setSelectedGuild(guild.id)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-slate-600 rounded-full flex items-center justify-center">
                        <Server className="w-5 h-5 text-gray-300" />
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-lg text-white">{guild.name}</CardTitle>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="secondary" className="text-xs">
                            <Bot className="w-3 h-3 mr-1" />
                            NexGuard Active
                          </Badge>
                          {guild.owner ? (
                            <Badge variant="outline" className="text-xs border-yellow-500 text-yellow-500">
                              <Crown className="w-3 h-3 mr-1" />
                              Owner
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-xs border-blue-500 text-blue-500">
                              <Shield className="w-3 h-3 mr-1" />
                              Admin
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              </StaggerItem>
            ))}
          </StaggerContainer>

          {/* Server Configuration Panel */}
          {selectedGuild && (
            <StaggerContainer>
              <StaggerItem index={0}>
                <Card className="bg-slate-800/50 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <Settings className="w-5 h-5" />
                      Server Configuration
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                      <Card className="bg-slate-700/50 border-slate-600">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm flex items-center gap-2 text-white">
                            <Shield className="w-4 h-4" />
                            Moderation
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <Button size="sm" className="w-full">
                            Configure
                          </Button>
                        </CardContent>
                      </Card>

                      <Card className="bg-slate-700/50 border-slate-600">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm flex items-center gap-2 text-white">
                            <MessageSquare className="w-4 h-4" />
                            Welcome Messages
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <Button size="sm" className="w-full">
                            Configure
                          </Button>
                        </CardContent>
                      </Card>

                      <Card className="bg-slate-700/50 border-slate-600">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm flex items-center gap-2 text-white">
                            <Activity className="w-4 h-4" />
                            Logging
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <Button size="sm" className="w-full">
                            Configure
                          </Button>
                        </CardContent>
                      </Card>
                    </div>
                  </CardContent>
                </Card>
              </StaggerItem>
            </StaggerContainer>
          )}

          {/* Demo Notice */}
          <div className="mt-8 text-center">
            <Card className="bg-orange-900/20 border-orange-500/50">
              <CardContent className="pt-6">
                <p className="text-orange-300">
                  This is a demo version of the dashboard. To access the full functionality with your Discord servers, 
                  please ensure Discord OAuth is properly configured.
                </p>
                <Button 
                  onClick={() => window.location.href = '/dashboard'}
                  className="mt-4 bg-blue-600 hover:bg-blue-700"
                >
                  Try OAuth Login
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </PageTransition>
  );
}