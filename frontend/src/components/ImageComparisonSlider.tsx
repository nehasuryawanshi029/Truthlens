import React, { useState } from 'react';
import { Columns, Eye, ZoomIn, ZoomOut, AlertCircle, RefreshCw } from 'lucide-react';

interface ComparisonProps {
  originalImageUrl: string;
  originalLabel: string;
  matchedImageUrl?: string | null;
  matchedTitle?: string | null;
  similarityScore?: number | null;
  provenanceText?: string | null;
}

export const ImageComparisonSlider: React.FC<ComparisonProps> = ({
  originalImageUrl,
  originalLabel,
  matchedImageUrl,
  matchedTitle,
  similarityScore,
  provenanceText,
}) => {
  const [viewMode, setViewMode] = useState<'side-by-side' | 'overlay'>('side-by-side');
  const [sliderPos, setSliderPos] = useState<number>(50);
  const [zoomLevel, setZoomLevel] = useState<number>(1);

  if (!matchedImageUrl) {
    return (
      <div className="editorial-card p-6 text-center text-xs text-[#5C6661]">
        <Eye className="w-6 h-6 text-[#737E79] mx-auto mb-2" />
        <p className="font-semibold text-sm text-[#1A1E1C]">No Identical Archival Match in Reference Corpus</p>
        <p className="mt-1 text-[#737E79] max-w-md mx-auto">
          The uploaded image did not trigger a high visual similarity candidate in our local indexed benchmark images.
        </p>
      </div>
    );
  }

  return (
    <div className="editorial-card p-6 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#F4F1EA]">
        <div>
          <h3 className="font-editorial text-base font-bold uppercase tracking-wider text-[#1A1E1C]">
            Visual Forensic Comparison View
          </h3>
          <p className="text-xs text-[#737E79]">
            Examine uploaded media against retrieved reference archival match.
          </p>
        </div>

        {/* View toggles & zoom */}
        <div className="flex items-center gap-2">
          <div className="bg-[#F4F1EA] p-1 rounded-md flex items-center gap-1 text-xs">
            <button
              onClick={() => setViewMode('side-by-side')}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                viewMode === 'side-by-side' ? 'bg-[#FFFFFF] text-[#1A1E1C] shadow-xs' : 'text-[#4A5450]'
              }`}
            >
              Side by Side
            </button>
            <button
              onClick={() => setViewMode('overlay')}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                viewMode === 'overlay' ? 'bg-[#FFFFFF] text-[#1A1E1C] shadow-xs' : 'text-[#4A5450]'
              }`}
            >
              Split Slider
            </button>
          </div>

          <div className="flex items-center gap-1 bg-[#F4F1EA] p-1 rounded-md text-[#4A5450]">
            <button
              onClick={() => setZoomLevel(Math.max(1, zoomLevel - 0.25))}
              className="p-1 hover:text-[#1A1E1C] disabled:opacity-40"
              disabled={zoomLevel <= 1}
              title="Zoom out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-[10px] font-mono px-1">{zoomLevel}x</span>
            <button
              onClick={() => setZoomLevel(Math.min(2.5, zoomLevel + 0.25))}
              className="p-1 hover:text-[#1A1E1C] disabled:opacity-40"
              disabled={zoomLevel >= 2.5}
              title="Zoom in"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Comparison Viewport */}
      {viewMode === 'side-by-side' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Uploaded */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-[#1A1E1C]">Investigated Upload</span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-[#EAE5DA] text-[#4A5450]">
                User Target
              </span>
            </div>
            <div className="aspect-video bg-[#1C211F] rounded-md overflow-hidden relative flex items-center justify-center border border-[#D9D3C7]">
              <img
                src={originalImageUrl}
                alt="Investigated Target"
                style={{ transform: `scale(${zoomLevel})` }}
                className="w-full h-full object-contain transition-transform duration-200"
              />
            </div>
          </div>

          {/* Reference Match */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-[#1A1E1C] truncate">{matchedTitle || 'Archival Match'}</span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-[#DCFCE7] text-[#166534]">
                {similarityScore ? `${Math.round(similarityScore * 100)}% Match` : 'Candidate'}
              </span>
            </div>
            <div className="aspect-video bg-[#1C211F] rounded-md overflow-hidden relative flex items-center justify-center border border-[#D9D3C7]">
              <img
                src={matchedImageUrl}
                alt="Archival Reference"
                style={{ transform: `scale(${zoomLevel})` }}
                className="w-full h-full object-contain transition-transform duration-200"
              />
            </div>
          </div>
        </div>
      ) : (
        /* Split Slider View */
        <div className="space-y-2">
          <div className="relative aspect-video bg-[#1C211F] rounded-md overflow-hidden border border-[#D9D3C7] select-none">
            {/* Background image (Reference) */}
            <img
              src={matchedImageUrl}
              alt="Reference"
              style={{ transform: `scale(${zoomLevel})` }}
              className="absolute inset-0 w-full h-full object-contain"
            />
            {/* Foreground clip (Original) */}
            <div
              className="absolute inset-0 overflow-hidden"
              style={{ width: `${sliderPos}%` }}
            >
              <img
                src={originalImageUrl}
                alt="Original"
                style={{ transform: `scale(${zoomLevel})`, width: '100%', height: '100%' }}
                className="w-full h-full object-contain max-w-none"
              />
            </div>
            {/* Split Divider */}
            <div
              className="absolute top-0 bottom-0 w-1 bg-[#FFFFFF] shadow-lg cursor-ew-resize flex items-center justify-center"
              style={{ left: `${sliderPos}%` }}
            >
              <div className="w-5 h-5 rounded-full bg-[#1B3B2B] text-white flex items-center justify-center text-[10px] font-bold shadow-md">
                ↔
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2 text-xs">
            <span className="text-[#737E79]">Slide to compare differences:</span>
            <input
              type="range"
              min="0"
              max="100"
              value={sliderPos}
              onChange={(e) => setSliderPos(Number(e.target.value))}
              className="flex-1 accent-[#1B3B2B]"
            />
            <span className="font-mono text-[11px] text-[#1A1E1C]">{sliderPos}%</span>
          </div>
        </div>
      )}

      {/* Provenance Explanatory Callout */}
      {provenanceText && (
        <div className="p-3.5 bg-[#FBF9F5] rounded border border-[#E6E1D8] text-xs text-[#2D3330] leading-relaxed">
          <span className="font-bold text-[#1B3B2B] block mb-1">Archival Provenance Note:</span>
          {provenanceText}
        </div>
      )}
    </div>
  );
};
