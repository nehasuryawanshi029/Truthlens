import os
import shutil
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.db.models import Investigation, EvidenceItem, ImageAnalysisResult, ClaimBreakdown, generate_uuid
from app.schemas.investigation import (
    InvestigationOut, InvestigationSummaryOut, CapabilitiesOut,
    AssistantQueryRequest, AssistantQueryResponse
)
from app.services.image_analysis.metadata_extractor import extract_image_metadata
from app.services.image_analysis.scene_analyzer import analyze_scene_clues
from app.services.image_analysis.privacy_stripper import strip_image_metadata
from app.services.claim_analysis.claim_extractor import analyze_claim, compare_claim_with_visuals
from app.services.location_verification.hypothesizer import generate_location_hypotheses
from app.services.evidence_retrieval.retriever import retrieve_evidence
from app.services.claim_verification.verifier import verify_claim_against_evidence
from app.services.report_generation.pdf_exporter import generate_pdf_report
from app.services.assistant.research_assistant import answer_research_question
from app.services.embeddings.projection import get_research_lab_data
from app.services.image_analysis.ai_detector import get_ai_detector

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/model-info")
def get_model_info():
    detector = get_ai_detector()
    return {
        "model_name": detector.model_name,
        "is_available": detector.is_available(),
        "load_error": detector.get_load_error(),
        "device": detector.device,
        "labels": detector.id2label,
        "supported_formats": settings.ALLOWED_IMAGE_EXTENSIONS,
        "max_upload_size_mb": settings.MAX_UPLOAD_SIZE_MB
    }

@router.post("/detect")
async def detect_ai_image(file: UploadFile = File(...)):
    """
    TRUTHLENS AI Image Authenticity Detector:
    Validates uploaded image and runs actual model inference to classify
    as likely AI-generated, likely real photograph, or uncertain.
    """
    detector = get_ai_detector()
    if not detector.is_available():
        raise HTTPException(
            status_code=503,
            detail=f"Model initialization failure: {detector.get_load_error() or 'Pretrained model is unavailable'}"
        )

    # 1. Validate file extension
    filename = file.filename or "uploaded_image"
    ext = Path(filename).suffix.lower()
    allowed_exts = [e.lower() for e in settings.ALLOWED_IMAGE_EXTENSIONS]
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported formats are: {', '.join(allowed_exts).upper()}"
        )

    # 2. Read bytes and validate size
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {str(e)}")

    if not contents or len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Uploaded file size ({len(contents) / (1024*1024):.2f}MB) exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    # 3. Run inference with actual model
    try:
        result = detector.detect_image(contents, filename=filename)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failure: {str(e)}")


@router.get("/capabilities", response_model=CapabilitiesOut)
def get_system_capabilities():
    has_vision = settings.has_vision_api()
    vision_model_desc = f"Google Gemini Vision ({settings.VISION_MODEL})" if settings.get_gemini_key() else (
        "OpenAI-compatible Vision API" if settings.OPENAI_API_KEY else "TruthLens Local Forensic Vision Pipeline (Pillow/NumPy/SciPy spatial decomposition & texture frequency)"
    )
    return CapabilitiesOut(
        visual_similarity=True,
        exif_inspection=True,
        scene_forensics=True,
        landmark_hypothesizer=True,
        claim_decomposition=True,
        evidence_retrieval_local=True,
        evidence_retrieval_web=True,  # Live Wikipedia + Live DuckDuckGo web search
        external_llm=has_vision,
        pdf_export=True,
        active_models={
            "vision_model": vision_model_desc,
            "scene_forensics": "General-Purpose Spatial-Frequency & Material Inspector",
            "landmark_hypothesizer": "Selective Architectural Reasoner with Epistemic Abstention",
            "retriever": "Hybrid TF-IDF + Live DuckDuckGo Web Search + Live Wikipedia Adapter",
            "claim_parser": "General-Purpose Natural Language & Entity Attribute Deconstructor",
            "verifier": "Multi-Stage Epistemic Synthesizer with 8 Decoupled Pillars"
        },
        disclaimer="TRUTHLENS never presents AI guesses as verified facts. All claims require independent multi-source corroboration before verification."
    )

