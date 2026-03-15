"use client"

import { useState } from "react"
import { motion } from "framer-motion"
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
  MessageSquare
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { useRouter } from "next/navigation"

const ticket = {
  id: "TKT-001",
  subject: "Question about my invoice",
  customer: {
    name: "Sarah Johnson",
    email: "sarah.johnson@acmecorp.com",
    company: "Acme Corporation",
    avatar: "SJ"
  },
  channel: "email",
  category: "billing",
  status: "pending",
  priority: "medium",
  sentiment: 0.6,
  createdAt: "2025-01-20T09:15:00Z",
  message: `Hi TechCorp Team,

I received my invoice for this month and noticed a charge of $79, but I thought I was on the Starter plan which should be $29. Could you please help me understand what happened here? I haven't upgraded my plan as far as I know.

My account email is sarah.johnson@acmecorp.com

Thank you for your assistance.

Best regards,
Sarah Johnson
Acme Corporation`,
  history: [
    {
      type: "created",
      time: "15 minutes ago",
      description: "Ticket created from Email"
    },
    {
      type: "ai_analysis",
      time: "14 minutes ago",
      description: "AI analyzed ticket - Category: Billing, Sentiment: Neutral (60%)"
    },
    {
      type: "assigned",
      time: "10 minutes ago",
      description: "Assigned to Support Team by System"
    }
  ]
}

const aiSuggestions = [
  {
    id: 1,
    title: "Standard Billing Inquiry",
    confidence: 92,
    response: `Dear Sarah,

Thank you for reaching out to us regarding your invoice.

I've reviewed your account and can see that you're currently on our Growth plan ($79/month), which was upgraded from the Starter plan on December 20th. This upgrade might have been done by a team member or during a period when you needed additional features.

The Growth plan includes:
- Up to 50 users (vs 10 on Starter)
- 100GB storage (vs 5GB on Starter)
- Priority support
- Unlimited integrations

If you'd like to downgrade back to the Starter plan, I'd be happy to help with that. Please note that the downgrade will take effect from your next billing cycle.

Would you like me to:
1. Keep you on the Growth plan and explain the additional features you now have access to
2. Downgrade to the Starter plan with prorated refund
3. Schedule a call to discuss which plan best fits your needs

Please let me know how you'd like to proceed.

Best regards,
TechCorp Support Team`
  },
  {
    id: 2,
    title: "Escalate to Billing",
    confidence: 78,
    response: `Dear Sarah,

Thank you for contacting us about the billing discrepancy.

I understand your concern about the unexpected charge. Let me escalate this to our billing specialist team who can investigate this matter more thoroughly.

In the meantime, I've placed a temporary hold on your account to prevent any automatic renewals until we resolve this.

Our billing team will review your account history and get back to you within 2 hours with a detailed explanation and resolution.

Reference Number: BILL-2025-0120-001

Is there anything else I can help you with in the meantime?

Best regards,
TechCorp Support Team`
  },
  {
    id: 3,
    title: "Offer Plan Review",
    confidence: 85,
    response: `Dear Sarah,

I appreciate you bringing this to our attention.

It appears there might have been some confusion about your plan selection. I'd be happy to help clarify and find the best solution for you.

Looking at your usage over the past month, I can see you've been utilizing features from both plans. Let me offer you two options:

Option 1: Stay on Growth Plan
- We'll apply a 20% loyalty discount for the next 3 months
- You'll retain access to all advanced features
- Effective monthly cost: $63.20

Option 2: Downgrade to Starter
- Immediate downgrade with prorated refund of $50
- We'll help export any data that exceeds Starter limits
- Next billing: $29/month

Which option works better for you? I'm here to ensure you get the best value.

Best regards,
TechCorp Support Team`
  }
]

