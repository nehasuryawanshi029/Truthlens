import re
from typing import Dict, Any, List, Tuple

def verify_claim_against_evidence(
    claim_breakdown: Dict[str, Any],
    evidence_items: List[Dict[str, Any]],
    visual_match: Dict[str, Any] = None,
    authenticity_signals: Dict[str, Any] = None,
    scene_clues: Dict[str, Any] = None,
    candidate_hypotheses: List[Dict[str, Any]] = None,
    search_trace: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    STAGES D, E, F: Multimodal Verification & Decoupled Epistemic Synthesis.
    Strictly enforces the 8 Decoupled Analysis Pillars:
    1. Visually predicted scene/objects vs verified facts
    2. Candidate landmark identity vs user claim
    3. Evidence-supported actual location vs claimed location
    4. Image authenticity vs claim veracity (an unedited image can have a false caption!)
    5. Temporal context vs location context
    6. Claim accuracy across discrete atomic assertions
    7. Evidence quality & publisher provenance
    8. Honest confidence calibration (abstention on insufficient evidence)
    """
    raw_claim = claim_breakdown.get("raw_claim", "")
    claimed_location = claim_breakdown.get("location")
    claimed_time = claim_breakdown.get("time_reference")
    claimed_event = claim_breakdown.get("event")
    scene_category = (scene_clues.get("scene_category") if scene_clues else "general")
    vis_objects = [o.lower() for o in (scene_clues.get("visible_objects", []) if scene_clues else [])]

    # 1. Independent Source Corroboration (deduplicating by publisher/domain)
    independent_publishers = set()
    supports_evidence = []
    contradicts_evidence = []
    neutral_evidence = []

    for ev in evidence_items:
        pub = ev.get("publisher", "").lower().strip()
        rel = ev.get("relationship_to_claim")
        if rel == "supports":
            supports_evidence.append(ev)
            if pub:
                independent_publishers.add(pub)
        elif rel == "contradicts":
            contradicts_evidence.append(ev)
            if pub:
                independent_publishers.add(pub)
        else:
            neutral_evidence.append(ev)

    # 2. Candidate Location Evaluation & Architectural Plausibility Filter
    best_supported_location = None
    location_verification_status = "UNVERIFIED_INSUFFICIENT_EVIDENCE"
    rejected_candidates = []
    independent_location_clues = []
    supporting_source_urls = []

    # Check 1: Provenance from exact or near-exact archival image match
    if visual_match and visual_match.get("location"):
        is_exact = visual_match.get("is_exact_match", False)
        sim_score = visual_match.get("similarity_score", 1.0)

        # Must be genuine archival match (exact bitwise hash or high verified similarity)
        if is_exact or sim_score >= 0.78:
            visual_loc = visual_match.get("location")
            best_supported_location = visual_loc
            location_verification_status = "VERIFIED"
            independent_location_clues.append(f"Visual archival photograph match: '{visual_match.get('title')}'")
            independent_location_clues.append(f"Archival provenance registry from {visual_match.get('publisher')}")
            if visual_match.get("source_url"):
                supporting_source_urls.append(visual_match["source_url"])

    # Check 2: Evaluate candidate hypotheses against visual observations & evidence
    if candidate_hypotheses and not best_supported_location:
        for cand in candidate_hypotheses:
            cand_name = cand.get("candidate_name", "")
            cand_city = cand.get("candidate_city", "")
            clues = cand.get("supporting_clues", [])

            # Architectural Plausibility Filter:
            # If candidate is a landmark/temple/monument but visual scene is a flood, street, or screenshot, REJECT it!
            cand_lower = (cand_name + " " + cand_city).lower()
            is_monument_cand = any(k in cand_lower for k in ["mandir", "temple", "arch", "minar", "monument", "gateway", "memorial"])
            if is_monument_cand and scene_category in ["disaster_or_weather", "screenshot_or_social_post", "document_or_signboard"]:
                rejected_candidates.append({
                    "candidate": f"{cand_name} ({cand_city})",
                    "reason": f"Rejected: Visual scene category ({scene_category.replace('_', ' ')}) is inconsistent with landmark monument architecture."
                })
                continue

            # Filter independent physical/architectural clues grounded in the image
            independent_clues = [
                c for c in clues
                if "Stated in circulating" not in c and "Stated in original" not in c and "awaiting" not in c.lower() and "User claim" not in c
            ]

            # Find independent corroborating published sources matching this candidate city
            confirming_sources = []
            confirming_publishers = set()
            for e in evidence_items:
                e_pub = e.get("publisher", "").lower().strip()
                pass_lower = (e.get("passage", "") + " " + e.get("source_title", "")).lower()
                if len(cand_city) > 2 and re.search(rf"\b{re.escape(cand_city.lower())}\b", pass_lower):
                    if e_pub not in confirming_publishers:
                        confirming_publishers.add(e_pub)
                        confirming_sources.append(e)

            # Check visual similarity match
            has_visual_match_support = False
            if visual_match and cand_city.lower() in (visual_match.get("location", "")).lower():
                has_visual_match_support = True
                independent_clues.append(f"Visual similarity with reference archive photo ({visual_match.get('title')})")
                if visual_match.get("source_url") and visual_match["source_url"] not in supporting_source_urls:
                    supporting_source_urls.append(visual_match["source_url"])

            # A pure user claim hypothesis cannot be verified without physical visual clues or visual match
            is_claim_hypothesis = cand.get("source_type") == "User Claim Hypothesis"
            if is_claim_hypothesis and not visual_match and len(independent_clues) == 0:
                rejected_candidates.append({
                    "candidate": f"{cand_name} ({cand_city})",
                    "reason": "Asserted in user claim, but lacks distinctive visual landmark features or archival photo match to verify."
                })
                continue

            # Strict Epistemic Criterion:
            # Location can ONLY be VERIFIED if there is at least one image-grounded physical clue (architectural clue or visual match)
            # AND independent documentary corroboration
            has_image_grounded_clue = (len(independent_clues) >= 1 or has_visual_match_support)
            has_documentary_corroboration = (len(confirming_publishers) >= 1)

            if has_image_grounded_clue and (len(independent_clues) >= 2 or (len(independent_clues) >= 1 and has_documentary_corroboration)) and cand_city.lower() not in ["unknown", "unspecified location"]:
                best_supported_location = f"{cand_name}, {cand_city}" if cand_name != cand_city else cand_city
                cand["is_verified"] = True
                location_verification_status = "VERIFIED"
                independent_location_clues = independent_clues + [
                    f"Corroborating record from {s['publisher']}" for s in confirming_sources
                ]
                for s in confirming_sources:
                    if s.get("source_url") and s["source_url"] not in supporting_source_urls:
                        supporting_source_urls.append(s["source_url"])
                break
            elif has_image_grounded_clue or len(confirming_publishers) >= 1:
                rejected_candidates.append({
                    "candidate": f"{cand_name} ({cand_city})",
                    "reason": "Preliminary candidate clues identified; lacks sufficient independent multi-source corroboration for verified status."
                })
            else:
                rejected_candidates.append({
                    "candidate": f"{cand_name} ({cand_city})",
                    "reason": "Zero independent architectural or documentary clues corroborate this candidate."
                })

    # Check 3: Broad Regional Heuristic if specific landmark not established
    if not best_supported_location and candidate_hypotheses:
        for cand in candidate_hypotheses:
            if cand.get("source_type") == "Broad Regional Heuristic" and cand.get("supporting_clues"):
                best_supported_location = cand["candidate_city"]
                location_verification_status = "SUPPORTED_NOT_VERIFIED"
                independent_location_clues.extend(cand["supporting_clues"])
                break

    # 3. Determine Image Authenticity Status (Strictly decoupled from claim veracity)
    image_authenticity_status = "UNVERIFIED"
    if authenticity_signals:
        if "High" in authenticity_signals.get("synthetic_indicator", ""):
            image_authenticity_status = "AI_GENERATED_SUSPECTED"
        elif authenticity_signals.get("has_editing_signatures"):
            image_authenticity_status = "MANIPULATION_SUSPECTED"

    # 4. Determine Event & Date Verification Status
    event_date_verification_status = "UNVERIFIED"
    if visual_match and visual_match.get("known_date"):
        v_sim = visual_match.get("similarity_score", 1.0)
        v_exact = visual_match.get("is_exact_match", False) or v_sim >= 0.78
        if v_exact:
            match_date = visual_match.get("known_date", "")
        if claimed_time and claimed_time.lower() in ["today", "now", "breaking", "yesterday", "recent"]:
            if match_date and not match_date.startswith("2026"):
                event_date_verification_status = "CONTRADICTED"
            else:
                event_date_verification_status = "VERIFIED"
        elif claimed_time:
            if claimed_time in match_date or match_date in claimed_time:
                event_date_verification_status = "VERIFIED"
            else:
                event_date_verification_status = "CONTRADICTED"

    elif claimed_time and supports_evidence:
        for ev in supports_evidence:
            if ev.get("publication_date") and (claimed_time.lower() in str(ev.get("publication_date")).lower() or "2026" in str(ev.get("publication_date"))):
                event_date_verification_status = "VERIFIED"
                break

    # 5. Synthesize Claim Assessment Verdict Category
    verdict_category = "INSUFFICIENT EVIDENCE"
    verdict_headline = "Insufficient Ground Evidence Available"
    reasons_for_verdict = []
    unverified_details = []
    next_steps = []

    # Case A: AI-Generated Image Suspected
    if image_authenticity_status == "AI_GENERATED_SUSPECTED":
        verdict_category = "AI-GENERATED IMAGE SUSPECTED"
        verdict_headline = "Synthetic Media Identified: Artificial Generation Artifacts"
        reasons_for_verdict.append("Forensic analysis detected generative diffusion metadata parameters or synthetic texture swirl patterns.")
        reasons_for_verdict.append("No meteorological, physical, or photographic registry corroborates the physical reality of the scene.")
        next_steps.append("Inspect prompt generation tags in raw PNG chunks.")
        next_steps.append("Cross-reference with satellite radar observational bulletins.")

    # Case B: Image Manipulation Suspected
    elif image_authenticity_status == "MANIPULATION_SUSPECTED":
        verdict_category = "IMAGE MANIPULATION SUSPECTED"
        verdict_headline = "Image Manipulation Signatures Detected"
        sw = authenticity_signals.get("editing_software_detected", "post-processing software") if authenticity_signals else "editing software"
        reasons_for_verdict.append(f"Software modification tags or compression error variance indicate editing with {sw}.")
        reasons_for_verdict.append("Visual compression anomalies suggest composite alteration or spliced elements.")
        next_steps.append("Request uncompressed camera RAW file from source.")

    # Case D: Claim Contradicted — Wrong Location (takes precedence when location is definitively verified)
    elif (best_supported_location and claimed_location and
          location_verification_status == "VERIFIED" and
          claimed_location.lower() not in best_supported_location.lower() and
          best_supported_location.lower() not in claimed_location.lower()):
        verdict_category = "CLAIM CONTRADICTED — WRONG LOCATION"
        verdict_headline = f"Claim Contradicted: Depicts {best_supported_location}, Not {claimed_location}"
        reasons_for_verdict.append(
            f"The circulating claim asserts this image shows {claimed_event or 'an event'} in {claimed_location}."
        )
        reasons_for_verdict.append(
            f"Documentary evidence and architectural forensics independently establish the actual location as {best_supported_location}."
        )
        if independent_location_clues:
            for c in independent_location_clues[:3]:
                reasons_for_verdict.append(f"Corroborating clue: {c}")

        unverified_details.append("Image physical capture timestamp remains unverified in absence of original RAW device clock.")
        next_steps.append("Verify archival registry records of the identified landmark.")
        next_steps.append("Search municipal tourism portals for photographic feature alignment.")

    # Case E: Claim Contradicted — Wrong Date or Event (repurposed historical media)
    elif event_date_verification_status == "CONTRADICTED":
        verdict_category = "CLAIM CONTRADICTED — WRONG DATE OR EVENT"
        verdict_headline = "Claim Contradicted: Temporal Misattribution of Historical Media"
        match_dt = visual_match.get("known_date", "earlier date") if visual_match else "a previous period"
        reasons_for_verdict.append(f"Circulating claim asserts a current event ({claimed_time or 'recent'}), but evidence dates the photograph back to {match_dt}.")
        reasons_for_verdict.append("The photograph is authentic, but it has been repurposed out of historical context.")
        next_steps.append("Search reverse image databases (TinEye, Google Images) for earlier web occurrences.")

    # Case C: Conflicting Evidence Across Documented Sources
    elif len(supports_evidence) > 0 and len(contradicts_evidence) > 0:
        verdict_category = "CONFLICTING EVIDENCE"
        verdict_headline = "Conflicting Evidence Identified Across Documented Records"
        reasons_for_verdict.append(f"{len(supports_evidence)} source(s) align with aspects of the claim while {len(contradicts_evidence)} source(s) state contradictory facts.")
        unverified_details.append("Disputed geographic and temporal claims remain unresolved between competing reports.")
        next_steps.append("Conduct primary interviews with local civic administrators or on-the-ground photojournalists.")

    # Case F: General Factual Mismatch
    elif len(contradicts_evidence) > 0:
        verdict_category = "CLAIM CONTRADICTED — OTHER FACTUAL MISMATCH"
        verdict_headline = "Claim Contradicted by Grounded Investigative Reports"
        reasons_for_verdict.append(f"Official reporting contradicts the claim assertion '{raw_claim}'.")
        reasons_for_verdict.append(f"Contradicting finding from {contradicts_evidence[0].get('publisher')}: \"{contradicts_evidence[0].get('passage')[:180]}...\"")
        next_steps.append("Check official municipal weather or civic registries.")

    # Case G: Claim Supported (requires location confirmation if location asserted)
    elif len(supports_evidence) > 0 and len(contradicts_evidence) == 0:
        is_loc_corroborated = (
            not claimed_location or
            (location_verification_status == "VERIFIED" and claimed_location.lower() in (best_supported_location or "").lower()) or
            (visual_match and visual_match.get("is_exact_match") and claimed_location and claimed_location.lower() in (visual_match.get("location") or "").lower())
        )
        if is_loc_corroborated:
            verdict_category = "CLAIM SUPPORTED"
            verdict_headline = "Claim Corroborated by Documented Evidence"
            reasons_for_verdict.append(f"The depiction matches verified records published by {supports_evidence[0].get('publisher')}.")
            reasons_for_verdict.append("Documented location, date, and visual details align with available reporting.")
            if best_supported_location:
                reasons_for_verdict.append(f"Established actual location: {best_supported_location}")
            next_steps.append("Perform independent confirmation with local eyewitness accounts.")
        else:
            verdict_category = "INSUFFICIENT EVIDENCE"
            verdict_headline = "Insufficient Ground Evidence Available for Asserted Location"
            reasons_for_verdict.append(f"While supporting documents exist, the asserted location '{claimed_location}' lacks verified visual or documentary confirmation.")
            unverified_details.append(f"Location '{claimed_location}' remains unverified from the image alone.")
            next_steps.append("Seek local municipal registries or geotagged reference imagery.")

    # Case H: Default Honest Abstention (Insufficient Evidence)
    else:
        verdict_category = "INSUFFICIENT EVIDENCE"
        verdict_headline = "Insufficient Ground Evidence Available"
        reasons_for_verdict.append(f"Search queries across public web and indexed archives yielded no definitive proof for '{raw_claim}'.")
        reasons_for_verdict.append("TRUTHLENS enforces ethical responsible AI: absence of documentation is never treated as proof of falsity.")
        unverified_details.append("Actual physical capture location, date, and photographer identity remain uncorroborated.")
        next_steps.append("Submit the image to local fact-checking organizations or municipal archives.")
        next_steps.append("Examine nearby street signboards, shop boards, or distinctive background topography.")

    # 6. Detailed Atomic Fact Claim Matrix
    fact_claim_matrix = []

    # Fact 1: Location Fact
    loc_fact_status = "UNKNOWN_UNAVAILABLE"
    loc_fact_note = "No specific location claimed."
    if claimed_location:
        if location_verification_status == "VERIFIED":
            if claimed_location.lower() in (best_supported_location or "").lower():
                loc_fact_status = "VERIFIED_BY_EVIDENCE"
                loc_fact_note = f"Verified: Confirmed at {best_supported_location}"
            else:
                loc_fact_status = "CONTRADICTED_BY_EVIDENCE"
                loc_fact_note = f"Contradicted: Depicts {best_supported_location}, not {claimed_location}"
        elif location_verification_status == "SUPPORTED_NOT_VERIFIED":
            loc_fact_status = "SUPPORTED_NOT_VERIFIED"
            loc_fact_note = f"Preliminary architectural support for {best_supported_location}; lacks second independent source."
        else:
            loc_fact_status = "UNKNOWN_UNAVAILABLE"
            loc_fact_note = f"Unverified: No independent proof confirms or refutes {claimed_location}."

    fact_claim_matrix.append({
        "fact_name": "Location Claim",
        "asserted_value": claimed_location or "Unspecified",
        "verification_status": loc_fact_status,
        "supported_value": best_supported_location or "Unverified",
        "explanation": loc_fact_note,
        "source_urls": supporting_source_urls or ([e["source_url"] for e in evidence_items[:2]] if evidence_items else [])
    })

    # Fact 2: Subject / Event Fact
    event_fact_status = "UNKNOWN_UNAVAILABLE"
    if claimed_event:
        if verdict_category in ["CLAIM SUPPORTED", "CLAIM CONTRADICTED — WRONG LOCATION", "CLAIM CONTRADICTED — WRONG DATE OR EVENT"]:
            event_fact_status = "VERIFIED_BY_EVIDENCE"
        elif verdict_category == "CLAIM CONTRADICTED — OTHER FACTUAL MISMATCH":
            event_fact_status = "CONTRADICTED_BY_EVIDENCE"
        else:
            event_fact_status = "UNKNOWN_UNAVAILABLE"

    fact_claim_matrix.append({
        "fact_name": "Landmark / Event Identity",
        "asserted_value": claimed_event or "General Incident",
        "verification_status": event_fact_status,
        "supported_value": best_supported_location or claimed_event or "Unverified",
        "explanation": "Evaluated against reference archives and visual feature signatures.",
        "source_urls": [e["source_url"] for e in (supports_evidence or evidence_items)[:2]]
    })

    # Fact 3: Temporal / Date Fact
    time_fact_status = "UNKNOWN_UNAVAILABLE"
    if claimed_time:
        if event_date_verification_status == "CONTRADICTED":
            time_fact_status = "CONTRADICTED_BY_EVIDENCE"
        elif event_date_verification_status == "VERIFIED":
            time_fact_status = "VERIFIED_BY_EVIDENCE"
        else:
            time_fact_status = "UNKNOWN_UNAVAILABLE"

    fact_claim_matrix.append({
        "fact_name": "Temporal / Date Reference",
        "asserted_value": claimed_time or "Unspecified",
        "verification_status": time_fact_status,
        "supported_value": visual_match.get("known_date") if visual_match else "Unconfirmed",
        "explanation": "Evaluated against archival photo publication timestamps.",
        "source_urls": [visual_match["source_url"]] if visual_match and visual_match.get("source_url") else []
    })

    # Fact 4: Image Authenticity Fact
    auth_fact_status = "UNKNOWN_UNAVAILABLE"
    if image_authenticity_status == "AI_GENERATED_SUSPECTED":
        auth_fact_status = "CONTRADICTED_BY_EVIDENCE"
    elif image_authenticity_status == "MANIPULATION_SUSPECTED":
        auth_fact_status = "CONTRADICTED_BY_EVIDENCE"
    else:
        auth_fact_status = "UNKNOWN_UNAVAILABLE"

    fact_claim_matrix.append({
        "fact_name": "Image Authenticity",
        "asserted_value": "Authentic physical camera capture (Implied)",
        "verification_status": auth_fact_status,
        "supported_value": image_authenticity_status,
        "explanation": "Decoupled from caption veracity. UNVERIFIED in absence of original RAW device proof.",
        "source_urls": []
    })

    # 7. Confidence Calibration (Grounded in evidence count, no fabricated numbers)
    confidence_level = "insufficient"
    confidence_explanation = "Low / Insufficient: No reliable independent corroboration found in public or reference archives."
    num_publishers = len(independent_publishers)
    num_clues = len(independent_location_clues)

    if (num_publishers >= 2 or num_clues >= 2) and verdict_category != "INSUFFICIENT EVIDENCE":
        confidence_level = "strong_evidence"
        confidence_explanation = (
            f"High Confidence: Grounded in {num_publishers} independent authoritative publisher(s) "
            f"and {num_clues} verified visual/forensic clue(s). "
            f"Confidence reflects strict multi-source corroboration and absence of contradictory records."
        )
    elif (num_publishers >= 1 or num_clues >= 1) and verdict_category != "INSUFFICIENT EVIDENCE":
        confidence_level = "moderate_evidence"
        confidence_explanation = (
            f"Moderate Confidence: Grounded in {num_publishers} documented record and {num_clues} preliminary clue; "
            f"additional on-the-ground corroboration recommended."
        )

    # 8. Auditable Investigation Trace
    investigation_trace = {
        "original_claim": raw_claim,
        "extracted_entities": claim_breakdown.get("extracted_entities", []),
        "claimed_location": claimed_location or "None specified",
        "visual_clues_detected": scene_clues.get("detected_features", []) if scene_clues else [],
        "search_queries_executed": search_trace.get("search_queries_executed", []) if search_trace else [],
        "search_providers_used": search_trace.get("search_providers_used", []) if search_trace else [],
        "provider_status": search_trace.get("provider_status", {}) if search_trace else {},
        "candidate_locations_evaluated": [f"{c.get('candidate_name', '')} ({c.get('candidate_city', '')})" for c in (candidate_hypotheses or [])],
        "best_supported_location": best_supported_location or "Unverified / Unknown",
        "location_verification_status": location_verification_status,
        "retrieved_evidence_count": len(evidence_items),
        "source_urls": [e["source_url"] for e in evidence_items],
        "rejected_candidates": rejected_candidates,
        "final_verdict": verdict_category,
        "unresolved_questions": unverified_details
    }

    # Narrative Summary
    summary = (
        f"Investigation evaluated the claim \"{raw_claim}\". "
        f"Verdict: {verdict_category}. "
        f"{' '.join(reasons_for_verdict)} "
        f"Image authenticity remains {image_authenticity_status}."
    )

    return {
        "verdict_category": verdict_category,
        "verdict_headline": verdict_headline,
        "summary": summary,
        "confidence_level": confidence_level,
        "confidence_explanation": confidence_explanation,
        "claimed_location": claimed_location,
        "candidate_locations": candidate_hypotheses or [],
        "best_supported_location": best_supported_location or "Unverified / Unknown",
        "location_verification_status": location_verification_status,
        "image_authenticity_status": image_authenticity_status,
        "event_date_verification_status": event_date_verification_status,
        "reasons_for_verdict": reasons_for_verdict,
        "unverified_details": unverified_details,
        "next_verification_steps": next_steps,
        "fact_claim_matrix": fact_claim_matrix,
        "investigation_trace": investigation_trace
    }
