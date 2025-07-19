import React from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageTransition } from "@/components/ui/page-transition";
import { StaggerContainer, StaggerItem } from "@/components/ui/stagger-container";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { 
  Shield, 
  Mail, 
  MessageSquare, 
  User, 
  ExternalLink, 
  HelpCircle, 
  Bug, 
  Settings, 
  AlertTriangle,
  Heart,
  Phone
} from "lucide-react";
import nexguardIcon from "@assets/file_0000000003fc61f58b4fd114190f81c9_1751936993313.png";

export default function Contact() {
  return (
    <PageTransition>
      <div className="min-h-screen hero-gradient circuit-pattern pt-24 relative overflow-hidden">
        <div 
          className="absolute inset-0 bg-center opacity-20" 
          style={{ 
            backgroundImage: `url(${nexguardIcon})`,
            backgroundSize: '400px 400px',
            backgroundRepeat: 'no-repeat'
          }}
        ></div>
        <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
        
        <div className="container mx-auto px-4 py-20 relative z-10">
          <PageHeader
            title="Contact Us"
            description="Need help or have questions? We're here to support you and your community."
            icon={Phone}
          />
          
          <div className="container mx-auto px-4 pb-16">
            <StaggerContainer>
              <StaggerItem>
                <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
                  <CardHeader className="pb-4">
                    <div className="flex items-center gap-3">
                      <Shield className="w-6 h-6 text-cyan-400" />
                      <CardTitle className="text-2xl text-white">Get in Touch</CardTitle>
                    </div>
                    <p className="text-slate-400 mt-2">
                      Choose the best way to reach us based on your needs. We're committed to providing excellent support for the NexGuard community.
                    </p>
                  </CardHeader>
                  
                  <CardContent>
                    <ScrollArea className="h-[600px] pr-4">
                      <div className="space-y-6 text-slate-300">
                        
                        {/* Contact Methods */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                            <span className="text-cyan-400">📞</span>
                            Contact Methods
                          </h3>
                          
                          <div className="grid gap-4">
                            {/* Discord Support */}
                            <div className="bg-slate-900/30 p-4 rounded-lg border border-slate-700">
                              <div className="flex items-center gap-3 mb-3">
                                <MessageSquare className="w-5 h-5 text-purple-400" />
                                <h4 className="font-semibold text-white">Discord Support Server</h4>
                                <Badge variant="outline" className="text-green-400 border-green-400">Recommended</Badge>
                              </div>
                              <p className="text-slate-400 mb-3">
                                Join our Discord server for real-time support, community discussions, and bot updates.
                              </p>
                              <a 
                                href="https://discord.gg/wpjZMPXaRT" 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-purple-400 hover:text-purple-300 transition-colors underline inline-flex items-center gap-2"
                              >
                                https://discord.gg/wpjZMPXaRT
                                <ExternalLink className="w-4 h-4" />
                              </a>
                            </div>
                            
                            {/* NexGuard Email */}
                            <div className="bg-slate-900/30 p-4 rounded-lg border border-slate-700">
                              <div className="flex items-center gap-3 mb-3">
                                <Mail className="w-5 h-5 text-cyan-400" />
                                <h4 className="font-semibold text-white">NexGuard Support Email</h4>
                              </div>
                              <p className="text-slate-400 mb-3">
                                Official support email for general inquiries, feature requests, and business matters.
                              </p>
                              <a 
                                href="mailto:nexguards@gmail.com" 
                                className="text-cyan-400 hover:text-cyan-300 transition-colors underline inline-flex items-center gap-2"
                              >
                                nexguards@gmail.com
                                <Mail className="w-4 h-4" />
                              </a>
                            </div>
                            
                            {/* Developer Contact */}
                            <div className="bg-slate-900/30 p-4 rounded-lg border border-slate-700">
                              <div className="flex items-center gap-3 mb-3">
                                <User className="w-5 h-5 text-green-400" />
                                <h4 className="font-semibold text-white">Developer Direct Contact</h4>
                              </div>
                              <p className="text-slate-400 mb-3">
                                Direct contact with Caleb Weston, Lead Developer, for technical issues and development inquiries.
                              </p>
                              <a 
                                href="mailto:crweston2004@gmail.com" 
                                className="text-green-400 hover:text-green-300 transition-colors underline inline-flex items-center gap-2"
                              >
                                crweston2004@gmail.com
                                <Mail className="w-4 h-4" />
                              </a>
                            </div>
                          </div>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* When to Contact Who */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                            <span className="text-cyan-400">🎯</span>
                            Who to Contact
                          </h3>
                          
                          <div className="space-y-4">
                            {/* Discord Support Server */}
                            <div className="bg-purple-900/20 p-4 rounded-lg border border-purple-700">
                              <div className="flex items-center gap-3 mb-3">
                                <MessageSquare className="w-5 h-5 text-purple-400" />
                                <h4 className="font-semibold text-purple-400">Discord Support Server</h4>
                              </div>
                              <p className="text-slate-400 mb-3">Best for:</p>
                              <ul className="list-disc pl-5 space-y-1 text-slate-400">
                                <li>General questions and quick support</li>
                                <li>Community discussions and tips</li>
                                <li>Bot setup and configuration help</li>
                                <li>Feature demonstrations and tutorials</li>
                                <li>Connecting with other server administrators</li>
                                <li>Real-time troubleshooting</li>
                              </ul>
                            </div>
                            
                            {/* NexGuard Email */}
                            <div className="bg-cyan-900/20 p-4 rounded-lg border border-cyan-700">
                              <div className="flex items-center gap-3 mb-3">
                                <Mail className="w-5 h-5 text-cyan-400" />
                                <h4 className="font-semibold text-cyan-400">NexGuard Support Email</h4>
                              </div>
                              <p className="text-slate-400 mb-3">Best for:</p>
                              <ul className="list-disc pl-5 space-y-1 text-slate-400">
                                <li>Feature requests and suggestions</li>
                                <li>Business inquiries and partnerships</li>
                                <li>Privacy and security concerns</li>
                                <li>Account-related issues</li>
                                <li>Feedback and testimonials</li>
                                <li>General support inquiries</li>
                              </ul>
                            </div>
                            
                            {/* Developer Direct */}
                            <div className="bg-green-900/20 p-4 rounded-lg border border-green-700">
                              <div className="flex items-center gap-3 mb-3">
                                <User className="w-5 h-5 text-green-400" />
                                <h4 className="font-semibold text-green-400">Developer Direct Contact</h4>
                              </div>
                              <p className="text-slate-400 mb-3">Best for:</p>
                              <ul className="list-disc pl-5 space-y-1 text-slate-400">
                                <li>Critical bugs and technical issues</li>
                                <li>Advanced technical questions</li>
                                <li>Integration and API discussions</li>
                                <li>Development collaboration</li>
                                <li>Security vulnerability reports</li>
                                <li>Custom feature development</li>
                              </ul>
                            </div>
                          </div>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Quick Reference Guide */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                            <span className="text-cyan-400">⚡</span>
                            Quick Reference Guide
                          </h3>
                          
                          <div className="grid gap-3">
                            <div className="flex items-center gap-3 p-3 bg-slate-900/20 rounded-lg border border-slate-700">
                              <HelpCircle className="w-5 h-5 text-blue-400" />
                              <span className="text-slate-400">Need help setting up the bot?</span>
                              <span className="text-blue-400 ml-auto">→ Discord Server</span>
                            </div>
                            
                            <div className="flex items-center gap-3 p-3 bg-slate-900/20 rounded-lg border border-slate-700">
                              <Bug className="w-5 h-5 text-red-400" />
                              <span className="text-slate-400">Found a bug or critical issue?</span>
                              <span className="text-red-400 ml-auto">→ Developer Email</span>
                            </div>
                            
                            <div className="flex items-center gap-3 p-3 bg-slate-900/20 rounded-lg border border-slate-700">
                              <Settings className="w-5 h-5 text-yellow-400" />
                              <span className="text-slate-400">Want to request a new feature?</span>
                              <span className="text-yellow-400 ml-auto">→ NexGuard Email</span>
                            </div>
                            
                            <div className="flex items-center gap-3 p-3 bg-slate-900/20 rounded-lg border border-slate-700">
                              <AlertTriangle className="w-5 h-5 text-orange-400" />
                              <span className="text-slate-400">Security or privacy concern?</span>
                              <span className="text-orange-400 ml-auto">→ NexGuard Email</span>
                            </div>
                            
                            <div className="flex items-center gap-3 p-3 bg-slate-900/20 rounded-lg border border-slate-700">
                              <Heart className="w-5 h-5 text-pink-400" />
                              <span className="text-slate-400">Love NexGuard and want to share?</span>
                              <span className="text-pink-400 ml-auto">→ Any Contact Method</span>
                            </div>
                          </div>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Response Times */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                            <span className="text-cyan-400">⏱️</span>
                            Expected Response Times
                          </h3>
                          
                          <div className="space-y-3">
                            <div className="flex justify-between items-center p-3 bg-slate-900/20 rounded-lg border border-slate-700">
                              <div className="flex items-center gap-2">
                                <MessageSquare className="w-4 h-4 text-purple-400" />
                                <span className="text-slate-300">Discord Support</span>
                              </div>
                              <Badge variant="outline" className="text-green-400 border-green-400">
                                Minutes to Hours
                              </Badge>
                            </div>
                            
                            <div className="flex justify-between items-center p-3 bg-slate-900/20 rounded-lg border border-slate-700">
                              <div className="flex items-center gap-2">
                                <Mail className="w-4 h-4 text-cyan-400" />
                                <span className="text-slate-300">NexGuard Email</span>
                              </div>
                              <Badge variant="outline" className="text-yellow-400 border-yellow-400">
                                24-48 Hours
                              </Badge>
                            </div>
                            
                            <div className="flex justify-between items-center p-3 bg-slate-900/20 rounded-lg border border-slate-700">
                              <div className="flex items-center gap-2">
                                <User className="w-4 h-4 text-green-400" />
                                <span className="text-slate-300">Developer Direct</span>
                              </div>
                              <Badge variant="outline" className="text-blue-400 border-blue-400">
                                1-3 Business Days
                              </Badge>
                            </div>
                          </div>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Additional Information */}
                        <div className="bg-slate-900/30 p-4 rounded-lg border border-slate-700">
                          <h4 className="font-semibold text-white mb-3">Before You Contact Us</h4>
                          <div className="space-y-2 text-slate-400">
                            <p>To help us assist you better, please:</p>
                            <ul className="list-disc pl-5 space-y-1">
                              <li>Check our <a href="/docs" className="text-cyan-400 hover:text-cyan-300 underline">documentation</a> for common solutions</li>
                              <li>Include your server ID and relevant error messages</li>
                              <li>Describe the issue clearly with steps to reproduce</li>
                              <li>Let us know what you've already tried</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    </ScrollArea>
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