export default function TicketDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [selectedSuggestion, setSelectedSuggestion] = useState<number | null>(null)
  const [copied, setCopied] = useState(false)
  const [response, setResponse] = useState("")

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleUseSuggestion = (suggestionText: string) => {
    setResponse(suggestionText)
    setSelectedSuggestion(null)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center gap-4">
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </motion.div>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">{ticket.subject}</h1>
            <Badge variant="info" className="border-blue-500/30 bg-blue-500/20 backdrop-blur-xl">Pending</Badge>
            <Badge variant="warning" className="border-amber-500/30 bg-amber-500/20 backdrop-blur-xl">Medium Priority</Badge>
          </div>
          <p className="text-muted-foreground text-sm mt-1">
            {ticket.id} • Created {new Date(ticket.createdAt).toLocaleString()}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button variant="outline" className="border-white/10 hover:bg-white/5">
              <RotateCcw className="h-4 w-4 mr-2" />
              Reopen
            </Button>
          </motion.div>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button variant="premium">
              <Send className="h-4 w-4 mr-2" />
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
                    {ticket.customer.avatar}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <CardTitle className="flex items-center gap-2">
                    {ticket.customer.name}
                    <Mail className="h-4 w-4 text-muted-foreground" />
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {ticket.customer.email} • {ticket.customer.company}
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="prose dark:prose-invert max-w-none">
                <p className="whitespace-pre-line">{ticket.message}</p>
              </div>
              <div className="flex items-center gap-4 mt-6 pt-4 border-t border-white/10">
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button variant="ghost" size="sm" className="hover:bg-white/5">
                    <ThumbsUp className="h-4 w-4 mr-2" />
                    Helpful
                  </Button>
                </motion.div>
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button variant="ghost" size="sm" className="hover:bg-white/5">
                    <ThumbsDown className="h-4 w-4 mr-2" />
                    Not Helpful
                  </Button>
                </motion.div>
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button variant="ghost" size="sm" className="hover:bg-white/5">
                    <Paperclip className="h-4 w-4 mr-2" />
                    Attach File
                  </Button>
                </motion.div>
              </div>
            </CardContent>
          </Card>

          {/* AI Response Suggestions */}
          <Card className="border-white/10 bg-gradient-to-br from-blue-600/10 via-indigo-600/10 to-purple-600/10 backdrop-blur-xl">
            <CardHeader>
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-500">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
                <CardTitle>AI Response Suggestions</CardTitle>
                <Badge variant="success" className="ml-auto border-emerald-500/30 bg-emerald-500/20 backdrop-blur-xl">
                  92% Confidence
                </Badge>
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
                      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
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
                      </motion.div>
                      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
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
                      </motion.div>
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
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button variant="outline" size="sm" className="border-white/10 hover:bg-white/5">
                    <Paperclip className="h-4 w-4 mr-2" />
                    Attach File
                  </Button>
                </motion.div>
                <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                  <Button variant="premium">
                    <Send className="h-4 w-4 mr-2" />
                    Send Response
                  </Button>
                </motion.div>
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
                      {ticket.customer.avatar}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium text-sm">{ticket.customer.name}</p>
                    <p className="text-xs text-muted-foreground">{ticket.customer.company}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                    <Mail className="h-4 w-4" />
                    Channel
                  </div>
                  <p className="font-medium capitalize">{ticket.channel.replace("_", " ")}</p>
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
                  <p className="font-medium text-amber-400 capitalize">{ticket.priority}</p>
                </div>
                <div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                    <Clock className="h-4 w-4" />
                    Response Time
                  </div>
                  <p className="font-medium">15m</p>
                </div>
              </div>

              <div>
                <div className="text-sm text-muted-foreground mb-2">Sentiment Analysis</div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-3 rounded-full bg-white/10 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${ticket.sentiment * 100}%` }}
                      transition={{ duration: 1 }}
                      className="h-full rounded-full bg-amber-500"
                    />
                  </div>
                  <span className="text-sm font-medium">{(ticket.sentiment * 100).toFixed(0)}%</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Neutral - Customer is calm but concerned
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Timeline */}
          <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-lg">Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {ticket.history.map((event, index) => (
                  <motion.div 
                    key={index} 
                    className="flex gap-3"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <div className="relative">
                      <motion.div 
                        className={`h-2 w-2 rounded-full mt-2 ${
                          event.type === "created" ? "bg-blue-500" :
                          event.type === "ai_analysis" ? "bg-purple-500" :
                          "bg-emerald-500"
                        }`}
                        whileHover={{ scale: 1.5 }}
                      />
                      {index < ticket.history.length - 1 && (
                        <div className="absolute top-4 left-1 w-px h-full bg-white/10" />
                      )}
                    </div>
                    <div className="flex-1 pb-4">
                      <p className="text-sm font-medium">{event.description}</p>
                      <p className="text-xs text-muted-foreground">{event.time}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <Card className="border-white/10 bg-white/[0.03] backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-lg">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {[
                { icon: Tag, text: "Change Category" },
                { icon: Flag, text: "Update Priority" },
                { icon: User, text: "Reassign Ticket" },
                { icon: Clock, text: "Schedule Follow-up" }
              ].map((action, index) => (
                <motion.div
                  key={index}
                  whileHover={{ scale: 1.02, x: 4 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Button variant="outline" className="w-full justify-start border-white/10 hover:bg-white/5">
                    <action.icon className="h-4 w-4 mr-2" />
                    {action.text}
                  </Button>
                </motion.div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </motion.div>
  )
}
