import { FEATURES, FEATURES_COUNT, COMMANDS_COUNT, SERVERS_COUNT, FEATURE_ICONS } from "@/data/features";
import { FeatureCard } from "@/components/ui/feature-card";
import { PageHeader } from "@/components/ui/page-header";
import { StaggerContainer, StaggerItem } from "@/components/ui/stagger-container";
import { HoverScale } from "@/components/ui/hover-scale";
import { Settings } from "lucide-react";

function Features() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 pt-24">
      <div className="container mx-auto px-4 py-12">
        <PageHeader 
          title="Bot Features"
          description={`NexGuard offers comprehensive Discord bot functionality with ${COMMANDS_COUNT} slash commands, enterprise security systems, professional ticket system, and real-time analytics.`}
          showLogo={false}
        />

        <StaggerContainer className="grid md:grid-cols-2 lg:grid-cols-3 gap-8" data-testid="grid-features">
          {FEATURES.map((feature, index) => (
            <StaggerItem key={feature.slug} index={index}>
              <HoverScale>
                <div data-testid={`card-feature-${feature.slug}`}>
                  <FeatureCard
                    icon={FEATURE_ICONS[feature.icon] || Settings}
                    title={feature.title}
                    description={feature.description}
                    benefits={feature.benefits}
                  />
                </div>
              </HoverScale>
            </StaggerItem>
          ))}
        </StaggerContainer>

        {/* Stats Banner */}
        <div className="mt-16 text-center" data-testid="banner-stats">
          <div className="inline-flex items-center gap-4 bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-full px-8 py-4">
            <span className="text-sm text-cyan-400">{FEATURES_COUNT} Features</span>
            <div className="w-px h-4 bg-slate-600"></div>
            <span className="text-sm text-cyan-400">{COMMANDS_COUNT} Commands</span>
            <div className="w-px h-4 bg-slate-600"></div>
            <span className="text-sm text-cyan-400">{SERVERS_COUNT} Servers</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Features;