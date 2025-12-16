"""
Validation Functions for Content Briefs
Ensures all output meets strict SEO and formatting requirements.
"""

import re
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse
import requests


# US to UK English spelling conversions
US_TO_UK_SPELLINGS = {
    'color': 'colour',
    'colors': 'colours',
    'favor': 'favour',
    'favors': 'favours',
    'favorite': 'favourite',
    'favorites': 'favourites',
    'honor': 'honour',
    'honors': 'honours',
    'labor': 'labour',
    'labors': 'labours',
    'neighbor': 'neighbour',
    'neighbors': 'neighbours',
    'behavior': 'behaviour',
    'behaviors': 'behaviours',
    'center': 'centre',
    'centers': 'centres',
    'theater': 'theatre',
    'theaters': 'theatres',
    'meter': 'metre',
    'meters': 'metres',
    'liter': 'litre',
    'liters': 'litres',
    'fiber': 'fibre',
    'fibers': 'fibres',
    'analyze': 'analyse',
    'analyzes': 'analyses',
    'analyzed': 'analysed',
    'analyzing': 'analysing',
    'organize': 'organise',
    'organizes': 'organises',
    'organized': 'organised',
    'organizing': 'organising',
    'organization': 'organisation',
    'organizations': 'organisations',
    'optimize': 'optimise',
    'optimizes': 'optimises',
    'optimized': 'optimised',
    'optimizing': 'optimising',
    'optimization': 'optimisation',
    'recognize': 'recognise',
    'recognizes': 'recognises',
    'recognized': 'recognised',
    'recognizing': 'recognising',
    'specialize': 'specialise',
    'specializes': 'specialises',
    'specialized': 'specialised',
    'specializing': 'specialising',
    'realize': 'realise',
    'realizes': 'realises',
    'realized': 'realised',
    'realizing': 'realising',
    'utilize': 'utilise',
    'utilizes': 'utilises',
    'utilized': 'utilised',
    'utilizing': 'utilising',
    'apologize': 'apologise',
    'defense': 'defence',
    'offense': 'offence',
    'license': 'licence',
    'practice': 'practise',
    'traveling': 'travelling',
    'traveled': 'travelled',
    'traveler': 'traveller',
    'canceled': 'cancelled',
    'canceling': 'cancelling',
    'enrollment': 'enrolment',
    'fulfill': 'fulfil',
    'installment': 'instalment',
    'modeling': 'modelling',
    'program': 'programme',
    'programs': 'programmes',
}


def validate_page_title(title: str) -> Tuple[bool, str]:
    """Validate page title meets requirements."""
    if not title:
        return False, "Page title is empty"

    if len(title) >= 60:
        return False, f"Page title is {len(title)} characters (must be under 60)"

    if contains_year(title):
        return False, "Page title contains a year/date"

    return True, f"Valid ({len(title)} characters)"


def validate_meta_description(description: str) -> Tuple[bool, str]:
    """Validate meta description meets requirements."""
    if not description:
        return False, "Meta description is empty"

    length = len(description)
    if length < 140:
        return False, f"Meta description is {length} characters (must be 140-160)"
    if length > 160:
        return False, f"Meta description is {length} characters (must be 140-160)"

    if contains_year(description):
        return False, "Meta description contains a year/date"

    return True, f"Valid ({length} characters)"


def validate_heading_structure(headings: List[Dict]) -> Tuple[bool, List[str]]:
    """Validate heading structure meets requirements."""
    errors = []

    if not headings:
        return False, ["No headings provided"]

    if headings[0].get('level') != 'H1':
        errors.append("H1 must be the first heading")

    h2_count = sum(1 for h in headings if h.get('level') == 'H2')
    if h2_count > 4:
        errors.append(f"Too many H2 sections ({h2_count}, maximum is 4)")

    for heading in headings:
        if heading.get('level') == 'H2':
            subheadings = heading.get('subheadings', [])
            if len(subheadings) > 2:
                errors.append(f"H2 '{heading.get('text', '')[:30]}...' has {len(subheadings)} H3s (maximum is 2)")

        if contains_year(heading.get('text', '')):
            errors.append(f"Heading contains year: '{heading.get('text', '')}'")

        for sub in heading.get('subheadings', []):
            if contains_year(sub.get('text', '')):
                errors.append(f"Subheading contains year: '{sub.get('text', '')}'")

    return len(errors) == 0, errors


def validate_faqs(faqs: List[str]) -> Tuple[bool, str]:
    """Validate FAQ list meets requirements."""
    if not faqs:
        return False, "No FAQs provided"

    if len(faqs) < 4:
        return False, f"Too few FAQs ({len(faqs)}, minimum is 4)"
    if len(faqs) > 6:
        return False, f"Too many FAQs ({len(faqs)}, maximum is 6)"

    for faq in faqs:
        if contains_year(faq):
            return False, f"FAQ contains year: '{faq}'"
        if not faq.strip().endswith('?'):
            return False, f"FAQ doesn't end with question mark: '{faq}'"

    return True, f"Valid ({len(faqs)} questions)"


def validate_restrictions(restrictions: List[str]) -> Tuple[bool, str]:
    """Validate restrictions list."""
    if restrictions and len(restrictions) > 5:
        return False, f"Too many restrictions ({len(restrictions)}, maximum is 5)"
    return True, f"Valid ({len(restrictions) if restrictions else 0} restrictions)"


