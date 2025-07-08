import { useQuery } from "@tanstack/react-query";
import { GradientText } from "@/components/ui/gradient-text";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Heart, MessageCircle, Rocket, Users, Wrench, Star, Shield, Gamepad2 } from "lucide-react";
import { SiDiscord } from "react-icons/si";
import type { NewsUpdate } from "@shared/schema";
import { memo } from "react";

const categoryIcons = {
  "NEW FEATURE": { icon: Rocket, color: "from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))]", textColor: "text-[hsl(var(--nexguard-cyan))]" },
  "COMMUNITY": { icon: Users, color: "from-[hsl(var(--nexguard-purple))] to-[hsl(var(--nexguard-cyan))]", textColor: "text-[hsl(var(--nexguard-purple))]" },
  "UPDATE": { icon: Wrench, color: "from-yellow-400 to-orange-500", textColor: "text-yellow-400" },
  "SECURITY": { icon: Shield, color: "from-green-400 to-blue-500", textColor: "text-green-400" },
  "GAMES": { icon: Gamepad2, color: "from-pink-400 to-purple-500", textColor: "text-pink-400" },
  "FEATURED": { icon: Star, color: "from-indigo-400 to-purple-600", textColor: "text-indigo-400" },
};

const Community = memo(function Community() {
  const { data: news, isLoading, error } = useQuery<NewsUpdate[]>({
    queryKey: ["/api/news"],
  });

  if (error) {
    return (
      <div className="min-h-screen bg-[hsl(var(--nexguard-dark))] pt-24 px-4">
        <div className="container mx-auto">
          <Alert className="max-w-2xl mx-auto">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Failed to load community updates. Please try again later.
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
          title="Community Updates"
          description="Stay updated with the latest features, improvements, and community highlights from NexGuard."
        />
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {isLoading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <Card key={i} className="bg-[hsl(var(--nexguard-darker))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20">
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    <Skeleton className="w-8 h-8 rounded-full mr-3" />
                    <div className="flex-1">
                      <Skeleton className="h-4 w-20 mb-1" />
                      <Skeleton className="h-3 w-16" />
                    </div>
                  </div>
                  <Skeleton className="h-6 w-3/4 mb-3" />
                  <Skeleton className="h-4 w-full mb-2" />
                  <Skeleton className="h-4 w-full mb-2" />
                  <Skeleton className="h-4 w-2/3 mb-4" />
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <Skeleton className="h-4 w-8" />
                      <Skeleton className="h-4 w-8" />
                    </div>
                    <Skeleton className="h-4 w-16" />
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            news?.map((update) => {
              const categoryInfo = categoryIcons[update.category as keyof typeof categoryIcons] || categoryIcons["NEW FEATURE"];
              const IconComponent = categoryInfo.icon;
              
              return (
                <Card 
                  key={update.id} 
                  className="bg-[hsl(var(--nexguard-darker))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 hover:border-[hsl(var(--nexguard-cyan))]/50 transition-all duration-300"
                >
                  <CardContent className="p-6">
                    <div className="flex items-center mb-4">
                      <div className={`w-8 h-8 bg-gradient-to-br ${categoryInfo.color} rounded-full flex items-center justify-center mr-3`}>
                        <IconComponent className="text-white" size={16} />
                      </div>
                      <div>
                        <span className={`text-sm font-semibold ${categoryInfo.textColor}`}>
                          {update.category}
                        </span>
                        <div className="text-xs text-gray-400">
                          {new Date(update.publishedAt).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    <h3 className="text-xl font-semibold text-white mb-3">{update.title}</h3>
                    <p className="text-gray-300 mb-4">{update.content}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 text-sm text-gray-400">
                        <span className="flex items-center">
                          <Heart className="mr-1" size={14} />
                          {update.likes}
                        </span>
                        <span className="flex items-center">
                          <MessageCircle className="mr-1" size={14} />
                          {update.comments}
                        </span>
                      </div>
                      <button className="text-[hsl(var(--nexguard-cyan))] hover:text-[hsl(var(--nexguard-cyan))]/80 text-sm font-semibold">
                        Read More
                      </button>
                    </div>
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>
        
        <div className="text-center mt-12">
          <a 
            href="https://discord.gg/wpjZMPXaR"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block"
          >
            <Button 
              size="lg"
              className="bg-[hsl(var(--nexguard-cyan))] hover:bg-[hsl(var(--nexguard-cyan))]/80 text-[hsl(var(--nexguard-dark))] font-semibold text-lg px-8 py-4 transform hover:scale-105 transition-all duration-300"
            >
              <SiDiscord className="mr-2" size={20} />
              Join Our Community
            </Button>
          </a>
        </div>
      </div>
    </div>
  );
});

export default Community;
