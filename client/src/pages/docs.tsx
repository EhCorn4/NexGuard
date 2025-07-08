import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { StaggerContainer, StaggerItem } from "@/components/ui/stagger-container";
import { PageTransition } from "@/components/ui/page-transition";
import { 
  Search, 
  Shield, 
  Settings, 
  Users, 
  MessageSquare, 
  Bot,
  Zap,
  Heart,
  ChevronRight,
  ExternalLink,
  Book,
  HelpCircle,
  Star,
  AlertCircle,
  CheckCircle,
  Clock,
  ArrowRight
} from "lucide-react";

interface DocSection {
  id: string;
  title: string;
  icon: any;
  articles: DocArticle[];
}

interface DocArticle {
  id: string;
  title: string;
  content: string;
  tags: string[];
  difficulty: "beginner" | "intermediate" | "advanced";
}

export default function Docs() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<DocArticle | null>(null);

  const docSections: DocSection[] = [
    {
      id: "getting-started",
      title: "Getting Started",
      icon: Book,
      articles: [
        {
          id: "setup",
          title: "Setting up NexGuard",
          content: `Welcome to NexGuard! Follow these steps to get started:

1. **Invite NexGuard to your server**
   - Use the invite link with proper permissions
   - Ensure NexGuard has Administrator permissions
   - Place NexGuard's role above other roles

2. **Initial Configuration**
   - Run /setup to begin initial setup
   - Configure basic moderation settings
   - Set up logging channels

3. **Test the Bot**
   - Try basic commands like /help
   - Test moderation features in a test channel
   - Verify logging is working correctly

**Important Notes:**
- NexGuard requires specific permissions to function properly
- Always test new features in a controlled environment
- Keep your server's rules updated as you configure NexGuard`,
          tags: ["setup", "invite", "permissions"],
          difficulty: "beginner"
        },
        {
          id: "first-steps",
          title: "First Steps After Installation",
          content: `Once NexGuard is installed, here's what to do next:

**1. Configure Basic Settings**
- Set up moderation log channel: /config logs set #mod-logs
- Configure auto-moderation: /automod setup
- Set welcome messages: /welcome setup

**2. Create Role Hierarchies**
- Ensure NexGuard's role is properly positioned
- Set up moderation team roles
- Configure auto-roles for new members

**3. Test Core Features**
- Test warning system: /warn @user reason
- Test mute functionality: /mute @user duration
- Verify logging is working correctly

**4. Customize for Your Server**
- Set up custom commands
- Configure economy system (if desired)
- Set up reaction roles`,
          tags: ["configuration", "setup", "commands"],
          difficulty: "beginner"
        }
      ]
    },
    {
      id: "moderation",
      title: "Moderation",
      icon: Shield,
      articles: [
        {
          id: "basic-moderation",
          title: "Basic Moderation Commands",
          content: `NexGuard provides comprehensive moderation tools:

**Warning System**
- /warn @user [reason] - Issue a warning
- /warnings @user - View user's warnings
- /clearwarnings @user - Clear all warnings

**Timeout/Mute System**
- /timeout @user [duration] [reason] - Timeout a user
- /untimeout @user - Remove timeout
- /mute @user [duration] [reason] - Mute a user
- /unmute @user - Unmute a user

**Kick and Ban**
- /kick @user [reason] - Kick a user
- /ban @user [duration] [reason] - Ban a user
- /unban @user - Unban a user
- /tempban @user [duration] [reason] - Temporary ban

**Bulk Actions**
- /purge [amount] - Delete multiple messages
- /purge @user [amount] - Delete messages from specific user
- /lockdown [channel] - Lock channel temporarily`,
          tags: ["moderation", "commands", "warnings", "bans"],
          difficulty: "beginner"
        },
        {
          id: "automod",
          title: "Auto-Moderation Setup",
          content: `Configure automatic moderation to keep your server clean:

**Anti-Spam Protection**
- Message spam detection
- Duplicate message filtering
- Rate limiting configuration
- Punishment escalation

**Content Filtering**
- Profanity filter with custom word lists
- Link filtering and whitelist
- Image and attachment scanning
- Mention spam protection

**Configuration Commands**
- /automod enable [feature] - Enable auto-mod feature
- /automod disable [feature] - Disable auto-mod feature
- /automod settings - View current settings
- /automod whitelist add/remove - Manage whitelists

**Advanced Features**
- Custom regex patterns
- Punishment escalation rules
- Bypass roles and channels
- Custom violation responses`,
          tags: ["automod", "spam", "filtering", "automation"],
          difficulty: "intermediate"
        }
      ]
    },
    {
      id: "configuration",
      title: "Configuration",
      icon: Settings,
      articles: [
        {
          id: "server-settings",
          title: "Server Configuration",
          content: `Customize NexGuard for your server's needs:

**Basic Settings**
- Server prefix: /config prefix [new_prefix]
- Moderation logs: /config logs #channel
- Default punishments: /config punishments

**Welcome/Leave Messages**
- Welcome channel: /welcome channel #channel
- Welcome message: /welcome message [message]
- Leave messages: /leave setup
- Custom embed styling

**Role Management**
- Auto-roles: /autorole setup
- Reaction roles: /reactionrole setup
- Moderation roles: /config modroles

**Economy Settings**
- Enable economy: /economy enable
- Daily rewards: /economy daily-amount [amount]
- Shop setup: /shop setup
- Currency name: /economy currency [name]`,
          tags: ["configuration", "settings", "welcome", "economy"],
          difficulty: "intermediate"
        },
        {
          id: "permissions",
          title: "Permission Management",
          content: `Understanding and configuring NexGuard permissions:

**Required Permissions**
- Administrator (recommended)
- Manage Messages
- Manage Roles
- Manage Channels
- Ban Members
- Kick Members

**Permission Hierarchy**
- NexGuard's role must be above moderated roles
- Users with higher roles cannot be moderated
- Permission overwrites in channels

**Custom Permission Setup**
- /permissions setup - Configure custom permissions
- /permissions role @role [command] - Grant command access
- /permissions user @user [command] - Grant user access
- /permissions channel #channel [command] - Channel-specific permissions

**Troubleshooting**
- Common permission errors
- Role hierarchy issues
- Channel permission conflicts`,
          tags: ["permissions", "roles", "hierarchy", "troubleshooting"],
          difficulty: "advanced"
        }
      ]
    },
    {
      id: "features",
      title: "Features",
      icon: Zap,
      articles: [
        {
          id: "custom-commands",
          title: "Custom Commands",
          content: `Create custom commands for your server:

**Basic Custom Commands**
- /customcmd create [name] [response] - Create basic command
- /customcmd edit [name] [response] - Edit existing command
- /customcmd delete [name] - Delete command
- /customcmd list - View all custom commands

**Advanced Features**
- Variables: {user}, {server}, {channel}
- Conditional responses
- Embed formatting
- Role restrictions

**Examples**
- Rules command: /customcmd create rules "Please read #rules"
- Info command with variables: /customcmd create info "Welcome {user} to {server}!"
- Embed command: /customcmd create welcome --embed --title "Welcome!" --description "Hello {user}"

**Best Practices**
- Use clear command names
- Keep responses concise
- Test commands before deploying
- Regular cleanup of unused commands`,
          tags: ["custom-commands", "automation", "variables"],
          difficulty: "intermediate"
        },
        {
          id: "economy-system",
          title: "Economy System",
          content: `Set up and manage the economy system:

**Basic Economy Setup**
- /economy enable - Enable economy system
- /economy currency [name] - Set currency name
- /economy daily-amount [amount] - Set daily reward
- /economy starting-balance [amount] - Set starting balance

**User Commands**
- /balance [@user] - Check balance
- /daily - Claim daily reward
- /pay @user [amount] - Send money to user
- /leaderboard - View server leaderboard

**Shop System**
- /shop setup - Initialize shop
- /shop add [item] [price] [description] - Add shop item
- /shop remove [item] - Remove shop item
- /shop buy [item] - Purchase item (user command)

**Advanced Features**
- Work commands for earning
- Gambling commands (if enabled)
- Role rewards and purchases
- Custom item effects`,
          tags: ["economy", "currency", "shop", "rewards"],
          difficulty: "intermediate"
        }
      ]
    },
    {
      id: "troubleshooting",
      title: "Troubleshooting",
      icon: AlertCircle,
      articles: [
        {
          id: "common-issues",
          title: "Common Issues",
          content: `Solutions to frequently encountered problems:

**Bot Not Responding**
- Check if bot is online
- Verify permissions
- Check role hierarchy
- Restart with /restart (admin only)

**Commands Not Working**
- Check command syntax
- Verify user permissions
- Check channel permissions
- Review command cooldowns

**Moderation Issues**
- Role hierarchy problems
- Permission conflicts
- Auto-mod false positives
- Logging not working

**Performance Issues**
- High latency responses
- Command timeouts
- Database connection issues
- Rate limiting problems

**Getting Help**
- Use /support for immediate assistance
- Check status page for outages
- Report bugs via /bugreport
- Join support server for live help`,
          tags: ["troubleshooting", "issues", "support", "bugs"],
          difficulty: "beginner"
        }
      ]
    }
  ];

  const filteredSections = docSections.map(section => ({
    ...section,
    articles: section.articles.filter(article =>
      article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      article.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      article.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    )
  })).filter(section => section.articles.length > 0);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "beginner": return "bg-green-500/20 text-green-400";
      case "intermediate": return "bg-yellow-500/20 text-yellow-400";
      case "advanced": return "bg-red-500/20 text-red-400";
      default: return "bg-gray-500/20 text-gray-400";
    }
  };

  if (selectedArticle) {
    return (
      <PageTransition>
        <div className="min-h-screen hero-gradient circuit-pattern pt-20 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
          <div className="container mx-auto px-4 py-8 relative z-10">
            <div className="max-w-4xl mx-auto">
              <Button 
                onClick={() => setSelectedArticle(null)}
                variant="ghost"
                className="text-gray-400 hover:text-white mb-4"
              >
                ← Back to Documentation
              </Button>
              
              <Card className="bg-slate-800/80 border-slate-700 backdrop-blur-sm">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-2xl text-white mb-2">
                        {selectedArticle.title}
                      </CardTitle>
                      <div className="flex items-center gap-2">
                        <Badge className={getDifficultyColor(selectedArticle.difficulty)}>
                          {selectedArticle.difficulty}
                        </Badge>
                        {selectedArticle.tags.map(tag => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-invert max-w-none">
                    <div className="whitespace-pre-wrap text-gray-300 leading-relaxed">
                      {selectedArticle.content}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-screen hero-gradient circuit-pattern pt-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
        <div className="container mx-auto px-4 py-8 relative z-10">
          <PageHeader
            title="Documentation & Help Center"
            description="Everything you need to know about NexGuard"
          />

          {/* Search Bar */}
          <div className="max-w-2xl mx-auto mb-12">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                placeholder="Search documentation..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-slate-800/50 border-slate-700 text-white placeholder-gray-400"
              />
            </div>
          </div>

          {/* Documentation Sections */}
          <StaggerContainer className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredSections.map((section, index) => (
              <StaggerItem key={section.id} index={index}>
                <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors h-full">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <section.icon className="w-5 h-5 text-cyan-400" />
                      {section.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {section.articles.map((article) => (
                        <div 
                          key={article.id}
                          className="p-3 bg-slate-700/50 rounded-lg hover:bg-slate-700/70 transition-colors cursor-pointer"
                          onClick={() => setSelectedArticle(article)}
                        >
                          <div className="flex items-center justify-between">
                            <h3 className="text-white font-medium text-sm">{article.title}</h3>
                            <ChevronRight className="w-4 h-4 text-gray-400" />
                          </div>
                          <div className="flex items-center gap-2 mt-2">
                            <Badge className={`text-xs ${getDifficultyColor(article.difficulty)}`}>
                              {article.difficulty}
                            </Badge>
                            <span className="text-xs text-gray-400">
                              {article.tags.slice(0, 2).join(", ")}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </StaggerItem>
            ))}
          </StaggerContainer>

          {/* Quick Links */}
          <div className="mt-16">
            <h2 className="text-2xl font-bold text-white mb-6 text-center">Need More Help?</h2>
            <StaggerContainer className="grid gap-4 md:grid-cols-3">
              <StaggerItem index={0}>
                <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors">
                  <CardHeader className="text-center">
                    <MessageSquare className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
                    <CardTitle className="text-white">Support Server</CardTitle>
                  </CardHeader>
                  <CardContent className="text-center">
                    <p className="text-gray-400 mb-4">Join our Discord server for live support</p>
                    <Button className="bg-[#5865F2] hover:bg-[#4752C4] text-white">
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Join Server
                    </Button>
                  </CardContent>
                </Card>
              </StaggerItem>
              <StaggerItem index={1}>
                <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors">
                  <CardHeader className="text-center">
                    <HelpCircle className="w-8 h-8 text-green-400 mx-auto mb-2" />
                    <CardTitle className="text-white">FAQ</CardTitle>
                  </CardHeader>
                  <CardContent className="text-center">
                    <p className="text-gray-400 mb-4">Common questions and answers</p>
                    <Button variant="outline" className="border-slate-600 text-gray-300">
                      View FAQ
                    </Button>
                  </CardContent>
                </Card>
              </StaggerItem>
              <StaggerItem index={2}>
                <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors">
                  <CardHeader className="text-center">
                    <AlertCircle className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                    <CardTitle className="text-white">Report Bug</CardTitle>
                  </CardHeader>
                  <CardContent className="text-center">
                    <p className="text-gray-400 mb-4">Found an issue? Let us know</p>
                    <Button variant="outline" className="border-slate-600 text-gray-300">
                      Report Issue
                    </Button>
                  </CardContent>
                </Card>
              </StaggerItem>
            </StaggerContainer>
          </div>
        </div>
      </div>
    </PageTransition>
  );
}