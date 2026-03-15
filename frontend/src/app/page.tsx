"use client"

import { motion } from "framer-motion"
import {
  ArrowRight,
  CheckCircle,
  Zap,
  Shield,
  Globe,
  MessageSquare,
  Mail,
  Smartphone,
  BarChart3,
  Clock,
  DollarSign,
  Play,
  Sparkles,
  Stars
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import Link from "next/link"

const features = [
  {
    icon: Zap,
    title: "Instant Responses",
    description: "AI-powered responses in under 3 seconds, 24/7/365 availability",
    gradient: "from-blue-500 to-cyan-500"
  },
  {
    icon: MessageSquare,
    title: "Multi-Channel Support",
    description: "Email, WhatsApp, and Web Form integration in one platform",
    gradient: "from-purple-500 to-pink-500"
  },
  {
    icon: BarChart3,
    title: "Smart Analytics",
    description: "Real-time insights, sentiment analysis, and performance metrics",
    gradient: "from-emerald-500 to-teal-500"
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description: "SOC 2 Type II, GDPR compliant, end-to-end encryption",
    gradient: "from-amber-500 to-orange-500"
  },
  {
    icon: Globe,
    title: "Global Scale",
    description: "Support customers in 80+ countries with multi-language AI",
    gradient: "from-indigo-500 to-blue-500"
  },
  {
    icon: Clock,
    title: "99.9% Uptime",
    description: "Enterprise-grade reliability with automatic failover",
    gradient: "from-rose-500 to-red-500"
  }
]

const channels = [
  {
    icon: Mail,
    name: "Email",
    description: "Gmail integration with Pub/Sub notifications",
    color: "from-blue-500 to-cyan-500"
  },
  {
    icon: Smartphone,
    name: "WhatsApp",
    description: "Twilio WhatsApp Business API integration",
    color: "from-green-500 to-emerald-500"
  },
  {
    icon: MessageSquare,
    name: "Web Form",
    description: "Embedded support form for your website",
    color: "from-purple-500 to-pink-500"
  }
]

const pricing = [
  {
    name: "Starter",
    price: "$29",
    description: "Perfect for small teams",
    features: [
      "Up to 1,000 tickets/month",
      "Email support channel",
      "Basic AI responses",
      "5GB storage",
      "Email support",
      "5 integrations"
    ],
    cta: "Start Free Trial",
    popular: false
  },
  {
    name: "Growth",
    price: "$79",
    description: "For growing businesses",
    features: [
      "Up to 10,000 tickets/month",
      "All 3 communication channels",
      "Advanced AI with sentiment analysis",
      "100GB storage",
      "Priority support",
      "Unlimited integrations",
      "Custom analytics"
    ],
    cta: "Start Free Trial",
    popular: true
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For large organizations",
    features: [
      "Unlimited tickets",
      "All channels + custom integrations",
      "Custom AI model training",
      "Unlimited storage",
      "24/7 dedicated support",
      "SSO/SAML",
      "Advanced security & compliance",
      "SLA guarantees"
    ],
    cta: "Contact Sales",
    popular: false
  }
]

const stats = [
  { value: "5,000+", label: "Customers Worldwide" },
  { value: "500K+", label: "Daily Active Users" },
  { value: "10M+", label: "Tasks Managed Monthly" },
  { value: "98%", label: "Cost Savings" }
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: [0.4, 0, 0.2, 1] as const
    }
  }
}

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#030712] overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/5 rounded-full blur-3xl animate-pulse-glow" />
      </div>

      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-white/10 glass-strong">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3"
          >
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center shadow-lg glow-blue">
              <span className="text-white font-bold text-lg">TC</span>
            </div>
            <span className="text-xl font-bold gradient-text">TechCorp</span>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="hidden md:flex items-center gap-8"
          >
            <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-all duration-300">Features</a>
            <a href="#channels" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-all duration-300">Channels</a>
            <a href="#pricing" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-all duration-300">Pricing</a>
            <Link href="/support" className="text-sm font-medium text-cyan-400 hover:text-cyan-300 transition-all duration-300">Support</Link>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="flex items-center gap-3"
          >
            <a href="/login" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-all duration-300">
              <Button variant="ghost">Sign In</Button>
            </a>
            <a href="/login" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-all duration-300">
              <Button variant="premium">
                Start Free Trial
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </a>
          </motion.div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 lg:py-32 relative">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="text-center max-w-5xl mx-auto"
        >
          <motion.div variants={itemVariants} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-sm font-medium mb-6 backdrop-blur-xl">
            <Sparkles className="h-4 w-4" />
            AI-Powered Customer Success FTE
          </motion.div>
          
          <motion.h1 
            variants={itemVariants}
            className="text-5xl lg:text-7xl font-bold tracking-tight mb-6"
          >
            Transform Customer Support with{" "}
            <span className="gradient-text glow-text">
              Intelligent AI
            </span>
          </motion.h1>
          
          <motion.p 
            variants={itemVariants}
            className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto"
          >
            Replace traditional support teams with an AI Digital FTE that works 24/7,
            responds in seconds, and costs 98% less than human agents.
          </motion.p>
          
          <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/login">
              <Button variant="premium" size="lg" className="text-base px-8">
                Start 14-Day Free Trial
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
            <Link href="/support">
              <Button variant="outline" size="lg" className="text-base px-8">
                <MessageSquare className="h-4 w-4 mr-2" />
                Contact Support
              </Button>
            </Link>
          </motion.div>
          
          <motion.p variants={itemVariants} className="text-sm text-muted-foreground mt-4">
            No credit card required • Setup in 5 minutes • Cancel anytime
          </motion.p>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-20"
        >
          {stats.map((stat) => (
            <motion.div 
              key={stat.label}
              whileHover={{ scale: 1.05 }}
              className="text-center p-6 rounded-2xl glass-light card-hover"
            >
              <div className="text-4xl lg:text-5xl font-bold gradient-text mb-2">
                {stat.value}
              </div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Cost Comparison */}
      <section className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm font-medium mb-6 backdrop-blur-xl">
            <DollarSign className="h-4 w-4" />
            Unbeatable ROI
          </div>
          <h2 className="text-4xl font-bold mb-4">See How Much You Can Save</h2>
          <p className="text-xl text-muted-foreground">
            Compare costs with traditional support solutions
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {[
            {
              name: "Human Agent (US)",
              cost: "$75,000",
              period: "/year",
              gradient: "from-red-500 to-orange-500",
              items: ["8 hours/day", "5 days/week", "Minutes to hours response", "Limited concurrency"]
            },
            {
              name: "Human Agent (Offshore)",
              cost: "$25,000",
              period: "/year",
              gradient: "from-amber-500 to-yellow-500",
              items: ["24/7 with shifts", "Variable quality", "Minutes to hours response", "Limited concurrency"]
            },
            {
              name: "TechCorp AI FTE",
              cost: "<$1,000",
              period: "/year",
              gradient: "from-green-500 to-emerald-500",
              popular: true,
              items: ["24/7/365 availability", "<3 second response", "Unlimited concurrency", "98% cost savings"]
            }
          ].map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ scale: plan.popular ? 1.05 : 1.02 }}
            >
              <Card className={`relative h-full ${plan.popular ? 'border-emerald-500/50 glow-emerald' : ''}`}>
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-emerald-500 to-green-500 text-white text-sm font-medium rounded-full shadow-lg">
                    Most Popular
                  </div>
                )}
                <CardContent className="pt-6">
                  <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${plan.gradient} mb-4 shadow-lg`}>
                    <DollarSign className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{plan.name}</h3>
                  <div className="mb-4">
                    <span className="text-4xl font-bold">{plan.cost}</span>
                    <span className="text-muted-foreground">{plan.period}</span>
                  </div>
                  <ul className="space-y-2">
                    {plan.items.map((item) => (
                      <li key={item} className="flex items-center gap-2 text-sm">
                        <CheckCircle className="h-4 w-4 text-emerald-500 shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-sm font-medium mb-6 backdrop-blur-xl">
            <Stars className="h-4 w-4" />
            Powerful Features
          </div>
          <h2 className="text-4xl font-bold mb-4">Everything You Need</h2>
          <p className="text-xl text-muted-foreground">
            Deliver exceptional customer support at scale
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ scale: 1.02, y: -4 }}
            >
              <Card className="h-full card-hover group">
                <CardContent className="pt-6">
                  <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${feature.gradient} mb-4 shadow-lg group-hover:shadow-xl transition-shadow`}>
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Channels */}
      <section id="channels" className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-sm font-medium mb-6 backdrop-blur-xl">
            <MessageSquare className="h-4 w-4" />
            Multi-Channel Support
          </div>
          <h2 className="text-4xl font-bold mb-4">Meet Customers Where They Are</h2>
          <p className="text-xl text-muted-foreground">
            Seamless integration across all communication channels
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {channels.map((channel, index) => (
            <motion.div
              key={channel.name}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ scale: 1.05, y: -8 }}
              className="text-center"
            >
              <Card className="card-hover">
                <CardContent className="pt-6">
                  <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-br ${channel.color} mb-4 shadow-lg`}>
                    <channel.icon className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{channel.name}</h3>
                  <p className="text-muted-foreground">{channel.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-sm font-medium mb-6 backdrop-blur-xl">
            <DollarSign className="h-4 w-4" />
            Simple Pricing
          </div>
          <h2 className="text-4xl font-bold mb-4">Choose Your Plan</h2>
          <p className="text-xl text-muted-foreground">
            Transparent pricing with no hidden fees
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {pricing.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ scale: plan.popular ? 1.05 : 1.02 }}
            >
              <Card className={`relative h-full ${plan.popular ? 'border-indigo-500/50 glow-blue' : ''}`}>
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-sm font-medium rounded-full shadow-lg">
                    Most Popular
                  </div>
                )}
                <CardContent className="pt-6">
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <p className="text-muted-foreground mb-4">{plan.description}</p>
                  <div className="mb-6">
                    {plan.price === "Custom" ? (
                      <span className="text-5xl font-bold">{plan.price}</span>
                    ) : (
                      <>
                        <span className="text-5xl font-bold">{plan.price}</span>
                        <span className="text-muted-foreground">/month</span>
                      </>
                    )}
                  </div>
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-center gap-2 text-sm">
                        <CheckCircle className="h-4 w-4 text-emerald-500 shrink-0" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <Button
                    variant={plan.popular ? "premium" : "outline"}
                    className="w-full"
                  >
                    {plan.cta}
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <Card className="border-0 bg-gradient-to-br from-blue-600/20 via-indigo-600/20 to-purple-600/20 backdrop-blur-xl overflow-hidden relative">
            <CardContent className="py-20 px-8 text-center relative z-10">
              <h2 className="text-4xl lg:text-5xl font-bold mb-6">
                Ready to Transform Your Support?
              </h2>
              <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
                Join 5,000+ companies delivering exceptional customer experiences with TechCorp AI
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link href="/login">
                  <Button variant="premium" size="lg" className="text-base px-8">
                    Start 14-Day Free Trial
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </Link>
                <Button variant="outline" size="lg" className="text-base px-8">
                  Schedule Demo
                </Button>
              </div>
            </CardContent>
            <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
          </Card>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 glass-strong">
        <div className="container mx-auto px-4 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">TC</span>
                </div>
                <span className="text-lg font-bold gradient-text">TechCorp</span>
              </div>
              <p className="text-sm text-muted-foreground">
                AI-powered customer success platform for modern businesses.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/support" className="hover:text-cyan-400 transition-colors">Contact Support</Link></li>
                <li><a href="#features" className="hover:text-foreground transition-colors">Features</a></li>
                <li><a href="#pricing" className="hover:text-foreground transition-colors">Pricing</a></li>
                <li><a href="#docs" className="hover:text-foreground transition-colors">Documentation</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#about" className="hover:text-foreground transition-colors">About</a></li>
                <li><a href="#blog" className="hover:text-foreground transition-colors">Blog</a></li>
                <li><a href="#careers" className="hover:text-foreground transition-colors">Careers</a></li>
                <li><a href="#contact" className="hover:text-foreground transition-colors">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#privacy" className="hover:text-foreground transition-colors">Privacy</a></li>
                <li><a href="#terms" className="hover:text-foreground transition-colors">Terms</a></li>
                <li><a href="#security" className="hover:text-foreground transition-colors">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/10 mt-12 pt-8 text-center text-sm text-muted-foreground">
            <p>&copy; 2025 TechCorp. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
