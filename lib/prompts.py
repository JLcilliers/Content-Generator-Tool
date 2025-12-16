"""
System Prompts for AI Brief Generation
Centralized prompts ensuring consistent, high-quality output.
"""

# Main brief generation prompt
BRIEF_GENERATION_PROMPT = """You are an expert SEO content brief generator. Generate precise, validated content briefs following the exact format and rules provided.

## STRICT RULES - APPLY TO EVERY BRIEF

### Content Rules
1. NO years or numeric dates anywhere (titles, descriptions, headings, content). Months (January, March) are allowed.
2. NO link references in content (never write "link to research document" or "link to this page")
3. Use ONLY the exact keywords provided - no modifications, no additions
4. NO emojis anywhere
5. Use hyphens, NOT em dashes

### Language Rules
6. Use UK English spelling throughout (colour, organisation, optimisation, centre) UNLESS client specifies US English
7. Year 8 reading level - short sentences, simple vocabulary, plain language
8. Clear, factual, professional tone
9. We/You perspective with active voice

### Character Limits (INCLUDING SPACES)
10. Page Title: UNDER 60 characters (this is critical)
11. Meta Description: 140-160 characters exactly

### Structure Rules
12. Maximum 4 H2 sections only
13. Maximum 2 H3 subheadings per H2
14. H1 comes first in heading structure
15. 4-6 FAQ questions only (NO answers provided)
16. Maximum 5 restrictions
17. Maximum 2 audience bullet points
18. Single CTA only

### Internal Linking Rules
19. Use exactly 3 URLs provided
20. No anchor text - just list the URLs
21. All URLs must be from the same domain

## OUTPUT FORMAT

You MUST return a valid JSON object with this exact structure:

```json
{
    "page_type": "Service Page OR Blog OR Landing Page",
    "page_title": "Under 60 chars, primary keyword near start",
    "meta_description": "140-160 chars exactly, includes primary keyword, has call to action",
    "target_url": "/keyword-rich-slug/",
    "h1": "Clear, natural heading aligned with primary keyword",
    "word_count": "800-1200 words for service pages, 800-1000 for blogs",
    "audience": [
        "First audience point - who they are",
        "Second audience point - what they want"
    ],
    "tone": [
        "Clear, factual, professional",
        "UK English spelling",
        "Year 8 reading level"
    ],
    "pov": [
        "We/You perspective",
        "Active voice"
    ],
    "cta": "Single call-to-action",
    "restrictions": [
        "Restriction 1",
        "Restriction 2",
        "Restriction 3",
        "Restriction 4",
        "Restriction 5"
    ],
    "requirements": [
        "Self-referencing canonical URL",
        "Structured data matching visible content (Organisation, Article, FAQPage)",
        "Robots meta applied appropriately"
    ],
    "headings": [
        {
            "level": "H1",
            "text": "Same as h1 field above",
            "description": "One short line explaining what this section covers"
        },
        {
            "level": "H2",
            "text": "Main Topic Heading 1",
            "description": "One short line explaining what this section covers",
            "subheadings": [
                {
                    "level": "H3",
                    "text": "Optional Subheading",
                    "description": "One short line describing what to include"
                }
            ]
        }
    ],
    "faqs": [
        "Question 1?",
        "Question 2?",
        "Question 3?",
        "Question 4?"
    ]
}
```

## VALIDATION CHECKLIST (verify before output)
- [ ] Page title under 60 characters
- [ ] Meta description 140-160 characters
- [ ] No years or dates anywhere
- [ ] UK English spelling (unless US specified)
- [ ] Maximum 4 H2 sections
- [ ] Maximum 2 H3s per H2
- [ ] 4-6 FAQ questions
- [ ] Maximum 5 restrictions
- [ ] Single CTA
- [ ] All provided keywords used naturally

Return ONLY the JSON object, no markdown formatting or explanation."""


# Website analysis prompt
WEBSITE_ANALYSIS_PROMPT = """Analyze the provided website content and extract key information for creating a content brief.

Extract and return as JSON:
{
    "brand_voice": "Description of the brand's communication style",
    "services_products": ["List of main services or products offered"],
    "target_audience": "Description of who the business serves",
    "geographic_focus": "Location(s) the business serves",
    "business_model": "B2B or B2C or Both",
    "unique_selling_points": ["Key differentiators"],
    "content_patterns": "Observed patterns in existing content",
    "key_terminology": ["Important terms used on the site"]
}

Be factual. Only include information clearly present in the content. Do not fabricate or assume."""


