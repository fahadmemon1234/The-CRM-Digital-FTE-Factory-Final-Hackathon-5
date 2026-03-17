"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import {
  Search,
  Filter,
  Mail,
  Smartphone,
  MessageSquare,
  Clock,
  CheckCircle2,
  AlertCircle,
  ChevronDown,
  ArrowUpDown,
  Eye,
  Sparkles,
  Zap,
  Loader2
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import Link from "next/link"
import NewTicketModal from "@/components/new-ticket-modal"

interface Ticket {
  id: string
  subject: string
  customer: string
  channel: string
  category: string
  status: string
  priority: string
  sentiment: number
  time: string
}

const channelIcons: Record<string, any> = {
  email: Mail,
  whatsapp: Smartphone,
  web_form: MessageSquare
}

const statusConfig: Record<string, { badge: any, label: string }> = {
  open: { badge: "info", label: "Open" },
  pending: { badge: "info", label: "Pending" },
  in_progress: { badge: "warning", label: "In Progress" },
  resolved: { badge: "success", label: "Resolved" },
  escalated: { badge: "destructive", label: "Escalated" },
  // Uppercase variants
  OPEN: { badge: "info", label: "Open" },
  PENDING: { badge: "info", label: "Pending" },
  IN_PROGRESS: { badge: "warning", label: "In Progress" },
  RESOLVED: { badge: "success", label: "Resolved" },
  ESCALATED: { badge: "destructive", label: "Escalated" }
}

const priorityConfig: Record<string, { color: string, label: string }> = {
  low: { color: "text-blue-400", label: "Low" },
  medium: { color: "text-amber-400", label: "Medium" },
  high: { color: "text-orange-400", label: "High" },
  critical: { color: "text-red-400", label: "Critical" },
  // Uppercase variants
  LOW: { color: "text-blue-400", label: "Low" },
  MEDIUM: { color: "text-amber-400", label: "Medium" },
  HIGH: { color: "text-orange-400", label: "High" },
  CRITICAL: { color: "text-red-400", label: "Critical" }
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4
    }
  }
}

