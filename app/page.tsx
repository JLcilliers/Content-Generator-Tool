'use client'

import { useState } from 'react'
import BriefForm from '@/components/BriefForm'
import BriefPreview from '@/components/BriefPreview'
import ProviderSelect from '@/components/ProviderSelect'

export default function Home() {
  const [provider, setProvider] = useState('claude')
  const [briefData, setBriefData] = useState<any>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [progressText, setProgressText] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async (formData: {
    url: string
    topic: string
    primaryKeyword: string
    secondaryKeywords: string[]
    autoResearch: boolean
    autoLinks: boolean
    manualLinks: string[]
  }) => {
    setIsGenerating(true)
    setError(null)
    setProgress(0)
    setBriefData(null)

    try {
      // Step 1: Research website (if enabled)
      setProgress(10)
      setProgressText('Researching website...')

      let researchData = null
      if (formData.autoResearch) {
        const researchRes = await fetch('/api/research', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: formData.url, topic: formData.topic }),
        })
        if (!researchRes.ok) {
          const err = await researchRes.json()
          throw new Error(err.error || 'Research failed')
        }
        researchData = await researchRes.json()
      }

      // Step 2: Generate brief
      setProgress(50)
      setProgressText('Generating brief with AI...')

      const generateRes = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider,
          url: formData.url,
          topic: formData.topic,
          primary_keyword: formData.primaryKeyword,
          secondary_keywords: formData.secondaryKeywords,
          auto_links: formData.autoLinks,
          manual_links: formData.manualLinks,
          research_data: researchData,
        }),
      })

      if (!generateRes.ok) {
        const err = await generateRes.json()
        throw new Error(err.error || 'Generation failed')
      }

      const brief = await generateRes.json()

      setProgress(100)
      setProgressText('Complete!')
      setBriefData(brief)

    } catch (err: any) {
      setError(err.message || 'An error occurred')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Single Brief Generator</h1>
        <p className="mt-2 text-gray-600">
          Generate a professional, AI-powered SEO content brief with automatic web research
          and Word document export.
        </p>
      </div>

      {/* Provider Selection */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Provider</h2>
        <ProviderSelect value={provider} onChange={setProvider} />
      </div>

      {/* Brief Form */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Brief Details</h2>
        <BriefForm
          onSubmit={handleGenerate}
          isLoading={isGenerating}
          progress={progress}
          progressText={progressText}
        />
      </div>

      {/* Error Display */}
      {error && (
        <div className="status-error">
          <p className="font-medium text-red-800">Error</p>
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Results */}
      {briefData && (
        <div className="card">
          <BriefPreview data={briefData} />
        </div>
      )}
    </div>
  )
}
