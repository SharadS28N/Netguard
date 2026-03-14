'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface DetectionResultsProps {
  results?: any
}

export default function DetectionResults({ results }: DetectionResultsProps) {

  if (!results) {
    return (
      <div className="border border-border rounded-lg p-8 text-center text-muted-foreground">
        No scan results yet. Start a scan to see detection results.
      </div>
    )
  }

  /**
   * Convert backend API format → dashboard format
   */
  const networks = results?.data || results?.networks || []

  const overallThreat =
    results?.overall_threat ||
    (results?.summary?.suspicious > 0 ? 'suspicious' : 'safe')

  const getThreatColor = (threat?: string) => {
    switch (threat) {
      case 'danger':
        return 'text-red-500'
      case 'suspicious':
      case 'medium':
        return 'text-yellow-500'
      default:
        return 'text-green-500'
    }
  }

  const getThreatBgColor = (threat?: string) => {
    switch (threat) {
      case 'danger':
        return 'bg-red-500/10 border-red-500/30'
      case 'suspicious':
      case 'medium':
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

      {/* Overall Threat */}
      <motion.div
        className={`border rounded-lg p-8 ${getThreatBgColor(overallThreat)}`}
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.3 }}
      >

        <h2 className="text-2xl font-light mb-4">
          Overall Threat Level
        </h2>

        <p className={`text-3xl font-light ${getThreatColor(overallThreat)}`}>
          {overallThreat.toUpperCase()}
        </p>

        <p className="text-sm text-muted-foreground mt-4">
          Scan completed at{" "}
          {results?.timestamp
            ? new Date(results.timestamp).toLocaleTimeString()
            : "N/A"}
        </p>

      </motion.div>

      {/* Networks */}
      <div className="grid gap-4">

        <h3 className="text-xl font-light">
          Detected Networks
        </h3>

        {networks.length ? (
          networks.map((network: any, index: number) => {

            const threat = network?.threat_level || network?.verdict

            return (
              <motion.div
                key={network.bssid || index}
                className={`border rounded-lg p-6 ${getThreatBgColor(threat)}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >

                <div className="grid md:grid-cols-2 gap-6">

                  <div>

                    <h4 className="text-lg font-light mb-4">
                      {network?.ssid || "Unknown Network"}
                    </h4>

                    <dl className="space-y-2 text-sm">

                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">BSSID:</dt>
                        <dd className="font-mono">{network?.bssid}</dd>
                      </div>

                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Signal Strength:</dt>
                        <dd>
                          {network?.avg_signal !== undefined
                            ? `${Math.abs(network.avg_signal)}%`
                            : network?.signal_strength
                            ? `${network.signal_strength}%`
                            : "N/A"}
                        </dd>
                      </div>

                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Channel:</dt>
                        <dd>{network?.avg_channel || network?.channel || "N/A"}</dd>
                      </div>

                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Security:</dt>
                        <dd>{network?.encryption || "N/A"}</dd>
                      </div>

                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Threat:</dt>
                        <dd className={getThreatColor(threat)}>
                          {threat?.toUpperCase() || "UNKNOWN"}
                        </dd>
                      </div>

                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Confidence:</dt>
                        <dd>
                          {network?.confidence !== undefined
                            ? (network.confidence * 100).toFixed(1) + "%"
                            : "N/A"}
                        </dd>
                      </div>

                    </dl>

                  </div>

                  {/* Analysis */}
                  <div>

                    <h5 className="text-sm text-muted-foreground mb-3">
                      Detection Analysis
                    </h5>

                    <dl className="space-y-2 text-sm">

                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Signature:</dt>
                        <dd>
                          {((network?.layer_scores?.signature ??
                            network?.details?.signature_score ??
                            0) * 100).toFixed(1)}%
                        </dd>
                      </div>

                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Behavior:</dt>
                        <dd>
                          {((network?.layer_scores?.behavior ??
                            network?.details?.behavior_score ??
                            0) * 100).toFixed(1)}%
                        </dd>
                      </div>

                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Traffic Analysis:</dt>
                        <dd>
                          {(network?.layer_scores?.ml !== undefined
                            ? network.layer_scores.ml * 100
                            : (network?.details?.traffic_score ?? 0) * 100
                          ).toFixed(1)}%
                        </dd>
                      </div>

                    </dl>

                  </div>

                </div>

                {/* Explanation */}
                {network?.explanation?.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-border">
                    <h5 className="text-sm text-muted-foreground mb-2">
                      Explanation
                    </h5>
                    <ul className="text-sm space-y-1">
                      {network.explanation.map((e: string, i: number) => (
                        <li key={i}>• {e}</li>
                      ))}
                    </ul>
                  </div>
                )}

              </motion.div>
            )
          })
        ) : (
          <p className="text-sm text-muted-foreground">
            No networks detected.
          </p>
        )}

      </div>

    </motion.div>
  )
}