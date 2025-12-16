"""
AI-Powered Brief Generator
Generates complete SEO content briefs using AI providers.
"""

import json
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ai_provider import AIProvider
from prompts import (
    BRIEF_GENERATION_PROMPT,
    build_brief_prompt,
    get_client_specific_instructions
)
from client_guidelines import (
    get_client_guidelines,
    get_client_name_from_url,
    get_language_preference,
)
from validators import (
    validate_brief,
    fix_brief_issues,
)


class BriefGenerator:
    """Generates SEO content briefs using AI."""

    def __init__(self, provider: str = None):
        self.ai = AIProvider(provider)
        self.provider_name = provider or 'claude'

    def generate_brief(
        self,
        url: str,
        topic: str,
        primary_keyword: str,
        secondary_keywords: List[str],
        internal_links: List[str],
        website_research: Dict = None,
        custom_guidelines: Dict = None
    ) -> Dict:
        """Generate a complete content brief."""
        known_guidelines = get_client_guidelines(url)
        guidelines = known_guidelines or custom_guidelines

        use_uk_english = get_language_preference(url) == 'UK'

        user_prompt = build_brief_prompt(
            url=url,
            topic=topic,
            primary_keyword=primary_keyword,
            secondary_keywords=secondary_keywords,
            internal_links=internal_links,
            website_research=website_research,
            client_guidelines=guidelines
        )

        system_prompt = BRIEF_GENERATION_PROMPT
        if guidelines:
            system_prompt += get_client_specific_instructions(guidelines)

        response = self.ai.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )

        brief_data = self._parse_ai_response(response)

        brief_data['client_name'] = get_client_name_from_url(url)
        brief_data['site'] = url
        brief_data['topic'] = topic
        brief_data['primary_keyword'] = primary_keyword
        brief_data['secondary_keywords'] = secondary_keywords
        brief_data['internal_links'] = internal_links[:3]

        brief_data = fix_brief_issues(brief_data, use_uk_english=use_uk_english)

        if guidelines:
            guideline_restrictions = guidelines.get('restrictions', [])
            brief_restrictions = brief_data.get('restrictions', [])
            merged_restrictions = list(guideline_restrictions)
            for r in brief_restrictions:
                if r not in merged_restrictions and len(merged_restrictions) < 5:
                    merged_restrictions.append(r)
            brief_data['restrictions'] = merged_restrictions[:5]

        validation = validate_brief(brief_data, url, use_uk_english)
        brief_data['_validation'] = validation

        return brief_data

    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response to extract brief data."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(json_pattern, response)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        brace_start = response.find('{')
        brace_end = response.rfind('}')
        if brace_start != -1 and brace_end != -1:
            try:
                return json.loads(response[brace_start:brace_end + 1])
            except json.JSONDecodeError:
                pass

        return self._parse_text_response(response)

    def _parse_text_response(self, response: str) -> Dict:
        """Fallback parser for non-JSON responses."""
        result = {
            'page_type': 'Service Page',
            'page_title': '',
            'meta_description': '',
            'target_url': '',
            'h1': '',
            'word_count': '800-1200 words',
            'audience': [],
            'tone': ['Clear, factual, professional', 'UK English spelling', 'Year 8 reading level'],
            'pov': ['We/You perspective', 'Active voice'],
            'cta': 'Contact us today',
            'restrictions': [],
            'requirements': [
                'Self-referencing canonical URL',
                'Structured data matching visible content',
                'Robots meta applied appropriately'
            ],
            'headings': [],
            'faqs': []
        }

        lines = response.split('\n')

        for line in lines:
            line_lower = line.lower().strip()

            if 'page title' in line_lower and ':' in line:
                result['page_title'] = line.split(':', 1)[1].strip().strip('"\'')
            elif 'meta description' in line_lower and ':' in line:
                result['meta_description'] = line.split(':', 1)[1].strip().strip('"\'')
            elif line_lower.startswith('h1') and ':' in line:
                result['h1'] = line.split(':', 1)[1].strip().strip('"\'')
            elif 'target url' in line_lower and ':' in line:
                result['target_url'] = line.split(':', 1)[1].strip()
            elif 'cta' in line_lower and ':' in line:
                result['cta'] = line.split(':', 1)[1].strip().strip('"\'')
            elif line.strip().endswith('?') and len(line.strip()) > 10:
                result['faqs'].append(line.strip())

        if not result['page_title']:
            result['page_title'] = 'Page Title Needed'
        if not result['meta_description']:
            result['meta_description'] = 'Meta description needed - 140-160 characters with call to action.'
        if not result['h1']:
            result['h1'] = result['page_title']

        return result
