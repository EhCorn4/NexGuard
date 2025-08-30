import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { Settings, Shield, MessageCircle, Users, BarChart3, Bot, Zap } from "lucide-react";

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

export default function ServerManagement() {
  const [selectedGuildId, setSelectedGuildId] = useState<string>("");
  const [config, setConfig] = useState<BotConfig | null>(null);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch bot guilds
  const { data: guilds, isLoading: guildsLoading } = useQuery<Guild[]>({
    queryKey: ["/api/bot/guilds"],
    retry: false,
  });

  // Fetch guild configuration
  const { data: guildConfig, isLoading: configLoading } = useQuery<BotConfig>({
    queryKey: ["/api/bot/config", selectedGuildId],
    enabled: !!selectedGuildId,
    retry: false,
  });

  // Fetch guild channels
  const { data: channels, isLoading: channelsLoading, error: channelsError } = useQuery<Channel[]>({
    queryKey: ["/api/bot/channels", selectedGuildId],
    enabled: !!selectedGuildId,
    retry: false,
  });

  // Fetch guild roles
  const { data: roles, isLoading: rolesLoading, error: rolesError } = useQuery<Role[]>({
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

  if (guildsLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Bot className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p>Loading Discord servers...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!guilds || guilds.length === 0) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>No Servers Found</CardTitle>
            <CardDescription>
              NexGuard bot is not currently in any Discord servers or you don't have permission to manage them.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center space-x-4">
        <Settings className="h-8 w-8" />
        <div>
          <h1 className="text-3xl font-bold">Server Management</h1>
          <p className="text-muted-foreground">Configure NexGuard bot settings for your Discord servers</p>
        </div>
      </div>

      {/* Server Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Select Discord Server</CardTitle>
          <CardDescription>Choose a server to configure bot settings</CardDescription>
        </CardHeader>
        <CardContent>
          <Select value={selectedGuildId} onValueChange={setSelectedGuildId}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Choose a Discord server..." />
            </SelectTrigger>
            <SelectContent>
              {guilds.map((guild) => (
                <SelectItem key={guild.id} value={guild.id}>
                  <div className="flex items-center space-x-2">
                    <span>{guild.name}</span>
                    <Badge variant="outline">{guild.member_count} members</Badge>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Configuration Tabs */}
      {selectedGuildId && config && (
        <Tabs defaultValue="general" className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="moderation">Moderation</TabsTrigger>
            <TabsTrigger value="automod">AutoMod</TabsTrigger>
            <TabsTrigger value="welcome">Welcome</TabsTrigger>
            <TabsTrigger value="logging">Logging</TabsTrigger>
            <TabsTrigger value="features">Features</TabsTrigger>
          </TabsList>

          {/* General Settings */}
          <TabsContent value="general">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="h-5 w-5" />
                  <span>General Settings</span>
                </CardTitle>
                <CardDescription>Basic bot configuration for {config.guild_name}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="prefix">Command Prefix</Label>
                    <Input
                      id="prefix"
                      value={config.prefix || "!"}
                      onChange={(e) => handleConfigChange("prefix", e.target.value)}
                      placeholder="!"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="language">Language</Label>
                    <Select value={config.language || "en"} onValueChange={(value) => handleConfigChange("language", value)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="es">Spanish</SelectItem>
                        <SelectItem value="fr">French</SelectItem>
                        <SelectItem value="de">German</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="timezone">Timezone</Label>
                    <Select value={config.timezone || "UTC"} onValueChange={(value) => handleConfigChange("timezone", value)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="UTC">UTC</SelectItem>
                        <SelectItem value="America/New_York">Eastern Time</SelectItem>
                        <SelectItem value="America/Chicago">Central Time</SelectItem>
                        <SelectItem value="America/Denver">Mountain Time</SelectItem>
                        <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                        <SelectItem value="Europe/London">London</SelectItem>
                        <SelectItem value="Europe/Paris">Paris</SelectItem>
                        <SelectItem value="Asia/Tokyo">Tokyo</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Moderation Settings */}
          <TabsContent value="moderation">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="h-5 w-5" />
                  <span>Moderation Settings</span>
                </CardTitle>
                <CardDescription>Configure moderation tools and roles</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={config.moderation_enabled || false}
                    onCheckedChange={(checked) => handleConfigChange("moderation_enabled", checked)}
                  />
                  <Label>Enable Moderation Features</Label>
                </div>

                <Separator />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>Moderator Role</Label>
                    <Select value={config.mod_role_id || ""} onValueChange={(value) => handleConfigChange("mod_role_id", value || null)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select moderator role..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {nonManagedRoles.map((role) => (
                          <SelectItem key={role.id} value={role.id}>
                            {role.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Administrator Role</Label>
                    <Select value={config.admin_role_id || ""} onValueChange={(value) => handleConfigChange("admin_role_id", value || null)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select admin role..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {nonManagedRoles.map((role) => (
                          <SelectItem key={role.id} value={role.id}>
                            {role.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Mute Role</Label>
                    <Select value={config.mute_role_id || ""} onValueChange={(value) => handleConfigChange("mute_role_id", value || null)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select mute role..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {nonManagedRoles.map((role) => (
                          <SelectItem key={role.id} value={role.id}>
                            {role.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.anti_raid_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("anti_raid_enabled", checked)}
                    />
                    <Label>Anti-Raid Protection</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.anti_nuke_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("anti_nuke_enabled", checked)}
                    />
                    <Label>Anti-Nuke Protection</Label>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* AutoMod Settings */}
          <TabsContent value="automod">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="h-5 w-5" />
                  <span>AutoMod Settings</span>
                </CardTitle>
                <CardDescription>Configure automatic moderation features</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={config.automod_enabled || false}
                    onCheckedChange={(checked) => handleConfigChange("automod_enabled", checked)}
                  />
                  <Label>Enable AutoMod</Label>
                </div>

                <Separator />

                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.spam_detection || false}
                      onCheckedChange={(checked) => handleConfigChange("spam_detection", checked)}
                      disabled={!config.automod_enabled}
                    />
                    <Label>Spam Detection</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.caps_detection || false}
                      onCheckedChange={(checked) => handleConfigChange("caps_detection", checked)}
                      disabled={!config.automod_enabled}
                    />
                    <Label>Caps Detection</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.link_detection || false}
                      onCheckedChange={(checked) => handleConfigChange("link_detection", checked)}
                      disabled={!config.automod_enabled}
                    />
                    <Label>Link Detection</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.invite_detection || false}
                      onCheckedChange={(checked) => handleConfigChange("invite_detection", checked)}
                      disabled={!config.automod_enabled}
                    />
                    <Label>Invite Detection</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.bad_words_detection || false}
                      onCheckedChange={(checked) => handleConfigChange("bad_words_detection", checked)}
                      disabled={!config.automod_enabled}
                    />
                    <Label>Bad Words</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.mention_spam_detection || false}
                      onCheckedChange={(checked) => handleConfigChange("mention_spam_detection", checked)}
                      disabled={!config.automod_enabled}
                    />
                    <Label>Mention Spam</Label>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>AutoMod Action</Label>
                    <Select 
                      value={config.automod_action || "warn"} 
                      onValueChange={(value) => handleConfigChange("automod_action", value)}
                      disabled={!config.automod_enabled}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="warn">Warn</SelectItem>
                        <SelectItem value="mute">Mute</SelectItem>
                        <SelectItem value="kick">Kick</SelectItem>
                        <SelectItem value="ban">Ban</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Violation Threshold</Label>
                    <Input
                      type="number"
                      value={config.automod_threshold || 3}
                      onChange={(e) => handleConfigChange("automod_threshold", parseInt(e.target.value))}
                      disabled={!config.automod_enabled}
                      min={1}
                      max={10}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Welcome Settings */}
          <TabsContent value="welcome">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="h-5 w-5" />
                  <span>Welcome & Goodbye Settings</span>
                </CardTitle>
                <CardDescription>Configure member join and leave messages</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Welcome Settings */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Welcome System</h3>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.welcome_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("welcome_enabled", checked)}
                    />
                    <Label>Enable Welcome Messages</Label>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label>Welcome Channel</Label>
                      <Select value={config.welcome_channel_id || ""} onValueChange={(value) => handleConfigChange("welcome_channel_id", value || null)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select channel..." />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">None</SelectItem>
                          {textChannels.map((channel) => (
                            <SelectItem key={channel.id} value={channel.id}>
                              #{channel.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Welcome Role</Label>
                      <Select value={config.welcome_role_id || ""} onValueChange={(value) => handleConfigChange("welcome_role_id", value || null)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select role..." />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">None</SelectItem>
                          {nonManagedRoles.map((role) => (
                            <SelectItem key={role.id} value={role.id}>
                              {role.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Welcome Message</Label>
                    <Textarea
                      value={config.welcome_message || ""}
                      onChange={(e) => handleConfigChange("welcome_message", e.target.value)}
                      placeholder="Welcome {user} to {server}! We hope you enjoy your stay."
                      rows={3}
                    />
                    <p className="text-sm text-muted-foreground">
                      Use {"{user}"} for user mention and {"{server}"} for server name
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center space-x-2">
                      <Switch
                        checked={config.welcome_embed_enabled || false}
                        onCheckedChange={(checked) => handleConfigChange("welcome_embed_enabled", checked)}
                      />
                      <Label>Rich Embed</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Switch
                        checked={config.welcome_dm_enabled || false}
                        onCheckedChange={(checked) => handleConfigChange("welcome_dm_enabled", checked)}
                      />
                      <Label>Send DM</Label>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Goodbye Settings */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Goodbye System</h3>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.goodbye_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("goodbye_enabled", checked)}
                    />
                    <Label>Enable Goodbye Messages</Label>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label>Goodbye Channel</Label>
                      <Select value={config.goodbye_channel_id || ""} onValueChange={(value) => handleConfigChange("goodbye_channel_id", value || null)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select channel..." />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">None</SelectItem>
                          {textChannels.map((channel) => (
                            <SelectItem key={channel.id} value={channel.id}>
                              #{channel.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Goodbye Message</Label>
                    <Textarea
                      value={config.goodbye_message || ""}
                      onChange={(e) => handleConfigChange("goodbye_message", e.target.value)}
                      placeholder="Goodbye {user}, we'll miss you!"
                      rows={3}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Logging Settings */}
          <TabsContent value="logging">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Logging Settings</span>
                </CardTitle>
                <CardDescription>Configure event logging channels</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {(channelsLoading || rolesLoading) ? (
                  <div className="flex items-center justify-center h-32">
                    <div className="text-center">
                      <Settings className="h-6 w-6 animate-spin mx-auto mb-2" />
                      <p>Loading channels and roles...</p>
                    </div>
                  </div>
                ) : (channelsError || rolesError) ? (
                  <div className="text-center p-8">
                    <p className="text-red-500 mb-2">Failed to load server data</p>
                    <p className="text-sm text-muted-foreground">Please refresh the page or try selecting a different server</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>General Log Channel</Label>
                    <Select value={config.general_log_channel_id || ""} onValueChange={(value) => handleConfigChange("general_log_channel_id", value || null)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select channel..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {textChannels.map((channel) => (
                          <SelectItem key={channel.id} value={channel.id}>
                            #{channel.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Member Log Channel</Label>
                    <Select value={config.member_log_channel_id || ""} onValueChange={(value) => handleConfigChange("member_log_channel_id", value || null)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select channel..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {textChannels.map((channel) => (
                          <SelectItem key={channel.id} value={channel.id}>
                            #{channel.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Message Log Channel</Label>
                    <Select value={config.message_log_channel_id || ""} onValueChange={(value) => handleConfigChange("message_log_channel_id", value || null)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select channel..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {textChannels.map((channel) => (
                          <SelectItem key={channel.id} value={channel.id}>
                            #{channel.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Voice Log Channel</Label>
                    <Select value={config.voice_log_channel_id || ""} onValueChange={(value) => handleConfigChange("voice_log_channel_id", value || null)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select channel..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {textChannels.map((channel) => (
                          <SelectItem key={channel.id} value={channel.id}>
                            #{channel.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Channel Log Channel</Label>
                    <Select value={config.channel_log_channel_id || ""} onValueChange={(value) => handleConfigChange("channel_log_channel_id", value || null)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select channel..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {textChannels.map((channel) => (
                          <SelectItem key={channel.id} value={channel.id}>
                            #{channel.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Role Log Channel</Label>
                    <Select value={config.role_log_channel_id || ""} onValueChange={(value) => handleConfigChange("role_log_channel_id", value || null)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select channel..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {textChannels.map((channel) => (
                          <SelectItem key={channel.id} value={channel.id}>
                            #{channel.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Moderation Log Channel</Label>
                    <Select value={config.moderation_log_channel_id || ""} onValueChange={(value) => handleConfigChange("moderation_log_channel_id", value || null)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select channel..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {textChannels.map((channel) => (
                          <SelectItem key={channel.id} value={channel.id}>
                            #{channel.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Server Log Channel</Label>
                    <Select value={config.server_log_channel_id || ""} onValueChange={(value) => handleConfigChange("server_log_channel_id", value || null)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select channel..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {textChannels.map((channel) => (
                          <SelectItem key={channel.id} value={channel.id}>
                            #{channel.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Feature Settings */}
          <TabsContent value="features">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Bot className="h-5 w-5" />
                  <span>Feature Settings</span>
                </CardTitle>
                <CardDescription>Enable and configure additional bot features</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.ticket_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("ticket_enabled", checked)}
                    />
                    <Label>Ticket System</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.stats_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("stats_enabled", checked)}
                    />
                    <Label>Server Stats</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.economy_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("economy_enabled", checked)}
                    />
                    <Label>Economy System</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.reaction_roles_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("reaction_roles_enabled", checked)}
                    />
                    <Label>Reaction Roles</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.custom_commands_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("custom_commands_enabled", checked)}
                    />
                    <Label>Custom Commands</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.ai_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("ai_enabled", checked)}
                    />
                    <Label>AI Assistant</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.music_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("music_enabled", checked)}
                    />
                    <Label>Music Player</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.autorole_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("autorole_enabled", checked)}
                    />
                    <Label>Auto Role</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={config.verification_enabled || false}
                      onCheckedChange={(checked) => handleConfigChange("verification_enabled", checked)}
                    />
                    <Label>Verification</Label>
                  </div>
                </div>

                <Separator />

                {/* Feature-specific settings */}
                {config.ticket_enabled && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Ticket System Configuration</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label>Ticket Category</Label>
                        <Select value={config.ticket_category_id || ""} onValueChange={(value) => handleConfigChange("ticket_category_id", value || null)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select category..." />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">None</SelectItem>
                            {categories.map((category) => (
                              <SelectItem key={category.id} value={category.id}>
                                {category.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Support Role</Label>
                        <Select value={config.ticket_support_role_id || ""} onValueChange={(value) => handleConfigChange("ticket_support_role_id", value || null)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select role..." />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">None</SelectItem>
                            {nonManagedRoles.map((role) => (
                              <SelectItem key={role.id} value={role.id}>
                                {role.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>
                )}

                {config.economy_enabled && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Economy Configuration</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label>Currency Name</Label>
                        <Input
                          value={config.currency_name || "coins"}
                          onChange={(e) => handleConfigChange("currency_name", e.target.value)}
                          placeholder="coins"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Daily Amount</Label>
                        <Input
                          type="number"
                          value={config.daily_amount || 100}
                          onChange={(e) => handleConfigChange("daily_amount", parseInt(e.target.value))}
                          min={1}
                          max={10000}
                        />
                      </div>
                    </div>
                  </div>
                )}

                {config.autorole_enabled && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Auto Role Configuration</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label>Auto Role</Label>
                        <Select value={config.autorole_id || ""} onValueChange={(value) => handleConfigChange("autorole_id", value || null)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select role..." />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">None</SelectItem>
                            {nonManagedRoles.map((role) => (
                              <SelectItem key={role.id} value={role.id}>
                                {role.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Delay (seconds)</Label>
                        <Input
                          type="number"
                          value={config.autorole_delay || 0}
                          onChange={(e) => handleConfigChange("autorole_delay", parseInt(e.target.value))}
                          min={0}
                          max={3600}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {configLoading && selectedGuildId && (
        <Card>
          <CardContent className="flex items-center justify-center h-32">
            <div className="text-center">
              <Settings className="h-6 w-6 animate-spin mx-auto mb-2" />
              <p>Loading server configuration...</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}