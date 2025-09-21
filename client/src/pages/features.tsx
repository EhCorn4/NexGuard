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
  
  // Debug logging
  console.log('Features component - data:', features);
  console.log('Features component - isLoading:', isLoading);
  console.log('Features component - error:', error);

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
    console.log('Features component - error condition reached:', error);
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
    <div className="min-h-screen bg-slate-900 pt-24 px-4">
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8 text-center">Bot Features</h1>
        
        {/* Debug Info */}
        <div className="bg-slate-800 p-4 rounded-lg mb-8 text-white">
          <p>Loading: {isLoading ? 'true' : 'false'}</p>
          <p>Error: {error ? String(error) : 'none'}</p>
          <p>Features count: {features ? features.length : '0'}</p>
        </div>
        
        {/* Simple feature list */}
        <div className="space-y-4">
          {isLoading ? (
            <p className="text-white">Loading features...</p>
          ) : features ? (
            features.map((feature) => (
              <div key={feature.id} className="bg-slate-800 p-6 rounded-lg text-white">
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-gray-300">{feature.description}</p>
                <p className="text-sm text-gray-500 mt-2">Icon: {feature.icon}</p>
              </div>
            ))
          ) : (
            <p className="text-red-400">No features data available</p>
          )}
        </div>
      </div>
    </div>
  );
});

export default Features;
