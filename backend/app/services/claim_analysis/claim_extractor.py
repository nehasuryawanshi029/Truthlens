import re
from typing import Dict, Any, List, Optional

# Generalized semantic categories for dynamic claim deconstruction
DISASTER_KEYWORDS = [
    "flooding", "flood", "deluge", "waterlogging", "submerged", "inundation",
    "wildfire", "forest fire", "fire", "blaze", "inferno",
    "earthquake", "tremor", "quake", "aftershock",
    "cyclone", "hurricane", "typhoon", "tornado", "storm", "blizzard", "tempest",
    "landslide", "mudslide", "avalanche", "tsunami", "drought",
    "explosion", "blast", "attack", "bombing", "wreckage", "collapse", "derailment", "accident", "crash"
]

LANDMARK_KEYWORDS = [
    "mandir", "temple", "shrine", "sanctum", "mosque", "masjid", "church", "cathedral", "chapel",
    "monument", "memorial", "statue", "palace", "fort", "castle", "citadel", "ruins",
    "bridge", "tower", "minar", "minaret", "arch", "gateway", "gate", "pyramid",
    "stadium", "arena", "museum", "gallery", "parliament", "capitol", "courthouse"
]

EVENT_KEYWORDS = [
    "protest", "rally", "strike", "demonstration", "march", "riot", "gathering",
    "relief", "rescue", "aid distribution", "humanitarian", "evacuation",
    "ceremony", "inauguration", "summit", "conference", "election", "parade", "festival",
    "announcement", "press release", "briefing", "speech"
]

AUTHENTICITY_KEYWORDS = [
    "ai-generated", "ai generated", "synthetic", "diffusion", "midjourney", "dall-e",
    "manipulated", "photoshop", "photoshocked", "photoshopped", "edited", "composite",
    "deepfake", "fake", "staged", "doctored", "tampered", "authentic", "real", "genuine", "unaltered"
]

TIME_PATTERNS = [
    r'\b(?:today|yesterday|tonight|this morning|this evening|this afternoon)\b',
    r'\b(?:now|breaking|just now|recent|recently|currently|earlier today)\b',
    r'\b(?:last night|last week|this week|last month|this month|last year)\b',
    r'\b(?:in\s+)?(19\d\d|20\d\d)\b',
    r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b',
    r'\b(?:during|in)\s+(?:the\s+)?(19\d\d|20\d\d)\s+[a-z]+'
]

COMMON_ORGANIZATIONS = [
    "un ocha", "unicef", "who", "united nations", "unesco",
    "nasa", "isro", "esa", "noaa", "imd", "met office",
    "ndrf", "fema", "red cross", "crescent",
    "bbc", "cnn", "reuters", "afp", "pti", "ap",
    "police", "government", "ministry", "municipal corporation"
]

KNOWN_GLOBAL_LOCATIONS = [
    "pune", "sangli", "mumbai", "delhi", "new delhi", "bengaluru", "bangalore", "chennai", "kolkata",
    "hyderabad", "kerala", "uttarakhand", "himachal", "assam", "gujarat", "maharashtra", "odisha",
    "paris", "london", "rome", "berlin", "madrid", "barcelona", "amsterdam", "kyiv", "moscow",
    "new york", "los angeles", "chicago", "washington", "california", "florida", "texas",
    "tokyo", "beijing", "shanghai", "hong kong", "singapore", "seoul", "bangkok",
    "turkey", "türkiye", "syria", "kahramanmaraş", "kahramanmaras", "gaza", "lebanon", "pakistan", "bangladesh",
    "valencia", "champs-élysées", "champs elysees", "maple avenue", "mehrauli", "colaba"
]

