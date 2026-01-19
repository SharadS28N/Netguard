'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

export default function ThreatStats() {
  const [stats, setStats] = useState({
    totalScans: 0,
    threatsDetected: 0,
    suspiciousNetworks: 0,
    avgConfidence: 0,
  })

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/logs?limit=100')
      if (!response.ok) throw new Error('Failed to fetch stats')
      const data = await response.json()
      const logs = data.logs

      const threatCount = logs.filter((l: any) => l.detection_result?.overall_threat === 'danger').length
      const suspiciousCount = logs.filter((l: any) => l.detection_result?.overall_threat === 'suspicious').length
      const avgConf = logs.reduce((sum: number, l: any) => sum + (l.detection_result?.networks?.[0]?.confidence || 0), 0) / Math.max(logs.length, 1)

      setStats({
        totalScans: logs.length,
        threatsDetected: threatCount,
        suspiciousNetworks: suspiciousCount,
        avgConfidence: avgConf,
      })
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const statCards = [
    { label: 'Total Scans', value: stats.totalScans, color: 'text-blue-500' },
    { label: 'Threats Detected', value: stats.threatsDetected, color: 'text-red-500' },
    { label: 'Suspicious Networks', value: stats.suspiciousNetworks, color: 'text-yellow-500' },
    { label: 'Avg Confidence', value: `${(stats.avgConfidence * 100).toFixed(1)}%`, color: 'text-green-500' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Stats Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, index) => (
          <motion.div
            key={card.label}
            className="border border-border rounded-lg p-6 bg-card hover:border-accent transition-colors"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
          >
            <p className="text-sm text-muted-foreground font-light tracking-wide mb-2">
              {card.label}
            </p>
            <p className={`text-3xl font-light ${card.color}`}>
              {card.value}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Detection Method Distribution */}
      <motion.div
        className="border border-border rounded-lg p-8 bg-card"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <h3 className="text-xl font-light tracking-tight mb-6">Detection Methodology</h3>
        <div className="space-y-4">
          {[
            { name: 'Signature Detection', desc: 'Known threat pattern matching', progress: 85 },
            { name: 'Behavior Analysis', desc: 'Network behavior anomaly detection', progress: 92 },
            { name: 'Traffic Analysis', desc: 'Real-time traffic pattern analysis', progress: 78 },
            { name: 'Ensemble Voting', desc: 'Multi-model consensus decision', progress: 95 },
          ].map((method, index) => (
            <motion.div
              key={method.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + index * 0.1 }}
            >
              <div className="flex justify-between mb-2">
                <div>
                  <p className="font-light text-sm">{method.name}</p>
                  <p className="text-xs text-muted-foreground">{method.desc}</p>
                </div>
                <p className="text-sm font-light text-accent">{method.progress}%</p>
              </div>
              <div className="w-full h-2 bg-background/50 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-accent"
                  initial={{ width: 0 }}
                  animate={{ width: `${method.progress}%` }}
                  transition={{ duration: 0.8, delay: 0.5 + index * 0.1 }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Key Features */}
      <motion.div
        className="border border-border rounded-lg p-8 bg-card"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <h3 className="text-xl font-light tracking-tight mb-6">AI/ML Detection Layers</h3>
        <div className="grid md:grid-cols-2 gap-6">
          {[
            {
              layer: 'Layer 1',
              title: 'Signature Detection',
              features: ['SSID pattern matching', 'Encryption weakness detection', 'Channel anomaly detection']
            },
            {
              layer: 'Layer 2',
              title: 'Behavior Analysis',
              features: ['WPS vulnerability detection', 'Rate anomaly detection', 'Power anomaly analysis']
            },
            {
              layer: 'Layer 3',
              title: 'Traffic Analysis',
              features: ['Beacon flooding detection', 'Association rate analysis', 'Client count anomalies']
            },
            {
              layer: 'Layer 4',
              title: 'Ensemble Decision',
              features: ['Weighted voting system', 'Multi-model consensus', 'Confidence scoring']
            },
          ].map((item, index) => (
            <motion.div
              key={item.layer}
              className="border border-border/50 rounded p-4 bg-background/50"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + index * 0.1 }}
            >
              <p className="text-xs text-accent font-light tracking-widest mb-2">{item.layer}</p>
              <h4 className="font-light text-sm mb-3">{item.title}</h4>
              <ul className="space-y-2">
                {item.features.map((feature) => (
                  <li key={feature} className="text-xs text-muted-foreground font-light flex items-start gap-2">
                    <span className="text-accent mt-0.5">→</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  )
}
