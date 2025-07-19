import { useQuery } from "@tanstack/react-query";
import { GradientText } from "@/components/ui/gradient-text";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Heart, MessageCircle, Rocket, Users, Wrench, Star, Shield, Gamepad2, ChevronDown, ChevronUp } from "lucide-react";
import { SiDiscord } from "react-icons/si";
import type { NewsUpdate } from "@shared/schema";
import { memo, useState } from "react";
import nexguardIcon from "@assets/file_0000000003fc61f58b4fd114190f81c9_1751936993313.png";

const categoryIcons = {
  "NEW FEATURE": { icon: Rocket, color: "from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))]", textColor: "text-[hsl(var(--nexguard-cyan))]" },
  "COMMUNITY": { icon: Users, color: "from-[hsl(var(--nexguard-purple))] to-[hsl(var(--nexguard-cyan))]", textColor: "text-[hsl(var(--nexguard-purple))]" },
  "UPDATE": { icon: Wrench, color: "from-yellow-400 to-orange-500", textColor: "text-yellow-400" },
  "SECURITY": { icon: Shield, color: "from-green-400 to-blue-500", textColor: "text-green-400" },
  "GAMES": { icon: Gamepad2, color: "from-pink-400 to-purple-500", textColor: "text-pink-400" },
  "FEATURED": { icon: Star, color: "from-indigo-400 to-purple-600", textColor: "text-indigo-400" },
};

// Extended content for each news update
const extendedContent: Record<number, string> = {
  1: "The Advanced Auto-Reply System represents a breakthrough in Discord automation. Built with sophisticated keyword matching algorithms, it supports multiple trigger types including exact matches, partial matches, starts-with, and ends-with patterns. Each auto-reply can feature rich embeds with custom colors, titles, descriptions, and footers. The system includes comprehensive analytics showing trigger counts, user engagement, and performance metrics. With built-in cooldown protection and spam prevention, administrators can create responsive, intelligent conversations while maintaining server quality and user experience.",
  2: "Our Comprehensive AutoMod System provides enterprise-level content moderation with real-time message scanning and intelligent threat detection. The six specialized commands cover spam protection with configurable message limits and time windows, advanced link filtering with Discord invite blocking, sophisticated bad words detection with strict mode options, and comprehensive word management tools. Each violation triggers customizable escalation actions including warnings, timeouts, kicks, and bans. The system integrates seamlessly with PostgreSQL for persistent settings and provides detailed logging for administrative oversight.",
  3: "The Custom Moderation Role Management system revolutionizes Discord server permissions by allowing administrators to define custom moderation roles beyond Discord's default permissions. With advanced hierarchy validation, the system prevents privilege escalation while ensuring proper bot permissions. The `/modrole` command provides intuitive role setting with visual confirmation, while `/modpermissions` offers detailed permission analysis. Role conflicts are automatically resolved, and all settings persist across server restarts with comprehensive PostgreSQL integration.",
  4: "Live Bot Statistics Integration brings unprecedented transparency to NexGuard's performance monitoring. The real-time system displays live data including server count (9+), user count (167+), and accurate uptime tracking with sub-second precision. Statistics update every 15 seconds through automated background processes, providing administrators and users with current operational status. The integration spans across all website pages, ensuring consistent and reliable information display with database persistence and error handling.",
  5: "The Multi-Category Ticket System transforms Discord support management with advanced organization and automation. Featuring Discord channel integration, administrators can create custom ticket categories that automatically place new tickets in appropriate Discord categories. The system supports comprehensive filtering by status, priority, category, and assignment. Staff can manage tickets efficiently with role-based permissions, automatic notifications, and detailed tracking. The PostgreSQL backend ensures data persistence and enables advanced reporting capabilities.",
  6: "With 41+ commands now available, NexGuard offers the most comprehensive Discord bot feature set in its class. The massive expansion covers six major categories: admin commands for server configuration, moderation commands for user management, ticket commands for support systems, utility commands for server information, auto-reply commands for automated responses, and automod commands for content filtering. Each command includes detailed help documentation, permission validation, error handling, and logging integration, providing administrators with professional-grade tools for community management.",
  7: "Reaching our community milestone of 167+ users protected across 9+ Discord servers represents the growing trust in NexGuard's advanced capabilities. This achievement reflects our commitment to providing reliable, sophisticated moderation tools that scale with community needs. Our user base spans gaming communities, educational servers, business organizations, and hobby groups, each benefiting from NexGuard's comprehensive feature set. We continue expanding our reach while maintaining the high-quality experience that defines the NexGuard platform.",
  8: "The Enhanced Welcome System delivers a premium first-impression experience for new server members. Rich embed support enables custom colors, thumbnails, images, and interactive elements that reflect your server's unique identity. The advanced placeholder system supports dynamic content including user mentions, server statistics, and custom variables. Channel-specific setup allows different welcome messages for various entry points, while comprehensive configuration options provide flexibility for servers of all sizes and purposes."
};

const Community = memo(function Community() {
  const { data: news, isLoading, error } = useQuery<NewsUpdate[]>({
    queryKey: ["/api/news"],
  });
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set());

  const toggleExpanded = (id: number) => {
    setExpandedCards(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

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
      <div 
        className="absolute inset-0 bg-center opacity-20" 
        style={{ 
          backgroundImage: `url(${nexguardIcon})`,
          backgroundSize: '1920px 1080px',
          backgroundRepeat: 'no-repeat'
        }}
      ></div>
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
              const isExpanded = expandedCards.has(update.id);
              const hasExtendedContent = extendedContent[update.id];
              
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
                    
                    {/* Main content */}
                    <p className="text-gray-300 mb-4">{update.content}</p>
                    
                    {/* Extended content - shown when expanded */}
                    {isExpanded && hasExtendedContent && (
                      <div className="mb-4 p-4 bg-[hsl(var(--nexguard-dark))]/30 rounded-lg border border-[hsl(var(--nexguard-cyan))]/10">
                        <h4 className="text-lg font-semibold text-[hsl(var(--nexguard-cyan))] mb-3">Detailed Overview</h4>
                        <p className="text-gray-300 leading-relaxed">{hasExtendedContent}</p>
                      </div>
                    )}
                    
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
                      {hasExtendedContent && (
                        <button 
                          onClick={() => toggleExpanded(update.id)}
                          className="flex items-center text-[hsl(var(--nexguard-cyan))] hover:text-[hsl(var(--nexguard-cyan))]/80 text-sm font-semibold transition-colors duration-200"
                        >
                          {isExpanded ? (
                            <>
                              Show Less
                              <ChevronUp className="ml-1" size={16} />
                            </>
                          ) : (
                            <>
                              Read More
                              <ChevronDown className="ml-1" size={16} />
                            </>
                          )}
                        </button>
                      )}
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