export default function TicketsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [filterStatus, setFilterStatus] = useState<string>("all")
  const [filterChannel, setFilterChannel] = useState<string>("all")
  const [isNewTicketModalOpen, setIsNewTicketModalOpen] = useState(false)
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isClient, setIsClient] = useState(false)
  const [stats, setStats] = useState({
    pending: 0,
    inProgress: 0,
    resolved: 0,
    avgResponse: "0m"
  })

  // Mark as client-side rendered
  useEffect(() => {
    setIsClient(true)
  }, [])

  // Fetch tickets from backend
  useEffect(() => {
    fetchTickets()
  }, [])

  const fetchTickets = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('http://localhost:8000/api/tickets', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Tickets data:', data)
      setTickets(data.tickets || [])

      // Fetch stats from API endpoint for accuracy
      const statsResponse = await fetch('http://localhost:8000/api/tickets/stats', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      })
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats({
          pending: statsData.pending || 0,
          inProgress: statsData.in_progress || 0,
          resolved: statsData.resolved || 0,
          avgResponse: statsData.avg_response || '2.4m'
        })
      } else {
        // Fallback to calculating from tickets data
        const pending = data.tickets?.filter((t: Ticket) => 
          t.status?.toUpperCase() === 'OPEN' || t.status?.toUpperCase() === 'PENDING'
        ).length || 0
        const inProgress = data.tickets?.filter((t: Ticket) => 
          t.status?.toUpperCase() === 'IN_PROGRESS'
        ).length || 0
        const resolved = data.tickets?.filter((t: Ticket) => 
          t.status?.toUpperCase() === 'RESOLVED'
        ).length || 0

        setStats({
          pending,
          inProgress,
          resolved,
          avgResponse: '2.4m'
        })
      }
    } catch (error) {
      console.error('Error fetching tickets:', error)
      // Set empty array on error
      setTickets([])
      setStats({
        pending: 0,
        inProgress: 0,
        resolved: 0,
        avgResponse: '0m'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const filteredTickets = tickets.filter(ticket => {
    const matchesSearch = ticket.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         ticket.customer.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = filterStatus === "all" || ticket.status?.toUpperCase() === filterStatus.toUpperCase()
    const matchesChannel = filterChannel === "all" || ticket.channel === filterChannel
    return matchesSearch && matchesStatus && matchesChannel
  })

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-6"
    >
      {!isClient ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-cyan-400" />
        </div>
      ) : (
        <>
          {/* Header */}
          <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text">
            Tickets
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage and respond to customer support requests
          </p>
        </div>
        <div className="flex items-center gap-2">
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button variant="outline" className="border-white/10 hover:bg-white/5">
              <Filter className="h-4 w-4 mr-2" />
              More Filters
            </Button>
          </motion.div>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button variant="premium" onClick={() => setIsNewTicketModalOpen(true)}>
              <Mail className="h-4 w-4 mr-2" />
              New Ticket
            </Button>
          </motion.div>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div variants={itemVariants}>
        <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl">
          <CardContent className="p-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search tickets by subject or customer..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="flex gap-2">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="h-10 px-3 rounded-xl border border-white/10 bg-white/[0.03] backdrop-blur-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all duration-300"
                >
                  <option value="all">All Status</option>
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                </select>
                <select
                  value={filterChannel}
                  onChange={(e) => setFilterChannel(e.target.value)}
                  className="h-10 px-3 rounded-xl border border-white/10 bg-white/[0.03] backdrop-blur-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all duration-300"
                >
                  <option value="all">All Channels</option>
                  <option value="email">Email</option>
                  <option value="whatsapp">WhatsApp</option>
                  <option value="web_form">Web Form</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Stats */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-4">
        {[
          { label: "Pending", value: stats.pending.toString(), icon: Clock, gradient: "from-blue-500 to-cyan-500", bg: "bg-blue-500/10", border: "border-blue-500/20" },
          { label: "In Progress", value: stats.inProgress.toString(), icon: AlertCircle, gradient: "from-amber-500 to-orange-500", bg: "bg-amber-500/10", border: "border-amber-500/20" },
          { label: "Resolved Today", value: stats.resolved.toString(), icon: CheckCircle2, gradient: "from-green-500 to-emerald-500", bg: "bg-green-500/10", border: "border-green-500/20" },
          { label: "Avg Response", value: stats.avgResponse, icon: ArrowUpDown, gradient: "from-purple-500 to-pink-500", bg: "bg-purple-500/10", border: "border-purple-500/20" }
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.03, y: -4 }}
          >
            <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl card-hover">
              <CardContent className="p-4 flex items-center gap-4">
                <motion.div
                  className={`p-3 rounded-lg ${stat.bg} border ${stat.border}`}
                  whileHover={{ scale: 1.1, rotate: 5 }}
                >
                  <stat.icon className={`h-5 w-5 bg-gradient-to-r ${stat.gradient} bg-clip-text`} style={{ WebkitTextFillColor: 'transparent' }} />
                </motion.div>
                <div>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <p className="text-2xl font-bold">{stat.value}</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* Loading State */}
      {isLoading && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center justify-center py-20"
        >
          <div className="text-center space-y-4">
            <Loader2 className="h-12 w-12 animate-spin text-cyan-400 mx-auto" />
            <p className="text-muted-foreground">Loading tickets from database...</p>
          </div>
        </motion.div>
      )}

      {/* No Tickets State */}
      {!isLoading && tickets.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-20"
        >
          <div className="max-w-md mx-auto space-y-4">
            <div className="p-6 rounded-full bg-white/5 border border-white/10 inline-block">
              <Mail className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold">No tickets found</h3>
            <p className="text-muted-foreground">
              Tickets will appear here when customers contact support.
            </p>
            <Button variant="premium" onClick={() => setIsNewTicketModalOpen(true)}>
              Create First Ticket
            </Button>
          </div>
        </motion.div>
      )}

      {/* Tickets List */}
      {!isLoading && tickets.length > 0 && (
      <motion.div variants={itemVariants} className="space-y-3">
        {filteredTickets.map((ticket, index) => {
          const ChannelIcon = channelIcons[ticket.channel] || MessageSquare
          const status = statusConfig[ticket.status] || { badge: "info", label: ticket.status || "Open" }
          const priority = priorityConfig[ticket.priority] || { color: "text-gray-400", label: ticket.priority || "Medium" }

          return (
            <motion.div
              key={ticket.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ scale: 1.01 }}
            >
              <Link href={`/dashboard/tickets/${ticket.id}`}>
                <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl hover:shadow-2xl hover:border-white/20 hover:bg-white/[0.06] transition-all duration-300 cursor-pointer group">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-4">
                      <Avatar>
                        <AvatarFallback className="bg-gradient-to-br from-blue-600 to-indigo-600 text-white text-xs">
                          {ticket.customer.split(" ").map(n => n[0]).join("")}
                        </AvatarFallback>
                      </Avatar>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-mono text-muted-foreground">{ticket.id}</span>
                          <Badge variant={status.badge as any} className="text-xs border-white/10 backdrop-blur-xl">
                            {status.label}
                          </Badge>
                          <span className={`text-xs font-medium ${priority.color}`}>
                            {priority.label}
                          </span>
                        </div>
                        <h3 className="font-medium truncate group-hover:text-blue-400 transition-colors">
                          {ticket.subject}
                        </h3>
                        <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <ChannelIcon className="h-3 w-3" />
                            {ticket.channel === "web_form" ? "Web Form" : 
                             ticket.channel === "gmail" ? "Email" :
                             ticket.channel?.charAt(0).toUpperCase() + ticket.channel?.slice(1)}
                          </span>
                          <span>•</span>
                          <span>{ticket.customer}</span>
                          <span>•</span>
                          <span>{ticket.time}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <div className="text-right hidden md:block">
                          <p className="text-xs text-muted-foreground">Sentiment</p>
                          <div className="flex items-center gap-1 mt-1">
                            <div className="w-20 h-2 rounded-full bg-white/10 overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${ticket.sentiment * 100}%` }}
                                transition={{ duration: 0.5, delay: index * 0.05 }}
                                className={`h-full rounded-full ${
                                  ticket.sentiment > 0.7 ? "bg-emerald-500" :
                                  ticket.sentiment > 0.4 ? "bg-amber-500" : "bg-red-500"
                                }`}
                              />
                            </div>
                            <span className="text-xs">{(ticket.sentiment * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                        <Button variant="ghost" size="icon" className="shrink-0 hover:bg-white/5">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          )
        })}
      </motion.div>
      )}

      {/* Pagination */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {filteredTickets.length} of {tickets.length} tickets
        </p>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled className="border-white/10">
            Previous
          </Button>
          <Button variant="outline" size="sm" className="border-white/10 hover:bg-white/5">
            Next
            <ChevronDown className="h-4 w-4 ml-1 rotate-180" />
          </Button>
        </div>
      </motion.div>

      {/* New Ticket Modal */}
      <NewTicketModal
        open={isNewTicketModalOpen}
        onOpenChange={setIsNewTicketModalOpen}
      />
        </>
      )}
    </motion.div>
  )
}
