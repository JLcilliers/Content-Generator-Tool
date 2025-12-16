'use client'

import { useState } from 'react'

interface BriefFormProps {
  onSubmit: (data: {
    url: string
    topic: string
    primaryKeyword: string
    secondaryKeywords: string[]
    autoResearch: boolean
    autoLinks: boolean
    manualLinks: string[]
  }) => void
  isLoading: boolean
  progress: number
  progressText: string
}

export default function BriefForm({ onSubmit, isLoading, progress, progressText }: BriefFormProps) {
  const [url, setUrl] = useState('')
  const [topic, setTopic] = useState('')
  const [keywords, setKeywords] = useState('')
  const [autoResearch, setAutoResearch] = useState(true)
  const [autoLinks, setAutoLinks] = useState(true)
  const [manualLinks, setManualLinks] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const keywordList = keywords.split('\n').map(k => k.trim()).filter(k => k)
    const primaryKeyword = keywordList[0] || ''
    const secondaryKeywords = keywordList.slice(1)

    const linkList = manualLinks.split('\n').map(l => l.trim()).filter(l => l)

    onSubmit({
      url,
      topic,
      primaryKeyword,
      secondaryKeywords,
      autoResearch,
      autoLinks,
      manualLinks: linkList,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* URL Input */}
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
            Website URL
          </label>
          <input
            type="url"
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            required
            className="w-full"
          />
        </div>

        {/* Topic Input */}
        <div>
          <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-1">
            Topic
          </label>
          <input
            type="text"
            id="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Neck Pain Treatment"
            required
            className="w-full"
          />
        </div>
      </div>

      {/* Keywords */}
      <div>
        <label htmlFor="keywords" className="block text-sm font-medium text-gray-700 mb-1">
          Keywords (one per line, primary first)
        </label>
        <textarea
          id="keywords"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="neck pain chiropractor plano&#10;upper cervical care for neck pain&#10;neck pain relief plano"
          rows={4}
          required
          className="w-full"
        />
      </div>

      {/* Options */}
      <div className="flex flex-wrap gap-6">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={autoResearch}
            onChange={(e) => setAutoResearch(e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-gray-700">Auto-research website</span>
        </label>

        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={autoLinks}
            onChange={(e) => setAutoLinks(e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-gray-700">Auto-discover internal links</span>
        </label>
      </div>

      {/* Manual Links (shown when auto-links is off) */}
      {!autoLinks && (
        <div>
          <label htmlFor="manualLinks" className="block text-sm font-medium text-gray-700 mb-1">
            Internal Links (one per line)
          </label>
          <textarea
            id="manualLinks"
            value={manualLinks}
            onChange={(e) => setManualLinks(e.target.value)}
            placeholder="https://example.com/about&#10;https://example.com/services&#10;https://example.com/contact"
            rows={3}
            className="w-full"
          />
        </div>
      )}

      {/* Progress Bar */}
      {isLoading && (
        <div>
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>{progressText}</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="btn-primary w-full py-3 text-lg"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Generating...
          </>
        ) : (
          <>Generate Content Brief</>
        )}
      </button>
    </form>
  )
}
