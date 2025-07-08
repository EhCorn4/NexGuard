import { GradientText } from "@/components/ui/gradient-text";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Download, Settings, Shield } from "lucide-react";
import { SiDiscord } from "react-icons/si";

export default function Invite() {
  const discordInviteUrl = "https://discord.com/oauth2/authorize?client_id=1389775821794705429";
  const supportServerUrl = "https://discord.gg/wpjZMPXaR";

  return (
    <div className="min-h-screen bg-[hsl(var(--nexguard-dark))] pt-24">
      <div className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            <GradientText>Ready to Protect Your Server?</GradientText>
          </h1>
          <p className="text-xl text-gray-300 mb-12">
            Join thousands of servers already using NexGuard to maintain order and enhance their community experience.
          </p>
          
          <Card className="bg-[hsl(var(--nexguard-darker))]/80 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 mb-12">
            <CardContent className="p-8">
              <div className="grid md:grid-cols-3 gap-8 mb-8">
                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mx-auto mb-4">
                    <Download className="text-white" size={24} />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">1. Invite Bot</h3>
                  <p className="text-gray-400 text-sm">Click the invite button to add NexGuard to your server</p>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mx-auto mb-4">
                    <Settings className="text-white" size={24} />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">2. Configure</h3>
                  <p className="text-gray-400 text-sm">Set up your preferences using our intuitive dashboard</p>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mx-auto mb-4">
                    <Shield className="text-white" size={24} />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">3. Stay Protected</h3>
                  <p className="text-gray-400 text-sm">Enjoy automated moderation and enhanced server features</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <a 
                  href={discordInviteUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block"
                >
                  <Button 
                    size="lg"
                    className="bg-[hsl(var(--discord-blurple))] hover:bg-[hsl(var(--discord-light))] text-white font-semibold text-xl px-12 py-4 transform hover:scale-105 transition-all duration-300"
                  >
                    <SiDiscord className="mr-3" size={24} />
                    Invite NexGuard to Your Server
                  </Button>
                </a>
                <p className="text-sm text-gray-400">
                  Required permissions: Administrator (for full functionality)
                </p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-[hsl(var(--nexguard-darker))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-purple))]/20">
            <CardContent className="p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Need Help Getting Started?</h3>
              <p className="text-gray-300 mb-4">Join our support server for setup assistance and community support.</p>
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
}
