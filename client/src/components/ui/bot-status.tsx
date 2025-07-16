import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Activity, Users, Server, Command, Clock } from "lucide-react";

interface BotStatus {
  online: boolean;
  guilds: number;
  users: number;
  uptime: number;
  commands: number;
  lastHeartbeat: string;
  version: string;
}

export function BotStatus() {
  const [realTimeStatus, setRealTimeStatus] = useState<BotStatus | null>(null);

  const { data: status, refetch } = useQuery<BotStatus>({
    queryKey: ["/api/bot/status"],
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Temporarily disable WebSocket until proper implementation
  // useEffect(() => {
  //   // WebSocket connection for real-time updates will be implemented later
  // }, []);

  const currentStatus = realTimeStatus || status;

  if (!currentStatus) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Bot Status
          </CardTitle>
          <CardDescription>Loading bot status...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const formatUptime = (uptime: number) => {
    if (!uptime) return "0m";
    const seconds = Math.floor((Date.now() - uptime) / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    return `${minutes}m`;
  };

  const getStatusColor = (online: boolean) => {
    return online ? "bg-green-500" : "bg-red-500";
  };

  const getStatusText = (online: boolean) => {
    return online ? "Online" : "Offline";
  };

  const lastSeen = new Date(currentStatus.lastHeartbeat);
  const timeSinceLastSeen = Math.floor((Date.now() - lastSeen.getTime()) / 1000);

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          NexGuard Bot Status
        </CardTitle>
        <CardDescription>
          <div className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${getStatusColor(currentStatus.online)}`} />
            {getStatusText(currentStatus.online)}
            <span className="text-xs text-muted-foreground">
              v{currentStatus.version}
            </span>
          </div>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <Server className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">{currentStatus.guilds}</p>
              <p className="text-xs text-muted-foreground">Servers</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">{currentStatus.users}</p>
              <p className="text-xs text-muted-foreground">Users</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Command className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">{currentStatus.commands}</p>
              <p className="text-xs text-muted-foreground">Commands</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">{formatUptime(currentStatus.uptime)}</p>
              <p className="text-xs text-muted-foreground">Uptime</p>
            </div>
          </div>
        </div>
        
        <Separator />
        
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Last seen:</span>
          <Badge variant="outline" className="text-xs">
            {timeSinceLastSeen < 60 ? `${timeSinceLastSeen}s ago` : `${Math.floor(timeSinceLastSeen / 60)}m ago`}
          </Badge>
        </div>
        
        {!currentStatus.online && (
          <div className="p-3 bg-red-50 dark:bg-red-900/10 rounded-lg border border-red-200 dark:border-red-800">
            <p className="text-sm text-red-700 dark:text-red-400">
              Bot is currently offline. Please check the bot logs or contact support.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function BotStatusBadge() {
  const { data: status, isLoading } = useQuery<BotStatus>({
    queryKey: ["/api/bot/status"],
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <Badge variant="outline" className="gap-2 text-white border-gray-400 bg-gray-800/50 px-3 py-1">
        <div className="h-2 w-2 rounded-full bg-gray-400 animate-pulse" />
        <span className="text-sm font-medium">Loading...</span>
      </Badge>
    );
  }

  if (!status) {
    return (
      <Badge variant="outline" className="gap-2 text-white border-red-400 bg-red-900/30 px-3 py-1">
        <div className="h-2 w-2 rounded-full bg-red-500" />
        <span className="text-sm font-medium">Offline</span>
      </Badge>
    );
  }

  return (
    <Badge variant="outline" className={`gap-2 text-white px-3 py-1 ${
      status.online 
        ? 'border-green-400 bg-green-900/30' 
        : 'border-red-400 bg-red-900/30'
    }`}>
      <div className={`h-2 w-2 rounded-full ${getStatusColor(status.online)}`} />
      <span className="text-sm font-medium">{getStatusText(status.online)}</span>
    </Badge>
  );
}

function getStatusColor(online: boolean) {
  return online ? "bg-green-500" : "bg-red-500";
}

function getStatusText(online: boolean) {
  return online ? "Online" : "Offline";
}