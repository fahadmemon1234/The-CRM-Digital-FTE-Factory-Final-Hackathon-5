"use client"

import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  LayoutDashboard,
  Ticket,
  BarChart3,
  Users,
  Mail,
  Menu,
  X,
  Bell,
  Search,
  LogOut,
  Sparkles,
  Radio,
  ArrowRight,
  FileText,
  MessageCircle,
  User
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { quickSearch, type SearchResult } from "@/lib/search"
import { getNotifications, getUnreadCount, markAsRead, markAllAsRead, type Notification } from "@/lib/notifications"

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
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [showNotifications, setShowNotifications] = useState(false)
  const [isLoadingNotifications, setIsLoadingNotifications] = useState(false)
  const searchTimeoutRef = useRef<NodeJS.Timeout>()
  const notificationsTimeoutRef = useRef<NodeJS.Timeout>()
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuth()

  useEffect(() => {
    setIsMounted(true)
    
    // Load initial unread count
    loadUnreadCount()
    
    // Refresh notifications every 30 seconds
    const interval = setInterval(loadUnreadCount, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadUnreadCount = async () => {
    const data = await getUnreadCount()
    setUnreadCount(data.unread)
  }

  const loadNotifications = async () => {
    setIsLoadingNotifications(true)
    const data = await getNotifications(10)
    setNotifications(data.notifications)
    setIsLoadingNotifications(false)
  }

  const handleNotificationClick = async (notification: Notification, url: string) => {
    // Mark as read if it's unread
    if (!notification.read) {
      await markSingleAsRead(notification.id)
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => n.id === notification.id ? { ...n, read: true } : n)
      )
      
      // Recalculate unread count
      loadUnreadCount()
    }
    
    // Navigate
    router.push(url)
    setShowNotifications(false)
  }

  const handleMarkAllRead = async () => {
    await markAllAsRead()

    // Mark all local notifications as read (but keep them visible)
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
    setUnreadCount(0)

    // Clear localStorage since all are read now
    localStorage.setItem('read_notifications', '[]')

    // Force refresh after a short delay to show updated state
    setTimeout(() => {
      loadUnreadCount()
      loadNotifications()
    }, 1000)
  }

  // Debounced search
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current)
    }

    if (!searchQuery || searchQuery.length < 2) {
      setSearchResults([])
      return
    }

    searchTimeoutRef.current = setTimeout(async () => {
      setIsSearching(true)
      const data = await quickSearch(searchQuery, 6)
      setSearchResults(data.results || [])
      setIsSearching(false)
    }, 300)

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current)
      }
    }
  }, [searchQuery])

  const handleSelectResult = (url: string) => {
    router.push(url)
    setShowResults(false)
    setSearchQuery('')
  }

  const getIconForType = (type: string) => {
    switch (type) {
      case 'ticket':
        return <Ticket className="h-4 w-4 text-blue-400" />
      case 'customer':
        return <User className="h-4 w-4 text-green-400" />
      case 'conversation':
        return <MessageCircle className="h-4 w-4 text-purple-400" />
      case 'message':
        return <FileText className="h-4 w-4 text-orange-400" />
      default:
        return <ArrowRight className="h-4 w-4 text-neutral-400" />
    }
  }

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
            <div className="relative max-w-md">
              <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-neutral-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  setShowResults(true)
                }}
                onFocus={() => setShowResults(true)}
                onBlur={() => setTimeout(() => setShowResults(false), 200)}
                placeholder="Search tickets, customers..."
                className="h-8 w-full rounded-md border border-neutral-700/50 bg-neutral-900/50 pl-9 pr-4 text-xs text-neutral-200 placeholder:text-neutral-500 focus:border-cyan-500/50 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 backdrop-blur-xl"
              />
              
              {/* Search Results Dropdown */}
              <AnimatePresence>
                {showResults && (searchQuery.length >= 2 || isSearching) && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute top-full left-0 right-0 mt-2 max-h-96 overflow-y-auto rounded-lg border border-neutral-700/50 bg-neutral-900/95 backdrop-blur-xl shadow-2xl z-50"
                  >
                    {isSearching && searchResults.length === 0 && (
                      <div className="flex items-center justify-center py-8">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-500 border-t-transparent" />
                        <span className="ml-2 text-xs text-neutral-400">Searching...</span>
                      </div>
                    )}
                    
                    {!isSearching && searchResults.length === 0 && searchQuery.length >= 2 && (
                      <div className="flex flex-col items-center justify-center py-8 text-center">
                        <Search className="h-8 w-8 text-neutral-600 mb-2" />
                        <p className="text-sm text-neutral-400">No results found</p>
                        <p className="text-xs text-neutral-500 mt-1">Try searching for tickets or customers</p>
                      </div>
                    )}
                    
                    {searchResults.length > 0 && (
                      <div className="py-2">
                        <div className="px-3 py-2 border-b border-neutral-700/50">
                          <p className="text-xs font-medium text-neutral-400">
                            {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} for "{searchQuery}"
                          </p>
                        </div>
                        {searchResults.map((result, index) => (
                          <button
                            key={`${result.type}-${result.id}`}
                            onClick={() => handleSelectResult(result.url)}
                            className="w-full px-3 py-2.5 flex items-center gap-3 hover:bg-neutral-800/50 transition-colors text-left group"
                          >
                            <div className="flex-shrink-0">
                              {getIconForType(result.type)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-xs font-medium text-neutral-200 truncate group-hover:text-cyan-400 transition-colors">
                                {result.title}
                              </p>
                              <p className="text-xs text-neutral-500 truncate">
                                {result.subtitle}
                              </p>
                            </div>
                            <ArrowRight className="h-3.5 w-3.5 text-neutral-600 group-hover:text-cyan-400 transition-colors" />
                          </button>
                        ))}
                        <div className="px-3 py-2 border-t border-neutral-700/50">
                          <Link
                            href={`/dashboard/tickets?search=${encodeURIComponent(searchQuery)}`}
                            className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors flex items-center justify-center gap-1"
                          >
                            View all results
                            <ArrowRight className="h-3 w-3" />
                          </Link>
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1.5">
            {/* Notifications */}
            <div className="relative">
              <Button
                variant="ghost"
                size="icon"
                className="relative h-8 w-8 hover:bg-neutral-800/50"
                onClick={() => {
                  setShowNotifications(!showNotifications)
                  if (!showNotifications) {
                    loadNotifications()
                  }
                }}
              >
                <Bell className="h-4 w-4 text-neutral-400" />
                {unreadCount > 0 && (
                  <span className="absolute -right-1 -top-1 flex h-5 min-w-[20px] items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white shadow-lg shadow-red-500/50">
                    {unreadCount > 99 ? '99+' : unreadCount}
                  </span>
                )}
              </Button>

              {/* Notifications Dropdown */}
              <AnimatePresence>
                {showNotifications && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    className="absolute right-0 mt-2 w-80 max-h-96 overflow-y-auto rounded-lg border border-neutral-700/50 bg-neutral-900/95 backdrop-blur-xl shadow-2xl z-50"
                    onBlur={() => setTimeout(() => setShowNotifications(false), 200)}
                  >
                    {/* Header */}
                    <div className="sticky top-0 flex items-center justify-between px-4 py-3 border-b border-neutral-700/50 bg-neutral-900/95 backdrop-blur-xl">
                      <div>
                        <h3 className="text-sm font-semibold text-white">Notifications</h3>
                        <p className="text-xs text-neutral-400">
                          {unreadCount > 0 ? `${unreadCount} unread` : 'All read'}
                        </p>
                      </div>
                      {unreadCount > 0 && (
                        <button
                          onClick={handleMarkAllRead}
                          className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
                        >
                          Mark all read
                        </button>
                      )}
                    </div>

                    {/* Content */}
                    {isLoadingNotifications ? (
                      <div className="flex items-center justify-center py-8">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-500 border-t-transparent" />
                        <span className="ml-2 text-xs text-neutral-400">Loading...</span>
                      </div>
                    ) : notifications.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-8 text-center">
                        <Bell className="h-8 w-8 text-neutral-600 mb-2" />
                        <p className="text-sm text-neutral-400">No notifications</p>
                        <p className="text-xs text-neutral-500 mt-1">
                          You're all caught up!
                        </p>
                      </div>
                    ) : (
                      <div className="py-2">
                        {notifications.map((notification) => (
                          <button
                            key={notification.id}
                            onClick={() => handleNotificationClick(notification, notification.url)}
                            className={`w-full px-4 py-3 flex gap-3 hover:bg-neutral-800/50 transition-colors text-left border-l-2 ${
                              !notification.read
                                ? 'border-cyan-500 bg-cyan-500/5'
                                : 'border-transparent'
                            }`}
                          >
                            {/* Icon */}
                            <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                              notification.color === 'red' ? 'bg-red-500/10' :
                              notification.color === 'blue' ? 'bg-blue-500/10' :
                              notification.color === 'green' ? 'bg-green-500/10' :
                              notification.color === 'purple' ? 'bg-purple-500/10' :
                              'bg-neutral-500/10'
                            }`}>
                              {notification.icon === 'alert' && (
                                <span className="text-sm">🚨</span>
                              )}
                              {notification.icon === 'ticket' && (
                                <span className="text-sm">📬</span>
                              )}
                              {notification.icon === 'message' && (
                                <span className="text-sm">💬</span>
                              )}
                              {notification.icon === 'refresh' && (
                                <span className="text-sm">📝</span>
                              )}
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                              <p className={`text-xs font-medium truncate ${
                                !notification.read ? 'text-white' : 'text-neutral-400'
                              }`}>
                                {notification.title}
                              </p>
                              <p className="text-xs text-neutral-500 truncate mt-0.5">
                                {notification.message}
                              </p>
                              {notification.timestamp && (
                                <p className="text-[10px] text-neutral-600 mt-1">
                                  {new Date(notification.timestamp).toLocaleString()}
                                </p>
                              )}
                            </div>

                            {/* Unread indicator */}
                            {!notification.read && (
                              <div className="flex-shrink-0 mt-1">
                                <div className="h-2 w-2 rounded-full bg-cyan-500" />
                              </div>
                            )}
                          </button>
                        ))}

                        {/* Footer */}
                        <div className="px-4 py-2 border-t border-neutral-700/50">
                          <Link
                            href="/dashboard/tickets"
                            className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors flex items-center justify-center gap-1"
                          >
                            View all activity
                            <ArrowRight className="h-3 w-3" />
                          </Link>
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

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
