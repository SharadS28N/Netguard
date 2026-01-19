'use client'

import React from 'react'

export interface ScanInterfaceProps {
  onScanStart: () => void | Promise<void>
  onScanComplete: (results: any) => void
  isScanning: boolean
}

const ScanInterface: React.FC<ScanInterfaceProps> = ({
  onScanStart,
  onScanComplete,
  isScanning,
}) => {
  return (
    <div className="bg-card border border-border rounded-lg p-8">
      <button
        onClick={onScanStart}
        disabled={isScanning}
        className="px-6 py-3 bg-accent text-white rounded-md disabled:opacity-50"
      >
        {isScanning ? 'Scanning...' : 'Start Scan'}
      </button>
    </div>
  )
}

export default ScanInterface
