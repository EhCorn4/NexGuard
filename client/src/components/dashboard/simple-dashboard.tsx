import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { Activity, Shield, Users, Server, Settings, BarChart3, MessageSquare, AlertTriangle, Clock, Zap, MessageCircle, Lock, Bot } from 'lucide-react';
import { useState, useEffect } from "react";

interface BotStatus {
  id: number;
  isOnline: boolean;
  guildsCount: number;
  usersCount: number;
  uptime: string;
  version: string;
}

interface BotConfig {
  guild_id: string;
  guild_name: string;
  icon?: string | null;
  member_count?: number;
  prefix?: string | null;
  language?: string | null;
  timezone?: string | null;
  welcome_enabled?: boolean;
  welcome_channel_id?: string | null;
  welcome_message?: string | null;
  welcome_embed_enabled?: boolean;
  welcome_role_id?: string | null;
  welcome_dm_enabled?: boolean;
  goodbye_enabled?: boolean;
  goodbye_channel_id?: string | null;
  goodbye_message?: string | null;
  moderation_enabled?: boolean;
  mod_role_id?: string | null;
  admin_role_id?: string | null;
  mute_role_id?: string | null;
  automod_enabled?: boolean;
  spam_detection?: boolean;
  caps_detection?: boolean;
  link_detection?: boolean;
  invite_detection?: boolean;
  bad_words_detection?: boolean;
  mention_spam_detection?: boolean;
  duplicate_message_detection?: boolean;
  automod_action?: string | null;
  automod_threshold?: number;
  log_channel_id?: string | null;
  general_log_channel_id?: string | null;
  member_log_channel_id?: string | null;
  message_log_channel_id?: string | null;
  voice_log_channel_id?: string | null;
  channel_log_channel_id?: string | null;
  role_log_channel_id?: string | null;
  moderation_log_channel_id?: string | null;
  server_log_channel_id?: string | null;
  invite_log_channel_id?: string | null;
  anti_raid_enabled?: boolean;
  anti_nuke_enabled?: boolean;
  verification_enabled?: boolean;
  verification_role_id?: string | null;
  verification_channel_id?: string | null;
  autorole_enabled?: boolean;
  autorole_id?: string | null;
  autorole_delay?: number;
  ticket_enabled?: boolean;
  ticket_category_id?: string | null;
  ticket_support_role_id?: string | null;
  ticket_log_channel_id?: string | null;
  stats_enabled?: boolean;
  member_count_channel_id?: string | null;
  bot_count_channel_id?: string | null;
  channel_count_channel_id?: string | null;
  economy_enabled?: boolean;
  currency_name?: string | null;
  daily_amount?: number;
  reaction_roles_enabled?: boolean;
  custom_commands_enabled?: boolean;
  ai_enabled?: boolean;
  ai_channel_id?: string | null;
  music_enabled?: boolean;
  default_volume?: number;
  audit_enabled?: boolean;
  audit_channel_id?: string | null;
}

interface Guild {
  id: string;
  name: string;
  icon?: string | null;
  member_count?: number;
  channel_count?: number;
  bot_in_server?: boolean;
  hasBot?: boolean;
}

interface Channel {
  id: string;
  name: string;
  type: number;
}

interface Role {
  id: string;
  name: string;
  color: number;
  position: number;
  managed: boolean;
}

