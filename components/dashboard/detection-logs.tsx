'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

export default function DetectionLogs() {
  const [logs, setLogs] = useState<any[]>([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchLogs()
  }, [filter])

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const url = `/api/logs?limit=20${filter !== 'all' ? `&threat_level=${filter}` : ''}`
      const response = await fetch(url)
      if (!response.ok) throw new Error('Failed to fetch logs')
      const data = await response.json()
      setLogs(data.logs)
    } catch (error) {
      console.error('Error fetching logs:', error)
    } finally {
      setLoading(false)
    }
  }

  const getThreatColor = (threat: string) => {
    switch (threat) {
      case 'danger':
        return 'text-red-500'
      case 'suspicious':
        return 'text-yellow-500'
      default:
        return 'text-green-500'
    }
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
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full"
          />
        </div>
      ) : logs.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No detection logs available
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
              {logs.map((log, index) => {
                const result = log.detection_result
                return (
                  <motion.tr
                    key={log.id}
                    className="border-t border-border hover:bg-background/50 transition-colors"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <td className="px-6 py-4 font-mono text-xs">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className={`px-6 py-4 ${getThreatColor(result?.overall_threat || 'safe')}`}>
                      {(result?.overall_threat || 'safe').toUpperCase()}
                    </td>
                    <td className="px-6 py-4">
                      {result?.networks?.length || 0}
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
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  )
}
