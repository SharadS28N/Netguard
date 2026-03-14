'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

type Stats = {
  totalScans: number
  suspiciousNetworks: number
  avgConfidence: number
}

type DetectionMethodology = {
  signature: number
  behavior: number
  traffic: number
  ensemble: number
}

export default function ThreatStats({ allScans }: { allScans: any[] }) {

  const stats = {
    totalScans: allScans.length,
    totalNetworks: allScans.reduce((sum, scan) => sum + (scan.count || 0), 0),
    threatsDetected: allScans.reduce((sum, scan) => sum + (scan.summary?.suspicious || 0) + (scan.summary?.danger || 0), 0),
    suspiciousNetworks: allScans.reduce((sum, scan) => sum + (scan.summary?.suspicious || 0), 0),
    avgConfidence: allScans.length > 0 ? allScans.reduce((sum, scan) => sum + (scan.summary?.avg_confidence || 0), 0) / allScans.length : 0,
  }

  const detectionMethodology = {
    signature: allScans.length > 0 ? allScans.reduce((sum, scan) => sum + (scan.summary?.methodology_averages?.signature || 0), 0) / allScans.length : 0,
    behavior: allScans.length > 0 ? allScans.reduce((sum, scan) => sum + (scan.summary?.methodology_averages?.behavior || 0), 0) / allScans.length : 0,
    traffic: 0, // Placeholder for traffic analysis
    ensemble: allScans.length > 0 ? allScans.reduce((sum, scan) => sum + (scan.summary?.methodology_averages?.ml || 0), 0) / allScans.length : 0,
  }

  const statCards = [
    {
      label: 'Total Scans',
      value: stats.totalScans,
      color: 'text-blue-500',
    },
    {
      label: 'Threats Detected',
      value: stats.threatsDetected,
      color: 'text-red-500',
    },
    {
      label: 'Suspicious Networks',
      value: stats.suspiciousNetworks,
      color: 'text-yellow-500',
    },
    {
      label: 'Avg Confidence',
      value: `${(stats.avgConfidence * 100).toFixed(1)}%`,
      color: 'text-green-500',
    },
  ]

  const detectionMethods = [
    {
      name: 'Signature Detection',
      desc: 'Known threat pattern matching',
      progress: detectionMethodology.signature,
    },
    {
      name: 'Behavior Analysis',
      desc: 'Network behavior anomaly detection',
      progress: detectionMethodology.behavior,
    },
    {
      name: 'Traffic Analysis',
      desc: 'Real-time traffic pattern analysis',
      progress: detectionMethodology.traffic,
    },
    {
      name: 'Ensemble Voting',
      desc: 'Multi-model consensus decision',
      progress: detectionMethodology.ensemble,
    },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >

      {/* Stats */}
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
            <p className="text-sm text-muted-foreground font-light mb-2">
              {card.label}
            </p>

            <p className={`text-3xl font-light ${card.color}`}>
              {card.value}
            </p>

          </motion.div>
        ))}
      </div>

      {/* Detection Methodology */}
      <motion.div
        className="border border-border rounded-lg p-8 bg-card"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >

        <h3 className="text-xl font-light mb-6">
          Detection Methodology
        </h3>

        <div className="space-y-4">

          {detectionMethods.map((method, index) => (

            <motion.div
              key={method.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >

              <div className="flex justify-between mb-2">

                <div>
                  <p className="font-light text-sm">
                    {method.name}
                  </p>

                  <p className="text-xs text-muted-foreground">
                    {method.desc}
                  </p>
                </div>

                <p className="text-sm font-light text-accent">
                  {method.progress}%
                </p>

              </div>

              <div className="w-full h-2 bg-background/50 rounded-full overflow-hidden">

                <motion.div
                  className="h-full bg-accent"
                  initial={{ width: 0 }}
                  animate={{ width: `${method.progress}%` }}
                  transition={{ duration: 0.8 }}
                />

              </div>

            </motion.div>

          ))}

        </div>

      </motion.div>

      {/* AI Layers */}
      <motion.div
        className="border border-border rounded-lg p-8 bg-card"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >

        <h3 className="text-xl font-light mb-6">
          AI/ML Detection Layers
        </h3>

        <div className="grid md:grid-cols-2 gap-6">

          {[
            {
              layer: 'Layer 1',
              title: 'Signature Detection',
              features: [
                'SSID pattern matching',
                'Encryption weakness detection',
                'Channel anomaly detection',
              ],
            },
            {
              layer: 'Layer 2',
              title: 'Behavior Analysis',
              features: [
                'WPS vulnerability detection',
                'Rate anomaly detection',
                'Power anomaly analysis',
              ],
            },
            {
              layer: 'Layer 3',
              title: 'Traffic Analysis',
              features: [
                'Beacon flooding detection',
                'Association rate analysis',
                'Client count anomalies',
              ],
            },
            {
              layer: 'Layer 4',
              title: 'Ensemble Decision',
              features: [
                'Weighted voting system',
                'Multi-model consensus',
                'Confidence scoring',
              ],
            },
          ].map((item, index) => (

            <motion.div
              key={item.layer}
              className="border border-border/50 rounded p-4 bg-background/50"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >

              <p className="text-xs text-accent mb-2">
                {item.layer}
              </p>

              <h4 className="text-sm mb-3">
                {item.title}
              </h4>

              <ul className="space-y-2">

                {item.features.map((feature) => (
                  <li
                    key={feature}
                    className="text-xs text-muted-foreground flex gap-2"
                  >
                    <span className="text-accent">→</span>
                    {feature}
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