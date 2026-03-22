"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { CheckCircle, Loader2, ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { useRouter } from "next/navigation"
import Link from "next/link"

const CATEGORIES = [
  { value: "general", label: "General Question" },
  { value: "technical", label: "Technical Support" },
  { value: "billing", label: "Billing Inquiry" },
  { value: "bug_report", label: "Bug Report" },
  { value: "feedback", label: "Feedback" }
]

export default function SupportFormPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    category: "general",
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
      console.log("📤 Submitting form...", formData)

      // API call to backend
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/support/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      })
      
      console.log("📥 Response status:", response.status)
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Submission failed")
      }
      
      const data = await response.json()
      console.log("✅ Submission successful:", data)
      
      setTicketId(data.ticket_id)
      setStatus("success")
    } catch (err) {
      console.error("❌ Error:", err)
      setError(err instanceof Error ? err.message : "Failed to submit. Please try again.")
      setStatus("error")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#030712]">
      {/* Back Button */}
      <Link href="/" className="fixed top-4 left-4">
        <Button variant="ghost" className="text-neutral-400 hover:text-white">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Home
        </Button>
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl"
      >
        {status === "success" ? (
          <Card className="border border-emerald-500/30 bg-emerald-500/10 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="text-center">
                <CheckCircle className="h-16 w-16 text-emerald-400 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-white mb-2">Thank You!</h2>
                <p className="text-neutral-400 mb-4">Your support request has been submitted successfully.</p>
                <div className="bg-neutral-900/50 rounded-lg p-4 mb-4">
                  <p className="text-sm text-neutral-400">Your Ticket ID</p>
                  <p className="text-2xl font-mono font-bold text-white">{ticketId}</p>
                </div>
                <p className="text-sm text-neutral-400 mb-4">
                  Our AI assistant will respond to your email within 5 minutes.
                </p>
                <Button onClick={() => {
                  setStatus("idle")
                  setFormData({ name: "", email: "", subject: "", category: "general", message: "" })
                }} variant="premium">
                  Submit Another Request
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-white">Contact Support</CardTitle>
              <CardDescription>Fill out the form and our AI assistant will help you shortly.</CardDescription>
            </CardHeader>
            <CardContent>
              {error && (
                <div className="mb-4 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                  {error}
                </div>
              )}
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-sm text-neutral-400 mb-1 block">Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full h-10 rounded-lg border border-neutral-700/50 bg-neutral-900/50 px-3 text-sm text-white focus:ring-2 focus:ring-cyan-500/50 focus:outline-none"
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label className="text-sm text-neutral-400 mb-1 block">Email *</label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full h-10 rounded-lg border border-neutral-700/50 bg-neutral-900/50 px-3 text-sm text-white focus:ring-2 focus:ring-cyan-500/50 focus:outline-none"
                    placeholder="john@example.com"
                  />
                </div>
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
                <Button 
                  type="submit" 
                  variant="premium" 
                  className="w-full h-11"
                  disabled={status === "submitting"}
                >
                  {status === "submitting" ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    "Submit Support Request"
                  )}
                </Button>
                <p className="text-xs text-center text-neutral-500">
                  By submitting, you agree to our{" "}
                  <Link href="/privacy" className="text-cyan-400 hover:underline">Privacy Policy</Link>
                </p>
              </form>
            </CardContent>
          </Card>
        )}
      </motion.div>
    </div>
  )
}
