import { useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Shield, 
  Settings, 
  Users, 
  MessageSquare, 
  Zap, 
  HelpCircle,
  Bot,
  Lock,
  AlertTriangle,
  CheckCircle
} from "lucide-react";
import { Link } from "wouter";
import nexguardIcon from "@assets/file_0000000003fc61f58b4fd114190f81c9_1751936993313.png";

interface FAQCategory {
  id: string;
  title: string;
  icon: React.ComponentType<any>;
  description: string;
  questions: Array<{
    question: string;
    answer: string;
    tags?: string[];
  }>;
}

const faqCategories: FAQCategory[] = [
  {
    id: "setup",
    title: "Setup & Installation",
    icon: Bot,
    description: "Getting started with NexGuard",
    questions: [
      {
        question: "How do I invite NexGuard to my Discord server?",
        answer: "Visit our Invite page and click the 'Add to Server' button. You'll need 'Manage Server' permission in your Discord server. Make sure to grant NexGuard the necessary permissions like 'Manage Messages', 'Ban Members', 'Kick Members', and 'Moderate Members' for full functionality.",
        tags: ["invite", "permissions"]
      },
      {
        question: "What permissions does NexGuard need?",
        answer: "NexGuard requires several key permissions: Manage Messages (for moderation), Ban/Kick Members (for enforcement), Moderate Members (for timeouts), Manage Channels (for lock/unlock), View Channels, Send Messages, Embed Links, and Read Message History. These permissions ensure all 44+ commands work properly.",
        tags: ["permissions", "setup"]
      },
      {
        question: "How do I configure NexGuard for my server?",
        answer: "Start with `/botlogging` to set up command logging, then use `/welcome` for welcome messages, `/automod-config` for spam protection, and `/modrole` to set custom moderator roles. Use `/help` to see all available commands and their setup instructions.",
        tags: ["configuration", "commands"]
      },
      {
        question: "Why isn't NexGuard responding to commands?",
        answer: "Check that: 1) NexGuard has the necessary permissions, 2) You're using slash commands (/) not prefix commands, 3) The bot is online (check its status), 4) You have the required role permissions for admin/moderation commands. Contact support if issues persist.",
        tags: ["troubleshooting", "commands"]
      }
    ]
  },
  {
    id: "moderation",
    title: "Moderation & AutoMod",
    icon: Shield,
    description: "Advanced moderation features",
    questions: [
      {
        question: "How does NexGuard's AutoMod spam protection work?",
        answer: "NexGuard tracks message frequency and automatically detects when users send too many messages in a short time (default: 5 messages in 10 seconds). It can delete messages, warn users, or apply timeouts. Configure it with `/automod-spam` command.",
        tags: ["automod", "spam", "protection"]
      },
      {
        question: "Can NexGuard automatically delete Discord invite links?",
        answer: "Yes! Use `/automod-links` to enable invite link blocking. NexGuard detects discord.gg links and other Discord invite formats, automatically deleting them and optionally warning or timing out the user.",
        tags: ["automod", "links", "invites"]
      },
      {
        question: "How do I set up custom bad word filtering?",
        answer: "Use `/automod-badwords` to enable the filter, then `/automod-words add [word]` to add custom words. You can set strict mode for exact word matching and choose actions like delete, warn, or timeout.",
        tags: ["automod", "badwords", "filtering"]
      },
      {
        question: "What's the difference between ban and tempban?",
        answer: "Regular `/ban` is permanent until manually unbanned. `/tempban` (using the duration parameter) automatically unbans users after the specified time (e.g., `/ban @user 7d` for 7 days). NexGuard tracks all bans in the banlist system.",
        tags: ["moderation", "ban", "tempban"]
      },
      {
        question: "How do warning points work?",
        answer: "NexGuard automatically assigns severity levels to warnings: Minor (1 point), Moderate (2 points), Serious (3 points), Severe (5 points). Use `/warnings @user` to view someone's warning history and points total.",
        tags: ["warnings", "points", "moderation"]
      }
    ]
  },
  {
    id: "features",
    title: "Features & Commands",
    icon: Zap,
    description: "Using NexGuard's 44+ commands",
    questions: [
      {
        question: "How many commands does NexGuard have?",
        answer: "NexGuard has 44+ commands across categories: 15 Admin commands, 17 Moderation commands, 11 Utility commands, and 4 Ticket system commands. Use `/commands` to see the complete list organized by category.",
        tags: ["commands", "features"]
      },
      {
        question: "How do I create auto-reply messages?",
        answer: "Use `/autoreply-create` to set up automatic responses to keywords. You can configure trigger types (contains, exact match, starts with, ends with), custom embed colors, titles, and descriptions. Manage them with `/autoreply-list` and `/autoreply-toggle`.",
        tags: ["autoreply", "automation"]
      },
      {
        question: "What is the ticket system and how do I use it?",
        answer: "NexGuard's ticket system creates private channels for user support. Use `/ticketcategory` to set up categories, then users can create tickets with `/ticket`. Staff can manage and close tickets efficiently. Supports multiple categories for different types of support.",
        tags: ["tickets", "support"]
      },
      {
        question: "Can I set custom moderator roles?",
        answer: "Yes! Use `/modrole @role` to designate custom moderator roles. This allows users with specific roles to use moderation commands even without Discord's default permissions. Use `/modpermissions @user` to check someone's mod capabilities.",
        tags: ["modrole", "permissions", "staff"]
      },
      {
        question: "How do I view server analytics and statistics?",
        answer: "Use `/botstats` for live bot statistics, `/serverinfo` for current server information, and visit the website's Analytics page for detailed charts and trends. NexGuard tracks message activity, user engagement, and command usage.",
        tags: ["analytics", "statistics", "data"]
      }
    ]
  },
  {
    id: "troubleshooting",
    title: "Troubleshooting",
    icon: AlertTriangle,
    description: "Common issues and solutions",
    questions: [
      {
        question: "NexGuard isn't logging commands to my channel",
        answer: "Ensure you've set up logging with `/botlogging #channel`. Check that NexGuard has 'Send Messages' and 'Embed Links' permissions in the logging channel. The channel must be a text channel, not a voice or category channel.",
        tags: ["logging", "troubleshooting", "channels"]
      },
      {
        question: "AutoMod isn't working in my server",
        answer: "First, enable AutoMod with `/automod-config`, then configure specific modules with `/automod-spam`, `/automod-links`, or `/automod-badwords`. Ensure NexGuard has 'Manage Messages' permission and that the user isn't a moderator (AutoMod skips staff).",
        tags: ["automod", "troubleshooting", "permissions"]
      },
      {
        question: "Welcome messages aren't sending",
        answer: "Configure welcome messages with `/welcome enable #channel`. NexGuard needs 'Send Messages' permission in the welcome channel. You can customize the message, embed colors, and thumbnails with additional `/welcome` command options.",
        tags: ["welcome", "troubleshooting", "channels"]
      },
      {
        question: "Some users can't use moderation commands",
        answer: "Check user permissions with `/modpermissions @user`. Users need either Discord's built-in mod permissions (Manage Messages, Moderate Members) or a custom mod role set with `/modrole`. Bot hierarchy also matters - NexGuard's role must be higher than the target user's highest role.",
        tags: ["permissions", "moderation", "hierarchy"]
      },
      {
        question: "The bot seems slow or unresponsive",
        answer: "NexGuard runs on high-performance infrastructure, but high server load or Discord API issues can cause delays. Check NexGuard's status on our website. If problems persist, contact support with specific details about which commands are affected.",
        tags: ["performance", "troubleshooting", "status"]
      }
    ]
  },
  {
    id: "advanced",
    title: "Advanced Usage",
    icon: Settings,
    description: "Pro tips and advanced configurations",
    questions: [
      {
        question: "How do I backup my NexGuard settings?",
        answer: "NexGuard stores all settings in a secure database. Your automod rules, auto-replies, and configurations are automatically saved. For manual backup, document your settings using `/automod-config`, `/autoreply-list`, and other status commands.",
        tags: ["backup", "settings", "database"]
      },
      {
        question: "Can I use NexGuard in multiple servers?",
        answer: "Absolutely! NexGuard supports unlimited servers. Each server has independent settings, so configurations in one server won't affect others. The same commands work across all servers where NexGuard is installed.",
        tags: ["multi-server", "scaling"]
      },
      {
        question: "How do I integrate NexGuard with other bots?",
        answer: "NexGuard works alongside other bots. Avoid overlapping functions (multiple moderation bots) to prevent conflicts. NexGuard's comprehensive feature set often eliminates the need for multiple specialized bots.",
        tags: ["integration", "compatibility"]
      },
      {
        question: "What's the difference between strict and normal AutoMod modes?",
        answer: "Normal mode uses 'contains' matching (partial word detection), while strict mode requires exact word matches. Strict mode reduces false positives but may miss variations. Choose based on your community's needs and tolerance for false positives.",
        tags: ["automod", "strict-mode", "configuration"]
      },
      {
        question: "How do I set up role-based command restrictions?",
        answer: "Use `/modrole` to set custom mod roles for moderation commands. Admin commands require 'Administrator' or 'Manage Server' permissions by default. You can create hierarchical moderation by assigning different roles for different command categories.",
        tags: ["roles", "permissions", "hierarchy"]
      }
    ]
  }
];

