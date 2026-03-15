"use client"

import { motion } from "framer-motion"
import {
  Ticket,
  CheckCircle2,
  Clock,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  MessageSquare,
  Mail,
  Smartphone,
  Zap,
  Sparkles
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell
} from "recharts"

const statsData = [
  {
    title: "Total Tickets",
    value: "2,847",
    change: "+12.5%",
    trend: "up",
    icon: Ticket,
    color: "#06b6d4"
  },
  {
    title: "Resolved",
    value: "2,456",
    change: "+8.2%",
    trend: "up",
    icon: CheckCircle2,
    color: "#10b981"
  },
  {
    title: "Pending",
    value: "312",
    change: "-3.1%",
    trend: "down",
    icon: Clock,
    color: "#f59e0b"
  },
  {
    title: "Avg Response Time",
    value: "2.4m",
    change: "-18.3%",
    trend: "down",
    icon: TrendingUp,
    color: "#8b5cf6"
  }
]

const ticketsByChannel = [
  { name: "Email", count: 1247, icon: Mail, color: "#06b6d4" },
  { name: "WhatsApp", count: 892, icon: Smartphone, color: "#10b981" },
  { name: "Web Form", count: 708, icon: MessageSquare, color: "#8b5cf6" }
]

const activityData = [
  { time: "00:00", tickets: 45, resolved: 38 },
  { time: "04:00", tickets: 32, resolved: 28 },
  { time: "08:00", tickets: 128, resolved: 115 },
  { time: "12:00", tickets: 256, resolved: 234 },
  { time: "16:00", tickets: 198, resolved: 187 },
  { time: "20:00", tickets: 89, resolved: 82 },
  { time: "23:59", tickets: 52, resolved: 48 }
]

const categoryData = [
  { name: "Technical", value: 45, color: "#06b6d4" },
  { name: "Billing", value: 28, color: "#10b981" },
  { name: "General", value: 15, color: "#8b5cf6" },
  { name: "Bug Report", value: 8, color: "#f59e0b" },
  { name: "Feedback", value: 4, color: "#ec4899" }
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5
    }
  }
}

