import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StaggerContainer, StaggerItem } from "@/components/ui/stagger-container";
import { PageTransition } from "@/components/ui/page-transition";
import { AuthNotice } from "@/components/ui/auth-notice";
import { 
  Settings, 
  Shield, 
  Users, 
  MessageSquare, 
  Activity, 
  LogOut,
  Server,
  Bot,
  Crown,
  Zap
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface UserGuild {
  id: string;
  name: string;
  icon: string | null;
  owner: boolean;
  permissions: string;
  hasBot: boolean;
}

interface DashboardUser {
  id: string;
  username: string;
  discriminator: string;
  avatar: string | null;
  globalName: string | null;
}

export default function Dashboard() {
  const { toast } = useToast();
  const [selectedGuild, setSelectedGuild] = useState<string | null>(null);

  const { data: user, isLoading: userLoading, error: userError } = useQuery<DashboardUser>({
    queryKey: ['/api/auth/user'],
    retry: false,
  });

  const { data: guilds, isLoading: guildsLoading } = useQuery<UserGuild[]>({
    queryKey: ['/api/auth/guilds'],
    retry: false,
    enabled: !!user,
  });

  // Check URL parameters for error state
  const urlParams = new URLSearchParams(window.location.search);
  const oauthError = urlParams.get('error');
  
  // Check if Discord OAuth is configured
  const isDiscordConfigured = !userError || !userError.message.includes('Discord OAuth not configured');

  useEffect(() => {
    if (!userLoading && !user && isDiscordConfigured && !oauthError) {
      toast({
        title: "Authentication Required",
        description: "Please log in to access the dashboard",
        variant: "destructive",
      });
      setTimeout(() => {
        window.location.href = '/api/auth/discord';
      }, 1000);
    }
  }, [user, userLoading, toast, isDiscordConfigured, oauthError]);

  // Show auth notice if Discord OAuth is not configured or there's an OAuth error
  if (!isDiscordConfigured || oauthError === 'oauth_not_configured') {
    return <AuthNotice />;
  }

  const handleLogout = () => {
    window.location.href = '/api/auth/logout';
  };

  if (userLoading || !user) {
    return (
      <PageTransition>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          <div className="container mx-auto px-4 py-8">
            <div className="flex items-center justify-center min-h-[60vh]">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto mb-4"></div>
                <p className="text-gray-300">Loading dashboard...</p>
              </div>
            </div>
          </div>
        </div>
      </PageTransition>
    );
  }

  const availableGuilds = guilds?.filter(guild => guild.hasBot) || [];
  const inviteableGuilds = guilds?.filter(guild => !guild.hasBot) || [];

  return (
    <PageTransition>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="container mx-auto px-4 py-8">
          <PageHeader 
            title="Server Management Dashboard"
            description="Manage NexGuard settings for your Discord servers"
          />

          {/* User Info Header */}
          <StaggerContainer className="mb-8">
            <StaggerItem index={0}>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      {user.avatar ? (
                        <img 
                          src={`https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png?size=64`}
                          alt={user.username}
                          className="w-12 h-12 rounded-full"
                        />
                      ) : (
                        <div className="w-12 h-12 bg-slate-600 rounded-full flex items-center justify-center">
                          <Users className="w-6 h-6 text-gray-300" />
                        </div>
                      )}
                      <div>
                        <h2 className="text-xl font-bold text-white">
                          {user.globalName || user.username}
                        </h2>
                        <p className="text-gray-400">
                          Server Administrator • @{user.username}#{user.discriminator}
                        </p>
                      </div>
                    </div>
                    <Button
                      onClick={handleLogout}
                      variant="outline"
                      className="border-slate-600 text-gray-300 hover:bg-slate-700"
                    >
                      <LogOut className="w-4 h-4 mr-2" />
                      Logout
                    </Button>
                  </div>
                </CardHeader>
              </Card>
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
                      {guild.icon ? (
                        <img 
                          src={`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png?size=32`}
                          alt={guild.name}
                          className="w-10 h-10 rounded-full"
                        />
                      ) : (
                        <div className="w-10 h-10 bg-slate-600 rounded-full flex items-center justify-center">
                          <Server className="w-5 h-5 text-gray-300" />
                        </div>
                      )}
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

          {/* Invite Bot to Servers */}
          {inviteableGuilds.length > 0 && (
            <StaggerContainer>
              <StaggerItem index={0}>
                <Card className="bg-slate-800/50 border-slate-700 mb-8">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center">
                      <Zap className="w-5 h-5 mr-2 text-yellow-500" />
                      Add NexGuard to Servers You Manage
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                      {inviteableGuilds.map((guild) => (
                        <div key={guild.id} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            {guild.icon ? (
                              <img 
                                src={`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png?size=32`}
                                alt={guild.name}
                                className="w-8 h-8 rounded-full"
                              />
                            ) : (
                              <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center">
                                <Server className="w-4 h-4 text-gray-300" />
                              </div>
                            )}
                            <span className="text-white font-medium">{guild.name}</span>
                          </div>
                          <Button
                            size="sm"
                            onClick={() => {
                              window.open(`https://discord.com/oauth2/authorize?client_id=1389775821794705429&permissions=8&guild_id=${guild.id}&scope=bot`, '_blank');
                            }}
                            className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white border-0"
                          >
                            Add Bot
                          </Button>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </StaggerItem>
            </StaggerContainer>
          )}

          {/* Dashboard Features */}
          {selectedGuild && (
            <StaggerContainer className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {[
                {
                  title: "Moderation Tools",
                  description: "Manage bans, kicks, warns, and timeouts for your server",
                  icon: Shield,
                  color: "text-red-400",
                  onClick: () => {
                    toast({
                      title: "Coming Soon",
                      description: "Moderation tools panel will be available soon",
                    });
                  }
                },
                {
                  title: "Auto-Moderation",
                  description: "Set up automatic filters and response rules",
                  icon: Activity,
                  color: "text-orange-400",
                  onClick: () => {
                    toast({
                      title: "Coming Soon",
                      description: "Auto-moderation configuration will be available soon",
                    });
                  }
                },
                {
                  title: "Server Configuration",
                  description: "Customize NexGuard settings for your server",
                  icon: Settings,
                  color: "text-blue-400",
                  onClick: () => {
                    window.location.href = `/server/${selectedGuild.id}`;
                  }
                },
                {
                  title: "Activity Logs",
                  description: "Monitor server activity and moderation history",
                  icon: MessageSquare,
                  color: "text-green-400",
                  onClick: () => {
                    toast({
                      title: "Coming Soon",
                      description: "Activity logs will be available soon",
                    });
                  }
                },
              ].map((feature, index) => (
                <StaggerItem key={feature.title} index={index}>
                  <Card 
                    className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors cursor-pointer"
                    onClick={feature.onClick}
                  >
                    <CardHeader className="text-center">
                      <feature.icon className={`w-12 h-12 ${feature.color} mx-auto mb-3`} />
                      <CardTitle className="text-white">{feature.title}</CardTitle>
                      <p className="text-gray-400 text-sm">{feature.description}</p>
                    </CardHeader>
                  </Card>
                </StaggerItem>
              ))}
            </StaggerContainer>
          )}

          {!selectedGuild && availableGuilds.length > 0 && (
            <div className="text-center py-12">
              <Server className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Select a Server to Manage</h3>
              <p className="text-gray-400">
                Choose a server above to access NexGuard's management tools and configuration options
              </p>
            </div>
          )}

          {availableGuilds.length === 0 && !guildsLoading && (
            <div className="text-center py-12">
              <Bot className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No Managed Servers</h3>
              <p className="text-gray-400 mb-6">
                You don't have any servers with NexGuard installed where you have admin permissions.
                Add NexGuard to a server you manage to get started!
              </p>
              <Button
                onClick={() => {
                  window.open('https://discord.com/oauth2/authorize?client_id=1389775821794705429&permissions=8&scope=bot', '_blank');
                }}
                className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white border-0"
              >
                <Bot className="w-4 h-4 mr-2" />
                Add NexGuard to Your Server
              </Button>
            </div>
          )}
        </div>
      </div>
    </PageTransition>
  );
}