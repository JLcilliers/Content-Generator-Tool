'use client'

import { useState } from 'react'
import BatchUpload from '@/components/BatchUpload'
import ProviderSelect from '@/components/ProviderSelect'
import JSZip from 'jszip'

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
  status: 'success' | 'error' | 'pending' | 'processing'
  error?: string
  documentBase64?: string
  documentFilename?: string
}

export default function BatchPage() {
  const [provider, setProvider] = useState('claude')
  const [items, setItems] = useState<BatchItem[]>([])
  const [results, setResults] = useState<BatchResult[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const handleFileUpload = (parsedItems: BatchItem[]) => {
    setItems(parsedItems)
    setResults([])
    setError(null)
  }

  const handleDownloadZip = async () => {
    const successResults = results.filter(r => r.status === 'success' && r.documentBase64)
    if (successResults.length === 0) return

    const zip = new JSZip()

    for (const result of successResults) {
      if (result.documentBase64 && result.documentFilename) {
        // Decode base64 to binary
        const binaryString = atob(result.documentBase64)
        const bytes = new Uint8Array(binaryString.length)
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i)
        }
        zip.file(result.documentFilename, bytes)
      }
    }

    const content = await zip.generateAsync({ type: 'blob' })
    const url = window.URL.createObjectURL(content)
    const link = document.createElement('a')
    link.href = url
    link.download = 'content_briefs.zip'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  const processItem = async (item: BatchItem): Promise<BatchResult> => {
    try {
      // First, research the website
      const researchResponse = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: item.url,
          topic: item.topic
        }),
      })

      let researchData = null
      if (researchResponse.ok) {
        researchData = await researchResponse.json()
      }

      // Generate the brief
      const generateResponse = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider,
          url: item.url,
          topic: item.topic,
          primary_keyword: item.primaryKeyword,
          secondary_keywords: item.secondaryKeywords,
          auto_links: true,
          research_data: researchData
        }),
      })

      if (!generateResponse.ok) {
        const err = await generateResponse.json()
        throw new Error(err.error || 'Generation failed')
      }

      const data = await generateResponse.json()

      return {
        row: item.row,
        topic: item.topic,
        status: 'success',
        documentBase64: data.document_base64,
        documentFilename: data.document_filename
      }

    } catch (err: any) {
      return {
        row: item.row,
        topic: item.topic,
        status: 'error',
        error: err.message || 'Unknown error'
      }
    }
  }

  const handleGenerate = async () => {
    if (items.length === 0) return

    setIsProcessing(true)
    setError(null)
    setCurrentIndex(0)

    // Initialize results as pending
    const initialResults: BatchResult[] = items.map(item => ({
      row: item.row,
      topic: item.topic,
      status: 'pending'
    }))
    setResults(initialResults)

    // Process items one at a time
    const finalResults: BatchResult[] = []

    for (let i = 0; i < items.length; i++) {
      setCurrentIndex(i)

      // Update current item to processing
      setResults(prev => prev.map((r, idx) =>
        idx === i ? { ...r, status: 'processing' } : r
      ))

      // Process the item
      const result = await processItem(items[i])
      finalResults.push(result)

      // Update with result
      setResults(prev => prev.map((r, idx) =>
        idx === i ? result : r
      ))
    }

    setIsProcessing(false)
  }

  const successCount = results.filter(r => r.status === 'success').length
  const errorCount = results.filter(r => r.status === 'error').length
  const hasResults = results.some(r => r.status === 'success' || r.status === 'error')

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
                Processing {currentIndex + 1} of {items.length}...
              </>
            ) : (
              <>Generate All Briefs ({items.length})</>
            )}
          </button>

          {/* Progress Bar */}
          {isProcessing && (
            <div className="mt-4">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Processing: {items[currentIndex]?.topic || 'Item'}</span>
                <span>{Math.round(((currentIndex + 1) / items.length) * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${((currentIndex + 1) / items.length) * 100}%` }}
                />
              </div>
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
          {hasResults && (
            <div className={errorCount === 0 ? 'status-success' : 'status-warning'}>
              <p className="font-medium">
                {successCount} of {items.length} briefs generated successfully
                {errorCount > 0 && ` (${errorCount} failed)`}
              </p>
            </div>
          )}

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
                      {result.status === 'success' && (
                        <span className="text-green-600">✓ Success</span>
                      )}
                      {result.status === 'error' && (
                        <span className="text-red-600">✗ {result.error}</span>
                      )}
                      {result.status === 'pending' && (
                        <span className="text-gray-400">○ Pending</span>
                      )}
                      {result.status === 'processing' && (
                        <span className="text-blue-600 flex items-center gap-1">
                          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                          </svg>
                          Processing...
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Download Button */}
          {successCount > 0 && !isProcessing && (
            <div className="mt-6">
              <button
                onClick={handleDownloadZip}
                className="btn-primary inline-flex"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download All Briefs (ZIP) - {successCount} files
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
