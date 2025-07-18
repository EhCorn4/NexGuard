import { Link } from "wouter";
import { GradientText } from "@/components/ui/gradient-text";
import { Button } from "@/components/ui/button";
import { SiDiscord } from "react-icons/si";
import nexguardLogo from "@assets/Nexguard_1751937048860.png";
import nexguardBanner from "@assets/file_00000000ee7c61f7a421642c4ce3b538_1751936999714.png";
import nexguardIcon from "@assets/file_0000000003fc61f58b4fd114190f81c9_1751936993313.png";
import blrpLogo from "@assets/BLRP_new2_1751996269430.png";
import { memo } from "react";
import { useQuery } from "@tanstack/react-query";

const Home = memo(function Home() {
  // Fetch live bot status
  const { data: botStatus } = useQuery({
    queryKey: ['/api/bot/status'],
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const getBotStatusColor = (isOnline: boolean) => {
    return isOnline ? 'text-green-400' : 'text-red-400';
  };

  const getBotStatusText = (isOnline: boolean) => {
    return isOnline ? 'Online' : 'Offline';
  };

  return (
    <div className="min-h-screen hero-gradient circuit-pattern flex items-center justify-center relative overflow-hidden">
      <div 
        className="absolute inset-0 bg-cover bg-center opacity-20" 
        style={{ backgroundImage: `url(${nexguardIcon})` }}
      ></div>
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      
      <div className="container mx-auto px-4 text-center relative z-10 pt-20">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8 flex justify-center">
            <img 
              src={nexguardBanner} 
              alt="NexGuard Banner" 
              className="w-64 md:w-80 h-auto max-w-full animate-float"
            />
          </div>
          

          
          <p className="text-xl md:text-2xl text-[hsl(var(--nexguard-cyan))] mb-6 font-medium">
            PROTECT. MANAGE. ENHANCE.
          </p>
          
          <p className="text-lg md:text-xl text-gray-300 mb-12 max-w-2xl mx-auto leading-relaxed">
            The ultimate Discord moderation and quality-of-life bot designed to keep your server safe, organized, and thriving. Advanced automation meets intuitive management.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/invite">
              <Button size="lg" className="bg-[hsl(var(--discord-blurple))] hover:bg-[hsl(var(--discord-light))] text-white font-semibold text-lg px-8 py-4 transform hover:scale-105 transition-all duration-300">
                <SiDiscord className="mr-2" size={20} />
                Invite to Server
              </Button>
            </Link>
            
            <Link href="/features">
              <Button 
                variant="outline" 
                size="lg" 
                className="border-2 border-[hsl(var(--nexguard-cyan))] text-[hsl(var(--nexguard-cyan))] hover:bg-[hsl(var(--nexguard-cyan))] hover:text-[hsl(var(--nexguard-dark))] font-semibold text-lg px-8 py-4 transform hover:scale-105 transition-all duration-300"
              >
                Explore Features
              </Button>
            </Link>
          </div>
          
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-2xl mx-auto">
            <div className="text-center">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">
                {botStatus?.guildsCount || 0}+
              </div>
              <div className="text-sm text-gray-400">Servers Protected</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">
                {botStatus?.usersCount ? formatNumber(botStatus.usersCount) : '0'}+
              </div>
              <div className="text-sm text-gray-400">Users Secured</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">
                {botStatus?.uptime || '0s'}
              </div>
              <div className="text-sm text-gray-400">Uptime</div>
            </div>
            <div className="text-center">
              <div className={`text-3xl font-bold ${getBotStatusColor(botStatus?.isOnline || false)}`}>
                {getBotStatusText(botStatus?.isOnline || false)}
              </div>
              <div className="text-sm text-gray-400">Bot Status</div>
            </div>
          </div>

          {/* Community Highlight Section */}
          <div className="mt-20 max-w-3xl mx-auto">
            <div className="text-center mb-8">
              <GradientText className="text-2xl md:text-3xl font-bold mb-4">
                Community Highlight
              </GradientText>
              <p className="text-gray-400 text-lg">
                Featuring our amazing beta testing community
              </p>
            </div>
            
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-8 text-center transform hover:scale-105 transition-all duration-300">
              <div className="flex justify-center mb-6">
                <div className="w-20 h-20 rounded-full overflow-hidden border-2 border-gradient-to-br from-cyan-400 to-purple-500 p-1">
                  <img 
                    src={blrpLogo} 
                    alt="BlueLine RolePlay Logo" 
                    className="w-full h-full object-cover rounded-full"
                  />
                </div>
              </div>
              
              <h3 className="text-2xl font-bold text-white mb-4">
                BlueLine RolePlay (BLRP)
              </h3>
              
              <p className="text-gray-300 text-lg mb-6 leading-relaxed">
                Our first active beta testers who are diligently helping us identify and fix any kinks in NexGuard. 
                Their dedication to testing and feedback is helping shape the future of Discord moderation.
              </p>
              
              <div className="flex justify-center items-center space-x-4 mb-6">
                <div className="px-4 py-2 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-full border border-cyan-500/30">
                  <span className="text-cyan-400 font-semibold">Beta Testers</span>
                </div>
                <div className="px-4 py-2 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-full border border-green-500/30">
                  <span className="text-green-400 font-semibold">Active Community</span>
                </div>
              </div>
              
              <p className="text-[hsl(var(--nexguard-cyan))] font-semibold text-lg">
                "Thank you for helping us build a better Discord experience!"
              </p>
            </div>
          </div>
        </div>
      </div>


    </div>
  );
});

export default Home;
