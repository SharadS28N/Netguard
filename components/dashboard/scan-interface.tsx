'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'

interface ScanInterfaceProps {
  onScanStart: () => void
  onScanComplete: (results: any) => void
  isScanning: boolean
  autoScanIntervalSeconds?: number
}

export default function ScanInterface({
  onScanStart,
  onScanComplete,
  isScanning,
  autoScanIntervalSeconds = 0,
}: ScanInterfaceProps) {
  const [scanDuration, setScanDuration] = useState(30)
  const [scanType, setScanType] = useState('active')

  const buildFallbackResult = useCallback(
    (networks: any[], errorMessage: string): any => {
      return {
        scan_id: `scan_error_${Date.now()}`,
        timestamp: Date.now(),
        networks,
        overall_threat: 'safe',
        error: errorMessage
      }
    },
    []
  )

  const handleStartScan = useCallback(async () => {
    onScanStart()

    try {
      const startResponse = await fetch('/api/scan/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scan_type: scanType,
          duration: scanDuration,
        }),
      })

      if (!startResponse.ok) {
        const errorPayload = await startResponse.json().catch(() => null)
        const fallback = buildFallbackResult(
          [],
          errorPayload?.error || 'Failed to start backend scan',
        )
        onScanComplete(fallback)
        return
      }

      const startData = await startResponse.json()
      const scanId = startData.scan_id

      if (!scanId) {
        const fallback = buildFallbackResult([], 'Backend did not return scan_id')
        onScanComplete(fallback)
        return
      }

      let status = startData.status
      let attempts = 0

      while (status === 'in_progress' && attempts < 40) {
        await new Promise((resolve) => setTimeout(resolve, 3000))
        attempts += 1

        const statusResponse = await fetch(`/api/scan/status/${scanId}`)
        if (!statusResponse.ok) {
          const errorPayload = await statusResponse.json().catch(() => null)
          const fallback = buildFallbackResult(
            [],
            errorPayload?.error || 'Failed to get scan status',
          )
          onScanComplete(fallback)
          return
        }

        const statusData = await statusResponse.json()
        status = statusData.status

        if (status === 'failed' || status === 'cancelled') {
          const fallback = buildFallbackResult(
            [],
            statusData.error || `Scan ${status}`,
          )
          onScanComplete(fallback)
          return
        }
      }

      if (status === 'in_progress') {
        const fallback = buildFallbackResult([], 'Scan timed out')
        onScanComplete(fallback)
        return
      }

      const resultsResponse = await fetch(`/api/scan/results/${scanId}`)

      if (!resultsResponse.ok) {
        const errorPayload = await resultsResponse.json().catch(() => null)
        const fallback = buildFallbackResult(
          [],
          errorPayload?.error || 'Failed to get scan results',
        )
        onScanComplete(fallback)
        return
      }

      const scanResults = await resultsResponse.json()
      const networks = scanResults.networks || []

      const detectResponse = await fetch('/api/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          networks,
          scan_type: scanType,
          duration: scanDuration,
        }),
      })

      let results: any

      if (detectResponse.ok) {
        results = await detectResponse.json()
      } else {
        const errorPayload = await detectResponse.json().catch(() => null)
        results = buildFallbackResult(
          networks,
          errorPayload?.error || 'Detection service unavailable',
        )
      }

      await fetch('/api/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          detection_result: results,
          user_action: 'scan_completed'
        }),
      })

      onScanComplete(results)
    } catch (error) {
      console.error('Scan error:', error)
      onScanComplete(
        buildFallbackResult([], String(error))
      )
    }
  }, [onScanStart, onScanComplete, scanType, scanDuration, buildFallbackResult])

  useEffect(() => {
    if (!autoScanIntervalSeconds || autoScanIntervalSeconds <= 0) return

    const interval = setInterval(() => {
      if (!isScanning) {
        handleStartScan()
      }
    }, autoScanIntervalSeconds * 1000)

    return () => clearInterval(interval)
  }, [autoScanIntervalSeconds, isScanning, handleStartScan])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-card border border-border rounded-lg p-8"
    >
      <div className="grid md:grid-cols-2 gap-8 mb-8">
        {/* Scan Type Selection */}
        <div>
          <label className="text-sm font-light tracking-wide text-muted-foreground mb-4 block">
            Scan Type
          </label>
          <div className="flex gap-4">
            {['active', 'passive'].map((type) => (
              <motion.button
                key={type}
                onClick={() => setScanType(type)}
                className={`flex-1 py-3 px-4 border rounded transition-colors ${
                  scanType === type
                    ? 'border-accent bg-accent/10 text-accent'
                    : 'border-border text-muted-foreground hover:border-accent'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Scan Duration */}
        <div>
          <label className="text-sm font-light tracking-wide text-muted-foreground mb-4 block">
            Scan Duration: {scanDuration}s
          </label>
          <input
            type="range"
            min="10"
            max="300"
            step="10"
            value={scanDuration}
            onChange={(e) => setScanDuration(Number(e.target.value))}
            disabled={isScanning}
            className="w-full h-2 bg-border rounded-lg appearance-none cursor-pointer accent-accent disabled:opacity-50"
          />
        </div>
      </div>

      {/* Scan Button */}
      <motion.button
        onClick={handleStartScan}
        disabled={isScanning}
        className="w-full py-4 px-6 bg-accent text-background text-lg font-light tracking-wide hover:bg-accent/90 disabled:opacity-50 transition-all relative overflow-hidden"
        whileHover={!isScanning ? { scale: 1.02 } : {}}
        whileTap={!isScanning ? { scale: 0.98 } : {}}
      >
        {isScanning ? (
          <div className="flex items-center justify-center gap-3">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              className="w-5 h-5 border-2 border-background border-t-transparent rounded-full"
            />
            Scanning Networks...
          </div>
        ) : (
          'Start Scan'
        )}
      </motion.button>

      {/* Info */}
      <div className="mt-8 p-4 bg-background/50 border border-border rounded text-sm text-muted-foreground">
        <p className="font-light leading-relaxed">
          This scan will search for networks in your vicinity and analyze them for evil twin WiFi
          detection using multi-layer AI/ML analysis including signature matching, behavior analysis,
          and real-time anomaly detection.
        </p>
      </div>
    </motion.div>
  )
}
