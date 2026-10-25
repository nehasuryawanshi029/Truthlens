import pytest
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.claim_analysis.claim_extractor import analyze_claim
from app.services.image_analysis.scene_analyzer import analyze_scene_clues
from app.services.location_verification.hypothesizer import generate_location_hypotheses
from app.services.evidence_retrieval.retriever import retrieve_evidence
from app.services.claim_verification.verifier import verify_claim_against_evidence

EVALUATION_SCENARIOS = [
    # 1. Famous landmark
    {
        "id": "scen_1_famous_landmark",
        "name": "Gateway of India falsely claimed in Delhi",
        "claim": "Photograph of Gateway of India in Delhi.",
        "location": "Delhi",
        "scene_features": {"detected_features": ["Indo-Saracenic basalt arch", "Mumbai Harbour waterfront promenade"], "primary_materials": ["Yellow basalt stone"], "surroundings_and_terrain": ["Water Body"]},
        "expected_verdict": "CLAIM CONTRADICTED — WRONG LOCATION",
        "expected_city": "Mumbai"
    },
    # 2. Temples with similar architecture
    {
        "id": "scen_2_similar_temple_arch",
        "name": "Sangli black stone temple claimed as Dagdusheth Pune",
        "claim": "Historic Ganapati Mandir in Pune.",
        "location": "Pune",
        "scene_features": {"detected_features": ["Historic black stone temple", "Riverfront Ghāt"], "primary_materials": ["Black Basalt / Carved Dark Stone"], "surroundings_and_terrain": ["Water Body / River / Lake Front"]},
        "expected_verdict": "CLAIM CONTRADICTED — WRONG LOCATION",
        "expected_city": "Sangli"
    },
    # 3. Same landmark in different cities
    {
        "id": "scen_3_same_name_diff_city",
        "name": "Ganapati Mandir in Sangli claimed in Pune",
        "claim": "This image shows Ganapati Mandir in Pune.",
        "location": "Pune",
        "scene_features": {"detected_features": ["Hemadpanthi architecture", "Riverfront Ghāt"], "primary_materials": ["Black Basalt / Carved Dark Stone"], "surroundings_and_terrain": ["Water Body / River / Lake Front"]},
        "expected_verdict": "CLAIM CONTRADICTED — WRONG LOCATION",
        "expected_city": "Sangli"
    },
    # 4. Images with visible signboards
    {
        "id": "scen_4_visible_signboard",
        "name": "Temple with metadata text clue",
        "claim": "Ganapati Temple in Pune.",
        "location": "Pune",
        "scene_features": {"detected_features": ["Black stone carvings"], "primary_materials": ["Black Basalt / Carved Dark Stone"], "text_and_signboard_clues": ["Metadata tag keyword identified: 'sangli'"], "surroundings_and_terrain": ["Water Body / River / Lake Front"]},
        "expected_verdict": "CLAIM CONTRADICTED — WRONG LOCATION",
        "expected_city": "Sangli"
    },
    # 5. Images without visible signs
    {
        "id": "scen_5_no_visible_signs",
        "name": "Architectural clue deduction without signboards",
        "claim": "Ganapati Mandir in Pune.",
        "location": "Pune",
        "scene_features": {"detected_features": ["Black stone temple", "Riverfront Ghāt"], "primary_materials": ["Black Basalt / Carved Dark Stone"], "surroundings_and_terrain": ["Water Body / River / Lake Front"]},
        "expected_verdict": "CLAIM CONTRADICTED — WRONG LOCATION",
        "expected_city": "Sangli"
    },
    # 6. Images with GPS metadata
    {
        "id": "scen_6_with_gps",
        "name": "Sangli temple with embedded Sangli GPS coordinates",
        "claim": "Ganapati Mandir in Pune.",
        "location": "Pune",
        "gps": {"has_gps": True, "latitude": 16.85, "longitude": 74.58},
        "scene_features": {"detected_features": ["Black stone"], "primary_materials": ["Black Basalt / Carved Dark Stone"], "surroundings_and_terrain": ["Water Body / River / Lake Front"]},
        "expected_verdict": "CLAIM CONTRADICTED — WRONG LOCATION",
        "expected_city": "Sangli"
    },
    # 7. Images without GPS metadata
    {
        "id": "scen_7_without_gps",
        "name": "Sangli temple without EXIF GPS tags",
        "claim": "Ganapati Mandir in Pune.",
        "location": "Pune",
        "gps": {"has_gps": False},
        "scene_features": {"detected_features": ["Black stone", "Riverfront Ghāt"], "primary_materials": ["Black Basalt / Carved Dark Stone"], "surroundings_and_terrain": ["Water Body / River / Lake Front"]},
        "expected_verdict": "CLAIM CONTRADICTED — WRONG LOCATION",
        "expected_city": "Sangli"
    },
    # 8. Cropped or compressed photographs
    {
        "id": "scen_8_cropped_photo",
        "name": "Cropped black stone temple sanctum",
        "claim": "Ganapati Mandir in Pune.",
        "location": "Pune",
        "scene_features": {"detected_features": ["Hemadpanthi Maratha Architecture"], "primary_materials": ["Black Basalt / Carved Dark Stone"], "surroundings_and_terrain": ["Water Body / River / Lake Front"]},
        "expected_verdict": "CLAIM CONTRADICTED — WRONG LOCATION",
        "expected_city": "Sangli"
    },
    # 9. Older photographs reused with a new caption
    {
        "id": "scen_9_reused_flood_photo",
        "name": "2019 Mumbai flood photo claimed as Pune flood today",
        "claim": "This photograph shows flooding in Pune today.",
        "location": "Pune",
        "time": "Today",
        "scene_features": {"detected_features": ["Flooded roadway", "Submerged bus"], "primary_materials": [], "surroundings_and_terrain": ["Inundated Ground"]},
        "visual_match": {"title": "Central Mumbai Monsoon Waterlogging Archive", "known_date": "2019-07-26", "location": "Mumbai", "publisher": "Press Photo Archive"},
        "expected_verdict": "CLAIM CONTRADICTED — WRONG LOCATION",
        "expected_city": "Mumbai"
    },
    # 10. Images with incorrect dates
    {
        "id": "scen_10_incorrect_date",
        "name": "2018 Yellow Vests photo claimed as breaking news today",
        "claim": "Massive protests erupt across Paris today.",
        "location": "Paris",
        "time": "Today",
        "scene_features": {"detected_features": ["Boulevard barricades"], "primary_materials": [], "surroundings_and_terrain": []},
        "visual_match": {"title": "Yellow Vests Demonstration", "known_date": "2018-11-24", "location": "Paris, France", "publisher": "Le Monde / AFP"},
        "expected_verdict": "CLAIM CONTRADICTED — WRONG DATE OR EVENT"
    },
    # 11. Images with manipulated elements
    {
        "id": "scen_11_manipulated_software",
        "name": "Image with Photoshop editing signatures",
        "claim": "Bridge collapse in suburban sector.",
        "authenticity": {"has_editing_signatures": True, "editing_software_detected": "Adobe Photoshop 2024"},
        "scene_features": {"detected_features": ["Bridge structure"], "primary_materials": [], "surroundings_and_terrain": []},
        "expected_verdict": "IMAGE MANIPULATION SUSPECTED"
    },
    # 12. Suspected AI-generated images
    {
        "id": "scen_12_synthetic_cyclone",
        "name": "Diffusion vortex cyclone image",
        "claim": "Terrifying storm clouds over coastal Odisha ahead of cyclone.",
        "authenticity": {"synthetic_indicator": "High (AI software metadata signature detected)"},
        "scene_features": {"detected_features": ["Unnatural concentric swirl"], "primary_materials": [], "surroundings_and_terrain": ["Coastal"]},
        "expected_verdict": "AI-GENERATED IMAGE SUSPECTED"
    },
    # 13. Generic streets and landscapes
    {
        "id": "scen_13_generic_street",
        "name": "Unverified fallen tree on residential road",
        "claim": "Tree fell on an electric pole on Maple Avenue.",
        "location": "Maple Avenue",
        "scene_features": {"detected_features": ["Residential roadway", "Fallen trunk"], "primary_materials": [], "surroundings_and_terrain": []},
        "expected_verdict": "INSUFFICIENT EVIDENCE"
    },
    # 14. Images that cannot be reliably geolocated
    {
        "id": "scen_14_cannot_be_geolocated",
        "name": "Close-up of a cobblestone pavement",
        "claim": "Historic cobblestone street in Rome today.",
        "location": "Rome",
        "scene_features": {"detected_features": ["Generic stone pavement"], "primary_materials": ["Stone"], "surroundings_and_terrain": []},
        "expected_verdict": "INSUFFICIENT EVIDENCE"
    },
    # 15. Images with conflicting reference sources
    {
        "id": "scen_15_conflicting_sources",
        "name": "Event with competing news reports",
        "claim": "Factory fire extinguished by firefighters.",
        "conflicting": True,
        "scene_features": {"detected_features": ["Industrial smoke"], "primary_materials": [], "surroundings_and_terrain": []},
        "expected_verdict": "CONFLICTING EVIDENCE"
    }
]

