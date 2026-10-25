import React, { useState } from 'react';
import {
  FileText,
  Download,
  Printer,
  CheckCircle2,
  XCircle,
  HelpCircle,
  AlertTriangle,
  Scale,
  Camera,
  Calendar,
  MessageSquare,
  Columns,
  Share2,
  ChevronLeft,
  Terminal,
  MapPin,
  ShieldCheck,
  Cpu,
  ArrowRight,
  ExternalLink,
  Layers,
  Info,
  Eye,
  Sparkles,
  Filter,
  Check,
  ListChecks
} from 'lucide-react';
import { Investigation, InvestigationMode, FactClaimItem } from '../types';
import { EvidenceCard } from '../components/EvidenceCard';
import { ExifInspector } from '../components/ExifInspector';
import { EvidenceTimeline } from '../components/EvidenceTimeline';
import { ImageComparisonSlider } from '../components/ImageComparisonSlider';
import { ResearchAssistantDrawer } from '../components/ResearchAssistantDrawer';
import { UncertaintyPanel } from '../components/UncertaintyPanel';
import { InvestigationTracePanel } from '../components/InvestigationTracePanel';
import { getExportPdfUrl, getExportJsonUrl, reanalyzeInvestigation } from '../services/api';

interface ReportPageProps {
  investigation: Investigation;
  onBackToWorkspace: () => void;
  onUpdateInvestigation: (updated: Investigation) => void;
}

