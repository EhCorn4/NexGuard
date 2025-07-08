import { Shield } from "lucide-react";
import { cn } from "@/lib/utils";

interface AnimatedShieldProps {
  className?: string;
  size?: number;
}

export function AnimatedShield({ className, size = 32 }: AnimatedShieldProps) {
  return (
    <div className={cn(
      "bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center animate-float shadow-2xl",
      className
    )}>
      <Shield className="text-white" size={size} />
    </div>
  );
}
