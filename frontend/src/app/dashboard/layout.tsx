"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  LayoutDashboard,
  Ticket,
  MessageSquare,
  BarChart3,
  Users,
  Mail,
  Menu,
  X,
  Bell,
  Search,
  LogOut,
  Sparkles,
  Radio
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Tickets", href: "/dashboard/tickets", icon: Ticket },
  { name: "Channels", href: "/dashboard/channels", icon: Radio },
  { name: "Analytics", href: "/dashboard/analytics", icon: BarChart3 },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isMounted, setIsMounted] = useState(false)
  const pathname = usePathname()
  const { user, logout } = useAuth()

  useEffect(() => {
    setIsMounted(true)
  }, [])

  if (!isMounted) {
    return null
  }

  return (
    <div className="flex h-screen overflow-hidden bg-[#030712]">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-40 w-72 border-r border-neutral-800/50 bg-neutral-900/80 backdrop-blur-xl lg:static lg:inset-auto">
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-14 items-center gap-3 border-b border-neutral-800/50 px-4">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-600 via-blue-600 to-indigo-600 shadow-lg shadow-cyan-500/20">
              <span className="text-sm font-bold text-white">TC</span>
            </div>
            <span className="text-lg font-bold bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
              TechCorp
            </span>
            <button
              onClick={() => setSidebarOpen(false)}
              className="ml-auto lg:hidden p-1 text-neutral-400 hover:text-neutral-200"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-0.5 overflow-y-auto px-2 py-4">
            {navigation.map((item) => {
              const isActive = pathname === item.href || pathname?.startsWith(item.href + '?')

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all duration-300",
                    isActive
                      ? "bg-gradient-to-r from-cyan-600/20 via-blue-600/20 to-indigo-600/20 text-cyan-400 border border-cyan-500/20 shadow-lg shadow-cyan-500/10"
                      : "text-neutral-400 hover:bg-neutral-800/50 hover:text-neutral-200"
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* Pro Banner */}
          <div className="px-2 pb-3">
            <div className="rounded-md border border-neutral-700/50 bg-gradient-to-br from-cyan-600/10 via-blue-600/10 to-indigo-600/10 p-2 backdrop-blur-xl">
              <div className="mb-1.5 flex items-center gap-2">
                <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
                <span className="text-xs font-semibold text-neutral-200">Upgrade to Pro</span>
              </div>
              <p className="mb-1.5 text-xs text-neutral-400">Unlock advanced AI features</p>
              <Button size="sm" variant="premium" className="h-7 w-full text-xs">
                Upgrade Now
              </Button>
            </div>
          </div>

          {/* User Profile */}
          <div className="border-t border-neutral-800/50 p-3">
            <div className="flex items-center gap-3 rounded-md border border-neutral-700/30 bg-neutral-800/30 p-2 backdrop-blur-xl">
              <Avatar>
                <AvatarImage src="/avatars/user.jpg" />
                <AvatarFallback className="bg-gradient-to-br from-cyan-600 to-indigo-600 text-xs font-medium text-white">
                  {user?.name?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-neutral-200">{user?.name || 'User'}</p>
                <div className="flex items-center gap-2">
                  <p className="truncate text-xs text-neutral-400">{user?.email || ''}</p>
                  {user?.role === 'admin' && (
                    <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-400 border border-cyan-500/30 rounded">
                      ADMIN
                    </span>
                  )}
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 shrink-0 hover:bg-red-500/10 hover:text-red-400"
                onClick={() => logout()}
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile backdrop */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-30 bg-black/80 backdrop-blur-sm lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Header */}
        <header className="sticky top-0 z-20 flex h-14 items-center gap-4 border-b border-neutral-800/50 bg-neutral-900/80 px-4 backdrop-blur-xl lg:px-6">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-1 text-neutral-400 hover:text-neutral-200 lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </button>

          {/* Search */}
          <div className="flex-1">
            <div className="relative hidden max-w-md md:block">
              <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-neutral-500" />
              <input
                type="text"
                placeholder="Search tickets, customers..."
                className="h-8 w-full rounded-md border border-neutral-700/50 bg-neutral-900/50 pl-9 pr-4 text-xs text-neutral-200 placeholder:text-neutral-500 focus:border-cyan-500/50 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 backdrop-blur-xl"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1.5">
            <Button variant="ghost" size="icon" className="relative h-8 w-8 hover:bg-neutral-800/50">
              <Bell className="h-4 w-4 text-neutral-400" />
              <span className="absolute right-0.5 top-0.5 h-2 w-2 rounded-full bg-red-500 shadow-lg shadow-red-500/50" />
            </Button>
            <Link href="/channels">
              <Button variant="premium" className="hidden h-8 text-xs sm:flex">
                <Mail className="mr-1 h-3.5 w-3.5" />
                <span className="hidden lg:inline">New Ticket</span>
              </Button>
            </Link>
          </div>
        </header>

        {/* Dashboard Content - Starts Immediately */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
