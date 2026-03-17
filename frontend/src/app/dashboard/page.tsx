"use client"

import { useEffect, useState } from "react"
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
  Sparkles,
  RefreshCw
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
import {
  fetchTickets,
  fetchDashboardStats,
  fetchChannelStats,
  fetchCategoryStats,
  fetchActivityData,
  getRelativeTime,
  type Ticket as TicketType,
  type DashboardStats,
  type ChannelStats,
  type CategoryStats,
  type ActivityData
} from "@/lib/api"

const channelIcons: Record<string, any> = {
  Email: Mail,
  WhatsApp: Smartphone,
  "Web Form": MessageSquare
}

const channelColors: Record<string, string> = {
  Email: "#06b6d4",
  WhatsApp: "#10b981",
  "Web Form": "#8b5cf6"
}

const categoryColors: Record<string, string> = {
  Technical: "#06b6d4",
  Billing: "#10b981",
  General: "#8b5cf6",
  "Bug Report": "#f59e0b",
  Feedback: "#ec4899"
}

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
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<DashboardStats>({
    totalTickets: 0,
    resolvedTickets: 0,
    pendingTickets: 0,
    avgResponseTime: "0m"
  })
  const [channelStats, setChannelStats] = useState<ChannelStats[]>([])
  const [categoryStats, setCategoryStats] = useState<CategoryStats[]>([])
  const [recentTickets, setRecentTickets] = useState<TicketType[]>([])
  const [activityData, setActivityData] = useState<ActivityData[]>([])

  useEffect(() => {
    loadDashboardData()
    // Refresh data every 30 seconds
    const interval = setInterval(loadDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)

      // Fetch all data in parallel
      const [tickets, dashboardStats, channels, categories, activity] = await Promise.all([
        fetchTickets(50, 0),
        fetchDashboardStats(),
        fetchChannelStats(),
        fetchCategoryStats(),
        fetchActivityData()
      ])

      console.log('Dashboard data loaded:', {
        tickets,
        dashboardStats,
        channels,
        categories,
        activity
      })

      // Set stats
      setStats(dashboardStats)
      setChannelStats(channels)
      setCategoryStats(categories)
      setActivityData(activity)
      setRecentTickets(tickets.slice(0, 10))

    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, any> = {
      OPEN: { variant: "info" as const, label: "Open" },
      IN_PROGRESS: { variant: "warning" as const, label: "In Progress" },
      RESOLVED: { variant: "success" as const, label: "Resolved" },
      PENDING: { variant: "warning" as const, label: "Pending" }
    }
    return statusMap[status.toUpperCase()] || { variant: "info" as const, label: status }
  }

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
            {loading ? 'Loading real-time data...' : 'Real-time data from database'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="success" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30 backdrop-blur-xl text-xs px-3 py-1.5">
            <CheckCircle2 className="mr-1 h-3 w-3" />
            Database Connected
          </Badge>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={loadDashboardData}
            disabled={loading}
            className="h-8 px-2"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <motion.div whileHover={{ scale: 1.02, y: -2 }} whileTap={{ scale: 0.98 }}>
          <Card className="relative overflow-hidden border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-md hover:border-neutral-600/50 transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xs font-medium uppercase tracking-wide text-neutral-400">
                Total Tickets
              </CardTitle>
              <div className="rounded-lg p-2" style={{ backgroundColor: '#06b6d415' }}>
                <Ticket className="h-4 w-4" style={{ color: '#06b6d4' }} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold tracking-tight text-white">
                {loading ? '-' : stats.totalTickets.toLocaleString()}
              </div>
              <div className="mt-2 flex items-center">
                <span className="ml-1 text-xs text-neutral-500">From database</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02, y: -2 }} whileTap={{ scale: 0.98 }}>
          <Card className="relative overflow-hidden border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-md hover:border-neutral-600/50 transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xs font-medium uppercase tracking-wide text-neutral-400">
                Resolved
              </CardTitle>
              <div className="rounded-lg p-2" style={{ backgroundColor: '#10b98115' }}>
                <CheckCircle2 className="h-4 w-4" style={{ color: '#10b981' }} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold tracking-tight text-white">
                {loading ? '-' : stats.resolvedTickets.toLocaleString()}
              </div>
              <div className="mt-2 flex items-center">
                <span className="ml-1 text-xs text-neutral-500">Successfully resolved</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02, y: -2 }} whileTap={{ scale: 0.98 }}>
          <Card className="relative overflow-hidden border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-md hover:border-neutral-600/50 transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xs font-medium uppercase tracking-wide text-neutral-400">
                Pending
              </CardTitle>
              <div className="rounded-lg p-2" style={{ backgroundColor: '#f59e0b15' }}>
                <Clock className="h-4 w-4" style={{ color: '#f59e0b' }} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold tracking-tight text-white">
                {loading ? '-' : stats.pendingTickets.toLocaleString()}
              </div>
              <div className="mt-2 flex items-center">
                <span className="ml-1 text-xs text-neutral-500">Awaiting response</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02, y: -2 }} whileTap={{ scale: 0.98 }}>
          <Card className="relative overflow-hidden border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-md hover:border-neutral-600/50 transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xs font-medium uppercase tracking-wide text-neutral-400">
                Avg Response Time
              </CardTitle>
              <div className="rounded-lg p-2" style={{ backgroundColor: '#8b5cf615' }}>
                <TrendingUp className="h-4 w-4" style={{ color: '#8b5cf6' }} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold tracking-tight text-white">
                {loading ? '-' : stats.avgResponseTime}
              </div>
              <div className="mt-2 flex items-center">
                <span className="ml-1 text-xs text-neutral-500">Average time</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>
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
            {loading || activityData.length === 0 ? (
              <div className="h-[300px] flex items-center justify-center text-neutral-500">
                <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                Loading data...
              </div>
            ) : (
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
            )}
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
            {loading || categoryStats.length === 0 ? (
              <div className="h-[250px] flex items-center justify-center text-neutral-500">
                <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                Loading...
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={categoryStats} layout="vertical">
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
                    {categoryStats.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={categoryColors[entry.name] || "#8b5cf6"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
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
            {loading || channelStats.length === 0 ? (
              <div className="h-[100px] flex items-center justify-center text-neutral-500">
                <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                Loading...
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-3">
                {channelStats.map((channel) => {
                  const Icon = channelIcons[channel.name] || MessageSquare
                  const color = channelColors[channel.name] || "#8b5cf6"
                  return (
                    <motion.div
                      key={channel.name}
                      whileHover={{ scale: 1.02 }}
                      className="flex cursor-pointer items-center gap-4 rounded-xl border border-neutral-700/30 bg-neutral-800/30 p-4 transition-all duration-300 hover:bg-neutral-800/50 hover:border-neutral-600/50 group"
                    >
                      <div
                        className="rounded-lg p-3 transition-transform group-hover:scale-110"
                        style={{ backgroundColor: `${color}15` }}
                      >
                        <Icon className="h-6 w-6" style={{ color: color }} />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-neutral-300">{channel.name}</p>
                        <p className="text-2xl font-bold text-white">{channel.count.toLocaleString()}</p>
                        <p className="text-xs text-neutral-500">
                          {channel.percentage.toFixed(1)}% of total
                        </p>
                      </div>
                      <ArrowUpRight className="h-5 w-5 text-emerald-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </motion.div>
                  )
                })}
              </div>
            )}
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
                <CardDescription className="text-xs text-neutral-400">Latest support requests from database</CardDescription>
              </div>
              <Button variant="ghost" className="text-xs hover:bg-neutral-800" onClick={loadDashboardData}>
                Refresh
                <ArrowUpRight className="ml-1 h-3.5 w-3.5" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="flex items-center gap-4 rounded-xl p-3 animate-pulse">
                    <div className="h-9 w-9 rounded-full bg-neutral-800" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-neutral-800 rounded w-3/4" />
                      <div className="h-3 bg-neutral-800 rounded w-1/2" />
                    </div>
                  </div>
                ))}
              </div>
            ) : recentTickets.length === 0 ? (
              <div className="text-center py-8 text-neutral-500">
                <Ticket className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No tickets found</p>
                <p className="text-xs">Send an email or WhatsApp message to create tickets</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentTickets.map((ticket, i) => {
                  const statusBadge = getStatusBadge(ticket.status)
                  const customerName = ticket.customer_name || ticket.customer_email || `User ${i + 1}`
                  const channel = ticket.channel || 'web_form'
                  
                  return (
                    <motion.div
                      key={ticket.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      whileHover={{ x: 4, backgroundColor: "rgba(38, 38, 38, 0.5)" }}
                      className="flex cursor-pointer items-center gap-4 rounded-xl p-3 transition-all duration-200 hover:bg-neutral-800/50 group"
                    >
                      <Avatar className="h-9 w-9 border border-neutral-700/50">
                        <AvatarFallback className="bg-gradient-to-br from-cyan-600 to-indigo-600 text-xs font-medium text-white">
                          {customerName.substring(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-neutral-200">
                          {ticket.category || 'General Inquiry'} - {customerName}
                        </p>
                        <p className="text-xs text-neutral-500">
                          {channel} • {getRelativeTime(ticket.time)}
                        </p>
                      </div>
                      <Badge
                        variant={statusBadge.variant}
                        className="bg-neutral-800/50 text-xs border-neutral-700/50"
                      >
                        {statusBadge.label}
                      </Badge>
                    </motion.div>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
