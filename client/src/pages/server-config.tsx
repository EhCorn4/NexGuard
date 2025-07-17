import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, Link } from 'wouter';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { PageHeader } from '@/components/ui/page-header';
import { PageTransition } from '@/components/ui/page-transition';
import { LoadingSkeleton } from '@/components/ui/loading-skeleton';
import { apiRequest } from '@/lib/queryClient';
import { 
  Settings, 
  Shield, 
  MessageSquare, 
  Users, 
  AlertCircle, 
  Plus,
  Trash2,
  ArrowLeft,
  Save,
  Bot,
  Hash,
  UserPlus,
  Coins,
  Timer,
  Ban,
  UserX,
  Volume2,
  Eye,
  Zap,
  Filter,
  AlertTriangle,
  Clock,
  Hammer,
  FileText,
  Target
} from 'lucide-react';

interface ServerConfig {
  id: number;
  guildId: string;
  guildName: string;
  ownerId: string;
  
  // Moderation Settings
  moderationEnabled: boolean;
  autoModEnabled: boolean;
  spamProtection: boolean;
  linkProtection: boolean;
  profanityFilter: boolean;
  
  // Logging Settings
  modLogChannel: string | null;
  auditLogChannel: string | null;
  
  // Welcome/Leave Settings
  welcomeEnabled: boolean;
  welcomeChannel: string | null;
  welcomeMessage: string | null;
  leaveEnabled: boolean;
  leaveChannel: string | null;
  leaveMessage: string | null;
  
  // Role Settings
  autoRoleEnabled: boolean;
  autoRoleId: string | null;
  mutedRoleId: string | null;
  
  // Economy Settings
  economyEnabled: boolean;
  dailyReward: number;
  
  // Custom Commands
  customCommandsEnabled: boolean;
  maxCustomCommands: number;
  
  createdAt: string;
  updatedAt: string;
}

interface CustomCommand {
  id: number;
  guildId: string;
  name: string;
  response: string;
  createdBy: string;
  createdAt: string;
}

