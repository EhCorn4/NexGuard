import React from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageTransition } from "@/components/ui/page-transition";
import { StaggerContainer, StaggerItem } from "@/components/ui/stagger-container";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Shield, Cookie, AlertCircle, Mail, MessageSquare, ExternalLink } from "lucide-react";
import nexguardIcon from "@assets/file_0000000003fc61f58b4fd114190f81c9_1751936993313.png";

export default function CookiesPolicy() {
  return (
    <PageTransition>
      <div className="min-h-screen hero-gradient circuit-pattern pt-24 relative overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-20" 
          style={{ backgroundImage: `url(${nexguardIcon})` }}
        ></div>
        <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
        
        <div className="container mx-auto px-4 py-20 relative z-10">
          <PageHeader
            title="Cookies Policy"
            description="Learn how we use cookies to enhance your experience on our website"
            icon={Cookie}
          />
          
          <div className="container mx-auto px-4 pb-16">
            <StaggerContainer>
              <StaggerItem>
                <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
                  <CardHeader className="pb-4">
                    <div className="flex items-center gap-3">
                      <Shield className="w-6 h-6 text-cyan-400" />
                      <CardTitle className="text-2xl text-white">NexGuard - Cookies Policy</CardTitle>
                    </div>
                    <div className="flex gap-2 mt-2">
                      <Badge variant="outline" className="text-cyan-400 border-cyan-400">
                        <AlertCircle className="w-3 h-3 mr-1" />
                        Effective Date: July 8, 2025
                      </Badge>
                      <Badge variant="outline" className="text-purple-400 border-purple-400">
                        Last Updated: July 8, 2025
                      </Badge>
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    <ScrollArea className="h-[600px] pr-4">
                      <div className="space-y-6 text-slate-300">
                        {/* Introduction */}
                        <div className="bg-slate-900/30 p-4 rounded-lg border border-slate-700">
                          <p className="leading-relaxed">
                            This Cookies Policy explains how NexGuard ("we", "us", or "our") uses cookies and similar tracking technologies on our website. By using our website, you agree to the use of cookies in accordance with this policy.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 1 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">1.</span>
                            What Are Cookies?
                          </h3>
                          <p className="leading-relaxed mb-4">
                            Cookies are small text files stored on your device when you visit a website. They help the website remember your actions and preferences (such as login, language, or theme) over a period of time so you don't have to re-enter them whenever you return to the site.
                          </p>
                          <p className="leading-relaxed mb-3">Cookies can be:</p>
                          <div className="space-y-2">
                            <div className="bg-slate-900/20 p-3 rounded-lg border border-slate-700">
                              <p className="text-cyan-400 font-semibold">Session Cookies:</p>
                              <p className="text-slate-400">Deleted when you close your browser.</p>
                            </div>
                            <div className="bg-slate-900/20 p-3 rounded-lg border border-slate-700">
                              <p className="text-cyan-400 font-semibold">Persistent Cookies:</p>
                              <p className="text-slate-400">Remain on your device for a set period or until deleted.</p>
                            </div>
                          </div>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 2 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">2.</span>
                            How We Use Cookies
                          </h3>
                          <p className="leading-relaxed mb-3">We use cookies to:</p>
                          <ul className="list-disc pl-5 space-y-1 text-slate-400 mb-4">
                            <li>Improve website performance and functionality</li>
                            <li>Analyze traffic and usage patterns</li>
                            <li>Remember user preferences</li>
                            <li>Enhance security</li>
                            <li>Provide a smoother, more personalized experience</li>
                          </ul>
                          <p className="leading-relaxed text-slate-400">
                            We may also use third-party cookies for analytics and service integrations.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 3 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">3.</span>
                            Types of Cookies We Use
                          </h3>
                          <div className="overflow-x-auto">
                            <table className="w-full bg-slate-900/30 rounded-lg border border-slate-700">
                              <thead>
                                <tr className="border-b border-slate-700">
                                  <th className="text-left p-3 text-cyan-400 font-semibold">Cookie Type</th>
                                  <th className="text-left p-3 text-cyan-400 font-semibold">Purpose</th>
                                </tr>
                              </thead>
                              <tbody>
                                <tr className="border-b border-slate-700">
                                  <td className="p-3 text-white font-medium">Strictly Necessary</td>
                                  <td className="p-3 text-slate-400">Essential for site navigation and functionality (e.g., login, security).</td>
                                </tr>
                                <tr className="border-b border-slate-700">
                                  <td className="p-3 text-white font-medium">Performance</td>
                                  <td className="p-3 text-slate-400">Help us understand how visitors use the site (e.g., Google Analytics).</td>
                                </tr>
                                <tr className="border-b border-slate-700">
                                  <td className="p-3 text-white font-medium">Functional</td>
                                  <td className="p-3 text-slate-400">Remember preferences (e.g., theme, layout, language).</td>
                                </tr>
                                <tr>
                                  <td className="p-3 text-white font-medium">Third-Party</td>
                                  <td className="p-3 text-slate-400">Set by external services we use (e.g., Discord integration, embeds).</td>
                                </tr>
                              </tbody>
                            </table>
                          </div>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 4 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">4.</span>
                            Third-Party Cookies
                          </h3>
                          <p className="leading-relaxed mb-3">We may use cookies from trusted third parties such as:</p>
                          <div className="space-y-2">
                            <div className="bg-slate-900/20 p-3 rounded-lg border border-slate-700">
                              <p className="text-cyan-400 font-semibold">Google Analytics</p>
                              <p className="text-slate-400">To track and report website traffic</p>
                            </div>
                            <div className="bg-slate-900/20 p-3 rounded-lg border border-slate-700">
                              <p className="text-cyan-400 font-semibold">Discord</p>
                              <p className="text-slate-400">For OAuth login or bot-related features</p>
                            </div>
                            <div className="bg-slate-900/20 p-3 rounded-lg border border-slate-700">
                              <p className="text-cyan-400 font-semibold">Cloudflare</p>
                              <p className="text-slate-400">For performance and security services</p>
                            </div>
                          </div>
                          <p className="leading-relaxed text-slate-400 mt-4">
                            These cookies are subject to the privacy policies of the respective providers.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 5 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">5.</span>
                            Managing Cookies
                          </h3>
                          <p className="leading-relaxed mb-3">
                            You can control or delete cookies via your browser settings. Most browsers allow you to:
                          </p>
                          <ul className="list-disc pl-5 space-y-1 text-slate-400 mb-4">
                            <li>View and delete stored cookies</li>
                            <li>Block all cookies or only third-party cookies</li>
                            <li>Set preferences for certain websites</li>
                          </ul>
                          <p className="leading-relaxed text-yellow-400 font-semibold">
                            Please note that disabling some cookies may affect website functionality.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 6 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">6.</span>
                            Consent
                          </h3>
                          <p className="leading-relaxed mb-3">
                            When you first visit our site, you may see a cookie banner notifying you of our use of cookies. By continuing to use the site, you consent to the use of cookies as described in this policy.
                          </p>
                          <p className="leading-relaxed text-slate-400">
                            If you do not agree to the use of cookies, you should adjust your browser settings or refrain from using our website.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 7 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">7.</span>
                            Updates to This Policy
                          </h3>
                          <p className="leading-relaxed">
                            We may update this Cookies Policy from time to time. All changes will be posted on this page with an updated "Last Updated" date. We encourage you to review this page periodically.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 8 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">8.</span>
                            Contact Us
                          </h3>
                          <p className="leading-relaxed mb-4">
                            If you have questions or concerns about our use of cookies, please contact us:
                          </p>
                          <div className="space-y-2">
                            <div className="flex items-center gap-2 text-cyan-400">
                              <Mail className="w-4 h-4" />
                              <span>Email: nexguards@gmail.com</span>
                            </div>
                            <div className="flex items-center gap-2 text-purple-400">
                              <MessageSquare className="w-4 h-4" />
                              <span>Discord: </span>
                              <a 
                                href="https://discord.gg/wpjZMPXaRT" 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-purple-400 hover:text-purple-300 transition-colors underline inline-flex items-center gap-1"
                              >
                                https://discord.gg/wpjZMPXaRT
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            </div>
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