def validate_internal_links(links: List[str], domain: str = None) -> Tuple[bool, List[str]]:
    """Validate internal links."""
    errors = []

    if not links:
        return False, ["No internal links provided"]

    if len(links) != 3:
        errors.append(f"Expected 3 internal links, got {len(links)}")

    if domain:
        for link in links:
            link_domain = urlparse(link).netloc.lower().replace('www.', '')
            expected_domain = domain.lower().replace('www.', '')
            if link_domain != expected_domain:
                errors.append(f"Link '{link}' is not from domain '{domain}'")

    return len(errors) == 0, errors


def contains_year(text: str) -> bool:
    """Check if text contains a year (1900-2099)."""
    if not text:
        return False
    year_pattern = r'\b(19|20)\d{2}\b'
    return bool(re.search(year_pattern, text))


def contains_emoji(text: str) -> bool:
    """Check if text contains emoji characters."""
    if not text:
        return False
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return bool(emoji_pattern.search(text))


def contains_em_dash(text: str) -> bool:
    """Check if text contains em dash."""
    if not text:
        return False
    return '\u2014' in text or '\u2013' in text


def convert_to_uk_english(text: str) -> str:
    """Convert US English spellings to UK English."""
    if not text:
        return text

    result = text
    for us, uk in US_TO_UK_SPELLINGS.items():
        pattern = re.compile(re.escape(us), re.IGNORECASE)
        matches = pattern.finditer(result)
        for match in reversed(list(matches)):
            original = match.group()
            if original.isupper():
                replacement = uk.upper()
            elif original[0].isupper():
                replacement = uk.capitalize()
            else:
                replacement = uk
            result = result[:match.start()] + replacement + result[match.end():]

    return result


def verify_url(url: str, timeout: int = 5) -> bool:
    """Verify URL returns HTTP 200."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        try:
            response = requests.get(url, allow_redirects=True, timeout=timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False


def validate_brief(brief_data: Dict, url: str = None, use_uk_english: bool = True) -> Dict:
    """Validate entire brief and return validation results."""
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'fixes_applied': []
    }

    title_valid, title_msg = validate_page_title(brief_data.get('page_title', ''))
    if not title_valid:
        results['errors'].append(f"Page Title: {title_msg}")
        results['valid'] = False

    meta_valid, meta_msg = validate_meta_description(brief_data.get('meta_description', ''))
    if not meta_valid:
        results['errors'].append(f"Meta Description: {meta_msg}")
        results['valid'] = False

    headings_valid, heading_errors = validate_heading_structure(brief_data.get('headings', []))
    if not headings_valid:
        for error in heading_errors:
            results['errors'].append(f"Headings: {error}")
        results['valid'] = False

    faqs_valid, faqs_msg = validate_faqs(brief_data.get('faqs', []))
    if not faqs_valid:
        results['errors'].append(f"FAQs: {faqs_msg}")
        results['valid'] = False

    restrictions_valid, restrictions_msg = validate_restrictions(brief_data.get('restrictions', []))
    if not restrictions_valid:
        results['warnings'].append(f"Restrictions: {restrictions_msg}")

    domain = urlparse(url).netloc if url else None
    links_valid, link_errors = validate_internal_links(brief_data.get('internal_links', []), domain)
    if not links_valid:
        for error in link_errors:
            results['errors'].append(f"Internal Links: {error}")
        results['valid'] = False

    text_fields = ['page_title', 'meta_description', 'h1', 'cta']
    for field in text_fields:
        if contains_emoji(brief_data.get(field, '')):
            results['errors'].append(f"{field}: Contains emoji (not allowed)")
            results['valid'] = False

    for field in text_fields:
        if contains_em_dash(brief_data.get(field, '')):
            results['warnings'].append(f"{field}: Contains em dash (should use hyphen)")

    audience = brief_data.get('audience', [])
    if len(audience) > 2:
        results['warnings'].append(f"Audience has {len(audience)} points (maximum is 2)")

    return results


def fix_brief_issues(brief_data: Dict, use_uk_english: bool = True) -> Dict:
    """Attempt to fix common issues in brief data."""
    fixed = brief_data.copy()

    if use_uk_english:
        text_fields = ['page_title', 'meta_description', 'h1', 'cta']
        for field in text_fields:
            if field in fixed and fixed[field]:
                fixed[field] = convert_to_uk_english(fixed[field])

        for heading in fixed.get('headings', []):
            if 'text' in heading:
                heading['text'] = convert_to_uk_english(heading['text'])
            if 'description' in heading:
                heading['description'] = convert_to_uk_english(heading['description'])
            for sub in heading.get('subheadings', []):
                if 'text' in sub:
                    sub['text'] = convert_to_uk_english(sub['text'])
                if 'description' in sub:
                    sub['description'] = convert_to_uk_english(sub['description'])

    for field in ['page_title', 'meta_description', 'h1', 'cta']:
        if field in fixed and fixed[field]:
            fixed[field] = fixed[field].replace('\u2014', '-').replace('\u2013', '-')

    if 'restrictions' in fixed and len(fixed['restrictions']) > 5:
        fixed['restrictions'] = fixed['restrictions'][:5]

    if 'audience' in fixed and len(fixed['audience']) > 2:
        fixed['audience'] = fixed['audience'][:2]

    if 'faqs' in fixed:
        fixed['faqs'] = [
            faq if faq.strip().endswith('?') else faq.strip() + '?'
            for faq in fixed['faqs']
        ]

    return fixed
