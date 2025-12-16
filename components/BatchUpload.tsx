'use client'

import { useState, useRef } from 'react'

interface BatchItem {
  row: number
  url: string
  topic: string
  primaryKeyword: string
  secondaryKeywords: string[]
}

interface BatchUploadProps {
  onUpload: (items: BatchItem[]) => void
  items: BatchItem[]
}

export default function BatchUpload({ onUpload, items }: BatchUploadProps) {
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const parseExcel = async (file: File) => {
    setError(null)

    // Send to backend for parsing (we'll handle Excel parsing server-side)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/parse-excel', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.error || 'Failed to parse Excel file')
      }

      const data = await response.json()
      onUpload(data.items)
    } catch (err: any) {
      setError(err.message || 'Failed to parse file')
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      parseExcel(file)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files?.[0]
    if (file && file.name.endsWith('.xlsx')) {
      parseExcel(file)
    } else {
      setError('Please upload an .xlsx file')
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  return (
    <div className="space-y-4">
      {/* File Format Info */}
      <div className="bg-gray-50 rounded-lg p-4 text-sm">
        <p className="font-medium text-gray-700 mb-2">Expected Excel format:</p>
        <div className="overflow-x-auto">
          <table className="min-w-full text-xs">
            <thead>
              <tr className="bg-gray-200">
                <th className="px-2 py-1">Column A</th>
                <th className="px-2 py-1">Column B</th>
                <th className="px-2 py-1">Column C</th>
                <th className="px-2 py-1">Column D</th>
                <th className="px-2 py-1">Column E</th>
                <th className="px-2 py-1">Column F</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="px-2 py-1 border">Website URL</td>
                <td className="px-2 py-1 border">Topic</td>
                <td className="px-2 py-1 border">Primary KW</td>
                <td className="px-2 py-1 border">Secondary 1</td>
                <td className="px-2 py-1 border">Secondary 2</td>
                <td className="px-2 py-1 border">Secondary 3</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-gray-500 mt-2">First row should be headers (will be skipped)</p>
      </div>

      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx"
          onChange={handleFileChange}
          className="hidden"
        />
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          stroke="currentColor"
          fill="none"
          viewBox="0 0 48 48"
        >
          <path
            d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <p className="mt-2 text-sm text-gray-600">
          <span className="font-medium text-primary-600">Click to upload</span> or drag and drop
        </p>
        <p className="text-xs text-gray-500 mt-1">Excel files only (.xlsx)</p>
      </div>

      {/* Error */}
      {error && (
        <div className="status-error">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Preview Table */}
      {items.length > 0 && (
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">
            Found {items.length} briefs to generate:
          </p>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Row</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">URL</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Primary KW</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Secondary KWs</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {items.map((item, idx) => (
                  <tr key={idx}>
                    <td className="px-3 py-2 text-gray-900">{item.row}</td>
                    <td className="px-3 py-2 text-gray-900 max-w-[150px] truncate">{item.url}</td>
                    <td className="px-3 py-2 text-gray-900">{item.topic}</td>
                    <td className="px-3 py-2 text-gray-900">{item.primaryKeyword}</td>
                    <td className="px-3 py-2 text-gray-500">{item.secondaryKeywords.join(', ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
