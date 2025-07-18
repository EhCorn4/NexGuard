import { useQuery } from "@tanstack/react-query";
import { Bot, Wifi, WifiOff } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { motion } from "framer-motion";
import type { BotStatus } from "@shared/schema";

interface BotStatusIndicatorProps {
  compact?: boolean;
  className?: string;
}

export function BotStatusIndicator({ compact = false, className = "" }: BotStatusIndicatorProps) {
  const { data: botStatus, isLoading } = useQuery<BotStatus>({
    queryKey: ['/api/bot/status'],
    refetchInterval: 15000, // Refetch every 15 seconds
  });

  if (isLoading) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
        {!compact && <span className="text-sm text-gray-400">Loading...</span>}
      </div>
    );
  }

  const isOnline = botStatus?.isOnline || false;
  const statusColor = isOnline ? 'bg-green-400' : 'bg-red-400';
  const statusText = isOnline ? 'Online' : 'Offline';
  const StatusIcon = isOnline ? Wifi : WifiOff;

  if (compact) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className={`flex items-center gap-2 ${className}`}>
              <motion.div
                className={`w-2 h-2 rounded-full ${statusColor}`}
                animate={isOnline ? { scale: [1, 1.2, 1] } : {}}
                transition={{ duration: 2, repeat: Infinity }}
              />
              <Bot className="w-4 h-4 text-gray-400" />
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <div className="text-sm">
              <div className="font-medium">NexGuard Bot</div>
              <div className="text-xs text-cyan-400 mt-1">
                24/7 Support
              </div>
              <div className={`text-xs ${isOnline ? 'text-green-400' : 'text-red-400'}`}>
                {statusText}
              </div>
              {botStatus && (
                <div className="text-xs text-gray-400 mt-1">
                  {botStatus.guildsCount} servers • {botStatus.usersCount} users
                </div>
              )}
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-xs text-cyan-400">24/7 Support</span>
      <motion.div
        className={`w-2 h-2 rounded-full ${statusColor}`}
        animate={isOnline ? { scale: [1, 1.2, 1] } : {}}
        transition={{ duration: 2, repeat: Infinity }}
      />
      <StatusIcon className="w-4 h-4 text-gray-400" />
      <span className="text-sm text-gray-300">{statusText}</span>
      {botStatus && (
        <Badge variant="secondary" className="text-xs">
          {botStatus.guildsCount} servers
        </Badge>
      )}
    </div>
  );
}