export default function DashboardPage() {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-4"
    >
      {/* Page Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white lg:text-3xl">
            Dashboard
          </h1>
          <p className="mt-0.5 text-xs text-neutral-400 lg:text-sm">
            Welcome back! Here&apos;s what&apos;s happening today.
          </p>
        </div>
        <Badge variant="success" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30 backdrop-blur-xl text-xs px-3 py-1.5">
          <CheckCircle2 className="mr-1 h-3 w-3" />
          All Systems Operational
        </Badge>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsData.map((stat) => (
          <motion.div
            key={stat.title}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <Card className="relative overflow-hidden border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-md hover:border-neutral-600/50 transition-all duration-300">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-xs font-medium uppercase tracking-wide text-neutral-400">
                  {stat.title}
                </CardTitle>
                <div
                  className="rounded-lg p-2"
                  style={{ backgroundColor: `${stat.color}15` }}
                >
                  <stat.icon className="h-4 w-4" style={{ color: stat.color }} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold tracking-tight text-white">{stat.value}</div>
                <div className="mt-2 flex items-center">
                  {stat.trend === "up" ? (
                    <ArrowUpRight className="h-3.5 w-3.5 text-emerald-400" />
                  ) : (
                    <ArrowDownRight className="h-3.5 w-3.5 text-emerald-400" />
                  )}
                  <span className="ml-1 text-xs font-medium text-emerald-400">{stat.change}</span>
                  <span className="ml-1 text-xs text-neutral-500">vs last month</span>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* Charts Row */}
      <motion.div variants={itemVariants} className="grid gap-4 lg:grid-cols-3">
        {/* Activity Chart */}
        <Card className="lg:col-span-2 border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-md">
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-cyan-500/10 p-2">
                <Zap className="h-4 w-4 text-cyan-400" />
              </div>
              <div>
                <CardTitle className="text-base font-semibold text-white">Ticket Activity (24h)</CardTitle>
                <CardDescription className="text-xs text-neutral-400">Real-time ticket inflow and resolution</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={activityData}>
                <defs>
                  <linearGradient id="colorTickets" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#262626" opacity={0.5} />
                <XAxis dataKey="time" stroke="#525252" fontSize={11} />
                <YAxis stroke="#525252" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(23, 23, 23, 0.95)',
                    border: '1px solid rgba(63, 63, 63, 0.5)',
                    borderRadius: '8px',
                    backdropFilter: 'blur(12px)'
                  }}
                  labelStyle={{ color: '#a3a3a3' }}
                />
                <Area
                  type="monotone"
                  dataKey="tickets"
                  stroke="#06b6d4"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorTickets)"
                  name="Tickets"
                />
                <Area
                  type="monotone"
                  dataKey="resolved"
                  stroke="#10b981"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorResolved)"
                  name="Resolved"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Category Distribution */}
        <Card className="border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-md">
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-violet-500/10 p-2">
                <Sparkles className="h-4 w-4 text-violet-400" />
              </div>
              <div>
                <CardTitle className="text-base font-semibold text-white">Categories</CardTitle>
                <CardDescription className="text-xs text-neutral-400">Distribution</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={categoryData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#262626" opacity={0.5} />
                <XAxis type="number" stroke="#525252" fontSize={11} hide />
                <YAxis dataKey="name" type="category" stroke="#737373" fontSize={10} width={90} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(23, 23, 23, 0.95)',
                    border: '1px solid rgba(63, 63, 63, 0.5)',
                    borderRadius: '8px',
                    backdropFilter: 'blur(12px)'
                  }}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </motion.div>

      {/* Tickets by Channel */}
      <motion.div variants={itemVariants}>
        <Card className="border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-md">
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-indigo-500/10 p-2">
                <MessageSquare className="h-4 w-4 text-indigo-400" />
              </div>
              <div>
                <CardTitle className="text-base font-semibold text-white">Tickets by Channel</CardTitle>
                <CardDescription className="text-xs text-neutral-400">Support requests across all communication channels</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              {ticketsByChannel.map((channel) => (
                <motion.div
                  key={channel.name}
                  whileHover={{ scale: 1.02 }}
                  className="flex cursor-pointer items-center gap-4 rounded-xl border border-neutral-700/30 bg-neutral-800/30 p-4 transition-all duration-300 hover:bg-neutral-800/50 hover:border-neutral-600/50 group"
                >
                  <div
                    className="rounded-lg p-3 transition-transform group-hover:scale-110"
                    style={{ backgroundColor: `${channel.color}15` }}
                  >
                    <channel.icon className="h-6 w-6" style={{ color: channel.color }} />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-neutral-300">{channel.name}</p>
                    <p className="text-2xl font-bold text-white">{channel.count.toLocaleString()}</p>
                    <p className="text-xs text-neutral-500">
                      {((channel.count / 2847) * 100).toFixed(1)}% of total
                    </p>
                  </div>
                  <ArrowUpRight className="h-5 w-5 text-emerald-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recent Activity */}
      <motion.div variants={itemVariants}>
        <Card className="border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-md">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base font-semibold text-white">Recent Tickets</CardTitle>
                <CardDescription className="text-xs text-neutral-400">Latest support requests</CardDescription>
              </div>
              <Button variant="ghost" className="text-xs hover:bg-neutral-800">
                View All
                <ArrowUpRight className="ml-1 h-3.5 w-3.5" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.08 }}
                  whileHover={{ x: 4, backgroundColor: "rgba(38, 38, 38, 0.5)" }}
                  className="flex cursor-pointer items-center gap-4 rounded-xl p-3 transition-all duration-200 hover:bg-neutral-800/50 group"
                >
                  <Avatar className="h-9 w-9 border border-neutral-700/50">
                    <AvatarFallback className="bg-gradient-to-br from-cyan-600 to-indigo-600 text-xs font-medium text-white">
                      U{i}
                    </AvatarFallback>
                  </Avatar>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-neutral-200">
                      Issue with {["file upload", "payment processing", "account access", "API integration", "mobile app"][i - 1]}
                    </p>
                    <p className="text-xs text-neutral-500">
                      User {i} • {["Email", "WhatsApp", "Web Form", "Email", "WhatsApp"][i - 1]} • {i * 15}m ago
                    </p>
                  </div>
                  <Badge
                    variant={["info", "warning", "success", "info", "warning"][i - 1] as any}
                    className="bg-neutral-800/50 text-xs border-neutral-700/50"
                  >
                    {["Pending", "In Progress", "Resolved", "Pending", "In Progress"][i - 1]}
                  </Badge>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