@router.get("/demo-cases")
def get_demo_cases():
    """Returns curated benchmark sample cases ready for instant exploration."""
    return [
        {
            "id": "demo_sangli_temple",
            "title": "Ganapati Mandir Location Misattribution",
            "claim": "This image shows Ganapati Mandir in Pune.",
            "image_url": "/samples/sangli_ganapati_mandir.jpg",
            "location": "Pune",
            "date": "Historical / Recent Post",
            "source_type": "Social Media Misinformation Post",
            "case_type": "Spatial Landmark Misattribution",
            "description": "Circulating image claimed to depict the famous Ganapati Mandir in Pune. Architectural forensics and MTDC records reveal it is the black stone riverside temple in Sangli."
        },
        {
            "id": "demo_pune_floods",
            "title": "Pune Flood Viral Miscaptioning",
            "claim": "This photograph shows flooding in Pune today.",
            "image_url": "/samples/mumbai_flooding_2019.jpg",
            "location": "Pune",
            "date": "Today",
            "source_type": "Social Media (X/WhatsApp viral post)",
            "case_type": "Temporal & Spatial Misattribution",
            "description": "Circulating image claimed to depict unprecedented current monsoon inundation in Pune, India. In reality, the photo was taken during the July 2019 Mumbai monsoon."
        },
        {
            "id": "demo_synthetic_cyclone",
            "title": "AI-Generated Coastal Cyclone",
            "claim": "Terrifying storm clouds forming over coastal Odisha ahead of cyclone.",
            "image_url": "/samples/synthetic_cyclone.jpg",
            "location": "Odisha",
            "date": "Today",
            "source_type": "Viral TikTok / Instagram Reel",
            "case_type": "Synthetic Media / Diffusion Artifice",
            "description": "Dramatic spiraling vortex clouds claimed to be radar-verified storm approaching Odisha. Satellite radar and diffusion prompt metadata reveal synthetic creation."
        },
        {
            "id": "demo_earthquake_relief",
            "title": "Turkey Earthquake Aid Distribution",
            "claim": "Relief workers and search teams distribute food and medical aid following the earthquake in Kahramanmaras.",
            "image_url": "/samples/turkey_earthquake_relief.jpg",
            "location": "Kahramanmaraş",
            "date": "February 2023",
            "source_type": "Humanitarian Field Dispatch",
            "case_type": "Supported Authentic Event",
            "description": "Documentary capture of international aid distribution in southern Turkey. Corroborated by UN OCHA and disaster relief situation reports."
        },
        {
            "id": "demo_paris_protest",
            "title": "Paris Protest Misattribution",
            "claim": "Massive protests erupt across Paris today with thousands taking over the Champs-Élysées.",
            "image_url": "/samples/paris_protest_2018.jpg",
            "location": "Paris",
            "date": "Today",
            "source_type": "Breaking News Aggregator",
            "case_type": "Temporal Misattribution",
            "description": "Authentic photo from the 2018 Yellow Vests protests shared as breaking current events in Paris."
        },
        {
            "id": "demo_fallen_tree_insufficient",
            "title": "Unverified Local Tree Collapse",
            "claim": "Tree fell on an electric pole on Maple Avenue after strong winds.",
            "image_url": "/samples/local_fallen_tree.jpg",
            "location": "Maple Avenue",
            "date": "Yesterday",
            "source_type": "Neighborhood Forum",
            "case_type": "Insufficient Ground Evidence",
            "description": "Real photo with hyper-local claim that lacks public news or civic records. Platform transparently abstains."
        }
    ]

