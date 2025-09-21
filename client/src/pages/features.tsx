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

function Features() {
  console.log('*** FEATURES COMPONENT LOADED ***');
  
  return (
    <div className="min-h-screen bg-red-500 text-white p-8">
      <h1 className="text-6xl font-bold">FEATURES PAGE TEST</h1>
      <p className="text-2xl mt-4">This is a simple test page</p>
      <p className="text-lg mt-4">If you can see this, the routing is working</p>
    </div>
  );
}

export default Features;
