export type AssessmentStatus = 'supported' | 'contradicted' | 'insufficient_evidence' | 'conflicting';

export type ConfidenceLevel = 'strong_evidence' | 'moderate_evidence' | 'inconclusive' | 'insufficient';

export type InvestigationMode = 'quick' | 'deep' | 'research';

export interface DetectionResult {
  success: boolean;
  prediction: 'likely_ai_generated' | 'likely_real_photograph' | 'uncertain';
  display_label: string;
  confidence: number;
  explanation: string;
  model_name: string;
  probabilities?: {
    ai_generated: number;
    real_photograph: number;
  };
  limitations: string[];
  image_metadata?: {
    format: string;
    width: number;
    height: number;
    file_size_bytes: number;
    filename: string;
  };
}

export interface ModelInfo {
  model_name: string;
  is_available: boolean;
  load_error: string | null;
  device: string;
  labels: Record<string, string>;
  supported_formats: string[];
  max_upload_size_mb: number;
}

export interface CandidateLocation {
  id?: string;
  candidate_name: string;
  candidate_city: string;
  candidate_state: string;
  supporting_clues: string[];
  source_type: string;
  is_verified: boolean;
  match_confidence: string;
}

export interface FactClaimItem {
  fact_name: string;
  asserted_value: string;
  verification_status: 'VERIFIED_BY_EVIDENCE' | 'SUPPORTED_NOT_VERIFIED' | 'CONTRADICTED_BY_EVIDENCE' | 'PREDICTED_BY_AI_ONLY' | 'UNKNOWN_UNAVAILABLE';
  supported_value: string;
  explanation: string;
  source_urls: string[];
}

export interface InvestigationTrace {
  original_claim: string;
  extracted_entities: string[];
  claimed_location: string;
  visual_clues_detected: string[];
  search_queries_executed: string[];
  search_providers_used: string[];
  provider_status?: Record<string, string>;
  candidate_locations_evaluated: string[];
  best_supported_location: string;
  location_verification_status?: string;
  retrieved_evidence_count: number;
  source_urls: string[];
  rejected_candidates: Array<{ candidate: string; reason: string }>;
  final_verdict: string;
  zero_evidence_reason?: string | null;
  unresolved_questions: string[];
  verification_questions?: string[];
  visual_consistency?: {
    consistent_parts?: string[];
    requires_external_verification?: string[];
    inconsistent_parts?: string[];
    indeterminable_visually?: string[];
  };
  ai_image_description?: string;
  vision_model_used?: string;
}

export interface EvidenceItem {
  id: string;
  source_title: string;
  source_url: string;
  publisher: string;
  publication_date?: string | null;
  relationship_to_claim: 'supports' | 'contradicts' | 'neutral' | 'context';
  retrieval_score: number;
  reliability_score: number;
  passage: string;
  retrieval_method: string;
  indicators: {
    publisher_identifiable?: boolean;
    is_established_outlet?: boolean;
    date_present?: boolean;
    primary_source_linked?: boolean;
    direct_claim_relevance?: boolean;
    transparency_level?: string;
  };
  thumbnail_url?: string | null;
}

export interface ImageAnalysis {
  file_type: string;
  file_size_bytes: number;
  dimensions: string;
  color_mode: string;
  exif_data: Record<string, string>;
  gps_data: {
    has_gps?: boolean;
    latitude?: number;
    longitude?: number;
    redacted_display?: string;
    note?: string;
  };
  perceptual_hash?: string;
  color_histogram_summary?: string;
  scene_clues?: {
    image_description?: string;
    scene_category?: string;
    visible_objects?: string[];
    visible_activities?: string[];
    text_and_signboards?: string[];
    distinctive_features?: string[];
    possible_landmark_clues?: string[];
    visual_uncertainties?: string[];
    vision_model_used?: string;
    confidence_in_clues?: string;
    architectural_style?: string;
    primary_materials?: string[];
    surroundings_and_terrain?: string[];
    text_and_signboard_clues?: string[];
    detected_features?: string[];
  };
  authenticity_signals: {
    synthetic_indicator?: string;
    has_editing_signatures?: boolean;
    editing_software_detected?: string | null;
    metadata_integrity?: string;
    ela_score?: number;
    limitations_notice?: string;
    notes?: string[];
  };
  limitations?: string;
}

export interface ClaimBreakdown {
  event?: string | null;
  location?: string | null;
  time_reference?: string | null;
  core_assertion: string;
  extracted_entities: string[];
  historical_context?: string | null;
  is_authenticity_claim?: boolean;
  authenticity_assertion?: string | null;
  verification_questions?: string[];
  is_ambiguous?: boolean;
  ambiguity_note?: string | null;
}

export interface Investigation {
  id: string;
  original_claim: string;
  normalized_claim?: string | null;
  image_url: string;
  image_filename: string;
  image_hash: string;
  mode: InvestigationMode;
  
  // 8 Decoupled Pillars & Verdict
  verdict_category: string;
  verdict_headline?: string | null;
  summary?: string | null;
  confidence_level: ConfidenceLevel;
  confidence_explanation?: string | null;
  
  claimed_location?: string | null;
  best_supported_location: string;
  location_verification_status: string;
  candidate_locations: CandidateLocation[];

  image_authenticity_status: string;
  event_date_verification_status: string;
  
  reasons_for_verdict: string[];
  unverified_details: string[];
  next_verification_steps: string[];
  fact_claim_matrix?: FactClaimItem[];
  
  investigation_trace: InvestigationTrace;

  location_asserted?: string | null;
  date_asserted?: string | null;
  source_url_asserted?: string | null;
  created_at: string;
  completed_at?: string | null;
  evidence_items: EvidenceItem[];
  image_analysis?: ImageAnalysis | null;
  claim_breakdown?: ClaimBreakdown | null;
}

export interface InvestigationSummary {
  id: string;
  original_claim: string;
  image_url: string;
  assessment_status?: AssessmentStatus;
  verdict_category: string;
  verdict_headline?: string | null;
  best_supported_location: string;
  confidence_level: ConfidenceLevel;
  created_at: string;
  evidence_count: number;
}

export interface DemoCase {
  id: string;
  title: string;
  claim: string;
  image_url: string;
  location: string;
  date: string;
  source_type: string;
  case_type: string;
  description: string;
}

export interface Capabilities {
  visual_similarity: boolean;
  exif_inspection: boolean;
  scene_forensics: boolean;
  landmark_hypothesizer: boolean;
  claim_decomposition: boolean;
  evidence_retrieval_local: boolean;
  evidence_retrieval_web: boolean;
  external_llm: boolean;
  pdf_export: boolean;
  active_models: Record<string, string>;
  disclaimer: string;
}

export interface AssistantResponse {
  question: string;
  answer: string;
  grounded_in_sources: string[];
  missing_information?: string | null;
  limitations: string;
}

export interface ResearchLabData {
  projection_points: Array<{
    id: string;
    title: string;
    category: string;
    x: number;
    y: number;
    publisher: string;
  }>;
  pca_variance_ratio: number[];
  evaluation_metrics: {
    benchmark_dataset: string;
    sample_size: number;
    metrics: Record<string, number>;
    confusion_matrix: {
      labels: string[];
      matrix: number[][];
    };
    explanation: string;
  };
  model_cards: Array<{
    name: string;
    purpose: string;
    latency_ms: string;
    hardware: string;
    strengths: string;
    limitations: string;
  }>;
}
