import { GradientText } from "@/components/ui/gradient-text";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Heart, Coffee, Shield, Users, Zap } from "lucide-react";
import { SiPaypal } from "react-icons/si";
import { memo } from "react";
import { useQuery } from "@tanstack/react-query";

const Donate = memo(function Donate() {
  const paypalUrl = "https://paypal.me/ehcorn4?country.x=CA&locale.x=en_US";

  // Real aggregated stats from the guilds.member_count column
  const { data: publicStats } = useQuery<{ totalServers: number; totalMembers: number }>({
    queryKey: ['/api/bot/public-stats'],
    refetchInterval: 60000,
  });

  const totalServers = publicStats?.totalServers ?? 0;
  const totalMembers = publicStats?.totalMembers ?? 0;

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const impactStats = [
    {
      icon: <Shield className="text-[hsl(var(--nexguard-cyan))]" size={32} />,
      title: "Servers Protected",
      description: "Discord communities using NexGuard",
      stat: `${totalServers}+ Servers`
    },
    {
      icon: <Zap className="text-[hsl(var(--nexguard-cyan))]" size={32} />,
      title: "Commands Available",
      description: "Moderation and utility commands",
      stat: "67+ Commands"
    },
    {
      icon: <Users className="text-[hsl(var(--nexguard-cyan))]" size={32} />,
      title: "Users Helped",
      description: "Community members protected",
      stat: `${formatNumber(totalMembers)}+ Users`
    }
  ];

  return (
    <div className="min-h-screen hero-gradient circuit-pattern pt-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      <div className="container mx-auto px-4 py-20 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <PageHeader 
              title={
                <span>
                  Support <GradientText>NexGuard</GradientText>
                </span>
              }
              description="NexGuard is a passion project created to help Discord communities stay safe and organized. If you find value in what I've built and would like to support its continued development, any contribution would mean the world to me."
            />
            
            <div className="flex items-center justify-center gap-2 mt-6">
              <Heart className="text-red-500" size={20} />
              <span className="text-gray-300">Created with care for the Discord community</span>
              <Heart className="text-red-500" size={20} />
            </div>
          </div>

          {/* Impact Statistics */}
          <div className="grid md:grid-cols-3 gap-6 mb-16">
            {impactStats.map((stat, index) => (
              <Card key={index} className="bg-[hsl(var(--nexguard-darker))]/80 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 text-center">
                <CardContent className="p-6">
                  <div className="flex justify-center mb-4">
                    {stat.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{stat.title}</h3>
                  <p className="text-gray-400 text-sm mb-3">{stat.description}</p>
                  <div className="text-2xl font-bold text-[hsl(var(--nexguard-cyan))]">{stat.stat}</div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Donation Section */}
          <Card className="bg-[hsl(var(--nexguard-darker))]/80 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 mb-16">
            <CardContent className="p-12 text-center">
              <div className="max-w-2xl mx-auto">
                <div className="mb-8">
                  <SiPaypal size={64} className="text-[#0070ba] mx-auto mb-6" />
                  <h3 className="text-2xl font-bold text-white mb-4">Show Your Appreciation</h3>
                  <p className="text-gray-300 text-lg leading-relaxed mb-6">
                    Building and maintaining NexGuard takes countless hours of development, testing, and support. 
                    Your donations help cover hosting costs and motivate me to keep improving the bot with new features 
                    and bug fixes.
                  </p>
                  <p className="text-gray-400 text-sm mb-8">
                    Every donation, no matter the size, is deeply appreciated and helps ensure NexGuard remains 
                    free and accessible to all Discord communities.
                  </p>
                </div>
                
                <a 
                  href={paypalUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block"
                >
                  <Button 
                    size="lg"
                    className="bg-[#0070ba] hover:bg-[#005ea6] text-white font-semibold text-lg px-12 py-6 transform hover:scale-105 transition-all duration-300"
                  >
                    <SiPaypal className="mr-3" size={24} />
                    Donate via PayPal
                  </Button>
                </a>
                
                <p className="text-gray-500 text-sm mt-4">
                  Secure payment processing through PayPal
                </p>
              </div>
            </CardContent>
          </Card>



          {/* Why Donate Section */}
          <Card className="bg-[hsl(var(--nexguard-darker))]/80 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 mb-16">
            <CardHeader>
              <CardTitle className="text-2xl text-center text-white">How Your Support Helps</CardTitle>
            </CardHeader>
            <CardContent className="p-8">
              <div className="grid md:grid-cols-2 gap-8 text-center">
                <div>
                  <div className="w-16 h-16 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mx-auto mb-4">
                    <Coffee className="text-white" size={24} />
                  </div>
                  <h4 className="text-lg font-semibold text-white mb-3">Development Time</h4>
                  <p className="text-gray-400 text-sm">
                    Your donations allow me to dedicate more time to adding new features, 
                    fixing bugs, and improving NexGuard's performance.
                  </p>
                </div>
                <div>
                  <div className="w-16 h-16 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mx-auto mb-4">
                    <Shield className="text-white" size={24} />
                  </div>
                  <h4 className="text-lg font-semibold text-white mb-3">Server Hosting</h4>
                  <p className="text-gray-400 text-sm">
                    Keeping NexGuard online 24/7 requires reliable hosting. 
                    Your support helps cover these essential operational costs.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Thank You Message */}
          <Card className="bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/10 to-[hsl(var(--nexguard-purple))]/10 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/30">
            <CardContent className="p-8 text-center">
              <Heart className="text-red-500 mx-auto mb-4" size={48} />
              <h3 className="text-2xl font-bold text-white mb-4">From the Bottom of My Heart, Thank You</h3>
              <p className="text-gray-300 max-w-2xl mx-auto leading-relaxed">
                Whether you choose to donate or simply use NexGuard in your community, your support means everything to me. 
                Knowing that this bot helps make Discord servers safer and more organized is incredibly rewarding. 
                If you do decide to contribute, please know that every dollar goes directly toward making NexGuard even better.
              </p>
              <div className="mt-8 space-y-4">
                <p className="text-gray-400 text-sm">
                  NexGuard will always be free to use. Donations are entirely optional and deeply appreciated.
                </p>
                <Button 
                  variant="outline" 
                  className="border-[hsl(var(--nexguard-cyan))] text-[hsl(var(--nexguard-cyan))] hover:bg-[hsl(var(--nexguard-cyan))] hover:text-white"
                  onClick={() => window.open('https://discord.gg/wpjZMPXaRT', '_blank')}
                >
                  <Users className="mr-2" size={18} />
                  Join Our Discord Community
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
});

export default Donate;