import { useQuery } from "@tanstack/react-query";
import { GradientText } from "@/components/ui/gradient-text";
import { FeatureCard } from "@/components/ui/feature-card";
import { PageHeader } from "@/components/ui/page-header";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { StaggerContainer, StaggerItem } from "@/components/ui/stagger-container";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Gavel, BarChart3, Users, Bell, Gamepad2, Settings, Shield, Ticket, Command, Zap, Cog, FileText, ShieldCheck } from "lucide-react";
import type { Feature } from "@shared/schema";
import { memo } from "react";

const iconMap = {
  gavel: Gavel,
  "chart-line": BarChart3,
  users: Users,
  bell: Bell,
  gamepad: Gamepad2,
  cog: Cog,
  shield: Shield,
  ticket: Ticket,
  command: Command,
  zap: Zap,
  "file-text": FileText,
  "shield-check": ShieldCheck,
};

const Features = memo(function Features() {
  const { data: features, isLoading, error } = useQuery<Feature[]>({
    queryKey: ["/api/features"],
  });

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
          description="NexGuard offers comprehensive Discord bot functionality with 44+ slash commands, universal logging system, advanced automod protection, and real-time analytics to enhance your server management experience."
        />
        
        {/* Bot Status Section */}
        <div className="mb-12 text-center">
          <div className="inline-flex items-center gap-4 bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-lg px-6 py-3">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-300">Bot Online & Ready</span>
            <div className="w-px h-4 bg-slate-600"></div>
            <span className="text-sm text-[hsl(var(--nexguard-cyan))]">44 Commands</span>
            <div className="w-px h-4 bg-slate-600"></div>
            <span className="text-sm text-[hsl(var(--nexguard-cyan))]">9 Servers</span>
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
