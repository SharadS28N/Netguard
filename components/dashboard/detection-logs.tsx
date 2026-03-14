'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

export default function DetectionLogs({ allScans }: { allScans: any[] }) {
  const [filter, setFilter] = useState('all')

  const filteredLogs = allScans.filter(scan => {
    if (filter === 'all') return true
    const threat = scan.summary?.danger > 0 ? 'danger' : scan.summary?.suspicious > 0 ? 'suspicious' : 'safe'
    return threat === filter
  })

  const getThreatColor = (scan: any) => {
    if (scan.summary?.danger > 0) return 'text-red-500'
    if (scan.summary?.suspicious > 0) return 'text-yellow-500'
    return 'text-green-500'
  }

  const getThreatLabel = (scan: any) => {
    if (scan.summary?.danger > 0) return 'DANGER'
    if (scan.summary?.suspicious > 0) return 'SUSPICIOUS'
    return 'SAFE'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Filter */}
      <div className="flex gap-4 overflow-x-auto pb-2">
        {['all', 'danger', 'suspicious', 'safe'].map((f) => (
          <motion.button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 text-sm font-light whitespace-nowrap rounded border transition-colors ${
              filter === f
                ? 'border-accent bg-accent/10 text-accent'
                : 'border-border text-muted-foreground hover:border-accent'
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </motion.button>
        ))}
      </div>

      {/* Logs Table */}
      {allScans.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No detection logs available. Run a scan to begin.
        </div>
      ) : (
        <div className="overflow-x-auto border border-border rounded-lg">
          <table className="w-full text-sm font-light">
            <thead className="border-b border-border bg-background/50">
              <tr>
                <th className="px-6 py-4 text-left font-light tracking-wide">Time</th>
                <th className="px-6 py-4 text-left font-light tracking-wide">Threat Level</th>
                <th className="px-6 py-4 text-left font-light tracking-wide">Networks Found</th>
                <th className="px-6 py-4 text-left font-light tracking-wide">Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((scan, index) => (
                <motion.tr
                  key={scan.timestamp}
                  className="border-t border-border hover:bg-background/50 transition-colors"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <td className="px-6 py-4 font-mono text-xs">
                    {new Date(scan.timestamp).toLocaleString()}
                  </td>
                  <td className={`px-6 py-4 ${getThreatColor(scan)}`}>
                    {getThreatLabel(scan)}
                  </td>
                  <td className="px-6 py-4">
                    {scan.count || 0}
                  </td>
                  <td className="px-6 py-4">
                    <motion.button
                      className="text-accent hover:text-accent/80 text-xs font-light"
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      View
                    </motion.button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  )
}
