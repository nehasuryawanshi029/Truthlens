import React, { useState, useEffect } from 'react';
import {
  UploadCloud,
  FileImage,
  X,
  Play,
  RotateCcw,
  Sparkles,
  AlertCircle,
  HelpCircle,
  CheckCircle2,
  Clock,
  Layers,
  MapPin,
  Calendar,
  Link as LinkIcon
} from 'lucide-react';
import { Investigation, InvestigationMode, DemoCase } from '../types';
import { createInvestigation, fetchDemoCases } from '../services/api';

interface WorkspaceProps {
  initialDemo?: DemoCase | null;
  onInvestigationComplete: (investigation: Investigation) => void;
}

export const WorkspacePage: React.FC<WorkspaceProps> = ({
  initialDemo,
  onInvestigationComplete,
}) => {
  const [claim, setClaim] = useState('');
  const [location, setLocation] = useState('');
  const [date, setDate] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [mode, setMode] = useState<InvestigationMode>('deep');

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedSampleName, setSelectedSampleName] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [progressStep, setProgressStep] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [demos, setDemos] = useState<DemoCase[]>([]);

  useEffect(() => {
    fetchDemoCases()
      .then(setDemos)
      .catch(() => {});
  }, []);

  // Prepopulate if initialized from a demo case
  useEffect(() => {
    if (initialDemo) {
      setClaim(initialDemo.claim);
      setLocation(initialDemo.location);
      setDate(initialDemo.date);
      setSelectedSampleName(initialDemo.image_url.replace('/samples/', ''));
      setPreviewUrl(initialDemo.image_url);
      setSelectedFile(null);
    }
  }, [initialDemo]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setSelectedSampleName(null);
      setPreviewUrl(URL.createObjectURL(file));
      setErrorMessage(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      setSelectedSampleName(null);
      setPreviewUrl(URL.createObjectURL(file));
      setErrorMessage(null);
    }
  };

  const handleSelectDemoCase = (demo: DemoCase) => {
    setClaim(demo.claim);
    setLocation(demo.location);
    setDate(demo.date);
    setSelectedSampleName(demo.image_url.replace('/samples/', ''));
    setPreviewUrl(demo.image_url);
    setSelectedFile(null);
    setErrorMessage(null);
  };

  const handleClearImage = () => {
    setSelectedFile(null);
    setSelectedSampleName(null);
    setPreviewUrl(null);
  };

  const handleResetAll = () => {
    setClaim('');
    setLocation('');
    setDate('');
    setSourceUrl('');
    setSelectedFile(null);
    setSelectedSampleName(null);
    setPreviewUrl(null);
    setErrorMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!claim.trim()) {
      setErrorMessage('Please specify the claim to investigate.');
      return;
    }
    if (!selectedFile && !selectedSampleName) {
      setErrorMessage('Please upload an image or choose a demonstration case.');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    setProgressStep(1);

    const formData = new FormData();
    formData.append('claim', claim.trim());
    if (location) formData.append('location', location.trim());
    if (date) formData.append('date', date.trim());
    if (sourceUrl) formData.append('source_url', sourceUrl.trim());
    formData.append('mode', mode);

    if (selectedFile) {
      formData.append('image', selectedFile);
    } else if (selectedSampleName) {
      formData.append('sample_image_name', selectedSampleName);
    }

    // Step simulation for transparency while real backend executes
    const t1 = setTimeout(() => setProgressStep(2), 500);
    const t2 = setTimeout(() => setProgressStep(3), 1100);
    const t3 = setTimeout(() => setProgressStep(4), 1800);

    try {
      const result = await createInvestigation(formData);
      setProgressStep(5);
      setTimeout(() => {
        setIsSubmitting(false);
        onInvestigationComplete(result);
      }, 600);
    } catch (err: any) {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      setIsSubmitting(false);
      setProgressStep(0);
      setErrorMessage(err.message || 'An unexpected error occurred during investigation.');
    }
  };

  const progressStages = [
    { id: 1, label: 'Ingesting Image & Computing Perceptual Hash' },
    { id: 2, label: 'Extracting Camera EXIF & Inspecting GPS Provenance' },
    { id: 3, label: 'Deconstructing Claim Assertion, Event & Location' },
    { id: 4, label: 'Retrieving Grounded Passages from Archival Index' },
    { id: 5, label: 'Synthesizing Epistemic Verdict & Formatting Dossier' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8 pb-4 border-b border-[#E6E1D8] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-editorial text-3xl font-bold text-[#1A1E1C]">
            Investigation Workspace
          </h1>
          <p className="text-sm text-[#4A5450] mt-1">
            Upload any image and supply the circulating caption or claim to launch general multimodal verification.
          </p>
        </div>
        <button
          type="button"
          onClick={handleResetAll}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#FFFFFF] border border-[#D9D3C7] text-xs font-medium text-[#4A5450] hover:text-[#1A1E1C] hover:bg-[#F4F1EA] transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5 text-[#1B3B2B]" />
          <span>Reset Form</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Form Panel */}
        <div className="lg:col-span-7 space-y-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Image Ingestion Card */}
            <div className="editorial-card p-6 space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-[#F4F1EA]">
                <h3 className="font-editorial text-sm font-bold uppercase tracking-wider text-[#1A1E1C]">
                  1. Image Evidence Target
                </h3>
                {previewUrl && (
                  <button
                    type="button"
                    onClick={handleClearImage}
                    className="text-xs text-[#9B2C2C] hover:underline flex items-center gap-1"
                  >
                    <X className="w-3.5 h-3.5" />
                    <span>Clear Image</span>
                  </button>
                )}
              </div>

              {!previewUrl ? (
                <div
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={handleDrop}
                  className="border-2 border-dashed border-[#D9D3C7] hover:border-[#1B3B2B] rounded-lg p-8 text-center transition-colors bg-[#FBF9F5] flex flex-col items-center justify-center cursor-pointer relative"
                >
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handleFileChange}
                    className="absolute inset-0 opacity-0 cursor-pointer"
                  />
                  <div className="w-12 h-12 rounded-full bg-[#EAF2ED] text-[#1B3B2B] flex items-center justify-center mb-3">
                    <UploadCloud className="w-6 h-6" />
                  </div>
                  <p className="text-xs font-semibold text-[#1A1E1C] mb-1">
                    Drag and drop image here, or browse files
                  </p>
                  <p className="text-[11px] text-[#737E79]">
                    Supports JPG, PNG, WEBP (Up to 15MB)
                  </p>
                </div>
              ) : (
                <div className="relative aspect-video bg-[#1C211F] rounded-md overflow-hidden border border-[#D9D3C7]">
                  <img
                    src={previewUrl}
                    alt="Preview Target"
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute bottom-2 left-2 bg-[#1A1E1C]/80 text-[#FBF9F5] text-[10px] px-2 py-0.5 rounded font-mono">
                    {selectedFile ? selectedFile.name : selectedSampleName}
                  </div>
                </div>
              )}

              {/* Sample Picker quick chips */}
              <div className="pt-2">
                <span className="text-[11px] font-semibold text-[#737E79] block mb-2">
                  Or load a benchmark demonstration case:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {demos.map((d) => (
                    <button
                      key={d.id}
                      type="button"
                      onClick={() => handleSelectDemoCase(d)}
                      className={`text-[11px] px-2.5 py-1 rounded border transition-colors ${
                        selectedSampleName === d.image_url.replace('/samples/', '')
                          ? 'bg-[#1B3B2B] text-[#FBF9F5] border-[#1B3B2B]'
                          : 'bg-[#F4F1EA] hover:bg-[#EAE5DA] text-[#2C332F] border-[#D9D3C7]'
                      }`}
                    >
                      {d.title}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Claim Assertion Card */}
            <div className="editorial-card p-6 space-y-4">
              <div className="pb-2 border-b border-[#F4F1EA]">
                <h3 className="font-editorial text-sm font-bold uppercase tracking-wider text-[#1A1E1C]">
                  2. Circulating Claim or Caption
                </h3>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#1A1E1C] mb-1">
                  Full Claim Statement *
                </label>
                <textarea
                  value={claim}
                  onChange={(e) => setClaim(e.target.value)}
                  placeholder="Enter the caption or assertion being investigated (e.g., 'This photograph shows flooding in Pune today.')"
                  rows={3}
                  className="w-full px-3.5 py-2.5 bg-[#FFFFFF] border border-[#D9D3C7] rounded-md text-xs text-[#1A1E1C] placeholder-[#737E79] focus:outline-none focus:border-[#1B3B2B]"
                  required
                />
              </div>

              {/* Optional Supplementary Meta */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
                <div>
                  <label className="text-[11px] font-medium text-[#4A5450] flex items-center gap-1 mb-1">
                    <MapPin className="w-3 h-3 text-[#1B3B2B]" />
                    <span>Location (Optional)</span>
                  </label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. Pune, India"
                    className="w-full px-3 py-2 bg-[#FFFFFF] border border-[#D9D3C7] rounded-md text-xs focus:outline-none focus:border-[#1B3B2B]"
                  />
                </div>

                <div>
                  <label className="text-[11px] font-medium text-[#4A5450] flex items-center gap-1 mb-1">
                    <Calendar className="w-3 h-3 text-[#1B3B2B]" />
                    <span>Time / Date (Optional)</span>
                  </label>
                  <input
                    type="text"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    placeholder="e.g. Today, July 2024"
                    className="w-full px-3 py-2 bg-[#FFFFFF] border border-[#D9D3C7] rounded-md text-xs focus:outline-none focus:border-[#1B3B2B]"
                  />
                </div>

                <div>
                  <label className="text-[11px] font-medium text-[#4A5450] flex items-center gap-1 mb-1">
                    <LinkIcon className="w-3 h-3 text-[#1B3B2B]" />
                    <span>Source URL (Optional)</span>
                  </label>
                  <input
                    type="url"
                    value={sourceUrl}
                    onChange={(e) => setSourceUrl(e.target.value)}
                    placeholder="https://..."
                    className="w-full px-3 py-2 bg-[#FFFFFF] border border-[#D9D3C7] rounded-md text-xs focus:outline-none focus:border-[#1B3B2B]"
                  />
                </div>
              </div>
            </div>

            {/* Investigation Mode Selector */}
            <div className="editorial-card p-6 space-y-4">
              <div className="pb-2 border-b border-[#F4F1EA]">
                <h3 className="font-editorial text-sm font-bold uppercase tracking-wider text-[#1A1E1C]">
                  3. Select Investigation Mode
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  {
                    id: 'quick',
                    title: 'Quick Scan',
                    desc: 'Fast perceptual hash lookup against known archival duplicates.'
                  },
                  {
                    id: 'deep',
                    title: 'Deep Investigation',
                    desc: 'Full hybrid semantic retrieval, passage scoring, and epistemic synthesis.'
                  },
                  {
                    id: 'research',
                    title: 'Research Mode',
                    desc: 'Exposes lower relevance thresholds, detailed forensic signals, and metrics.'
                  }
                ].map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => setMode(m.id as InvestigationMode)}
                    className={`p-3.5 rounded-md border text-left transition-all ${
                      mode === m.id
                        ? 'border-[#1B3B2B] bg-[#EAF2ED]/50 shadow-xs'
                        : 'border-[#D9D3C7] bg-[#FFFFFF] hover:border-[#A4B5AC]'
                    }`}
                  >
                    <span className="font-editorial font-bold text-xs text-[#1A1E1C] block mb-1">
                      {m.title}
                    </span>
                    <span className="text-[11px] text-[#5C6661] block leading-snug">
                      {m.desc}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Submission Action */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-[#1B3B2B] hover:bg-[#132E20] text-[#FBF9F5] py-3.5 px-6 rounded-md font-semibold text-sm tracking-wide shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Executing Investigation Pipeline...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Start Investigation</span>
                </>
              )}
            </button>

            {errorMessage && (
              <div className="p-3.5 bg-[#FEF2F2] border border-[#FECACA] rounded-md text-xs text-[#991B1B] flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}
          </form>
        </div>

        {/* Right Live Progress & Context Panel */}
        <div className="lg:col-span-5 space-y-6">
          <div className="editorial-card p-6 space-y-5">
            <div className="pb-3 border-b border-[#F4F1EA] flex items-center justify-between">
              <h3 className="font-editorial text-sm font-bold uppercase tracking-wider text-[#1A1E1C]">
                Pipeline Execution Status
              </h3>
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#EAE5DA] text-[#4A5450]">
                {isSubmitting ? 'Running' : 'Standby'}
              </span>
            </div>

            <div className="space-y-4">
              {progressStages.map((stage) => {
                const isCompleted = progressStep > stage.id;
                const isCurrent = progressStep === stage.id;

                return (
                  <div key={stage.id} className="flex items-start gap-3">
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-xs shrink-0 mt-0.5 font-mono ${
                        isCompleted
                          ? 'bg-[#1B7A43] text-white'
                          : isCurrent
                          ? 'bg-[#1B3B2B] text-white animate-pulse'
                          : 'bg-[#EAE5DA] text-[#737E79]'
                      }`}
                    >
                      {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : stage.id}
                    </div>
                    <div className="text-xs">
                      <span
                        className={`font-semibold block ${
                          isCurrent
                            ? 'text-[#1B3B2B]'
                            : isCompleted
                            ? 'text-[#1A1E1C]'
                            : 'text-[#737E79]'
                        }`}
                      >
                        {stage.label}
                      </span>
                      <span className="text-[11px] text-[#737E79]">
                        {isCompleted
                          ? 'Complete'
                          : isCurrent
                          ? 'Processing...'
                          : 'Pending previous stage'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Transparent Principles Card */}
          <div className="editorial-card p-6 bg-[#FBF9F5] space-y-3">
            <h4 className="font-editorial text-sm font-bold text-[#1A1E1C]">
              Investigative Protocol
            </h4>
            <p className="text-xs text-[#5C6661] leading-relaxed">
              TRUTHLENS processes uploaded media entirely on CPU with zero data leakage.
              When claims lack indexed corroboration, the system refuses to speculate, producing an explicit <em>Insufficient Evidence</em> report.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
