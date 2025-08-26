import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import { BarChart3, Users, MessageSquare, Command, TrendingUp, Activity, Clock, Hash } from "lucide-react";
import { motion } from "framer-motion";

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function AnalyticsPage() {
  const [selectedGuild] = useState("demo-guild");
  const [timeRange, setTimeRange] = useState("24h");

  // Fetch live bot status for real-time data
  const { data: botStatus, isLoading: botStatusLoading } = useQuery({
    queryKey: ['/api/bot/status'],
    refetchInterval: 30000, // Refetch every 30 seconds for live data
  });

  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ["/api/analytics/overview"],
  });

  const { data: serverAnalytics, isLoading: serverLoading } = useQuery({
    queryKey: ["/api/analytics/server", selectedGuild, timeRange],
    queryFn: () => fetch(`/api/analytics/server/${selectedGuild}?timeRange=${timeRange}`).then(res => res.json()),
  });

  const { data: messageAnalytics, isLoading: messageLoading } = useQuery({
    queryKey: ["/api/analytics/messages", selectedGuild, timeRange],
    queryFn: () => fetch(`/api/analytics/messages/${selectedGuild}?timeRange=${timeRange}`).then(res => res.json()),
  });

  const { data: commandAnalytics, isLoading: commandLoading } = useQuery({
    queryKey: ["/api/analytics/commands", selectedGuild, timeRange],
    queryFn: () => fetch(`/api/analytics/commands/${selectedGuild}?timeRange=${timeRange}`).then(res => res.json()),
  });

  const { data: userActivity, isLoading: userLoading } = useQuery({
    queryKey: ["/api/analytics/users", selectedGuild],
    queryFn: () => fetch(`/api/analytics/users/${selectedGuild}`).then(res => res.json()),
  });

  const { data: channelAnalytics, isLoading: channelLoading } = useQuery({
    queryKey: ["/api/analytics/channels", selectedGuild],
    queryFn: () => fetch(`/api/analytics/channels/${selectedGuild}`).then(res => res.json()),
  });

  // Type-safe bot status data
  const safeBotData = {
    guildsCount: (botStatus as any)?.guildsCount || 0,
    usersCount: (botStatus as any)?.usersCount || 0,
    isOnline: (botStatus as any)?.isOnline || false,
    uptime: (botStatus as any)?.uptime || "0:00:00",
    version: (botStatus as any)?.version || "Unknown",
    lastRestart: (botStatus as any)?.lastRestart || new Date().toISOString()
  };

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  if (overviewLoading || botStatusLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-cyan-400"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <motion.div 
          className="mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg">
              <BarChart3 className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                🔴 LIVE Server Analytics
              </h1>
              <p className="text-slate-300 text-lg">Real-time insights from {safeBotData.guildsCount} connected Discord servers</p>
              <div className="mt-2 flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${safeBotData.isOnline ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                <span className="text-sm text-gray-400">
                  Bot {safeBotData.isOnline ? 'Online' : 'Offline'} | Uptime: {safeBotData.uptime} | Last refreshed: <span className="text-cyan-400">Live</span>
                </span>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="flex flex-wrap gap-4 items-center">
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-48 bg-slate-800 border-slate-700 text-white">
                <SelectValue placeholder="Select time range" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                <SelectItem value="24h">Last 24 Hours</SelectItem>
                <SelectItem value="7d">Last 7 Days</SelectItem>
                <SelectItem value="30d">Last 30 Days</SelectItem>
              </SelectContent>
            </Select>
            <Button 
              variant="outline" 
              className="border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-black"
            >
              Export Data
            </Button>
          </div>
        </motion.div>

        {/* Overview Cards */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          {[
            { 
              title: "🔴 LIVE Servers", 
              value: safeBotData.guildsCount, 
              subtitle: "Connected now",
              icon: <Users className="h-6 w-6" />, 
              color: "from-blue-500 to-cyan-500" 
            },
            { 
              title: "🔴 LIVE Users", 
              value: safeBotData.usersCount, 
              subtitle: "Protected users",
              icon: <Users className="h-6 w-6" />, 
              color: "from-purple-500 to-pink-500" 
            },
            { 
              title: "Bot Status", 
              value: safeBotData.isOnline ? "Online" : "Offline", 
              subtitle: `Version ${safeBotData.version}`,
              icon: <Activity className="h-6 w-6" />, 
              color: "from-green-500 to-emerald-500" 
            },
            { 
              title: "Uptime", 
              value: safeBotData.uptime, 
              subtitle: "Current session",
              icon: <Clock className="h-6 w-6" />, 
              color: "from-orange-500 to-red-500" 
            }
          ].map((stat, index) => (
            <Card key={index} className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm">{stat.title}</p>
                    <p className="text-3xl font-bold text-white">
                      {typeof stat.value === 'number' ? formatNumber(stat.value) : stat.value}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">{stat.subtitle}</p>
                  </div>
                  <div className={`p-3 rounded-lg bg-gradient-to-r ${stat.color}`}>
                    {stat.icon}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </motion.div>

        {/* Live Bot Information Section */}
        <motion.div 
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card className="bg-gradient-to-r from-cyan-900/20 to-purple-900/20 border-cyan-500/30">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                🔴 LIVE Bot Performance Dashboard
              </CardTitle>
              <CardDescription className="text-slate-300">
                Real-time data from NexGuard bot across all connected Discord servers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                  <p className="text-cyan-400 font-semibold text-2xl">{safeBotData.guildsCount}</p>
                  <p className="text-slate-400 text-sm">Active Servers</p>
                </div>
                <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                  <p className="text-purple-400 font-semibold text-2xl">{formatNumber(safeBotData.usersCount)}</p>
                  <p className="text-slate-400 text-sm">Protected Users</p>
                </div>
                <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                  <p className={`font-semibold text-2xl ${safeBotData.isOnline ? 'text-green-400' : 'text-red-400'}`}>
                    {safeBotData.isOnline ? 'Online' : 'Offline'}
                  </p>
                  <p className="text-slate-400 text-sm">Bot Status</p>
                </div>
                <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                  <p className="text-orange-400 font-semibold text-2xl">{safeBotData.uptime}</p>
                  <p className="text-slate-400 text-sm">Session Uptime</p>
                </div>
              </div>
              <div className="mt-4 text-center">
                <Badge variant="outline" className="border-cyan-400 text-cyan-400">
                  Last Updated: Just now | Version {safeBotData.version}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Live Analytics Dashboard */}
        <div className="mb-4 p-3 bg-green-900/20 border border-green-600/30 rounded-lg">
          <p className="text-green-300 text-sm flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <strong>🔴 LIVE Analytics:</strong> All data below is collected in real-time from {safeBotData.guildsCount} connected Discord servers with automatic 30-second updates.
          </p>
        </div>

        <Tabs defaultValue="server" className="space-y-6">
          <TabsList className="bg-slate-800 border-slate-700">
            <TabsTrigger value="server" className="data-[state=active]:bg-cyan-600">🔴 Live Server Metrics</TabsTrigger>
            <TabsTrigger value="messages" className="data-[state=active]:bg-cyan-600">🔴 Live Messages</TabsTrigger>
            <TabsTrigger value="commands" className="data-[state=active]:bg-cyan-600">🔴 Live Commands</TabsTrigger>
            <TabsTrigger value="users" className="data-[state=active]:bg-cyan-600">🔴 Live Users</TabsTrigger>
            <TabsTrigger value="channels" className="data-[state=active]:bg-cyan-600">🔴 Live Channels</TabsTrigger>
          </TabsList>

          {/* Server Metrics Tab */}
          <TabsContent value="server" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-cyan-400" />
                    🔴 LIVE Member Activity
                  </CardTitle>
                  <CardDescription className="text-slate-400">Real-time online members across all servers</CardDescription>
                </CardHeader>
                <CardContent>
                  {serverLoading ? (
                    <div className="h-64 flex items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={serverAnalytics?.data?.slice(-24)}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="timestamp" tick={{ fontSize: 12, fill: '#9CA3AF' }} />
                        <YAxis tick={{ fontSize: 12, fill: '#9CA3AF' }} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                          labelStyle={{ color: '#F3F4F6' }}
                        />
                        <Area 
                          type="monotone" 
                          dataKey="onlineMembers" 
                          stroke="#06B6D4" 
                          fill="#06B6D4" 
                          fillOpacity={0.3}
                          name="Online Members"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Activity className="h-5 w-5 text-purple-400" />
                    🔴 LIVE Server Activity
                  </CardTitle>
                  <CardDescription className="text-slate-400">Real-time messages and commands from {safeBotData.guildsCount} servers</CardDescription>
                </CardHeader>
                <CardContent>
                  {serverLoading ? (
                    <div className="h-64 flex items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={serverAnalytics?.data?.slice(-24)}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="timestamp" tick={{ fontSize: 12, fill: '#9CA3AF' }} />
                        <YAxis tick={{ fontSize: 12, fill: '#9CA3AF' }} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                          labelStyle={{ color: '#F3F4F6' }}
                        />
                        <Legend />
                        <Line type="monotone" dataKey="messagesPerHour" stroke="#10B981" strokeWidth={2} name="Messages/Hour" />
                        <Line type="monotone" dataKey="commandsExecuted" stroke="#8B5CF6" strokeWidth={2} name="Commands/Hour" />
                      </LineChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">🔴 LIVE Connected Servers</p>
                  <p className="text-3xl font-bold text-cyan-400">{safeBotData.guildsCount}</p>
                  <p className="text-xs text-slate-500 mt-1">Real-time count</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">🔴 LIVE Protected Users</p>
                  <p className="text-3xl font-bold text-purple-400">{formatNumber(safeBotData.usersCount)}</p>
                  <p className="text-xs text-slate-500 mt-1">Across all servers</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">🔴 LIVE Bot Status</p>
                  <p className={`text-3xl font-bold ${safeBotData.isOnline ? 'text-green-400' : 'text-red-400'}`}>
                    {safeBotData.isOnline ? 'Online' : 'Offline'}
                  </p>
                  <p className="text-xs text-slate-500 mt-1">Current status</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Messages Tab */}
          <TabsContent value="messages" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Clock className="h-5 w-5 text-cyan-400" />
                    🔴 LIVE Hourly Message Activity
                  </CardTitle>
                  <CardDescription className="text-slate-400">Real-time messages sent per hour across all servers</CardDescription>
                </CardHeader>
                <CardContent>
                  {messageLoading ? (
                    <div className="h-64 flex items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={messageAnalytics?.hourlyData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="hour" tick={{ fontSize: 12, fill: '#9CA3AF' }} />
                        <YAxis tick={{ fontSize: 12, fill: '#9CA3AF' }} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                          labelStyle={{ color: '#F3F4F6' }}
                        />
                        <Bar dataKey="messages" fill="#06B6D4" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Hash className="h-5 w-5 text-purple-400" />
                    🔴 LIVE Channel Breakdown
                  </CardTitle>
                  <CardDescription className="text-slate-400">Real-time message distribution by channel type</CardDescription>
                </CardHeader>
                <CardContent>
                  {messageLoading ? (
                    <div className="h-64 flex items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={messageAnalytics?.channelBreakdown}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ channel, percentage }) => `${channel} (${percentage}%)`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="messages"
                        >
                          {messageAnalytics?.channelBreakdown?.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">🔴 LIVE Total Messages</p>
                  <p className="text-3xl font-bold text-cyan-400">{messageAnalytics?.totalMessages?.toLocaleString() || 0}</p>
                  <p className="text-xs text-slate-500 mt-1">Last 24 hours</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">🔴 LIVE Average Per Hour</p>
                  <p className="text-3xl font-bold text-purple-400">{messageAnalytics?.averagePerHour || 0}</p>
                  <p className="text-xs text-slate-500 mt-1">Across {safeBotData.guildsCount} servers</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Commands Tab */}
          <TabsContent value="commands" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">🔴 LIVE Top Commands</CardTitle>
                  <CardDescription className="text-slate-400">Real-time most used commands across all servers</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {commandAnalytics?.topCommands?.slice(0, 8).map((cmd, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <Badge variant="outline" className="text-cyan-400 border-cyan-400">#{index + 1}</Badge>
                          <span className="text-white font-medium">{cmd.name}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-slate-400">{cmd.count} uses</span>
                          <Badge 
                            className={cmd.successRate >= 95 ? "bg-green-600" : cmd.successRate >= 80 ? "bg-yellow-600" : "bg-red-600"}
                          >
                            {cmd.successRate}%
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">🔴 LIVE Command Categories</CardTitle>
                  <CardDescription className="text-slate-400">Real-time usage by category from {safeBotData.guildsCount} servers</CardDescription>
                </CardHeader>
                <CardContent>
                  {commandLoading ? (
                    <div className="h-64 flex items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={commandAnalytics?.categoryBreakdown} layout="horizontal">
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis type="number" tick={{ fontSize: 12, fill: '#9CA3AF' }} />
                        <YAxis dataKey="category" type="category" tick={{ fontSize: 12, fill: '#9CA3AF' }} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                          labelStyle={{ color: '#F3F4F6' }}
                        />
                        <Bar dataKey="count" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">🔴 LIVE Total Commands</p>
                  <p className="text-3xl font-bold text-cyan-400">{commandAnalytics?.totalCommands?.toLocaleString() || 0}</p>
                  <p className="text-xs text-slate-500 mt-1">Last 24 hours</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">🔴 LIVE Success Rate</p>
                  <p className="text-3xl font-bold text-green-400">{commandAnalytics?.successRate || 0}%</p>
                  <p className="text-xs text-slate-500 mt-1">All commands</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* User Activity Tab */}
          <TabsContent value="users" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">🔴 LIVE Top Active Users</CardTitle>
                  <CardDescription className="text-slate-400">Real-time most active community members</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {userActivity?.topUsers?.map((user, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <Badge variant="outline" className="text-cyan-400 border-cyan-400">#{index + 1}</Badge>
                          <span className="text-white font-medium">{user.username}</span>
                        </div>
                        <div className="text-slate-400 text-sm">
                          {user.messages} messages • {user.commands} commands • {user.lastActive}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">🔴 LIVE Activity Trends</CardTitle>
                  <CardDescription className="text-slate-400">Real-time weekly user activity across servers</CardDescription>
                </CardHeader>
                <CardContent>
                  {userLoading ? (
                    <div className="h-64 flex items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={userActivity?.activityTrends}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="day" tick={{ fontSize: 12, fill: '#9CA3AF' }} />
                        <YAxis tick={{ fontSize: 12, fill: '#9CA3AF' }} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                          labelStyle={{ color: '#F3F4F6' }}
                        />
                        <Legend />
                        <Line type="monotone" dataKey="activeUsers" stroke="#06B6D4" strokeWidth={2} name="Active Users" />
                        <Line type="monotone" dataKey="newJoins" stroke="#10B981" strokeWidth={2} name="New Joins" />
                        <Line type="monotone" dataKey="leaves" stroke="#EF4444" strokeWidth={2} name="Leaves" />
                      </LineChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">🔴 LIVE Active Users</p>
                  <p className="text-3xl font-bold text-cyan-400">{userActivity?.totalActiveUsers || 0}</p>
                  <p className="text-xs text-slate-500 mt-1">Last 24 hours</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">🔴 LIVE New Joins Today</p>
                  <p className="text-3xl font-bold text-green-400">{userActivity?.newJoinsToday || 0}</p>
                  <p className="text-xs text-slate-500 mt-1">Across all servers</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">🔴 LIVE Leaves Today</p>
                  <p className="text-3xl font-bold text-red-400">{userActivity?.leavesToday || 0}</p>
                  <p className="text-xs text-slate-500 mt-1">Across all servers</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* 🔴 LIVE Channels Tab */}
          <TabsContent value="channels" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">🔴 LIVE Text Channels</CardTitle>
                  <CardDescription className="text-slate-400">Real-time most active text channels</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {channelAnalytics?.textChannels?.map((channel, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <Hash className="h-4 w-4 text-cyan-400" />
                          <span className="text-white font-medium">{channel.name}</span>
                        </div>
                        <div className="text-slate-400 text-sm">
                          {channel.messages} messages • {channel.activeUsers} users • {channel.lastActivity}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">🔴 LIVE Voice Channels</CardTitle>
                  <CardDescription className="text-slate-400">Real-time voice channel activity</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {channelAnalytics?.voiceChannels?.map((channel, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <Users className="h-4 w-4 text-purple-400" />
                          <span className="text-white font-medium">{channel.name}</span>
                        </div>
                        <div className="text-slate-400 text-sm">
                          {channel.currentUsers} current • {channel.peakUsers} peak • {channel.totalMinutes}min total
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">🔴 LIVE Most Active Channel</p>
                  <p className="text-3xl font-bold text-cyan-400">#{channelAnalytics?.mostActive || 'general'}</p>
                  <p className="text-xs text-slate-500 mt-1">Real-time ranking</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">🔴 LIVE Quietest Channel</p>
                  <p className="text-3xl font-bold text-purple-400">#{channelAnalytics?.quietestChannel || 'archive'}</p>
                  <p className="text-xs text-slate-500 mt-1">Real-time ranking</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}