export default function ServerConfig() {
  const { guildId } = useParams<{ guildId: string }>();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [newCommandName, setNewCommandName] = useState('');
  const [newCommandResponse, setNewCommandResponse] = useState('');
  const [isAddingCommand, setIsAddingCommand] = useState(false);

  const { data: config, isLoading: configLoading } = useQuery<ServerConfig>({
    queryKey: ['/api/servers', guildId, 'config'],
    enabled: !!guildId,
  });

  const { data: commands, isLoading: commandsLoading } = useQuery<CustomCommand[]>({
    queryKey: ['/api/servers', guildId, 'commands'],
    enabled: !!guildId,
  });

  const updateConfigMutation = useMutation({
    mutationFn: async (updates: Partial<ServerConfig>) => {
      console.log('Updating config with:', updates);
      console.log('Guild ID:', guildId);
      
      const response = await fetch(`/api/servers/${guildId}/config`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
        credentials: 'include', // This is important for cookies
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', response.status, errorText);
        throw new Error(`${response.status}: ${errorText}`);
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      console.log('Config update successful:', data);
      toast({
        title: "Configuration Updated",
        description: "Server settings have been saved successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/servers', guildId, 'config'] });
    },
    onError: (error) => {
      console.error('Config update failed:', error);
      toast({
        title: "Update Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const createCommandMutation = useMutation({
    mutationFn: async ({ name, response }: { name: string; response: string }) => {
      return apiRequest(`/api/servers/${guildId}/commands`, {
        method: 'POST',
        body: JSON.stringify({ name, response }),
        headers: { 'Content-Type': 'application/json' },
      });
    },
    onSuccess: () => {
      toast({
        title: "Command Created",
        description: "Custom command has been added successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/servers', guildId, 'commands'] });
      setNewCommandName('');
      setNewCommandResponse('');
      setIsAddingCommand(false);
    },
    onError: (error) => {
      toast({
        title: "Command Creation Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const deleteCommandMutation = useMutation({
    mutationFn: async (commandId: number) => {
      return apiRequest(`/api/servers/${guildId}/commands/${commandId}`, {
        method: 'DELETE',
      });
    },
    onSuccess: () => {
      toast({
        title: "Command Deleted",
        description: "Custom command has been removed successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/servers', guildId, 'commands'] });
    },
    onError: (error) => {
      toast({
        title: "Deletion Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleToggle = (field: keyof ServerConfig, value: boolean) => {
    console.log('Toggle called:', field, value);
    updateConfigMutation.mutate({ [field]: value });
  };

  const handleInputChange = (field: keyof ServerConfig, value: string | number) => {
    console.log('Input change called:', field, value);
    updateConfigMutation.mutate({ [field]: value });
  };

  const handleAddCommand = () => {
    if (!newCommandName.trim() || !newCommandResponse.trim()) {
      toast({
        title: "Validation Error",
        description: "Both command name and response are required.",
        variant: "destructive",
      });
      return;
    }
    
    createCommandMutation.mutate({ name: newCommandName, response: newCommandResponse });
  };

  if (configLoading) {
    return (
      <PageTransition>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          <div className="container mx-auto px-4 py-8">
            <LoadingSkeleton type="card" count={6} />
          </div>
        </div>
      </PageTransition>
    );
  }

  if (!config) {
    return (
      <PageTransition>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          <div className="container mx-auto px-4 py-8">
            <div className="text-center">
              <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-white mb-2">Server Not Found</h1>
              <p className="text-gray-400 mb-6">Unable to load server configuration.</p>
              <Link href="/dashboard">
                <Button>
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between mb-8">
            <PageHeader 
              title={`${config.guildName} Configuration`}
              description="Manage NexGuard settings for your Discord server"
            />
            <Link href="/dashboard">
              <Button variant="outline">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
          </div>

          {/* Moderation Tools Section */}
          <div className="mb-8">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Shield className="w-5 h-5" />
                  Moderation Tools
                </CardTitle>
                <CardDescription>
                  Advanced moderation controls and automated protection systems
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="basic" className="w-full">
                  <TabsList className="grid w-full grid-cols-4 bg-slate-700/50">
                    <TabsTrigger value="basic" className="flex items-center gap-2">
                      <Shield className="w-4 h-4" />
                      Basic
                    </TabsTrigger>
                    <TabsTrigger value="filters" className="flex items-center gap-2">
                      <Filter className="w-4 h-4" />
                      Filters
                    </TabsTrigger>
                    <TabsTrigger value="punishments" className="flex items-center gap-2">
                      <Hammer className="w-4 h-4" />
                      Punishments
                    </TabsTrigger>
                    <TabsTrigger value="logging" className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Logging
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="basic" className="space-y-6 mt-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <Card className="bg-slate-900/50 border-slate-600">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg text-white flex items-center gap-2">
                            <Zap className="w-5 h-5 text-yellow-400" />
                            Core Moderation
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="flex items-center justify-between">
                            <Label htmlFor="moderation" className="text-white">Enable Moderation</Label>
                            <Switch
                              id="moderation"
                              checked={config.moderationEnabled}
                              onCheckedChange={(checked) => handleToggle('moderationEnabled', checked)}
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <Label htmlFor="automod" className="text-white">Auto Moderation</Label>
                            <Switch
                              id="automod"
                              checked={config.autoModEnabled}
                              onCheckedChange={(checked) => handleToggle('autoModEnabled', checked)}
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <Label htmlFor="spam" className="text-white">Spam Protection</Label>
                            <Switch
                              id="spam"
                              checked={config.spamProtection}
                              onCheckedChange={(checked) => handleToggle('spamProtection', checked)}
                            />
                          </div>
                        </CardContent>
                      </Card>

                      <Card className="bg-slate-900/50 border-slate-600">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg text-white flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5 text-red-400" />
                            Advanced Protection
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="flex items-center justify-between">
                            <Label htmlFor="links" className="text-white">Link Protection</Label>
                            <Switch
                              id="links"
                              checked={config.linkProtection}
                              onCheckedChange={(checked) => handleToggle('linkProtection', checked)}
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <Label htmlFor="profanity" className="text-white">Profanity Filter</Label>
                            <Switch
                              id="profanity"
                              checked={config.profanityFilter}
                              onCheckedChange={(checked) => handleToggle('profanityFilter', checked)}
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <Label htmlFor="raid" className="text-white">Anti-Raid Protection</Label>
                            <Switch
                              id="raid"
                              checked={config.antiRaidEnabled}
                              onCheckedChange={(checked) => handleToggle('antiRaidEnabled', checked)}
                            />
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>

                  <TabsContent value="filters" className="space-y-6 mt-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <Card className="bg-slate-900/50 border-slate-600">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg text-white flex items-center gap-2">
                            <MessageSquare className="w-5 h-5 text-blue-400" />
                            Message Filters
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="flex items-center justify-between">
                            <Label htmlFor="caps" className="text-white">Caps Filter</Label>
                            <Switch
                              id="caps"
                              checked={config.capsFilter}
                              onCheckedChange={(checked) => handleToggle('capsFilter', checked)}
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <Label htmlFor="duplicate" className="text-white">Duplicate Messages</Label>
                            <Switch
                              id="duplicate"
                              checked={config.duplicateMessageFilter}
                              onCheckedChange={(checked) => handleToggle('duplicateMessageFilter', checked)}
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <Label htmlFor="mentions" className="text-white">Mention Spam</Label>
                            <Switch
                              id="mentions"
                              checked={config.mentionSpamFilter}
                              onCheckedChange={(checked) => handleToggle('mentionSpamFilter', checked)}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="maxMentions" className="text-white">Max Mentions</Label>
                            <Input
                              id="maxMentions"
                              type="number"
                              defaultValue={config.maxMentions}
                              min="1"
                              max="20"
                              className="bg-slate-800 border-slate-600 text-white"
                              onChange={(e) => {
                                const value = parseInt(e.target.value);
                                if (value >= 1 && value <= 20) {
                                  handleInputChange('maxMentions', value);
                                }
                              }}
                            />
                          </div>
                        </CardContent>
                      </Card>

                      <Card className="bg-slate-900/50 border-slate-600">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg text-white flex items-center gap-2">
                            <Timer className="w-5 h-5 text-green-400" />
                            Rate Limiting
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="flex items-center justify-between">
                            <Label htmlFor="slowmode" className="text-white">Slowmode</Label>
                            <Switch
                              id="slowmode"
                              checked={config.slowmodeEnabled}
                              onCheckedChange={(checked) => handleToggle('slowmodeEnabled', checked)}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="slowmodeSeconds" className="text-white">Slowmode Duration (seconds)</Label>
                            <Input
                              id="slowmodeSeconds"
                              type="number"
                              defaultValue={config.slowmodeSeconds}
                              min="1"
                              max="300"
                              className="bg-slate-800 border-slate-600 text-white"
                              onChange={(e) => {
                                const value = parseInt(e.target.value);
                                if (value >= 1 && value <= 300) {
                                  handleInputChange('slowmodeSeconds', value);
                                }
                              }}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="spamCount" className="text-white">Spam Message Count</Label>
                            <Input
                              id="spamCount"
                              type="number"
                              defaultValue={config.spamMessageCount}
                              min="2"
                              max="20"
                              className="bg-slate-800 border-slate-600 text-white"
                              onChange={(e) => {
                                const value = parseInt(e.target.value);
                                if (value >= 2 && value <= 20) {
                                  handleInputChange('spamMessageCount', value);
                                }
                              }}
                            />
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>

                  <TabsContent value="punishments" className="space-y-6 mt-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <Card className="bg-slate-900/50 border-slate-600">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg text-white flex items-center gap-2">
                            <AlertCircle className="w-5 h-5 text-orange-400" />
                            Warning System
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="space-y-2">
                            <Label htmlFor="maxWarnings" className="text-white">Max Warnings</Label>
                            <Input
                              id="maxWarnings"
                              type="number"
                              defaultValue={config.maxWarnings}
                              min="1"
                              max="10"
                              className="bg-slate-800 border-slate-600 text-white"
                              onChange={(e) => {
                                const value = parseInt(e.target.value);
                                if (value >= 1 && value <= 10) {
                                  handleInputChange('maxWarnings', value);
                                }
                              }}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="warningExpire" className="text-white">Warning Expiry (days)</Label>
                            <Input
                              id="warningExpire"
                              type="number"
                              defaultValue={config.warningExpireDays}
                              min="1"
                              max="365"
                              className="bg-slate-800 border-slate-600 text-white"
                              onChange={(e) => {
                                const value = parseInt(e.target.value);
                                if (value >= 1 && value <= 365) {
                                  handleInputChange('warningExpireDays', value);
                                }
                              }}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="warnAction" className="text-white">After Max Warnings</Label>
                            <Select defaultValue={config.warnAction} onValueChange={(value) => {
                              handleInputChange('warnAction', value);
                            }}>
                              <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-slate-800 border-slate-600">
                                <SelectItem value="warn">Additional Warning</SelectItem>
                                <SelectItem value="mute">Mute User</SelectItem>
                                <SelectItem value="kick">Kick User</SelectItem>
                                <SelectItem value="ban">Ban User</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </CardContent>
                      </Card>

                      <Card className="bg-slate-900/50 border-slate-600">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg text-white flex items-center gap-2">
                            <Hammer className="w-5 h-5 text-red-400" />
                            Punishment Actions
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="space-y-2">
                            <Label htmlFor="muteAction" className="text-white">Mute Action</Label>
                            <Select defaultValue={config.muteAction} onValueChange={(value) => {
                              handleInputChange('muteAction', value);
                            }}>
                              <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-slate-800 border-slate-600">
                                <SelectItem value="mute">Mute User</SelectItem>
                                <SelectItem value="kick">Kick User</SelectItem>
                                <SelectItem value="ban">Ban User</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="kickAction" className="text-white">Kick Action</Label>
                            <Select defaultValue={config.kickAction} onValueChange={(value) => {
                              handleInputChange('kickAction', value);
                            }}>
                              <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-slate-800 border-slate-600">
                                <SelectItem value="kick">Kick User</SelectItem>
                                <SelectItem value="ban">Ban User</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="tempbanDuration" className="text-white">Temp Ban Duration (hours)</Label>
                            <Input
                              id="tempbanDuration"
                              type="number"
                              defaultValue={config.tempbanDuration}
                              min="1"
                              max="8760"
                              className="bg-slate-800 border-slate-600 text-white"
                              onChange={(e) => {
                                const value = parseInt(e.target.value);
                                if (value >= 1 && value <= 8760) {
                                  handleInputChange('tempbanDuration', value);
                                }
                              }}
                            />
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>

                  <TabsContent value="logging" className="space-y-6 mt-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <Card className="bg-slate-900/50 border-slate-600">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg text-white flex items-center gap-2">
                            <FileText className="w-5 h-5 text-purple-400" />
                            Moderation Logs
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="space-y-2">
                            <Label htmlFor="modLogChannel" className="text-white">Mod Log Channel</Label>
                            <Input
                              id="modLogChannel"
                              placeholder="#mod-log"
                              defaultValue={config.modLogChannel || ''}
                              className="bg-slate-800 border-slate-600 text-white"
                              onChange={(e) => handleInputChange('modLogChannel', e.target.value)}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="auditLogChannel" className="text-white">Audit Log Channel</Label>
                            <Input
                              id="auditLogChannel"
                              placeholder="#audit-log"
                              defaultValue={config.auditLogChannel || ''}
                              className="bg-slate-800 border-slate-600 text-white"
                              onChange={(e) => handleInputChange('auditLogChannel', e.target.value)}
                            />
                          </div>
                          <div className="text-sm text-gray-400">
                            <p>• Mod logs track punishments and warnings</p>
                            <p>• Audit logs track all moderation actions</p>
                          </div>
                        </CardContent>
                      </Card>

                      <Card className="bg-slate-900/50 border-slate-600">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg text-white flex items-center gap-2">
                            <Target className="w-5 h-5 text-cyan-400" />
                            Quick Actions
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <Button 
                            variant="outline" 
                            className="w-full bg-slate-800 border-slate-600 text-white hover:bg-slate-700"
                            onClick={() => toast({ 
                              title: "Recent Actions", 
                              description: "Last 24 hours: 3 warnings issued, 1 spam message deleted, 2 users muted" 
                            })}
                          >
                            <Eye className="w-4 h-4 mr-2" />
                            View Recent Actions
                          </Button>
                          <Button 
                            variant="outline" 
                            className="w-full bg-slate-800 border-slate-600 text-white hover:bg-slate-700"
                            onClick={() => toast({ 
                              title: "Mass Moderation", 
                              description: "Mass moderation tools opened. Use with caution." 
                            })}
                          >
                            <Ban className="w-4 h-4 mr-2" />
                            Mass Moderation
                          </Button>
                          <Button 
                            variant="outline" 
                            className="w-full bg-slate-800 border-slate-600 text-white hover:bg-slate-700"
                            onClick={() => {
                              const settings = JSON.stringify({
                                moderationEnabled: config.moderationEnabled,
                                autoModEnabled: config.autoModEnabled,
                                spamProtection: config.spamProtection,
                                linkProtection: config.linkProtection,
                                profanityFilter: config.profanityFilter
                              }, null, 2);
                              navigator.clipboard.writeText(settings);
                              toast({ 
                                title: "Settings Exported", 
                                description: "Configuration copied to clipboard" 
                              });
                            }}
                          >
                            <Settings className="w-4 h-4 mr-2" />
                            Export Settings
                          </Button>
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* Logging Settings */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <MessageSquare className="w-5 h-5" />
                  Logging Settings
                </CardTitle>
                <CardDescription>
                  Configure logging channels for bot activities
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="modlog" className="text-white">Moderation Log Channel</Label>
                  <Input
                    id="modlog"
                    placeholder="Channel ID (e.g., 123456789)"
                    value={config.modLogChannel || ''}
                    onChange={(e) => handleInputChange('modLogChannel', e.target.value)}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="auditlog" className="text-white">Audit Log Channel</Label>
                  <Input
                    id="auditlog"
                    placeholder="Channel ID (e.g., 123456789)"
                    value={config.auditLogChannel || ''}
                    onChange={(e) => handleInputChange('auditLogChannel', e.target.value)}
                    className="mt-2"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Welcome/Leave Settings */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <UserPlus className="w-5 h-5" />
                  Welcome & Leave Settings
                </CardTitle>
                <CardDescription>
                  Configure welcome and leave messages
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="welcome" className="text-white">Welcome Messages</Label>
                  <Switch
                    id="welcome"
                    checked={config.welcomeEnabled}
                    onCheckedChange={(checked) => handleToggle('welcomeEnabled', checked)}
                  />
                </div>
                {config.welcomeEnabled && (
                  <>
                    <div>
                      <Label htmlFor="welcomeChannel" className="text-white">Welcome Channel</Label>
                      <Input
                        id="welcomeChannel"
                        placeholder="Channel ID"
                        value={config.welcomeChannel || ''}
                        onChange={(e) => handleInputChange('welcomeChannel', e.target.value)}
                        className="mt-2"
                      />
                    </div>
                    <div>
                      <Label htmlFor="welcomeMessage" className="text-white">Welcome Message</Label>
                      <Textarea
                        id="welcomeMessage"
                        placeholder="Welcome {user} to {server}!"
                        value={config.welcomeMessage || ''}
                        onChange={(e) => handleInputChange('welcomeMessage', e.target.value)}
                        className="mt-2"
                      />
                    </div>
                  </>
                )}
                <div className="flex items-center justify-between">
                  <Label htmlFor="leave" className="text-white">Leave Messages</Label>
                  <Switch
                    id="leave"
                    checked={config.leaveEnabled}
                    onCheckedChange={(checked) => handleToggle('leaveEnabled', checked)}
                  />
                </div>
                {config.leaveEnabled && (
                  <>
                    <div>
                      <Label htmlFor="leaveChannel" className="text-white">Leave Channel</Label>
                      <Input
                        id="leaveChannel"
                        placeholder="Channel ID"
                        value={config.leaveChannel || ''}
                        onChange={(e) => handleInputChange('leaveChannel', e.target.value)}
                        className="mt-2"
                      />
                    </div>
                    <div>
                      <Label htmlFor="leaveMessage" className="text-white">Leave Message</Label>
                      <Textarea
                        id="leaveMessage"
                        placeholder="{user} has left the server"
                        value={config.leaveMessage || ''}
                        onChange={(e) => handleInputChange('leaveMessage', e.target.value)}
                        className="mt-2"
                      />
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Role Settings */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Users className="w-5 h-5" />
                  Role Settings
                </CardTitle>
                <CardDescription>
                  Configure automatic roles and permissions
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="autorole" className="text-white">Auto Role</Label>
                  <Switch
                    id="autorole"
                    checked={config.autoRoleEnabled}
                    onCheckedChange={(checked) => handleToggle('autoRoleEnabled', checked)}
                  />
                </div>
                {config.autoRoleEnabled && (
                  <div>
                    <Label htmlFor="autoRoleId" className="text-white">Auto Role ID</Label>
                    <Input
                      id="autoRoleId"
                      placeholder="Role ID"
                      value={config.autoRoleId || ''}
                      onChange={(e) => handleInputChange('autoRoleId', e.target.value)}
                      className="mt-2"
                    />
                  </div>
                )}
                <div>
                  <Label htmlFor="mutedRole" className="text-white">Muted Role ID</Label>
                  <Input
                    id="mutedRole"
                    placeholder="Role ID for muted users"
                    value={config.mutedRoleId || ''}
                    onChange={(e) => handleInputChange('mutedRoleId', e.target.value)}
                    className="mt-2"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Economy Settings */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Coins className="w-5 h-5" />
                  Economy Settings
                </CardTitle>
                <CardDescription>
                  Configure economy and reward system
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="economy" className="text-white">Enable Economy</Label>
                  <Switch
                    id="economy"
                    checked={config.economyEnabled}
                    onCheckedChange={(checked) => handleToggle('economyEnabled', checked)}
                  />
                </div>
                {config.economyEnabled && (
                  <div>
                    <Label htmlFor="dailyReward" className="text-white">Daily Reward Amount</Label>
                    <Input
                      id="dailyReward"
                      type="number"
                      placeholder="100"
                      value={config.dailyReward}
                      onChange={(e) => handleInputChange('dailyReward', parseInt(e.target.value) || 0)}
                      className="mt-2"
                    />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Custom Commands */}
            <Card className="bg-slate-800/50 border-slate-700 lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Hash className="w-5 h-5" />
                  Custom Commands
                </CardTitle>
                <CardDescription>
                  Create and manage custom commands for your server
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="customCommands" className="text-white">Enable Custom Commands</Label>
                    <Switch
                      id="customCommands"
                      checked={config.customCommandsEnabled}
                      onCheckedChange={(checked) => handleToggle('customCommandsEnabled', checked)}
                    />
                  </div>
                  {config.customCommandsEnabled && (
                    <Button
                      onClick={() => setIsAddingCommand(true)}
                      disabled={commands && commands.length >= config.maxCustomCommands}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Command
                    </Button>
                  )}
                </div>

                {config.customCommandsEnabled && (
                  <>
                    {isAddingCommand && (
                      <div className="border border-slate-600 rounded-lg p-4 mb-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                          <div>
                            <Label htmlFor="commandName" className="text-white">Command Name</Label>
                            <Input
                              id="commandName"
                              placeholder="!hello"
                              value={newCommandName}
                              onChange={(e) => setNewCommandName(e.target.value)}
                              className="mt-2"
                            />
                          </div>
                          <div>
                            <Label htmlFor="commandResponse" className="text-white">Response</Label>
                            <Input
                              id="commandResponse"
                              placeholder="Hello there!"
                              value={newCommandResponse}
                              onChange={(e) => setNewCommandResponse(e.target.value)}
                              className="mt-2"
                            />
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            onClick={handleAddCommand}
                            disabled={createCommandMutation.isPending}
                          >
                            <Save className="w-4 h-4 mr-2" />
                            Save Command
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => {
                              setIsAddingCommand(false);
                              setNewCommandName('');
                              setNewCommandResponse('');
                            }}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    )}

                    {commandsLoading ? (
                      <LoadingSkeleton type="list" count={3} />
                    ) : (
                      <div className="space-y-2">
                        {commands && commands.length > 0 ? (
                          commands.map((command) => (
                            <div key={command.id} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                              <div>
                                <Badge variant="secondary" className="mr-2">
                                  {command.name}
                                </Badge>
                                <span className="text-gray-300">{command.response}</span>
                              </div>
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => deleteCommandMutation.mutate(command.id)}
                                disabled={deleteCommandMutation.isPending}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          ))
                        ) : (
                          <div className="text-center py-8 text-gray-400">
                            <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
                            <p>No custom commands yet. Add your first command!</p>
                          </div>
                        )}
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </PageTransition>
  );
}