def analyze_claim(claim_text: str, user_location: str = None, user_date: str = None) -> Dict[str, Any]:
    """
    STAGES C: General-Purpose Natural Language Claim Parsing Engine.
    Deconstructs circulating claims across any subject matter into discrete,
    verifiable attributes:
    - Subject or event
    - Claimed location
    - Claimed date or time
    - Named people or organizations
    - Object identity
    - Historical context
    - Authenticity or manipulation assertion
    - Dynamic verification questions
    - Ambiguity evaluation
    """
    cleaned = claim_text.strip()
    lower = cleaned.lower()

    # 1. Subject / Event Detection
    detected_event = None
    detected_category = "general_claim"

    for term in AUTHENTICITY_KEYWORDS:
        if re.search(r'\b' + re.escape(term) + r'\b', lower):
            detected_event = f"Authenticity Claim ({term.title()})"
            detected_category = "authenticity"
            break

    if not detected_event:
        for term in DISASTER_KEYWORDS:
            if re.search(r'\b' + re.escape(term) + r's?\b', lower):
                detected_event = "Floods" if term == "flood" else term.title()
                detected_category = "disaster"
                break

    if not detected_event:
        for term in LANDMARK_KEYWORDS:
            if re.search(r'\b' + re.escape(term) + r'\b', lower):
                # Check if multi-word monument like "Ganapati Mandir" or "Gateway of India"
                m_match = re.search(r'([A-Za-z\s]+(?:' + re.escape(term) + r'))', cleaned, re.IGNORECASE)
                if m_match and len(m_match.group(1).split()) <= 4:
                    detected_event = m_match.group(1).strip().title()
                else:
                    detected_event = term.title()
                detected_category = "landmark"
                break

    if not detected_event:
        for term in EVENT_KEYWORDS:
            if re.search(r'\b' + re.escape(term) + r'\b', lower):
                detected_event = term.title()
                detected_category = "news_event"
                break

    if not detected_event:
        # Check screenshot or document keywords
        if any(w in lower for w in ["screenshot", "announcement", "notice", "post", "tweet", "document", "circular"]):
            detected_event = "Official Document / Screenshot"
            detected_category = "document"
        else:
            words = cleaned.split()
            detected_event = " ".join(words[:4]).title() if len(words) > 3 else cleaned.title()

    # 2. Location Detection
    detected_location = user_location
    if not detected_location:
        # Prepositional location extraction: "in/at/near/around/from [Location]"
        loc_regex = re.search(r'\b(?:in|at|near|around|from|across|over)\s+([A-Z][a-zA-Z\u00C0-\u024F\s]{2,25}?)(?:[\.,;\?]|\s+(?:today|yesterday|this|now|during|on|in|after|before|with)|\s*$)', cleaned)
        if loc_regex:
            cand_loc = loc_regex.group(1).strip()
            # Avoid matching common prepositions or non-location words
            if cand_loc.lower() not in ["this", "that", "the", "a", "an", "an image", "a photograph", "today", "yesterday"]:
                detected_location = cand_loc.title()

    if not detected_location:
        for loc in KNOWN_GLOBAL_LOCATIONS:
            if re.search(r'\b' + re.escape(loc) + r'\b', lower):
                detected_location = loc.title()
                break

    # 3. Temporal / Date Reference Detection
    detected_time = user_date
    historical_context = None

    if not detected_time:
        for pat in TIME_PATTERNS:
            t_match = re.search(pat, lower)
            if t_match:
                detected_time = t_match.group(0).strip().capitalize()
                break

    # Historical context pattern (e.g. "2013 Uttarakhand floods", "1994 earthquake")
    hist_match = re.search(r'\b(18\d\d|19\d\d|200\d|201\d)\b', cleaned)
    if hist_match:
        historical_context = f"Historical capture context ({hist_match.group(1)})"
        if not detected_time:
            detected_time = hist_match.group(1)

    # 4. Named People and Organizations
    named_orgs = []
    for org in COMMON_ORGANIZATIONS:
        if org in lower:
            named_orgs.append(org.upper())

    # General capitalized entities
    entities = []
    cap_words = re.findall(r'\b[A-Z][a-zA-Z\u00C0-\u024F]{2,}\b', cleaned)
    stop_words = {"This", "That", "These", "Those", "Photo", "Photograph", "Image", "Picture", "Shows", "Showing", "There", "What", "When", "Where", "Today", "Yesterday"}
    for cw in cap_words:
        if cw not in stop_words and cw not in entities:
            entities.append(cw)

    # 5. Authenticity / Manipulation Claim Attributes
    is_authenticity_claim = any(ak in lower for ak in AUTHENTICITY_KEYWORDS)
    authenticity_assertion = None
    if is_authenticity_claim:
        if any(ak in lower for ak in ["ai-generated", "ai generated", "synthetic", "midjourney", "dall-e"]):
            authenticity_assertion = "Claimed to be AI-generated / synthetic"
        elif any(ak in lower for ak in ["manipulated", "photoshop", "photoshopped", "edited", "deepfake", "fake"]):
            authenticity_assertion = "Claimed to be digitally manipulated or altered"
        elif any(ak in lower for ak in ["authentic", "real", "genuine"]):
            authenticity_assertion = "Claimed to be authentic and unedited"

    # 6. Core Assertion Formulation
    assertion_parts = []
    if authenticity_assertion:
        assertion_parts.append(authenticity_assertion)
    else:
        assertion_parts.append(f"Depicts {detected_event or 'an event'}")

    if detected_location:
        assertion_parts.append(f"in {detected_location}")
    if detected_time:
        assertion_parts.append(f"dating to {detected_time.lower()}")

    core_assertion = "The circulating claim asserts this image " + " ".join(assertion_parts) + "."

    # 7. Ambiguity Evaluation
    is_ambiguous = False
    ambiguity_note = None
    words = cleaned.split()
    if len(words) <= 3 and not detected_location and not detected_time and detected_category == "general_claim":
        is_ambiguous = True
        ambiguity_note = "The claim is terse or underspecified. Verification results will evaluate general subject consistency and visual authenticity."

    # 8. Dynamic Verification Questions Formulated
    verification_questions = []
    verification_questions.append(f"1. Does the visual content of the photograph physically support the claimed subject '{detected_event}'?")
    if detected_location:
        verification_questions.append(f"2. Can the claimed geographic location '{detected_location}' be corroborated by independent architectural, municipal, or photographic archives?")
    else:
        verification_questions.append("2. What physical or topographical clues in the scene indicate its geographic origin?")

    if detected_time:
        verification_questions.append(f"3. Does documentary, meteorological, or reverse-image evidence corroborate the asserted temporal context '{detected_time}'?")

    if is_authenticity_claim or detected_category == "authenticity":
        verification_questions.append("4. Are there forensic indicators of generative AI synthesis, compression splicing, or digital manipulation?")
    else:
        verification_questions.append("4. Does the image display authentic capture metadata or signs of post-processing alteration?")

    # 9. Atomic Fact Matrix for discrete corroboration
    claimed_facts = []
    if detected_location:
        claimed_facts.append({
            "fact_type": "location",
            "claim_component": "Location Claim",
            "asserted_value": detected_location
        })
    if detected_event:
        claimed_facts.append({
            "fact_type": "event",
            "claim_component": "Landmark / Event Identity",
            "asserted_value": detected_event
        })
    if detected_time:
        claimed_facts.append({
            "fact_type": "time",
            "claim_component": "Date / Temporal Reference",
            "asserted_value": detected_time
        })
    if authenticity_assertion:
        claimed_facts.append({
            "fact_type": "authenticity",
            "claim_component": "Image Authenticity Claim",
            "asserted_value": authenticity_assertion
        })

    return {
        "event": detected_event,
        "location": detected_location,
        "time_reference": detected_time,
        "historical_context": historical_context,
        "named_organizations": named_orgs,
        "core_assertion": core_assertion,
        "extracted_entities": entities,
        "claimed_facts": claimed_facts,
        "claim_category": detected_category,
        "is_authenticity_claim": is_authenticity_claim,
        "authenticity_assertion": authenticity_assertion,
        "verification_questions": verification_questions,
        "is_ambiguous": is_ambiguous,
        "ambiguity_note": ambiguity_note,
        "raw_claim": cleaned
    }

