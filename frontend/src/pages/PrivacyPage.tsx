import React, { useState } from 'react';
import {
  Lock,
  Shield,
  Trash2,
  Download,
  AlertCircle,
  CheckCircle2,
  EyeOff,
  Server
} from 'lucide-react';
import { clearAllInvestigations } from '../services/api';

export const PrivacyPage: React.FC = () => {
  const [cleared, setCleared] = useState(false);

  const handleClearHistory = async () => {
    if (!window.confirm('Delete all stored investigation dossiers and uploaded images?')) return;
    try {
      await clearAllInvestigations();
      setCleared(true);
      setTimeout(() => setCleared(false), 3000);
    } catch (err) {
      alert('Failed to clear records.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="pb-4 border-b border-[#E6E1D8]">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-[#EAF2ED] text-[#1B3B2B] text-xs font-semibold uppercase tracking-wider mb-2 border border-[#C5DDD0]">
          <Lock className="w-3.5 h-3.5" />
          <span>Privacy & Data Sovereignty</span>
        </div>
        <h1 className="font-editorial text-3xl font-bold text-[#1A1E1C]">
          Privacy Controls & Ethical Architecture
        </h1>
        <p className="text-sm text-[#4A5450] mt-1">
          TRUTHLENS is engineered with privacy-by-design principles, avoiding cloud telemetry and protecting user images.
        </p>
      </div>

      <div className="space-y-6">
        {/* Retention Policy */}
        <div className="editorial-card p-6 space-y-3 bg-[#FFFFFF]">
          <h3 className="font-editorial text-base font-bold text-[#1A1E1C] flex items-center gap-2">
            <Server className="w-4 h-4 text-[#1B3B2B]" />
            <span>Local-First Data Storage</span>
          </h3>
          <p className="text-xs text-[#4A5450] leading-relaxed">
            All uploaded images and forensic records remain inside your local project environment (stored in <code>data/uploads/</code> and <code>data/truthlens.db</code>).
            Images are never uploaded to public AI training datasets, commercial vector clouds, or third-party tracking services.
          </p>
        </div>

        {/* GPS and Metadata Redaction */}
        <div className="editorial-card p-6 space-y-3 bg-[#FFFFFF]">
          <h3 className="font-editorial text-base font-bold text-[#1A1E1C] flex items-center gap-2">
            <EyeOff className="w-4 h-4 text-[#1B3B2B]" />
            <span>EXIF & GPS Sanitization Safeguards</span>
          </h3>
          <p className="text-xs text-[#4A5450] leading-relaxed">
            When extracting geolocation tags from uploaded imagery, precise coordinate pairs are automatically masked and generalized to avoid publishing private user residential locations.
            The dossier view offers an on-demand <strong>Sanitized Copy Downloader</strong> that outputs images with all device and location markers permanently stripped.
          </p>
        </div>

        {/* External Service Transparency */}
        <div className="editorial-card p-6 space-y-3 bg-[#FFFFFF]">
          <h3 className="font-editorial text-base font-bold text-[#1A1E1C] flex items-center gap-2">
            <Shield className="w-4 h-4 text-[#1B3B2B]" />
            <span>Zero Unannounced Outbound Requests</span>
          </h3>
          <div className="text-xs text-[#4A5450] space-y-2">
            <p>
              By default, TRUTHLENS executes completely offline against the local benchmark index and CPU-based perceptual hashes.
            </p>
            <div className="p-3 bg-[#FBF9F5] rounded border border-[#E6E1D8] space-y-1 font-mono text-[11px]">
              <div>ENABLE_EXTERNAL_WEB_SEARCH=false (No external search provider pinged)</div>
              <div>ENABLE_EXTERNAL_LLM=false (No proprietary LLM API receives your image)</div>
            </div>
          </div>
        </div>

        {/* Action: Clear History */}
        <div className="p-6 bg-[#FEF2F2] border border-[#FECACA] rounded-md space-y-3">
          <div className="flex items-center gap-2 text-[#991B1B]">
            <Trash2 className="w-5 h-5" />
            <h3 className="font-bold text-sm">Purge All Local Investigation Records</h3>
          </div>
          <p className="text-xs text-[#7F1D1D] leading-relaxed">
            Permanently delete all saved dossiers, extracted forensic metadata, and uploaded image files from your local storage.
          </p>
          <button
            onClick={handleClearHistory}
            className="px-4 py-2 bg-[#991B1B] hover:bg-[#7F1D1D] text-white rounded text-xs font-semibold transition-colors shadow-xs"
          >
            {cleared ? 'History Cleared' : 'Purge All Dossiers Now'}
          </button>
        </div>
      </div>
    </div>
  );
};
