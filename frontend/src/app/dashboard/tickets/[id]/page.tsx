"use client"

import { useState, useEffect, use } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  ArrowLeft,
  Mail,
  Clock,
  User,
  Tag,
  Flag,
  Send,
  Sparkles,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Paperclip,
  Zap,
  MessageSquare,
  Loader2,
  Smartphone,
  Globe,
  RefreshCw,
  CheckCircle,
  AlertCircle
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { useRouter } from "next/navigation"

interface Ticket {
  id: string
  subject: string
  customer_name: string
  customer_email: string
  channel: string
  category: string
  status: string
  priority: string
  sentiment: number
  time: string
  created_at: string
  message?: string
}

interface Message {
  id: string
  role: string
  content: string
  created_at: string
  channel: string
}

const channelIcons: Record<string, any> = {
  email: Mail,
  whatsapp: Smartphone,
  web_form: Globe
}

const statusConfig: Record<string, { badge: any, label: string }> = {
  open: { badge: "info", label: "Open" },
  pending: { badge: "info", label: "Pending" },
  in_progress: { badge: "warning", label: "In Progress" },
  resolved: { badge: "success", label: "Resolved" },
  escalated: { badge: "destructive", label: "Escalated" },
  OPEN: { badge: "info", label: "Open" },
  PENDING: { badge: "info", label: "Pending" },
  IN_PROGRESS: { badge: "warning", label: "In Progress" },
  RESOLVED: { badge: "success", label: "Resolved" },
  ESCALATED: { badge: "destructive", label: "Escalated" }
}

