import React from 'react';
import { Calendar, Clock, AlertCircle, CheckCircle } from 'lucide-react';
import { EvidenceItem } from '../types';

interface TimelineProps {
  evidenceItems: EvidenceItem[];
  investigationCreatedAt: string;
  claimedDate?: string | null;
}

interface TimelineEvent {
  date: string;
  title: string;
  type: 'capture' | 'publication' | 'claim' | 'investigation';
  description: string;
  publisher?: string;
}

export const EvidenceTimeline: React.FC<TimelineProps> = ({
  evidenceItems,
  investigationCreatedAt,
  claimedDate
}) => {
  // Construct timeline events
  const events: TimelineEvent[] = [];

  // Claimed time
  if (claimedDate) {
    events.push({
      date: claimedDate,
      title: 'Asserted Event Time',
      type: 'claim',
      description: `Claim specifies that the image depicts events occurring ${claimedDate.toLowerCase()}.`
    });
  }

  // Publication dates from evidence
  evidenceItems.forEach((ev) => {
    if (ev.publication_date && ev.publication_date !== 'Unknown') {
      events.push({
        date: ev.publication_date,
        title: ev.source_title,
        type: 'publication',
        description: `Published by ${ev.publisher} (${ev.relationship_to_claim === 'contradicts' ? 'Contradictory Record' : 'Corroborating Record'}).`,
        publisher: ev.publisher
      });
    }
  });

  // Current investigation time
  events.push({
    date: new Date(investigationCreatedAt).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }),
    title: 'TRUTHLENS Forensic Analysis Executed',
    type: 'investigation',
    description: 'System performed multimodal verification and reference document indexing.'
  });

  // Sort events chronologically if date formats match YYYY-MM-DD
  events.sort((a, b) => a.date.localeCompare(b.date));

  return (
    <div className="editorial-card p-6">
      <div className="flex items-center gap-2 mb-6 pb-3 border-b border-[#F4F1EA]">
        <Calendar className="w-4 h-4 text-[#1B3B2B]" />
        <h3 className="font-editorial text-base font-bold uppercase tracking-wider text-[#1A1E1C]">
          Chronological Evidence Timeline
        </h3>
      </div>

      <div className="relative pl-6 space-y-8 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#D9D3C7]">
        {events.map((ev, index) => {
          let dotColor = 'bg-[#1B3B2B]';
          if (ev.type === 'claim') dotColor = 'bg-[#C97A1E]';
          if (ev.type === 'publication') dotColor = 'bg-[#1A1E1C]';

          return (
            <div key={index} className="relative group">
              {/* Dot on line */}
              <div
                className={`absolute -left-[27px] top-1 w-3.5 h-3.5 rounded-full border-2 border-[#FFFFFF] ${dotColor} shadow-xs`}
              />

              <div className="bg-[#FBF9F5] p-4 rounded-md border border-[#E6E1D8] transition-all hover:border-[#1B3B2B]/40">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1">
                  <span className="font-mono text-xs font-bold text-[#1B3B2B]">
                    {ev.date}
                  </span>
                  <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded bg-[#EAE5DA] text-[#4A5450]">
                    {ev.type}
                  </span>
                </div>
                <h4 className="font-editorial text-sm font-bold text-[#1A1E1C] mb-1">
                  {ev.title}
                </h4>
                <p className="text-xs text-[#4A5450] leading-relaxed">
                  {ev.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-[#F4F1EA] text-[11px] text-[#737E79] flex items-center gap-2">
        <Clock className="w-3.5 h-3.5 text-[#1B3B2B]" />
        <span>
          A significant gap between earliest publication date and asserted viral claim date is a hallmark of temporal misattribution.
        </span>
      </div>
    </div>
  );
};
