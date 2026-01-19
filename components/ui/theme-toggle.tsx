'use client'

import React, { useEffect, useState } from 'react'
import { useTheme } from '@/components/providers/theme-provider'
import { motion } from 'framer-motion'

export function ThemeToggle() {
  const { theme, toggleTheme, mounted } = useTheme()
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  if (!isMounted || !mounted) {
    return (
      <div className="w-12 h-12 rounded-full border border-border bg-card" />
    )
  }

  return (
    <motion.button
      onClick={toggleTheme}
      className="relative w-12 h-12 rounded-full border border-border hover:border-primary bg-card text-foreground transition-colors"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label="Toggle theme"
    >
      <motion.div
        initial={false}
        animate={{
          scale: theme === 'dark' ? 1 : 0,
          opacity: theme === 'dark' ? 1 : 0
        }}
        transition={{ duration: 0.2 }}
        className="absolute inset-0 flex items-center justify-center"
      >
        <svg
          className="w-6 h-6"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M21.64 15.95c-.18-.96-.46-1.88-.92-2.74.86-1.12 1.28-2.6.92-4.04-.2-.74-.55-1.44-.98-2.04-.8-.98-1.97-1.59-3.29-1.59-.66 0-1.3.13-1.93.39-1.12-.86-2.6-1.28-4.04-.92-.74.2-1.44.55-2.04.98-.98.8-1.59 1.97-1.59 3.29 0 .66.13 1.3.39 1.93-.86 1.12-1.28 2.6-.92 4.04.2.74.55 1.44.98 2.04.8.98 1.97 1.59 3.29 1.59.66 0 1.3-.13 1.93-.39 1.12.86 2.6 1.28 4.04.92.74-.2 1.44-.55 2.04-.98.98-.8 1.59-1.97 1.59-3.29 0-.66-.13-1.3-.39-1.93.86-1.12 1.28-2.6.92-4.04zm-9.64 4.05c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z" />
        </svg>
      </motion.div>

      <motion.div
        initial={false}
        animate={{
          scale: theme === 'light' ? 1 : 0,
          opacity: theme === 'light' ? 1 : 0
        }}
        transition={{ duration: 0.2 }}
        className="absolute inset-0 flex items-center justify-center"
      >
        <svg
          className="w-6 h-6"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M12 18c-3.3 0-6-2.7-6-6s2.7-6 6-6 6 2.7 6 6-2.7 6-6 6zm0-10c-2.2 0-4 1.8-4 4s1.8 4 4 4 4-1.8 4-4-1.8-4-4-4zM13 2h-2v3h2V2zm0 15h-2v3h2v-3zM5 11H2v2h3v-2zm15 0h-3v2h3v-2zM6.3 5.3L4.2 3.2 1.9 5.5l2.1 2.1 2.3-2.3zm12.4 12.4l-2.1 2.1 2.3 2.3 2.1-2.1-2.3-2.3zM19.8 4.9l-2.3 2.3 2.1 2.1 2.3-2.3-2.1-2.1zM7.5 16.5l-2.1 2.1 2.3 2.3 2.1-2.1-2.3-2.3z" />
        </svg>
      </motion.div>
    </motion.button>
  )
}
