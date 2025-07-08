import { useQuery } from "@tanstack/react-query";
import { GradientText } from "@/components/ui/gradient-text";
import { FeatureCard } from "@/components/ui/feature-card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Gavel, BarChart3, Users, Bell, Gamepad2, Settings } from "lucide-react";
import type { Feature } from "@shared/schema";

const iconMap = {
  gavel: Gavel,
  "chart-line": BarChart3,
  users: Users,
  bell: Bell,
  gamepad: Gamepad2,
  cog: Settings,
};

export default function Features() {
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
    <div className="min-h-screen bg-[hsl(var(--nexguard-darker))] pt-24">
      <div className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <GradientText>Powerful Features</GradientText>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            NexGuard combines cutting-edge moderation tools with quality-of-life features to create the perfect Discord server experience.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {isLoading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="space-y-4">
                <Skeleton className="h-20 w-20 rounded-lg" />
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
              </div>
            ))
          ) : (
            features?.map((feature) => {
              const IconComponent = iconMap[feature.icon as keyof typeof iconMap] || Settings;
              return (
                <FeatureCard
                  key={feature.id}
                  icon={IconComponent}
                  title={feature.title}
                  description={feature.description}
                  benefits={feature.benefits || []}
                />
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
