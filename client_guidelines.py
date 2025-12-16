"""
Client-Specific Guidelines
Contains hardcoded guidelines for known clients that require special handling.
"""

from typing import Dict, Optional
from urllib.parse import urlparse


# Known client guidelines with specific rules
CLIENT_GUIDELINES = {
    "healthworkstx.com": {
        "client_name": "HealthWorks",
        "language": "UK",  # UK English spelling
        "never_include": [
            "Free consultations",
            "Complimentary anything",
            "Pricing information",
            "Insurance discussions",
            "Massage therapists (they only have a massage chair)",
            "Guarantees (guaranteed results, will cure, 100% effective)",
            "Absolute claims (no side effects, no risks, always works)",
            "Claims implying chiropractic replaces medical care",
            "Unsubstantiated detox claims",
            "Em dashes",
            "Emojis",
            "Excessive bold",
            "Years or numeric dates"
        ],
        "always_include": [
            "Orthospinology technique references",
            "Upper cervical focus (atlas C1, axis C2)",
            "Nothing rough positioning",
            "Dr. Jennifer Taylor and/or Dr. Josh Taylor credentials",
            "F3 comprehensive examination process",
            "Gentle, precise adjustment descriptions",
            "Plano, Texas location",
            "Instrument-assisted adjustments (no twisting or cracking)"
        ],
        "restrictions": [
            "No pricing information",
            "No insurance discussions",
            "No absolute claims or guarantees",
            "No free consultation mentions",
            "No claims about curing specific conditions"
        ],
        "cta": "Book your comprehensive consultation today"
    },

    "cell-gate.com": {
        "client_name": "CellGate",
        "language": "UK",  # UK English spelling
        "never_include": [
            "Direct sales/purchase options (dealer network only)",
            "Installation pricing",
            "Unsupported range claims",
            "DIY installation mentions",
            "Generic 'best in class' without proof",
            "Competitor positioning as inferior",
            "Em dashes",
            "Years or numeric dates"
        ],
        "always_include": [
            "Tagline: Wireless Where You Need It. Wired Where You Have It.",
            "Product names exactly: Watchman, OmniPoint, Entria, TrueCloud Connect, Virtual Keys",
            "Dealer-based sales model",
            "US-only sales (headquartered in Carrollton, Texas)",
            "Cloud-managed access control",
            "LoRa wireless technology (up to ~1 mile range with site-specific caveats)",
            "Route to Request a demo or Find a dealer"
        ],
        "technical_terms": [
            "DESFire EV3",
            "Bluetooth touchless entry",
            "QR codes",
            "26-bit Wiegand",
            "HID credentials",
            "Cellular and ethernet connectivity",
            "Photo capture",
            "Live video streaming",
            "Directory listings",
            "Call groups",
            "EPMs"
        ],
        "restrictions": [
            "No direct sales language (route to dealers)",
            "No installation pricing",
            "No unsupported range claims",
            "No DIY installation mentions",
            "No competitor disparagement"
        ],
        "cta": "Request a demo today"
    },

    "aim-companies.com": {
        "client_name": "AIM Companies",
        "language": "US",  # US English spelling (exception)
        "never_include": [
            "Specific legal advice about gambling/raffle laws",
            "Insurance advice requiring licensing",
            "Guarantees about claim outcomes",
            "Competitor disparagement"
        ],
        "always_include": [
            "National leader positioning (22,000+ groups insured)",
            "The 4-criteria test (planned, scheduled, approved, majority volunteer-staffed)",
            "Coverage types: General Liability, D&O, Embezzlement/Blanket Bond, Property/Inland Marine",
            "Starting prices if listed on site",
            "Phone number: 1-800-876-4044"
        ],
        "restrictions": [
            "No specific pricing beyond site-listed starting prices",
            "No guarantees about claim outcomes",
            "No legal advice on state gambling laws",
            "No competitor positioning as inferior",
            "No insurance advice requiring licensing"
        ],
        "cta": "Call 1-800-876-4044 for a quote"
    }
}


def extract_domain(url: str) -> str:
    """Extract clean domain from URL."""
    if not url:
        return ""

    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # Remove www. prefix
    if domain.startswith('www.'):
        domain = domain[4:]

    return domain


def get_client_guidelines(url: str) -> Optional[Dict]:
    """
    Get guidelines for a known client based on URL.

    Args:
        url: Website URL to check

    Returns:
        Dictionary with client guidelines if known client, None otherwise
    """
    domain = extract_domain(url)
    return CLIENT_GUIDELINES.get(domain)


def is_known_client(url: str) -> bool:
    """Check if URL belongs to a known client."""
    domain = extract_domain(url)
    return domain in CLIENT_GUIDELINES


def get_client_name_from_url(url: str) -> str:
    """
    Get client name from URL.
    For known clients, returns their official name.
    For unknown clients, extracts from domain.
    """
    guidelines = get_client_guidelines(url)
    if guidelines:
        return guidelines.get('client_name', '')

    # Extract from domain for unknown clients
    domain = extract_domain(url)
    if domain:
        # Get first part of domain and capitalize
        name = domain.split('.')[0]
        return name.replace('-', ' ').replace('_', ' ').title()

    return "Client"


def get_language_preference(url: str) -> str:
    """
    Get language preference for client.
    Most clients use UK English, AIM Companies uses US English.
    """
    guidelines = get_client_guidelines(url)
    if guidelines:
        return guidelines.get('language', 'UK')
    return 'UK'  # Default to UK English


def get_restrictions_for_brief(url: str, custom_restrictions: list = None) -> list:
    """
    Get restrictions list for brief (max 5).
    Combines known client restrictions with any custom ones.
    """
    restrictions = []

    guidelines = get_client_guidelines(url)
    if guidelines:
        restrictions.extend(guidelines.get('restrictions', []))

    if custom_restrictions:
        for r in custom_restrictions:
            if r not in restrictions:
                restrictions.append(r)

    # Return max 5 restrictions
    return restrictions[:5]


def get_default_cta(url: str) -> str:
    """Get default CTA for known client or generic one."""
    guidelines = get_client_guidelines(url)
    if guidelines:
        return guidelines.get('cta', 'Contact us today')
    return 'Contact us today'
