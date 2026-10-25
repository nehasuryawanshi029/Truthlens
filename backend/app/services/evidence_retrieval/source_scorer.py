from typing import Dict, Any

# Reputable news agencies, academic institutions, and verified fact-checking networks
KNOWN_VERIFIED_DOMAINS = [
    "reuters.com", "apnews.com", "afp.com", "bbc.com", "thehindu.com",
    "indianexpress.com", "altnews.in", "boomlive.in", "snopes.com",
    "who.int", "un.org", "imd.gov.in", "usgs.gov", "lemonde.fr"
]

def calculate_source_reliability(
    publisher: str,
    source_url: str,
    publication_date: str = None,
    has_primary_link: bool = True,
    is_direct_quote: bool = True
) -> Dict[str, Any]:
    """
    Computes a transparent, 5-factor credibility and evidence-quality score (0.0 to 1.0).
    Never uses domain name alone as absolute proof of truth.
    """
    domain = source_url.lower().replace("https://", "").replace("http://", "").split("/")[0]
    
    # 1. Identifiable Publisher (0.25)
    score_publisher = 0.20
    is_known_wire = any(kd in domain for kd in KNOWN_VERIFIED_DOMAINS)
    if is_known_wire or len(publisher) > 2:
        score_publisher = 0.25

    # 2. Publication Date Transparency (0.20)
    score_date = 0.05
    if publication_date and publication_date != "Unknown" and len(publication_date) >= 4:
        score_date = 0.20

    # 3. Primary Evidence / Corroboration Link (0.20)
    score_primary = 0.20 if has_primary_link else 0.10

    # 4. Passage Specificity & Directness (0.20)
    score_specificity = 0.20 if is_direct_quote else 0.12

    # 5. Editorial Accountability / Domain Stance (0.15)
    score_accountability = 0.15 if is_known_wire else 0.10

    total_score = round(score_publisher + score_date + score_primary + score_specificity + score_accountability, 2)

    indicators = {
        "publisher_identifiable": True if publisher else False,
        "is_established_outlet": is_known_wire,
        "date_present": bool(publication_date and publication_date != "Unknown"),
        "primary_source_linked": has_primary_link,
        "direct_claim_relevance": is_direct_quote,
        "transparency_level": "High" if total_score >= 0.8 else ("Moderate" if total_score >= 0.6 else "Low")
    }

    return {
        "reliability_score": total_score,
        "indicators": indicators,
        "explanation": f"Source scored {int(total_score * 100)}% based on publisher provenance, clear timestamping, primary record linkage, and direct claim relevance."
    }
