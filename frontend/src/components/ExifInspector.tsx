import React, { useState } from 'react';
import { Camera, MapPin, Cpu, ShieldCheck, Download, AlertTriangle, Info } from 'lucide-react';
import { ImageAnalysis } from '../types';
import { getSanitizedImageUrl } from '../services/api';

interface ExifInspectorProps {
  analysis: ImageAnalysis;
  investigationId: string;
}

export const ExifInspector: React.FC<ExifInspectorProps> = ({ analysis, investigationId }) => {
  const [downloadingClean, setDownloadingClean] = useState(false);

  const handleDownloadSanitized = () => {
    setDownloadingClean(true);
    window.open(getSanitizedImageUrl(investigationId), '_blank');
    setTimeout(() => setDownloadingClean(false), 1500);
  };

  const exif = analysis.exif_data || {};
  const gps = analysis.gps_data || {};
  const signals = analysis.authenticity_signals || {};

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="editorial-card p-3.5 bg-[#FFFFFF]">
          <span className="text-[10px] uppercase tracking-wider text-[#737E79] block mb-0.5">Format</span>
          <span className="font-mono text-sm font-bold text-[#1A1E1C]">{analysis.file_type}</span>
        </div>
        <div className="editorial-card p-3.5 bg-[#FFFFFF]">
          <span className="text-[10px] uppercase tracking-wider text-[#737E79] block mb-0.5">Dimensions</span>
          <span className="font-mono text-sm font-bold text-[#1A1E1C]">{analysis.dimensions}</span>
        </div>
        <div className="editorial-card p-3.5 bg-[#FFFFFF]">
          <span className="text-[10px] uppercase tracking-wider text-[#737E79] block mb-0.5">File Size</span>
          <span className="font-mono text-sm font-bold text-[#1A1E1C]">
            {(analysis.file_size_bytes / (1024 * 1024)).toFixed(2)} MB
          </span>
        </div>
        <div className="editorial-card p-3.5 bg-[#FFFFFF]">
          <span className="text-[10px] uppercase tracking-wider text-[#737E79] block mb-0.5">Color Space</span>
          <span className="font-mono text-sm font-bold text-[#1A1E1C]">{analysis.color_mode}</span>
        </div>
      </div>

      {/* Camera & Hardware Forensics */}
      <div className="editorial-card p-5">
        <div className="flex items-center gap-2 mb-4 pb-2 border-b border-[#F4F1EA]">
          <Camera className="w-4 h-4 text-[#1B3B2B]" />
          <h4 className="font-editorial text-sm font-bold uppercase tracking-wider text-[#1A1E1C]">
            Embedded Camera & Capture EXIF
          </h4>
        </div>

        {Object.keys(exif).length > 0 ? (
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3 text-xs">
            <div>
              <dt className="text-[#737E79]">Camera Device</dt>
              <dd className="font-mono font-medium text-[#1A1E1C] mt-0.5">
                {exif.Make || exif.Model ? `${exif.Make || ''} ${exif.Model || ''}` : 'Not Specified'}
              </dd>
            </div>
            <div>
              <dt className="text-[#737E79]">Original Timestamp</dt>
              <dd className="font-mono font-medium text-[#1A1E1C] mt-0.5">
                {exif.DateTimeOriginal || exif.DateTime || 'No timestamp tag'}
              </dd>
            </div>
            {exif.LensModel && (
              <div>
                <dt className="text-[#737E79]">Lens Model</dt>
                <dd className="font-mono font-medium text-[#1A1E1C] mt-0.5">{exif.LensModel}</dd>
              </div>
            )}
            {exif.Software && (
              <div>
                <dt className="text-[#737E79]">Software / Post-Processing</dt>
                <dd className="font-mono font-medium text-[#1A1E1C] mt-0.5">{exif.Software}</dd>
              </div>
            )}
          </dl>
        ) : (
          <div className="p-3 bg-[#FBF9F5] rounded text-xs text-[#5C6661] border border-[#E6E1D8]">
            No camera hardware EXIF tags detected. This is typical for images shared across social media platforms (WhatsApp, X, Facebook, Reddit), which scrub metadata on upload to protect user privacy.
          </div>
        )}

        <div className="mt-4 pt-3 border-t border-[#F4F1EA] flex items-start gap-2 text-[11px] text-[#737E79]">
          <Info className="w-3.5 h-3.5 text-[#1B3B2B] shrink-0 mt-0.5" />
          <span>
            <strong>Epistemic Note:</strong> EXIF metadata is recorded by device clocks and can be altered or stripped. Its presence does not alone prove capture authenticity.
          </span>
        </div>
      </div>

      {/* Geolocation Forensics */}
      <div className="editorial-card p-5">
        <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[#F4F1EA]">
          <MapPin className="w-4 h-4 text-[#1B3B2B]" />
          <h4 className="font-editorial text-sm font-bold uppercase tracking-wider text-[#1A1E1C]">
            Geolocation & GPS Metadata
          </h4>
        </div>

        {gps.has_gps ? (
          <div className="space-y-3">
            <div className="p-3 bg-[#EAF2ED] rounded border border-[#C5DDD0] text-xs text-[#1B3B2B]">
              <span className="font-semibold block mb-1">GPS Coordinates Detected</span>
              <span className="font-mono">{gps.redacted_display}</span>
              <p className="mt-1.5 text-[11px] text-[#3E5247]">
                {gps.note}
              </p>
            </div>
          </div>
        ) : (
          <div className="p-3 bg-[#FBF9F5] rounded border border-[#E6E1D8] text-xs text-[#5C6661]">
            No embedded GPS coordinates found in image header.
          </div>
        )}
      </div>

      {/* Authenticity Signals & Manipulation Check */}
      <div className="editorial-card p-5">
        <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[#F4F1EA]">
          <Cpu className="w-4 h-4 text-[#1B3B2B]" />
          <h4 className="font-editorial text-sm font-bold uppercase tracking-wider text-[#1A1E1C]">
            Authenticity & Synthetic Signals
          </h4>
        </div>

        <div className="space-y-3 text-xs">
          <div className="flex items-center justify-between p-2.5 bg-[#FBF9F5] rounded border border-[#E6E1D8]">
            <span className="text-[#4A5450]">Generative / Diffusion Artifacts:</span>
            <span className="font-semibold text-[#1A1E1C]">{signals.synthetic_indicator || 'Low / Inconclusive'}</span>
          </div>

          <div className="flex items-center justify-between p-2.5 bg-[#FBF9F5] rounded border border-[#E6E1D8]">
            <span className="text-[#4A5450]">Software Modification Markers:</span>
            <span className="font-semibold text-[#1A1E1C]">
              {signals.has_editing_signatures ? (
                <span className="text-[#9B2C2C]">Detected ({signals.editing_software_detected || 'Composite Discrepancy'})</span>
              ) : (
                <span className="text-[#1B7A43]">None Detected</span>
              )}
            </span>
          </div>

          {signals.ela_score !== undefined && (
            <div className="flex items-center justify-between p-2.5 bg-[#FBF9F5] rounded border border-[#E6E1D8]">
              <span className="text-[#4A5450]">Error Level Analysis (ELA) Discrepancy:</span>
              <span className="font-mono font-semibold text-[#1A1E1C]">
                {signals.ela_score} {signals.ela_score > 28 ? '(Elevated variance: potential splicing)' : '(Normal variance)'}
              </span>
            </div>
          )}

          {signals.notes && signals.notes.length > 0 && (
            <div className="mt-2 space-y-1">
              {signals.notes.map((note: string, idx: number) => (
                <div key={idx} className="flex items-start gap-1.5 text-[11px] text-[#4A5450]">
                  <span className="text-[#1B3B2B]">•</span>
                  <span>{note}</span>
                </div>
              ))}
            </div>
          )}

          {signals.limitations_notice && (
            <div className="mt-3 p-2.5 bg-[#FFFBEB] rounded border border-[#FDE68A] text-[11px] text-[#92400E]">
              <strong>Authenticity Limitation Notice:</strong> {signals.limitations_notice}
            </div>
          )}
        </div>
      </div>

      {/* Privacy Redaction Tool */}
      <div className="p-4 bg-[#F4F1EA] rounded-md border border-[#D9D3C7] flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h5 className="text-xs font-bold text-[#1A1E1C] flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-[#1B3B2B]" />
            Privacy Safeguard: Clean Metadata Copy
          </h5>
          <p className="text-[11px] text-[#5C6661] mt-0.5">
            Export a copy of this image with all device, GPS, and timestamp tags permanently scrubbed.
          </p>
        </div>
        <button
          onClick={handleDownloadSanitized}
          disabled={downloadingClean}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-[#1B3B2B] text-[#FBF9F5] hover:bg-[#132E20] text-xs font-medium shrink-0 transition-colors"
        >
          <Download className="w-3.5 h-3.5" />
          <span>{downloadingClean ? 'Preparing Clean File...' : 'Download Sanitized Image'}</span>
        </button>
      </div>
    </div>
  );
};