export const ReportPage: React.FC<ReportPageProps> = ({
  investigation,
  onBackToWorkspace,
  onUpdateInvestigation
}) => {
  const [activeTab, setActiveTab] = useState<'evidence' | 'trace' | 'comparison' | 'forensics' | 'timeline' | 'assistant' | 'uncertainty'>('evidence');
  const [evidenceFilter, setEvidenceFilter] = useState<'all' | 'supports' | 'contradicts' | 'neutral'>('all');
  const [isReanalyzing, setIsReanalyzing] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);

  const sceneClues = investigation.image_analysis?.scene_clues || {};
  const claimBreakdown = (investigation.claim_breakdown || {}) as any;
  const trace = investigation.investigation_trace || {};
  const aiDescription = sceneClues.image_description || (trace as any).ai_image_description || "Visual forensic description unavailable.";
  const visionModelUsed = sceneClues.vision_model_used || (trace as any).vision_model_used || "TruthLens Local Forensic Vision Pipeline";
  const verificationQuestions = (trace as any).verification_questions || claimBreakdown.verification_questions || [];
  const visualConsistency = (trace as any).visual_consistency || {};
  const visibleObjects = sceneClues.visible_objects || [];
  const visibleActivities = sceneClues.visible_activities || [];
  const textAndSigns = sceneClues.text_and_signboards || [];
  const visualUncertainties = sceneClues.visual_uncertainties || [];

  const supportsCount = investigation.evidence_items.filter((e) => e.relationship_to_claim === 'supports').length;
  const contradictsCount = investigation.evidence_items.filter((e) => e.relationship_to_claim === 'contradicts').length;
  const neutralCount = investigation.evidence_items.filter((e) => e.relationship_to_claim !== 'supports' && e.relationship_to_claim !== 'contradicts').length;

  const filteredEvidence = investigation.evidence_items.filter((e) => {
    if (evidenceFilter === 'supports') return e.relationship_to_claim === 'supports';
    if (evidenceFilter === 'contradicts') return e.relationship_to_claim === 'contradicts';
    if (evidenceFilter === 'neutral') return e.relationship_to_claim !== 'supports' && e.relationship_to_claim !== 'contradicts';
    return true;
  });

  const handleReanalyze = async (newMode: InvestigationMode) => {
    setIsReanalyzing(true);
    try {
      const updated = await reanalyzeInvestigation(investigation.id, newMode);
      onUpdateInvestigation(updated);
    } catch (err) {
      alert('Failed to re-analyze investigation.');
    } finally {
      setIsReanalyzing(false);
    }
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  const getVerdictBadge = () => {
    const v = investigation.verdict_category.toUpperCase();
    if (v.includes('SUPPORTED') && !v.includes('CONTRADICTED')) {
      return (
        <div className="editorial-badge status-supported flex items-center gap-1.5 text-xs py-1 px-3">
          <CheckCircle2 className="w-4 h-4 text-[#166534]" />
          <span className="font-bold">{investigation.verdict_category}</span>
        </div>
      );
    } else if (v.includes('CONTRADICTED')) {
      return (
        <div className="editorial-badge status-contradicted flex items-center gap-1.5 text-xs py-1 px-3">
          <XCircle className="w-4 h-4 text-[#991B1B]" />
          <span className="font-bold">{investigation.verdict_category}</span>
        </div>
      );
    } else if (v.includes('MANIPULATION') || v.includes('AI-GENERATED')) {
      return (
        <div className="editorial-badge status-contradicted flex items-center gap-1.5 text-xs py-1 px-3">
          <AlertTriangle className="w-4 h-4 text-[#991B1B]" />
          <span className="font-bold">{investigation.verdict_category}</span>
        </div>
      );
    } else {
      return (
        <div className="editorial-badge status-insufficient flex items-center gap-1.5 text-xs py-1 px-3">
          <HelpCircle className="w-4 h-4 text-[#92400E]" />
          <span className="font-bold">{investigation.verdict_category}</span>
        </div>
      );
    }
  };

  const getFactStatusBadge = (status: string) => {
    switch (status) {
      case 'VERIFIED_BY_EVIDENCE':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded bg-[#DCFCE7] text-[#166534] border border-[#BBF7D0]">
            <CheckCircle2 className="w-3 h-3" />
            <span>Verified by evidence</span>
          </span>
        );
      case 'SUPPORTED_NOT_VERIFIED':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A]">
            <Info className="w-3 h-3" />
            <span>Supported but not fully verified</span>
          </span>
        );
      case 'CONTRADICTED_BY_EVIDENCE':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded bg-[#FEE2E2] text-[#991B1B] border border-[#FECACA]">
            <XCircle className="w-3 h-3" />
            <span>Contradicted by evidence</span>
          </span>
        );
      case 'PREDICTED_BY_AI_ONLY':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded bg-[#EDE9FE] text-[#6D28D9] border border-[#DDD6FE]">
            <Cpu className="w-3 h-3" />
            <span>Predicted by AI only</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded bg-[#F4F1EA] text-[#5C6661] border border-[#E6E1D8]">
            <HelpCircle className="w-3 h-3" />
            <span>Unknown or unavailable</span>
          </span>
        );
    }
  };

  const matchedEvidence = investigation.evidence_items.find((e) => e.thumbnail_url);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Breadcrumb & Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E6E1D8]">
        <button
          onClick={onBackToWorkspace}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#1B3B2B] hover:underline"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Back to Workspace</span>
        </button>

        <div className="flex flex-wrap items-center gap-2">
          {/* Re-analyze dropdown */}
          <div className="flex items-center gap-1 bg-[#F4F1EA] p-1 rounded-md text-xs">
            <span className="text-[11px] text-[#737E79] px-2">Mode:</span>
            {(['quick', 'deep', 'research'] as InvestigationMode[]).map((m) => (
              <button
                key={m}
                onClick={() => handleReanalyze(m)}
                disabled={isReanalyzing || investigation.mode === m}
                className={`px-2 py-1 rounded text-[11px] capitalize transition-colors ${
                  investigation.mode === m
                    ? 'bg-[#1B3B2B] text-[#FBF9F5] font-semibold'
                    : 'text-[#4A5450] hover:text-[#1A1E1C]'
                }`}
              >
                {m}
              </button>
            ))}
          </div>

          <a
            href={getExportPdfUrl(investigation.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#FFFFFF] border border-[#D9D3C7] hover:bg-[#F4F1EA] rounded-md text-xs font-medium text-[#1A1E1C] transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-[#1B3B2B]" />
            <span>Export PDF</span>
          </a>

          <a
            href={getExportJsonUrl(investigation.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#FFFFFF] border border-[#D9D3C7] hover:bg-[#F4F1EA] rounded-md text-xs font-medium text-[#1A1E1C] transition-colors"
          >
            <FileText className="w-3.5 h-3.5 text-[#1B3B2B]" />
            <span>JSON</span>
          </a>

          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#FFFFFF] border border-[#D9D3C7] hover:bg-[#F4F1EA] rounded-md text-xs font-medium text-[#1A1E1C] transition-colors no-print"
          >
            <Printer className="w-3.5 h-3.5 text-[#1B3B2B]" />
            <span>Print</span>
          </button>

          <button
            onClick={handleShare}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#1B3B2B] text-[#FBF9F5] hover:bg-[#132E20] rounded-md text-xs font-medium transition-colors"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>{copiedLink ? 'Link Copied' : 'Share'}</span>
          </button>
        </div>
      </div>

      {/* Executive Verdict Banner */}
      <div className="editorial-card-elevated p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#F4F1EA]">
          <div>
            <span className="font-mono text-xs uppercase tracking-wider text-[#737E79]">
              INVESTIGATION DOSSIER &bull; ID: {investigation.id.slice(0, 13)}
            </span>
            <h1 className="font-editorial text-2xl sm:text-3xl font-extrabold text-[#1A1E1C] mt-1">
              {investigation.verdict_headline || investigation.verdict_category}
            </h1>
          </div>
          <div>{getVerdictBadge()}</div>
        </div>

        {/* Target Image & Summary Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-4 space-y-3">
            <div className="aspect-video bg-[#1C211F] rounded-md overflow-hidden border border-[#D9D3C7] shadow-sm">
              <img
                src={investigation.image_url}
                alt="Target Under Investigation"
                className="w-full h-full object-contain"
              />
            </div>
            <div className="flex justify-between text-[11px] text-[#737E79] px-1 font-mono">
              <span>SHA-256: {investigation.image_hash.slice(0, 14)}...</span>
              <span>MODE: {investigation.mode.toUpperCase()}</span>
            </div>
          </div>

          <div className="lg:col-span-8 space-y-4">
            {/* Original Claim Banner */}
            <div className="p-4 bg-[#FBF9F5] rounded-md border border-[#E6E1D8] space-y-1">
              <span className="text-[10px] uppercase font-bold tracking-wider text-[#737E79]">
                Original User Claim
              </span>
              <p className="font-editorial text-base font-bold text-[#1A1E1C]">
                "{investigation.original_claim}"
              </p>
            </div>

            {/* Findings Narrative */}
            <div className="space-y-1.5 text-xs text-[#2D3330] leading-relaxed">
              <h3 className="font-editorial text-sm font-bold uppercase tracking-wider text-[#1A1E1C]">
                Executive Findings Summary
              </h3>
              <p className="p-3 bg-[#FFFFFF] rounded border border-[#E6E1D8]">
                {investigation.summary}
              </p>
            </div>

            {/* Reasons for Verdict */}
            {investigation.reasons_for_verdict && investigation.reasons_for_verdict.length > 0 && (
              <div className="space-y-1.5 text-xs">
                <span className="font-bold text-[#1A1E1C] uppercase tracking-wider text-[11px]">
                  Reasons for the Verdict:
                </span>
                <ul className="space-y-1">
                  {investigation.reasons_for_verdict.map((reason, idx) => (
                    <li key={idx} className="flex items-start gap-2 p-2 bg-[#FBF9F5] rounded border border-[#E6E1D8]">
                      <span className="text-[#1B3B2B] font-bold">•</span>
                      <span className="text-[#2C332F]">{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* AI-Generated Visual Observations Panel */}
            <div className="p-4 bg-[#F8F6F0] rounded-md border border-[#D9D3C7] space-y-3 text-xs">
              <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-[#E6E1D8]">
                <div className="flex items-center gap-1.5 font-bold text-[#1B3B2B] uppercase tracking-wider text-[11px]">
                  <Sparkles className="w-3.5 h-3.5 text-[#1B3B2B]" />
                  <span>AI-Generated Visual Observations</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded font-mono bg-[#EAE5DA] text-[#2D3330]">
                  Model: {visionModelUsed}
                </span>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] uppercase font-bold text-[#737E79]">Visual Scene Description:</span>
                <p className="p-2.5 bg-[#FFFFFF] rounded border border-[#E6E1D8] text-[#1A1E1C] italic leading-relaxed">
                  "{aiDescription}"
                </p>
              </div>

              {/* Tags: Category, Objects, Activities */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                {visibleObjects.length > 0 && (
                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-bold text-[#737E79]">Visible Objects:</span>
                    <div className="flex flex-wrap gap-1">
                      {visibleObjects.map((obj: string, oIdx: number) => (
                        <span key={oIdx} className="px-1.5 py-0.5 rounded bg-[#FFFFFF] border border-[#D9D3C7] text-[10px] text-[#2C332F]">
                          {obj}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {visibleActivities.length > 0 && (
                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-bold text-[#737E79]">Visible Activities / Dynamic State:</span>
                    <div className="flex flex-wrap gap-1">
                      {visibleActivities.map((act: string, aIdx: number) => (
                        <span key={aIdx} className="px-1.5 py-0.5 rounded bg-[#FFFFFF] border border-[#D9D3C7] text-[10px] text-[#1B3B2B] font-medium">
                          {act}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {textAndSigns.length > 0 && (
                <div className="space-y-1 pt-1">
                  <span className="text-[10px] uppercase font-bold text-[#737E79]">Signboard & Inscription Text:</span>
                  <div className="flex flex-wrap gap-1">
                    {textAndSigns.map((txt: string, tIdx: number) => (
                      <span key={tIdx} className="px-2 py-0.5 rounded bg-[#FEF3C7] border border-[#FDE68A] text-[10px] text-[#92400E] font-mono">
                        "{txt}"
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {visualUncertainties.length > 0 && (
                <div className="p-2.5 bg-[#FBF9F5] rounded border border-[#E6E1D8] space-y-1">
                  <span className="text-[10px] uppercase font-bold text-[#92400E] block">
                    Visual Uncertainty & Scope Limitations:
                  </span>
                  <ul className="text-[11px] text-[#5C6661] space-y-0.5">
                    {visualUncertainties.map((u: string, uIdx: number) => (
                      <li key={uIdx} className="flex items-start gap-1">
                        <span className="text-[#C97A1E] font-bold">•</span>
                        <span>{u}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Dynamic Claim Deconstruction & Verification Questions Panel */}
            <div className="p-4 bg-[#FFFFFF] rounded-md border border-[#E6E1D8] space-y-3 text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-[#F4F1EA]">
                <div className="flex items-center gap-1.5 font-bold text-[#1A1E1C] uppercase tracking-wider text-[11px]">
                  <ListChecks className="w-3.5 h-3.5 text-[#1B3B2B]" />
                  <span>Claim Deconstruction & Verification Questions</span>
                </div>
                <span className="text-[10px] text-[#737E79]">Dynamic Claim Parsing</span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                <div className="p-2 bg-[#FBF9F5] rounded border border-[#E6E1D8]">
                  <span className="text-[9px] uppercase text-[#737E79] block">Subject / Event</span>
                  <span className="font-semibold text-[#1A1E1C] block">{claimBreakdown.event || 'Unspecified'}</span>
                </div>
                <div className="p-2 bg-[#FBF9F5] rounded border border-[#E6E1D8]">
                  <span className="text-[9px] uppercase text-[#737E79] block">Claimed Location</span>
                  <span className="font-semibold text-[#1B3B2B] block">{claimBreakdown.location || 'None Asserted'}</span>
                </div>
                <div className="p-2 bg-[#FBF9F5] rounded border border-[#E6E1D8]">
                  <span className="text-[9px] uppercase text-[#737E79] block">Claimed Time</span>
                  <span className="font-semibold text-[#1A1E1C] block">{claimBreakdown.time_reference || 'Unspecified'}</span>
                </div>
                <div className="p-2 bg-[#FBF9F5] rounded border border-[#E6E1D8]">
                  <span className="text-[9px] uppercase text-[#737E79] block">Entities Detected</span>
                  <span className="font-semibold text-[#1A1E1C] block">{claimBreakdown.extracted_entities?.join(', ') || 'None'}</span>
                </div>
              </div>

              {verificationQuestions.length > 0 && (
                <div className="space-y-1">
                  <span className="text-[10px] uppercase font-bold text-[#737E79]">Investigation Questions:</span>
                  <ul className="space-y-1 text-[11px] text-[#2D3330]">
                    {verificationQuestions.map((q: string, qIdx: number) => (
                      <li key={qIdx} className="p-1.5 bg-[#F8F6F0] rounded border border-[#E6E1D8]">
                        {q}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Visual Consistency Breakdown */}
              {visualConsistency && (visualConsistency.consistent_parts?.length > 0 || visualConsistency.inconsistent_parts?.length > 0) && (
                <div className="pt-1 space-y-1.5">
                  <span className="text-[10px] uppercase font-bold text-[#737E79]">Claim vs Visual Consistency:</span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                    {visualConsistency.consistent_parts?.length > 0 && (
                      <div className="p-2 bg-[#DCFCE7]/40 rounded border border-[#BBF7D0] space-y-0.5">
                        <span className="font-bold text-[#166534] text-[10px] block">Directly Consistent with Image:</span>
                        {visualConsistency.consistent_parts.map((p: string, pIdx: number) => (
                          <p key={pIdx} className="text-[#166534]">• {p}</p>
                        ))}
                      </div>
                    )}
                    {visualConsistency.inconsistent_parts?.length > 0 && (
                      <div className="p-2 bg-[#FEE2E2]/40 rounded border border-[#FECACA] space-y-0.5">
                        <span className="font-bold text-[#991B1B] text-[10px] block">Visually Inconsistent / Contradicted:</span>
                        {visualConsistency.inconsistent_parts.map((p: string, pIdx: number) => (
                          <p key={pIdx} className="text-[#991B1B]">• {p}</p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 8 DECOUPLED ANALYSIS PILLARS GRID */}
        <div className="pt-4 border-t border-[#F4F1EA] space-y-4">
          <div className="flex items-center gap-2">
            <Scale className="w-4 h-4 text-[#1B3B2B]" />
            <h3 className="font-editorial text-sm font-bold uppercase tracking-wider text-[#1A1E1C]">
              Decoupled Analysis Pillars (Strict Separation of Guesses vs Verified Facts)
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
            {/* Pillar 1: Claimed Location */}
            <div className="p-3.5 bg-[#FFFFFF] rounded border border-[#E6E1D8] space-y-1">
              <span className="text-[10px] uppercase tracking-wider text-[#737E79] block">
                1. User-Claimed Location
              </span>
              <span className="font-semibold text-sm text-[#1A1E1C] block">
                {investigation.claimed_location || 'None Specified'}
              </span>
              <span className="text-[10px] text-[#737E79]">Source: Stated by user</span>
            </div>

            {/* Pillar 2: Best-Supported Actual Location */}
            <div className="p-3.5 bg-[#FFFFFF] rounded border border-[#E6E1D8] space-y-1">
              <span className="text-[10px] uppercase tracking-wider text-[#737E79] block">
                2. Best-Supported Location
              </span>
              <span className="font-semibold text-sm text-[#1B3B2B] block">
                {investigation.best_supported_location}
              </span>
              <span className="text-[10px] text-[#737E79]">
                Verification: {investigation.location_verification_status}
              </span>
            </div>

            {/* Pillar 3: Image Authenticity Status */}
            <div className="p-3.5 bg-[#FFFFFF] rounded border border-[#E6E1D8] space-y-1">
              <span className="text-[10px] uppercase tracking-wider text-[#737E79] block">
                3. Image Authenticity
              </span>
              <span className="font-semibold text-sm text-[#1A1E1C] block">
                {investigation.image_authenticity_status}
              </span>
              <span className="text-[10px] text-[#737E79]">
                Decoupled from location veracity
              </span>
            </div>

            {/* Pillar 4: Event & Date Status */}
            <div className="p-3.5 bg-[#FFFFFF] rounded border border-[#E6E1D8] space-y-1">
              <span className="text-[10px] uppercase tracking-wider text-[#737E79] block">
                4. Event / Date Status
              </span>
              <span className="font-semibold text-sm text-[#1A1E1C] block">
                {investigation.event_date_verification_status}
              </span>
              <span className="text-[10px] text-[#737E79]">
                Archival & temporal alignment
              </span>
            </div>
          </div>

          {/* CLAIM FACT VERIFICATION MATRIX (Section 4 Requirement) */}
          {investigation.fact_claim_matrix && investigation.fact_claim_matrix.length > 0 && (
            <div className="p-4 bg-[#FFFFFF] rounded border border-[#E6E1D8] space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-editorial text-sm font-bold uppercase tracking-wider text-[#1A1E1C]">
                  Atomic Claim Verification Matrix
                </span>
                <span className="text-[10px] text-[#737E79]">
                  Each claimed assertion evaluated independently against evidence
                </span>
              </div>

              <div className="divide-y divide-[#F4F1EA]">
                {investigation.fact_claim_matrix.map((fact, idx) => (
                  <div key={idx} className="py-2.5 flex flex-col md:flex-row md:items-center justify-between gap-2">
                    <div className="space-y-0.5 md:w-1/3">
                      <span className="font-bold text-[#1A1E1C]">{fact.fact_name}</span>
                      <p className="text-[11px] text-[#5C6661]">
                        Asserted: <span className="font-medium text-[#1A1E1C]">"{fact.asserted_value}"</span>
                      </p>
                    </div>

                    <div className="md:w-1/3">
                      {getFactStatusBadge(fact.verification_status)}
                      <p className="text-[11px] text-[#2C332F] mt-1">
                        Supported Finding: <span className="font-semibold text-[#1B3B2B]">{fact.supported_value}</span>
                      </p>
                    </div>

                    <div className="md:w-1/3 text-[11px] text-[#5C6661] space-y-1">
                      <p>{fact.explanation}</p>
                      {fact.source_urls && fact.source_urls.length > 0 && (
                        <div className="flex flex-wrap gap-2 pt-0.5">
                          {fact.source_urls.map((url, uIdx) => (
                            <a
                              key={uIdx}
                              href={url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-[10px] text-[#1B3B2B] hover:underline font-semibold"
                            >
                              <span>Source Link {uIdx + 1}</span>
                              <ExternalLink className="w-2.5 h-2.5" />
                            </a>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Candidate Locations List */}
          {investigation.candidate_locations && investigation.candidate_locations.length > 0 && (
            <div className="p-4 bg-[#FBF9F5] rounded border border-[#E6E1D8] space-y-2 text-xs">
              <span className="font-bold text-[#1A1E1C] block">
                Candidate Landmark & Location Hypotheses Evaluated:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {investigation.candidate_locations.map((cand, idx) => (
                  <div key={idx} className="p-2.5 bg-[#FFFFFF] rounded border border-[#E6E1D8] space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#1A1E1C]">{cand.candidate_name} ({cand.candidate_city})</span>
                      <span className={`text-[10px] uppercase px-1.5 py-0.5 rounded font-mono ${cand.is_verified ? 'bg-[#DCFCE7] text-[#166534]' : 'bg-[#EAE5DA] text-[#4A5450]'}`}>
                        {cand.is_verified ? 'Verified Location' : 'Hypothesis'}
                      </span>
                    </div>
                    <ul className="text-[11px] text-[#5C6661] space-y-0.5">
                      {cand.supporting_clues.map((c, cIdx) => (
                        <li key={cIdx}>• {c}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Confidence Calculation Rationale */}
          <div className="p-3.5 bg-[#EAF2ED] rounded border border-[#C5DDD0] text-xs text-[#1B3B2B] flex items-start gap-2.5">
            <ShieldCheck className="w-4 h-4 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-bold block uppercase tracking-wide">
                Confidence Calibrated Level: {investigation.confidence_level.replace('_', ' ').toUpperCase()}
              </span>
              <span className="text-[11px] text-[#2C4A38] leading-relaxed block">
                {investigation.confidence_explanation || 'Confidence is calibrated based on independent multi-source corroboration, architectural feature matches, and absence of contradictory records. TRUTHLENS never presents a fabricated percentage.'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Investigation Deep-Dive Tabs */}
      <div className="space-y-6">
        <div className="border-b border-[#E6E1D8] flex flex-wrap gap-2 text-xs font-semibold">
          {[
            { id: 'evidence', label: `Evidence Items (${investigation.evidence_items.length})`, icon: FileText },
            { id: 'trace', label: 'Investigation Trace', icon: Terminal },
            { id: 'comparison', label: 'Visual Comparison', icon: Columns },
            { id: 'forensics', label: 'Camera & EXIF Forensics', icon: Camera },
            { id: 'timeline', label: 'Chronological Timeline', icon: Calendar },
            { id: 'uncertainty', label: 'Epistemic Uncertainty', icon: Scale },
            { id: 'assistant', label: 'Ask About the Evidence', icon: MessageSquare },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 py-3 px-4 border-b-2 transition-all ${
                  isActive
                    ? 'border-[#1B3B2B] text-[#1B3B2B] bg-[#FFFFFF]/60'
                    : 'border-transparent text-[#5C6661] hover:text-[#1A1E1C]'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content Panes */}
        <div>
          {activeTab === 'evidence' && (
            <div className="space-y-4">
              {investigation.evidence_items.length > 0 ? (
                <>
                  {/* Evidence Stance Filter Bar */}
                  <div className="flex flex-wrap items-center justify-between gap-2 p-2 bg-[#F4F1EA] rounded-md text-xs">
                    <div className="flex items-center gap-1 font-semibold text-[#1A1E1C]">
                      <Filter className="w-3.5 h-3.5 text-[#1B3B2B]" />
                      <span>Filter by Claim Relationship:</span>
                    </div>
                    <div className="flex flex-wrap items-center gap-1.5">
                      <button
                        onClick={() => setEvidenceFilter('all')}
                        className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                          evidenceFilter === 'all'
                            ? 'bg-[#1B3B2B] text-[#FBF9F5] font-bold'
                            : 'bg-[#FFFFFF] text-[#4A5450] hover:text-[#1A1E1C]'
                        }`}
                      >
                        All Sources ({investigation.evidence_items.length})
                      </button>
                      <button
                        onClick={() => setEvidenceFilter('supports')}
                        className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                          evidenceFilter === 'supports'
                            ? 'bg-[#166534] text-[#FFFFFF] font-bold'
                            : 'bg-[#DCFCE7] text-[#166534] hover:bg-[#BBF7D0]'
                        }`}
                      >
                        Corroborating ({supportsCount})
                      </button>
                      <button
                        onClick={() => setEvidenceFilter('contradicts')}
                        className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                          evidenceFilter === 'contradicts'
                            ? 'bg-[#991B1B] text-[#FFFFFF] font-bold'
                            : 'bg-[#FEE2E2] text-[#991B1B] hover:bg-[#FECACA]'
                        }`}
                      >
                        Contradicting ({contradictsCount})
                      </button>
                      <button
                        onClick={() => setEvidenceFilter('neutral')}
                        className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                          evidenceFilter === 'neutral'
                            ? 'bg-[#4A5450] text-[#FFFFFF] font-bold'
                            : 'bg-[#EAE5DA] text-[#4A5450] hover:bg-[#D9D3C7]'
                        }`}
                      >
                        Contextual ({neutralCount})
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-4">
                    {filteredEvidence.length > 0 ? (
                      filteredEvidence.map((ev, idx) => (
                        <EvidenceCard key={ev.id} evidence={ev} rank={idx + 1} />
                      ))
                    ) : (
                      <div className="p-6 text-center text-xs text-[#737E79] bg-[#FFFFFF] rounded border border-[#E6E1D8]">
                        No evidence items match the selected filter category ('{evidenceFilter}').
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <div className="editorial-card p-8 text-center text-xs text-[#5C6661] space-y-3">
                  <HelpCircle className="w-8 h-8 text-[#C97A1E] mx-auto" />
                  <p className="font-bold text-sm text-[#1A1E1C]">Evidence Items: 0 Retrieved</p>
                  <div className="max-w-xl mx-auto p-4 bg-[#FBF9F5] rounded border border-[#E6E1D8] text-left space-y-2 text-[11px]">
                    <span className="font-bold text-[#1A1E1C] block">Audit Diagnostics:</span>
                    <ul className="space-y-1 list-disc list-inside text-[#4A5450]">
                      <li>Local reference corpus contained 0 documents exceeding the relevance threshold for this specific assertion.</li>
                      <li>Live encyclopedic adapter queried public Wikipedia without finding high-relevance matches.</li>
                      <li>External commercial search APIs (Serper / Tavily) are currently unconfigured in the server environment.</li>
                      <li>In accordance with ethical AI standards, TRUTHLENS refrains from hallucinating evidence and marks this case as <em>Insufficient Evidence</em>.</li>
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'trace' && (
            <InvestigationTracePanel trace={investigation.investigation_trace} />
          )}

          {activeTab === 'comparison' && (
            <ImageComparisonSlider
              originalImageUrl={investigation.image_url}
              originalLabel="Investigated Upload"
              matchedImageUrl={matchedEvidence?.thumbnail_url || null}
              matchedTitle={matchedEvidence?.source_title || null}
              similarityScore={matchedEvidence?.retrieval_score || null}
              provenanceText={
                matchedEvidence
                  ? `Corroborated by ${matchedEvidence.publisher}. Visual similarity matches historical capture dated ${matchedEvidence.publication_date || 'earlier'}.`
                  : null
              }
            />
          )}

          {activeTab === 'forensics' && investigation.image_analysis && (
            <ExifInspector
              analysis={investigation.image_analysis}
              investigationId={investigation.id}
            />
          )}

          {activeTab === 'timeline' && (
            <EvidenceTimeline
              evidenceItems={investigation.evidence_items}
              investigationCreatedAt={investigation.created_at}
              claimedDate={investigation.claim_breakdown?.time_reference}
            />
          )}

          {activeTab === 'uncertainty' && (
            <UncertaintyPanel
              status={investigation.verdict_category as any}
              confidence={investigation.confidence_level}
              summary={investigation.summary}
              evidenceCount={investigation.evidence_items.length}
            />
          )}

          {activeTab === 'assistant' && (
            <ResearchAssistantDrawer investigationId={investigation.id} />
          )}
        </div>
      </div>

      {/* Unverified Details & Next Steps Footer Card */}
      <div className="editorial-card p-6 bg-[#FBF9F5] space-y-4">
        <h4 className="font-editorial text-sm font-bold uppercase tracking-wider text-[#1A1E1C]">
          Unverified Details & Next Recommended Investigative Steps
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="space-y-1.5">
            <span className="font-bold text-[#737E79] uppercase text-[10px]">Unverified Elements:</span>
            <ul className="space-y-1 text-[#4A5450]">
              {investigation.unverified_details && investigation.unverified_details.length > 0 ? (
                investigation.unverified_details.map((u, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-[#C97A1E]">•</span>
                    <span>{u}</span>
                  </li>
                ))
              ) : (
                <li className="italic text-[#737E79]">All primary core claims were either corroborated or disproved.</li>
              )}
            </ul>
          </div>

          <div className="space-y-1.5">
            <span className="font-bold text-[#737E79] uppercase text-[10px]">Recommended Actions:</span>
            <ul className="space-y-1 text-[#4A5450]">
              {investigation.next_verification_steps && investigation.next_verification_steps.length > 0 ? (
                investigation.next_verification_steps.map((step, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-[#1B3B2B]">•</span>
                    <span>{step}</span>
                  </li>
                ))
              ) : (
                <li className="italic text-[#737E79]">No further automated steps required.</li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
