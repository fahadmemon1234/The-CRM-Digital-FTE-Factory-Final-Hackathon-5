"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { MessageSquare, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function SupportButton() {
  const [isVisible, setIsVisible] = useState(true)
  const [isHovered, setIsHovered] = useState(false)

  // Hide button when scrolling down, show when scrolling up
  useEffect(() => {
    let lastScrollY = window.scrollY

    const handleScroll = () => {
      const currentScrollY = window.scrollY
      if (currentScrollY > lastScrollY && currentScrollY > 100) {
        setIsVisible(false)
      } else {
        setIsVisible(true)
      }
      lastScrollY = currentScrollY
    }

    window.addEventListener("scroll", handleScroll, { passive: true })
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  if (!isVisible) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0, opacity: 0 }}
        transition={{ type: "spring", stiffness: 260, damping: 20 }}
        className="fixed bottom-6 right-6 z-50"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <Link href="/support">
          <Button
            variant="premium"
            size="lg"
            className="h-14 w-14 rounded-full shadow-2xl shadow-cyan-500/50 hover:shadow-cyan-500/80 transition-all duration-300 group"
          >
            <MessageSquare className="h-6 w-6" />
            
            {/* Tooltip */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: isHovered ? 1 : 0, x: isHovered ? -80 : 20 }}
              className="absolute right-full mr-4 px-4 py-2 bg-neutral-900 border border-neutral-700 rounded-lg whitespace-nowrap pointer-events-none"
            >
              <p className="text-sm font-medium text-white">Need Help?</p>
              <p className="text-xs text-neutral-400">Contact our support team</p>
            </motion.div>
          </Button>
        </Link>
      </motion.div>
    </AnimatePresence>
  )
}
