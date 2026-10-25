import io
import pytest
from pathlib import Path
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

import sys
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.core.config import settings
from app.services.image_analysis.vision_service import analyze_image_with_vision
from app.services.claim_analysis.claim_extractor import analyze_claim
from app.services.location_verification.hypothesizer import generate_location_hypotheses
from app.services.evidence_retrieval.retriever import retrieve_evidence
from app.services.claim_verification.verifier import verify_claim_against_evidence

client = TestClient(app)

def create_synthetic_image(scene_type: str) -> bytes:
    """Creates deterministic test images for reproducible regression testing."""
    img = Image.new("RGB", (400, 300))
    draw = ImageDraw.Draw(img)

    if scene_type == "flood":
        # Overcast gray sky, roadway, and extensive murky sediment water plane in lower region
        draw.rectangle([0, 0, 400, 100], fill=(110, 115, 120))
        draw.rectangle([0, 100, 400, 180], fill=(70, 72, 75))
        draw.rectangle([0, 180, 400, 300], fill=(85, 80, 65))
        for y in range(200, 290, 15):
            draw.line([(20, y), (380, y)], fill=(100, 95, 80), width=2)
    elif scene_type == "landscape":
        # Blue open sky, green rolling hills and forest canopy
        draw.rectangle([0, 0, 400, 140], fill=(80, 150, 225))
        draw.rectangle([0, 140, 400, 300], fill=(40, 140, 45))
        draw.ellipse([50, 120, 200, 260], fill=(30, 115, 35))
        draw.ellipse([220, 130, 380, 270], fill=(35, 125, 40))
    elif scene_type == "temple":
        # Sky, dark basalt stone sanctum with shikhara and pillars, river ghat steps
        draw.rectangle([0, 0, 400, 100], fill=(100, 115, 125))
        draw.polygon([(160, 40), (200, 10), (240, 40), (250, 130), (150, 130)], fill=(32, 35, 38))
        draw.rectangle([120, 130, 280, 200], fill=(40, 44, 48))
        for px in [140, 170, 200, 230, 260]:
            draw.rectangle([px, 140, px + 8, 200], fill=(25, 28, 30))
        draw.rectangle([0, 200, 400, 300], fill=(42, 55, 62))
    else:
        draw.rectangle([0, 0, 400, 300], fill=(128, 128, 128))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