@router.post("/investigations", response_model=InvestigationOut)
async def create_investigation(
    claim: str = Form(...),
    image: Optional[UploadFile] = File(None),
    sample_image_name: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    source_url: Optional[str] = Form(None),
    mode: Optional[str] = Form("deep"),
    db: Session = Depends(get_db)
):
    """
    Executes the Complete Multi-Stage Investigation Pipeline:
    Stage A: Image Inspection, EXIF, GPS & Scene Forensics
    Stage B: Generate Location & Landmark Hypotheses
    Stage C: Retrieve Reference Evidence (Local Corpus + Live Knowledge Adapter)
    Stage D & E: Candidate Verification, Decoupled Epistemic Synthesis & Audit Trace
    """
    if not claim or len(claim.strip()) < 3:
        raise HTTPException(status_code=400, detail="Claim text must be at least 3 characters.")
    if len(claim) > 1000:
        raise HTTPException(status_code=400, detail="Claim text exceeds maximum length of 1000 characters.")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    sample_dir = Path(settings.SAMPLE_DIR)
    if not sample_dir.exists():
        sample_dir = settings.BASE_DIR / "data" / "samples"

    saved_filename = ""
    target_path = None

    if image and image.filename:
        ext = Path(image.filename).suffix.lower()
        if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format: {ext}. Allowed: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
            )
        
        file_uuid = generate_uuid()
        saved_filename = f"{file_uuid}{ext}"
        target_path = upload_dir / saved_filename
        
        contents = await image.read()
        if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Image file size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )
        
        with open(target_path, "wb") as f:
            f.write(contents)
    elif sample_image_name:
        clean_name = Path(sample_image_name).name
        src_sample = sample_dir / clean_name
        if not src_sample.exists():
            src_sample = settings.BASE_DIR / "data" / "samples" / clean_name
        if not src_sample.exists():
            raise HTTPException(status_code=404, detail="Selected sample image not found.")
        
        file_uuid = generate_uuid()
        ext = src_sample.suffix
        saved_filename = f"{file_uuid}{ext}"
        target_path = upload_dir / saved_filename
        shutil.copyfile(src_sample, target_path)
    else:
        raise HTTPException(status_code=400, detail="Either an image upload or a sample image must be provided.")

    # Calculate SHA-256 hash of file
    hasher = hashlib.sha256()
    with open(target_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    image_hash = hasher.hexdigest()

    # STAGE A: Image Inspection, EXIF, GPS & Scene Clues
    metadata = extract_image_metadata(str(target_path))
    scene_clues = analyze_scene_clues(str(target_path), exif_data=metadata.get("exif_data"), user_claim=claim)

    # STAGE C: Deconstruct Claim & Visual Consistency Analysis
    claim_breakdown_data = analyze_claim(claim, user_location=location, user_date=date)
    visual_consistency = compare_claim_with_visuals(claim_breakdown_data, scene_clues)
    claim_breakdown_data["visual_consistency"] = visual_consistency

    # STAGE B: Generate Location & Landmark Hypotheses
    candidate_hypotheses = generate_location_hypotheses(
        claim_components=claim_breakdown_data,
        scene_clues=scene_clues,
        gps_data=metadata.get("gps_data")
    )

    # STAGE D: Multi-Strategy Evidence Retrieval
    retrieved_evidence, visual_match, search_trace = retrieve_evidence(
        claim_components=claim_breakdown_data,
        image_phash=metadata.get("perceptual_hash", ""),
        scene_clues=scene_clues,
        candidate_hypotheses=candidate_hypotheses,
        investigation_mode=mode
    )

    # Inject visual analysis and dynamic questions into trace
    search_trace["ai_image_description"] = scene_clues.get("image_description", "")
    search_trace["vision_model_used"] = scene_clues.get("vision_model_used", "")
    search_trace["verification_questions"] = claim_breakdown_data.get("verification_questions", [])
    search_trace["visual_consistency"] = visual_consistency
    search_trace["is_ambiguous"] = claim_breakdown_data.get("is_ambiguous", False)
    search_trace["ambiguity_note"] = claim_breakdown_data.get("ambiguity_note")

    # STAGE E & F: Candidate Verification & Epistemic Synthesis
    synthesis = verify_claim_against_evidence(
        claim_breakdown=claim_breakdown_data,
        evidence_items=retrieved_evidence,
        visual_match=visual_match,
        authenticity_signals=metadata.get("authenticity_signals"),
        scene_clues=scene_clues,
        candidate_hypotheses=candidate_hypotheses,
        search_trace=search_trace
    )

    # Persist Complete Dossier
    investigation_id = generate_uuid()
    investigation = Investigation(
        id=investigation_id,
        original_claim=claim.strip(),
        normalized_claim=claim_breakdown_data.get("core_assertion"),
        image_path=str(target_path),
        image_filename=saved_filename,
        image_hash=image_hash,
        mode=mode,
        
        # 8 Decoupled Pillars
        verdict_category=synthesis["verdict_category"],
        verdict_headline=synthesis["verdict_headline"],
        summary=synthesis["summary"],
        confidence_level=synthesis["confidence_level"],
        confidence_explanation=synthesis["confidence_explanation"],
        
        claimed_location=synthesis["claimed_location"],
        best_supported_location=synthesis["best_supported_location"],
        location_verification_status=synthesis["location_verification_status"],
        candidate_locations=synthesis["candidate_locations"],

        image_authenticity_status=synthesis["image_authenticity_status"],
        event_date_verification_status=synthesis["event_date_verification_status"],
        
        reasons_for_verdict=synthesis["reasons_for_verdict"],
        unverified_details=synthesis["unverified_details"],
        next_verification_steps=synthesis["next_verification_steps"],
        fact_claim_matrix=synthesis.get("fact_claim_matrix", []),
        investigation_trace=synthesis["investigation_trace"],
        
        location_asserted=location,
        date_asserted=date,
        source_url_asserted=source_url,
        completed_at=datetime.now(timezone.utc)
    )
    db.add(investigation)
    db.flush()

    # Image Analysis Record
    analysis_record = ImageAnalysisResult(
        id=generate_uuid(),
        investigation_id=investigation.id,
        file_type=metadata.get("file_type", "UNKNOWN"),
        file_size_bytes=metadata.get("file_size_bytes", 0),
        dimensions=metadata.get("dimensions", "0x0"),
        color_mode=metadata.get("color_mode", "RGB"),
        exif_data=metadata.get("exif_data", {}),
        gps_data=metadata.get("gps_data", {}),
        perceptual_hash=metadata.get("perceptual_hash"),
        color_histogram_summary=metadata.get("color_histogram_summary"),
        scene_clues=scene_clues,
        authenticity_signals=metadata.get("authenticity_signals", {}),
        limitations=metadata.get("limitations")
    )
    db.add(analysis_record)

    # Claim Breakdown Record
    claim_record = ClaimBreakdown(
        id=generate_uuid(),
        investigation_id=investigation.id,
        event=claim_breakdown_data.get("event"),
        location=claim_breakdown_data.get("location"),
        time_reference=claim_breakdown_data.get("time_reference"),
        core_assertion=claim_breakdown_data.get("core_assertion", ""),
        extracted_entities=claim_breakdown_data.get("extracted_entities", [])
    )
    db.add(claim_record)

    # Evidence Items Records
    for item in retrieved_evidence:
        ev_record = EvidenceItem(
            id=generate_uuid(),
            investigation_id=investigation.id,
            source_title=item.get("source_title", "Untitled Source"),
            source_url=item.get("source_url", ""),
            publisher=item.get("publisher", "Independent Record"),
            publication_date=item.get("publication_date"),
            relationship_to_claim=item.get("relationship_to_claim", "neutral"),
            retrieval_score=item.get("retrieval_score", 0.0),
            reliability_score=item.get("reliability_score", 0.0),
            passage=item.get("passage", ""),
            retrieval_method=item.get("retrieval_method", "semantic_text"),
            indicators=item.get("indicators", {}),
            thumbnail_url=item.get("thumbnail_url")
        )
        db.add(ev_record)

    db.commit()
    db.refresh(investigation)

    return format_investigation_response(investigation)

@router.get("/investigations", response_model=List[InvestigationSummaryOut])
def list_investigations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lists saved investigations with optional filtering and search."""
    query = db.query(Investigation)
    if status:
        query = query.filter(Investigation.verdict_category.ilike(f"%{status}%"))
    if search:
        query = query.filter(Investigation.original_claim.ilike(f"%{search}%"))

    investigations = query.order_by(Investigation.created_at.desc()).offset(skip).limit(limit).all()
    results = []
    for inv in investigations:
        results.append(InvestigationSummaryOut(
            id=inv.id,
            original_claim=inv.original_claim,
            image_url=f"/uploads/{inv.image_filename}",
            verdict_category=inv.verdict_category or "INSUFFICIENT EVIDENCE",
            verdict_headline=inv.verdict_headline,
            best_supported_location=inv.best_supported_location or "Unverified / Unknown",
            confidence_level=inv.confidence_level or "insufficient",
            created_at=inv.created_at,
            evidence_count=len(inv.evidence_items)
        ))
    return results

@router.get("/investigations/{investigation_id}", response_model=InvestigationOut)
def get_investigation(investigation_id: str, db: Session = Depends(get_db)):
    """Retrieves full investigation dossier by ID."""
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation record not found.")
    return format_investigation_response(inv)

@router.delete("/investigations/{investigation_id}")
def delete_investigation(investigation_id: str, db: Session = Depends(get_db)):
    """Deletes an investigation record and its uploaded image file."""
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation record not found.")
    
    try:
        p = Path(inv.image_path)
        if p.exists() and "uploads" in str(p):
            p.unlink()
    except Exception:
        pass

    db.delete(inv)
    db.commit()
    return {"status": "deleted", "id": investigation_id}

@router.delete("/investigations")
def clear_all_investigations(confirm: bool = Query(False), db: Session = Depends(get_db)):
    """Clears all investigation records."""
    if not confirm:
        raise HTTPException(status_code=400, detail="Confirmation required to clear history (confirm=true).")
    
    db.query(EvidenceItem).delete()
    db.query(ImageAnalysisResult).delete()
    db.query(ClaimBreakdown).delete()
    db.query(Investigation).delete()
    db.commit()
    return {"status": "all_records_cleared"}

@router.post("/investigations/{investigation_id}/reanalyze", response_model=InvestigationOut)
def reanalyze_investigation(
    investigation_id: str,
    mode: str = Query("research"),
    db: Session = Depends(get_db)
):
    """Re-analyzes an existing investigation with a different mode (e.g. Research Mode)."""
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found.")

    claim_breakdown_data = analyze_claim(inv.original_claim, user_location=inv.location_asserted, user_date=inv.date_asserted)
    metadata = extract_image_metadata(inv.image_path)
    scene_clues = analyze_scene_clues(inv.image_path, exif_data=metadata.get("exif_data"), user_claim=inv.original_claim)
    visual_consistency = compare_claim_with_visuals(claim_breakdown_data, scene_clues)
    claim_breakdown_data["visual_consistency"] = visual_consistency

    candidate_hypotheses = generate_location_hypotheses(
        claim_components=claim_breakdown_data,
        scene_clues=scene_clues,
        gps_data=metadata.get("gps_data")
    )

    retrieved_evidence, visual_match, search_trace = retrieve_evidence(
        claim_components=claim_breakdown_data,
        image_phash=metadata.get("perceptual_hash", ""),
        scene_clues=scene_clues,
        candidate_hypotheses=candidate_hypotheses,
        investigation_mode=mode
    )

    search_trace["ai_image_description"] = scene_clues.get("image_description", "")
    search_trace["vision_model_used"] = scene_clues.get("vision_model_used", "")
    search_trace["verification_questions"] = claim_breakdown_data.get("verification_questions", [])
    search_trace["visual_consistency"] = visual_consistency
    search_trace["is_ambiguous"] = claim_breakdown_data.get("is_ambiguous", False)
    search_trace["ambiguity_note"] = claim_breakdown_data.get("ambiguity_note")

    synthesis = verify_claim_against_evidence(
        claim_breakdown=claim_breakdown_data,
        evidence_items=retrieved_evidence,
        visual_match=visual_match,
        authenticity_signals=metadata.get("authenticity_signals"),
        scene_clues=scene_clues,
        candidate_hypotheses=candidate_hypotheses,
        search_trace=search_trace
    )

    inv.mode = mode
    inv.verdict_category = synthesis["verdict_category"]
    inv.verdict_headline = synthesis["verdict_headline"]
    inv.summary = synthesis["summary"]
    inv.confidence_level = synthesis["confidence_level"]
    inv.confidence_explanation = synthesis["confidence_explanation"]
    inv.claimed_location = synthesis["claimed_location"]
    inv.best_supported_location = synthesis["best_supported_location"]
    inv.location_verification_status = synthesis["location_verification_status"]
    inv.candidate_locations = synthesis["candidate_locations"]
    inv.image_authenticity_status = synthesis["image_authenticity_status"]
    inv.event_date_verification_status = synthesis["event_date_verification_status"]
    inv.reasons_for_verdict = synthesis["reasons_for_verdict"]
    inv.unverified_details = synthesis["unverified_details"]
    inv.next_verification_steps = synthesis["next_verification_steps"]
    inv.fact_claim_matrix = synthesis.get("fact_claim_matrix", [])
    inv.investigation_trace = synthesis["investigation_trace"]
    inv.completed_at = datetime.now(timezone.utc)

    # Update associated analysis records if present
    if inv.image_analysis:
        inv.image_analysis.scene_clues = scene_clues
    if inv.claim_breakdown:
        inv.claim_breakdown.core_assertion = claim_breakdown_data.get("core_assertion", "")
        inv.claim_breakdown.extracted_entities = claim_breakdown_data.get("extracted_entities", [])

    # Replace evidence items
    db.query(EvidenceItem).filter(EvidenceItem.investigation_id == inv.id).delete()
    for item in retrieved_evidence:
        db.add(EvidenceItem(
            id=generate_uuid(),
            investigation_id=inv.id,
            source_title=item.get("source_title", "Untitled Source"),
            source_url=item.get("source_url", ""),
            publisher=item.get("publisher", "Independent Record"),
            publication_date=item.get("publication_date"),
            relationship_to_claim=item.get("relationship_to_claim", "neutral"),
            retrieval_score=item.get("retrieval_score", 0.0),
            reliability_score=item.get("reliability_score", 0.0),
            passage=item.get("passage", ""),
            retrieval_method=item.get("retrieval_method", "semantic_text"),
            indicators=item.get("indicators", {}),
            thumbnail_url=item.get("thumbnail_url")
        ))
    db.commit()
    db.refresh(inv)
    return format_investigation_response(inv)

@router.get("/investigations/{investigation_id}/export/pdf")
def export_investigation_pdf(investigation_id: str, db: Session = Depends(get_db)):
    """Exports dossier as an editorial PDF document."""
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation record not found.")

    formatted = format_investigation_response(inv).model_dump()
    pdf_bytes = generate_pdf_report(formatted)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=truthlens_dossier_{investigation_id[:8]}.pdf"}
    )

@router.get("/investigations/{investigation_id}/export/json")
def export_investigation_json(investigation_id: str, db: Session = Depends(get_db)):
    """Exports dossier as structured JSON for academic exchange."""
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation record not found.")
    return format_investigation_response(inv)

@router.get("/investigations/{investigation_id}/export/sanitized-image")
def export_sanitized_image(investigation_id: str, db: Session = Depends(get_db)):
    """Returns a privacy-sanitized copy of the image with all EXIF and GPS tags removed."""
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation record not found.")

    clean_dir = Path(settings.UPLOAD_DIR) / "sanitized"
    clean_dir.mkdir(parents=True, exist_ok=True)
    clean_path = clean_dir / f"clean_{inv.image_filename}"
    
    strip_image_metadata(inv.image_path, str(clean_path))
    
    with open(clean_path, "rb") as f:
        clean_bytes = f.read()

    return Response(
        content=clean_bytes,
        media_type="image/jpeg",
        headers={"Content-Disposition": f"attachment; filename=sanitized_{inv.image_filename}"}
    )

@router.post("/assistant/query", response_model=AssistantQueryResponse)
def ask_assistant(req: AssistantQueryRequest, db: Session = Depends(get_db)):
    """Evidence-grounded assistant answering questions about the investigation dossier."""
    inv = db.query(Investigation).filter(Investigation.id == req.investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation record not found.")

    evidence_dicts = [
        {
            "publisher": e.publisher,
            "source_title": e.source_title,
            "source_url": e.source_url,
            "relationship_to_claim": e.relationship_to_claim,
            "passage": e.passage,
            "retrieval_score": e.retrieval_score
        }
        for e in inv.evidence_items
    ]

    res = answer_research_question(
        question=req.question,
        investigation_summary=inv.summary or "",
        assessment_status=inv.verdict_category or "INSUFFICIENT EVIDENCE",
        claim_assertion=inv.normalized_claim or inv.original_claim,
        evidence_items=evidence_dicts
    )

    return AssistantQueryResponse(**res)

@router.get("/research-lab")
def get_research_lab_info():
    """Returns PCA embedding projections, model cards, and benchmark metrics."""
    return get_research_lab_data()

def format_investigation_response(inv: Investigation) -> InvestigationOut:
    """Helper to convert ORM model into Pydantic schema with web URLs."""
    evidence_outs = [
        {
            "id": e.id,
            "source_title": e.source_title,
            "source_url": e.source_url,
            "publisher": e.publisher,
            "publication_date": e.publication_date,
            "relationship_to_claim": e.relationship_to_claim,
            "retrieval_score": e.retrieval_score,
            "reliability_score": e.reliability_score,
            "passage": e.passage,
            "retrieval_method": e.retrieval_method,
            "indicators": e.indicators or {},
            "thumbnail_url": e.thumbnail_url
        }
        for e in inv.evidence_items
    ]

    analysis_out = None
    if inv.image_analysis:
        analysis_out = {
            "file_type": inv.image_analysis.file_type,
            "file_size_bytes": inv.image_analysis.file_size_bytes,
            "dimensions": inv.image_analysis.dimensions,
            "color_mode": inv.image_analysis.color_mode,
            "exif_data": inv.image_analysis.exif_data or {},
            "gps_data": inv.image_analysis.gps_data or {},
            "perceptual_hash": inv.image_analysis.perceptual_hash,
            "color_histogram_summary": inv.image_analysis.color_histogram_summary,
            "scene_clues": inv.image_analysis.scene_clues or {},
            "authenticity_signals": inv.image_analysis.authenticity_signals or {},
            "limitations": inv.image_analysis.limitations
        }

    claim_bd_out = None
    if inv.claim_breakdown:
        claim_bd_out = {
            "event": inv.claim_breakdown.event,
            "location": inv.claim_breakdown.location,
            "time_reference": inv.claim_breakdown.time_reference,
            "core_assertion": inv.claim_breakdown.core_assertion,
            "extracted_entities": inv.claim_breakdown.extracted_entities or []
        }

    return InvestigationOut(
        id=inv.id,
        original_claim=inv.original_claim,
        normalized_claim=inv.normalized_claim,
        image_url=f"/uploads/{inv.image_filename}",
        image_filename=inv.image_filename,
        image_hash=inv.image_hash,
        mode=inv.mode,
        
        # 8 Decoupled Pillars
        verdict_category=inv.verdict_category or "INSUFFICIENT EVIDENCE",
        verdict_headline=inv.verdict_headline,
        summary=inv.summary,
        confidence_level=inv.confidence_level or "insufficient",
        confidence_explanation=inv.confidence_explanation,
        
        claimed_location=inv.claimed_location,
        best_supported_location=inv.best_supported_location or "Unverified / Unknown",
        location_verification_status=inv.location_verification_status or "UNVERIFIED_INSUFFICIENT_EVIDENCE",
        candidate_locations=inv.candidate_locations or [],
        
        image_authenticity_status=inv.image_authenticity_status or "UNVERIFIED",
        event_date_verification_status=inv.event_date_verification_status or "UNVERIFIED",
        
        reasons_for_verdict=inv.reasons_for_verdict or [],
        unverified_details=inv.unverified_details or [],
        next_verification_steps=inv.next_verification_steps or [],
        fact_claim_matrix=inv.fact_claim_matrix or [],
        
        investigation_trace=inv.investigation_trace or {},

        location_asserted=inv.location_asserted,
        date_asserted=inv.date_asserted,
        source_url_asserted=inv.source_url_asserted,
        created_at=inv.created_at,
        completed_at=inv.completed_at,
        evidence_items=evidence_outs,
        image_analysis=analysis_out,
        claim_breakdown=claim_bd_out
    )
