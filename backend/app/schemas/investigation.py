from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class InvestigationCreateForm(BaseModel):
    claim: str = Field(..., min_length=3, max_length=1000)
    location: Optional[str] = Field(None, max_length=128)
    date: Optional[str] = Field(None, max_length=64)
    source_url: Optional[str] = Field(None, max_length=512)
    mode: Optional[str] = Field("deep", description="quick, deep, or research")

class EvidenceItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_title: str
    source_url: str
    publisher: str
    publication_date: Optional[str] = None
    relationship_to_claim: str
    retrieval_score: float
    reliability_score: float
    passage: str
    retrieval_method: str
    indicators: Dict[str, Any] = {}
    thumbnail_url: Optional[str] = None

class ImageAnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    file_type: str
    file_size_bytes: int
    dimensions: str
    color_mode: str
    exif_data: Dict[str, Any] = {}
    gps_data: Dict[str, Any] = {}
    perceptual_hash: Optional[str] = None
    color_histogram_summary: Optional[str] = None
    scene_clues: Dict[str, Any] = {}
    authenticity_signals: Dict[str, Any] = {}
    limitations: Optional[str] = None

class ClaimBreakdownOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event: Optional[str] = None
    location: Optional[str] = None
    time_reference: Optional[str] = None
    core_assertion: str
    extracted_entities: List[str] = []

class InvestigationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_claim: str
    normalized_claim: Optional[str] = None
    image_url: str
    image_filename: str
    image_hash: str
    mode: str
    
    # 8 Decoupled Analysis Pillars & Verdict
    verdict_category: str
    verdict_headline: Optional[str] = None
    summary: Optional[str] = None
    confidence_level: str
    confidence_explanation: Optional[str] = None
    
    claimed_location: Optional[str] = None
    best_supported_location: str
    location_verification_status: str
    candidate_locations: List[Dict[str, Any]] = []

    image_authenticity_status: str
    event_date_verification_status: str
    
    reasons_for_verdict: List[str] = []
    unverified_details: List[str] = []
    next_verification_steps: List[str] = []
    fact_claim_matrix: List[Dict[str, Any]] = []
    
    investigation_trace: Dict[str, Any] = {}

    location_asserted: Optional[str] = None
    date_asserted: Optional[str] = None
    source_url_asserted: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    evidence_items: List[EvidenceItemOut] = []
    image_analysis: Optional[ImageAnalysisOut] = None
    claim_breakdown: Optional[ClaimBreakdownOut] = None

class InvestigationSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_claim: str
    image_url: str
    verdict_category: str
    verdict_headline: Optional[str] = None
    best_supported_location: str
    confidence_level: str
    created_at: datetime
    evidence_count: int

class AssistantQueryRequest(BaseModel):
    investigation_id: str
    question: str = Field(..., min_length=2, max_length=500)

class AssistantQueryResponse(BaseModel):
    question: str
    answer: str
    grounded_in_sources: List[str]
    missing_information: Optional[str] = None
    limitations: str

class CapabilitiesOut(BaseModel):
    visual_similarity: bool
    exif_inspection: bool
    scene_forensics: bool
    landmark_hypothesizer: bool
    claim_decomposition: bool
    evidence_retrieval_local: bool
    evidence_retrieval_web: bool
    external_llm: bool
    pdf_export: bool
    active_models: Dict[str, str]
    disclaimer: str
