import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { SiDiscord } from "react-icons/si";
import nexguardBanner from "@assets/file_00000000ee7c61f7a421642c4ce3b538_1751936999714.png";
import nexguardIcon from "@assets/file_0000000003fc61f58b4fd114190f81c9_1751936993313.png";
import { memo } from "react";
import { useQuery } from "@tanstack/react-query";
import { SEOHead } from "@/components/optimized/seo-head";
import { OptimizedImage } from "@/components/optimized/image-optimization";

const Home = memo(function Home() {
  // Fetch live bot status
  const { data: botStatus } = useQuery({
    queryKey: ['/api/bot/status'],
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Fetch real aggregated stats from the guilds.member_count column
  const { data: publicStats } = useQuery<{ totalServers: number; totalMembers: number }>({
    queryKey: ['/api/bot/public-stats'],
    refetchInterval: 60000,
  });

  // Type-safe bot status data — prefer real member_count aggregates, fall back to bot_status
  const safeGuildsCount = publicStats?.totalServers ?? (botStatus as any)?.guildsCount ?? 0;
  const safeUsersCount = publicStats?.totalMembers ?? (botStatus as any)?.usersCount ?? 0;
  const safeIsOnline = (botStatus as any)?.isOnline || false;

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
    <>
      <SEOHead 
        title="Home"
        description={`NexGuard - Professional Discord bot with advanced moderation, ticket system, analytics, and comprehensive server management. Protecting ${formatNumber(safeUsersCount)}+ users across ${safeGuildsCount}+ servers.`}
        keywords="discord bot, moderation bot, discord moderation, server management, discord utilities, ticket system, automod, discord analytics"
        image="/nexguard-banner.png"
        type="website"
      />
      <div className="min-h-screen hero-gradient circuit-pattern flex items-center justify-center relative overflow-hidden">
      <div 
        className="absolute inset-0 bg-cover bg-center opacity-20" 
        style={{ backgroundImage: `url(${nexguardIcon})` }}
      ></div>
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      
      <div className="container mx-auto px-4 text-center relative z-10 pt-20">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8 flex justify-center">
            <OptimizedImage
              src={nexguardBanner} 
              alt="NexGuard - Professional Discord Bot Banner" 
              className="w-64 md:w-80 h-auto max-w-full animate-float"
              width={320}
              height={160}
              priority
              loading="eager"
            />
          </div>
          

          
          <p className="text-xl md:text-2xl text-[hsl(var(--nexguard-cyan))] mb-6 font-medium">
            PROTECT. MANAGE. ENHANCE.
          </p>
          
          <p className="text-lg md:text-xl text-gray-300 mb-12 max-w-2xl mx-auto leading-relaxed">
            The ultimate Discord moderation and quality-of-life bot with 60+ commands, professional ticket system, live server statistics channels, reaction roles, universal logging, and advanced automod protection. Keep your server safe, organized, and thriving with enterprise-grade automation.
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
                {safeGuildsCount}+
              </div>
              <div className="text-sm text-gray-400">Servers Protected</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">
                {formatNumber(safeUsersCount)}+
              </div>
              <div className="text-sm text-gray-400">Users Secured</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">
                24/7
              </div>
              <div className="text-sm text-gray-400">Support</div>
            </div>
            <div className="text-center">
              <div className={`text-3xl font-bold ${getBotStatusColor(safeIsOnline)}`}>
                {getBotStatusText(safeIsOnline)}
              </div>
              <div className="text-sm text-gray-400">Bot Status</div>
            </div>
          </div>

        </div>
      </div>
      </div>
    </>
  );
});

export default Home;
