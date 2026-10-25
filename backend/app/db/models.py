import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    original_claim = Column(Text, nullable=False)
    normalized_claim = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=False)
    image_filename = Column(String(255), nullable=False)
    image_hash = Column(String(64), nullable=False, index=True)
    mode = Column(String(32), default="deep")  # quick, deep, research
    
    # 8 Decoupled Analysis Pillars & Verdict
    verdict_category = Column(String(64), default="INSUFFICIENT EVIDENCE")
    verdict_headline = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    confidence_level = Column(String(64), default="insufficient")
    confidence_explanation = Column(Text, nullable=True)
    
    # Location & Landmark Decoupling
    claimed_location = Column(String(128), nullable=True)
    best_supported_location = Column(String(128), default="Unverified / Unknown")
    location_verification_status = Column(String(64), default="UNVERIFIED_INSUFFICIENT_EVIDENCE")
    candidate_locations = Column(JSON, default=list)

    # Authenticity & Epistemic Decoupling
    image_authenticity_status = Column(String(64), default="UNVERIFIED")
    event_date_verification_status = Column(String(64), default="UNVERIFIED")
    
    # Granular Reasons & Actionable Steps
    reasons_for_verdict = Column(JSON, default=list)
    unverified_details = Column(JSON, default=list)
    next_verification_steps = Column(JSON, default=list)
    fact_claim_matrix = Column(JSON, default=list)
    
    # Auditable Investigation Trace
    investigation_trace = Column(JSON, default=dict)
    
    # User optional context
    location_asserted = Column(String(128), nullable=True)
    date_asserted = Column(String(64), nullable=True)
    source_url_asserted = Column(String(512), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    evidence_items = relationship("EvidenceItem", back_populates="investigation", cascade="all, delete-orphan")
    image_analysis = relationship("ImageAnalysisResult", back_populates="investigation", uselist=False, cascade="all, delete-orphan")
    claim_breakdown = relationship("ClaimBreakdown", back_populates="investigation", uselist=False, cascade="all, delete-orphan")

class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    source_title = Column(String(255), nullable=False)
    source_url = Column(String(1024), nullable=False)
    publisher = Column(String(128), nullable=False)
    publication_date = Column(String(64), nullable=True)
    relationship_to_claim = Column(String(32), default="neutral")  # supports, contradicts, neutral, context
    retrieval_score = Column(Float, default=0.0)
    reliability_score = Column(Float, default=0.0)
    passage = Column(Text, nullable=False)
    retrieval_method = Column(String(64), default="semantic_text")
    indicators = Column(JSON, default=dict)
    thumbnail_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="evidence_items")

class ImageAnalysisResult(Base):
    __tablename__ = "image_analysis_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, unique=True)
    file_type = Column(String(16), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    dimensions = Column(String(32), nullable=False)
    color_mode = Column(String(16), nullable=False)
    exif_data = Column(JSON, default=dict)
    gps_data = Column(JSON, default=dict)
    perceptual_hash = Column(String(64), nullable=True)
    color_histogram_summary = Column(Text, nullable=True)
    scene_clues = Column(JSON, default=dict)
    authenticity_signals = Column(JSON, default=dict)
    limitations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="image_analysis")

class ClaimBreakdown(Base):
    __tablename__ = "claim_breakdowns"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, unique=True)
    event = Column(String(128), nullable=True)
    location = Column(String(128), nullable=True)
    time_reference = Column(String(64), nullable=True)
    core_assertion = Column(Text, nullable=False)
    extracted_entities = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="claim_breakdown")

class ReferenceImage(Base):
    __tablename__ = "reference_images"

    id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    image_path = Column(String(255), nullable=False)
    provenance = Column(Text, nullable=False)
    source_url = Column(String(1024), nullable=False)
    known_date = Column(String(64), nullable=True)
    location = Column(String(128), nullable=True)
    category = Column(String(64), nullable=False)
    perceptual_hash = Column(String(64), nullable=True)
    license = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
