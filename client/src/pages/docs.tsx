import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { 
  Search, 
  BookOpen, 
  Settings, 
  Shield, 
  Users, 
  Bot, 
  ChevronDown, 
  ChevronRight,
  ExternalLink,
  MessageSquare,
  Zap,
  Lock,
  Star
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
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedSections, setExpandedSections] = useState<string[]>(["getting-started"]);

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => 
      prev.includes(sectionId) 
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  const docSections: DocSection[] = [
    {
      id: "getting-started",
      title: "Getting Started",
      icon: BookOpen,
      articles: [
        {
          id: "invite-bot",
          title: "How to Invite NexGuard to Your Server",
          content: `1. Click the "Invite Bot" button on our website
2. Select your Discord server from the dropdown
3. Choose the permissions NexGuard needs (we recommend keeping all permissions for full functionality)
4. Click "Authorize" to complete the setup
5. Use /setup command in your server to begin configuration

After invitation, NexGuard will automatically create necessary channels and roles if they don't exist.`,
          tags: ["setup", "invitation", "basic"],
          difficulty: "beginner"
        },
        {
          id: "basic-setup",
          title: "Basic Server Setup",
          content: `After inviting NexGuard, follow these steps:

**Step 1: Run Setup Command**
Use \`/setup\` in any channel to start the configuration wizard.

**Step 2: Configure Moderation**
- Set moderation log channel
- Choose auto-moderation strictness level
- Configure warning thresholds

**Step 3: Set Up Roles**
- Define moderator roles
- Configure auto-role assignment
- Set up role rewards

**Step 4: Test Configuration**
Use \`/test\` command to verify all settings are working correctly.`,
          tags: ["setup", "configuration", "commands"],
          difficulty: "beginner"
        },
        {
          id: "first-commands",
          title: "Essential Commands to Know",
          content: `**Basic Commands:**
- \`/help\` - Shows all available commands
- \`/setup\` - Initial server configuration
- \`/config\` - View current settings
- \`/test\` - Test bot functionality

**Moderation Commands:**
- \`/warn @user [reason]\` - Warn a user
- \`/mute @user [time] [reason]\` - Temporarily mute a user
- \`/ban @user [reason]\` - Ban a user
- \`/kick @user [reason]\` - Kick a user

**Info Commands:**
- \`/userinfo @user\` - Get user information
- \`/serverinfo\` - Get server statistics
- \`/botinfo\` - Get bot information`,
          tags: ["commands", "moderation", "basic"],
          difficulty: "beginner"
        }
      ]
    },
    {
      id: "moderation",
      title: "Moderation Features",
      icon: Shield,
      articles: [
        {
          id: "auto-mod",
          title: "Auto-Moderation Settings",
          content: `NexGuard's auto-moderation system can automatically handle common issues:

**Spam Detection:**
- Message flooding protection
- Repeated character detection
- Link spam filtering
- Mention spam prevention

**Content Filtering:**
- Profanity filter with customizable word lists
- NSFW content detection
- Scam link protection
- Malicious file scanning

**Configuration Options:**
Use \`/automod config\` to adjust:
- Sensitivity levels (Low, Medium, High, Custom)
- Whitelist channels or roles
- Set custom punishment actions
- Configure bypass permissions`,
          tags: ["automod", "spam", "filtering"],
          difficulty: "intermediate"
        },
        {
          id: "raid-protection",
          title: "Raid Protection",
          content: `Protect your server from coordinated attacks:

**Anti-Raid Features:**
- Mass join detection (configurable thresholds)
- Automatic server lockdown
- IP address monitoring
- Account age filtering

**Configuration:**
1. Use \`/raidprotection setup\`
2. Set join rate limits (e.g., 5 joins per 10 seconds)
3. Configure minimum account age (e.g., 7 days)
4. Set automatic actions (kick, ban, or verify)

**Manual Controls:**
- \`/lockdown\` - Immediately lock server
- \`/unlock\` - Remove lockdown
- \`/raid status\` - Check current threat level`,
          tags: ["raid", "protection", "security"],
          difficulty: "advanced"
        },
        {
          id: "warning-system",
          title: "Warning and Punishment System",
          content: `Set up automated punishment escalation:

**Warning Levels:**
1. First offense: Verbal warning
2. Second offense: 1-hour mute
3. Third offense: 24-hour mute
4. Fourth offense: 7-day temporary ban
5. Fifth offense: Permanent ban

**Configuration:**
- \`/warnings config\` - Set up punishment ladder
- \`/warnings view @user\` - Check user's warning history
- \`/warnings remove @user [id]\` - Remove specific warning
- \`/warnings clear @user\` - Clear all warnings

**Custom Punishment Actions:**
- Temporary mutes (minutes to days)
- Role removals/additions
- Channel restrictions
- Custom messages`,
          tags: ["warnings", "punishment", "moderation"],
          difficulty: "intermediate"
        }
      ]
    },
    {
      id: "dashboard",
      title: "Web Dashboard",
      icon: Settings,
      articles: [
        {
          id: "dashboard-overview",
          title: "Dashboard Overview",
          content: `Access your server's web dashboard at dashboard.nexguard.bot

**Main Features:**
- Real-time server statistics
- Moderation log viewing
- User management interface
- Configuration settings panel

**Getting Started:**
1. Log in with your Discord account
2. Select your server from the list
3. Verify you have admin permissions
4. Start configuring settings

**Key Sections:**
- **Overview:** Server stats and recent activity
- **Moderation:** Logs, warnings, and bans
- **Settings:** Bot configuration options
- **Users:** Member management tools`,
          tags: ["dashboard", "web", "overview"],
          difficulty: "beginner"
        },
        {
          id: "advanced-config",
          title: "Advanced Configuration",
          content: `Fine-tune NexGuard for your specific needs:

**Custom Commands:**
- Create server-specific commands
- Set up auto-responses
- Configure command aliases
- Restrict command usage by role

**Channel Management:**
- Auto-channel creation
- Channel-specific rules
- Message archiving
- Slow mode automation

**Role Management:**
- Auto-role assignment based on activity
- Reaction roles setup
- Role hierarchy respect
- Custom role permissions

**Integration Settings:**
- Webhook configurations
- Third-party bot integration
- API access management
- Backup and restore options`,
          tags: ["advanced", "customization", "integration"],
          difficulty: "advanced"
        }
      ]
    },
    {
      id: "community",
      title: "Community Features",
      icon: Users,
      articles: [
        {
          id: "engagement-tools",
          title: "Community Engagement Tools",
          content: `Keep your community active and engaged:

**Mini-Games:**
- Trivia competitions with custom questions
- Word games and riddles
- Daily challenges and rewards
- Leaderboards and achievements

**Activity Tracking:**
- Member activity scoring
- Recognition for active members
- Weekly/monthly activity reports
- Custom activity rewards

**Events and Announcements:**
- Scheduled event reminders
- Automatic role assignments for events
- Event feedback collection
- Community polls and surveys

**Setup Commands:**
- \`/games setup\` - Configure mini-games
- \`/activity config\` - Set up activity tracking
- \`/events create\` - Schedule community events`,
          tags: ["engagement", "games", "events"],
          difficulty: "intermediate"
        },
        {
          id: "verification",
          title: "Member Verification System",
          content: `Ensure your community stays safe with verification:

**Verification Methods:**
- Phone number verification
- Email verification
- CAPTCHA challenges
- Account age requirements

**Setup Process:**
1. Use \`/verification setup\`
2. Choose verification methods
3. Set requirements (account age, phone, etc.)
4. Configure verified role permissions
5. Test the verification flow

**Customization Options:**
- Custom verification messages
- Multiple verification levels
- Bypass roles for trusted members
- Integration with existing role systems

**Benefits:**
- Reduces spam and bot accounts
- Improves community quality
- Provides additional security layer`,
          tags: ["verification", "security", "members"],
          difficulty: "intermediate"
        }
      ]
    },
    {
      id: "troubleshooting",
      title: "Troubleshooting",
      icon: Zap,
      articles: [
        {
          id: "common-issues",
          title: "Common Issues and Solutions",
          content: `**Bot Not Responding:**
- Check if bot has necessary permissions
- Verify bot is online (check our status page)
- Ensure commands are typed correctly
- Try using commands in different channels

**Permissions Issues:**
- Bot needs Administrator permission for full functionality
- Check channel-specific permissions
- Verify role hierarchy (bot role above managed roles)
- Review Discord's permission system

**Auto-Moderation Not Working:**
- Check if auto-mod is enabled (\`/automod status\`)
- Verify channels aren't whitelisted
- Review sensitivity settings
- Check if user has bypass permissions

**Commands Not Working:**
- Ensure proper command syntax
- Check if command is enabled for the channel
- Verify user has required permissions
- Try using commands in DMs with the bot`,
          tags: ["troubleshooting", "issues", "support"],
          difficulty: "beginner"
        },
        {
          id: "performance-optimization",
          title: "Performance Optimization",
          content: `Optimize NexGuard for the best performance:

**Server Settings:**
- Limit auto-moderation to active channels only
- Configure appropriate log retention periods
- Use channel whitelists for heavy features
- Optimize database cleanup schedules

**Large Server Considerations:**
- Enable batched processing for large member lists
- Use selective auto-moderation rules
- Configure tiered permission systems
- Implement efficient role caching

**Monitoring Tools:**
- \`/performance stats\` - View bot performance metrics
- \`/logs errors\` - Check for recent errors
- \`/health check\` - Comprehensive system check

**Best Practices:**
- Regular configuration reviews
- Periodic permission audits
- Performance monitoring
- Keep bot updated with latest features`,
          tags: ["performance", "optimization", "large-servers"],
          difficulty: "advanced"
        }
      ]
    }
  ];

  const filteredSections = docSections.map(section => ({
    ...section,
    articles: section.articles.filter(article =>
      article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    )
  })).filter(section => section.articles.length > 0);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "beginner": return "bg-green-600/20 text-green-300 border-green-600/30";
      case "intermediate": return "bg-yellow-600/20 text-yellow-300 border-yellow-600/30";
      case "advanced": return "bg-red-600/20 text-red-300 border-red-600/30";
      default: return "bg-gray-600/20 text-gray-300 border-gray-600/30";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 pt-20">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-4">
              Documentation & Help Center
            </h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-8">
              Everything you need to know about setting up and using NexGuard
            </p>

            {/* Search */}
            <div className="relative max-w-md mx-auto">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                placeholder="Search documentation..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-slate-800 border-slate-700 text-white placeholder:text-gray-400"
              />
            </div>
          </div>

          {/* Quick Links */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
            <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors cursor-pointer">
              <CardContent className="p-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-green-600/20 rounded-lg">
                    <Bot className="w-6 h-6 text-green-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">Quick Start</h3>
                    <p className="text-sm text-gray-400">Get NexGuard running in 5 minutes</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors cursor-pointer">
              <CardContent className="p-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-600/20 rounded-lg">
                    <MessageSquare className="w-6 h-6 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">Support</h3>
                    <p className="text-sm text-gray-400">Get help from our community</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors cursor-pointer">
              <CardContent className="p-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-purple-600/20 rounded-lg">
                    <Star className="w-6 h-6 text-purple-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">Examples</h3>
                    <p className="text-sm text-gray-400">See NexGuard in action</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Documentation Sections */}
          <div className="space-y-6">
            {filteredSections.map((section) => (
              <Card key={section.id} className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <Collapsible>
                    <CollapsibleTrigger
                      onClick={() => toggleSection(section.id)}
                      className="flex items-center justify-between w-full text-left hover:text-cyan-400 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <section.icon className="w-6 h-6 text-cyan-400" />
                        <CardTitle className="text-xl font-semibold text-white">
                          {section.title}
                        </CardTitle>
                      </div>
                      {expandedSections.includes(section.id) ? (
                        <ChevronDown className="w-5 h-5" />
                      ) : (
                        <ChevronRight className="w-5 h-5" />
                      )}
                    </CollapsibleTrigger>

                    <CollapsibleContent>
                      <CardContent className="pt-6">
                        <div className="space-y-4">
                          {section.articles.map((article) => (
                            <Card key={article.id} className="bg-slate-700/50 border-slate-600">
                              <CardHeader className="pb-3">
                                <div className="flex items-center justify-between">
                                  <CardTitle className="text-lg font-medium text-white">
                                    {article.title}
                                  </CardTitle>
                                  <div className="flex items-center space-x-2">
                                    <Badge 
                                      variant="outline" 
                                      className={getDifficultyColor(article.difficulty)}
                                    >
                                      {article.difficulty}
                                    </Badge>
                                    <ExternalLink className="w-4 h-4 text-gray-400" />
                                  </div>
                                </div>
                                <div className="flex flex-wrap gap-2 mt-2">
                                  {article.tags.map((tag) => (
                                    <Badge 
                                      key={tag} 
                                      variant="secondary" 
                                      className="bg-purple-600/20 text-purple-300 border-purple-600/30 text-xs"
                                    >
                                      {tag}
                                    </Badge>
                                  ))}
                                </div>
                              </CardHeader>
                              <CardContent>
                                <div className="text-gray-300 leading-relaxed whitespace-pre-line">
                                  {article.content}
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      </CardContent>
                    </CollapsibleContent>
                  </Collapsible>
                </CardHeader>
              </Card>
            ))}
          </div>

          {/* No Results */}
          {searchQuery && filteredSections.length === 0 && (
            <div className="text-center py-12">
              <Search className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No results found</h3>
              <p className="text-gray-400">
                Try searching with different keywords or browse the sections above.
              </p>
            </div>
          )}

          {/* Footer Help */}
          <Card className="mt-12 bg-slate-800/50 border-slate-700">
            <CardContent className="p-6">
              <div className="text-center">
                <h3 className="text-xl font-semibold text-white mb-2">Still need help?</h3>
                <p className="text-gray-300 mb-4">
                  Can't find what you're looking for? Our support team is here to help.
                </p>
                <div className="flex justify-center space-x-4">
                  <div className="flex items-center space-x-2 text-sm text-gray-400">
                    <MessageSquare className="w-4 h-4" />
                    <span>Join our Discord support server</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-400">
                    <MessageSquare className="w-4 h-4" />
                    <span>Email: nexguards@gmail.com</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}