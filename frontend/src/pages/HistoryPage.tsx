import React, { useState, useEffect } from 'react';
import {
  History,
  Search,
  Filter,
  Trash2,
  ExternalLink,
  Calendar,
  AlertCircle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ChevronRight,
  Database
} from 'lucide-react';
import { InvestigationSummary, AssessmentStatus } from '../types';
import { fetchInvestigations, deleteInvestigation, clearAllInvestigations } from '../services/api';

interface HistoryPageProps {
  onSelectInvestigation: (id: string) => void;
  onNewInvestigation: () => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({
  onSelectInvestigation,
  onNewInvestigation
}) => {
  const [items, setItems] = useState<InvestigationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchInvestigations({
        status: statusFilter || undefined,
        search: searchTerm || undefined
      });
      setItems(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Delete this investigation dossier permanently?')) return;
    try {
      await deleteInvestigation(id);
      setItems((prev) => prev.filter((i) => i.id !== id));
    } catch (err) {
      alert('Failed to delete dossier.');
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Are you sure you want to delete all investigation dossiers? This action cannot be undone.')) return;
    try {
      await clearAllInvestigations();
      setItems([]);
    } catch (err) {
      alert('Failed to clear history.');
    }
  };

  const getStatusBadge = (status?: string, verdictCategory?: string) => {
    const raw = (verdictCategory || status || 'insufficient').toLowerCase();
    if (raw.includes('contradict') || raw.includes('wrong')) {
      return (
        <span className="editorial-badge status-contradicted flex items-center gap-1">
          <XCircle className="w-3 h-3" />
          <span>{verdictCategory || 'Contradicted'}</span>
        </span>
      );
    }
    if (raw.includes('support')) {
      return (
        <span className="editorial-badge status-supported flex items-center gap-1">
          <CheckCircle2 className="w-3 h-3" />
          <span>{verdictCategory || 'Supported'}</span>
        </span>
      );
    }
    if (raw.includes('insufficient')) {
      return (
        <span className="editorial-badge status-insufficient flex items-center gap-1">
          <HelpCircle className="w-3 h-3" />
          <span>{verdictCategory || 'Insufficient Evidence'}</span>
        </span>
      );
    }
    return (
      <span className="editorial-badge status-conflicting flex items-center gap-1">
        <AlertCircle className="w-3 h-3" />
        <span>{verdictCategory || status || 'Conflicting'}</span>
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E6E1D8]">
        <div>
          <h1 className="font-editorial text-3xl font-bold text-[#1A1E1C]">
            Investigation History & Dossiers
          </h1>
          <p className="text-sm text-[#4A5450] mt-1">
            Persisted forensic records stored in local SQLite database.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {items.length > 0 && (
            <button
              onClick={handleClearAll}
              className="text-xs font-medium text-[#9B2C2C] hover:underline flex items-center gap-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear History</span>
            </button>
          )}

          <button
            onClick={onNewInvestigation}
            className="px-4 py-2 bg-[#1B3B2B] text-[#FBF9F5] hover:bg-[#132E20] rounded-md text-xs font-semibold shadow-xs"
          >
            New Investigation
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <form onSubmit={handleSearchSubmit} className="flex-1 w-full relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-[#737E79]" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search investigations by claim keywords..."
            className="w-full pl-9 pr-4 py-2 bg-[#FFFFFF] border border-[#D9D3C7] rounded-md text-xs text-[#1A1E1C] focus:outline-none focus:border-[#1B3B2B]"
          />
        </form>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-[#737E79]" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-[#FFFFFF] border border-[#D9D3C7] rounded-md text-xs text-[#1A1E1C] focus:outline-none focus:border-[#1B3B2B]"
          >
            <option value="">All Statuses</option>
            <option value="contradicted">Contradicted</option>
            <option value="supported">Supported</option>
            <option value="insufficient_evidence">Insufficient Evidence</option>
            <option value="conflicting">Conflicting</option>
          </select>
        </div>
      </div>

      {/* Investigation Records List */}
      {loading ? (
        <div className="p-12 text-center text-xs text-[#737E79]">
          <div className="w-5 h-5 border-2 border-[#1B3B2B]/30 border-t-[#1B3B2B] rounded-full animate-spin mx-auto mb-2" />
          <span>Loading dossier archives...</span>
        </div>
      ) : items.length === 0 ? (
        <div className="editorial-card p-12 text-center text-xs text-[#5C6661] space-y-3">
          <History className="w-8 h-8 text-[#737E79] mx-auto" />
          <p className="font-bold text-sm text-[#1A1E1C]">No Investigation Records Found</p>
          <p className="text-[#737E79] max-w-sm mx-auto">
            You haven't conducted any investigations matching this filter yet. Start an investigation from the workspace or try one of the demonstration cases.
          </p>
          <button
            onClick={onNewInvestigation}
            className="mt-2 inline-flex items-center gap-1.5 px-4 py-2 bg-[#1B3B2B] text-[#FBF9F5] rounded-md text-xs font-semibold"
          >
            Launch Investigation
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {items.map((item) => (
            <div
              key={item.id}
              onClick={() => onSelectInvestigation(item.id)}
              className="editorial-card p-4 hover:border-[#1B3B2B] hover:shadow-xs transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="flex items-start gap-4">
                <div className="w-20 h-14 bg-[#1C211F] rounded overflow-hidden shrink-0 border border-[#D9D3C7]">
                  <img
                    src={item.image_url}
                    alt="Thumbnail"
                    className="w-full h-full object-cover"
                  />
                </div>

                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {getStatusBadge(item.assessment_status, item.verdict_category)}
                    <span className="text-[10px] text-[#737E79] font-mono">
                      ID: {item.id.slice(0, 8)}
                    </span>
                  </div>

                  <h3 className="font-editorial text-sm font-bold text-[#1A1E1C] line-clamp-1">
                    "{item.original_claim}"
                  </h3>

                  <div className="flex items-center gap-3 text-[11px] text-[#737E79]">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(item.created_at).toLocaleDateString()}</span>
                    </span>
                    <span>• {item.evidence_count} evidence records retrieved</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-center">
                <button
                  onClick={(e) => handleDelete(item.id, e)}
                  className="p-1.5 text-[#737E79] hover:text-[#9B2C2C] hover:bg-[#FEE2E2] rounded transition-colors"
                  title="Delete record"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                <ChevronRight className="w-4 h-4 text-[#737E79]" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