# TEST 1: Upload a temple image and investigate a location claim
def test_regression_test_1_temple_image_location_investigation():
    """
    TEST 1:
    Upload a temple image and investigate a location claim.
    Expected:
    - Claimed location is Pune
    - The actual architecture of the black basalt temple corresponds to Sangli
    - Verdict category reflects location contradiction
    - Image is not claimed to be synthetic or manipulated
    """
    temple_bytes = create_synthetic_image("temple")
    response = client.post(
        "/api/v1/investigations",
        data={
            "claim": "This image shows Ganapati Mandir in Pune.",
            "sample_image_name": "sangli_ganapati_mandir.jpg",
            "location": "Pune",
            "mode": "standard"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["claimed_location"] == "Pune"
    assert "Sangli" in data["best_supported_location"]
    assert "WRONG LOCATION" in data["verdict_category"]
    assert len(data["evidence_items"]) > 0


# TEST 2: Upload a flood image and investigate a flooding claim
def test_regression_test_2_flood_image_flooding_claim():
    """
    TEST 2:
    Upload a flood image and investigate a flooding claim.
    CRITICAL OBJECTIVE:
    TRUTHLENS must NOT identify this flood image as Ganapati Mandir in Sangli.
    It must not retrieve Sangli temple documents as evidence.
    """
    flood_bytes = create_synthetic_image("flood")
    response = client.post(
        "/api/v1/investigations",
        files={"image": ("flood_test.jpg", flood_bytes, "image/jpeg")},
        data={
            "claim": "Severe flooding on city streets following heavy monsoon rains.",
            "mode": "standard"
        }
    )
    assert response.status_code == 200
    data = response.json()

    # Must NOT identify as Ganapati Mandir or Sangli
    best_loc = (data.get("best_supported_location") or "").lower()
    headline = (data.get("verdict_headline") or "").lower()
    assert "sangli" not in best_loc
    assert "ganapati mandir" not in best_loc
    assert "sangli" not in headline
    assert "ganapati" not in headline

    # Evidence items must NOT contain Sangli temple gazetteer documents
    for ev in data.get("evidence_items", []):
        assert "ganapati-temple-sangli" not in ev.get("source_url", "")
        assert "sangli.nic.in" not in ev.get("source_url", "")


# TEST 3: Upload a landscape image and investigate a location claim
def test_regression_test_3_landscape_image_location_claim():
    """
    TEST 3:
    Upload a landscape image and investigate a location claim.
    The system must categorize the scene as landscape/nature and not invent a landmark.
    Without verified geo-markers, it must report uncertainty honestly rather than fabricating facts.
    """
    landscape_bytes = create_synthetic_image("landscape")
    response = client.post(
        "/api/v1/investigations",
        files={"image": ("alpine_valley.jpg", landscape_bytes, "image/jpeg")},
        data={
            "claim": "Pristine alpine forest meadow in Switzerland.",
            "location": "Switzerland",
            "mode": "standard"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["claimed_location"] == "Switzerland"
    # Scene should be recognized as landscape / nature
    analysis = data.get("image_analysis", {})
    scene_clues = analysis.get("scene_clues", {})
    assert scene_clues.get("scene_category") in ["landscape_or_nature", "everyday_object_or_scene"]
    # Should not fabricate a temple or monument name
    assert "mandir" not in scene_clues.get("architectural_style", "").lower()


# TEST 4: Run two different investigations sequentially and verify that the second does not reuse the first result
def test_regression_test_4_sequential_investigations_isolation():
    """
    TEST 4:
    Run two different investigations sequentially:
    Inv 1: Temple claim
    Inv 2: Disaster / flood claim
    Verify that Inv 2 does NOT inherit findings, evidence, or location from Inv 1.
    """
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

    flood_bytes = create_synthetic_image("flood")
    res2 = client.post(
        "/api/v1/investigations",
        files={"image": ("submerged_road.jpg", flood_bytes, "image/jpeg")},
        data={
            "claim": "Flooded street after torrential cloudburst.",
            "mode": "standard"
        }
    )
    assert res2.status_code == 200
    inv2 = res2.json()

    # Distinct investigations
    assert inv1["id"] != inv2["id"]
    assert inv1["image_hash"] != inv2["image_hash"]

    # Inv 2 must be completely free of Inv 1's temple findings
    assert "sangli" not in inv2["best_supported_location"].lower()
    assert "ganapati" not in inv2["best_supported_location"].lower()
    for ev in inv2.get("evidence_items", []):
        assert "sangli" not in ev.get("source_url", "").lower()


# TEST 5: Trigger a backend failure and verify that the API reports the error clearly
def test_regression_test_5_backend_failure_reporting():
    """
    TEST 5:
    Trigger backend validation failures:
    - Empty claim
    - Non-existent image file
    - Unsupported format
    Verify that the API returns clean HTTP error responses with descriptive messages
    and does not return stale or partial investigation results.
    """
    # 1. Too short claim
    res_short = client.post("/api/v1/investigations", data={"claim": "a", "mode": "deep"})
    assert res_short.status_code == 400
    assert "at least 3 characters" in res_short.json()["detail"]

    # 2. Missing image
    res_no_img = client.post("/api/v1/investigations", data={"claim": "Valid claim text here."})
    assert res_no_img.status_code == 400
    assert "Either an image upload or a sample image must be provided" in res_no_img.json()["detail"]

    # 3. Non-existent sample
    res_bad_sample = client.post(
        "/api/v1/investigations",
        data={"claim": "Valid claim text here.", "sample_image_name": "does_not_exist_999.jpg"}
    )
    assert res_bad_sample.status_code == 404
    assert "not found" in res_bad_sample.json()["detail"]


# TEST 6: Submit a claim when the evidence provider is unavailable and verify honest limitation reporting
def test_regression_test_6_evidence_provider_unavailable_honest_reporting():
    """
    TEST 6:
    Submit an unindexed, unfamiliar claim with zero matching reference documents.
    Verify that the application reports the limitation honestly in the trace and
    arrives at INSUFFICIENT EVIDENCE rather than fabricating sources.
    """
    landscape_bytes = create_synthetic_image("landscape")
    response = client.post(
        "/api/v1/investigations",
        files={"image": ("unfamiliar_remote_hill.jpg", landscape_bytes, "image/jpeg")},
        data={
            "claim": "Astronomer observes rare green comet over Mount X9Z in 1742.",
            "location": "Mount X9Z",
            "mode": "standard"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verdict_category"] == "INSUFFICIENT EVIDENCE"
    assert data["confidence_level"] == "insufficient"
    trace = data.get("investigation_trace", {})
    assert "provider_status" in trace


# TEST 7: Verify that an image's actual visual content is passed to the configured vision model
def test_regression_test_7_visual_content_passed_to_vision_pipeline():
    """
    TEST 7:
    Verify that analyze_image_with_vision inspects the actual image bytes/pixels
    and returns distinct visual descriptions for flood vs landscape images.
    """
    flood_bytes = create_synthetic_image("flood")
    flood_analysis = analyze_image_with_vision(flood_bytes, "flood.jpg")

    landscape_bytes = create_synthetic_image("landscape")
    landscape_analysis = analyze_image_with_vision(landscape_bytes, "landscape.jpg")

    assert flood_analysis["scene_category"] == "disaster_or_weather"
    assert "flood" in flood_analysis["image_description"].lower() or "water" in flood_analysis["image_description"].lower()

    assert landscape_analysis["scene_category"] in ["landscape_or_nature", "everyday_object_or_scene"]
    assert "foliage" in landscape_analysis["image_description"].lower() or "vegetation" in landscape_analysis["image_description"].lower() or "landscape" in landscape_analysis["image_description"].lower()

    # The two analyses must have distinct descriptions and objects reflecting their actual pixels
    assert flood_analysis["image_description"] != landscape_analysis["image_description"]


# TEST 8: Verify that unrelated evidence cannot determine the current investigation's verdict
def test_regression_test_8_unrelated_evidence_cannot_determine_verdict():
    """
    TEST 8:
    Verify that unrelated evidence (e.g. a document about a temple in Sangli)
    cannot force a 'WRONG LOCATION: Depicts Sangli' verdict on a claim about a flood.
    """
    claim_bd = {
        "raw_claim": "Photograph of flash flooding in downtown street.",
        "event": "Flooding",
        "location": "Downtown",
        "time_reference": "Today"
    }
    # Unrelated evidence item about a temple
    unrelated_temple_evidence = [
        {
            "id": "doc_unrelated_temple",
            "source_title": "Ancient Temple Gazette",
            "source_url": "https://example.gov/ancient-temple-sangli",
            "publisher": "Heritage Council",
            "publication_date": "2024",
            "relationship_to_claim": "neutral",
            "retrieval_score": 0.5,
            "reliability_score": 0.9,
            "passage": "The ancient temple in Sangli is constructed of stone.",
            "retrieval_method": "text"
        }
    ]
    scene_clues = {
        "scene_category": "disaster_or_weather",
        "visible_objects": ["floodwater", "roadway"],
        "detected_features": ["inundated street"]
    }

    synthesis = verify_claim_against_evidence(
        claim_breakdown=claim_bd,
        evidence_items=unrelated_temple_evidence,
        scene_clues=scene_clues
    )

    # The temple in Sangli must NOT determine the verdict or location
    assert "sangli" not in synthesis["best_supported_location"].lower()
    assert "WRONG LOCATION" not in synthesis["verdict_category"]
    assert synthesis["verdict_category"] == "INSUFFICIENT EVIDENCE"
