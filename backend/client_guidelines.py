CLIENT_GUIDELINES = {
    "healthworkstx.com": {
        "never_include": [
            "Free consultations", "complimentary",
            "Pricing information",
            "Insurance discussions",
            "Massage therapists",
            "Guarantees", "guaranteed results", "will cure", "100% effective",
            "Absolute claims", "no side effects", "no risks", "always works",
            "Claims implying chiropractic replaces medical care",
            "Unsubstantiated detox claims",
            "Em dashes", "emojis", "excessive bold",
            "Years or numeric dates"
        ],
        "always_include": [
            "Orthospinology technique",
            "Upper cervical focus", "atlas C1", "axis C2",
            "Nothing rough",
            "Dr. Jennifer Taylor", "Dr. Josh Taylor",
            "F3 comprehensive examination",
            "Gentle, precise adjustment",
            "Plano, Texas",
            "Instrument-assisted adjustments", "no twisting or cracking"
        ],
        "restrictions": [
            "No pricing information",
            "No insurance discussions",
            "No absolute claims or guarantees",
            "No free consultation mentions",
            "No claims about curing specific conditions"
        ]
    },
    "cell-gate.com": {
        "never_include": [
            "Direct sales/purchase options",
            "Installation pricing",
            "Unsupported range claims",
            "DIY installation mentions",
            "Generic 'best in class' without proof",
            "Competitor positioning as inferior",
            "Em dashes",
            "Years or numeric dates"
        ],
        "always_include": [
            "Wireless Where You Need It. Wired Where You Have It.",
            "Watchman", "OmniPoint", "Entría", "TrueCloud Connect", "Virtual Keys",
            "Dealer-based sales model",
            "US-only sales", "headquartered in Carrollton, Texas",
            "Cloud-managed access control",
            "LoRa wireless technology",
            "Request a demo", "Find a dealer"
        ],
        "restrictions": [
            "No direct sales language (route to dealers)",
            "No installation pricing",
            "No unsupported range claims",
            "No DIY installation mentions",
            "No competitor disparagement"
        ]
    },
    "aim-companies.com": {
        "never_include": [
            "Specific legal advice about gambling/raffle laws",
            "Insurance advice requiring licensing",
            "Guarantees about claim outcomes",
            "Competitor disparagement"
        ],
        "always_include": [
            "National leader", "22,000+ groups insured",
            "The 4-criteria test",
            "General Liability", "D&O", "Embezzlement/Blanket Bond", "Property/Inland Marine",
            "Starting prices",
            "1-800-876-4044",
            "US English spelling"
        ],
        "restrictions": [
            "No specific pricing beyond site-listed starting prices",
            "No guarantees about claim outcomes",
            "No legal advice on state gambling laws",
            "No competitor positioning as inferior",
            "No insurance advice requiring licensing"
        ]
    }
}

def get_client_guidelines(domain):
    """
    Returns the guidelines for a given client domain.
    """
    return CLIENT_GUIDELINES.get(domain)
