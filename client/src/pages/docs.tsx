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
import { Search, Book, Terminal, Settings, Shield, Ticket, Zap, HelpCircle, AlertCircle, Users } from "lucide-react";
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
        "Ensure the bot has Administrator permissions for full functionality",
        "The bot needs Manage Messages, Manage Roles, Ban Members, and Kick Members permissions"
      ]
    },
    {
      title: "2. Configure Moderation Roles",
      description: "Set up custom moderation roles with hierarchy validation using /modrole.",
      content: [
        "Use `/modrole @Moderator` to set a custom moderation role",
        "Use `/modrole` without parameters to view current moderation role",
        "Use `/resetmodrole` to revert to default Discord permissions",
        "Use `/modpermissions @user` to check moderation permissions for specific users",
        "Ensure moderation roles are below the bot's role in the hierarchy"
      ]
    },
    {
      title: "3. Set Up AutoMod System",
      description: "Configure comprehensive auto-moderation with multiple protection layers.",
      content: [
        "Use `/automod-config` to view current automod status and settings",
        "Configure spam protection: `/automod-spam True 5 10 timeout`",
        "Set up link filtering: `/automod-links True delete`",
        "Enable bad word filtering: `/automod-badwords True True warn`",
        "Manage custom word lists: `/automod-words add [word]` or `/automod-words list`",
        "Reset all settings: `/automod-reset` (with confirmation prompt)"
      ]
    },
    {
      title: "4. Configure Auto-Reply System",
      description: "Create intelligent auto-reply rules with rich embed responses.",
      content: [
        "Create rules: `/autoreply-create welcome-rule hello 'Welcome!' contains blue`",
        "List all rules: `/autoreply-list` to see active rules and statistics",
        "Toggle rules: `/autoreply-toggle rule-name` to enable/disable specific rules",
        "Delete rules: `/autoreply-delete rule-name` with confirmation",
        "View statistics: `/autoreply-stats` for usage analytics and trigger counts",
        "Supports trigger types: contains, exact, starts_with, ends_with"
      ]
    },
    {
      title: "5. Set Up Ticket System",
      description: "Configure multi-category ticket system with Discord integration.",
      content: [
        "Create ticket categories: `/ticketcategory create technical 'Tech Support'`",
        "List categories: `/ticketcategory list` to view all available categories",
        "Users create tickets: `/ticket Need help technical` (with category)",
        "Manage tickets: `/tickets open` to filter and view tickets",
        "Close tickets: `/close-ticket Issue resolved` to archive tickets",
        "Categories are automatically linked to Discord channel categories"
      ]
    },
    {
      title: "6. Configure Welcome System",
      description: "Set up advanced welcome messages with rich embeds and placeholders.",
      content: [
        "Enable welcome: `/welcome enable #welcome-channel`",
        "Set custom message: `/welcome message 'Welcome {user} to {server}!'`",
        "Configure embed mode: `/welcome embed True` for rich embed welcomes",
        "Disable welcome: `/welcome disable` to turn off welcome messages",
        "Supports placeholders: {user}, {server}, {membercount}, {mention}",
        "Customize colors, thumbnails, and interactive elements"
      ]
    },
    {
      title: "7. Test Basic Commands",
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
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="setup" className="flex items-center gap-2">
              <Book className="w-4 h-4" />
              Setup Guide
            </TabsTrigger>
            <TabsTrigger value="advanced" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Advanced
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

          <TabsContent value="advanced">
            <div className="space-y-6">
              {/* Advanced AutoMod Configuration */}
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <Shield className="w-6 h-6 text-red-400" />
                    <GradientText>Advanced AutoMod Configuration</GradientText>
                  </CardTitle>
                  <CardDescription>
                    Deep dive into NexGuard's sophisticated auto-moderation system with spam detection, link filtering, and content analysis.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                  
                  {/* Spam Protection */}
                  <div className="border-l-2 border-red-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Intelligent Spam Protection</h3>
                    <div className="space-y-4">
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-2">Configuration Parameters:</h4>
                        <div className="grid md:grid-cols-2 gap-4 text-sm">
                          <div>
                            <code className="text-cyan-400">/automod-spam enable max_messages time_window action</code>
                            <ul className="mt-2 space-y-1 text-gray-300">
                              <li>• <strong>max_messages:</strong> 1-20 messages (default: 5)</li>
                              <li>• <strong>time_window:</strong> 5-60 seconds (default: 10)</li>
                              <li>• <strong>action:</strong> delete, warn, timeout</li>
                            </ul>
                          </div>
                          <div>
                            <p className="text-gray-300 mb-2">Advanced Examples:</p>
                            <code className="block text-xs bg-slate-800 p-2 rounded text-cyan-400">
                              /automod-spam True 3 5 timeout<br/>
                              # Strict: 3 messages in 5 seconds = timeout
                            </code>
                            <code className="block text-xs bg-slate-800 p-2 rounded text-cyan-400 mt-2">
                              /automod-spam True 8 15 warn<br/>
                              # Lenient: 8 messages in 15 seconds = warn
                            </code>
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-blue-900/20 p-4 rounded-lg border border-blue-500/30">
                        <h4 className="font-medium text-white mb-2">How Spam Detection Works:</h4>
                        <ul className="space-y-2 text-sm text-gray-300">
                          <li>• <strong>Message Tracking:</strong> Every message is logged with timestamp to PostgreSQL database</li>
                          <li>• <strong>Real-time Analysis:</strong> Bot checks recent message count within the time window</li>
                          <li>• <strong>Smart Exemptions:</strong> Moderators and admins are automatically excluded</li>
                          <li>• <strong>Action Escalation:</strong> Delete → Warn → Timeout based on configuration</li>
                          <li>• <strong>Professional Logging:</strong> All actions logged to configured channels with detailed embeds</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Link Filtering */}
                  <div className="border-l-2 border-orange-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Advanced Link Filtering</h3>
                    <div className="space-y-4">
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-2">Link Protection Options:</h4>
                        <div className="grid md:grid-cols-2 gap-4 text-sm">
                          <div>
                            <code className="text-cyan-400">/automod-links enable action [invite_block] [url_block]</code>
                            <ul className="mt-2 space-y-1 text-gray-300">
                              <li>• <strong>invite_block:</strong> Discord invite detection</li>
                              <li>• <strong>url_block:</strong> External link filtering</li>
                              <li>• <strong>Regex Patterns:</strong> Advanced URL detection</li>
                            </ul>
                          </div>
                          <div>
                            <p className="text-gray-300 mb-2">Detected Patterns:</p>
                            <code className="block text-xs bg-slate-800 p-2 rounded text-gray-300">
                              discord.gg/[code]<br/>
                              discord.com/invite/[code]<br/>
                              discordapp.com/invite/[code]<br/>
                              https?://[domain]/[path]
                            </code>
                          </div>
                        </div>
                      </div>
                      
                      <Alert>
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription className="text-sm">
                          <strong>Pro Tip:</strong> Enable invite blocking for community servers to prevent raid attempts. Use URL blocking cautiously in discussion channels.
                        </AlertDescription>
                      </Alert>
                    </div>
                  </div>

                  {/* Bad Word Filtering */}
                  <div className="border-l-2 border-purple-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Intelligent Content Filtering</h3>
                    <div className="space-y-4">
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-2">Word Filter Management:</h4>
                        <div className="space-y-3">
                          <div>
                            <code className="text-cyan-400">/automod-badwords enable strict_mode action</code>
                            <p className="text-sm text-gray-300 mt-1">Configure base filtering behavior</p>
                          </div>
                          <div>
                            <code className="text-cyan-400">/automod-words add|remove|list|clear [word]</code>
                            <p className="text-sm text-gray-300 mt-1">Manage custom word blacklist</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="bg-green-900/20 p-4 rounded-lg border border-green-500/30">
                          <h4 className="font-medium text-white mb-2">Normal Mode:</h4>
                          <ul className="space-y-1 text-sm text-gray-300">
                            <li>• Contains matching</li>
                            <li>• Detects word within text</li>
                            <li>• Higher detection rate</li>
                            <li>• May have false positives</li>
                          </ul>
                        </div>
                        <div className="bg-red-900/20 p-4 rounded-lg border border-red-500/30">
                          <h4 className="font-medium text-white mb-2">Strict Mode:</h4>
                          <ul className="space-y-1 text-sm text-gray-300">
                            <li>• Exact word matching</li>
                            <li>• Requires word boundaries</li>
                            <li>• Fewer false positives</li>
                            <li>• May miss variations</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                </CardContent>
              </Card>

              {/* Advanced Auto-Reply System */}
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <Zap className="w-6 h-6 text-yellow-400" />
                    <GradientText>Advanced Auto-Reply System</GradientText>
                  </CardTitle>
                  <CardDescription>
                    Create sophisticated automated responses with conditional logic, rich embeds, and advanced trigger patterns.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                  
                  <div className="border-l-2 border-yellow-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Trigger Type Strategies</h3>
                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div className="bg-slate-900/50 p-4 rounded-lg">
                          <h4 className="font-medium text-white mb-2">Contains Matching:</h4>
                          <code className="text-cyan-400 text-sm">/autoreply-create help-rule "need help" "How can I assist?" contains</code>
                          <ul className="mt-2 space-y-1 text-sm text-gray-300">
                            <li>• Triggers on partial matches</li>
                            <li>• Best for flexible responses</li>
                            <li>• Example: "I need help with bot" → triggers</li>
                          </ul>
                        </div>
                        
                        <div className="bg-slate-900/50 p-4 rounded-lg">
                          <h4 className="font-medium text-white mb-2">Exact Matching:</h4>
                          <code className="text-cyan-400 text-sm">/autoreply-create ping-rule "ping" "Pong! 🏓" exact</code>
                          <ul className="mt-2 space-y-1 text-sm text-gray-300">
                            <li>• Requires exact message match</li>
                            <li>• Best for specific commands</li>
                            <li>• Example: Only "ping" triggers, not "ping me"</li>
                          </ul>
                        </div>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="bg-slate-900/50 p-4 rounded-lg">
                          <h4 className="font-medium text-white mb-2">Starts With:</h4>
                          <code className="text-cyan-400 text-sm">/autoreply-create welcome-rule "hello" "Welcome!" starts_with</code>
                          <ul className="mt-2 space-y-1 text-sm text-gray-300">
                            <li>• Triggers on message beginning</li>
                            <li>• Best for greeting responses</li>
                            <li>• Example: "hello everyone" → triggers</li>
                          </ul>
                        </div>
                        
                        <div className="bg-slate-900/50 p-4 rounded-lg">
                          <h4 className="font-medium text-white mb-2">Ends With:</h4>
                          <code className="text-cyan-400 text-sm">/autoreply-create question-rule "?" "Great question!" ends_with</code>
                          <ul className="mt-2 space-y-1 text-sm text-gray-300">
                            <li>• Triggers on message ending</li>
                            <li>• Best for question responses</li>
                            <li>• Example: "How does this work?" → triggers</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="border-l-2 border-green-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Rich Embed Responses</h3>
                    <div className="bg-slate-900/50 p-4 rounded-lg">
                      <h4 className="font-medium text-white mb-3">Advanced Embed Configuration:</h4>
                      <div className="space-y-3">
                        <code className="block text-sm bg-slate-800 p-3 rounded text-cyan-400">
                          /autoreply-create support-rule "support" \<br/>
                          &nbsp;&nbsp;title:"🎫 Need Support?" \<br/>
                          &nbsp;&nbsp;description:"Create a ticket with /ticket or check our FAQ!" \<br/>
                          &nbsp;&nbsp;color:"0x00FF00" \<br/>
                          &nbsp;&nbsp;footer:"NexGuard Support • Powered by AI" \<br/>
                          &nbsp;&nbsp;timestamp:true
                        </code>
                        
                        <div className="grid md:grid-cols-3 gap-4 mt-4 text-sm">
                          <div>
                            <h5 className="font-medium text-white mb-2">Color Options:</h5>
                            <ul className="space-y-1 text-gray-300">
                              <li>• <code>0xFF0000</code> - Red</li>
                              <li>• <code>0x00FF00</code> - Green</li>
                              <li>• <code>0x0099FF</code> - Blue</li>
                              <li>• <code>0xFF00FF</code> - Purple</li>
                            </ul>
                          </div>
                          <div>
                            <h5 className="font-medium text-white mb-2">Special Features:</h5>
                            <ul className="space-y-1 text-gray-300">
                              <li>• Timestamp display</li>
                              <li>• Custom footers</li>
                              <li>• Thumbnail support</li>
                              <li>• Field embedding</li>
                            </ul>
                          </div>
                          <div>
                            <h5 className="font-medium text-white mb-2">Best Practices:</h5>
                            <ul className="space-y-1 text-gray-300">
                              <li>• Keep descriptions concise</li>
                              <li>• Use brand colors</li>
                              <li>• Add helpful links</li>
                              <li>• Include call-to-actions</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="border-l-2 border-blue-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Analytics & Optimization</h3>
                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-2">Performance Monitoring:</h4>
                        <code className="text-cyan-400 text-sm">/autoreply-stats [rule_name]</code>
                        <ul className="mt-2 space-y-1 text-sm text-gray-300">
                          <li>• View trigger counts per rule</li>
                          <li>• Analyze usage patterns</li>
                          <li>• Identify popular responses</li>
                          <li>• Optimize rule effectiveness</li>
                        </ul>
                      </div>
                      
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-2">Cooldown Management:</h4>
                        <ul className="space-y-1 text-sm text-gray-300">
                          <li>• Prevent spam with intelligent cooldowns</li>
                          <li>• Per-rule cooldown configuration</li>
                          <li>• User-specific trigger tracking</li>
                          <li>• Automatic cooldown enforcement</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                </CardContent>
              </Card>

              {/* Multi-Server Management */}
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <Settings className="w-6 h-6 text-purple-400" />
                    <GradientText>Multi-Server Management</GradientText>
                  </CardTitle>
                  <CardDescription>
                    Advanced strategies for managing NexGuard across multiple Discord servers with centralized monitoring and distributed configuration.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                  
                  <div className="border-l-2 border-purple-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Server Independence & Configuration</h3>
                    <div className="space-y-4">
                      <Alert>
                        <Settings className="h-4 w-4" />
                        <AlertDescription>
                          <strong>Important:</strong> Each server maintains completely independent settings. AutoMod rules, auto-replies, and moderation configurations are isolated per server.
                        </AlertDescription>
                      </Alert>
                      
                      <div className="grid md:grid-cols-2 gap-6">
                        <div className="bg-slate-900/50 p-4 rounded-lg">
                          <h4 className="font-medium text-white mb-2">Per-Server Settings:</h4>
                          <ul className="space-y-1 text-sm text-gray-300">
                            <li>• Independent AutoMod configurations</li>
                            <li>• Separate auto-reply rule sets</li>
                            <li>• Unique moderation role assignments</li>
                            <li>• Individual logging channel setups</li>
                            <li>• Custom ticket category configurations</li>
                          </ul>
                        </div>
                        
                        <div className="bg-slate-900/50 p-4 rounded-lg">
                          <h4 className="font-medium text-white mb-2">Configuration Templates:</h4>
                          <ul className="space-y-1 text-sm text-gray-300">
                            <li>• Document successful configurations</li>
                            <li>• Create setup checklists</li>
                            <li>• Standardize moderation approaches</li>
                            <li>• Share best practices across servers</li>
                            <li>• Maintain consistent branding</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="border-l-2 border-cyan-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Centralized Monitoring</h3>
                    <div className="bg-slate-900/50 p-4 rounded-lg">
                      <h4 className="font-medium text-white mb-3">Analytics Dashboard Access:</h4>
                      <div className="grid md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <h5 className="font-medium text-white mb-2">Live Statistics:</h5>
                          <ul className="space-y-1 text-gray-300">
                            <li>• Real-time server count</li>
                            <li>• Total user protection</li>
                            <li>• Command execution metrics</li>
                            <li>• Uptime monitoring</li>
                          </ul>
                        </div>
                        <div>
                          <h5 className="font-medium text-white mb-2">Performance Metrics:</h5>
                          <ul className="space-y-1 text-gray-300">
                            <li>• AutoMod action counts</li>
                            <li>• Message processing speed</li>
                            <li>• Error rate tracking</li>
                            <li>• Response time analysis</li>
                          </ul>
                        </div>
                        <div>
                          <h5 className="font-medium text-white mb-2">Health Monitoring:</h5>
                          <ul className="space-y-1 text-gray-300">
                            <li>• Database connectivity</li>
                            <li>• API endpoint status</li>
                            <li>• Service availability</li>
                            <li>• Automated restart capability</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                </CardContent>
              </Card>

              {/* Role Management & Hierarchies */}
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <Users className="w-6 h-6 text-green-400" />
                    <GradientText>Advanced Role Management</GradientText>
                  </CardTitle>
                  <CardDescription>
                    Master complex permission systems, role hierarchies, and custom moderation workflows for enterprise-level Discord server management.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                  
                  <div className="border-l-2 border-green-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Custom Moderation Hierarchies</h3>
                    <div className="space-y-4">
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-3">Role Setup Strategy:</h4>
                        <div className="grid md:grid-cols-2 gap-6">
                          <div>
                            <h5 className="font-medium text-cyan-400 mb-2">Traditional Discord Permissions:</h5>
                            <ul className="space-y-1 text-sm text-gray-300">
                              <li>• Administrator: Full access to all commands</li>
                              <li>• Manage Server: Access to admin commands</li>
                              <li>• Moderate Members: Moderation commands</li>
                              <li>• Manage Messages: Message management</li>
                            </ul>
                          </div>
                          <div>
                            <h5 className="font-medium text-cyan-400 mb-2">NexGuard Custom Roles:</h5>
                            <code className="block text-xs bg-slate-800 p-2 rounded mb-2">
                              /modrole @Senior Moderator<br/>
                              /modrole @Helper<br/>
                              /modrole @Trial Mod
                            </code>
                            <p className="text-sm text-gray-300">Custom roles bypass Discord's default permission requirements</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-blue-900/20 p-4 rounded-lg border border-blue-500/30">
                        <h4 className="font-medium text-white mb-2">Permission Analysis:</h4>
                        <code className="text-cyan-400">/modpermissions @username</code>
                        <p className="text-sm text-gray-300 mt-2">
                          This command provides detailed analysis of user permissions including source (Administrator, Moderate Members, Custom Role) and available command categories.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="border-l-2 border-yellow-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Hierarchy Validation & Security</h3>
                    <div className="space-y-4">
                      <Alert>
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                          <strong>Critical:</strong> NexGuard's role must be positioned higher than any roles it needs to manage. This prevents privilege escalation and ensures proper moderation capabilities.
                        </AlertDescription>
                      </Alert>
                      
                      <div className="grid md:grid-cols-2 gap-6">
                        <div className="bg-red-900/20 p-4 rounded-lg border border-red-500/30">
                          <h4 className="font-medium text-white mb-2">Security Considerations:</h4>
                          <ul className="space-y-1 text-sm text-gray-300">
                            <li>• Bot role positioning in hierarchy</li>
                            <li>• Moderation role validation</li>
                            <li>• Permission escalation prevention</li>
                            <li>• Audit log integration</li>
                            <li>• Emergency override capabilities</li>
                          </ul>
                        </div>
                        
                        <div className="bg-green-900/20 p-4 rounded-lg border border-green-500/30">
                          <h4 className="font-medium text-white mb-2">Best Practices:</h4>
                          <ul className="space-y-1 text-sm text-gray-300">
                            <li>• Regular permission audits</li>
                            <li>• Minimal necessary permissions</li>
                            <li>• Clear role documentation</li>
                            <li>• Staff training programs</li>
                            <li>• Incident response procedures</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                </CardContent>
              </Card>

              {/* Troubleshooting & Performance */}
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <AlertCircle className="w-6 h-6 text-orange-400" />
                    <GradientText>Advanced Troubleshooting</GradientText>
                  </CardTitle>
                  <CardDescription>
                    Expert-level troubleshooting techniques, performance optimization, and diagnostic procedures for complex NexGuard deployments.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                  
                  <div className="border-l-2 border-orange-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Performance Diagnostics</h3>
                    <div className="space-y-4">
                      <div className="grid md:grid-cols-2 gap-6">
                        <div className="bg-slate-900/50 p-4 rounded-lg">
                          <h4 className="font-medium text-white mb-2">Command Response Analysis:</h4>
                          <code className="text-cyan-400 text-sm">/ping</code>
                          <ul className="mt-2 space-y-1 text-sm text-gray-300">
                            <li>• WebSocket latency measurement</li>
                            <li>• API response time tracking</li>
                            <li>• Database connection speed</li>
                            <li>• Discord API rate limit status</li>
                          </ul>
                        </div>
                        
                        <div className="bg-slate-900/50 p-4 rounded-lg">
                          <h4 className="font-medium text-white mb-2">System Health Monitoring:</h4>
                          <code className="text-cyan-400 text-sm">/botstats</code>
                          <ul className="mt-2 space-y-1 text-sm text-gray-300">
                            <li>• Memory usage and optimization</li>
                            <li>• CPU utilization patterns</li>
                            <li>• Network I/O performance</li>
                            <li>• Database query efficiency</li>
                          </ul>
                        </div>
                      </div>
                      
                      <Alert>
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                          <strong>Performance Tip:</strong> High latency (&gt;100ms) may indicate database connection issues or Discord API rate limiting. Check AutoMod settings if response times degrade.
                        </AlertDescription>
                      </Alert>
                    </div>
                  </div>

                  <div className="border-l-2 border-red-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Advanced Error Resolution</h3>
                    <div className="space-y-4">
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-3">Database Connectivity Issues:</h4>
                        <div className="space-y-3 text-sm">
                          <div>
                            <strong className="text-cyan-400">Symptom:</strong>
                            <p className="text-gray-300">Commands timeout or return "Database error"</p>
                          </div>
                          <div>
                            <strong className="text-cyan-400">Diagnosis:</strong>
                            <ul className="space-y-1 text-gray-300">
                              <li>• Check PostgreSQL connection pool status</li>
                              <li>• Verify database server accessibility</li>
                              <li>• Monitor connection timeout settings</li>
                              <li>• Analyze query performance logs</li>
                            </ul>
                          </div>
                          <div>
                            <strong className="text-cyan-400">Resolution:</strong>
                            <ul className="space-y-1 text-gray-300">
                              <li>• Restart bot service for connection reset</li>
                              <li>• Scale database resources if needed</li>
                              <li>• Optimize slow database queries</li>
                              <li>• Implement connection retry logic</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-3">Permission Conflicts:</h4>
                        <div className="space-y-3 text-sm">
                          <div>
                            <strong className="text-cyan-400">Symptom:</strong>
                            <p className="text-gray-300">Commands fail with "Missing Permissions" despite proper role setup</p>
                          </div>
                          <div>
                            <strong className="text-cyan-400">Advanced Debugging:</strong>
                            <code className="block bg-slate-800 p-2 rounded text-cyan-400 mt-2">
                              /modpermissions @user<br/>
                              /modrole<br/>
                              # Analyze permission sources and conflicts
                            </code>
                          </div>
                          <div>
                            <strong className="text-cyan-400">Common Causes:</strong>
                            <ul className="space-y-1 text-gray-300">
                              <li>• Bot role positioned below target user's role</li>
                              <li>• Channel-specific permission overwrites</li>
                              <li>• Role hierarchy conflicts</li>
                              <li>• Custom mod role misconfiguration</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="border-l-2 border-blue-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">AutoMod Performance Optimization</h3>
                    <div className="space-y-4">
                      <div className="bg-blue-900/20 p-4 rounded-lg border border-blue-500/30">
                        <h4 className="font-medium text-white mb-2">Message Processing Optimization:</h4>
                        <ul className="space-y-1 text-sm text-gray-300">
                          <li>• <strong>Database Indexing:</strong> Ensure proper indexes on message analytics tables</li>
                          <li>• <strong>Batch Processing:</strong> Group similar automod actions for efficiency</li>
                          <li>• <strong>Regex Optimization:</strong> Use efficient patterns for link/word detection</li>
                          <li>• <strong>Caching Strategy:</strong> Cache frequent automod rule lookups</li>
                          <li>• <strong>Rate Limiting:</strong> Implement smart rate limiting to prevent API overload</li>
                        </ul>
                      </div>
                      
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="bg-green-900/20 p-4 rounded-lg border border-green-500/30">
                          <h4 className="font-medium text-white mb-2">Optimal Settings:</h4>
                          <ul className="space-y-1 text-sm text-gray-300">
                            <li>• Spam threshold: 5 messages/10 seconds</li>
                            <li>• Word filter: Strict mode for accuracy</li>
                            <li>• Link filtering: Selective enable</li>
                            <li>• Logging: Essential actions only</li>
                          </ul>
                        </div>
                        
                        <div className="bg-yellow-900/20 p-4 rounded-lg border border-yellow-500/30">
                          <h4 className="font-medium text-white mb-2">Performance Monitoring:</h4>
                          <ul className="space-y-1 text-sm text-gray-300">
                            <li>• Track message processing latency</li>
                            <li>• Monitor database query times</li>
                            <li>• Analyze false positive rates</li>
                            <li>• Review action effectiveness</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                </CardContent>
              </Card>

              {/* API Reference & Integration */}
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <Terminal className="w-6 h-6 text-cyan-400" />
                    <GradientText>API Reference & Integration</GradientText>
                  </CardTitle>
                  <CardDescription>
                    Technical reference for NexGuard's internal APIs, webhook integrations, and external service connections for advanced automation workflows.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                  
                  <div className="border-l-2 border-cyan-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Internal API Endpoints</h3>
                    <div className="space-y-4">
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-3">Bot Status & Analytics:</h4>
                        <div className="space-y-3">
                          <div>
                            <code className="text-cyan-400">GET /api/bot/status</code>
                            <p className="text-sm text-gray-300 mt-1">Live bot status, guild count, user count, uptime</p>
                            <code className="block text-xs bg-slate-800 p-2 rounded text-gray-300 mt-2">
                              {`{
  "isOnline": true,
  "guildsCount": 9,
  "usersCount": 168,
  "uptime": "2d 4h 23m",
  "version": "2.1.0"
}`}
                            </code>
                          </div>
                          
                          <div>
                            <code className="text-cyan-400">GET /api/bot/commands</code>
                            <p className="text-sm text-gray-300 mt-1">Complete command reference with metadata</p>
                            <code className="block text-xs bg-slate-800 p-2 rounded text-gray-300 mt-2">
                              {`[{
  "name": "automod-config",
  "description": "Configure AutoMod settings",
  "category": "admin",
  "usage": "/automod-config",
  "permissions": ["Administrator"]
}]`}
                            </code>
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-3">Analytics Data:</h4>
                        <div className="space-y-3">
                          <div>
                            <code className="text-cyan-400">GET /api/analytics/server/{guild_id}</code>
                            <p className="text-sm text-gray-300 mt-1">Server-specific analytics and metrics</p>
                          </div>
                          
                          <div>
                            <code className="text-cyan-400">GET /api/analytics/automod/{guild_id}</code>
                            <p className="text-sm text-gray-300 mt-1">AutoMod action statistics and trends</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="border-l-2 border-purple-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Command Parameter Reference</h3>
                    <div className="space-y-4">
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-3">Advanced Command Syntax:</h4>
                        <div className="space-y-4">
                          <div>
                            <h5 className="font-medium text-cyan-400 mb-2">AutoMod Configuration:</h5>
                            <code className="block text-sm bg-slate-800 p-3 rounded text-gray-300">
                              /automod-spam &lt;enable: boolean&gt; [max_messages: 1-20] [time_window: 5-60] [action: delete|warn|timeout]<br/>
                              /automod-links &lt;enable: boolean&gt; [action: delete|warn|timeout] [invite_block: boolean] [url_block: boolean]<br/>
                              /automod-badwords &lt;enable: boolean&gt; [strict_mode: boolean] [action: delete|warn|timeout]
                            </code>
                          </div>
                          
                          <div>
                            <h5 className="font-medium text-cyan-400 mb-2">Auto-Reply Creation:</h5>
                            <code className="block text-sm bg-slate-800 p-3 rounded text-gray-300">
                              /autoreply-create &lt;rule_name: string&gt; &lt;trigger: string&gt; &lt;response: string&gt; \<br/>
                              &nbsp;&nbsp;[trigger_type: contains|exact|starts_with|ends_with] \<br/>
                              &nbsp;&nbsp;[embed_color: hex_color] [embed_title: string] [embed_description: string]
                            </code>
                          </div>
                          
                          <div>
                            <h5 className="font-medium text-cyan-400 mb-2">Moderation Commands:</h5>
                            <code className="block text-sm bg-slate-800 p-3 rounded text-gray-300">
                              /ban &lt;user: member&gt; [reason: string] [duration: 1d|7d|30d|permanent] [delete_messages: 0-7]<br/>
                              /warn &lt;user: member&gt; &lt;reason: string&gt; [severity: minor|moderate|serious|severe]<br/>
                              /timeout &lt;user: member&gt; &lt;duration: 60s-28d&gt; [reason: string]
                            </code>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="border-l-2 border-green-400 pl-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Best Practices & Standards</h3>
                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-2">Security Guidelines:</h4>
                        <ul className="space-y-1 text-sm text-gray-300">
                          <li>• Implement role hierarchy validation</li>
                          <li>• Use audit logging for all actions</li>
                          <li>• Regular permission audits</li>
                          <li>• Secure API endpoint access</li>
                          <li>• Rate limiting protection</li>
                        </ul>
                      </div>
                      
                      <div className="bg-slate-900/50 p-4 rounded-lg">
                        <h4 className="font-medium text-white mb-2">Performance Standards:</h4>
                        <ul className="space-y-1 text-sm text-gray-300">
                          <li>• &lt;50ms command response time</li>
                          <li>• &lt;100ms automod processing</li>
                          <li>• 99.9% uptime target</li>
                          <li>• Efficient database queries</li>
                          <li>• Optimized memory usage</li>
                        </ul>
                      </div>
                    </div>
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
                              <p>• <strong>Admin Commands (15):</strong> Administrator permission required</p>
                              <p>• <strong>Moderation Commands (17):</strong> Moderate Members permission required</p>
                              <p>• <strong>Ticket Commands (4):</strong> Available to all users (creation), staff for management</p>
                              <p>• <strong>Utility Commands (11):</strong> Available to all users</p>
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