'use client'

import { useState } from 'react'

interface BriefPreviewProps {
  data: any
}

export default function BriefPreview({ data }: BriefPreviewProps) {
  const [activeTab, setActiveTab] = useState('overview')

  const handleDownload = () => {
    if (data.document_base64 && data.document_filename) {
      // Decode base64 and create blob
      const byteCharacters = atob(data.document_base64)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      })

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = data.document_filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }
  }

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'structure', label: 'Structure' },
    { id: 'guidelines', label: 'Guidelines' },
    { id: 'headings', label: 'Headings & FAQs' },
  ]

  // Validation status
  const validation = data._validation || {}
  const hasErrors = validation.errors?.length > 0
  const hasWarnings = validation.warnings?.length > 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Generated Content Brief</h2>

        {/* Download Button */}
        {data.document_base64 && (
          <button
            onClick={handleDownload}
            className="btn-primary"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download Word Document
          </button>
        )}
      </div>

      {/* Validation Status */}
      {hasErrors && (
        <div className="status-error">
          <p className="font-medium text-red-800">Validation Errors</p>
          <ul className="mt-2 list-disc list-inside text-red-700">
            {validation.errors.map((err: string, idx: number) => (
              <li key={idx}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      {!hasErrors && hasWarnings && (
        <div className="status-warning">
          <p className="font-medium text-yellow-800">Validation Warnings</p>
          <ul className="mt-2 list-disc list-inside text-yellow-700">
            {validation.warnings.map((warn: string, idx: number) => (
              <li key={idx}>{warn}</li>
            ))}
          </ul>
        </div>
      )}

      {!hasErrors && !hasWarnings && (
        <div className="status-success">
          <p className="font-medium text-green-800">All validations passed!</p>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[300px]">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <InfoItem label="Client" value={data.client_name} />
              <InfoItem label="Site" value={data.site} />
              <InfoItem label="Topic" value={data.topic} />
            </div>
            <div className="space-y-4">
              <InfoItem label="Primary Keyword" value={data.primary_keyword} />
              <InfoItem label="Secondary Keywords" value={data.secondary_keywords?.join(', ')} />
            </div>
          </div>
        )}

        {activeTab === 'structure' && (
          <div className="space-y-4">
            <InfoItem label="Page Type" value={data.page_type} />
            <InfoItem
              label="Page Title"
              value={`${data.page_title} (${data.page_title?.length || 0} chars)`}
            />
            <InfoItem
              label="Meta Description"
              value={`${data.meta_description} (${data.meta_description?.length || 0} chars)`}
            />
            <InfoItem label="Target URL" value={data.target_url} />
            <InfoItem label="H1 Heading" value={data.h1} />
            <div>
              <p className="text-sm font-medium text-gray-500">Internal Links</p>
              <ul className="mt-1 list-disc list-inside text-gray-900">
                {data.internal_links?.map((link: string, idx: number) => (
                  <li key={idx} className="truncate">{link}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'guidelines' && (
          <div className="space-y-4">
            <InfoItem label="Word Count" value={data.word_count} />
            <ListItem label="Audience" items={data.audience} />
            <ListItem label="Tone" items={data.tone} />
            <InfoItem label="CTA" value={data.cta} />
            <ListItem label="Restrictions" items={data.restrictions} />
          </div>
        )}

        {activeTab === 'headings' && (
          <div className="space-y-6">
            <div>
              <p className="text-sm font-medium text-gray-500 mb-2">Heading Structure</p>
              <div className="space-y-3">
                {data.headings?.map((heading: any, idx: number) => (
                  <div key={idx} className="border-l-2 border-gray-200 pl-4">
                    <p className="font-medium text-gray-900">
                      {heading.level} - {heading.text}
                    </p>
                    {heading.description && (
                      <p className="text-sm text-gray-500 italic">{heading.description}</p>
                    )}
                    {heading.subheadings?.map((sub: any, subIdx: number) => (
                      <div key={subIdx} className="ml-4 mt-2">
                        <p className="font-medium text-gray-700">H3 - {sub.text}</p>
                        {sub.description && (
                          <p className="text-sm text-gray-500 italic">{sub.description}</p>
                        )}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-500 mb-2">FAQs</p>
              <ul className="list-disc list-inside space-y-1">
                {data.faqs?.map((faq: string, idx: number) => (
                  <li key={idx} className="text-gray-900">{faq}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function InfoItem({ label, value }: { label: string; value?: string }) {
  return (
    <div>
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className="text-gray-900">{value || '-'}</p>
    </div>
  )
}

function ListItem({ label, items }: { label: string; items?: string[] }) {
  return (
    <div>
      <p className="text-sm font-medium text-gray-500">{label}</p>
      {items && items.length > 0 ? (
        <ul className="mt-1 list-disc list-inside text-gray-900">
          {items.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-900">-</p>
      )}
    </div>
  )
}
