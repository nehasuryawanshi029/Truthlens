import React, { useState } from 'react';
import { ExternalLink, CheckCircle2, XCircle, HelpCircle, Shield, ChevronDown, ChevronUp } from 'lucide-react';
import { EvidenceItem } from '../types';

interface EvidenceCardProps {
  evidence: EvidenceItem;
  rank: number;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({ evidence, rank }) => {
  const [expanded, setExpanded] = useState(false);
  const [showReliabilityDetails, setShowReliabilityDetails] = useState(false);

  const getRelationshipBadge = () => {
    switch (evidence.relationship_to_claim) {
      case 'contradicts':
        return (
          <span className="editorial-badge status-contradicted flex items-center gap-1">
            <XCircle className="w-3.5 h-3.5" />
            <span>Contradicts Claim</span>
          </span>
        );
      case 'supports':
        return (
          <span className="editorial-badge status-supported flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Corroborates Claim</span>
          </span>
        );
      default:
        return (
          <span className="editorial-badge status-conflicting flex items-center gap-1">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Contextual Record</span>
          </span>
        );
    }
  };

  const reliabilityPercent = Math.round(evidence.reliability_score * 100);
  const retrievalPercent = Math.round(evidence.retrieval_score * 100);

  return (
    <div className="editorial-card p-5 transition-all hover:border-[#1B3B2B]/30">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3 pb-3 border-b border-[#F4F1EA]">
        <div className="flex items-center gap-2.5">
          <span className="w-6 h-6 rounded bg-[#F4F1EA] text-[#4A5450] font-mono text-xs flex items-center justify-center font-bold">
            #{rank}
          </span>
          <span className="font-semibold text-xs tracking-wider uppercase text-[#1B3B2B]">
            {evidence.publisher}
          </span>
          {evidence.publication_date && (
            <span className="text-xs text-[#737E79]">
              • {evidence.publication_date}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          {getRelationshipBadge()}
        </div>
      </div>

      {/* Title */}
      <h3 className="font-editorial text-base font-bold text-[#1A1E1C] mb-2 leading-snug">
        {evidence.source_title}
      </h3>

      {/* Excerpt Passage */}
      <div className="bg-[#FBF9F5] p-3.5 rounded border border-[#E6E1D8] text-xs text-[#2D3330] leading-relaxed mb-4">
        <p className="italic">
          "{expanded ? evidence.passage : `${evidence.passage.slice(0, 220)}...`}"
        </p>
        {evidence.passage.length > 220 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-2 text-[11px] font-semibold text-[#1B3B2B] hover:underline flex items-center gap-1"
          >
            {expanded ? (
              <>Show Less <ChevronUp className="w-3 h-3" /></>
            ) : (
              <>Read Full Passage <ChevronDown className="w-3 h-3" /></>
            )}
          </button>
        )}
      </div>

      {/* Footer Metrics and Source Link */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs">
        <div className="flex items-center gap-4 text-[#5C6661]">
          <div className="flex items-center gap-1.5" title="Relevance match from hybrid semantic retrieval">
            <span className="text-[11px] uppercase tracking-wider text-[#737E79]">Relevance:</span>
            <span className="font-mono font-medium text-[#1A1E1C]">{retrievalPercent}%</span>
          </div>

          <div className="relative">
            <button
              onClick={() => setShowReliabilityDetails(!showReliabilityDetails)}
              className="flex items-center gap-1.5 hover:text-[#1B3B2B] transition-colors"
              title="Click to view 5-factor credibility breakdown"
            >
              <Shield className="w-3.5 h-3.5 text-[#1B3B2B]" />
              <span className="text-[11px] uppercase tracking-wider text-[#737E79]">Reliability:</span>
              <span className="font-mono font-medium text-[#1A1E1C] underline decoration-dotted">
                {reliabilityPercent}%
              </span>
            </button>

            {/* Reliability Tooltip / Modal Popover */}
            {showReliabilityDetails && (
              <div className="absolute left-0 bottom-full mb-2 w-72 bg-[#FFFFFF] border border-[#D9D3C7] shadow-lg rounded-md p-3 text-[11px] z-20 text-[#2D3330]">
                <div className="font-bold text-xs text-[#1A1E1C] mb-2 border-b border-[#E6E1D8] pb-1">
                  5-Factor Source Assessment
                </div>
                <ul className="space-y-1.5">
                  <li className="flex justify-between">
                    <span>Identifiable Publisher:</span>
                    <span className="font-semibold text-[#1B3B2B]">
                      {evidence.indicators.publisher_identifiable ? 'Verified' : 'Unspecified'}
                    </span>
                  </li>
                  <li className="flex justify-between">
                    <span>Established Press/Agency:</span>
                    <span className="font-semibold text-[#1B3B2B]">
                      {evidence.indicators.is_established_outlet ? 'Yes (Major Wire)' : 'Standard'}
                    </span>
                  </li>
                  <li className="flex justify-between">
                    <span>Documented Timestamp:</span>
                    <span className="font-semibold text-[#1B3B2B]">
                      {evidence.indicators.date_present ? 'Present' : 'Missing'}
                    </span>
                  </li>
                  <li className="flex justify-between">
                    <span>Primary Linkage:</span>
                    <span className="font-semibold text-[#1B3B2B]">
                      {evidence.indicators.primary_source_linked ? 'Direct' : 'Secondary'}
                    </span>
                  </li>
                </ul>
                <div className="mt-2 pt-1 border-t border-[#E6E1D8] text-[10px] text-[#737E79]">
                  Scores reflect source transparency and citation rigor, not an absolute guarantee of factual reality.
                </div>
              </div>
            )}
          </div>
        </div>

        <a
          href={evidence.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#1B3B2B] hover:text-[#132E20] hover:underline"
        >
          <span>Examine Original Source</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  );
};
