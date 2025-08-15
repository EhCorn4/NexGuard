import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { GradientText } from "@/components/ui/gradient-text";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Separator } from "@/components/ui/separator";
import { 
  Search, Book, Terminal, Settings, Shield, Ticket, Zap, HelpCircle, AlertCircle, 
  ChevronDown, ChevronRight, Copy, ExternalLink, Star, Users, Bot, MessageSquare,
  Activity, Lock, Sparkles, Database, BarChart3, Webhook, Globe,
  Headphones, Calendar, Timer, Gamepad2, Crown, CheckCircle2, ArrowRight, Download
} from "lucide-react";
import type { Command } from "@shared/schema";
import { memo } from "react";

const Docs = memo(function Docs() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  
  const { data: commands, isLoading } = useQuery<Command[]>({
    queryKey: ["/api/bot/commands"],
  });

  const filteredCommands = commands?.filter(command =>
    command.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    command.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    command.category.toLowerCase().includes(searchTerm.toLowerCase())
  ).filter(command => 
    !selectedCategory || command.category === selectedCategory
  );

  const commandsByCategory = filteredCommands?.reduce((acc, command) => {
    if (!acc[command.category]) acc[command.category] = [];
    acc[command.category].push(command);
    return acc;
  }, {} as Record<string, Command[]>);

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'admin': return Settings;
      case 'moderation': return Shield;
      case 'ticket': return Ticket;
      case 'utility': return Zap;
      case 'autoreply': return MessageSquare;
      case 'automod': return Sparkles;
      case 'role': return Crown;
      case 'embed': return Terminal;
      case 'analytics': return BarChart3;
      case 'eventlog': return Activity;
      case 'serverstats': return Database;
      case 'reactionroles': return Star;
      default: return Terminal;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'admin': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'moderation': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'ticket': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'utility': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'autoreply': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'automod': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'role': return 'bg-pink-500/20 text-pink-400 border-pink-500/30';
      case 'embed': return 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30';
      case 'analytics': return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
      case 'eventlog': return 'bg-violet-500/20 text-violet-400 border-violet-500/30';
      case 'serverstats': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'reactionroles': return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const categories = [
    { id: 'admin', name: 'Admin', description: 'Server configuration and management', count: commands?.filter(c => c.category === 'admin').length || 0 },
    { id: 'moderation', name: 'Moderation', description: 'User moderation and punishment', count: commands?.filter(c => c.category === 'moderation').length || 0 },
    { id: 'ticket', name: 'Tickets', description: 'Support ticket system', count: commands?.filter(c => c.category === 'ticket').length || 0 },
    { id: 'utility', name: 'Utility', description: 'General bot utilities', count: commands?.filter(c => c.category === 'utility').length || 0 },
    { id: 'automod', name: 'AutoMod', description: 'Automated moderation', count: commands?.filter(c => c.category === 'automod').length || 0 },
    { id: 'autoreply', name: 'Auto-Reply', description: 'Automated responses', count: commands?.filter(c => c.category === 'autoreply').length || 0 },
    { id: 'eventlog', name: 'Event Logging', description: 'Server event tracking', count: commands?.filter(c => c.category === 'eventlog').length || 0 },
    { id: 'role', name: 'Role Management', description: 'Role assignment and permissions', count: commands?.filter(c => c.category === 'role').length || 0 }
  ];

  const featuresShowcase = [
    {
      title: "Professional Ticket System",
      description: "TicketsBot.net-style ticket system with permanent interactive panels",
      icon: Ticket,
      color: "text-blue-400",
      features: [
        "Permanent interactive panels that persist across bot restarts",
        "21 ticket panel views restored across 5 guilds", 
        "{panel}-{username} channel naming convention",
        "Close 🔒 and Claim 🙌 buttons for staff management",
        "Automatic transcript delivery when tickets close",
        "Support for placeholder variables: {user.mention}, {user.name}, {guild.name}"
      ],
      commands: ["/ticket-panel", "/close", "/claim", "/add", "/rename"]
    },
    {
      title: "Advanced AutoMod Suite",
      description: "Comprehensive automated moderation with multiple protection layers",
      icon: Sparkles,
      color: "text-yellow-400",
      features: [
        "Spam detection with configurable thresholds",
        "Bad word filtering with custom word lists",
        "Link filtering with whitelist support",
        "Caps lock protection (configurable percentage)",
        "Mention spam limits (configurable count)",
        "Comprehensive logging for all automod actions"
      ],
      commands: ["/automod-config", "/automod-spam", "/automod-badwords", "/automod-links"]
    },
    {
      title: "Live Server Statistics",
      description: "Real-time voice channels displaying live server metrics",
      icon: Database,
      color: "text-emerald-400",
      features: [
        "Live member count updates",
        "Bot count statistics",
        "Channel count tracking",
        "Role count display",
        "Automatic updates every few minutes",
        "Clean professional formatting"
      ],
      commands: ["/serverstats add", "/serverstats list", "/serverstats remove"]
    },
    {
      title: "Complete Event Logging",
      description: "Comprehensive tracking across 7 specialized event categories",
      icon: Activity,
      color: "text-violet-400",
      features: [
        "Member events (joins, leaves, role changes)",
        "Message events (edits, deletes, reactions)",
        "Voice events (join, leave, mute, deafen)",
        "Channel events (create, delete, update)",
        "Role events (create, delete, permission changes)",
        "Moderation events (bans, kicks, warnings)",
        "Server events (settings changes, emoji updates)"
      ],
      commands: ["/eventlog setup", "/eventlog toggle", "/eventlog status"]
    }
  ];

  const quickStart = [
    {
      title: "1. Invite NexGuard",
      description: "Add NexGuard to your Discord server with full permissions.",
      icon: Bot,
      color: "text-cyan-400",
      content: [
        "Click the 'Invite to Server' button",
        "Select your server from the dropdown",
        "Grant Administrator permissions for full functionality",
        "Verify the bot appears online in your member list"
      ],
      command: "Invite Bot",
      tip: "Administrator permissions ensure all features work correctly including advanced moderation and ticket management."
    },
    {
      title: "2. Essential Configuration",
      description: "Configure core bot settings and moderation roles.",
      icon: Settings,
      color: "text-orange-400",
      content: [
        "Run `/settings` to view current server configuration",
        "Set moderation role: `/modrole @Moderator`",
        "Configure logging: `/eventlog setup #logs`",
        "Test basic functionality: `/ping` and `/serverinfo`"
      ],
      command: "/settings",
      tip: "Proper role hierarchy is crucial - ensure NexGuard's role is above moderation roles."
    },
    {
      title: "3. Ticket System Setup", 
      description: "Create professional support ticket panels with interactive buttons.",
      icon: Ticket,
      color: "text-blue-400",
      content: [
        "Create ticket panel: `/ticket-panel action:create panel_id:support`",
        "Deploy to channel: `/ticket-panel action:deploy panel_id:support`",
        "Test ticket creation by clicking the panel button",
        "Staff can use Close 🔒 and Claim 🙌 buttons"
      ],
      command: "/ticket-panel",
      tip: "Tickets use {panel}-{username} naming and provide automatic transcripts when closed."
    },
    {
      title: "4. AutoMod Protection", 
      description: "Enable comprehensive automated moderation across multiple layers.",
      icon: Sparkles,
      color: "text-yellow-400", 
      content: [
        "View current settings: `/automod-config`",
        "Enable spam protection: `/automod-spam True`",
        "Configure bad word filter: `/automod-badwords True`",
        "Set mention limits: `/automod-mentions True 5`"
      ],
      command: "/automod-config",
      tip: "AutoMod provides 6 protection layers: spam, links, bad words, caps lock, mentions, and custom words."
    },
    {
      title: "5. Live Statistics",
      description: "Set up real-time voice channels displaying server metrics.",
      icon: Database,
      color: "text-emerald-400",
      content: [
        "Add member count: `/serverstats add member_count`",
        "Add channel count: `/serverstats add channel_count`", 
        "View all stats: `/serverstats list`",
        "Force update: `/serverstats force-update`"
      ],
      command: "/serverstats add",
      tip: "Statistics channels update automatically and display live metrics in voice channel names."
    },
    {
      title: "6. Ready to Use",
      description: "Your NexGuard bot is now fully configured and operational.",
      icon: CheckCircle2,
      color: "text-green-400",
      content: [
        "All 60 commands are now available",
        "Test with `/commands` to view all commands",
        "Use `/help <command>` for detailed command info",
        "Join our community for support and updates"
      ],
      command: "/commands",
      tip: "Visit our community Discord for additional help, feature requests, and updates."
    }
  ];

  return (
    <div className="min-h-screen hero-gradient circuit-pattern pt-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      <div className="container mx-auto px-4 py-20 relative z-10">
        <PageHeader 
          title="Documentation"
          description="Complete guide to NexGuard's 60 commands featuring professional ticket system, advanced automod, live statistics, event logging, and enterprise-level Discord server management."
        />

        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-6 mb-8">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="quickstart" className="flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Quick Start
            </TabsTrigger>
            <TabsTrigger value="commands" className="flex items-center gap-2">
              <Terminal className="w-4 h-4" />
              Commands
            </TabsTrigger>
            <TabsTrigger value="features" className="flex items-center gap-2">
              <Star className="w-4 h-4" />
              Features
            </TabsTrigger>
            <TabsTrigger value="guides" className="flex items-center gap-2">
              <Book className="w-4 h-4" />
              Guides
            </TabsTrigger>
            <TabsTrigger value="support" className="flex items-center gap-2">
              <HelpCircle className="w-4 h-4" />
              Support
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <div className="space-y-6">
              {/* Bot Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-500/20 rounded-lg">
                        <Terminal className="w-5 h-5 text-blue-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-white">60</p>
                        <p className="text-sm text-gray-400">Total Commands</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-green-500/20 rounded-lg">
                        <Users className="w-5 h-5 text-green-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-white">17</p>
                        <p className="text-sm text-gray-400">Active Servers</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-purple-500/20 rounded-lg">
                        <Star className="w-5 h-5 text-purple-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-white">29.5k</p>
                        <p className="text-sm text-gray-400">Lines of Code</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Overview Content */}
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="text-2xl">
                    <GradientText>Enterprise Discord Management</GradientText>
                  </CardTitle>
                  <CardDescription>
                    NexGuard provides comprehensive Discord server management with 60 commands across 8 specialized categories
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {categories.slice(0, 8).map((category) => {
                      const IconComponent = getCategoryIcon(category.id);
                      return (
                        <div key={category.id} className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                          <div className="flex items-center gap-3 mb-2">
                            <IconComponent className="w-5 h-5 text-[hsl(var(--nexguard-cyan))]" />
                            <h3 className="font-semibold text-white">{category.name}</h3>
                            <Badge variant="secondary" className={getCategoryColor(category.id)}>
                              {category.count}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-400">{category.description}</p>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Key Features */}
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5" />
                    Core Capabilities
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="text-center p-4">
                      <Ticket className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                      <h4 className="font-semibold text-white mb-1">Ticket System</h4>
                      <p className="text-xs text-gray-400">Professional support panels</p>
                    </div>
                    <div className="text-center p-4">
                      <Sparkles className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                      <h4 className="font-semibold text-white mb-1">AutoMod</h4>
                      <p className="text-xs text-gray-400">6-layer protection system</p>
                    </div>
                    <div className="text-center p-4">
                      <Database className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                      <h4 className="font-semibold text-white mb-1">Live Statistics</h4>
                      <p className="text-xs text-gray-400">Real-time server metrics</p>
                    </div>
                    <div className="text-center p-4">
                      <Activity className="w-8 h-8 text-violet-400 mx-auto mb-2" />
                      <h4 className="font-semibold text-white mb-1">Event Logging</h4>
                      <p className="text-xs text-gray-400">7 specialized categories</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="quickstart">
            <div className="space-y-6">
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="text-2xl">
                    <GradientText>Quick Start Guide</GradientText>
                  </CardTitle>
                  <CardDescription>
                    Get NexGuard running on your server in 6 simple steps
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {quickStart.map((step, index) => {
                      const IconComponent = step.icon;
                      return (
                        <div key={index} className="relative">
                          <div className="flex items-start gap-4">
                            <div className={`p-3 bg-slate-900/50 rounded-lg border border-slate-700/50 flex-shrink-0`}>
                              <IconComponent className={`w-6 h-6 ${step.color}`} />
                            </div>
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                              <p className="text-gray-400 mb-4">{step.description}</p>
                              <div className="space-y-2 mb-4">
                                {step.content.map((item, itemIndex) => (
                                  <div key={itemIndex} className="flex items-start gap-2">
                                    <ArrowRight className="w-4 h-4 text-[hsl(var(--nexguard-cyan))] mt-0.5 flex-shrink-0" />
                                    <span className="text-gray-300 text-sm">{item}</span>
                                  </div>
                                ))}
                              </div>
                              {step.command && (
                                <div className="flex items-center gap-2 mb-2">
                                  <code className="bg-slate-900/80 px-3 py-1 rounded text-[hsl(var(--nexguard-cyan))] text-sm">
                                    {step.command}
                                  </code>
                                  <Button size="sm" variant="outline" className="h-7 px-2">
                                    <Copy className="w-3 h-3" />
                                  </Button>
                                </div>
                              )}
                              {step.tip && (
                                <Alert className="bg-blue-950/30 border-blue-800/50">
                                  <AlertCircle className="h-4 w-4" />
                                  <AlertDescription className="text-sm text-blue-200">
                                    {step.tip}
                                  </AlertDescription>
                                </Alert>
                              )}
                            </div>
                          </div>
                          {index < quickStart.length - 1 && (
                            <div className="absolute left-[22px] top-16 w-0.5 h-6 bg-gradient-to-b from-[hsl(var(--nexguard-cyan))] to-transparent"></div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="commands">
            <div className="space-y-6">
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Terminal className="w-5 h-5" />
                    Command Reference
                  </CardTitle>
                  <CardDescription>
                    Search and browse all 60 available bot commands organized by category
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {/* Search and Filter Controls */}
                  <div className="flex flex-col md:flex-row gap-4 mb-6">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <Input
                        placeholder="Search commands by name, description, or category..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                    <div className="flex gap-2 flex-wrap">
                      <Button
                        variant={selectedCategory === null ? "default" : "outline"}
                        size="sm"
                        onClick={() => setSelectedCategory(null)}
                      >
                        All Categories
                      </Button>
                      {categories.slice(0, 4).map((category) => (
                        <Button
                          key={category.id}
                          variant={selectedCategory === category.id ? "default" : "outline"}
                          size="sm"
                          onClick={() => setSelectedCategory(category.id)}
                          className="text-xs"
                        >
                          {category.name} ({category.count})
                        </Button>
                      ))}
                    </div>
                  </div>

                  {/* Category Overview Grid */}
                  {!searchTerm && !selectedCategory && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                      {categories.map((category) => {
                        const IconComponent = getCategoryIcon(category.id);
                        return (
                          <Card
                            key={category.id}
                            className="bg-slate-900/50 border-slate-700/50 cursor-pointer hover:border-[hsl(var(--nexguard-cyan))]/50 transition-colors"
                            onClick={() => setSelectedCategory(category.id)}
                          >
                            <CardContent className="pt-4">
                              <div className="flex items-center gap-3 mb-2">
                                <IconComponent className="w-5 h-5 text-[hsl(var(--nexguard-cyan))]" />
                                <div>
                                  <h3 className="font-semibold text-white text-sm">{category.name}</h3>
                                  <Badge variant="secondary" className={`${getCategoryColor(category.id)} text-xs`}>
                                    {category.count} commands
                                  </Badge>
                                </div>
                              </div>
                              <p className="text-xs text-gray-400">{category.description}</p>
                            </CardContent>
                          </Card>
                        );
                      })}
                    </div>
                  )}

                  {/* Commands List */}
                  {isLoading ? (
                    <div className="text-center py-12">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[hsl(var(--nexguard-cyan))] mx-auto"></div>
                      <p className="mt-4 text-gray-400">Loading commands...</p>
                    </div>
                  ) : (
                    <div className="space-y-8">
                      {Object.entries(commandsByCategory || {}).map(([category, categoryCommands]) => {
                        const IconComponent = getCategoryIcon(category);
                        return (
                          <Collapsible
                            key={category}
                            open={expandedSections[category] !== false}
                            onOpenChange={() => toggleSection(category)}
                          >
                            <CollapsibleTrigger className="w-full">
                              <div className="flex items-center gap-3 mb-4 p-3 bg-slate-900/50 rounded-lg border border-slate-700/50 hover:border-[hsl(var(--nexguard-cyan))]/50 transition-colors">
                                <IconComponent className="w-6 h-6 text-[hsl(var(--nexguard-cyan))]" />
                                <h3 className="text-xl font-semibold text-white capitalize flex-1 text-left">{category} Commands</h3>
                                <Badge variant="secondary" className={getCategoryColor(category)}>
                                  {categoryCommands.length}
                                </Badge>
                                {expandedSections[category] !== false ? (
                                  <ChevronDown className="w-5 h-5 text-gray-400" />
                                ) : (
                                  <ChevronRight className="w-5 h-5 text-gray-400" />
                                )}
                              </div>
                            </CollapsibleTrigger>
                            <CollapsibleContent>
                              <div className="grid gap-4 ml-4">
                                {categoryCommands.map((command) => (
                                  <Card key={command.id} className="bg-slate-900/30 border-slate-700/50 hover:bg-slate-900/50 transition-colors">
                                    <CardHeader className="pb-3">
                                      <div className="flex items-center justify-between">
                                        <CardTitle className="text-lg flex items-center gap-2">
                                          <code className="text-[hsl(var(--nexguard-cyan))] bg-slate-800 px-2 py-1 rounded">
                                            /{command.name}
                                          </code>
                                          <Button size="sm" variant="ghost" className="h-6 w-6 p-0">
                                            <Copy className="w-3 h-3" />
                                          </Button>
                                        </CardTitle>
                                        <Badge variant="outline" className={getCategoryColor(command.category)}>
                                          {command.category}
                                        </Badge>
                                      </div>
                                      <CardDescription className="text-gray-300">
                                        {command.description}
                                      </CardDescription>
                                    </CardHeader>
                                    <CardContent className="pt-0">
                                      <div className="space-y-3">
                                        <div>
                                          <span className="text-sm font-medium text-gray-300 mb-1 block">Usage:</span>
                                          <code className="text-sm bg-slate-800 px-3 py-2 rounded block text-gray-300 border border-slate-700">
                                            {command.usage}
                                          </code>
                                        </div>
                                        {command.permissions && command.permissions.length > 0 && (
                                          <div>
                                            <span className="text-sm font-medium text-gray-300 mb-1 block">Required Permissions:</span>
                                            <div className="flex flex-wrap gap-1 mt-1">
                                              {command.permissions.map((perm, index) => (
                                                <Badge key={index} variant="secondary" className="text-xs">
                                                  {perm}
                                                </Badge>
                                              ))}
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                    </CardContent>
                                  </Card>
                                ))}
                              </div>
                            </CollapsibleContent>
                          </Collapsible>
                        );
                      })}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="features">
            <div className="space-y-6">
              {featuresShowcase.map((feature, index) => {
                const IconComponent = feature.icon;
                return (
                  <Card key={index} className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                    <CardHeader>
                      <div className="flex items-center gap-3 mb-4">
                        <div className="p-3 bg-slate-900/50 rounded-lg">
                          <IconComponent className={`w-8 h-8 ${feature.color}`} />
                        </div>
                        <div>
                          <CardTitle className="text-xl text-white">{feature.title}</CardTitle>
                          <CardDescription>{feature.description}</CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="font-semibold text-white mb-3">Key Features</h4>
                          <ul className="space-y-2">
                            {feature.features.map((feat, featIndex) => (
                              <li key={featIndex} className="flex items-start gap-2">
                                <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                                <span className="text-sm text-gray-300">{feat}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-semibold text-white mb-3">Related Commands</h4>
                          <div className="space-y-2">
                            {feature.commands.map((cmd, cmdIndex) => (
                              <div key={cmdIndex} className="flex items-center gap-2">
                                <code className="bg-slate-900/80 px-3 py-1 rounded text-[hsl(var(--nexguard-cyan))] text-sm">
                                  {cmd}
                                </code>
                                <Button size="sm" variant="ghost" className="h-6 w-6 p-0">
                                  <Copy className="w-3 h-3" />
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          <TabsContent value="guides">
            <div className="space-y-6">
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="text-2xl">
                    <GradientText>Downloadable Guides</GradientText>
                  </CardTitle>
                  <CardDescription>
                    Comprehensive PDF guides and documentation for NexGuard setup and advanced usage
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Quick Start Guide */}
                    <Card className="bg-slate-900/50 border-slate-700/50 hover:border-[hsl(var(--nexguard-cyan))]/50 transition-colors">
                      <CardHeader className="pb-3">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-green-500/20 rounded-lg">
                            <Zap className="w-5 h-5 text-green-400" />
                          </div>
                          <div>
                            <CardTitle className="text-lg">Quick Start Guide</CardTitle>
                            <p className="text-sm text-gray-400">Essential setup steps</p>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <p className="text-sm text-gray-300 mb-4">
                          Complete setup guide from bot invitation to first commands. Perfect for new users.
                        </p>
                        <div className="space-y-2 text-xs text-gray-400 mb-4">
                          <div className="flex justify-between">
                            <span>Pages:</span>
                            <span>12</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Size:</span>
                            <span>2.3 MB</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Updated:</span>
                            <span>Jan 2025</span>
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="w-full hover:bg-[hsl(var(--nexguard-cyan))]/10"
                          onClick={() => window.open('/api/guides/download/quickstart', '_blank')}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Download PDF
                        </Button>
                      </CardContent>
                    </Card>

                    {/* AutoMod Setup Guide */}
                    <Card className="bg-slate-900/50 border-slate-700/50 hover:border-[hsl(var(--nexguard-cyan))]/50 transition-colors">
                      <CardHeader className="pb-3">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-yellow-500/20 rounded-lg">
                            <Sparkles className="w-5 h-5 text-yellow-400" />
                          </div>
                          <div>
                            <CardTitle className="text-lg">AutoMod Setup</CardTitle>
                            <p className="text-sm text-gray-400">Advanced moderation</p>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <p className="text-sm text-gray-300 mb-4">
                          Configure spam detection, word filtering, and automated punishments with examples.
                        </p>
                        <div className="space-y-2 text-xs text-gray-400 mb-4">
                          <div className="flex justify-between">
                            <span>Pages:</span>
                            <span>18</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Size:</span>
                            <span>4.1 MB</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Updated:</span>
                            <span>Jan 2025</span>
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="w-full hover:bg-[hsl(var(--nexguard-cyan))]/10"
                          onClick={() => window.open('/api/guides/download/automod', '_blank')}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Download PDF
                        </Button>
                      </CardContent>
                    </Card>

                    {/* Ticket System Guide */}
                    <Card className="bg-slate-900/50 border-slate-700/50 hover:border-[hsl(var(--nexguard-cyan))]/50 transition-colors">
                      <CardHeader className="pb-3">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-blue-500/20 rounded-lg">
                            <Ticket className="w-5 h-5 text-blue-400" />
                          </div>
                          <div>
                            <CardTitle className="text-lg">Ticket System</CardTitle>
                            <p className="text-sm text-gray-400">Professional support</p>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <p className="text-sm text-gray-300 mb-4">
                          Create interactive ticket panels, configure categories, and manage support workflows.
                        </p>
                        <div className="space-y-2 text-xs text-gray-400 mb-4">
                          <div className="flex justify-between">
                            <span>Pages:</span>
                            <span>22</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Size:</span>
                            <span>5.7 MB</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Updated:</span>
                            <span>Jan 2025</span>
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="w-full hover:bg-[hsl(var(--nexguard-cyan))]/10"
                          onClick={() => window.open('/api/guides/download/tickets', '_blank')}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Download PDF
                        </Button>
                      </CardContent>
                    </Card>

                    {/* Analytics & Logging Guide */}
                    <Card className="bg-slate-900/50 border-slate-700/50 hover:border-[hsl(var(--nexguard-cyan))]/50 transition-colors">
                      <CardHeader className="pb-3">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-cyan-500/20 rounded-lg">
                            <BarChart3 className="w-5 h-5 text-cyan-400" />
                          </div>
                          <div>
                            <CardTitle className="text-lg">Analytics & Logging</CardTitle>
                            <p className="text-sm text-gray-400">Data insights</p>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <p className="text-sm text-gray-300 mb-4">
                          Setup server statistics, event logging, and analytics dashboards for data-driven decisions.
                        </p>
                        <div className="space-y-2 text-xs text-gray-400 mb-4">
                          <div className="flex justify-between">
                            <span>Pages:</span>
                            <span>15</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Size:</span>
                            <span>3.2 MB</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Updated:</span>
                            <span>Jan 2025</span>
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="w-full hover:bg-[hsl(var(--nexguard-cyan))]/10"
                          onClick={() => window.open('/api/guides/download/analytics', '_blank')}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Download PDF
                        </Button>
                      </CardContent>
                    </Card>

                    {/* Role Management Guide */}
                    <Card className="bg-slate-900/50 border-slate-700/50 hover:border-[hsl(var(--nexguard-cyan))]/50 transition-colors">
                      <CardHeader className="pb-3">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-pink-500/20 rounded-lg">
                            <Crown className="w-5 h-5 text-pink-400" />
                          </div>
                          <div>
                            <CardTitle className="text-lg">Role Management</CardTitle>
                            <p className="text-sm text-gray-400">Permissions & roles</p>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <p className="text-sm text-gray-300 mb-4">
                          Configure reaction roles, auto-roles, and permission hierarchies for organized servers.
                        </p>
                        <div className="space-y-2 text-xs text-gray-400 mb-4">
                          <div className="flex justify-between">
                            <span>Pages:</span>
                            <span>14</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Size:</span>
                            <span>2.8 MB</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Updated:</span>
                            <span>Jan 2025</span>
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="w-full hover:bg-[hsl(var(--nexguard-cyan))]/10"
                          onClick={() => window.open('/api/guides/download/roles', '_blank')}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Download PDF
                        </Button>
                      </CardContent>
                    </Card>

                    {/* Complete Admin Guide */}
                    <Card className="bg-slate-900/50 border-slate-700/50 hover:border-[hsl(var(--nexguard-cyan))]/50 transition-colors">
                      <CardHeader className="pb-3">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-orange-500/20 rounded-lg">
                            <Settings className="w-5 h-5 text-orange-400" />
                          </div>
                          <div>
                            <CardTitle className="text-lg">Complete Admin Guide</CardTitle>
                            <p className="text-sm text-gray-400">Everything included</p>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <p className="text-sm text-gray-300 mb-4">
                          Comprehensive guide covering all NexGuard features, best practices, and troubleshooting.
                        </p>
                        <div className="space-y-2 text-xs text-gray-400 mb-4">
                          <div className="flex justify-between">
                            <span>Pages:</span>
                            <span>85</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Size:</span>
                            <span>18.4 MB</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Updated:</span>
                            <span>Jan 2025</span>
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="w-full hover:bg-[hsl(var(--nexguard-cyan))]/10"
                          onClick={() => window.open('/api/guides/download/complete', '_blank')}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Download PDF
                        </Button>
                      </CardContent>
                    </Card>
                  </div>
                </CardContent>
              </Card>

              {/* Additional Resources */}
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Book className="w-5 h-5" />
                    Additional Resources
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Templates & Examples */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-white">Templates & Examples</h3>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg border border-slate-700/50">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-purple-500/20 rounded-lg">
                              <MessageSquare className="w-4 h-4 text-purple-400" />
                            </div>
                            <div>
                              <p className="font-medium text-white">AutoReply Templates</p>
                              <p className="text-xs text-gray-400">JSON config files</p>
                            </div>
                          </div>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => window.open('/api/guides/download/templates/autoreply', '_blank')}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg border border-slate-700/50">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-yellow-500/20 rounded-lg">
                              <Sparkles className="w-4 h-4 text-yellow-400" />
                            </div>
                            <div>
                              <p className="font-medium text-white">AutoMod Configurations</p>
                              <p className="text-xs text-gray-400">Ready-to-use configs</p>
                            </div>
                          </div>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => window.open('/api/guides/download/templates/automod', '_blank')}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="support">
            <div className="space-y-6">
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <HelpCircle className="w-5 h-5" />
                    Support & Community
                  </CardTitle>
                  <CardDescription>
                    Get help, report issues, and connect with other NexGuard users
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <Alert className="bg-blue-950/30 border-blue-800/50">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription className="text-blue-200">
                        For immediate help, use <code>/commands</code> to see all 60 available commands or <code>/help &lt;command&gt;</code> for detailed command information.
                      </AlertDescription>
                    </Alert>

                    <div className="grid md:grid-cols-2 gap-6">
                      <Card className="bg-slate-900/50 border-slate-700/50">
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2 text-lg">
                            <MessageSquare className="w-5 h-5" />
                            Discord Community
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <p className="text-gray-300 text-sm">
                            Join our Discord server for real-time support, feature requests, and community discussions.
                          </p>
                          <Button className="w-full" asChild>
                            <a href="https://discord.gg/DNxp3Xxw59" target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="w-4 h-4 mr-2" />
                              Join Discord Server
                            </a>
                          </Button>
                        </CardContent>
                      </Card>

                      <Card className="bg-slate-900/50 border-slate-700/50">
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2 text-lg">
                            <Book className="w-5 h-5" />
                            Documentation
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <p className="text-gray-300 text-sm">
                            Comprehensive guides and documentation for all features and commands.
                          </p>
                          <div className="space-y-2">
                            <Button variant="outline" size="sm" className="w-full justify-start">
                              <Terminal className="w-4 h-4 mr-2" />
                              Command Reference
                            </Button>
                            <Button variant="outline" size="sm" className="w-full justify-start">
                              <Zap className="w-4 h-4 mr-2" />
                              Quick Start Guide
                            </Button>
                            <Button variant="outline" size="sm" className="w-full justify-start">
                              <Star className="w-4 h-4 mr-2" />
                              Feature Showcase
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    <Card className="bg-slate-900/50 border-slate-700/50">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Activity className="w-5 h-5" />
                          Troubleshooting
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <div className="space-y-3">
                            <h4 className="font-semibold text-white">Common Issues & Solutions</h4>
                            
                            <Collapsible>
                              <CollapsibleTrigger className="flex items-center gap-2 text-sm font-medium text-gray-300 hover:text-white transition-colors">
                                <ChevronRight className="w-4 h-4" />
                                Commands not working / Permission errors
                              </CollapsibleTrigger>
                              <CollapsibleContent className="mt-2 pl-6 text-sm text-gray-400 space-y-1">
                                <p>• Ensure NexGuard has Administrator permissions</p>
                                <p>• Check that the bot's role is above moderation roles</p>
                                <p>• Verify the bot is online in your server member list</p>
                                <p>• Try <code>/ping</code> to test basic connectivity</p>
                              </CollapsibleContent>
                            </Collapsible>

                            <Collapsible>
                              <CollapsibleTrigger className="flex items-center gap-2 text-sm font-medium text-gray-300 hover:text-white transition-colors">
                                <ChevronRight className="w-4 h-4" />
                                Ticket system not working
                              </CollapsibleTrigger>
                              <CollapsibleContent className="mt-2 pl-6 text-sm text-gray-400 space-y-1">
                                <p>• Use <code>/ticket-panel action:list</code> to see existing panels</p>
                                <p>• Ensure panels are deployed with <code>/ticket-panel action:deploy</code></p>
                                <p>• Check that the bot can create channels in your server</p>
                                <p>• Verify ticket categories have proper permissions</p>
                              </CollapsibleContent>
                            </Collapsible>

                            <Collapsible>
                              <CollapsibleTrigger className="flex items-center gap-2 text-sm font-medium text-gray-300 hover:text-white transition-colors">
                                <ChevronRight className="w-4 h-4" />
                                AutoMod not detecting violations
                              </CollapsibleTrigger>
                              <CollapsibleContent className="mt-2 pl-6 text-sm text-gray-400 space-y-1">
                                <p>• Check settings with <code>/automod-config</code></p>
                                <p>• Ensure AutoMod features are enabled</p>
                                <p>• Verify the bot can delete messages and timeout users</p>
                                <p>• Test with <code>/automod-status</code> for system health</p>
                              </CollapsibleContent>
                            </Collapsible>

                            <Collapsible>
                              <CollapsibleTrigger className="flex items-center gap-2 text-sm font-medium text-gray-300 hover:text-white transition-colors">
                                <ChevronRight className="w-4 h-4" />
                                Statistics channels not updating
                              </CollapsibleTrigger>
                              <CollapsibleContent className="mt-2 pl-6 text-sm text-gray-400 space-y-1">
                                <p>• Use <code>/serverstats list</code> to check configured stats</p>
                                <p>• Force update with <code>/serverstats force-update</code></p>
                                <p>• Ensure the bot can modify voice channel names</p>
                                <p>• Clean orphaned entries with <code>/serverstats cleanup</code></p>
                              </CollapsibleContent>
                            </Collapsible>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="bg-slate-900/50 border-slate-700/50">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Bot className="w-5 h-5" />
                          Bot Information
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                          <div>
                            <p className="text-2xl font-bold text-[hsl(var(--nexguard-cyan))]">60</p>
                            <p className="text-xs text-gray-400">Commands</p>
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-[hsl(var(--nexguard-cyan))]">17</p>
                            <p className="text-xs text-gray-400">Active Servers</p>
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-[hsl(var(--nexguard-cyan))]">8</p>
                            <p className="text-xs text-gray-400">Categories</p>
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-[hsl(var(--nexguard-cyan))]">99.9%</p>
                            <p className="text-xs text-gray-400">Uptime</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
});

export default Docs;