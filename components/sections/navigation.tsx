'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ThemeToggle } from '@/components/ui/theme-toggle'

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false)

  const navItems = [
    { label: 'Threat', href: '#threat' },
    { label: 'Technology', href: '#technology' },
    { label: 'How It Works', href: '#how' },
    { label: 'Documentation', href: '#docs' },
  ]

  return (
    <header className="fixed top-0 w-full z-50 bg-background/95 backdrop-blur-sm border-b border-border">
      <nav className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          className="text-xl font-light tracking-widest"
        >
          NETGUARD
        </motion.div>

        {/* Desktop Menu */}
        <div className="hidden md:flex items-center gap-6">
          {navItems.map((item) => (
            <motion.a
              key={item.label}
              href={item.href}
              whileHover={{ color: '#dc2626' }}
              transition={{ duration: 0.2 }}
              className="text-sm font-light tracking-wide text-muted-foreground hover:text-accent"
            >
              {item.label}
            </motion.a>
          ))}
          <ThemeToggle />
          <motion.a
            href="/dashboard"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-6 py-2 border border-accent text-accent text-sm font-light tracking-wide hover:bg-accent hover:text-background transition-colors"
          >
            Get Started
          </motion.a>
        </div>

        {/* Mobile Menu Button */}
        <motion.button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden relative w-6 h-6 flex flex-col justify-center gap-1.5"
          whileTap={{ scale: 0.95 }}
        >
          <motion.span
            animate={isOpen ? { rotate: 45, y: 8 } : { rotate: 0, y: 0 }}
            className="w-full h-0.5 bg-foreground"
          />
          <motion.span
            animate={isOpen ? { opacity: 0 } : { opacity: 1 }}
            className="w-full h-0.5 bg-foreground"
          />
          <motion.span
            animate={isOpen ? { rotate: -45, y: -8 } : { rotate: 0, y: 0 }}
            className="w-full h-0.5 bg-foreground"
          />
        </motion.button>

        {/* Mobile Menu */}
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 right-0 bg-background border-b border-border p-6 md:hidden"
          >
            {navItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="block py-3 text-sm font-light tracking-wide text-muted-foreground hover:text-accent"
                onClick={() => setIsOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <button className="w-full mt-4 px-6 py-2 border border-accent text-accent text-sm font-light tracking-wide hover:bg-accent hover:text-background transition-colors">
              Get Started
            </button>
          </motion.div>
        )}
      </nav>
    </header>
  )
}