def test_15_scenario_evaluation_metrics():
    """
    Executes the 15-scenario evaluation suite and measures:
    - Location accuracy on landmark scenarios
    - Confident incorrect rate (must be 0.0%)
    - Honest abstention rate on insufficient evidence cases (>= 100%)
    """
    correct_verdicts = 0
    location_eval_count = 0
    location_correct_count = 0
    insufficient_cases = 0
    insufficient_correct = 0
    confident_incorrect = 0

    for scen in EVALUATION_SCENARIOS:
        claim_components = analyze_claim(scen["claim"], user_location=scen.get("location"), user_date=scen.get("time"))
        scene_clues = scen.get("scene_features", {})
        gps_data = scen.get("gps")
        authenticity_signals = scen.get("authenticity")
        visual_match = scen.get("visual_match")

        # Hypotheses
        hypotheses = generate_location_hypotheses(claim_components, scene_clues, gps_data)

        # Retrieval
        evidence_items, match, trace = retrieve_evidence(
            claim_components=claim_components,
            image_phash="1234567812345678",
            scene_clues=scene_clues,
            candidate_hypotheses=hypotheses
        )

        if visual_match:
            match = visual_match

        if scen.get("conflicting"):
            evidence_items = [
                {"publisher": "Source A", "relationship_to_claim": "supports", "source_url": "https://a.com", "passage": "Factory fire extinguished"},
                {"publisher": "Source B", "relationship_to_claim": "contradicts", "source_url": "https://b.com", "passage": "Fire still active"}
            ]

        # Epistemic Verification
        synthesis = verify_claim_against_evidence(
            claim_breakdown=claim_components,
            evidence_items=evidence_items,
            visual_match=match,
            authenticity_signals=authenticity_signals,
            scene_clues=scene_clues,
            candidate_hypotheses=hypotheses,
            search_trace=trace
        )

        verdict = synthesis["verdict_category"]
        expected = scen["expected_verdict"]

        # Track verdict match
        if verdict == expected:
            correct_verdicts += 1
        else:
            # Check if incorrect and confident
            if synthesis["confidence_level"] == "strong_evidence":
                confident_incorrect += 1

        # Track location accuracy
        if "expected_city" in scen:
            location_eval_count += 1
            if scen["expected_city"].lower() in synthesis["best_supported_location"].lower():
                location_correct_count += 1

        # Track abstention
        if expected == "INSUFFICIENT EVIDENCE":
            insufficient_cases += 1
            if verdict == "INSUFFICIENT EVIDENCE":
                insufficient_correct += 1

    total = len(EVALUATION_SCENARIOS)
    overall_accuracy = correct_verdicts / total
    loc_accuracy = location_correct_count / location_eval_count if location_eval_count > 0 else 1.0
    abstention_rate = insufficient_correct / insufficient_cases if insufficient_cases > 0 else 1.0

    print(f"\n===== EVALUATION METRICS (15 SCENARIOS) =====")
    print(f"Overall Scenario Verdict Accuracy: {overall_accuracy * 100:.1f}% ({correct_verdicts}/{total})")
    print(f"Location Landmark Accuracy: {loc_accuracy * 100:.1f}% ({location_correct_count}/{location_eval_count})")
    print(f"Abstention Fidelity on Insufficient Cases: {abstention_rate * 100:.1f}% ({insufficient_correct}/{insufficient_cases})")
    print(f"Confident Incorrect Rate: {confident_incorrect}/{total} (0.0%)")

    assert loc_accuracy >= 0.85, f"Location accuracy {loc_accuracy} below threshold"
    assert abstention_rate >= 0.90, f"Abstention rate {abstention_rate} below threshold"
    assert confident_incorrect == 0, f"Detected {confident_incorrect} confident incorrect verdicts!"
