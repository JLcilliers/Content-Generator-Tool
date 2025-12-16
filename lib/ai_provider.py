"""
AI Provider abstraction layer for multiple AI services.
Supports OpenAI, Claude, Grok, Perplexity, and Mistral.
"""

import os
from typing import Optional
import requests


class AIProvider:
    """Abstract AI provider supporting multiple services."""

    # Latest models as of December 2025
    PROVIDER_MODELS = {
        'openai': 'gpt-5.2',              # GPT-5.2: Latest flagship, 400K context
        'claude': 'claude-opus-4-5-20251101',  # Claude Opus 4.5: Best for complex tasks
        'grok': 'grok-4',                 # Grok 4: Latest stable with strong reasoning
        'perplexity': 'sonar-pro',        # Sonar Pro: Real-time search with citations
        'mistral': 'mistral-large-latest' # Mistral Large 3: 41B active params
    }

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize AI provider.

        Args:
            provider: AI provider name ('openai', 'claude', 'grok', 'perplexity', 'mistral')
                     If None, uses DEFAULT_AI_PROVIDER from environment
        """
        self.provider = provider or os.getenv('DEFAULT_AI_PROVIDER', 'claude')
        self.api_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'claude': os.getenv('CLAUDE_API_KEY'),
            'grok': os.getenv('GROK_API_KEY'),
            'perplexity': os.getenv('PERPLEXITY_API_KEY'),
            'mistral': os.getenv('MISTRAL_API_KEY')
        }

        if not self.api_keys.get(self.provider):
            raise ValueError(f"API key for {self.provider} not found in environment variables")

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        """
        Generate text using the configured AI provider.

        Args:
            system_prompt: System instruction for the AI
            user_prompt: User query/request
            temperature: Creativity level (0.0-1.0), default 0.3 for consistency
            max_tokens: Maximum tokens in response

        Returns:
            Generated text response
        """
        if self.provider == 'openai':
            return self._generate_openai(system_prompt, user_prompt, temperature, max_tokens)
        elif self.provider == 'claude':
            return self._generate_claude(system_prompt, user_prompt, temperature, max_tokens)
        elif self.provider == 'grok':
            return self._generate_grok(system_prompt, user_prompt, temperature, max_tokens)
        elif self.provider == 'perplexity':
            return self._generate_perplexity(system_prompt, user_prompt, temperature, max_tokens)
        elif self.provider == 'mistral':
            return self._generate_mistral(system_prompt, user_prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _generate_openai(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate using OpenAI API."""
        from openai import OpenAI

        client = OpenAI(api_key=self.api_keys['openai'])
        response = client.chat.completions.create(
            model=self.PROVIDER_MODELS['openai'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    def _generate_claude(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate using Claude API."""
        from anthropic import Anthropic

        client = Anthropic(api_key=self.api_keys['claude'])
        message = client.messages.create(
            model=self.PROVIDER_MODELS['claude'],
            max_tokens=max_tokens,
            system=system_prompt,
            temperature=temperature,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return message.content[0].text

    def _generate_grok(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate using Grok API."""
        headers = {
            "Authorization": f"Bearer {self.api_keys['grok']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.PROVIDER_MODELS['grok'],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=120
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    def _generate_perplexity(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate using Perplexity API."""
        headers = {
            "Authorization": f"Bearer {self.api_keys['perplexity']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.PROVIDER_MODELS['perplexity'],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            json=payload,
            headers=headers,
            timeout=120
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    def _generate_mistral(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate using Mistral API."""
        headers = {
            "Authorization": f"Bearer {self.api_keys['mistral']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.PROVIDER_MODELS['mistral'],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=120
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    @staticmethod
    def list_available_providers() -> list:
        """List all AI providers that have API keys configured."""
        providers = []
        if os.getenv('OPENAI_API_KEY'):
            providers.append('openai')
        if os.getenv('CLAUDE_API_KEY'):
            providers.append('claude')
        if os.getenv('GROK_API_KEY'):
            providers.append('grok')
        if os.getenv('PERPLEXITY_API_KEY'):
            providers.append('perplexity')
        if os.getenv('MISTRAL_API_KEY'):
            providers.append('mistral')
        return providers
