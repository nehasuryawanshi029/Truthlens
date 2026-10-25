import React from 'react';
import { AlertCircle, HelpCircle, ShieldAlert, CheckCircle2, Scale } from 'lucide-react';
import { AssessmentStatus, ConfidenceLevel } from '../types';

interface UncertaintyProps {
  status: AssessmentStatus;
  confidence: ConfidenceLevel;
  summary?: string | null;
  evidenceCount: number;
}

export const UncertaintyPanel: React.FC<UncertaintyProps> = ({
  status,
  confidence,
  summary,
  evidenceCount
}) => {
  const getConfidenceDetails = () => {
    switch (confidence) {
      case 'strong_evidence':
        return {
          title: 'Strong Corroborating / Contradictory Evidence',
          color: 'text-[#1B7A43]',
          desc: 'Multiple authoritative records corroborate the date, location, or visual origin of this image.'
        };
      case 'moderate_evidence':
        return {
          title: 'Moderate Contextual Corroboration',
          color: 'text-[#1B3B2B]',
          desc: 'Relevant context retrieved, but direct primary coverage contains partial gaps.'
        };
      case 'insufficient':
        return {
          title: 'Insufficient Ground Evidence Available',
          color: 'text-[#C97A1E]',
          desc: 'Index contains no verified archival match. The platform strictly abstains rather than inventing a verdict.'
        };
      default:
        return {
          title: 'Automated Forensic Analysis Inconclusive',
          color: 'text-[#737E79]',
          desc: 'Signals do not reach statistical threshold for decisive classification.'
        };
    }
  };

  const confInfo = getConfidenceDetails();

  return (
    <div className="editorial-card p-6 space-y-4">
      <div className="flex items-center gap-2 pb-3 border-b border-[#F4F1EA]">
        <Scale className="w-4 h-4 text-[#1B3B2B]" />
        <h3 className="font-editorial text-base font-bold uppercase tracking-wider text-[#1A1E1C]">
          Epistemic Uncertainty & Methodology Principles
        </h3>
      </div>

      <div className="p-4 bg-[#FBF9F5] rounded border border-[#E6E1D8]">
        <div className="flex items-center gap-2 mb-1">
          <span className={`text-xs font-bold uppercase tracking-wider ${confInfo.color}`}>
            {confInfo.title}
          </span>
        </div>
        <p className="text-xs text-[#4A5450] leading-relaxed">
          {confInfo.desc}
        </p>
      </div>

      {/* Disentanglement Principles Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-1">
        <div className="p-3 bg-[#FFFFFF] rounded border border-[#E6E1D8] space-y-1">
          <div className="font-bold text-[#1A1E1C]">Image Authenticity ≠ Claim Veracity</div>
          <p className="text-[11px] text-[#5C6661] leading-normal">
            A 100% genuine, unaltered photograph taken in 2019 can still be circulated with a completely false 2026 caption.
          </p>
        </div>

        <div className="p-3 bg-[#FFFFFF] rounded border border-[#E6E1D8] space-y-1">
          <div className="font-bold text-[#1A1E1C]">Absence of Evidence ≠ Proof of Falsity</div>
          <p className="text-[11px] text-[#5C6661] leading-normal">
            If our index finds no news articles about a hyper-local event, TRUTHLENS marks it as <em>Insufficient Evidence</em>, never falsely as "Fake".
          </p>
        </div>
      </div>
    </div>
  );
};
