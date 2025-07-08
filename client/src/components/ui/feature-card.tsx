import { Card, CardContent } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { memo } from "react";

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  benefits: string[];
  className?: string;
}

export const FeatureCard = memo(function FeatureCard({ icon: Icon, title, description, benefits, className }: FeatureCardProps) {
  return (
    <Card 
      className={cn(
        "feature-card-hover bg-[hsl(var(--nexguard-dark))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 hover:border-[hsl(var(--nexguard-cyan))]/50 animate-fade-in",
        className
      )}
      role="article"
      aria-labelledby={`feature-${title.replace(/\s+/g, '-').toLowerCase()}`}
    >
      <CardContent className="p-8">
        <div className="w-16 h-16 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-lg flex items-center justify-center mb-6">
          <Icon className="text-white" size={24} aria-hidden="true" />
        </div>
        <h3 
          id={`feature-${title.replace(/\s+/g, '-').toLowerCase()}`}
          className="text-xl font-semibold mb-3 text-white"
        >
          {title}
        </h3>
        <p className="text-gray-300 mb-4">{description}</p>
        <ul className="text-sm text-gray-400 space-y-1" role="list" aria-label="Feature benefits">
          {benefits.map((benefit, index) => (
            <li key={index} role="listitem">• {benefit}</li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
});
