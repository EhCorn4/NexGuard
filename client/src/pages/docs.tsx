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
import { Search, Book, Terminal, Settings, Shield, Ticket, Zap, HelpCircle, AlertCircle } from "lucide-react";
import type { Command } from "@shared/schema";
import { memo } from "react";

const Docs = memo(function Docs() {
  const [searchTerm, setSearchTerm] = useState("");
  
  const { data: commands, isLoading } = useQuery<Command[]>({
    queryKey: ["/api/bot/commands"],
  });

  const filteredCommands = commands?.filter(command =>
    command.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    command.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    command.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const commandsByCategory = filteredCommands?.reduce((acc, command) => {
    if (!acc[command.category]) acc[command.category] = [];
    acc[command.category].push(command);
    return acc;
  }, {} as Record<string, Command[]>);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'admin': return Settings;
      case 'moderation': return Shield;
      case 'ticket': return Ticket;
      case 'utility': return Zap;
      default: return Terminal;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'admin': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'moderation': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'ticket': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'utility': return 'bg-green-500/20 text-green-400 border-green-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const setupGuide = [
    {
      title: "1. Invite the Bot",
      description: "Add NexGuard to your Discord server with the necessary permissions.",
      content: [
        "Click the 'Invite to Server' button on the home page",
        "Select your server and grant the required permissions",
        "Ensure the bot has Administrator permissions for full functionality"
      ]
    },
    {
      title: "2. Configure Server Settings",
      description: "Set up your server configuration using the /configure command.",
      content: [
        "Use `/configure roles` to set admin, moderator, and mute roles",
        "Use `/configure channels` to set log and welcome channels",
        "Use `/configure moderation` to enable/disable moderation features",
        "Use `/configure tickets` to enable/disable the ticket system"
      ]
    },
    {
      title: "3. Set Command Prefix",
      description: "Customize your server's command prefix (default is !).",
      content: [
        "Use `/setprefix <new_prefix>` to change the command prefix",
        "Choose a unique prefix to avoid conflicts with other bots",
        "The prefix only affects legacy commands, slash commands work regardless"
      ]
    },
    {
      title: "4. Test Basic Commands",
      description: "Verify the bot is working correctly with basic commands.",
      content: [
        "Try `/ping` to check bot responsiveness",
        "Use `/help` to see all available commands",
        "Test `/serverinfo` to view server statistics",
        "Use `/serverstats` (admin only) for detailed server information"
      ]
    }
  ];

  return (
    <div className="min-h-screen hero-gradient circuit-pattern pt-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      <div className="container mx-auto px-4 py-20 relative z-10">
        <PageHeader 
          title="Documentation"
          description="Complete guide to using NexGuard bot commands and features for your Discord server."
        />

        <Tabs defaultValue="setup" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="setup" className="flex items-center gap-2">
              <Book className="w-4 h-4" />
              Setup Guide
            </TabsTrigger>
            <TabsTrigger value="commands" className="flex items-center gap-2">
              <Terminal className="w-4 h-4" />
              Commands
            </TabsTrigger>
            <TabsTrigger value="help" className="flex items-center gap-2">
              <HelpCircle className="w-4 h-4" />
              Support
            </TabsTrigger>
          </TabsList>

          <TabsContent value="setup">
            <div className="space-y-6">
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="text-2xl">
                    <GradientText>Getting Started</GradientText>
                  </CardTitle>
                  <CardDescription>
                    Follow these steps to set up NexGuard on your Discord server
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-8">
                    {setupGuide.map((step, index) => (
                      <div key={index} className="border-l-2 border-[hsl(var(--nexguard-cyan))] pl-6">
                        <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                        <p className="text-gray-400 mb-4">{step.description}</p>
                        <ul className="space-y-2">
                          {step.content.map((item, itemIndex) => (
                            <li key={itemIndex} className="flex items-start gap-2 text-gray-300">
                              <span className="w-1.5 h-1.5 bg-[hsl(var(--nexguard-cyan))] rounded-full mt-2 flex-shrink-0"></span>
                              {item}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
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
                    Search and browse all available bot commands
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="relative mb-6">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      placeholder="Search commands..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  {isLoading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[hsl(var(--nexguard-cyan))] mx-auto"></div>
                      <p className="mt-2 text-gray-400">Loading commands...</p>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {Object.entries(commandsByCategory || {}).map(([category, categoryCommands]) => {
                        const IconComponent = getCategoryIcon(category);
                        return (
                          <div key={category}>
                            <div className="flex items-center gap-2 mb-4">
                              <IconComponent className="w-5 h-5 text-[hsl(var(--nexguard-cyan))]" />
                              <h3 className="text-lg font-semibold text-white capitalize">{category} Commands</h3>
                              <Badge variant="secondary" className={getCategoryColor(category)}>
                                {categoryCommands.length}
                              </Badge>
                            </div>
                            <div className="grid gap-4">
                              {categoryCommands.map((command) => (
                                <Card key={command.id} className="bg-slate-900/50 border-slate-700/50">
                                  <CardHeader className="pb-3">
                                    <div className="flex items-center justify-between">
                                      <CardTitle className="text-base">
                                        <code className="text-[hsl(var(--nexguard-cyan))]">/{command.name}</code>
                                      </CardTitle>
                                      <Badge variant="outline" className={getCategoryColor(command.category)}>
                                        {command.category}
                                      </Badge>
                                    </div>
                                    <CardDescription className="text-sm">
                                      {command.description}
                                    </CardDescription>
                                  </CardHeader>
                                  <CardContent className="pt-0">
                                    <div className="space-y-2">
                                      <div>
                                        <span className="text-sm font-medium text-gray-300">Usage:</span>
                                        <code className="ml-2 text-xs bg-slate-800 px-2 py-1 rounded text-gray-300">
                                          {command.usage}
                                        </code>
                                      </div>
                                      {command.permissions && command.permissions.length > 0 && (
                                        <div>
                                          <span className="text-sm font-medium text-gray-300">Permissions:</span>
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
                          </div>
                        );
                      })}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="help">
            <div className="space-y-6">
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <HelpCircle className="w-5 h-5" />
                    Need Help?
                  </CardTitle>
                  <CardDescription>
                    Get support and assistance with NexGuard
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <Alert>
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>
                        For immediate help, use the <code>/help</code> command in your Discord server to get a quick overview of all available commands.
                      </AlertDescription>
                    </Alert>

                    <div className="grid md:grid-cols-2 gap-6">
                      <Card className="bg-slate-900/50 border-slate-700/50">
                        <CardHeader>
                          <CardTitle className="text-base">Common Issues</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <ul className="space-y-2 text-sm">
                            <li>• Bot not responding? Check if it has the necessary permissions</li>
                            <li>• Commands not working? Verify your role permissions</li>
                            <li>• Moderation features disabled? Use <code>/configure moderation</code></li>
                            <li>• Tickets not working? Enable tickets with <code>/configure tickets</code></li>
                          </ul>
                        </CardContent>
                      </Card>

                      <Card className="bg-slate-900/50 border-slate-700/50">
                        <CardHeader>
                          <CardTitle className="text-base">Support Channels</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <ul className="space-y-2 text-sm">
                            <li>• Use <code>/ticket</code> to create a support ticket</li>
                            <li>• Check our community testimonials for tips</li>
                            <li>• Submit feedback through our feedback form</li>
                            <li>• Browse the changelog for recent updates</li>
                          </ul>
                        </CardContent>
                      </Card>
                    </div>

                    <Card className="bg-slate-900/50 border-slate-700/50">
                      <CardHeader>
                        <CardTitle className="text-base">Permissions Guide</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <div>
                            <h4 className="font-medium text-white mb-2">Required Bot Permissions:</h4>
                            <div className="grid grid-cols-2 gap-2 text-sm">
                              <span>• View Channels</span>
                              <span>• Send Messages</span>
                              <span>• Manage Messages</span>
                              <span>• Embed Links</span>
                              <span>• Read Message History</span>
                              <span>• Add Reactions</span>
                              <span>• Use Slash Commands</span>
                              <span>• Manage Channels</span>
                              <span>• Kick Members</span>
                              <span>• Ban Members</span>
                              <span>• Manage Roles</span>
                              <span>• Moderate Members</span>
                            </div>
                          </div>
                          <div>
                            <h4 className="font-medium text-white mb-2">User Permissions for Commands:</h4>
                            <div className="space-y-1 text-sm">
                              <p>• <strong>Admin Commands:</strong> Require Administrator permission</p>
                              <p>• <strong>Moderation Commands:</strong> Require Moderate Members permission</p>
                              <p>• <strong>Ticket Commands:</strong> Available to all users (creation), staff for management</p>
                              <p>• <strong>Utility Commands:</strong> Available to all users</p>
                            </div>
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