import { useQuery } from "@tanstack/react-query";
import { GradientText } from "@/components/ui/gradient-text";
import { FeatureCard } from "@/components/ui/feature-card";
import { PageHeader } from "@/components/ui/page-header";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { StaggerContainer, StaggerItem } from "@/components/ui/stagger-container";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Gavel, BarChart3, Users, Bell, Gamepad2, Settings, Shield, Ticket, Command, Zap, Cog, FileText, ShieldCheck, ShieldAlert, ShieldX, Activity, HeartPulse, Plug } from "lucide-react";
import type { Feature } from "@shared/schema";
import { memo } from "react";

const iconMap = {
  gavel: Gavel,
  activity: Activity,
  users: Users,
  book: FileText,
  bot: Command,
  monitor: Settings,
  shield: Shield,
  ticket: Ticket,
  "chart-bar": BarChart3,
  gauge: HeartPulse,
  api: Plug,
  megaphone: Bell,
  network: Zap,
  "chart-line": BarChart3,
  bell: Bell,
  gamepad: Gamepad2,
  cog: Settings,
  command: Command,
  zap: Zap,
  "file-text": FileText,
  "shield-check": ShieldCheck,
  "shield-alert": ShieldAlert,
  "shield-x": ShieldX,
  "heart-pulse": HeartPulse,
  "plug": Plug,
};

const Features = memo(function Features() {
  const { data: features, isLoading, error } = useQuery<Feature[]>({
    queryKey: ["/api/features"],
  });

  // Fetch live bot status
  const { data: botStatus } = useQuery({
    queryKey: ['/api/bot/status'],
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Type-safe bot status data
  const safeGuildsCount = (botStatus as any)?.guildsCount || 0;
  const safeUsersCount = (botStatus as any)?.usersCount || 0;
  const safeIsOnline = (botStatus as any)?.isOnline || false;

  if (error) {
    return (
      <div className="min-h-screen bg-[hsl(var(--nexguard-darker))] pt-24 px-4">
        <div className="container mx-auto">
          <Alert className="max-w-2xl mx-auto">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Failed to load features. Please try again later.
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen hero-gradient circuit-pattern pt-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      <div className="container mx-auto px-4 py-20 relative z-10">
        <PageHeader 
          title="Bot Features"
          description={`NexGuard offers comprehensive Discord bot functionality with 66+ slash commands, enterprise security systems, professional ticket system, live server statistics channels, reaction roles, comprehensive event logging, advanced automod protection, performance monitoring, and real-time analytics to enhance your server management experience across ${safeGuildsCount}+ servers.`}
        />
        
        {/* Bot Status Section */}
        <div className="mb-12 text-center">
          <div className="inline-flex items-center gap-4 bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-lg px-6 py-3">
            <div className={`w-2 h-2 rounded-full animate-pulse ${safeIsOnline ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span className="text-sm text-gray-300">{safeIsOnline ? 'Bot Online & Ready' : 'Bot Offline'}</span>
            <div className="w-px h-4 bg-slate-600"></div>
            <span className="text-sm text-[hsl(var(--nexguard-cyan))]">66 Commands</span>
            <div className="w-px h-4 bg-slate-600"></div>
            <span className="text-sm text-[hsl(var(--nexguard-cyan))]">{safeGuildsCount}+ Servers</span>
            <div className="w-px h-4 bg-slate-600"></div>
            <span className="text-sm text-[hsl(var(--nexguard-cyan))]">{safeUsersCount}+ Users</span>
          </div>
        </div>
        
        
        <StaggerContainer className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {isLoading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <StaggerItem key={i}>
                <div className="space-y-4">
                  <Skeleton className="h-20 w-20 rounded-lg" />
                  <Skeleton className="h-6 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3" />
                </div>
              </StaggerItem>
            ))
          ) : (
            features?.map((feature, index) => {
              const IconComponent = iconMap[feature.icon as keyof typeof iconMap] || Settings;
              return (
                <StaggerItem key={feature.id} index={index}>
                  <FeatureCard
                    icon={IconComponent}
                    title={feature.title}
                    description={feature.description}
                    benefits={feature.benefits || []}
                  />
                </StaggerItem>
              );
            })
          )}
        </StaggerContainer>
      </div>
    </div>
  );
});

export default Features;
