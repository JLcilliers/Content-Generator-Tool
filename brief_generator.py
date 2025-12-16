"""
AI-Powered Brief Generator
Generates complete SEO content briefs using AI providers.
"""

import json
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

from ai_provider import AIProvider
from prompts import (
    BRIEF_GENERATION_PROMPT,
    WEBSITE_ANALYSIS_PROMPT,
    build_brief_prompt,
    get_client_specific_instructions
)
from client_guidelines import (
    get_client_guidelines,
    get_client_name_from_url,
    get_language_preference,
    get_restrictions_for_brief,
    get_default_cta
)
from validators import (
    validate_brief,
    fix_brief_issues,
    validate_page_title,
    validate_meta_description,
    convert_to_uk_english
)


class BriefGenerator:
    """Generates SEO content briefs using AI."""

    def __init__(self, provider: str = None):
        """
        Initialize brief generator.

        Args:
            provider: AI provider to use ('openai', 'claude', 'grok', 'perplexity', 'mistral')
        """
        self.ai = AIProvider(provider)
        self.provider_name = provider or 'openai'

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
        """
        Generate a complete content brief.

        Args:
            url: Website URL
            topic: Content topic
            primary_keyword: Primary target keyword
            secondary_keywords: List of secondary keywords
            internal_links: List of 3 verified internal URLs
            website_research: Optional website research data
            custom_guidelines: Optional custom client guidelines

        Returns:
            Complete brief data dictionary
        """
        # Get client guidelines (known clients or custom)
        known_guidelines = get_client_guidelines(url)
        guidelines = known_guidelines or custom_guidelines

        # Determine language preference
        use_uk_english = get_language_preference(url) == 'UK'

        # Build the prompt
        user_prompt = build_brief_prompt(
            url=url,
            topic=topic,
            primary_keyword=primary_keyword,
            secondary_keywords=secondary_keywords,
            internal_links=internal_links,
            website_research=website_research,
            client_guidelines=guidelines
        )

        # Add client-specific instructions to system prompt
        system_prompt = BRIEF_GENERATION_PROMPT
        if guidelines:
            system_prompt += get_client_specific_instructions(guidelines)

        # Generate brief using AI
        response = self.ai.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3  # Lower temperature for consistency
        )

        # Parse the response
        brief_data = self._parse_ai_response(response)

        # Add metadata
        brief_data['client_name'] = get_client_name_from_url(url)
        brief_data['site'] = url
        brief_data['topic'] = topic
        brief_data['primary_keyword'] = primary_keyword
        brief_data['secondary_keywords'] = secondary_keywords
        brief_data['internal_links'] = internal_links[:3]

        # Apply fixes (UK English, etc.)
        brief_data = fix_brief_issues(brief_data, use_uk_english=use_uk_english)

        # Ensure restrictions from guidelines are included
        if guidelines:
            guideline_restrictions = guidelines.get('restrictions', [])
            brief_restrictions = brief_data.get('restrictions', [])
            # Merge, prioritizing guideline restrictions
            merged_restrictions = list(guideline_restrictions)
            for r in brief_restrictions:
                if r not in merged_restrictions and len(merged_restrictions) < 5:
                    merged_restrictions.append(r)
            brief_data['restrictions'] = merged_restrictions[:5]

        # Validate and log any issues
        validation = validate_brief(brief_data, url, use_uk_english)
        brief_data['_validation'] = validation

        return brief_data

    def _parse_ai_response(self, response: str) -> Dict:
        """
        Parse AI response to extract brief data.

        Args:
            response: Raw AI response string

        Returns:
            Parsed brief data dictionary
        """
        # Try to find JSON in the response
        try:
            # First, try direct JSON parse
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code blocks
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(json_pattern, response)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        # Try to find JSON object in response
        brace_start = response.find('{')
        brace_end = response.rfind('}')
        if brace_start != -1 and brace_end != -1:
            try:
                return json.loads(response[brace_start:brace_end + 1])
            except json.JSONDecodeError:
                pass

        # Fallback: create structure from text parsing
        return self._parse_text_response(response)

    def _parse_text_response(self, response: str) -> Dict:
        """
        Fallback parser for non-JSON responses.

        Args:
            response: Raw response text

        Returns:
            Best-effort parsed dictionary
        """
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
                'Structured data matching visible content (Organisation, Article, FAQPage)',
                'Robots meta applied appropriately'
            ],
            'headings': [],
            'faqs': []
        }

        lines = response.split('\n')

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Extract page title
            if 'page title' in line_lower and ':' in line:
                result['page_title'] = line.split(':', 1)[1].strip().strip('"\'')

            # Extract meta description
            elif 'meta description' in line_lower and ':' in line:
                result['meta_description'] = line.split(':', 1)[1].strip().strip('"\'')

            # Extract H1
            elif line_lower.startswith('h1') and ':' in line:
                result['h1'] = line.split(':', 1)[1].strip().strip('"\'')

            # Extract target URL
            elif 'target url' in line_lower and ':' in line:
                result['target_url'] = line.split(':', 1)[1].strip()

            # Extract page type
            elif 'page type' in line_lower or 'type:' in line_lower:
                text = line.split(':', 1)[1].strip() if ':' in line else ''
                if 'blog' in text.lower():
                    result['page_type'] = 'Blog'
                elif 'landing' in text.lower():
                    result['page_type'] = 'Landing Page'
                else:
                    result['page_type'] = 'Service Page'

            # Extract CTA
            elif 'cta' in line_lower and ':' in line:
                result['cta'] = line.split(':', 1)[1].strip().strip('"\'')

            # Extract FAQs (questions ending with ?)
            elif line.strip().endswith('?') and len(line.strip()) > 10:
                result['faqs'].append(line.strip())

        # Ensure we have required fields
        if not result['page_title']:
            result['page_title'] = 'Page Title Needed'
        if not result['meta_description']:
            result['meta_description'] = 'Meta description needed - 140-160 characters with call to action.'
        if not result['h1']:
            result['h1'] = result['page_title']

        return result

    def regenerate_section(
        self,
        brief_data: Dict,
        section: str,
        additional_instructions: str = None
    ) -> Dict:
        """
        Regenerate a specific section of the brief.

        Args:
            brief_data: Existing brief data
            section: Section to regenerate ('headings', 'faqs', 'meta_description', etc.)
            additional_instructions: Optional extra instructions

        Returns:
            Updated brief data
        """
        section_prompts = {
            'headings': f"""Regenerate the heading structure for this content brief.

Topic: {brief_data.get('topic', '')}
Primary Keyword: {brief_data.get('primary_keyword', '')}
H1: {brief_data.get('h1', '')}

Rules:
- Maximum 4 H2 sections
- Maximum 2 H3 subheadings per H2
- No dates or years
- Each heading needs a one-line description

{additional_instructions or ''}

Return ONLY a JSON array of headings.""",

            'faqs': f"""Generate 4-6 FAQ questions for this topic.

Topic: {brief_data.get('topic', '')}
Keywords: {brief_data.get('primary_keyword', '')}, {', '.join(brief_data.get('secondary_keywords', []))}

Rules:
- Questions only, no answers
- Natural, conversational phrasing
- 4-6 questions maximum
- No dates or years

{additional_instructions or ''}

Return ONLY a JSON array of question strings.""",

            'meta_description': f"""Write a meta description for this page.

Page Title: {brief_data.get('page_title', '')}
Topic: {brief_data.get('topic', '')}
Primary Keyword: {brief_data.get('primary_keyword', '')}

Rules:
- EXACTLY 140-160 characters (including spaces)
- Include primary keyword
- Include a call to action
- No dates or years

{additional_instructions or ''}

Return ONLY the meta description text, nothing else."""
        }

        if section not in section_prompts:
            return brief_data

        response = self.ai.generate(
            system_prompt="You are an SEO expert. Follow the instructions exactly.",
            user_prompt=section_prompts[section],
            temperature=0.3
        )

        # Update the relevant section
        updated_data = brief_data.copy()

        if section == 'meta_description':
            updated_data['meta_description'] = response.strip().strip('"\'')
        elif section in ['headings', 'faqs']:
            try:
                parsed = json.loads(response)
                updated_data[section] = parsed
            except json.JSONDecodeError:
                # Try to extract from response
                if section == 'faqs':
                    questions = [line.strip() for line in response.split('\n') if line.strip().endswith('?')]
                    if questions:
                        updated_data['faqs'] = questions[:6]

        return updated_data


def generate_brief_simple(
    url: str,
    topic: str,
    keywords: str,
    internal_links: List[str],
    provider: str = 'openai',
    website_research: Dict = None
) -> Dict:
    """
    Simplified function for generating briefs.

    Args:
        url: Website URL
        topic: Content topic
        keywords: Keywords string (one per line, primary first)
        internal_links: List of internal URLs
        provider: AI provider to use
        website_research: Optional research data

    Returns:
        Generated brief data
    """
    # Parse keywords
    keyword_lines = [k.strip() for k in keywords.strip().split('\n') if k.strip()]
    primary_keyword = keyword_lines[0] if keyword_lines else topic
    secondary_keywords = keyword_lines[1:] if len(keyword_lines) > 1 else []

    # Generate brief
    generator = BriefGenerator(provider=provider)
    return generator.generate_brief(
        url=url,
        topic=topic,
        primary_keyword=primary_keyword,
        secondary_keywords=secondary_keywords,
        internal_links=internal_links[:3],
        website_research=website_research
    )
