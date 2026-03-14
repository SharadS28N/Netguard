// 'use client'

// import React from 'react'

// export interface ScanInterfaceProps {
//   onScanStart: () => void | Promise<void>
//   onScanComplete: (results: any) => void
//   isScanning: boolean
// }

// const ScanInterface: React.FC<ScanInterfaceProps> = ({
//   onScanStart,
//   onScanComplete,
//   isScanning,
// }) => {
//   return (
//     <div className="bg-card border border-border rounded-lg p-8">
//       <button
//         onClick={onScanStart}
//         disabled={isScanning}
//         className="px-6 py-3 bg-accent text-white rounded-md disabled:opacity-50"
//       >
//         {isScanning ? 'Scanning...' : 'Start Scan'}
//       </button>
//     </div>
//   )
// }

// export default ScanInterface



'use client'

import React, { useState } from 'react'
import axios from 'axios'

export interface ScanInterfaceProps {
  onScanStart?: () => void | Promise<void>
  onScanComplete?: (results: any) => void
  isScanning?: boolean
}

const ScanInterface: React.FC<ScanInterfaceProps> = ({
  onScanStart,
  onScanComplete,
  isScanning,
}) => {
  const handleStartScan = async () => {
    if (onScanStart) {
      await onScanStart()
    }
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-card border border-border rounded-lg p-12 text-center relative overflow-hidden group">
        <div className="absolute inset-0 bg-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        
        <div className="relative z-10 max-w-2xl mx-auto space-y-6">
          <div className="w-20 h-20 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-8 animate-pulse">
            <svg 
              className="w-10 h-10 text-accent" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={1.5} 
                d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" 
              />
            </svg>
          </div>

          <h2 className="text-3xl font-light tracking-tight">Ready to Scan</h2>
          <p className="text-muted-foreground text-lg font-light leading-relaxed">
            Begin a comprehensive network analysis to detect evil twin access points, 
            suspicious behavior, and potential security vulnerabilities.
          </p>

          <div className="pt-8">
            <button
              onClick={handleStartScan}
              disabled={isScanning}
              className={`
                px-12 py-4 rounded-full text-sm font-light tracking-[0.2em] uppercase transition-all duration-500
                ${isScanning 
                  ? 'bg-accent/20 text-accent cursor-not-allowed' 
                  : 'bg-accent text-white hover:bg-accent/90 hover:scale-105 active:scale-95 shadow-lg shadow-accent/20'
                }
              `}
            >
              {isScanning ? (
                <span className="flex items-center gap-3">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Analyzing Environment...
                </span>
              ) : (
                'Initiate Security Scan'
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Quick Stats/Features */}
      <div className="grid md:grid-cols-3 gap-6">
        {[
          { title: 'Evil Twin Detection', desc: 'Identify rogue access points mimicking legitimate networks.' },
          { title: 'Behavior Analysis', desc: 'Monitor for suspicious packet patterns and authentication anomalies.' },
          { title: 'Signal Intelligence', desc: 'Analyze signal strength and consistency across detected nodes.' }
        ].map((item, i) => (
          <div key={i} className="p-6 border border-border rounded-lg bg-card/50 hover:border-accent/30 transition-colors">
            <h3 className="text-sm font-medium tracking-wide mb-2 uppercase">{item.title}</h3>
            <p className="text-sm text-muted-foreground font-light leading-relaxed">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
export default ScanInterface