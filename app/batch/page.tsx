'use client'

import { useState } from 'react'
import BatchUpload from '@/components/BatchUpload'
import ProviderSelect from '@/components/ProviderSelect'

interface BatchItem {
  row: number
  url: string
  topic: string
  primaryKeyword: string
  secondaryKeywords: string[]
}

interface BatchResult {
  row: number
  topic: string
  status: 'success' | 'error'
  error?: string
}

export default function BatchPage() {
  const [provider, setProvider] = useState('claude')
  const [items, setItems] = useState<BatchItem[]>([])
  const [results, setResults] = useState<BatchResult[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentItem, setCurrentItem] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [zipData, setZipData] = useState<{ base64: string; filename: string } | null>(null)

  const handleFileUpload = (parsedItems: BatchItem[]) => {
    setItems(parsedItems)
    setResults([])
    setError(null)
    setZipData(null)
  }

  const handleDownloadZip = () => {
    if (zipData) {
      // Decode base64 and create blob
      const byteCharacters = atob(zipData.base64)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], { type: 'application/zip' })

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = zipData.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }
  }

  const handleGenerate = async () => {
    if (items.length === 0) return

    setIsProcessing(true)
    setError(null)
    setResults([])
    setZipData(null)
    setProgress(0)
    setCurrentItem('Starting batch processing...')

    try {
      const response = await fetch('/api/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, items }),
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.error || 'Batch processing failed')
      }

      const data = await response.json()

      // Update results
      setResults(data.results || [])
      setProgress(100)
      setCurrentItem('Complete!')

      // Store ZIP data for download
      if (data.zip_base64) {
        setZipData({
          base64: data.zip_base64,
          filename: data.zip_filename || 'content_briefs.zip'
        })
      }

    } catch (err: any) {
      setError(err.message || 'An error occurred')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Batch Brief Generator</h1>
        <p className="mt-2 text-gray-600">
          Upload an Excel file to generate multiple content briefs at once.
          All briefs will be bundled into a ZIP file for download.
        </p>
      </div>

      {/* Provider Selection */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Provider</h2>
        <ProviderSelect value={provider} onChange={setProvider} />
      </div>

      {/* File Upload */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload Excel File</h2>
        <BatchUpload onUpload={handleFileUpload} items={items} />
      </div>

      {/* Generate Button */}
      {items.length > 0 && (
        <div className="card">
          <button
            onClick={handleGenerate}
            disabled={isProcessing}
            className="btn-primary w-full py-3 text-lg"
          >
            {isProcessing ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Processing... (this may take a few minutes)
              </>
            ) : (
              <>Generate All Briefs ({items.length})</>
            )}
          </button>

          {/* Progress Indicator */}
          {isProcessing && (
            <div className="mt-4">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>{currentItem}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300 animate-pulse"
                  style={{ width: '100%' }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Processing {items.length} briefs. Please wait...
              </p>
            </div>
          )}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="status-error">
          <p className="font-medium text-red-800">Error</p>
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Results</h2>

          {/* Summary */}
          <div className={results.every(r => r.status === 'success') ? 'status-success' : 'status-warning'}>
            <p className="font-medium">
              {results.filter(r => r.status === 'success').length} of {results.length} briefs generated successfully
            </p>
          </div>

          {/* Results Table */}
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Row</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {results.map((result, idx) => (
                  <tr key={idx}>
                    <td className="px-4 py-3 text-sm text-gray-900">{result.row}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{result.topic}</td>
                    <td className="px-4 py-3 text-sm">
                      {result.status === 'success' ? (
                        <span className="text-green-600">✓ Success</span>
                      ) : (
                        <span className="text-red-600">✗ {result.error}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Download Button */}
          {zipData && (
            <div className="mt-6">
              <button
                onClick={handleDownloadZip}
                className="btn-primary inline-flex"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download All Briefs (ZIP)
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
