"use client"

import { motion } from "framer-motion"
import { Shield, Lock, Eye, Database, Globe, ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-[#030712]">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3]
          }}
          transition={{ duration: 20, repeat: Infinity }}
          className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.2, 0.4, 0.2]
          }}
          transition={{ duration: 25, repeat: Infinity }}
          className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
        />
      </div>

      {/* Header */}
      <header className="border-b border-neutral-800/50 bg-neutral-900/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-cyan-600 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg">
                <span className="text-xl font-bold text-white">TC</span>
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
                TechCorp
              </span>
            </div>
          </Link>
          <Link href="/">
            <Button variant="outline" className="border-neutral-700 hover:bg-neutral-800">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Button>
          </Link>
        </div>
      </header>

      {/* Content */}
      <main className="relative max-w-5xl mx-auto px-4 py-12">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Shield className="h-12 w-12 text-cyan-400" />
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
              Privacy Policy
            </h1>
          </div>
          <p className="text-neutral-400 text-lg max-w-2xl mx-auto">
            Your privacy is important to us. This policy explains how we collect, use, and protect your personal information.
          </p>
          <p className="text-neutral-500 text-sm mt-2">
            Last updated: March 20, 2026
          </p>
        </motion.div>

        {/* Privacy Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                    <Database className="h-5 w-5 text-blue-400" />
                  </div>
                  <CardTitle className="text-base">Data Collection</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-neutral-400">
                  We collect information you provide directly, including name, email, and support tickets.
                </CardDescription>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                    <Lock className="h-5 w-5 text-green-400" />
                  </div>
                  <CardTitle className="text-base">Data Security</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-neutral-400">
                  We implement industry-standard security measures to protect your personal information.
                </CardDescription>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                    <Eye className="h-5 w-5 text-purple-400" />
                  </div>
                  <CardTitle className="text-base">Transparency</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-neutral-400">
                  We're transparent about our data practices and never sell your personal information.
                </CardDescription>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Main Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-8"
        >
          {/* Section 1 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">1. Information We Collect</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>
                We collect information that you provide directly to us, including:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Name and email address</li>
                <li>Company name and contact information</li>
                <li>Support tickets and messages</li>
                <li>Communication preferences</li>
                <li>Usage data and analytics</li>
              </ul>
            </CardContent>
          </Card>

          {/* Section 2 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">2. How We Use Your Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>We use the information we collect to:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Provide, maintain, and improve our services</li>
                <li>Process your support requests and respond to inquiries</li>
                <li>Send you technical notices and support messages</li>
                <li>Communicate with you about products, services, and events</li>
                <li>Monitor and analyze trends, usage, and activities</li>
                <li>Detect, investigate, and prevent fraudulent transactions</li>
              </ul>
            </CardContent>
          </Card>

          {/* Section 3 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">3. Data Sharing</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>
                We do not sell, trade, or rent your personal information to third parties. We may share your information only in the following situations:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>With your consent or at your direction</li>
                <li>With service providers who perform services on our behalf</li>
                <li>To comply with legal obligations</li>
                <li>To protect our rights and prevent fraud</li>
              </ul>
            </CardContent>
          </Card>

          {/* Section 4 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">4. Data Retention</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>
                We retain your personal information for as long as necessary to provide our services and comply with legal obligations. You can request deletion of your data at any time by contacting us.
              </p>
            </CardContent>
          </Card>

          {/* Section 5 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">5. Your Rights</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>You have the right to:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Access your personal information</li>
                <li>Correct inaccurate data</li>
                <li>Request deletion of your data</li>
                <li>Opt-out of marketing communications</li>
                <li>Export your data in a portable format</li>
              </ul>
            </CardContent>
          </Card>

          {/* Section 6 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">6. Contact Us</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>
                If you have questions about this Privacy Policy, please contact us at:
              </p>
              <div className="ml-4 space-y-2">
                <p className="text-neutral-400">
                  <strong>Email:</strong> privacy@techcorp.com
                </p>
                <p className="text-neutral-400">
                  <strong>Address:</strong> 123 Tech Street, San Francisco, CA 94105
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Footer CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-12 text-center"
        >
          <div className="flex items-center justify-center gap-2 text-neutral-400 mb-4">
            <Globe className="h-5 w-5" />
            <span className="text-sm">Your data is protected with industry-standard security</span>
          </div>
          <Link href="/">
            <Button variant="premium" className="h-11 px-8">
              Get Started
            </Button>
          </Link>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="border-t border-neutral-800/50 bg-neutral-900/80 backdrop-blur-xl mt-12">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-cyan-600 to-indigo-600 flex items-center justify-center">
                <span className="text-sm font-bold text-white">TC</span>
              </div>
              <span className="text-sm text-neutral-400">
                © 2026 TechCorp. All rights reserved.
              </span>
            </div>
            <div className="flex items-center gap-6">
              <Link href="/privacy" className="text-sm text-neutral-400 hover:text-neutral-200">
                Privacy Policy
              </Link>
              <Link href="/terms" className="text-sm text-neutral-400 hover:text-neutral-200">
                Terms of Service
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