def compare_claim_with_visuals(claim_breakdown: Dict[str, Any], scene_clues: Dict[str, Any]) -> Dict[str, Any]:
    """
    STAGE C: Dynamic Visual Consistency Analysis.
    Compares user claim directly with objective visual observations from the vision model.
    Categorizes:
    - consistent_parts: elements visually supported by the photograph
    - requires_external_verification: elements that cannot be verified by pixels alone
    - inconsistent_parts: elements directly contradicted by visual content
    - indeterminable_visually: elements requiring documentation
    """
    scene_category = scene_clues.get("scene_category", "")
    vis_objects = [o.lower() for o in scene_clues.get("visible_objects", [])]
    vis_text = [t.lower() for t in scene_clues.get("text_and_signboards", [])]
    detected_features_str = " ".join(scene_clues.get("detected_features", [])).lower()
    img_desc = scene_clues.get("image_description", "")

    claimed_event = (claim_breakdown.get("event") or "").lower()
    claimed_loc = claim_breakdown.get("location")
    claimed_time = claim_breakdown.get("time_reference")

    consistent_parts = []
    requires_external_verification = []
    inconsistent_parts = []
    indeterminable_visually = []

    # Check Event / Subject consistency
    if any(k in claimed_event for k in ["flood", "flooding", "waterlogging", "deluge", "inundation"]):
        if scene_category == "disaster_or_weather" or any("flood" in o or "water" in o for o in vis_objects):
            consistent_parts.append("Visual observations confirm street-level waterlogging and inundation.")
        else:
            inconsistent_parts.append(f"Claim asserts flooding, but visual analysis shows {scene_category.replace('_', ' ')} without waterlogging.")
    elif any(k in claimed_event for k in ["temple", "mandir", "cathedral", "church", "monument"]):
        if scene_category == "architectural_or_monument" or "facade" in detected_features_str:
            consistent_parts.append(f"Visual observations confirm architectural masonry structure.")
        elif scene_category == "disaster_or_weather" or "floodwater" in vis_objects:
            inconsistent_parts.append(f"Claim asserts {claimed_event}, but visual analysis depicts a flooded roadway/disaster scene with no temple facade.")
        else:
            requires_external_verification.append(f"Visual scene does not clearly display a prominent religious or monumental structure.")
    elif any(k in claimed_event for k in ["fire", "blaze", "wildfire"]):
        if "fire" in detected_features_str or "smoke" in detected_features_str:
            consistent_parts.append("Visual observations confirm flame combustion or particulate smoke haze.")
        else:
            inconsistent_parts.append("No smoke or flame signatures detected in the image.")
    elif any(k in claimed_event for k in ["screenshot", "announcement", "notice"]):
        if scene_category in ["screenshot_or_social_post", "document_or_signboard"]:
            consistent_parts.append("Visual observations confirm digital screenshot / formatted document layout.")
        else:
            inconsistent_parts.append("Image is a photographic capture rather than a digital document screenshot.")
    else:
        requires_external_verification.append(f"Subject '{claimed_event}' requires external evidentiary corroboration.")

    # Location cannot be visually established without geo-markers
    if claimed_loc:
        # Check if signboard or OCR text mentions the location
        text_matches = [t for t in vis_text if claimed_loc.lower() in t]
        if text_matches:
            consistent_parts.append(f"Signboard text directly references '{claimed_loc}'.")
        else:
            requires_external_verification.append(f"Location '{claimed_loc}' cannot be verified from visual appearance alone without documentary records or GPS.")
            indeterminable_visually.append(f"Geographic identity: Visual pixels do not prove {claimed_loc}.")

    # Temporal context cannot be visually established
    if claimed_time:
        requires_external_verification.append(f"Date '{claimed_time}' cannot be confirmed from image appearance alone.")
        indeterminable_visually.append("Capture date and time cannot be proven by pixels without archival or camera clock provenance.")

    return {
        "consistent_parts": consistent_parts,
        "requires_external_verification": requires_external_verification,
        "inconsistent_parts": inconsistent_parts,
        "indeterminable_visually": indeterminable_visually
    }