export function SimpleDashboard() {
  const [selectedGuildId, setSelectedGuildId] = useState<string>("");
  const [config, setConfig] = useState<BotConfig | null>(null);
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  // Get user data
  const { data: user } = useQuery({
    queryKey: ["/api/auth/user"],
    retry: false,
  });

  const { data: botStatus, isLoading } = useQuery<BotStatus>({
    queryKey: ['/api/bot/status'],
    refetchInterval: 15000,
  });

  // Fetch bot guilds
  const { data: guilds, isLoading: guildsLoading } = useQuery<Guild[]>({
    queryKey: ["/api/bot/guilds"],
    retry: false,
  });

  // Debug guild data
  console.log('Guild data received:', guilds);

  // Fetch guild configuration
  const { data: guildConfig, isLoading: configLoading } = useQuery<BotConfig>({
    queryKey: ["/api/bot/config", selectedGuildId],
    enabled: !!selectedGuildId,
    retry: false,
  });

  // Fetch guild channels
  const { data: channels } = useQuery<Channel[]>({
    queryKey: ["/api/bot/channels", selectedGuildId],
    enabled: !!selectedGuildId,
    retry: false,
  });

  // Fetch guild roles
  const { data: roles } = useQuery<Role[]>({
    queryKey: ["/api/bot/roles", selectedGuildId],
    enabled: !!selectedGuildId,
    retry: false,
  });

  // Update configuration mutation
  const updateConfigMutation = useMutation({
    mutationFn: async (updates: Partial<BotConfig>) => {
      const response = await fetch(`/api/bot/config/${selectedGuildId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updates),
        credentials: "include",
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Configuration Updated",
        description: "Bot settings have been successfully updated.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/bot/config", selectedGuildId] });
    },
    onError: (error) => {
      toast({
        title: "Update Failed",
        description: `Failed to update configuration: ${error.message}`,
        variant: "destructive",
      });
    },
  });

  // Update config state when guild config changes
  useEffect(() => {
    if (guildConfig) {
      setConfig(guildConfig);
    }
  }, [guildConfig]);

  const handleConfigChange = (field: keyof BotConfig, value: any) => {
    if (!config) return;
    
    const updatedConfig = { ...config, [field]: value };
    setConfig(updatedConfig);
    
    // Auto-save the change
    updateConfigMutation.mutate({ [field]: value });
  };

  const textChannels = channels?.filter(ch => ch.type === 0) || [];
  const categories = channels?.filter(ch => ch.type === 4) || [];
  const nonManagedRoles = roles?.filter(role => !role.managed) || [];

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
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-6">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">
              NexGuard Security Dashboard
            </span>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Monitor your Discord bot, manage server configurations, and view real-time security analytics
          </p>
        </div>

        {/* User Info & Logout */}
        <div className="flex justify-between items-center mb-8 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold">
                {(user as any)?.username?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <p className="text-white font-medium">{(user as any)?.username}</p>
              <p className="text-gray-400 text-sm">Administrator</p>
            </div>
          </div>
          <button
            onClick={() => window.location.href = '/api/logout'}
            className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-md transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Logout
          </button>
        </div>

        {/* Main Dashboard Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 bg-gray-800/50 border-gray-700">
            <TabsTrigger value="overview" className="data-[state=active]:bg-cyan-600">Overview</TabsTrigger>
            <TabsTrigger value="configuration" className="data-[state=active]:bg-purple-600">Server Configuration</TabsTrigger>
            <TabsTrigger value="analytics" className="data-[state=active]:bg-green-600">Analytics</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
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

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
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

        {/* Dashboard Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gray-800/50 border-gray-700 hover:border-cyan-500 transition-colors cursor-pointer">
            <CardHeader className="text-center">
              <Settings className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
              <CardTitle className="text-white">Bot Configuration</CardTitle>
            </CardHeader>
            <CardContent className="text-gray-300 text-center">
              <p className="text-sm mb-4">Configure automod, logging, welcome messages, and other bot settings</p>
              <Button className="bg-cyan-600 hover:bg-cyan-700">
                Manage Settings
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700 hover:border-purple-500 transition-colors cursor-pointer">
            <CardHeader className="text-center">
              <BarChart3 className="w-8 h-8 text-purple-400 mx-auto mb-2" />
              <CardTitle className="text-white">Analytics</CardTitle>
            </CardHeader>
            <CardContent className="text-gray-300 text-center">
              <p className="text-sm mb-4">View detailed analytics, command usage, and server statistics</p>
              <Button className="bg-purple-600 hover:bg-purple-700">
                View Analytics
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700 hover:border-green-500 transition-colors cursor-pointer">
            <CardHeader className="text-center">
              <MessageSquare className="w-8 h-8 text-green-400 mx-auto mb-2" />
              <CardTitle className="text-white">Ticket System</CardTitle>
            </CardHeader>
            <CardContent className="text-gray-300 text-center">
              <p className="text-sm mb-4">Manage support tickets and user inquiries across all servers</p>
              <Button className="bg-green-600 hover:bg-green-700">
                Manage Tickets
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Commands Executed Today</CardTitle>
              <Zap className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">1,247</div>
              <p className="text-xs text-gray-400">
                +12% from yesterday
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Active Tickets</CardTitle>
              <Clock className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">23</div>
              <p className="text-xs text-gray-400">
                Across all servers
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Threats Blocked</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">156</div>
              <p className="text-xs text-gray-400">
                This week
              </p>
            </CardContent>
          </Card>
            </div>
          </TabsContent>

          {/* Server Configuration Tab */}
          <TabsContent value="configuration">
            <div className="space-y-6">
              {/* Server Selection */}
              <Card className="bg-gray-800/50 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <Settings className="h-5 w-5" />
                    <span>Server Configuration</span>
                  </CardTitle>
                  <CardDescription className="text-gray-300">Select a Discord server to configure bot settings</CardDescription>
                </CardHeader>
                <CardContent>
                  <Select value={selectedGuildId} onValueChange={setSelectedGuildId}>
                    <SelectTrigger className="w-full bg-gray-700 border-gray-600 text-white">
                      <SelectValue placeholder="Choose a Discord server..." />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-700 border-gray-600">
                      {guilds?.map((guild) => (
                        <SelectItem key={guild.id} value={guild.id} className="text-white">
                          <div className="flex items-center justify-between w-full">
                            <div className="flex items-center space-x-2">
                              <span>{guild.name}</span>
                              <Badge variant="outline" className="text-gray-300">{guild.member_count} members</Badge>
                            </div>
                            {(guild.bot_in_server || guild.hasBot) ? (
                              <Badge className="bg-green-600 text-white text-xs">Bot Active</Badge>
                            ) : (
                              <Badge variant="destructive" className="text-xs">No Bot</Badge>
                            )}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </CardContent>
              </Card>

              {/* Bot Invite Message for servers without bot */}
              {selectedGuildId && guilds && !(guilds.find(g => g.id === selectedGuildId)?.bot_in_server || guilds.find(g => g.id === selectedGuildId)?.hasBot) && (
                <Card className="bg-yellow-900/20 border-yellow-600/50">
                  <CardHeader>
                    <CardTitle className="text-yellow-400 flex items-center space-x-2">
                      <AlertTriangle className="h-5 w-5" />
                      <span>Bot Not Installed</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-yellow-300 mb-4">
                      NexGuard bot is not installed in this server yet. You need to invite the bot first to configure settings.
                    </p>
                    <Button 
                      onClick={() => window.open('https://discord.com/oauth2/authorize?client_id=1389775821794705429&permissions=8&scope=bot%20applications.commands', '_blank')}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      Invite NexGuard Bot
                    </Button>
                  </CardContent>
                </Card>
              )}

              {/* Configuration Settings */}
              {selectedGuildId && config && (guilds?.find(g => g.id === selectedGuildId)?.bot_in_server || guilds?.find(g => g.id === selectedGuildId)?.hasBot) && (
                <Tabs defaultValue="general" className="space-y-6">
                  <TabsList className="grid w-full grid-cols-6 bg-gray-800/50 border-gray-700">
                    <TabsTrigger value="general">General</TabsTrigger>
                    <TabsTrigger value="moderation">Moderation</TabsTrigger>
                    <TabsTrigger value="automod">AutoMod</TabsTrigger>
                    <TabsTrigger value="welcome">Welcome</TabsTrigger>
                    <TabsTrigger value="logging">Logging</TabsTrigger>
                    <TabsTrigger value="features">Features</TabsTrigger>
                  </TabsList>

                  {/* General Settings */}
                  <TabsContent value="general">
                    <Card className="bg-gray-800/50 border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-white flex items-center space-x-2">
                          <Settings className="h-5 w-5" />
                          <span>General Settings</span>
                        </CardTitle>
                        <CardDescription className="text-gray-300">Basic bot configuration for {config.guild_name}</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="space-y-2">
                            <Label htmlFor="prefix" className="text-white">Command Prefix</Label>
                            <Input
                              id="prefix"
                              value={config.prefix || "!"}
                              onChange={(e) => handleConfigChange("prefix", e.target.value)}
                              placeholder="!"
                              className="bg-gray-700 border-gray-600 text-white"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="language" className="text-white">Language</Label>
                            <Select value={config.language || "en"} onValueChange={(value) => handleConfigChange("language", value)}>
                              <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-gray-700 border-gray-600">
                                <SelectItem value="en" className="text-white">English</SelectItem>
                                <SelectItem value="es" className="text-white">Spanish</SelectItem>
                                <SelectItem value="fr" className="text-white">French</SelectItem>
                                <SelectItem value="de" className="text-white">German</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  {/* AutoMod Settings */}
                  <TabsContent value="automod">
                    <Card className="bg-gray-800/50 border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-white flex items-center space-x-2">
                          <Zap className="h-5 w-5" />
                          <span>AutoMod Settings</span>
                        </CardTitle>
                        <CardDescription className="text-gray-300">Configure automatic moderation features</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-6">
                        <div className="flex items-center space-x-2">
                          <Switch
                            checked={config.automod_enabled || false}
                            onCheckedChange={(checked) => handleConfigChange("automod_enabled", checked)}
                          />
                          <Label className="text-white">Enable AutoMod</Label>
                        </div>

                        <Separator className="bg-gray-600" />

                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={config.spam_detection || false}
                              onCheckedChange={(checked) => handleConfigChange("spam_detection", checked)}
                              disabled={!config.automod_enabled}
                            />
                            <Label className="text-white">Spam Detection</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={config.caps_detection || false}
                              onCheckedChange={(checked) => handleConfigChange("caps_detection", checked)}
                              disabled={!config.automod_enabled}
                            />
                            <Label className="text-white">Caps Detection</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={config.link_detection || false}
                              onCheckedChange={(checked) => handleConfigChange("link_detection", checked)}
                              disabled={!config.automod_enabled}
                            />
                            <Label className="text-white">Link Detection</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={config.invite_detection || false}
                              onCheckedChange={(checked) => handleConfigChange("invite_detection", checked)}
                              disabled={!config.automod_enabled}
                            />
                            <Label className="text-white">Invite Detection</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={config.bad_words_detection || false}
                              onCheckedChange={(checked) => handleConfigChange("bad_words_detection", checked)}
                              disabled={!config.automod_enabled}
                            />
                            <Label className="text-white">Bad Words</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={config.mention_spam_detection || false}
                              onCheckedChange={(checked) => handleConfigChange("mention_spam_detection", checked)}
                              disabled={!config.automod_enabled}
                            />
                            <Label className="text-white">Mention Spam</Label>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="space-y-2">
                            <Label className="text-white">AutoMod Action</Label>
                            <Select 
                              value={config.automod_action || "warn"} 
                              onValueChange={(value) => handleConfigChange("automod_action", value)}
                              disabled={!config.automod_enabled}
                            >
                              <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-gray-700 border-gray-600">
                                <SelectItem value="warn" className="text-white">Warn</SelectItem>
                                <SelectItem value="mute" className="text-white">Mute</SelectItem>
                                <SelectItem value="kick" className="text-white">Kick</SelectItem>
                                <SelectItem value="ban" className="text-white">Ban</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label className="text-white">Violation Threshold</Label>
                            <Input
                              type="number"
                              value={config.automod_threshold || 3}
                              onChange={(e) => handleConfigChange("automod_threshold", parseInt(e.target.value))}
                              disabled={!config.automod_enabled}
                              min={1}
                              max={10}
                              className="bg-gray-700 border-gray-600 text-white"
                            />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  {/* Feature Settings */}
                  <TabsContent value="features">
                    <Card className="bg-gray-800/50 border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-white flex items-center space-x-2">
                          <Bot className="h-5 w-5" />
                          <span>Feature Settings</span>
                        </CardTitle>
                        <CardDescription className="text-gray-300">Enable and configure additional bot features</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={config.ticket_enabled || false}
                              onCheckedChange={(checked) => handleConfigChange("ticket_enabled", checked)}
                            />
                            <Label className="text-white">Ticket System</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={config.stats_enabled || false}
                              onCheckedChange={(checked) => handleConfigChange("stats_enabled", checked)}
                            />
                            <Label className="text-white">Server Stats</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={config.economy_enabled || false}
                              onCheckedChange={(checked) => handleConfigChange("economy_enabled", checked)}
                            />
                            <Label className="text-white">Economy System</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={config.reaction_roles_enabled || false}
                              onCheckedChange={(checked) => handleConfigChange("reaction_roles_enabled", checked)}
                            />
                            <Label className="text-white">Reaction Roles</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={config.custom_commands_enabled || false}
                              onCheckedChange={(checked) => handleConfigChange("custom_commands_enabled", checked)}
                            />
                            <Label className="text-white">Custom Commands</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={config.ai_enabled || false}
                              onCheckedChange={(checked) => handleConfigChange("ai_enabled", checked)}
                            />
                            <Label className="text-white">AI Assistant</Label>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>
                </Tabs>
              )}

              {configLoading && selectedGuildId && (
                <Card className="bg-gray-800/50 border-gray-700">
                  <CardContent className="flex items-center justify-center h-32">
                    <div className="text-center">
                      <Settings className="h-6 w-6 animate-spin mx-auto mb-2 text-white" />
                      <p className="text-white">Loading server configuration...</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics">
            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Server Analytics</span>
                </CardTitle>
                <CardDescription className="text-gray-300">Coming soon - detailed analytics and insights</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-400">Advanced analytics features are being developed</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}