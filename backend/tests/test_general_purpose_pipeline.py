import pytest
import io
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
from fastapi.testclient import TestClient

import sys
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.claim_analysis.claim_extractor import analyze_claim, compare_claim_with_visuals
from app.services.image_analysis.vision_service import analyze_image_with_vision
from app.services.location_verification.hypothesizer import generate_location_hypotheses
from app.services.evidence_retrieval.retriever import retrieve_evidence
from app.services.claim_verification.verifier import verify_claim_against_evidence

client = TestClient(app)

def create_synthetic_test_image(scene_type: str) -> bytes:
    """Creates a deterministic synthetic test image for diverse scene types."""
    img = Image.new("RGB", (320, 240))
    draw = ImageDraw.Draw(img)

    if scene_type == "flood":
        # Top third overcast sky (muted gray), middle roadway, bottom half dark murky sediment water
        draw.rectangle([0, 0, 320, 70], fill=(120, 125, 130))
        draw.rectangle([0, 70, 320, 130], fill=(80, 82, 85))
        draw.rectangle([0, 130, 320, 240], fill=(95, 88, 70))
    elif scene_type == "fire":
        # Dark smoky sky with intense red/orange/yellow flame band
        draw.rectangle([0, 0, 320, 100], fill=(40, 35, 30))
        draw.rectangle([0, 100, 320, 200], fill=(220, 70, 20))
        draw.rectangle([0, 200, 320, 240], fill=(240, 180, 30))
    elif scene_type == "landscape":
        # Azure sky with green rolling grass/foliage
        draw.rectangle([0, 0, 320, 120], fill=(90, 150, 220))
        draw.rectangle([0, 120, 320, 240], fill=(45, 140, 50))
    elif scene_type == "document":
        # White document page with horizontal dark text lines
        draw.rectangle([0, 0, 320, 240], fill=(250, 250, 250))
        for y in range(40, 200, 20):
            draw.line([30, y, 280, y], fill=(30, 30, 30), width=3)
    else:
        # Generic everyday texture
        draw.rectangle([0, 0, 320, 240], fill=(128, 128, 128))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

def test_sequential_investigations_no_cross_contamination():
    """
    CRITICAL REQUIREMENT: Sequential Investigation Isolation.
    Investigation 1: Sangli Ganapati Mandir.
    Investigation 2: Flooded road (mumbai_flooding_2019.jpg).
    Verify that Investigation 2 NEVER inherits Sangli temple findings, evidence, or location.
    """
    # 1. First investigation: Temple
    res1 = client.post(
        "/api/v1/investigations",
        data={
            "claim": "This image shows Ganapati Mandir in Pune.",
            "sample_image_name": "sangli_ganapati_mandir.jpg",
            "location": "Pune",
            "mode": "standard"
        }
    )
    assert res1.status_code == 200
    inv1 = res1.json()
    assert "Sangli" in inv1["best_supported_location"]

    # 2. Second investigation immediately after: Flood image
    res2 = client.post(
        "/api/v1/investigations",
        data={
            "claim": "Flooding on roadway during monsoon deluge.",
            "sample_image_name": "mumbai_flooding_2019.jpg",
            "mode": "standard"
        }
    )
    assert res2.status_code == 200
    inv2 = res2.json()

    # Verify complete state and evidence isolation:
    assert inv1["id"] != inv2["id"], "Investigation IDs must be unique"
    assert inv1["image_hash"] != inv2["image_hash"], "Image hashes must differ"

    # CRITICAL: Investigation 2 must NOT mention Sangli Ganapati Mandir anywhere
    assert "sangli" not in inv2["best_supported_location"].lower()
    assert "ganapati mandir" not in inv2["best_supported_location"].lower()
    assert "sangli" not in inv2["verdict_headline"].lower()

    # Evidence items for investigation 2 must be for flood/monsoon, not Sangli temple
    for ev in inv2["evidence_items"]:
        assert "sangli.nic.in" not in ev["source_url"]
        assert "ganapati-temple-sangli" not in ev["source_url"]

