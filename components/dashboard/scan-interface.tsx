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
  isScanning: externalIsScanning,
}) => {
  const [isScanning, setIsScanning] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [apiResponse, setApiResponse] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleStartScan = async () => {
    setIsScanning(true)
    setError(null)
    
    try {
      console.log('Starting scan...')
      
      // Make API request to backend
      const response = await axios.post('http://localhost:5001/api/pipeline/run', {
        duration: 10,
        scan_type: 'active'
      })
      
      console.log('API Response:', response.data)
      
      // Store response
      setApiResponse(response.data)
      
      // Show modal with response
      setShowModal(true)
      
      // Call parent callbacks if provided
      if (onScanComplete) {
        onScanComplete(response.data)
      }
      
    } catch (err: any) {
      console.error('Scan failed:', err)
      
      const errorMessage = err.response?.data?.error || err.message || 'Failed to start scan'
      setError(errorMessage)
      
      // Show error in modal
      setApiResponse({ error: errorMessage })
      setShowModal(true)
      
    } finally {
      setIsScanning(false)
    }
  }

  const closeModal = () => {
    setShowModal(false)
    setApiResponse(null)
    setError(null)
  }

  const scanning = externalIsScanning || isScanning

  return (
    <>
      <div className="bg-card border border-border rounded-lg p-8">
        <button
          onClick={handleStartScan}
          disabled={scanning}
          className="px-6 py-3 bg-accent text-white rounded-md disabled:opacity-50 hover:bg-accent/90 transition-colors"
        >
          {scanning ? 'Scanning...' : 'Start Scan'}
        </button>
        
        {scanning && (
          <div className="mt-4">
            <div className="flex items-center space-x-2">
              <div className="animate-spin h-5 w-5 border-2 border-accent border-t-transparent rounded-full"></div>
              <span className="text-sm text-muted-foreground">Scanning networks...</span>
            </div>
          </div>
        )}
      </div>

      {/* Response Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card border border-border rounded-lg max-w-2xl w-full max-h-[80vh] overflow-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-card border-b border-border p-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-foreground">
                {error ? '❌ Scan Failed' : '✅ API Response'}
              </h2>
              <button
                onClick={closeModal}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              {error ? (
                <div className="bg-red-500/10 border border-red-500 rounded-lg p-4">
                  <p className="text-red-500 font-semibold">Error:</p>
                  <p className="text-red-400 mt-2">{error}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Pretty-printed JSON response */}
                  <div className="bg-muted rounded-lg p-4">
                    <p className="text-sm font-semibold text-foreground mb-2">Response Data:</p>
                    <pre className="text-xs text-muted-foreground overflow-x-auto whitespace-pre-wrap">
                      {JSON.stringify(apiResponse, null, 2)}
                    </pre>
                  </div>

                  {/* Display key fields if available */}
                  {apiResponse && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {apiResponse.scan_id && (
                        <div className="bg-muted rounded-lg p-4">
                          <p className="text-sm text-muted-foreground">Scan ID</p>
                          <p className="text-lg font-semibold text-foreground">{apiResponse.scan_id}</p>
                        </div>
                      )}
                      
                      {apiResponse.status && (
                        <div className="bg-muted rounded-lg p-4">
                          <p className="text-sm text-muted-foreground">Status</p>
                          <p className="text-lg font-semibold text-foreground">{apiResponse.status}</p>
                        </div>
                      )}
                      
                      {apiResponse.message && (
                        <div className="bg-muted rounded-lg p-4 col-span-full">
                          <p className="text-sm text-muted-foreground">Message</p>
                          <p className="text-foreground">{apiResponse.message}</p>
                        </div>
                      )}

                      {apiResponse.networks && Array.isArray(apiResponse.networks) && (
                        <div className="bg-muted rounded-lg p-4 col-span-full">
                          <p className="text-sm text-muted-foreground mb-2">Networks Found</p>
                          <p className="text-2xl font-bold text-foreground">{apiResponse.networks.length}</p>
                        </div>
                      )}

                      {apiResponse.threat_level && (
                        <div className="bg-muted rounded-lg p-4">
                          <p className="text-sm text-muted-foreground">Threat Level</p>
                          <p className={`text-lg font-semibold ${
                            apiResponse.threat_level === 'danger' ? 'text-red-500' :
                            apiResponse.threat_level === 'suspicious' ? 'text-yellow-500' :
                            'text-green-500'
                          }`}>
                            {apiResponse.threat_level?.toUpperCase()}
                          </p>
                        </div>
                      )}

                      {apiResponse.overall_confidence !== undefined && (
                        <div className="bg-muted rounded-lg p-4">
                          <p className="text-sm text-muted-foreground">Confidence</p>
                          <p className="text-lg font-semibold text-foreground">
                            {(apiResponse.overall_confidence * 100).toFixed(1)}%
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="sticky bottom-0 bg-card border-t border-border p-4">
              <button
                onClick={closeModal}
                className="w-full px-4 py-2 bg-accent text-white rounded-md hover:bg-accent/90 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default ScanInterface