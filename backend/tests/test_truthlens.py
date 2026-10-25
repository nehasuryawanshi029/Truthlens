import pytest
from pathlib import Path
from fastapi.testclient import TestClient

import sys
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.claim_analysis.claim_extractor import analyze_claim
from app.services.evidence_retrieval.source_scorer import calculate_source_reliability
from app.services.claim_verification.verifier import verify_claim_against_evidence
from app.services.image_analysis.metadata_extractor import extract_image_metadata
from app.services.image_analysis.scene_analyzer import analyze_scene_clues
from app.services.location_verification.hypothesizer import generate_location_hypotheses

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "TRUTHLENS" in data["service"]

def test_capabilities_endpoint():
    response = client.get("/api/v1/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["visual_similarity"] is True
    assert data["exif_inspection"] is True
    assert data["scene_forensics"] is True
    assert data["landmark_hypothesizer"] is True

def test_demo_cases_includes_sangli_temple():
    response = client.get("/api/v1/demo-cases")
    assert response.status_code == 200
    cases = response.json()
    case_ids = [c["id"] for c in cases]
    assert "demo_sangli_temple" in case_ids

def test_claim_extractor_pune_flood():
    claim = "This photograph shows flooding in Pune today."
    res = analyze_claim(claim)
    assert res["event"] == "Flooding"
    assert res["location"] == "Pune"
    assert res["time_reference"] == "Today"

def test_source_reliability_scoring():
    res = calculate_source_reliability(
        publisher="Reuters Fact Check",
        source_url="https://www.reuters.com/fact-check/article-123",
        publication_date="2024-05-10"
    )
    assert res["reliability_score"] >= 0.80
    assert res["indicators"]["publisher_identifiable"] is True

def test_verifier_insufficient_evidence():
    claim_bd = {"raw_claim": "Alien spaceship landed in park", "event": "Alien", "location": "Park"}
    synthesis = verify_claim_against_evidence(
        claim_breakdown=claim_bd,
        evidence_items=[]
    )
    assert synthesis["verdict_category"] == "INSUFFICIENT EVIDENCE"
    assert synthesis["confidence_level"] == "insufficient"

def test_ganapati_mandir_sangli_vs_pune_regression():
    """
    CRITICAL REGRESSION TEST:
    User claim: 'This image shows Ganapati Mandir in Pune.'
    Uploaded image: Photograph of the historic black basalt stone Ganapati Mandir in Sangli.
    Expected:
    - Pune identified as claimed location
    - Sangli identified as candidate/actual location
    - Verdict: CLAIM CONTRADICTED — WRONG LOCATION
    - Image authenticity: UNVERIFIED
    - Evidence items retrieved with real source URLs
    """
    response = client.post(
        "/api/v1/investigations",
        data={
            "claim": "This image shows Ganapati Mandir in Pune.",
            "sample_image_name": "sangli_ganapati_mandir.jpg",
            "location": "Pune",
            "mode": "deep"
        }
    )
    assert response.status_code == 200
    inv = response.json()
    
    assert inv["claimed_location"] == "Pune"
    assert "Sangli" in inv["best_supported_location"]
    assert inv["verdict_category"] == "CLAIM CONTRADICTED — WRONG LOCATION"
    assert inv["image_authenticity_status"] == "UNVERIFIED"
    assert len(inv["evidence_items"]) >= 1
    assert "maharashtratourism" in inv["evidence_items"][0]["source_url"] or "sangli.nic.in" in inv["evidence_items"][0]["source_url"]
    assert "investigation_trace" in inv
    assert len(inv["investigation_trace"]["search_queries_executed"]) >= 1

def test_research_lab_endpoint():
    response = client.get("/api/v1/research-lab")
    assert response.status_code == 200
    data = response.json()
    assert "projection_points" in data
    assert "evaluation_metrics" in data
