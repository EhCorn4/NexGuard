import React from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageTransition } from "@/components/ui/page-transition";
import { StaggerContainer, StaggerItem } from "@/components/ui/stagger-container";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Shield, FileText, AlertCircle, Mail, MessageSquare } from "lucide-react";

export default function TermsOfService() {
  return (
    <PageTransition>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
        {/* Circuit Pattern Background */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-transparent animate-pulse"></div>
        </div>
        
        <div className="relative z-10">
          <PageHeader
            title="Terms of Service"
            description="Please read these terms carefully before using NexGuard"
            icon={FileText}
          />
          
          <div className="container mx-auto px-4 pb-16">
            <StaggerContainer>
              <StaggerItem>
                <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
                  <CardHeader className="pb-4">
                    <div className="flex items-center gap-3">
                      <Shield className="w-6 h-6 text-cyan-400" />
                      <CardTitle className="text-2xl text-white">NexGuard - Terms of Service</CardTitle>
                    </div>
                    <div className="flex gap-2 mt-2">
                      <Badge variant="outline" className="text-cyan-400 border-cyan-400">
                        <AlertCircle className="w-3 h-3 mr-1" />
                        Effective Date: August 15, 2025
                      </Badge>
                      <Badge variant="outline" className="text-purple-400 border-purple-400">
                        Last Updated: August 15, 2025
                      </Badge>
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    <ScrollArea className="h-[600px] pr-4">
                      <div className="space-y-6 text-slate-300">
                        {/* Introduction */}
                        <div className="bg-slate-900/30 p-4 rounded-lg border border-slate-700">
                          <p className="leading-relaxed">
                            Welcome to NexGuard! These Terms of Service ("Terms") govern your access to and use of the NexGuard website (the "Site") and any services provided by NexGuard ("Services"), including but not limited to interaction with the NexGuard Discord bot. By accessing or using the Site or Services, you agree to be bound by these Terms. If you do not agree, you may not use our Site or Services.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 1 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">1.</span>
                            Use of Services
                          </h3>
                          <p className="leading-relaxed">
                            You agree to use the Services only for lawful purposes and in accordance with these Terms. You may not use the Site or Services in any manner that could damage, disable, overburden, or impair any NexGuard server or interfere with any other party's use of the Site.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 2 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">2.</span>
                            User Conduct
                          </h3>
                          <p className="leading-relaxed mb-3">
                            By using NexGuard, you agree that you will not:
                          </p>
                          <ul className="list-disc list-inside space-y-2 ml-4 text-slate-400">
                            <li>Violate any applicable laws or regulations;</li>
                            <li>Attempt to gain unauthorized access to any part of the Site or Services;</li>
                            <li>Interfere with or disrupt the integrity or performance of the Services;</li>
                            <li>Use the Services to transmit malicious code, viruses, or harmful content;</li>
                            <li>Impersonate any person or entity, or misrepresent your affiliation with NexGuard.</li>
                          </ul>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 3 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">3.</span>
                            Accounts and Access
                          </h3>
                          <p className="leading-relaxed">
                            Some features of NexGuard may require you to connect via your Discord account or other platforms. You are responsible for maintaining the confidentiality of your account information and for all activities that occur under your account.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 4 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">4.</span>
                            Intellectual Property
                          </h3>
                          <p className="leading-relaxed">
                            All content, branding, graphics, code, and software on this website are the property of NexGuard or its licensors and are protected by copyright and trademark laws. You may not copy, distribute, or modify any part of the Site or Services without prior written consent.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 5 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">5.</span>
                            Third-Party Services
                          </h3>
                          <p className="leading-relaxed">
                            NexGuard may integrate or rely on third-party platforms (such as Discord) to provide functionality. You acknowledge and agree that NexGuard is not responsible for the availability, accuracy, or functionality of such third-party services.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 6 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">6.</span>
                            Termination
                          </h3>
                          <p className="leading-relaxed">
                            We reserve the right to suspend or terminate your access to the Site or Services at any time, without prior notice or liability, if you violate these Terms or engage in harmful behavior.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 7 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">7.</span>
                            Disclaimer of Warranties
                          </h3>
                          <p className="leading-relaxed">
                            The NexGuard Site and Services are provided "as is" and "as available." We make no warranties, express or implied, regarding the reliability, accuracy, or availability of the Services.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 8 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">8.</span>
                            Limitation of Liability
                          </h3>
                          <p className="leading-relaxed">
                            In no event shall NexGuard, its affiliates, or its developers be liable for any indirect, incidental, special, or consequential damages arising out of or in connection with your use of the Site or Services.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 9 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">9.</span>
                            Privacy
                          </h3>
                          <p className="leading-relaxed">
                            Our Privacy Policy explains how we collect, use, and protect your information. By using the Services, you consent to the collection and use of your data as outlined in our Privacy Policy.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 10 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">10.</span>
                            Changes to Terms
                          </h3>
                          <p className="leading-relaxed">
                            NexGuard reserves the right to modify these Terms at any time. We will notify users of any material changes. Continued use of the Site or Services after changes are made constitutes your acceptance of the revised Terms.
                          </p>
                        </div>

                        <Separator className="bg-slate-600" />

                        {/* Section 11 */}
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="text-cyan-400">11.</span>
                            Contact Information
                          </h3>
                          <p className="leading-relaxed mb-3">
                            If you have any questions about these Terms, please contact us at:
                          </p>
                          <div className="space-y-2 ml-4">
                            <div className="flex items-center gap-2 text-slate-400">
                              <Mail className="w-4 h-4 text-cyan-400" />
                              <span>Email: nexguards@gmail.com</span>
                            </div>
                            <div className="flex items-center gap-2 text-slate-400">
                              <MessageSquare className="w-4 h-4 text-purple-400" />
                              <span>Discord: EhCorn.</span>
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