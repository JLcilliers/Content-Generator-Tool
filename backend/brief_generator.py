def generate_brief_markdown(data):
    """
    Generates a content brief in Markdown format.
    """
    url = data.get('url')
    topic = data.get('topic')
    keywords = data.get('keywords')
    internal_links = data.get('internal_links', [])
    client_guidelines = data.get('client_guidelines', {})

    # Extract client name from URL
    client_name = url.split('.')[0].replace('https://', '').capitalize()

    # Get primary and secondary keywords
    keyword_lines = keywords.split('\n')
    primary_keyword = keyword_lines[0] if keyword_lines else ""
    secondary_keywords = keyword_lines[1:] if len(keyword_lines) > 1 else []

    brief = f"""
# {client_name} – {topic} – Content Brief

## Client Site
{url}

## Keywords
**Primary Keyword:** {primary_keyword}
**Secondary Keywords:** {', '.join(secondary_keywords)}

## Web Page Structure
**Type:** [Blog / Service Page / Landing Page]
**Page Title:** [Under 60 characters, primary keyword near start, no dates]
**Meta Description:** [140-160 characters, includes primary keyword, no dates]
**Target URL:** /[keyword-rich-slug]/
**H1 Heading:** [Clear, natural, aligned with primary keyword]

## Internal Linking
{''.join([f'[{link}]({link})\n' for link in internal_links])}

## Writing Guidelines
**Word Count:** [Blog: 800-1000 words / Service Page: 800-1200 words]

**Audience:**
• [Who it is for]
• [What they want]

**Tone:**
• Clear, factual, professional
• UK English spelling
• Year 8 reading level

**POV:**
• We/You perspective
• Active voice

**CTA:** [Single call-to-action only]
"""

    if client_guidelines:
        brief += "\n**Restrictions:**\n"
        for restriction in client_guidelines.get('restrictions', []):
            brief += f"• {restriction}\n"

    brief += """

**Requirements:**
• Self-referencing canonical URL
• Structured data matching visible content (Organisation, Article, FAQPage)
• Robots meta applied appropriately

## Suggested Headings and Key Points to Include

**H1 - [Same as H1 Heading above]**
[One short line explaining what this section covers]

**H2 - [Main Topic Heading 1]**
[One short line explaining what this section covers]

**H3 - [Optional Subheading]**
[One short line describing what to include]

**H2 - [Main Topic Heading 2]**
[One short line explaining what this section covers]

## FAQs
[Question 1]?
[Question 2]?
[Question 3]?
[Question 4]?
"""
    return brief