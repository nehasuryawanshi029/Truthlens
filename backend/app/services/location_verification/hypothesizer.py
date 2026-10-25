from typing import Dict, Any, List
from app.core.config import settings

# Curated reference catalog of verified landmark architectural profiles for candidate disambiguation
LANDMARK_CATALOG = [
    {
        "id": "sangli_ganapati_mandir",
        "name": "Ganapati Mandir, Sangli",
        "city": "Sangli",
        "state": "Maharashtra",
        "district": "Sangli",
        "architectural_style": "Historic Black Basalt Stone Temple with Carved Pillars & Riverfront Ghāt",
        "built_by": "Thorle Chintamanrao Patwardhan (1843)",
        "surroundings": "On the banks of Krishna River with stone steps (ghāts)",
        "key_visual_clues": [
            "Black Basalt / Carved Dark Stone",
            "Hemadpanthi / Maratha Architecture",
            "Riverfront Ghāt / Water Steps",
            "Historic black stone temple"
        ]
    },
    {
        "id": "dagdusheth_ganapati_pune",
        "name": "Shreemant Dagdusheth Halwai Ganapati Temple",
        "city": "Pune",
        "state": "Maharashtra",
        "district": "Pune",
        "architectural_style": "Multi-Story Modern Urban Temple with Gold & Marble Sanctum",
        "built_by": "Dagdusheth Gadve & Laxmibai (1893)",
        "surroundings": "Dense commercial city street (Budhwar Peth, Shivaji Road)",
        "key_visual_clues": [
            "Modern urban street facade",
            "White Marble / Light Polished Stone",
            "Golden dome and ornate glass chandeliers",
            "No river or open water ghāt directly adjoining"
        ]
    },
    {
        "id": "kasba_ganapati_pune",
        "name": "Shri Kasba Ganapati Mandir (Gramdaivat)",
        "city": "Pune",
        "state": "Maharashtra",
        "district": "Pune",
        "architectural_style": "Historic Peshwa-era Sanctum with Wooden Sabhamandapa",
        "built_by": "Chhatrapati Shivaji Maharaj & Jijabai (1639)",
        "surroundings": "Historic residential core of Kasba Peth, Pune",
        "key_visual_clues": [
            "Enclosed courtyard sanctum",
            "Wooden pillar sabhamandapa",
            "Narrow residential alleyway location"
        ]
    },
    {
        "id": "gateway_of_india",
        "name": "Gateway of India",
        "city": "Mumbai",
        "state": "Maharashtra",
        "district": "Mumbai",
        "architectural_style": "Indo-Saracenic Basalt Triumphal Arch",
        "built_by": "George Wittet (1924)",
        "surroundings": "Mumbai Harbour waterfront facing the Arabian Sea",
        "key_visual_clues": [
            "Indo-Saracenic basalt arch",
            "Indo-Saracenic / Triumphal Arch",
            "Yellow basalt stone",
            "Mumbai Harbour waterfront promenade",
            "Waterfront promenade / Sea vista"
        ]
    },
    {
        "id": "india_gate_delhi",
        "name": "India Gate War Memorial",
        "city": "Delhi",
        "state": "Delhi",
        "district": "New Delhi",
        "architectural_style": "Memorial Triumphal Arch in Red and Pale Sandstone",
        "built_by": "Sir Edwin Lutyens (1931)",
        "surroundings": "Kartavya Path ceremonial avenue with open lawns and fountains",
        "key_visual_clues": [
            "Red Sandstone / Terracotta Brick",
            "Ceremonial boulevard / Lawns",
            "No sea or maritime harbour"
        ]
    },
    {
        "id": "qutub_minar",
        "name": "Qutub Minar",
        "city": "Delhi",
        "state": "Delhi",
        "district": "South Delhi",
        "architectural_style": "Fluted Red Sandstone and Marble Victory Tower",
        "built_by": "Qutb-ud-din Aibak (1199)",
        "surroundings": "Mehrauli Archaeological Park",
        "key_visual_clues": [
            "Tapering fluted minaret / Victory Tower",
            "Red Sandstone / Terracotta Brick",
            "Ruined arcades / Iron Pillar courtyard"
        ]
    }
]