export default function FAQ() {
  useEffect(() => {
    document.title = "FAQ - NexGuard Discord Bot";
  }, []);

  return (
    <div className="min-h-screen hero-gradient circuit-pattern relative overflow-hidden">
      <div 
        className="absolute inset-0 bg-center opacity-20" 
        style={{ 
          backgroundImage: `url(${nexguardIcon})`,
          backgroundSize: '1920px 1080px',
          backgroundRepeat: 'no-repeat'
        }}
      ></div>
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      <div className="relative z-10">
      {/* Hero Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,255,255,0.1),transparent_50%)]" />
        <div className="container mx-auto max-w-4xl relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full mb-6">
              <HelpCircle className="w-4 h-4" />
              <span className="text-sm font-medium">Frequently Asked Questions</span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] bg-clip-text text-transparent">
              How Can We Help?
            </h1>
            
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Find answers to common questions about NexGuard's 44+ commands, setup, and advanced features.
            </p>

            <div className="flex flex-wrap gap-4 justify-center">
              <Button asChild size="lg" className="bg-gradient-to-r from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))]">
                <Link href="/contact">Contact Support</Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link href="/docs">View Documentation</Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* FAQ Categories */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="grid gap-8">
            {faqCategories.map((category, categoryIndex) => (
              <motion.div
                key={category.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: categoryIndex * 0.1 }}
              >
                <Card className="overflow-hidden border-border/50 bg-card/50 backdrop-blur-sm">
                  <CardHeader>
                    <div className="flex items-center gap-4">
                      <div className="p-3 rounded-lg bg-gradient-to-br from-[hsl(var(--nexguard-cyan))]/20 to-[hsl(var(--nexguard-purple))]/20">
                        <category.icon className="w-6 h-6 text-[hsl(var(--nexguard-cyan))]" />
                      </div>
                      <div>
                        <CardTitle className="text-2xl">{category.title}</CardTitle>
                        <CardDescription className="text-base">{category.description}</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    <Accordion type="single" collapsible className="w-full">
                      {category.questions.map((faq, faqIndex) => (
                        <AccordionItem 
                          key={faqIndex} 
                          value={`${category.id}-${faqIndex}`}
                          className="border-border/30"
                        >
                          <AccordionTrigger className="text-left hover:no-underline hover:text-[hsl(var(--nexguard-cyan))] transition-colors">
                            <div className="flex items-start gap-3 text-left">
                              <CheckCircle className="w-5 h-5 text-[hsl(var(--nexguard-cyan))] mt-0.5 flex-shrink-0" />
                              <span className="font-medium">{faq.question}</span>
                            </div>
                          </AccordionTrigger>
                          <AccordionContent className="text-muted-foreground">
                            <div className="pl-8 space-y-4">
                              <p className="leading-relaxed">{faq.answer}</p>
                              {faq.tags && (
                                <div className="flex flex-wrap gap-2">
                                  {faq.tags.map((tag) => (
                                    <Badge 
                                      key={tag} 
                                      variant="secondary" 
                                      className="text-xs bg-primary/10 text-primary hover:bg-primary/20"
                                    >
                                      {tag}
                                    </Badge>
                                  ))}
                                </div>
                              )}
                            </div>
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Quick Help Section */}
      <section className="py-16 px-4 bg-muted/30">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h2 className="text-3xl font-bold mb-6">Still Need Help?</h2>
            <p className="text-lg text-muted-foreground mb-8">
              Can't find what you're looking for? Our support team is here to help.
            </p>
            
            <div className="grid md:grid-cols-3 gap-6">
              <Card className="text-center">
                <CardHeader>
                  <MessageSquare className="w-8 h-8 text-[hsl(var(--nexguard-cyan))] mx-auto mb-2" />
                  <CardTitle className="text-lg">Contact Support</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    Get direct help from our support team
                  </p>
                  <Button asChild variant="outline" size="sm">
                    <Link href="/contact">Contact Us</Link>
                  </Button>
                </CardContent>
              </Card>

              <Card className="text-center">
                <CardHeader>
                  <Users className="w-8 h-8 text-[hsl(var(--nexguard-cyan))] mx-auto mb-2" />
                  <CardTitle className="text-lg">Community</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    Join our Discord for community support
                  </p>
                  <Button asChild variant="outline" size="sm">
                    <Link href="/community">Join Discord</Link>
                  </Button>
                </CardContent>
              </Card>

              <Card className="text-center">
                <CardHeader>
                  <Lock className="w-8 h-8 text-[hsl(var(--nexguard-cyan))] mx-auto mb-2" />
                  <CardTitle className="text-lg">Documentation</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    Detailed guides and command reference
                  </p>
                  <Button asChild variant="outline" size="sm">
                    <Link href="/docs">View Docs</Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        </div>
      </section>
      </div>
    </div>
  );
}