export default function TicketDetailPage({ params }: { params: Promise<{ id: string }> }) {
  // Unwrap params Promise using React.use()
  const unwrappedParams = use(params)
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [selectedSuggestion, setSelectedSuggestion] = useState<number | null>(null)
  const [copied, setCopied] = useState(false)
  const [response, setResponse] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [notification, setNotification] = useState<{type: 'success' | 'error', message: string} | null>(null)

  // Auto-hide notification after 5 seconds
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [notification])

  useEffect(() => {
    fetchTicketData()
  }, [unwrappedParams.id])

  const fetchTicketData = async () => {
    try {
      setLoading(true)
      console.log("📤 Fetching ticket:", unwrappedParams.id)

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/tickets/${unwrappedParams.id}`)
      console.log("📥 Response status:", response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log("✅ Ticket data received:", data)
        
        if (data.error) {
          console.error("API returned error:", data.error)
          setTicket(null)
        } else {
          setTicket(data.ticket)
          setMessages(data.messages || [])
        }
      } else {
        console.error("API request failed with status:", response.status)
        const errorData = await response.json()
        console.error("Error data:", errorData)
        setTicket(null)
      }
    } catch (error) {
      console.error("❌ Error fetching ticket:", error)
      setTicket(null)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchTicketData()
    setRefreshing(false)
  }

  const handleSendResponse = async () => {
    if (!response.trim() || !ticket) return

    setSubmitting(true)
    try {
      console.log("📤 Sending response...", { ticket_id: unwrappedParams.id, message: response })

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

      // First update status to IN_PROGRESS
      await fetch(`${apiUrl}/api/tickets/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticket_id: unwrappedParams.id,
          status: "IN_PROGRESS"
        })
      })

      // Then send the response
      const responsePayload = await fetch(`${apiUrl}/api/tickets/response`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticket_id: unwrappedParams.id,
          message: response,
          sender: "AGENT"
        })
      })

      if (responsePayload.ok) {
        const data = await responsePayload.json()
        console.log("✅ Response sent:", data)
        
        // Show success notification
        setNotification({
          type: 'success',
          message: '✅ Response sent successfully! Status updated to In Progress.'
        })
        
        setResponse("")
        
        // Wait 2 seconds then redirect to tickets page
        setTimeout(() => {
          router.push("/dashboard/tickets")
        }, 2000)
      } else {
        const errorData = await responsePayload.json()
        console.error("❌ Error sending response:", errorData)
        setNotification({
          type: 'error',
          message: '❌ Failed to send response: ' + (errorData.error || "Unknown error")
        })
      }
    } catch (error) {
      console.error("Error sending response:", error)
      setNotification({
        type: 'error',
        message: '❌ Error: ' + (error as Error).message
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleStatusUpdate = async (newStatus: string) => {
    if (!ticket) return

    try {
      console.log("📤 Updating status...", { ticket_id: unwrappedParams.id, status: newStatus })

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/tickets/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticket_id: unwrappedParams.id,
          status: newStatus
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log("✅ Status updated:", data)
        setNotification({
          type: 'success',
          message: `✅ Status updated to ${newStatus.replace('_', ' ')}!`
        })
        await fetchTicketData()
      } else {
        const errorData = await response.json()
        console.error("❌ Error updating status:", errorData)
        setNotification({
          type: 'error',
          message: '❌ Failed to update status: ' + (errorData.error || "Unknown error")
        })
      }
    } catch (error) {
      console.error("Error updating status:", error)
      setNotification({
        type: 'error',
        message: '❌ Error: ' + (error as Error).message
      })
    }
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleUseSuggestion = (suggestionText: string) => {
    setResponse(suggestionText)
    setSelectedSuggestion(null)
  }

  const aiSuggestions = [
    {
      id: 1,
      title: "Standard Response",
      confidence: 92,
      response: `Dear ${ticket?.customer_name || 'Customer'},

Thank you for contacting TechCorp Support.

I've reviewed your ticket and I'm here to help you resolve this issue. Let me look into the details and get back to you with a solution.

If you have any additional information that might help, please don't hesitate to share.

Best regards,
TechCorp Support Team`
    },
    {
      id: 2,
      title: "Request More Info",
      confidence: 85,
      response: `Dear ${ticket?.customer_name || 'Customer'},

Thank you for reaching out to us.

To better assist you, could you please provide the following information:
1. When did this issue first occur?
2. Have you tried any troubleshooting steps?
3. Are you seeing any error messages?

This will help us resolve your issue faster.

Best regards,
TechCorp Support Team`
    },
    {
      id: 3,
      title: "Escalate to Specialist",
      confidence: 78,
      response: `Dear ${ticket?.customer_name || 'Customer'},

Thank you for your patience.

I'm escalating this to our specialist team who can provide more targeted assistance. They will review your case and get back to you within 2 hours.

Reference: ${ticket?.id}

Best regards,
TechCorp Support Team`
    }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-12 w-12 animate-spin text-cyan-400" />
      </div>
    )
  }

  if (!ticket) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold text-white mb-2">Ticket Not Found</h2>
        <p className="text-neutral-400 mb-4">The ticket you're looking for doesn't exist or API is not responding.</p>
        <div className="text-sm text-neutral-500 mb-4">
          Looking for: {unwrappedParams.id}
        </div>
        <Button onClick={() => router.push("/dashboard/tickets")}>
          Back to Tickets
        </Button>
      </div>
    )
  }

  const statusBadge = statusConfig[ticket.status?.toLowerCase()] || { badge: "info", label: ticket.status }
  const ChannelIcon = channelIcons[ticket.channel?.toLowerCase()] || Mail

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Notification Toast */}
      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, y: -50, x: "-50%" }}
            animate={{ opacity: 1, y: 0, x: "-50%" }}
            exit={{ opacity: 0, y: -50, x: "-50%" }}
            className={`fixed top-4 left-1/2 z-50 px-6 py-4 rounded-xl shadow-2xl backdrop-blur-xl border ${
              notification.type === 'success'
                ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-400'
                : 'bg-red-500/20 border-red-500/30 text-red-400'
            }`}
          >
            <div className="flex items-center gap-3">
              {notification.type === 'success' ? (
                <CheckCircle className="h-5 w-5" />
              ) : (
                <AlertCircle className="h-5 w-5" />
              )}
              <span className="font-medium">{notification.message}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button variant="ghost" size="icon" onClick={() => router.back()}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </motion.div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold">{ticket.subject}</h1>
              <Badge variant={statusBadge.badge} className="border-emerald-500/30 bg-emerald-500/20 backdrop-blur-xl">
                {statusBadge.label}
              </Badge>
            </div>
            <p className="text-muted-foreground text-sm mt-1">
              {ticket.id} • Created {new Date(ticket.created_at).toLocaleString()}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button 
              variant="outline" 
              className="border-white/10 hover:bg-white/5"
              onClick={() => handleStatusUpdate("RESOLVED")}
            >
              <Check className="h-4 w-4 mr-2" />
              Resolve
            </Button>
          </motion.div>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button variant="premium" onClick={handleSendResponse} disabled={submitting}>
              {submitting ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Send className="h-4 w-4 mr-2" />
              )}
              Send Response
            </Button>
          </motion.div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Customer Message */}
          <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl">
            <CardHeader>
              <div className="flex items-center gap-4">
                <Avatar className="h-12 w-12">
                  <AvatarFallback className="bg-gradient-to-br from-blue-600 to-indigo-600 text-white">
                    {(ticket.customer_name || "C").substring(0, 2).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <CardTitle className="flex items-center gap-2">
                    {ticket.customer_name || ticket.customer_email}
                    <Mail className="h-4 w-4 text-muted-foreground" />
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {ticket.customer_email}
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="prose dark:prose-invert max-w-none">
                <p className="whitespace-pre-line">
                  {ticket.message || `Subject: ${ticket.subject}\n\nCategory: ${ticket.category}\nPriority: ${ticket.priority}\n\nPlease assist with this issue.`}
                </p>
              </div>
              <div className="flex items-center gap-4 mt-6 pt-4 border-t border-white/10">
                <div className="flex items-center gap-2">
                  <ChannelIcon className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    {ticket.channel === "web_form" ? "Web Form" : ticket.channel}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">{ticket.time}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Messages Timeline */}
          {messages.length > 0 && (
            <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl">
              <CardHeader>
                <CardTitle>Conversation</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`p-4 rounded-lg ${
                      msg.role === "CUSTOMER" 
                        ? "bg-blue-500/10 border border-blue-500/20" 
                        : "bg-green-500/10 border border-green-500/20"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <Badge variant={msg.role === "CUSTOMER" ? "info" : "success"}>
                        {msg.role}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(msg.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm">{msg.content}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* AI Response Suggestions */}
          <Card className="border-white/10 bg-gradient-to-br from-blue-600/10 via-indigo-600/10 to-purple-600/10 backdrop-blur-xl">
            <CardHeader>
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-500">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
                <CardTitle>AI Response Suggestions</CardTitle>
              </div>
              <p className="text-sm text-muted-foreground">
                AI-generated responses based on ticket analysis
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              {aiSuggestions.map((suggestion) => (
                <motion.div
                  key={suggestion.id}
                  whileHover={{ scale: 1.01 }}
                  className={`border rounded-xl p-4 cursor-pointer transition-all duration-300 ${
                    selectedSuggestion === suggestion.id
                      ? "border-blue-500/50 bg-blue-500/10 backdrop-blur-xl"
                      : "border-white/10 hover:border-white/20 hover:bg-white/[0.03]"
                  }`}
                  onClick={() => setSelectedSuggestion(
                    selectedSuggestion === suggestion.id ? null : suggestion.id
                  )}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{suggestion.title}</span>
                      <Badge variant="secondary" className="text-xs border-white/10">
                        {suggestion.confidence}% match
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleCopy(suggestion.response)
                        }}
                        className="hover:bg-white/5"
                      >
                        {copied ? (
                          <Check className="h-4 w-4 text-emerald-500" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleUseSuggestion(suggestion.response)
                        }}
                        className="border-white/10 hover:bg-white/5"
                      >
                        Use This
                      </Button>
                    </div>
                  </div>
                  {selectedSuggestion === suggestion.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      className="mt-3 p-3 bg-white/[0.03] border border-white/10 rounded-md text-sm whitespace-pre-line"
                    >
                      {suggestion.response}
                    </motion.div>
                  )}
                </motion.div>
              ))}
            </CardContent>
          </Card>

          {/* Response Editor */}
          <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Your Response</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <textarea
                value={response}
                onChange={(e) => setResponse(e.target.value)}
                placeholder="Type your response or select an AI suggestion above..."
                className="w-full min-h-[200px] p-4 rounded-xl border border-white/10 bg-white/[0.03] backdrop-blur-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 resize-none transition-all duration-300"
              />
              <div className="flex items-center justify-between">
                <Button variant="outline" size="sm" className="border-white/10 hover:bg-white/5">
                  <Paperclip className="h-4 w-4 mr-2" />
                  Attach File
                </Button>
                <Button 
                  variant="premium" 
                  onClick={handleSendResponse}
                  disabled={submitting || !response.trim()}
                >
                  {submitting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      Send Response
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Ticket Details */}
          <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-lg">Ticket Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                  <User className="h-4 w-4" />
                  Customer
                </div>
                <div className="flex items-center gap-3">
                  <Avatar>
                    <AvatarFallback className="bg-gradient-to-br from-blue-600 to-indigo-600 text-white text-xs">
                      {(ticket.customer_name || "C").substring(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium text-sm">{ticket.customer_name || "Customer"}</p>
                    <p className="text-xs text-muted-foreground">{ticket.customer_email}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                    <Mail className="h-4 w-4" />
                    Channel
                  </div>
                  <p className="font-medium capitalize">
                    {ticket.channel === "web_form" ? "Web Form" : ticket.channel}
                  </p>
                </div>
                <div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                    <Tag className="h-4 w-4" />
                    Category
                  </div>
                  <p className="font-medium capitalize">{ticket.category}</p>
                </div>
                <div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                    <Flag className="h-4 w-4" />
                    Priority
                  </div>
                  <p className={`font-medium ${
                    ticket.priority === "HIGH" || ticket.priority === "high" ? "text-red-400" :
                    ticket.priority === "MEDIUM" || ticket.priority === "medium" ? "text-amber-400" :
                    "text-blue-400"
                  }`}>
                    {ticket.priority}
                  </p>
                </div>
                <div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                    <Clock className="h-4 w-4" />
                    Created
                  </div>
                  <p className="font-medium text-sm">{ticket.time}</p>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="pt-4 border-t border-white/10">
                <div className="text-sm text-muted-foreground mb-2">Quick Actions</div>
                <div className="space-y-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start border-white/10 hover:bg-white/5"
                    onClick={() => handleStatusUpdate("IN_PROGRESS")}
                  >
                    <Clock className="h-4 w-4 mr-2" />
                    Mark In Progress
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start border-white/10 hover:bg-white/5"
                    onClick={() => handleStatusUpdate("RESOLVED")}
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Resolve Ticket
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start border-white/10 hover:bg-white/5"
                    onClick={() => handleStatusUpdate("OPEN")}
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Reopen Ticket
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </motion.div>
  )
}
