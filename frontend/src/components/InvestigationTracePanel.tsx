import React from 'react';
import { Terminal, Search, CheckCircle2, XCircle, HelpCircle, ArrowRight, ExternalLink, Globe, Layers, AlertTriangle } from 'lucide-react';
import { InvestigationTrace } from '../types';

interface TraceProps {
  trace: InvestigationTrace;
}

export const InvestigationTracePanel: React.FC<TraceProps> = ({ trace }) => {
  if (!trace) {
    return (
      <div className="editorial-card p-6 text-xs text-[#737E79]">
        No audit trace available for this record.
      </div>
    );
  }

  return (
    <div className="editorial-card p-6 space-y-6">
      <div className="flex items-center justify-between pb-3 border-b border-[#F4F1EA]">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-[#1B3B2B]" />
          <h3 className="font-editorial text-base font-bold uppercase tracking-wider text-[#1A1E1C]">
            Auditable Investigation Trace
          </h3>
        </div>
        <span className="text-[10px] font-mono bg-[#EAF2ED] text-[#1B3B2B] px-2 py-0.5 rounded border border-[#C5DDD0]">
          Zero Fabricated Steps &bull; Grounded Audit Log
        </span>
      </div>

      {/* Zero Evidence Alert Box if applicable */}
      {trace.zero_evidence_reason && (
        <div className="p-4 bg-[#FFFBEB] rounded-md border border-[#FDE68A] text-xs text-[#92400E] flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-[#C97A1E] shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold block">Zero Evidence Retrieved Explanation:</span>
            <p className="leading-relaxed">{trace.zero_evidence_reason}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        {/* Queries Executed */}
        <div className="p-4 bg-[#FBF9F5] rounded-md border border-[#E6E1D8] space-y-2">
          <span className="font-bold text-[#1A1E1C] flex items-center gap-1.5">
            <Search className="w-3.5 h-3.5 text-[#1B3B2B]" />
            Search Queries Executed ({trace.search_queries_executed?.length || 0})
          </span>
          <ul className="space-y-1 font-mono text-[11px] text-[#4A5450]">
            {trace.search_queries_executed && trace.search_queries_executed.length > 0 ? (
              trace.search_queries_executed.map((q, idx) => (
                <li key={idx} className="p-1.5 bg-[#FFFFFF] rounded border border-[#E6E1D8]">
                  {q}
                </li>
              ))
            ) : (
              <li className="italic text-[#737E79]">No queries executed.</li>
            )}
          </ul>
        </div>

        {/* Providers Used & Configuration Status */}
        <div className="p-4 bg-[#FBF9F5] rounded-md border border-[#E6E1D8] space-y-2">
          <span className="font-bold text-[#1A1E1C] flex items-center gap-1.5">
            <Globe className="w-3.5 h-3.5 text-[#1B3B2B]" />
            Reference Providers & Active Status
          </span>
          <ul className="space-y-1.5 text-[11px] text-[#4A5450]">
            {trace.provider_status ? (
              Object.entries(trace.provider_status).map(([prov, stat], idx) => (
                <li key={idx} className="flex items-center justify-between p-1.5 bg-[#FFFFFF] rounded border border-[#E6E1D8]">
                  <span className="font-semibold text-[#1A1E1C] capitalize">{prov.replace(/_/g, ' ')}:</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${stat.startsWith('Active') ? 'bg-[#DCFCE7] text-[#166534]' : 'bg-[#FEF3C7] text-[#92400E]'}`}>
                    {stat}
                  </span>
                </li>
              ))
            ) : (
              (trace.search_providers_used || []).map((p, idx) => (
                <li key={idx} className="flex items-center gap-1.5 p-1.5 bg-[#FFFFFF] rounded border border-[#E6E1D8]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#1B7A43] shrink-0" />
                  <span>{p}</span>
                </li>
              ))
            )}
          </ul>
        </div>
      </div>

      {/* Candidate Evaluations & Rejected Candidates */}
      <div className="space-y-3">
        <h4 className="font-editorial text-sm font-bold text-[#1A1E1C]">
          Candidate Hypothesis Evaluation & Decision Rationale
        </h4>

        {trace.rejected_candidates && trace.rejected_candidates.length > 0 ? (
          <div className="space-y-2">
            {trace.rejected_candidates.map((rej, idx) => (
              <div key={idx} className="p-3 bg-[#FFFBEB] rounded border border-[#FDE68A] text-xs flex items-start gap-2 text-[#92400E]">
                <XCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">{rej.candidate}: </span>
                  <span>{rej.reason}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-3 bg-[#FBF9F5] rounded border border-[#E6E1D8] text-xs text-[#5C6661]">
            All viable candidates met independent verification thresholds or were resolved.
          </div>
        )}
      </div>

      {/* Visual Clues Detected */}
      {trace.visual_clues_detected && trace.visual_clues_detected.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-editorial text-sm font-bold text-[#1A1E1C]">
            Detected Visual Clues & Architectural Features
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {trace.visual_clues_detected.map((clue, idx) => (
              <span key={idx} className="text-[11px] px-2.5 py-1 rounded bg-[#EAF2ED] text-[#1B3B2B] border border-[#C5DDD0]">
                {clue}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Unresolved Questions */}
      {trace.unresolved_questions && trace.unresolved_questions.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-[#F4F1EA]">
          <h4 className="font-editorial text-sm font-bold text-[#1A1E1C] flex items-center gap-1.5">
            <HelpCircle className="w-4 h-4 text-[#C97A1E]" />
            <span>Unresolved Questions & Epistemic Boundaries</span>
          </h4>
          <ul className="space-y-1 text-xs text-[#5C6661]">
            {trace.unresolved_questions.map((q, idx) => (
              <li key={idx} className="flex items-start gap-1.5">
                <span className="text-[#C97A1E]">•</span>
                <span>{q}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
