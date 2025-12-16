'use client'

interface ProviderSelectProps {
  value: string
  onChange: (value: string) => void
}

const providers = [
  { id: 'openai', name: 'OpenAI GPT-5.2', description: 'Latest flagship model' },
  { id: 'claude', name: 'Claude Opus 4.5', description: 'Best for complex tasks' },
  { id: 'grok', name: 'Grok 4', description: 'Strong reasoning' },
  { id: 'perplexity', name: 'Perplexity Sonar Pro', description: 'Real-time search' },
  { id: 'mistral', name: 'Mistral Large 3', description: '41B parameters' },
]

export default function ProviderSelect({ value, onChange }: ProviderSelectProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
      {providers.map((provider) => (
        <button
          key={provider.id}
          onClick={() => onChange(provider.id)}
          className={`p-3 rounded-lg border-2 text-left transition-all ${
            value === provider.id
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-gray-300 bg-white'
          }`}
        >
          <div className="font-medium text-sm text-gray-900">{provider.name}</div>
          <div className="text-xs text-gray-500 mt-1">{provider.description}</div>
        </button>
      ))}
    </div>
  )
}
