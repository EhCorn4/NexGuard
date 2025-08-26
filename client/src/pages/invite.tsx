import { GradientText } from "@/components/ui/gradient-text";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Download, Settings, Shield } from "lucide-react";
import { SiDiscord } from "react-icons/si";
import { memo } from "react";
import { useQuery } from "@tanstack/react-query";

const Invite = memo(function Invite() {
  const { data: config } = useQuery({
    queryKey: ['/api/config'],
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const discordInviteUrl = config?.discordInviteUrl || "https://discord.com/oauth2/authorize?client_id=1389775821794705429";
  const supportServerUrl = config?.supportServerUrl || "https://discord.gg/wpjZMPXaRT";

  return (
    <div className="min-h-screen hero-gradient circuit-pattern pt-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      <div className="container mx-auto px-4 py-20 relative z-10">
        <div className="max-w-6xl mx-auto text-center">
          <PageHeader 
            title="Ready to Protect Your Server?"
            description="Join 17+ servers already using NexGuard's 61+ commands with professional ticket system, live server statistics channels, reaction roles, universal logging, and advanced automod protection to maintain order and enhance their community experience."
          />
          
          {/* Bot Stats Section */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="bg-[hsl(var(--nexguard-darker))]/60 backdrop-blur-sm border border-[hsl(var(--nexguard-cyan))]/20 rounded-lg p-6">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">639+</div>
              <div className="text-gray-400 text-sm">Active Users</div>
            </div>
            <div className="bg-[hsl(var(--nexguard-darker))]/60 backdrop-blur-sm border border-[hsl(var(--nexguard-cyan))]/20 rounded-lg p-6">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">17+</div>
              <div className="text-gray-400 text-sm">Servers Protected</div>
            </div>
            <div className="bg-[hsl(var(--nexguard-darker))]/60 backdrop-blur-sm border border-[hsl(var(--nexguard-cyan))]/20 rounded-lg p-6">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">61+</div>
              <div className="text-gray-400 text-sm">Slash Commands</div>
            </div>
          </div>
          
          <Card className="bg-[hsl(var(--nexguard-darker))]/80 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 mb-12">
            <CardContent className="p-8">
              <div className="grid md:grid-cols-3 gap-8 mb-8">
                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mx-auto mb-4">
                    <Download className="text-white" size={24} />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">1. Invite Bot</h3>
                  <p className="text-gray-400 text-sm">Click the invite button to add NexGuard to your server with essential permissions</p>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mx-auto mb-4">
                    <Settings className="text-white" size={24} />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">2. Configure</h3>
                  <p className="text-gray-400 text-sm">Set up channels, roles, and customize settings using simple slash commands</p>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mx-auto mb-4">
                    <Shield className="text-white" size={24} />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">3. Stay Protected</h3>
                  <p className="text-gray-400 text-sm">Enjoy automated moderation, welcome messages, and comprehensive server management</p>
                </div>
              </div>
              
              {/* Core Features Preview */}
              <div className="grid md:grid-cols-2 gap-6 mb-8">
                <div className="text-left">
                  <h4 className="text-lg font-semibold text-white mb-3">🛡️ Moderation Features</h4>
                  <ul className="text-gray-400 text-sm space-y-2">
                    <li>• 17+ moderation commands with temporary bans</li>
                    <li>• Channel lock/unlock management</li>
                    <li>• Universal command logging system</li>
                    <li>• Advanced automod with professional logging</li>
                  </ul>
                </div>
                <div className="text-left">
                  <h4 className="text-lg font-semibold text-white mb-3">🎫 Professional Features</h4>
                  <ul className="text-gray-400 text-sm space-y-2">
                    <li>• TicketsBot.net-style panel system with interactive buttons</li>
                    <li>• Live server statistics channels with real-time updates</li>
                    <li>• Reaction roles with automatic role management</li>
                    <li>• Smart auto-reply with analytics and cooldowns</li>
                    <li>• Real-time dashboard monitoring and error logging</li>
                  </ul>
                </div>
              </div>
              
              <div className="space-y-4 flex flex-col items-center">
                <a 
                  href={discordInviteUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block"
                >
                  <Button 
                    size="lg"
                    className="bg-[hsl(var(--discord-blurple))] hover:bg-[hsl(var(--discord-light))] text-white font-semibold text-lg px-8 py-4 transform hover:scale-105 transition-all duration-300 w-full max-w-md"
                  >
                    <SiDiscord className="mr-3" size={24} />
                    Invite NexGuard to Your Server
                  </Button>
                </a>
                <p className="text-sm text-gray-400 text-center">
                  Required permissions: Administrator (for full functionality)
                </p>
              </div>
            </CardContent>
          </Card>
          
          {/* Required Permissions Section */}
          <Card className="bg-[hsl(var(--nexguard-darker))]/80 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 mb-12">
            <CardContent className="p-8">
              <h3 className="text-2xl font-bold text-white mb-6 text-center">Required Permissions</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold text-[hsl(var(--nexguard-cyan))] mb-3">🔒 Essential Permissions</h4>
                  <ul className="text-gray-400 text-sm space-y-2">
                    <li>• View Channels - Navigate your server</li>
                    <li>• Send Messages - Communicate with users</li>
                    <li>• Embed Links - Rich message content</li>
                    <li>• Manage Messages - Delete spam/inappropriate content</li>
                    <li>• Read Message History - Context for moderation</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-lg font-semibold text-[hsl(var(--nexguard-cyan))] mb-3">⚡ Advanced Permissions</h4>
                  <ul className="text-gray-400 text-sm space-y-2">
                    <li>• Kick Members - Remove problematic users</li>
                    <li>• Ban Members - Permanent user removal</li>
                    <li>• Timeout Members - Temporary restrictions</li>
                    <li>• Manage Roles - Assign moderation roles</li>
                    <li>• Manage Channels - Create ticket channels</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Setup Guide Section */}
          <Card className="bg-[hsl(var(--nexguard-darker))]/80 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 mb-12">
            <CardContent className="p-8">
              <h3 className="text-2xl font-bold text-white mb-6 text-center">Quick Setup Guide</h3>
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg font-semibold text-[hsl(var(--nexguard-cyan))] mb-4">Basic Configuration</h4>
                  <div className="space-y-4 text-gray-400 text-sm">
                    <div className="flex items-start">
                      <div className="w-6 h-6 bg-[hsl(var(--nexguard-cyan))] rounded-full flex items-center justify-center mr-3 mt-0.5">
                        <span className="text-white text-xs">1</span>
                      </div>
                      <div>
                        <strong className="text-white">Set Welcome Channel:</strong><br />
                        <code className="text-[hsl(var(--nexguard-cyan))]">/welcome channel #general</code>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <div className="w-6 h-6 bg-[hsl(var(--nexguard-cyan))] rounded-full flex items-center justify-center mr-3 mt-0.5">
                        <span className="text-white text-xs">2</span>
                      </div>
                      <div>
                        <strong className="text-white">Enable Welcome Messages:</strong><br />
                        <code className="text-[hsl(var(--nexguard-cyan))]">/welcome enable</code>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <div className="w-6 h-6 bg-[hsl(var(--nexguard-cyan))] rounded-full flex items-center justify-center mr-3 mt-0.5">
                        <span className="text-white text-xs">3</span>
                      </div>
                      <div>
                        <strong className="text-white">Set Logging Channel:</strong><br />
                        <code className="text-[hsl(var(--nexguard-cyan))]">/configure logging #mod-logs</code>
                      </div>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="text-lg font-semibold text-[hsl(var(--nexguard-cyan))] mb-4">Advanced Features</h4>
                  <div className="space-y-4 text-gray-400 text-sm">
                    <div className="flex items-start">
                      <div className="w-6 h-6 bg-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mr-3 mt-0.5">
                        <span className="text-white text-xs">4</span>
                      </div>
                      <div>
                        <strong className="text-white">Custom Welcome Message:</strong><br />
                        <code className="text-[hsl(var(--nexguard-purple))]">/welcome set Welcome {'{user.mention}'}!</code>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <div className="w-6 h-6 bg-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mr-3 mt-0.5">
                        <span className="text-white text-xs">5</span>
                      </div>
                      <div>
                        <strong className="text-white">Enable Embed Mode:</strong><br />
                        <code className="text-[hsl(var(--nexguard-purple))]">/welcome embed true</code>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <div className="w-6 h-6 bg-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mr-3 mt-0.5">
                        <span className="text-white text-xs">6</span>
                      </div>
                      <div>
                        <strong className="text-white">Test Configuration:</strong><br />
                        <code className="text-[hsl(var(--nexguard-purple))]">/welcome test</code>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Feature Highlights Section */}
          <Card className="bg-[hsl(var(--nexguard-darker))]/80 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 mb-12">
            <CardContent className="p-8">
              <h3 className="text-2xl font-bold text-white mb-8 text-center">Why Choose NexGuard?</h3>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="w-12 h-12 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-white font-bold">⚡</span>
                  </div>
                  <h4 className="text-lg font-semibold text-white mb-2">Lightning Fast</h4>
                  <p className="text-gray-400 text-sm">Python-powered bot with millisecond response times and 99.9% uptime</p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-white font-bold">🛡️</span>
                  </div>
                  <h4 className="text-lg font-semibold text-white mb-2">Advanced Security</h4>
                  <p className="text-gray-400 text-sm">Comprehensive moderation tools with automated threat detection</p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-white font-bold">🎨</span>
                  </div>
                  <h4 className="text-lg font-semibold text-white mb-2">Highly Customizable</h4>
                  <p className="text-gray-400 text-sm">Personalized welcome messages, embeds, and server-specific settings</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-[hsl(var(--nexguard-darker))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-purple))]/20">
            <CardContent className="p-6 text-center">
              <h3 className="text-xl font-semibold text-white mb-4">Need Help Getting Started?</h3>
              <p className="text-gray-300 mb-6">Join our support server for setup assistance and community support.</p>
              <a 
                href={supportServerUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block"
              >
                <Button 
                  className="bg-[hsl(var(--nexguard-purple))] hover:bg-[hsl(var(--nexguard-purple))]/80 text-white font-semibold px-6 py-3 transition-all duration-300"
                >
                  <SiDiscord className="mr-2" size={20} />
                  Join Support Server
                </Button>
              </a>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
});

export default Invite;
