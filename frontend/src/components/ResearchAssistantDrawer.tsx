import React, { useState } from 'react';
import { MessageSquare, Send, Sparkles, AlertCircle, Bookmark, CheckCircle2, X } from 'lucide-react';
import { queryAssistant } from '../services/api';
import { AssistantResponse } from '../types';

interface AssistantProps {
  investigationId: string;
}

export const ResearchAssistantDrawer: React.FC<AssistantProps> = ({ investigationId }) => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<AssistantResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  const predefinedQuestions = [
    'Which evidence contradicts the claim?',
    'Why was this source considered relevant?',
    'What information is still missing?',
    'What should I investigate next?'
  ];

  const handleSend = async (queryText: string) => {
    if (!queryText.trim() || loading) return;
    setLoading(true);
    setError(null);

    try {
      const resp = await queryAssistant(investigationId, queryText);
      setHistory((prev) => [...prev, resp]);
      setQuestion('');
    } catch (err: any) {
      setError(err.message || 'Assistant service failed to respond.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="editorial-card p-6 space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-[#F4F1EA]">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-[#1B3B2B]" />
          <h3 className="font-editorial text-base font-bold uppercase tracking-wider text-[#1A1E1C]">
            Interactive Assistant: Ask About the Evidence
          </h3>
        </div>
        <span className="text-[10px] font-mono uppercase bg-[#EAF2ED] text-[#1B3B2B] px-2 py-0.5 rounded border border-[#C5DDD0]">
          Strictly Grounded
        </span>
      </div>

      <p className="text-xs text-[#5C6661] leading-relaxed">
        Query the investigative dossier. Responses are synthesized strictly from retrieved documents and forensic signals with zero outside hallucination.
      </p>

      {/* Preset Query Chips */}
      <div className="flex flex-wrap gap-2">
        {predefinedQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            disabled={loading}
            className="text-[11px] bg-[#F4F1EA] hover:bg-[#EAE5DA] text-[#2C332F] px-2.5 py-1.5 rounded-md border border-[#D9D3C7] transition-colors disabled:opacity-50 text-left"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Conversation Thread */}
      {history.length > 0 && (
        <div className="space-y-4 pt-2">
          {history.map((item, idx) => (
            <div key={idx} className="space-y-2">
              <div className="flex justify-end">
                <div className="bg-[#1B3B2B] text-[#FBF9F5] text-xs p-3 rounded-lg max-w-md shadow-xs">
                  {item.question}
                </div>
              </div>

              <div className="bg-[#FBF9F5] border border-[#E6E1D8] p-4 rounded-lg text-xs text-[#232826] space-y-2">
                <div className="flex items-center gap-1.5 font-bold text-[#1B3B2B]">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Dossier Grounded Synthesis</span>
                </div>
                <p className="leading-relaxed">{item.answer}</p>

                {item.missing_information && (
                  <div className="mt-2 p-2 bg-[#FFFBEB] rounded border border-[#FDE68A] text-[11px] text-[#92400E]">
                    <strong>Identified Knowledge Gap:</strong> {item.missing_information}
                  </div>
                )}

                {item.grounded_in_sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-[#E6E1D8] text-[11px]">
                    <span className="text-[#737E79] font-medium block mb-1">Cited Records:</span>
                    <ul className="space-y-0.5">
                      {item.grounded_in_sources.map((src, sIdx) => (
                        <li key={sIdx} className="font-mono text-[#1B3B2B] flex items-center gap-1">
                          <Bookmark className="w-3 h-3 text-[#1B3B2B]" />
                          <span>{src}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Input Field */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend(question);
        }}
        className="flex items-center gap-2 pt-2"
      >
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the evidence (e.g., Why is this result inconclusive?)..."
          disabled={loading}
          className="flex-1 px-3.5 py-2.5 bg-[#FFFFFF] border border-[#D9D3C7] rounded-md text-xs text-[#1A1E1C] placeholder-[#737E79] focus:outline-none focus:border-[#1B3B2B]"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="px-4 py-2.5 bg-[#1B3B2B] text-[#FBF9F5] hover:bg-[#132E20] rounded-md text-xs font-semibold flex items-center gap-1.5 disabled:opacity-40 transition-colors"
        >
          <span>Ask</span>
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>

      {error && (
        <div className="p-2.5 bg-[#FEF2F2] border border-[#FECACA] rounded text-xs text-[#991B1B] flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
