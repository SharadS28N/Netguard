'use client'

import React from 'react'
import { motion } from 'framer-motion'
import Navigation from '@/components/sections/navigation'
import DashboardContent from '@/components/sections/dashboard-content'
import { ErrorBoundary } from '@/components/providers/error-boundary'

export default function Dashboard() {
  return (
    <ErrorBoundary>
      <main className="bg-background text-foreground min-h-screen">
        <Navigation />
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          className="pt-20"
        >
          <DashboardContent />
        </motion.div>
      </main>
    </ErrorBoundary>
  )
}
