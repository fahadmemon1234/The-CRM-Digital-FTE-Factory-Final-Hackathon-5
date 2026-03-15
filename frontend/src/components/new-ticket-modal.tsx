"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { X, Mail, Smartphone, MessageSquare, Send, Loader2, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface NewTicketModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

interface TicketFormData {
  customerName: string
  customerEmail: string
  customerPhone: string
  subject: string
  category: string
  channel: string
  priority: string
  message: string
}

export default function NewTicketModal({ open, onOpenChange }: NewTicketModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [ticketId, setTicketId] = useState("")
  
  const [formData, setFormData] = useState<TicketFormData>({
    customerName: "",
    customerEmail: "",
    customerPhone: "",
    subject: "",
    category: "general",
    channel: "web_form",
    priority: "medium",
    message: ""
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Generate random ticket ID
    const newTicketId = `TKT-${Math.random().toString(36).substr(2, 6).toUpperCase()}`
    setTicketId(newTicketId)
    setSubmitted(true)
    setIsLoading(false)
    
    // Reset after 3 seconds
    setTimeout(() => {
      setSubmitted(false)
      setFormData({
        customerName: "",
        customerEmail: "",
        customerPhone: "",
        subject: "",
        category: "general",
        channel: "web_form",
        priority: "medium",
        message: ""
      })
      onOpenChange(false)
    }, 3000)
  }

  const updateField = (field: keyof TicketFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const channelIcons: Record<string, any> = {
    email: Mail,
    whatsapp: Smartphone,
    web_form: MessageSquare
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto border-white/10 bg-gradient-to-br from-neutral-900/95 via-neutral-900/90 to-neutral-900/95 backdrop-blur-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 260, damping: 20 }}
            >
              <Sparkles className="h-5 w-5 text-cyan-400" />
            </motion.div>
            Create New Ticket
          </DialogTitle>
          <DialogDescription className="text-neutral-400">
            Manually create a support ticket for a customer. All fields are required.
          </DialogDescription>
        </DialogHeader>

        <AnimatePresence mode="wait">
          {!submitted ? (
            <motion.form
              key="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              onSubmit={handleSubmit}
              className="space-y-6"
            >
              {/* Customer Information */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 mb-3">
                  <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                  <span className="text-xs font-medium text-neutral-400 uppercase tracking-wider">Customer Information</span>
                  <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="customerName" className="text-sm font-medium">
                      Customer Name *
                    </Label>
                    <Input
                      id="customerName"
                      placeholder="John Doe"
                      value={formData.customerName}
                      onChange={(e) => updateField("customerName", e.target.value)}
                      required
                      className="border-white/10 bg-white/[0.03] focus:border-cyan-500/50 focus:ring-cyan-500/20"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="customerEmail" className="text-sm font-medium">
                      Customer Email *
                    </Label>
                    <Input
                      id="customerEmail"
                      type="email"
                      placeholder="john@example.com"
                      value={formData.customerEmail}
                      onChange={(e) => updateField("customerEmail", e.target.value)}
                      required
                      className="border-white/10 bg-white/[0.03] focus:border-cyan-500/50 focus:ring-cyan-500/20"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="customerPhone" className="text-sm font-medium">
                    Customer Phone
                  </Label>
                  <Input
                    id="customerPhone"
                    type="tel"
                    placeholder="+1 (415) 555-1234"
                    value={formData.customerPhone}
                    onChange={(e) => updateField("customerPhone", e.target.value)}
                    className="border-white/10 bg-white/[0.03] focus:border-cyan-500/50 focus:ring-cyan-500/20"
                  />
                </div>
              </div>

              {/* Ticket Details */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 mb-3">
                  <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                  <span className="text-xs font-medium text-neutral-400 uppercase tracking-wider">Ticket Details</span>
                  <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="subject" className="text-sm font-medium">
                    Subject *
                  </Label>
                  <Input
                    id="subject"
                    placeholder="Brief description of the issue"
                    value={formData.subject}
                    onChange={(e) => updateField("subject", e.target.value)}
                    required
                    className="border-white/10 bg-white/[0.03] focus:border-cyan-500/50 focus:ring-cyan-500/20"
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <Label htmlFor="category" className="text-sm font-medium">
                      Category
                    </Label>
                    <Select value={formData.category} onValueChange={(value) => updateField("category", value)}>
                      <SelectTrigger className="border-white/10 bg-white/[0.03]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="general">General</SelectItem>
                        <SelectItem value="technical">Technical</SelectItem>
                        <SelectItem value="billing">Billing</SelectItem>
                        <SelectItem value="bug_report">Bug Report</SelectItem>
                        <SelectItem value="feedback">Feedback</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="channel" className="text-sm font-medium">
                      Channel
                    </Label>
                    <Select value={formData.channel} onValueChange={(value) => updateField("channel", value)}>
                      <SelectTrigger className="border-white/10 bg-white/[0.03]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="email">
                          <div className="flex items-center gap-2">
                            <Mail className="h-4 w-4" />
                            Email
                          </div>
                        </SelectItem>
                        <SelectItem value="whatsapp">
                          <div className="flex items-center gap-2">
                            <Smartphone className="h-4 w-4" />
                            WhatsApp
                          </div>
                        </SelectItem>
                        <SelectItem value="web_form">
                          <div className="flex items-center gap-2">
                            <MessageSquare className="h-4 w-4" />
                            Web Form
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="priority" className="text-sm font-medium">
                      Priority
                    </Label>
                    <Select value={formData.priority} onValueChange={(value) => updateField("priority", value)}>
                      <SelectTrigger className="border-white/10 bg-white/[0.03]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="message" className="text-sm font-medium">
                    Message *
                  </Label>
                  <Textarea
                    id="message"
                    placeholder="Detailed description of the customer issue..."
                    value={formData.message}
                    onChange={(e) => updateField("message", e.target.value)}
                    required
                    rows={6}
                    className="border-white/10 bg-white/[0.03] focus:border-cyan-500/50 focus:ring-cyan-500/20 resize-none"
                  />
                </div>
              </div>

              <DialogFooter className="gap-2 sm:gap-0">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => onOpenChange(false)}
                  disabled={isLoading}
                  className="border-white/10 hover:bg-white/5"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="premium"
                  disabled={isLoading}
                  className="min-w-[140px]"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      Create Ticket
                    </>
                  )}
                </Button>
              </DialogFooter>
            </motion.form>
          ) : (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="py-12"
            >
              <Card className="border-emerald-500/20 bg-emerald-500/5 backdrop-blur-xl">
                <CardContent className="text-center space-y-4">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 260, damping: 20, delay: 0.2 }}
                    className="mx-auto w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-green-500 flex items-center justify-center shadow-lg shadow-emerald-500/30"
                  >
                    <Sparkles className="h-8 w-8 text-white" />
                  </motion.div>
                  
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                  >
                    <h3 className="text-2xl font-bold gradient-text mb-2">
                      Ticket Created Successfully!
                    </h3>
                    <p className="text-neutral-400 mb-4">
                      The support ticket has been created and assigned to our team.
                    </p>
                    
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
                      <span className="text-sm text-neutral-400">Ticket ID:</span>
                      <Badge variant="warning" className="font-mono">
                        {ticketId}
                      </Badge>
                    </div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="pt-4"
                  >
                    <p className="text-sm text-neutral-500">
                      Closing in 3 seconds...
                    </p>
                  </motion.div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </DialogContent>
    </Dialog>
  )
}
