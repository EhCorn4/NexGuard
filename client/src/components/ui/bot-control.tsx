import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, Play, Square, RotateCcw } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiRequest } from '@/lib/queryClient';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface BotStatus {
  online: boolean;
  guilds: number;
  users: number;
  uptime: string;
  commands: number;
  lastHeartbeat: string;
  version: string;
  lastUpdated: string;
}

export function BotControl() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const { data: status, isLoading } = useQuery<BotStatus>({
    queryKey: ['/api/bot/status'],
    refetchInterval: 5000, // More frequent updates for control panel
  });

  const startMutation = useMutation({
    mutationFn: () => apiRequest('/api/bot/start', { method: 'POST' }),
    onSuccess: () => {
      toast({
        title: "Bot Started",
        description: "The Discord bot has been started successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/bot/status'] });
    },
    onError: () => {
      toast({
        title: "Start Failed",
        description: "Failed to start the Discord bot. Please check the logs.",
        variant: "destructive",
      });
    },
  });

  const stopMutation = useMutation({
    mutationFn: () => apiRequest('/api/bot/stop', { method: 'POST' }),
    onSuccess: () => {
      toast({
        title: "Bot Stopped",
        description: "The Discord bot has been stopped successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/bot/status'] });
    },
    onError: () => {
      toast({
        title: "Stop Failed",
        description: "Failed to stop the Discord bot. Please check the logs.",
        variant: "destructive",
      });
    },
  });

  const restartMutation = useMutation({
    mutationFn: () => apiRequest('/api/bot/restart', { method: 'POST' }),
    onSuccess: () => {
      toast({
        title: "Bot Restarted",
        description: "The Discord bot has been restarted successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/bot/status'] });
    },
    onError: () => {
      toast({
        title: "Restart Failed",
        description: "Failed to restart the Discord bot. Please check the logs.",
        variant: "destructive",
      });
    },
  });

  const isLoading_ = isLoading || startMutation.isPending || stopMutation.isPending || restartMutation.isPending;

  return (
    <Card className="bg-gradient-to-br from-gray-900 to-gray-800 border-gray-700">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <AlertCircle className="h-5 w-5" />
          Bot Control Panel
        </CardTitle>
        <CardDescription className="text-gray-400">
          Manage the NexGuard Discord bot instance
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Status Display */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`h-3 w-3 rounded-full ${status?.online ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-white font-medium">
              {status?.online ? 'Online' : 'Offline'}
            </span>
          </div>
          <Badge variant="outline" className="text-white border-gray-600">
            v{status?.version || '2.3.2'}
          </Badge>
        </div>

        {/* Bot Statistics */}
        {status?.online && (
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-2xl font-bold text-cyan-400">{status.guilds}</div>
              <div className="text-sm text-gray-400">Servers</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-2xl font-bold text-purple-400">{status.users.toLocaleString()}</div>
              <div className="text-sm text-gray-400">Users</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-2xl font-bold text-green-400">{status.commands}</div>
              <div className="text-sm text-gray-400">Commands</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-2xl font-bold text-yellow-400">{status.uptime}</div>
              <div className="text-sm text-gray-400">Uptime</div>
            </div>
          </div>
        )}

        {/* Control Buttons */}
        <div className="flex gap-2">
          <Button
            onClick={() => startMutation.mutate()}
            disabled={isLoading_ || status?.online}
            className="flex-1 bg-green-600 hover:bg-green-700"
          >
            <Play className="h-4 w-4 mr-2" />
            Start Bot
          </Button>
          <Button
            onClick={() => stopMutation.mutate()}
            disabled={isLoading_ || !status?.online}
            variant="destructive"
            className="flex-1"
          >
            <Square className="h-4 w-4 mr-2" />
            Stop Bot
          </Button>
          <Button
            onClick={() => restartMutation.mutate()}
            disabled={isLoading_ || !status?.online}
            variant="outline"
            className="flex-1 border-gray-600 text-white hover:bg-gray-700"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Restart
          </Button>
        </div>

        {/* Last Updated */}
        {status?.lastUpdated && (
          <div className="text-xs text-gray-500 text-center">
            Last updated: {new Date(status.lastUpdated).toLocaleString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
}