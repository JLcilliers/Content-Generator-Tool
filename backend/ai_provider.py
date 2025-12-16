"""
AI Provider abstraction layer for multiple AI services.
Supports OpenAI, Claude, Perplexity, and Mistral.
"""

import os
from typing import Optional
import requests

# Try to import streamlit for secrets support
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class AIProvider:
    """Abstract AI provider supporting multiple services."""
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize AI provider.
        
        Args:
            provider: AI provider name ('openai', 'claude', 'perplexity', 'mistral')
                     If None, uses DEFAULT_AI_PROVIDER from .env or Streamlit secrets
        """
        self.provider = provider or self._get_config('DEFAULT_AI_PROVIDER', 'openai')
        self.api_keys = {
            'openai': self._get_config('OPENAI_API_KEY'),
            'claude': self._get_config('CLAUDE_API_KEY'),
            'grok': self._get_config('GROK_API_KEY'),
            'perplexity': self._get_config('PERPLEXITY_API_KEY'),
            'mistral': self._get_config('MISTRAL_API_KEY')
        }
        
        if not self.api_keys.get(self.provider):
            raise ValueError(f"API key for {self.provider} not found in environment variables")
    
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """
        Generate text using the configured AI provider.
        
        Args:
            system_prompt: System instruction for the AI
            user_prompt: User query/request
            temperature: Creativity level (0.0-1.0)
            
        Returns:
            Generated text response
        """
        if self.provider == 'openai':
            return self._generate_openai(system_prompt, user_prompt, temperature)
        elif self.provider == 'claude':
            return self._generate_claude(system_prompt, user_prompt, temperature)
        elif self.provider == 'grok':
            return self._generate_grok(system_prompt, user_prompt, temperature)
        elif self.provider == 'perplexity':
            return self._generate_perplexity(system_prompt, user_prompt, temperature)
        elif self.provider == 'mistral':
            return self._generate_mistral(system_prompt, user_prompt, temperature)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _generate_openai(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Generate using OpenAI API."""
        from openai import OpenAI
        
        client = OpenAI(api_key=self.api_keys['openai'])
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _generate_claude(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Generate using Claude API."""
        from anthropic import Anthropic
        
        client = Anthropic(api_key=self.api_keys['claude'])
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=system_prompt,
            temperature=temperature,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return message.content[0].text
    
    def _generate_grok(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Generate using Grok API."""
        headers = {
            "Authorization": f"Bearer {self.api_keys['grok']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _generate_perplexity(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Generate using Perplexity API."""
        headers = {
            "Authorization": f"Bearer {self.api_keys['perplexity']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _generate_mistral(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Generate using Mistral API."""
        headers = {
            "Authorization": f"Bearer {self.api_keys['mistral']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistral-large-latest",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    @staticmethod
    def _get_config(key: str, default: str = None) -> Optional[str]:
        """Get configuration from environment or Streamlit secrets."""
        # Try environment variable first
        value = os.getenv(key)
        if value:
            return value
        
        # Try Streamlit secrets if available
        if STREAMLIT_AVAILABLE:
            try:
                return st.secrets.get(key, default)
            except (FileNotFoundError, KeyError):
                pass
        
        return default
    
    @staticmethod
    def list_available_providers() -> list:
        """List all AI providers that have API keys configured."""
        providers = []
        if AIProvider._get_config('OPENAI_API_KEY'):
            providers.append('openai')
        if AIProvider._get_config('CLAUDE_API_KEY'):
            providers.append('claude')
        if AIProvider._get_config('GROK_API_KEY'):
            providers.append('grok')
        if AIProvider._get_config('PERPLEXITY_API_KEY'):
            providers.append('perplexity')
        if AIProvider._get_config('MISTRAL_API_KEY'):
            providers.append('mistral')
        return providers
