"use client"

import { motion } from "framer-motion"
import { FileText, Scale, CheckCircle, AlertCircle, ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function TermsPage() {
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
            <Scale className="h-12 w-12 text-cyan-400" />
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
              Terms of Service
            </h1>
          </div>
          <p className="text-neutral-400 text-lg max-w-2xl mx-auto">
            Please read these terms carefully before using our services.
          </p>
          <p className="text-neutral-500 text-sm mt-2">
            Last updated: March 20, 2026
          </p>
        </motion.div>

        {/* Key Points */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                    <CheckCircle className="h-5 w-5 text-green-400" />
                  </div>
                  <CardTitle className="text-base">Acceptable Use</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-neutral-400">
                  Use our services responsibly and in compliance with all laws.
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
                  <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                    <FileText className="h-5 w-5 text-blue-400" />
                  </div>
                  <CardTitle className="text-base">Service License</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-neutral-400">
                  Limited, non-exclusive, non-transferable license to use our platform.
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
                  <div className="h-10 w-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                    <AlertCircle className="h-5 w-5 text-amber-400" />
                  </div>
                  <CardTitle className="text-base">Limitations</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-neutral-400">
                  Certain restrictions apply to protect the integrity of our services.
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
              <CardTitle className="text-xl text-white">1. Agreement to Terms</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>
                By accessing or using TechCorp's services, you agree to be bound by these Terms of Service and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using or accessing this site.
              </p>
            </CardContent>
          </Card>

          {/* Section 2 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">2. Use License</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>
                Permission is granted to temporarily access the materials (information or software) on TechCorp's website for personal, non-commercial transitory viewing only. This is the grant of a license, not a transfer of title.
              </p>
              <p className="text-neutral-400 text-sm">
                Under this license, you may not:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 text-neutral-400">
                <li>Modify or copy the materials</li>
                <li>Use the materials for any commercial purpose</li>
                <li>Attempt to decompile or reverse engineer any software</li>
                <li>Remove any copyright or proprietary notations</li>
                <li>Transfer the materials to another person</li>
              </ul>
            </CardContent>
          </Card>

          {/* Section 3 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">3. Disclaimer</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>
                The materials on TechCorp's website are provided on an 'as is' basis. TechCorp makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property.
              </p>
            </CardContent>
          </Card>

          {/* Section 4 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">4. Limitations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>
                In no event shall TechCorp or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on TechCorp's website.
              </p>
            </CardContent>
          </Card>

          {/* Section 5 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">5. Accuracy of Materials</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>
                The materials appearing on TechCorp's website could include technical, typographical, or photographic errors. TechCorp does not warrant that any of the materials on its website are accurate, complete or current. TechCorp may make changes to the materials contained on its website at any time without notice.
              </p>
            </CardContent>
          </Card>

          {/* Section 6 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">6. Links</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>
                TechCorp has not reviewed all of the sites linked to its website and is not responsible for the contents of any such linked site. The inclusion of any link does not imply endorsement by TechCorp of the site. Use of any such linked website is at the user's own risk.
              </p>
            </CardContent>
          </Card>

          {/* Section 7 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">7. Modifications</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>
                TechCorp may revise these terms of service for its website at any time without notice. By using this website you are agreeing to be bound by the then current version of these terms of service.
              </p>
            </CardContent>
          </Card>

          {/* Section 8 */}
          <Card className="border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-xl text-white">8. Governing Law</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-neutral-300">
              <p>
                These terms and conditions are governed by and construed in accordance with the laws and you irrevocably submit to the exclusive jurisdiction of the courts in that location.
              </p>
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
          <p className="text-neutral-400 text-sm mb-4">
            By using our services, you acknowledge that you have read and understood these terms.
          </p>
          <Link href="/">
            <Button variant="premium" className="h-11 px-8">
              Accept and Continue
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
