'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import ScanInterface from '@/components/dashboard/scan-interface'
import DetectionResults from '@/components/dashboard/detection-results'
import DetectionLogs from '@/components/dashboard/detection-logs'
import ThreatStats from '@/components/dashboard/threat-stats'
import { io, Socket } from 'socket.io-client'

export default function DashboardContent() {
  const [activeTab, setActiveTab] = useState('scan')
  const [scanResults, setScanResults] = useState(null)
  const [isScanning, setIsScanning] = useState(false)
  const [socketConnected, setSocketConnected] = useState(false)

  useEffect(() => {
    const backendUrl =
      process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL || 'http://localhost:5000'

    const socket: Socket = io(backendUrl, {
      transports: ['websocket'],
    })

    socket.on('connect', () => {
      setSocketConnected(true)
    })

    socket.on('disconnect', () => {
      setSocketConnected(false)
    })

    socket.on('scan_status', (payload: any) => {
      if (payload?.status === 'completed') {
        console.log('Scan completed via socket', payload)
      }
    })

    socket.on('detection_result', (payload: any) => {
      console.log('Detection result via socket', payload)
    })

    return () => {
      socket.disconnect()
    }
  }, [])

  const handleScanStart = () => {
    setIsScanning(true)
  }

  const handleScanComplete = (results: any) => {
    setScanResults(results)
    setIsScanning(false)
    setActiveTab('results')
  }

  const tabs = [
    { id: 'scan', label: 'Network Scan' },
    { id: 'results', label: 'Detection Results' },
    { id: 'logs', label: 'Detection Logs' },
    { id: 'stats', label: 'Statistics' },
  ]

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-12"
      >
        <h1 className="text-4xl md:text-5xl font-light tracking-tight mb-4">
          Evil Twin Detection
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl">
          Real-time network scanning and threat analysis powered by AI/ML detection algorithms
        </p>
        <p className="text-xs mt-2 text-muted-foreground">
          Backend link: {socketConnected ? 'Live via WebSocket' : 'Connecting...'}
        </p>
      </motion.div>

      {/* Tab Navigation */}
      <div className="flex gap-4 mb-8 overflow-x-auto">
        {tabs.map((tab) => (
          <motion.button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-6 py-3 text-sm font-light tracking-wide whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? 'text-accent border-b-2 border-accent'
                : 'text-muted-foreground hover:text-foreground'
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {tab.label}
          </motion.button>
        ))}
      </div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {activeTab === 'scan' && (
          <ScanInterface
            onScanStart={handleScanStart}
            onScanComplete={handleScanComplete}
            isScanning={isScanning}
            autoScanIntervalSeconds={60}
          />
        )}
        {activeTab === 'results' && scanResults ? (
          <DetectionResults results={scanResults} />
        ) : activeTab === 'results' ? (
          <div className="bg-card border border-border rounded-lg p-8 text-center">
            <p className="text-muted-foreground">Run a scan to see detection results</p>
          </div>
        ) : null}
        {activeTab === 'logs' && <DetectionLogs />}
        {activeTab === 'stats' && <ThreatStats />}
      </motion.div>
    </div>
  )
}