def test_vision_pipeline_on_diverse_unseen_scenes():
    """
    Tests that the vision model (whether local CV or hosted) accurately distinguishes
    fundamentally different visual scenes without hardcoded heuristics.
    """
    # Flood image
    flood_bytes = create_synthetic_test_image("flood")
    flood_obs = analyze_image_with_vision(flood_bytes, "flood.jpg")
    assert flood_obs["scene_category"] in ["disaster_or_weather", "general"]
    assert any("water" in o or "flood" in o or "overcast" in o for o in [flood_obs["image_description"].lower()] + [o.lower() for o in flood_obs["visible_objects"]])

    # Fire image
    fire_bytes = create_synthetic_test_image("fire")
    fire_obs = analyze_image_with_vision(fire_bytes, "fire.jpg")
    assert any("fire" in o or "flame" in o or "smoke" in o or "thermal" in o for o in [fire_obs["image_description"].lower()] + [o.lower() for o in fire_obs["visible_objects"] + fire_obs.get("visible_activities", []) + fire_obs.get("detected_features", [])])

    # Landscape image
    landscape_bytes = create_synthetic_test_image("landscape")
    landscape_obs = analyze_image_with_vision(landscape_bytes, "landscape.jpg")
    assert landscape_obs["scene_category"] in ["landscape_or_nature", "general"]
    assert "mandir" not in landscape_obs["image_description"].lower()

    # Document image
    doc_bytes = create_synthetic_test_image("document")
    doc_obs = analyze_image_with_vision(doc_bytes, "document.jpg")
    assert doc_obs["scene_category"] in ["document_or_signboard", "screenshot_or_social_post", "general"]

def test_general_claim_parsing_diverse_types():
    """
    Tests that natural language claim parser dynamically extracts entities across
    diverse real-world claims without hardcoded assumptions.
    """
    # 1. Historical disaster claim
    c1 = analyze_claim("This photograph was taken during the 2013 Uttarakhand floods.")
    assert c1["event"] == "Floods" or "flood" in c1["event"].lower()
    assert c1["location"] == "Uttarakhand"
    assert "2013" in str(c1["time_reference"])
    assert len(c1["verification_questions"]) >= 2

    # 2. Official announcement screenshot claim
    c2 = analyze_claim("This screenshot contains an official government announcement regarding holiday.")
    assert "Announcement" in c2["event"] or "official" in c2["event"].lower() or "holiday" in c2["event"].lower()
    assert len(c2["verification_questions"]) >= 1

    # 3. AI generation claim
    c3 = analyze_claim("This picture is completely AI-generated using Midjourney.")
    assert c3["authenticity_assertion"] == "ai_generated" or "ai" in str(c3.get("authenticity_assertion", "")).lower()

    # 4. Image manipulation claim
    c4 = analyze_claim("This photograph has been heavily manipulated and photoshopped.")
    assert "manipulated" in c4["authenticity_assertion"].lower()

    # 5. Generic building claim without date or disaster
    c5 = analyze_claim("This historic Victorian building is located in Mumbai.")
    assert c5["location"] == "Mumbai"
    assert "Victorian" in c5["event"] or "Building" in c5["event"]

def test_visual_consistency_decoupling():
    """
    Verifies Stage C: Comparing user claim with visual observations.
    Recognizing floodwaters does not prove Pune; contradictory scenes are flagged.
    """
    visual_obs = {
        "scene_category": "disaster_or_weather",
        "visible_objects": ["floodwater", "submerged vehicles", "overcast sky"],
        "distinctive_visual_features": ["Deep road inundation"]
    }

    # Case A: User claims flood in Pune
    # The flood part is consistent; the Pune part requires external verification
    claim_components = analyze_claim("Flooding in Pune today.", user_location="Pune", user_date="Today")
    comp = compare_claim_with_visuals(claim_components, visual_obs)

    assert any("flood" in str(c).lower() or "water" in str(c).lower() for c in comp["consistent_parts"])
    assert any("pune" in str(c).lower() for c in comp["requires_external_verification"])

    # Case B: User claims a temple for a flood image
    claim_temple = analyze_claim("This is Ganapati Mandir in Sangli.")
    comp_temple = compare_claim_with_visuals(claim_temple, visual_obs)
    assert any("mandir" in str(c).lower() or "temple" in str(c).lower() for c in comp_temple["inconsistent_parts"])

def test_honest_abstention_on_unverifiable_uploaded_file():
    """
    Verifies that uploading an arbitrary unseen image with an unsubstantiated claim
    yields honest INSUFFICIENT EVIDENCE rather than fabricated results.
    """
    # Create an arbitrary synthetic everyday object image
    img_bytes = create_synthetic_test_image("everyday")
    
    response = client.post(
        "/api/v1/investigations",
        files={"image": ("unseen_random_sample.jpg", img_bytes, "image/jpeg")},
        data={
            "claim": "Rare antique wooden chair sold at Tokyo auction in 1920.",
            "mode": "standard"
        }
    )
    assert response.status_code == 200
    inv = response.json()

    # Must honestly abstain due to absence of ground archives
    assert inv["verdict_category"] in ["INSUFFICIENT EVIDENCE", "CLAIM CONTRADICTED — OTHER FACTUAL MISMATCH"]
    # Must NOT invent a definitive verified landmark
    assert inv["location_verification_status"] != "VERIFIED"
    assert "Tokyo" not in inv["best_supported_location"] or "Unverified" in inv["best_supported_location"] or "Unknown" in inv["best_supported_location"]
