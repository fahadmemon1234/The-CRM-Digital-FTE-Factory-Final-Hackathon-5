"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { CheckCircle, Loader2, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

export default function TestAPIPage() {
  const [apiStatus, setApiStatus] = useState<"checking" | "connected" | "error">("checking")
  const [message, setMessage] = useState("")

  const testAPI = async () => {
    setApiStatus("checking")
    setMessage("")
    
    try {
      console.log("🔍 Testing API connection...")
      
      const response = await fetch("http://localhost:8000/health", {
        method: "GET",
        headers: { "Content-Type": "application/json" }
      })
      
      console.log("📥 Response status:", response.status)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      console.log("✅ API Response:", data)
      
      setApiStatus("connected")
      setMessage(`API is healthy! Database: ${data.database || "connected"}`)
    } catch (error) {
      console.error("❌ Error testing API:", error)
      setApiStatus("error")
      setMessage(`Error: ${error instanceof Error ? error.message : "Cannot connect to API"}`)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#030712]">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl"
      >
        <Card className="border border-neutral-700/30 bg-neutral-900/40 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-white">API Connection Test</CardTitle>
            <CardDescription>Test if the backend API is running and accessible</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-lg bg-neutral-800/50 border border-neutral-700/50">
              <h3 className="text-sm font-medium text-neutral-300 mb-2">Instructions:</h3>
              <ol className="text-sm text-neutral-400 space-y-1">
                <li>1. Open a new terminal</li>
                <li>2. Run: <code className="bg-neutral-900 px-2 py-1 rounded">cd D:\GIAIC\Hackathon 5</code></li>
                <li>3. Run: <code className="bg-neutral-900 px-2 py-1 rounded">start-api.bat</code></li>
                <li>4. Wait for "Application startup complete"</li>
                <li>5. Click "Test Connection" button below</li>
              </ol>
            </div>

            <Button 
              onClick={testAPI} 
              variant="premium" 
              className="w-full h-12"
              disabled={apiStatus === "checking"}
            >
              {apiStatus === "checking" ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Checking...
                </>
              ) : (
                "Test Connection"
              )}
            </Button>

            {apiStatus === "connected" && (
              <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-emerald-400 mt-0.5" />
                <div>
                  <p className="font-medium text-emerald-400">✓ Connection Successful!</p>
                  <p className="text-sm text-neutral-400 mt-1">{message}</p>
                </div>
              </div>
            )}

            {apiStatus === "error" && (
              <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-400 mt-0.5" />
                <div>
                  <p className="font-medium text-red-400">✗ Connection Failed</p>
                  <p className="text-sm text-neutral-400 mt-1">{message}</p>
                  <p className="text-sm text-neutral-500 mt-2">
                    Make sure the API server is running on http://localhost:8000
                  </p>
                </div>
              </div>
            )}

            <div className="pt-4 border-t border-neutral-700/50">
              <p className="text-xs text-neutral-500">
                <strong>API Endpoints:</strong><br/>
                • Health: <code className="text-cyan-400">http://localhost:8000/health</code><br/>
                • Docs: <code className="text-cyan-400">http://localhost:8000/docs</code><br/>
                • Submit: <code className="text-cyan-400">POST http://localhost:8000/support/submit</code>
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