# Internal link relevance prompt
INTERNAL_LINK_PROMPT = """Given the topic and list of URLs from the same domain, select the 3 most relevant URLs for internal linking.

Selection criteria:
1. Contextual relevance to the topic
2. Would make sense as a supporting link in content about this topic
3. Provides value to readers seeking more information

Return ONLY a JSON array of exactly 3 URLs, ordered by relevance:
["url1", "url2", "url3"]

Do not include any URLs that are:
- Obviously unrelated to the topic
- Homepage only (unless highly relevant)
- Contact or privacy policy pages (unless specifically relevant)"""


# Client-specific prompt additions
def get_client_specific_instructions(guidelines: dict) -> str:
    """Generate client-specific instructions to append to prompts."""
    if not guidelines:
        return ""

    instructions = "\n\n## CLIENT-SPECIFIC REQUIREMENTS\n\n"

    client_name = guidelines.get('client_name', 'This client')

    # Language preference
    language = guidelines.get('language', 'UK')
    if language == 'US':
        instructions += f"**IMPORTANT**: {client_name} uses US English spelling (color, organization, center).\n\n"

    # Never include
    never_include = guidelines.get('never_include', [])
    if never_include:
        instructions += "**NEVER INCLUDE:**\n"
        for item in never_include:
            instructions += f"- {item}\n"
        instructions += "\n"

    # Always include
    always_include = guidelines.get('always_include', [])
    if always_include:
        instructions += "**ALWAYS INCLUDE (when relevant):**\n"
        for item in always_include:
            instructions += f"- {item}\n"
        instructions += "\n"

    # Restrictions
    restrictions = guidelines.get('restrictions', [])
    if restrictions:
        instructions += "**RESTRICTIONS FOR BRIEF:**\n"
        for item in restrictions[:5]:  # Max 5
            instructions += f"- {item}\n"
        instructions += "\n"

    # Technical terms
    technical_terms = guidelines.get('technical_terms', [])
    if technical_terms:
        instructions += "**TECHNICAL TERMS TO USE CORRECTLY:**\n"
        for term in technical_terms:
            instructions += f"- {term}\n"
        instructions += "\n"

    # CTA
    cta = guidelines.get('cta')
    if cta:
        instructions += f"**PREFERRED CTA:** {cta}\n"

    return instructions


def build_brief_prompt(
    url: str,
    topic: str,
    primary_keyword: str,
    secondary_keywords: list,
    internal_links: list,
    website_research: dict = None,
    client_guidelines: dict = None
) -> str:
    """Build the complete user prompt for brief generation."""

    prompt = f"""Generate a complete SEO content brief for:

## INPUT DATA

**Website URL:** {url}
**Topic:** {topic}
**Primary Keyword:** {primary_keyword}
**Secondary Keywords:** {', '.join(secondary_keywords)}

**Internal Links to Use (exactly 3):**
{chr(10).join(['- ' + link for link in internal_links[:3]])}

"""

    # Add website research if available
    if website_research:
        prompt += f"""## WEBSITE RESEARCH

**Brand Voice:** {website_research.get('brand_voice', 'Professional and informative')}
**Target Audience:** {website_research.get('target_audience', 'Not specified')}
**Geographic Focus:** {website_research.get('geographic_focus', 'Not specified')}
**Business Model:** {website_research.get('business_model', 'Not specified')}
**Key Services/Products:** {', '.join(website_research.get('services_products', []))}

"""

    # Add client-specific instructions
    if client_guidelines:
        prompt += get_client_specific_instructions(client_guidelines)

    prompt += """
## TASK

Generate a complete content brief following the exact JSON format specified in the system prompt.

Ensure:
1. Page title is under 60 characters
2. Meta description is 140-160 characters
3. All provided keywords are incorporated naturally
4. All 3 internal links are included
5. Maximum 4 H2 sections with max 2 H3s each
6. 4-6 FAQ questions
7. No dates or years anywhere

Return ONLY valid JSON."""

    return prompt
