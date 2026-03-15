"use client"

import { motion } from "framer-motion"
import {
  TrendingUp,
  TrendingDown,
  Users,
  MessageSquare,
  Clock,
  Target,
  ArrowUpRight,
  Download,
  Sparkles,
  Zap,
  BarChart3,
  PieChart as PieChartIcon
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts"

const performanceData = [
  { date: "Mon", tickets: 245, resolved: 232, sla: 98.5 },
  { date: "Tue", tickets: 289, resolved: 275, sla: 97.8 },
  { date: "Wed", tickets: 312, resolved: 298, sla: 98.2 },
  { date: "Thu", tickets: 278, resolved: 265, sla: 97.5 },
  { date: "Fri", tickets: 345, resolved: 328, sla: 98.9 },
  { date: "Sat", tickets: 156, resolved: 148, sla: 99.1 },
  { date: "Sun", tickets: 134, resolved: 128, sla: 98.7 }
]

const channelPerformance = [
  { channel: "Email", volume: 1247, avgResponse: "2.4m", resolution: "1.2h", satisfaction: 94 },
  { channel: "WhatsApp", volume: 892, avgResponse: "1.8m", resolution: "0.8h", satisfaction: 96 },
  { channel: "Web Form", volume: 708, avgResponse: "3.2m", resolution: "1.5h", satisfaction: 92 }
]

const sentimentData = [
  { name: "Positive", value: 58, color: "#22c55e" },
  { name: "Neutral", value: 28, color: "#f59e0b" },
  { name: "Negative", value: 10, color: "#ef4444" },
  { name: "Critical", value: 4, color: "#7c3aed" }
]

const categoryTrends = [
  { category: "Technical", current: 847, previous: 756, change: 12.0 },
  { category: "Billing", current: 523, previous: 489, change: 6.9 },
  { category: "General", current: 312, previous: 345, change: -9.6 },
  { category: "Bug Report", current: 189, previous: 234, change: -19.2 },
  { category: "Feedback", current: 98, previous: 87, change: 12.6 }
]

const COLORS = ["#22c55e", "#f59e0b", "#ef4444", "#7c3aed"]

const kpis = [
  {
    title: "First Response Time",
    value: "2.4 min",
    change: "-18.3%",
    trend: "down",
    icon: Clock,
    gradient: "from-blue-500 to-cyan-500"
  },
  {
    title: "Resolution Rate",
    value: "94.8%",
    change: "+3.2%",
    trend: "up",
    icon: Target,
    gradient: "from-green-500 to-emerald-500"
  },
  {
    title: "Customer Satisfaction",
    value: "94.2%",
    change: "+1.8%",
    trend: "up",
    icon: Users,
    gradient: "from-purple-500 to-pink-500"
  },
  {
    title: "SLA Compliance",
    value: "98.4%",
    change: "+0.6%",
    trend: "up",
    icon: MessageSquare,
    gradient: "from-amber-500 to-orange-500"
  }
]

export default function AnalyticsPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text">
            Analytics
          </h1>
          <p className="text-muted-foreground mt-1">
            Comprehensive insights into support performance
          </p>
        </div>
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Button variant="outline" className="border-white/10 hover:bg-white/5">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </motion.div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {kpis.map((kpi, index) => (
          <motion.div
            key={kpi.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.03, y: -4 }}
          >
            <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl card-hover">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {kpi.title}
                </CardTitle>
                <motion.div 
                  className={`p-2 rounded-lg bg-gradient-to-br ${kpi.gradient} shadow-lg`}
                  whileHover={{ scale: 1.1, rotate: 5 }}
                >
                  <kpi.icon className="h-4 w-4 text-white" />
                </motion.div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{kpi.value}</div>
                <div className="flex items-center mt-2">
                  {kpi.trend === "up" ? (
                    <TrendingUp className="h-4 w-4 text-emerald-500 mr-1" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-emerald-500 mr-1" />
                  )}
                  <span className="text-xs text-emerald-500 font-medium">{kpi.change}</span>
                  <span className="text-xs text-muted-foreground ml-1">vs last week</span>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Charts Row 1 */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Ticket Volume Trend */}
        <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl">
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500">
                <BarChart3 className="h-4 w-4 text-white" />
              </div>
              <div>
                <CardTitle>Ticket Volume & Resolution</CardTitle>
                <CardDescription>7-day trend comparison</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={performanceData}>
                <defs>
                  <linearGradient id="colorTickets" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="date" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(10, 15, 30, 0.9)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '12px',
                    backdropFilter: 'blur(10px)'
                  }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="tickets"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorTickets)"
                  name="Tickets Received"
                />
                <Area
                  type="monotone"
                  dataKey="resolved"
                  stroke="#22c55e"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorResolved)"
                  name="Tickets Resolved"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Sentiment Distribution */}
        <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl">
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500">
                <PieChartIcon className="h-4 w-4 text-white" />
              </div>
              <div>
                <CardTitle>Customer Sentiment</CardTitle>
                <CardDescription>Distribution of ticket sentiments</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-6">
              <ResponsiveContainer width="50%" height={250}>
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'rgba(10, 15, 30, 0.9)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '12px',
                      backdropFilter: 'blur(10px)'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-3 flex-1">
                {sentimentData.map((item) => (
                  <motion.div 
                    key={item.name} 
                    className="flex items-center justify-between"
                    whileHover={{ x: 4 }}
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full shadow-lg"
                        style={{ backgroundColor: item.color, boxShadow: `0 0 10px ${item.color}50` }}
                      />
                      <span className="text-sm font-medium">{item.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 rounded-full bg-white/10 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${item.value}%` }}
                          transition={{ duration: 1, delay: 0.5 }}
                          className="h-full rounded-full"
                          style={{ backgroundColor: item.color }}
                        />
                      </div>
                      <span className="text-sm font-medium w-8 text-right">{item.value}%</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Channel Performance */}
      <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500">
                <Zap className="h-4 w-4 text-white" />
              </div>
              <div>
                <CardTitle>Channel Performance</CardTitle>
                <CardDescription>Metrics by communication channel</CardDescription>
              </div>
            </div>
            <Badge variant="success" className="border-emerald-500/30 bg-emerald-500/20 backdrop-blur-xl">
              <TrendingUp className="h-3 w-3 mr-1" />
              All channels performing well
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Channel</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Volume</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Avg Response</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Resolution Time</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Satisfaction</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Trend</th>
                </tr>
              </thead>
              <tbody>
                {channelPerformance.map((channel) => (
                  <motion.tr 
                    key={channel.channel} 
                    className="border-b border-white/10 hover:bg-white/[0.03] transition-colors"
                    whileHover={{ scale: 1.01 }}
                  >
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
                          <MessageSquare className="h-4 w-4 text-blue-400" />
                        </div>
                        <span className="font-medium">{channel.channel}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-sm">{channel.volume.toLocaleString()}</td>
                    <td className="py-4 px-4 text-sm">
                      <Badge variant="success" className="border-emerald-500/30 bg-emerald-500/20">{channel.avgResponse}</Badge>
                    </td>
                    <td className="py-4 px-4 text-sm">{channel.resolution}</td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 rounded-full bg-white/10 overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${channel.satisfaction}%` }}
                            transition={{ duration: 1 }}
                            className="h-full rounded-full bg-emerald-500"
                          />
                        </div>
                        <span className="text-sm font-medium">{channel.satisfaction}%</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <ArrowUpRight className="h-4 w-4 text-emerald-500" />
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Category Trends */}
      <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl">
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-gradient-to-br from-amber-500 to-orange-500">
              <TrendingUp className="h-4 w-4 text-white" />
            </div>
            <div>
              <CardTitle>Category Trends</CardTitle>
              <CardDescription>Week-over-week comparison by ticket category</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {categoryTrends.map((category) => (
              <motion.div 
                key={category.category} 
                className="flex items-center gap-4"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                whileHover={{ x: 4 }}
              >
                <div className="w-32 text-sm font-medium">{category.category}</div>
                <div className="flex-1 flex items-center gap-4">
                  <div className="flex-1 h-8 bg-white/5 rounded-md overflow-hidden relative">
                    <div
                      className="absolute top-0 left-0 h-full bg-blue-500/30"
                      style={{ width: `${(category.previous / 1000) * 100}%` }}
                    />
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(category.current / 1000) * 100}%` }}
                      transition={{ duration: 1 }}
                      className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-500 to-indigo-500"
                    />
                  </div>
                  <div className="w-24 text-right">
                    <div className="text-sm font-medium">{category.current}</div>
                    <div className="text-xs text-muted-foreground">Prev: {category.previous}</div>
                  </div>
                  <div className={`w-16 text-right ${
                    category.change > 0 ? "text-red-500" : "text-emerald-500"
                  }`}>
                    <div className="text-sm font-medium flex items-center justify-end gap-1">
                      {category.change > 0 ? (
                        <ArrowUpRight className="h-3 w-3" />
                      ) : (
                        <TrendingDown className="h-3 w-3" />
                      )}
                      {Math.abs(category.change)}%
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
