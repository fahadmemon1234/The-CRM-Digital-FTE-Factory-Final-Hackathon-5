"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { CheckCircle, Loader2, ArrowLeft, Mail, Smartphone, Globe } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"
import Link from "next/link"

const CATEGORIES = [
  { value: "general", label: "General Question" },
  { value: "technical", label: "Technical Support" },
  { value: "billing", label: "Billing Inquiry" },
  { value: "bug_report", label: "Bug Report" },
  { value: "feedback", label: "Feature Request" }
]

const CHANNELS = [
  {
    id: "whatsapp",
    name: "WhatsApp",
    icon: Smartphone,
    color: "from-green-500 to-emerald-500",
    bgColor: "bg-green-500/10",
    borderColor: "border-green-500/30",
    description: "Get support via WhatsApp"
  },
  {
    id: "email",
    name: "Email",
    icon: Mail,
    color: "from-blue-500 to-cyan-500",
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/30",
    description: "Receive response via email"
  },
  {
    id: "web_form",
    name: "Web Form",
    icon: Globe,
    color: "from-purple-500 to-pink-500",
    bgColor: "bg-purple-500/10",
    borderColor: "border-purple-500/30",
    description: "Submit via web form"
  }
]

export default function ChannelsPage() {
  const router = useRouter()
  const [selectedChannel, setSelectedChannel] = useState<string>("web_form")
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    subject: "",
    category: "general",
    priority: "MEDIUM",
    message: ""
  })
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle")
  const [ticketId, setTicketId] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus("submitting")
    setError("")

    try {
      console.log("📤 Creating ticket...", { channel: selectedChannel, ...formData })

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      let response

      if (selectedChannel === "whatsapp") {
        // WhatsApp: Send via webhook
        response = await fetch(`${apiUrl}/webhooks/whatsapp`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({
            From: formData.phone,
            Body: `${formData.subject}\n\n${formData.message}\n\nName: ${formData.name}\nEmail: ${formData.email}`,
            To: "whatsapp:+14155238886"
          }).toString()
        })
      } else if (selectedChannel === "email") {
        // Email: Send via webhook
        response = await fetch(`${apiUrl}/webhooks/email`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            from: formData.email,
            name: formData.name,
            subject: formData.subject,
            body: formData.message
          })
        })
      } else {
        // Web Form: Use support submit endpoint
        response = await fetch(`${apiUrl}/support/submit`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: formData.name,
            email: formData.email,
            subject: formData.subject,
            category: formData.category.toLowerCase(),
            message: formData.message
          })
        })
      }

      console.log("📥 Response status:", response.status)

      if (!response.ok) {
        const errorData = await response.json()
        const detail = errorData.detail
        const message = Array.isArray(detail)
          ? detail.map((e: any) => e.msg || e.message).join(", ")
          : detail || "Submission failed"
        throw new Error(message)
      }

      const data = await response.json()
      console.log("✅ Ticket created:", data)

      setTicketId(data.ticket_id)
      setStatus("success")
    } catch (err) {
      console.error("❌ Error:", err)
      setError(err instanceof Error ? err.message : "Failed to create ticket. Please try again.")
      setStatus("error")
    }
  }

  const selectedChannelData = CHANNELS.find(ch => ch.id === selectedChannel)

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#030712]">
      {/* Back Button */}
      <Link href="/dashboard" className="fixed top-4 left-4">
        <Button variant="ghost" className="text-neutral-400 hover:text-white">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-4xl"
      >
        {status === "success" ? (
          <Card className="border border-emerald-500/30 bg-emerald-500/10 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="text-center">
                <CheckCircle className="h-16 w-16 text-emerald-400 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-white mb-2">Ticket Created Successfully!</h2>
                <p className="text-neutral-400 mb-4">Your support request has been submitted via {selectedChannelData?.name}.</p>
                <div className="bg-neutral-900/50 rounded-lg p-4 mb-4">
                  <p className="text-sm text-neutral-400">Your Ticket ID</p>
                  <p className="text-2xl font-mono font-bold text-white">{ticketId}</p>
                </div>
                <div className="flex items-center justify-center gap-2 mb-4">
                  <Badge variant="outline" className="border-emerald-500/30 text-emerald-400">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Response within 5 minutes
                  </Badge>
                </div>
                <div className="flex gap-3 justify-center">
                  <Button onClick={() => {
                    setStatus("idle")
                    setFormData({ name: "", email: "", phone: "", subject: "", category: "general", priority: "MEDIUM", message: "" })
                  }} variant="premium">
                    Create Another Ticket
                  </Button>
                  <Button onClick={() => router.push(`/dashboard/tickets/${ticketId}`)} variant="premium">
                    View Ticket
                  </Button>
                  <Button onClick={() => router.push("/dashboard/tickets")} variant="outline">
                    View All Tickets
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-3">
            {/* Channel Selection */}
            <div className="md:col-span-1 space-y-3">
              <h3 className="text-lg font-semibold text-white mb-4">Select Channel</h3>
              {CHANNELS.map((channel) => {
                const Icon = channel.icon
                return (
                  <motion.button
                    key={channel.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setSelectedChannel(channel.id)}
                    className={`w-full p-4 rounded-xl border backdrop-blur-xl transition-all duration-300 text-left ${
                      selectedChannel === channel.id
                        ? `${channel.bgColor} ${channel.borderColor} border-2`
                        : "border-neutral-700/30 bg-neutral-900/40 hover:border-neutral-600/50"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg bg-gradient-to-br ${channel.color}`}>
                        <Icon className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-white">{channel.name}</p>
                        <p className="text-xs text-neutral-400">{channel.description}</p>
                      </div>
                    </div>
                  </motion.button>
                )
              })}

              {/* Info Card */}
              <Card className="border-neutral-700/30 bg-neutral-900/40 backdrop-blur-xl mt-4">
                <CardContent className="p-4">
                  <h4 className="font-medium text-white mb-2">How it works:</h4>
                  <ul className="text-xs text-neutral-400 space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="text-emerald-400">•</span>
                      <span>Choose your preferred channel</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-emerald-400">•</span>
                      <span>Fill in your details and issue</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-emerald-400">•</span>
                      <span>Get instant ticket ID</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-emerald-400">•</span>
                      <span>AI responds within 5 minutes</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </div>

            {/* Form */}
            <Card className="md:col-span-2 border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-xl">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg bg-gradient-to-br ${selectedChannelData?.color}`}>
                    {selectedChannelData && <selectedChannelData.icon className="h-5 w-5 text-white" />}
                  </div>
                  <div>
                    <CardTitle className="text-white">Create Ticket via {selectedChannelData?.name}</CardTitle>
                    <CardDescription>Fill in the details below to create a support ticket</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {error && (
                  <div className="mb-4 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                    {error}
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Name */}
                  <div>
                    <label className="text-sm text-neutral-400 mb-1 block">Your Name *</label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full h-10 rounded-lg border border-neutral-700/50 bg-neutral-900/50 px-3 text-sm text-white focus:ring-2 focus:ring-cyan-500/50 focus:outline-none"
                      placeholder="John Doe"
                    />
                  </div>

                  {/* Contact Info based on channel */}
                  {selectedChannel === "whatsapp" ? (
                    <div>
                      <label className="text-sm text-neutral-400 mb-1 block">WhatsApp Number *</label>
                      <input
                        type="tel"
                        required
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        className="w-full h-10 rounded-lg border border-neutral-700/50 bg-neutral-900/50 px-3 text-sm text-white focus:ring-2 focus:ring-green-500/50 focus:outline-none"
                        placeholder="+1 (555) 123-4567"
                      />
                      <p className="text-xs text-neutral-500 mt-1">Include country code (e.g., +1 for US)</p>
                    </div>
                  ) : (
                    <div>
                      <label className="text-sm text-neutral-400 mb-1 block">Email Address *</label>
                      <input
                        type="email"
                        required
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="w-full h-10 rounded-lg border border-neutral-700/50 bg-neutral-900/50 px-3 text-sm text-white focus:ring-2 focus:ring-blue-500/50 focus:outline-none"
                        placeholder="john@example.com"
                      />
                    </div>
                  )}

                  {/* Subject */}
                  <div>
                    <label className="text-sm text-neutral-400 mb-1 block">Subject *</label>
                    <input
                      type="text"
                      required
                      value={formData.subject}
                      onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                      className="w-full h-10 rounded-lg border border-neutral-700/50 bg-neutral-900/50 px-3 text-sm text-white focus:ring-2 focus:ring-cyan-500/50 focus:outline-none"
                      placeholder="Brief description of your issue"
                    />
                  </div>

                  {/* Category and Priority */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm text-neutral-400 mb-1 block">Category *</label>
                      <select
                        value={formData.category}
                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                        className="w-full h-10 rounded-lg border border-neutral-700/50 bg-neutral-900/50 px-3 text-sm text-white focus:ring-2 focus:ring-cyan-500/50 focus:outline-none"
                      >
                        {CATEGORIES.map(cat => (
                          <option key={cat.value} value={cat.value}>{cat.label}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-sm text-neutral-400 mb-1 block">Priority *</label>
                      <select
                        value={formData.priority}
                        onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                        className="w-full h-10 rounded-lg border border-neutral-700/50 bg-neutral-900/50 px-3 text-sm text-white focus:ring-2 focus:ring-cyan-500/50 focus:outline-none"
                      >
                        <option value="LOW">Low</option>
                        <option value="MEDIUM">Medium</option>
                        <option value="HIGH">High</option>
                        <option value="CRITICAL">Critical</option>
                      </select>
                    </div>
                  </div>

                  {/* Message */}
                  <div>
                    <label className="text-sm text-neutral-400 mb-1 block">Message *</label>
                    <textarea
                      required
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      rows={6}
                      className="w-full rounded-lg border border-neutral-700/50 bg-neutral-900/50 px-3 py-2 text-sm text-white focus:ring-2 focus:ring-cyan-500/50 focus:outline-none resize-none"
                      placeholder="Please describe your issue or question in detail..."
                    />
                    <p className="text-xs text-neutral-500 mt-1 text-right">
                      {formData.message.length}/1000 characters
                    </p>
                  </div>

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    variant="premium"
                    className="w-full h-11"
                    disabled={status === "submitting"}
                  >
                    {status === "submitting" ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating Ticket...
                      </>
                    ) : (
                      <>
                        {selectedChannelData && <selectedChannelData.icon className="mr-2 h-4 w-4" />}
                        Create Ticket via {selectedChannelData?.name}
                      </>
                    )}
                  </Button>

                  <p className="text-xs text-center text-neutral-500">
                    By submitting, you agree to our{" "}
                    <Link href="/privacy" className="text-cyan-400 hover:underline">Privacy Policy</Link>
                  </p>
                </form>
              </CardContent>
            </Card>
          </div>
        )}
      </motion.div>
    </div>
  )
}
