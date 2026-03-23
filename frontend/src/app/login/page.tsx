"use client"

import { useState, Suspense } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  CheckCircle,
  Github,
  Chrome,
  Sparkles,
  Zap,
  Shield,
  Users
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"
import { useAuth } from "@/contexts/auth-context"
import toast from "react-hot-toast"

function LoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { login: authLogin } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate email
    if (!email || !email.includes('@')) {
      toast.error('Please enter a valid email address')
      return
    }
    
    // Validate password
    if (!password || password.length < 6) {
      toast.error('Password must be at least 6 characters')
      return
    }

    setIsLoading(true)

    try {
      await authLogin({ email, password })
      // Redirect handled by auth context
    } catch (err: any) {
      // Error toast already shown by auth context
    } finally {
      setIsLoading(false)
    }
  }

  // Get redirect message from URL params
  const expired = searchParams.get('expired')
  const registered = searchParams.get('registered')
  
  const redirectMessage = expired
    ? "Your session has expired. Please login again."
    : registered
    ? "Account created successfully! Please login with your credentials."
    : null

  const features = [
    { icon: Zap, text: "2.4min Avg Response", color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20" },
    { icon: Shield, text: "99.9% Uptime SLA", color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20" },
    { icon: Users, text: "5,000+ Customers", color: "text-purple-400", bg: "bg-purple-500/10", border: "border-purple-500/20" }
  ]

  return (
    <div className="min-h-screen flex items-center justify-center p-3 sm:p-4 md:p-6 lg:p-8 bg-[#030712] relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 90, 0],
            opacity: [0.3, 0.5, 0.3]
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute top-0 left-1/4 w-48 sm:w-64 md:w-80 lg:w-96 h-48 sm:h-64 md:h-80 lg:h-96 bg-blue-500/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            rotate: [0, -90, 0],
            opacity: [0.2, 0.4, 0.2]
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear",
            delay: 2
          }}
          className="absolute bottom-0 right-1/4 w-48 sm:w-64 md:w-80 lg:w-96 h-48 sm:h-64 md:h-80 lg:h-96 bg-purple-500/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.1, 0.2, 0.1]
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "linear",
            delay: 4
          }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] sm:w-[400px] md:w-[500px] lg:w-[600px] h-[300px] sm:h-[400px] md:h-[500px] lg:h-[600px] bg-indigo-500/10 rounded-full blur-3xl"
        />
      </div>

      {/* Grid Pattern Overlay */}
      <div className="fixed inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:32px_32px] sm:bg-[size:64px_64px] pointer-events-none" />

      <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-4 sm:gap-6 md:gap-8 relative z-10">
        {/* Left Side - Branding */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="hidden lg:flex flex-col justify-center space-y-6 md:space-y-8"
        >
          <div className="space-y-4">
            <motion.div
              className="flex items-center gap-2 sm:gap-3"
              whileHover={{ scale: 1.02 }}
            >
              <div className="h-10 w-10 sm:h-12 sm:w-12 rounded-xl bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center shadow-lg glow-blue">
                <span className="text-xl sm:text-2xl font-bold text-white">TC</span>
              </div>
              <span className="text-2xl sm:text-3xl font-bold gradient-text">TechCorp</span>
            </motion.div>

            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold leading-tight">
              <span className="gradient-text">AI-Powered</span> Customer Success
            </h1>
            <p className="text-base sm:text-lg md:text-xl text-muted-foreground">
              Transform your customer support with intelligent automation.
              24/7 support, instant responses, and 98% cost savings.
            </p>
          </div>

          <div className="space-y-3 sm:space-y-4">
            {features.map((feature, index) => (
              <motion.div
                key={feature.text}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                whileHover={{ x: 8, scale: 1.02 }}
                className={`flex items-center gap-3 sm:gap-4 p-3 sm:p-4 rounded-xl sm:rounded-2xl ${feature.bg} border ${feature.border} backdrop-blur-xl transition-all duration-300 cursor-pointer`}
              >
                <div className={`h-10 w-10 sm:h-12 sm:w-12 rounded-xl sm:rounded-2xl ${feature.bg} flex items-center justify-center border ${feature.border}`}>
                  <feature.icon className={`h-5 w-5 sm:h-6 sm:w-6 ${feature.color}`} />
                </div>
                <div>
                  <p className="font-semibold text-sm sm:text-base">{feature.text}</p>
                  <p className="text-xs sm:text-sm text-muted-foreground/80">Enterprise-grade quality</p>
                </div>
              </motion.div>
            ))}
          </div>

          <motion.div
            className="flex items-center gap-3 sm:gap-4 pt-6 sm:pt-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1 }}
          >
            <div className="flex -space-x-2 sm:-space-x-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3, delay: 1.2 + i * 0.1 }}
                  whileHover={{ scale: 1.2, zIndex: 10 }}
                  className="h-8 w-8 sm:h-10 sm:w-10 rounded-full border-2 border-white/20 bg-gradient-to-br from-blue-400 to-indigo-600 flex items-center justify-center text-xs font-bold shadow-lg"
                >
                  {String.fromCharCode(64 + i)}
                </motion.div>
              ))}
            </div>
            <div>
              <p className="font-semibold text-sm sm:text-base">500K+ Daily Users</p>
              <div className="flex items-center gap-1 text-xs sm:text-sm text-muted-foreground">
                <div className="flex -space-x-1">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <span key={i} className="text-yellow-400 drop-shadow-lg text-xs sm:text-sm">★</span>
                  ))}
                </div>
                <span>4.9/5 rating</span>
              </div>
            </div>
          </motion.div>
        </motion.div>

        {/* Right Side - Login Form */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="flex items-center justify-center p-2 sm:p-0"
        >
          <Card className="w-full max-w-md border-white/10 bg-white/[0.03] backdrop-blur-xl shadow-2xl mx-2 sm:mx-0">
            <CardHeader className="space-y-2 sm:space-y-3 pb-3 sm:pb-4">
              <div className="lg:hidden flex items-center gap-2 mb-2">
                <div className="h-9 w-9 sm:h-10 sm:w-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg">
                  <span className="text-lg sm:text-xl font-bold text-white">TC</span>
                </div>
                <span className="text-xl sm:text-2xl font-bold gradient-text">TechCorp</span>
              </div>
              <CardTitle className="text-xl sm:text-2xl font-bold">Welcome back</CardTitle>
              <CardDescription className="text-xs sm:text-sm">
                Enter your credentials to access your account
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 sm:space-y-4">
              {/* Session Expired Message */}
              <AnimatePresence>
                {redirectMessage && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm flex items-center gap-2"
                  >
                    <CheckCircle className="h-4 w-4" />
                    {redirectMessage}
                  </motion.div>
                )}
              </AnimatePresence>

              <form onSubmit={handleLogin} className="space-y-3 sm:space-y-4">
                <div className="space-y-1.5 sm:space-y-2">
                  <label className="text-xs sm:text-sm font-medium">Email</label>
                  <div className="relative">
                    <Mail className="absolute left-2.5 sm:left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      type="email"
                      placeholder="name@company.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-9 sm:pl-10 h-11 sm:h-12 text-sm sm:text-base"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-1.5 sm:space-y-2">
                  <label className="text-xs sm:text-sm font-medium">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-2.5 sm:left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-9 sm:pl-10 pr-9 sm:pr-10 h-11 sm:h-12 text-sm sm:text-base"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-2.5 sm:right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs sm:text-sm">
                  <label className="flex items-center gap-1.5 sm:gap-2 cursor-pointer">
                    <input type="checkbox" className="rounded border-white/20 bg-white/5 h-3.5 w-3.5 sm:h-4 sm:w-4" />
                    <span>Remember me</span>
                  </label>
                  <Link href="/forgot-password" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
                    Forgot password?
                  </Link>
                </div>

                <Button
                  type="submit"
                  variant="premium"
                  className="w-full h-11 sm:h-12 text-sm sm:text-base"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="h-4 w-4 sm:h-5 sm:w-5 border-2 border-white border-t-transparent rounded-full"
                    />
                  ) : (
                    <>
                      Sign In
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </Button>
              </form>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white/10" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-[#030712] px-2 text-muted-foreground">Or continue with</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2.5 sm:gap-3">
                <Button variant="outline" className="h-10 sm:h-12 text-xs sm:text-base">
                  <Chrome className="h-3.5 sm:h-4 w-3.5 sm:w-4 mr-1.5 sm:mr-2" />
                  Google
                </Button>
                <Button variant="outline" className="h-10 sm:h-12 text-xs sm:text-base">
                  <Github className="h-3.5 sm:h-4 w-3.5 sm:w-4 mr-1.5 sm:mr-2" />
                  GitHub
                </Button>
              </div>
            </CardContent>
            <CardFooter className="flex flex-col space-y-3 sm:space-y-4 pt-2 sm:pt-0">
              <p className="text-xs sm:text-sm text-center text-muted-foreground">
                Don&apos;t have an account?{" "}
                <Link href="/signup" className="text-blue-400 hover:text-blue-300 font-medium transition-colors text-xs sm:text-sm">
                  Create account
                </Link>
              </p>
              <p className="text-[10px] sm:text-xs text-center text-muted-foreground/60">
                By signing in, you agree to our{" "}
                <Link href="/terms" className="underline hover:text-foreground transition-colors">
                  Terms of Service
                </Link>{" "}
                and{" "}
                <Link href="/privacy" className="underline hover:text-foreground transition-colors">
                  Privacy Policy
                </Link>
              </p>
            </CardFooter>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto"></div>
          <p className="text-muted-foreground mt-4">Loading...</p>
        </div>
      </div>
    }>
      <LoginForm />
    </Suspense>
  )
}