def generate_location_hypotheses(
    claim_components: Dict[str, Any],
    scene_clues: Dict[str, Any],
    gps_data: Dict[str, Any] = None,
    image_path: str = None
) -> List[Dict[str, Any]]:
    """
    Stage B: Generates candidate landmark and location hypotheses.
    Enforces the Decoupling Principle:
    - Never assumes every image depicts a landmark or news event.
    - Disasters, floods, screenshots, and everyday scenes are NEVER forced into a landmark template.
    - Only evaluates architectural landmark catalog if the scene is genuinely architectural or the claim mentions a monument.
    - Records candidate hypotheses separately from verified evidence.
    - Honest abstention for unanchored or unfamiliar locations.
    """
    candidates = []
    claimed_location = (claim_components.get("location") or "").lower()
    raw_claim = (claim_components.get("raw_claim") or "").lower()
    claimed_event = (claim_components.get("event") or "").lower()
    scene_category = scene_clues.get("scene_category", "")

    # Aggregate scene observations
    scene_features_list = scene_clues.get("detected_features", []) + scene_clues.get("primary_materials", [])
    scene_features_str = " ".join(scene_features_list).lower()
    scene_surroundings_str = " ".join(scene_clues.get("surroundings_and_terrain", [])).lower()
    text_clues_str = " ".join(scene_clues.get("text_and_signboard_clues", [])).lower()
    vis_objects_str = " ".join(scene_clues.get("visible_objects", [])).lower()

    # Determine if scene or claim is architectural
    # CRITICAL SAFEGUARD: If image is clearly a flood, disaster, or screenshot, DO NOT match random temples!
    is_non_landmark_scene = (
        scene_category in ["disaster_or_weather", "screenshot_or_social_post", "document_or_signboard"] or
        ("flood" in vis_objects_str and "temple" not in raw_claim and "mandir" not in raw_claim) or
        ("waterlogging" in vis_objects_str and "temple" not in raw_claim and "mandir" not in raw_claim)
    )

    is_monument_mentioned = any(k in raw_claim for k in ["mandir", "temple", "gateway", "minar", "monument", "memorial", "arch", "church", "cathedral", "mosque"])
    is_architectural_context = (scene_category == "architectural_or_monument" or is_monument_mentioned) and not is_non_landmark_scene

    # 1. Evaluate known landmarks in catalog ONLY when architectural context exists and it's not a disaster scene
    if is_architectural_context:
        for landmark in LANDMARK_CATALOG:
            clues_matched = []
            name_lower = landmark["name"].lower()
            city_lower = landmark["city"].lower()

            # Check if landmark name tokens appear in claim
            name_tokens = ["ganapati", "ganpati", "mandir", "temple", "gateway", "india", "minar", "qutub"]
            has_name_overlap = any(token in raw_claim for token in name_tokens if token in name_lower)

            # Check architectural clue matches against scene analysis
            for kv in landmark["key_visual_clues"]:
                kv_lower = kv.lower()
                terms = [t.strip() for t in kv_lower.split(" / ")]
                if any(term in scene_features_str or term in scene_surroundings_str for term in terms):
                    clues_matched.append(f"Visual architectural match: {kv}")

            # Check if signboard or OCR text mentions landmark or city
            if city_lower in text_clues_str:
                clues_matched.append(f"Signboard text directly identifies city: '{landmark['city']}'")
            if any(token in text_clues_str for token in name_tokens if token in name_lower):
                clues_matched.append(f"Signboard text mentions landmark token matching {landmark['name']}")

            # Check GPS coordinates
            if gps_data and gps_data.get("has_gps"):
                lat = gps_data.get("latitude")
                lon = gps_data.get("longitude")
                if city_lower == "sangli" and lat and 16.5 < lat < 17.2 and lon and 74.2 < lon < 74.9:
                    clues_matched.append("GPS coordinates correlate with Sangli district geographic bounds")
                elif city_lower == "pune" and lat and 18.2 < lat < 18.8 and lon and 73.5 < lon < 74.2:
                    clues_matched.append("GPS coordinates correlate with Pune metropolitan bounds")
                elif city_lower == "mumbai" and lat and 18.8 < lat < 19.3 and lon and 72.7 < lon < 73.1:
                    clues_matched.append("GPS coordinates correlate with Mumbai coastal bounds")
                elif city_lower == "delhi" and lat and 28.3 < lat < 28.9 and lon and 76.8 < lon < 77.4:
                    clues_matched.append("GPS coordinates correlate with Delhi National Capital Region")

            # Same-name landmark disambiguation (e.g. Ganapati Mandir in Sangli vs Pune)
            is_same_name_alternative = ("ganapati" in raw_claim or "ganpati" in raw_claim) and landmark["id"] in ["sangli_ganapati_mandir", "dagdusheth_ganapati_pune", "kasba_ganapati_pune"]
            is_gateway_alternative = ("gateway" in raw_claim or "india gate" in raw_claim) and landmark["id"] in ["gateway_of_india", "india_gate_delhi"]

            # Must have name overlap, same-name alternative, GPS clue, or (if claim is investigating a monument) >= 2 visual clues
            qualifies = (
                (has_name_overlap and len(clues_matched) >= 1) or
                is_same_name_alternative or
                is_gateway_alternative or
                (gps_data and gps_data.get("has_gps") and len(clues_matched) >= 1) or
                (is_monument_mentioned and len(clues_matched) >= 2)
            )

            if qualifies:
                conf = "high" if len(clues_matched) >= 2 else ("moderate" if len(clues_matched) == 1 else "low")
                supporting = clues_matched if clues_matched else [f"Plausible alternative candidate bearing name in {landmark['city']}"]
                if city_lower == claimed_location and not clues_matched:
                    supporting = ["Stated in original user claim; awaiting architectural verification"]

                candidates.append({
                    "id": landmark["id"],
                    "candidate_name": landmark["name"],
                    "candidate_city": landmark["city"],
                    "candidate_state": landmark["state"],
                    "supporting_clues": supporting,
                    "source_type": "Visual Scene Clues & Architectural Match" if clues_matched else "Known Same-Name Candidate Disambiguation",
                    "is_verified": False,
                    "match_confidence": conf
                })

    # 2. If user claimed a specific location or event, include it as a dedicated hypothesis to investigate
    if claimed_location and not any(c["candidate_city"].lower() == claimed_location for c in candidates):
        event_name = claim_components.get("event") or "Claimed Incident / Site"
        candidates.append({
            "id": f"claim_candidate_{claimed_location.replace(' ', '_').lower()}",
            "candidate_name": f"{event_name} in {claimed_location.title()}",
            "candidate_city": claimed_location.title(),
            "candidate_state": "Pending Independent Evidence",
            "supporting_clues": ["Stated in circulating user claim; requires independent corroboration"],
            "source_type": "User Claim Hypothesis",
            "is_verified": False,
            "match_confidence": "low"
        })

    # 3. For non-landmark or unanchored scenes, provide an honest, unanchored hypothesis
    if not candidates:
        if is_non_landmark_scene or "disaster" in scene_category:
            desc = "Disaster / Environmental Event" if "disaster" in scene_category else "Unanchored Ground Event"
            candidates.append({
                "id": "unanchored_event_scene",
                "candidate_name": desc,
                "candidate_city": (claim_components.get("location") or "Unspecified Location").title(),
                "candidate_state": "Unverified Ground",
                "supporting_clues": [f"Scene identified as {scene_category.replace('_', ' ')}; specific location requires documentary corroboration"],
                "source_type": "Event Scene Hypothesis",
                "is_verified": False,
                "match_confidence": "low"
            })
        else:
            candidates.append({
                "id": "unanchored_scene",
                "candidate_name": "Unanchored Location",
                "candidate_city": "Unknown / Insufficient Distinctive Landmarks",
                "candidate_state": "Unverified",
                "supporting_clues": ["Scene lacks unique monumental, geographical, or architectural landmarks to verify location independently"],
                "source_type": "Honest Abstention Hypothesis",
                "is_verified": False,
                "match_confidence": "low"
            })

    return candidates
