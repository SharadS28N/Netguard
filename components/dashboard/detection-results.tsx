'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface DetectionResultsProps {
  results: any
}

export default function DetectionResults({ results }: DetectionResultsProps) {
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

  const getThreatBgColor = (threat: string) => {
    switch (threat) {
      case 'danger':
        return 'bg-red-500/10 border-red-500/30'
      case 'suspicious':
        return 'bg-yellow-500/10 border-yellow-500/30'
      default:
        return 'bg-green-500/10 border-green-500/30'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Overall Threat Status */}
      <motion.div
        className={`border rounded-lg p-8 ${getThreatBgColor(results.overall_threat)}`}
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <h2 className="text-2xl font-light tracking-tight mb-4">Overall Threat Level</h2>
        <p className={`text-3xl font-light ${getThreatColor(results.overall_threat)}`}>
          {results.overall_threat.toUpperCase()}
        </p>
        <p className="text-sm text-muted-foreground mt-4">
          Scan completed at {new Date(results.timestamp).toLocaleTimeString()}
        </p>
      </motion.div>

      {/* Network Results */}
      <div className="grid gap-4">
        <h3 className="text-xl font-light tracking-tight">Detected Networks</h3>
        {results.networks && results.networks.length > 0 ? results.networks.map((network: any, index: number) => (
          <motion.div
            key={network.bssid}
            className={`border rounded-lg p-6 ${getThreatBgColor(network.threat_level)}`}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <div className="grid md:grid-cols-2 gap-6">
              {/* Left: Network Info */}
              <div>
                <h4 className="text-lg font-light mb-4">{network.ssid}</h4>
                <dl className="space-y-2 text-sm font-light">
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">BSSID:</dt>
                    <dd className="font-mono">{network.bssid}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Threat Level:</dt>
                    <dd className={getThreatColor(network.threat_level)}>
                      {network.threat_level.toUpperCase()}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Confidence:</dt>
                    <dd>{(network.confidence * 100).toFixed(1)}%</dd>
                  </div>
                </dl>
              </div>

              {/* Right: Analysis Details */}
              <div>
                <h5 className="text-sm font-light text-muted-foreground mb-3">Detection Analysis</h5>
                <dl className="space-y-2 text-sm font-light">
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Signature Score:</dt>
                    <dd>{(network.details.signature_score * 100).toFixed(1)}%</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Behavior Score:</dt>
                    <dd>{(network.details.behavior_score * 100).toFixed(1)}%</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Traffic Score:</dt>
                    <dd>{(network.details.traffic_score * 100).toFixed(1)}%</dd>
                  </div>
                  <div className="pt-2 border-t border-border">
                    <dt className="text-muted-foreground text-xs">Method:</dt>
                    <dd className="text-xs">{network.details.ensemble_decision}</dd>
                  </div>
                </dl>
              </div>
            </div>

            {/* Recommendations */}
            {network.recommendations && network.recommendations.length > 0 && (
              <div className="mt-4 pt-4 border-t border-border">
                <h5 className="text-sm font-light text-muted-foreground mb-3">Recommendations</h5>
                <ul className="space-y-2 text-sm font-light">
                  {network.recommendations.map((rec: string, i: number) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-accent mt-1">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )) : null}
      </div>
    </motion.div>
  )
}
