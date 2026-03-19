"use client"

import { motion } from "framer-motion"
import {
  Mail,
  Smartphone,
  MessageSquare,
  CheckCircle2,
  Zap,
  Settings,
  Bell,
  Link as LinkIcon,
  Globe,
  Phone
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

const channels = [
  {
    name: "Email",
    icon: Mail,
    status: "active",
    description: "Gmail integration with Pub/Sub notifications",
    color: "#3b82f6",
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/30",
    textColor: "text-blue-400",
    stats: {
      tickets: 1247,
      responseTime: "2.4m",
      satisfaction: 94
    },
    features: [
      "Real-time notifications",
      "Auto-ticket creation",
      "Thread tracking",
      "Attachment support"
    ],
    config: {
      provider: "Gmail API",
      webhook: "Configured",
      lastSync: "2 minutes ago"
    }
  },
  {
    name: "WhatsApp",
    icon: Smartphone,
    status: "active",
    description: "Twilio WhatsApp Business API integration",
    color: "#22c55e",
    bgColor: "bg-green-500/10",
    borderColor: "border-green-500/30",
    textColor: "text-green-400",
    stats: {
      tickets: 892,
      responseTime: "1.8m",
      satisfaction: 96
    },
    features: [
      "Instant messaging",
      "Media support",
      "Read receipts",
      "Quick replies"
    ],
    config: {
      provider: "Twilio",
      webhook: "Configured",
      lastSync: "1 minute ago"
    }
  },
  {
    name: "Web Form",
    icon: MessageSquare,
    status: "active",
    description: "Embedded support form for your website",
    color: "#8b5cf6",
    bgColor: "bg-purple-500/10",
    borderColor: "border-purple-500/30",
    textColor: "text-purple-400",
    stats: {
      tickets: 708,
      responseTime: "3.2m",
      satisfaction: 92
    },
    features: [
      "Customizable form",
      "File attachments",
      "Spam protection",
      "Auto-responders"
    ],
    config: {
      provider: "FastAPI",
      webhook: "N/A",
      lastSync: "Real-time"
    }
  }
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
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

export default function ChannelsPage() {
  // Display all channels (no tabs)
  const displayChannels = channels

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-6"
    >
      {/* Page Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white lg:text-3xl">
            Channels
          </h1>
          <p className="mt-0.5 text-xs text-neutral-400 lg:text-sm">
            Manage your communication channels
          </p>
        </div>
        <Button variant="premium" className="h-9 text-sm">
          <Settings className="mr-2 h-4 w-4" />
          Configure All
        </Button>
      </motion.div>

      {/* Channel Cards */}
      <motion.div variants={itemVariants} className="grid gap-6 lg:grid-cols-3">
        {displayChannels.map((channel) => {
          const Icon = channel.icon
          return (
            <motion.div
              key={channel.name}
              whileHover={{ scale: 1.02, y: -4 }}
              whileTap={{ scale: 0.98 }}
            >
              <Card className={`border ${channel.borderColor} ${channel.bgColor} backdrop-blur-md`}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`rounded-lg ${channel.bgColor} p-2.5`}>
                        <Icon className={`h-6 w-6 ${channel.textColor}`} />
                      </div>
                      <div>
                        <CardTitle className="text-lg font-semibold text-white">
                          {channel.name}
                        </CardTitle>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="success" className="text-xs bg-emerald-500/10 border-emerald-500/30 text-emerald-400">
                            <CheckCircle2 className="mr-1 h-3 w-3" />
                            {channel.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                  <CardDescription className="text-neutral-400">
                    {channel.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-2">
                    <div className="rounded-lg bg-neutral-900/50 p-2 text-center">
                      <p className="text-xs text-neutral-400">Tickets</p>
                      <p className="text-lg font-bold text-white">{channel.stats.tickets}</p>
                    </div>
                    <div className="rounded-lg bg-neutral-900/50 p-2 text-center">
                      <p className="text-xs text-neutral-400">Response</p>
                      <p className="text-lg font-bold text-white">{channel.stats.responseTime}</p>
                    </div>
                    <div className="rounded-lg bg-neutral-900/50 p-2 text-center">
                      <p className="text-xs text-neutral-400">Satisfaction</p>
                      <p className="text-lg font-bold text-white">{channel.stats.satisfaction}%</p>
                    </div>
                  </div>

                  {/* Features */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-neutral-400">
                      <Zap className="h-3.5 w-3.5" />
                      <span>Features</span>
                    </div>
                    <ul className="space-y-1.5">
                      {channel.features.map((feature) => (
                        <li key={feature} className="flex items-center gap-2 text-xs text-neutral-300">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Config */}
                  <div className="rounded-lg border border-neutral-700/50 bg-neutral-900/50 p-3 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-neutral-400">Provider</span>
                      <span className="text-neutral-200">{channel.config.provider}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-neutral-400">Webhook</span>
                      <span className="text-emerald-400">{channel.config.webhook}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-neutral-400">Last Sync</span>
                      <span className="text-neutral-200">{channel.config.lastSync}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button variant="outline" className="flex-1 h-9 text-xs border-neutral-700/50 hover:bg-neutral-800/50">
                      <Settings className="mr-2 h-3.5 w-3.5" />
                      Settings
                    </Button>
                    <Button variant="ghost" className="h-9 w-9 p-0 hover:bg-neutral-800/50">
                      <Bell className="h-4 w-4 text-neutral-400" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </motion.div>

      {/* Integration Guide */}
      <motion.div variants={itemVariants}>
        <Card className="border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-md">
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-cyan-500/10 p-2">
                <LinkIcon className="h-4 w-4 text-cyan-400" />
              </div>
              <div>
                <CardTitle className="text-base font-semibold text-white">Integration Guide</CardTitle>
                <CardDescription className="text-xs text-neutral-400">Quick setup instructions for each channel</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              {/* Email Setup */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10">
                    <Mail className="h-4 w-4 text-blue-400" />
                  </div>
                  <h3 className="text-sm font-semibold text-white">Email Setup</h3>
                </div>
                <ol className="space-y-2 text-xs text-neutral-400">
                  <li className="flex gap-2">
                    <span className="font-semibold text-neutral-300">1.</span>
                    <span>Enable Gmail API in Google Cloud Console</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-semibold text-neutral-300">2.</span>
                    <span>Create service account and download JSON</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-semibold text-neutral-300">3.</span>
                    <span>Set up Pub/Sub topic for notifications</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-semibold text-neutral-300">4.</span>
                    <span>Add credentials to environment variables</span>
                  </li>
                </ol>
              </div>

              {/* WhatsApp Setup */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-green-500/10">
                    <Phone className="h-4 w-4 text-green-400" />
                  </div>
                  <h3 className="text-sm font-semibold text-white">WhatsApp Setup</h3>
                </div>
                <ol className="space-y-2 text-xs text-neutral-400">
                  <li className="flex gap-2">
                    <span className="font-semibold text-neutral-300">1.</span>
                    <span>Create Twilio account</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-semibold text-neutral-300">2.</span>
                    <span>Enable WhatsApp sandbox</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-semibold text-neutral-300">3.</span>
                    <span>Configure webhook URL</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-semibold text-neutral-300">4.</span>
                    <span>Add account SID and auth token</span>
                  </li>
                </ol>
              </div>

              {/* Web Form Setup */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/10">
                    <Globe className="h-4 w-4 text-purple-400" />
                  </div>
                  <h3 className="text-sm font-semibold text-white">Web Form Setup</h3>
                </div>
                <ol className="space-y-2 text-xs text-neutral-400">
                  <li className="flex gap-2">
                    <span className="font-semibold text-neutral-300">1.</span>
                    <span>Copy the React component code</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-semibold text-neutral-300">2.</span>
                    <span>Paste into your website</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-semibold text-neutral-300">3.</span>
                    <span>Configure API endpoint</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-semibold text-neutral-300">4.</span>
                    <span>Customize styling as needed</span>
                  </li>
                </ol>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
