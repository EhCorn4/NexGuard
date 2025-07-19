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
import nexguardIcon from "@assets/file_0000000003fc61f58b4fd114190f81c9_1751936993313.png";

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function AnalyticsPage() {
  const [selectedGuild] = useState("demo-guild");
  const [timeRange, setTimeRange] = useState("24h");

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

  if (overviewLoading) {
    return (
      <div className="min-h-screen hero-gradient circuit-pattern pt-24 relative overflow-hidden">
        <div 
          className="absolute inset-0 bg-center opacity-20" 
          style={{ 
            backgroundImage: `url(${nexguardIcon})`,
            backgroundSize: '400px 400px',
            backgroundRepeat: 'no-repeat'
          }}
        ></div>
        <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
        <div className="container mx-auto px-4 py-20 relative z-10">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-cyan-400"></div>
          </div>
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
          backgroundSize: '400px 400px',
          backgroundRepeat: 'no-repeat'
        }}
      ></div>
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      <div className="container mx-auto px-4 py-20 relative z-10">
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
                Server Analytics
              </h1>
              <p className="text-slate-300 text-lg">Real-time insights into your Discord community</p>
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
            { title: "Total Servers", value: overview?.totalServers, icon: <Users className="h-6 w-6" />, color: "from-blue-500 to-cyan-500" },
            { title: "Total Users", value: overview?.totalUsers, icon: <Users className="h-6 w-6" />, color: "from-purple-500 to-pink-500" },
            { title: "Messages Today", value: overview?.totalMessages, icon: <MessageSquare className="h-6 w-6" />, color: "from-green-500 to-emerald-500" },
            { title: "Commands Used", value: overview?.totalCommands, icon: <Command className="h-6 w-6" />, color: "from-orange-500 to-red-500" }
          ].map((stat, index) => (
            <Card key={index} className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm">{stat.title}</p>
                    <p className="text-3xl font-bold text-white">{stat.value?.toLocaleString()}</p>
                  </div>
                  <div className={`p-3 rounded-lg bg-gradient-to-r ${stat.color}`}>
                    {stat.icon}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </motion.div>

        {/* Main Analytics Dashboard */}
        <Tabs defaultValue="server" className="space-y-6">
          <TabsList className="bg-slate-800 border-slate-700">
            <TabsTrigger value="server" className="data-[state=active]:bg-cyan-600">Server Metrics</TabsTrigger>
            <TabsTrigger value="messages" className="data-[state=active]:bg-cyan-600">Messages</TabsTrigger>
            <TabsTrigger value="commands" className="data-[state=active]:bg-cyan-600">Commands</TabsTrigger>
            <TabsTrigger value="users" className="data-[state=active]:bg-cyan-600">User Activity</TabsTrigger>
            <TabsTrigger value="channels" className="data-[state=active]:bg-cyan-600">Channels</TabsTrigger>
          </TabsList>

          {/* Server Metrics Tab */}
          <TabsContent value="server" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-cyan-400" />
                    Member Activity
                  </CardTitle>
                  <CardDescription className="text-slate-400">Online members over time</CardDescription>
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
                    Server Activity
                  </CardTitle>
                  <CardDescription className="text-slate-400">Messages and commands per hour</CardDescription>
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
                  <p className="text-slate-400 text-sm">Total Members</p>
                  <p className="text-3xl font-bold text-cyan-400">{serverAnalytics?.summary?.totalMembers}</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">Peak Online</p>
                  <p className="text-3xl font-bold text-purple-400">{serverAnalytics?.summary?.peakOnline}</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">Avg Messages/Hour</p>
                  <p className="text-3xl font-bold text-green-400">{serverAnalytics?.summary?.avgMessages}</p>
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
                    Hourly Message Activity
                  </CardTitle>
                  <CardDescription className="text-slate-400">Messages sent per hour</CardDescription>
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
                    Channel Breakdown
                  </CardTitle>
                  <CardDescription className="text-slate-400">Messages by channel</CardDescription>
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
                  <p className="text-slate-400 text-sm">Total Messages</p>
                  <p className="text-3xl font-bold text-cyan-400">{messageAnalytics?.totalMessages?.toLocaleString()}</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">Average Per Hour</p>
                  <p className="text-3xl font-bold text-purple-400">{messageAnalytics?.averagePerHour}</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Commands Tab */}
          <TabsContent value="commands" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Top Commands</CardTitle>
                  <CardDescription className="text-slate-400">Most used commands</CardDescription>
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
                  <CardTitle className="text-white">Command Categories</CardTitle>
                  <CardDescription className="text-slate-400">Usage by category</CardDescription>
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
                  <p className="text-slate-400 text-sm">Total Commands</p>
                  <p className="text-3xl font-bold text-cyan-400">{commandAnalytics?.totalCommands?.toLocaleString()}</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">Success Rate</p>
                  <p className="text-3xl font-bold text-green-400">{commandAnalytics?.successRate}%</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* User Activity Tab */}
          <TabsContent value="users" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Top Active Users</CardTitle>
                  <CardDescription className="text-slate-400">Most active community members</CardDescription>
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
                  <CardTitle className="text-white">Activity Trends</CardTitle>
                  <CardDescription className="text-slate-400">Weekly user activity</CardDescription>
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
                  <p className="text-slate-400 text-sm">Active Users</p>
                  <p className="text-3xl font-bold text-cyan-400">{userActivity?.totalActiveUsers}</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">New Joins Today</p>
                  <p className="text-3xl font-bold text-green-400">{userActivity?.newJoinsToday}</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">Leaves Today</p>
                  <p className="text-3xl font-bold text-red-400">{userActivity?.leavesToday}</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Channels Tab */}
          <TabsContent value="channels" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Text Channels</CardTitle>
                  <CardDescription className="text-slate-400">Most active text channels</CardDescription>
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
                  <CardTitle className="text-white">Voice Channels</CardTitle>
                  <CardDescription className="text-slate-400">Voice channel activity</CardDescription>
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
                  <p className="text-slate-400 text-sm">Most Active Channel</p>
                  <p className="text-3xl font-bold text-cyan-400">#{channelAnalytics?.mostActive}</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-6 text-center">
                  <p className="text-slate-400 text-sm">Quietest Channel</p>
                  <p className="text-3xl font-bold text-purple-400">#{channelAnalytics?.quietestChannel}</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}