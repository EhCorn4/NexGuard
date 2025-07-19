import React from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageTransition } from "@/components/ui/page-transition";
import { StaggerContainer, StaggerItem } from "@/components/ui/stagger-container";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Shield, Eye, AlertCircle, Mail, MessageSquare, ExternalLink } from "lucide-react";
import nexguardIcon from "@assets/file_0000000003fc61f58b4fd114190f81c9_1751936993313.png";

export default function PrivacyPolicy() {
  return (
    <PageTransition>
      <div className="min-h-screen hero-gradient circuit-pattern pt-24 relative overflow-hidden">
        <div 
          className="absolute inset-0 bg-center opacity-20" 
          style={{ 
            backgroundImage: `url(${nexguardIcon})`,
            backgroundSize: '1920px 1080px',
            backgroundRepeat: 'no-repeat'
          }}
        ></div>
        <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
        
        <div className="container mx-auto px-4 py-20 relative z-10">
          <PageHeader
            title="Privacy Policy"
            description="Your privacy is important to us. Learn how we protect and handle your data."
            icon={Eye}
          />
          
          <div className="container mx-auto px-4 pb-16">
            <StaggerContainer>
              <StaggerItem>
                <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
                  <CardHeader className="pb-4">
                    <div className="flex items-center gap-3">
                      <Shield className="w-6 h-6 text-cyan-400" />
                      <CardTitle className="text-2xl text-white">NexGuard - Privacy Policy</CardTitle>
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
                            NexGuard ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard your information when you visit our website or interact with our services, including the NexGuard Discord bot.
                          </p>
                          <p className="leading-relaxed mt-3">
                            By using our Site or Services, you agree to the terms of this Privacy Policy.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 1 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">1.</span>
                            Information We Collect
                          </h3>
                          <p className="leading-relaxed mb-4">
                            We may collect the following types of information:
                          </p>
                          
                          <div className="space-y-4">
                            <div className="bg-slate-900/20 p-3 rounded-lg border border-slate-700">
                              <h4 className="font-semibold text-cyan-400 mb-2">a. Information from Discord</h4>
                              <p className="mb-2">When you interact with the NexGuard Discord bot or authorize access via OAuth2, we may collect:</p>
                              <ul className="list-disc pl-5 space-y-1 text-slate-400">
                                <li>Discord User ID and username</li>
                                <li>Guild (server) IDs and roles</li>
                                <li>Channel and message data (as necessary for moderation features)</li>
                                <li>User avatar or profile image (for identification)</li>
                              </ul>
                            </div>
                            
                            <div className="bg-slate-900/20 p-3 rounded-lg border border-slate-700">
                              <h4 className="font-semibold text-cyan-400 mb-2">b. Website Analytics</h4>
                              <p className="mb-2">We may use third-party analytics tools (e.g., Google Analytics) to collect:</p>
                              <ul className="list-disc pl-5 space-y-1 text-slate-400">
                                <li>IP address</li>
                                <li>Browser type and version</li>
                                <li>Pages visited and time spent</li>
                                <li>Referring URLs</li>
                              </ul>
                              <p className="mt-2 text-sm text-slate-400">This data is aggregated and anonymized and helps us improve the user experience.</p>
                            </div>
                            
                            <div className="bg-slate-900/20 p-3 rounded-lg border border-slate-700">
                              <h4 className="font-semibold text-cyan-400 mb-2">c. Voluntarily Submitted Information</h4>
                              <p className="mb-2">If you contact us or submit a request via email, Discord, or forms, we may store:</p>
                              <ul className="list-disc pl-5 space-y-1 text-slate-400">
                                <li>Your email address or Discord username</li>
                                <li>Any message content or inquiries you submit</li>
                              </ul>
                            </div>
                          </div>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 2 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">2.</span>
                            How We Use Your Information
                          </h3>
                          <p className="leading-relaxed mb-3">We use your data to:</p>
                          <ul className="list-disc pl-5 space-y-1 text-slate-400 mb-4">
                            <li>Provide and maintain our services (e.g., bot functionality)</li>
                            <li>Improve site performance and usability</li>
                            <li>Respond to user inquiries or support requests</li>
                            <li>Monitor for abuse, spam, or policy violations</li>
                            <li>Customize features based on server settings and preferences</li>
                          </ul>
                          <p className="leading-relaxed font-semibold text-cyan-400">
                            We do not sell your data to third parties.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 3 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">3.</span>
                            Cookies & Tracking
                          </h3>
                          <p className="leading-relaxed mb-3">Our website may use cookies to:</p>
                          <ul className="list-disc pl-5 space-y-1 text-slate-400 mb-4">
                            <li>Remember user preferences</li>
                            <li>Support security features</li>
                            <li>Enable analytics</li>
                          </ul>
                          <p className="leading-relaxed text-slate-400">
                            You can disable cookies in your browser settings; however, this may affect the functionality of our website.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 4 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">4.</span>
                            Data Sharing
                          </h3>
                          <p className="leading-relaxed mb-3">We do not share personal data with third parties except:</p>
                          <ul className="list-disc pl-5 space-y-1 text-slate-400">
                            <li>With your consent</li>
                            <li>When required by law or legal process</li>
                            <li>To protect the security or integrity of our services</li>
                            <li>To trusted service providers under NDA for infrastructure (e.g., hosting)</li>
                          </ul>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 5 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">5.</span>
                            Data Retention
                          </h3>
                          <p className="leading-relaxed mb-3">We retain data only for as long as necessary to:</p>
                          <ul className="list-disc pl-5 space-y-1 text-slate-400 mb-4">
                            <li>Fulfill the purpose for which it was collected</li>
                            <li>Comply with legal obligations</li>
                            <li>Resolve disputes and enforce our agreements</li>
                          </ul>
                          <p className="leading-relaxed text-cyan-400">
                            You can request deletion of your data at any time (see Section 8).
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 6 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">6.</span>
                            Security
                          </h3>
                          <p className="leading-relaxed mb-3">We use industry-standard methods to secure your data, including:</p>
                          <ul className="list-disc pl-5 space-y-1 text-slate-400 mb-4">
                            <li>HTTPS encryption</li>
                            <li>Access control measures</li>
                            <li>Regular audits</li>
                          </ul>
                          <p className="leading-relaxed text-slate-400">
                            However, no method of transmission over the internet is 100% secure. Use the Services at your own risk.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 7 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">7.</span>
                            Children's Privacy
                          </h3>
                          <p className="leading-relaxed">
                            NexGuard is not intended for use by anyone under the age of 13 (or the minimum legal age in your jurisdiction). We do not knowingly collect data from children.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 8 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">8.</span>
                            Your Rights
                          </h3>
                          <p className="leading-relaxed mb-3">Depending on your location, you may have the following rights:</p>
                          <ul className="list-disc pl-5 space-y-1 text-slate-400 mb-4">
                            <li>Request access to your data</li>
                            <li>Request correction or deletion</li>
                            <li>Object to processing or request data portability</li>
                          </ul>
                          <p className="leading-relaxed text-cyan-400">
                            To exercise any of these rights, contact us at the information below.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 9 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">9.</span>
                            Changes to This Policy
                          </h3>
                          <p className="leading-relaxed">
                            We may update this Privacy Policy at any time. Changes will be posted here with an updated "Last Updated" date. Continued use of our services after changes are made indicates your agreement.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 10 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">10.</span>
                            Contact Us
                          </h3>
                          <p className="leading-relaxed mb-4">
                            If you have any questions or concerns about this Privacy Policy or your data, you can contact us at:
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