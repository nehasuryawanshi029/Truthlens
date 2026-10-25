import React, { useState, useRef, useEffect } from 'react';
import {
  UploadCloud,
  FileImage,
  Sparkles,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  RefreshCw,
  X,
  Info,
  Cpu,
  Layers,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import { DetectionResult, ModelInfo } from '../types';
import { detectImage, fetchModelInfo } from '../services/api';

const SAMPLE_BENCHMARKS = [
  {
    title: 'Authentic Photo: Central Mumbai Flood',
    url: '/samples/mumbai_flooding_2019.jpg',
    expected: 'Likely Real Photograph',
    type: 'real'
  },
  {
    title: 'Authentic Photo: Sangli Mandir',
    url: '/samples/sangli_ganapati_mandir.jpg',
    expected: 'Likely Real Photograph',
    type: 'real'
  },
  {
    title: 'AI-Generated: Mars Astronaut Portrait',
    url: '/samples/ai_astronaut_mars.jpg',
    expected: 'AI Generative Benchmark',
    type: 'ai'
  },
  {
    title: 'Authentic Photo: Earthquake Relief',
    url: '/samples/turkey_earthquake_relief.jpg',
    expected: 'Likely Real Photograph',
    type: 'real'
  }
];

export const DetectorPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [isDragging, setIsDragging] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchModelInfo()
      .then(setModelInfo)
      .catch((err) => {
        console.warn('Model info could not be fetched:', err);
      });
  }, []);

  const handleFileSelect = (file: File) => {
    // Clear previous results immediately upon new selection
    setResult(null);
    setErrorMessage(null);

    // Basic format check
    const ext = file.name.split('.').pop()?.toLowerCase();
    const validExts = ['jpg', 'jpeg', 'png', 'webp'];
    if (ext && !validExts.includes(ext)) {
      setErrorMessage(`Unsupported format .${ext}. Please upload a JPEG, PNG, or WEBP image.`);
      setSelectedFile(null);
      setPreviewUrl(null);
      setFileName('');
      return;
    }

    // Size check (15MB)
    if (file.size > 15 * 1024 * 1024) {
      setErrorMessage(`File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds the 15MB limit.`);
      setSelectedFile(null);
      setPreviewUrl(null);
      setFileName('');
      return;
    }

    setSelectedFile(file);
    setFileName(file.name);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleSelectSample = async (sample: typeof SAMPLE_BENCHMARKS[0]) => {
    try {
      setResult(null);
      setErrorMessage(null);
      setIsLoading(true);

      const resp = await fetch(sample.url);
      if (!resp.ok) throw new Error('Could not load sample benchmark');
      const blob = await resp.blob();
      const fname = sample.url.split('/').pop() || 'sample.jpg';
      const file = new File([blob], fname, { type: blob.type || 'image/jpeg' });

      setSelectedFile(file);
      setFileName(fname);
      setPreviewUrl(sample.url);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load sample image');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setErrorMessage('Please select or upload an image first.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setResult(null); // Never retain old result during an in-flight request

    try {
      const data = await detectImage(selectedFile);
      setResult(data);
    } catch (err: any) {
      setResult(null); // Never display old result on error
      setErrorMessage(err.message || 'An error occurred while connecting to the image detector backend.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setFileName('');
    setResult(null);
    setErrorMessage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
      {/* Header Banner */}
      <div className="text-center max-w-3xl mx-auto mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#EAF2ED] text-[#1B3B2B] text-xs font-semibold tracking-wider uppercase border border-[#C5DDD0] mb-4">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Deep Forensic Vision System</span>
        </div>
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-editorial font-bold text-[#1A1E1C] tracking-tight">
          TRUTHLENS
        </h1>
        <p className="text-lg sm:text-xl font-medium text-[#1B3B2B] mt-1 tracking-wide uppercase">
          AI Image Authenticity Detector
        </p>
        <p className="text-sm sm:text-base text-[#4A5450] mt-3 max-w-2xl mx-auto leading-relaxed">
          Evaluate whether an uploaded image shows high-frequency generative artifacts characteristic of synthetic AI diffusion, or organic optical sensor noise typical of authentic photographic captures.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Upload & Main Panel */}
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-white rounded-xl border border-[#E6E1D8] shadow-sm p-6 sm:p-8">
            <h2 className="text-lg font-semibold text-[#1A1E1C] mb-1">
              Is this image AI-generated or a real photograph?
            </h2>
            <p className="text-xs text-[#6B7570] mb-5">
              Upload any image to run Swin Transformer computer-vision forensics. Supported: JPEG, PNG, WEBP (Max 15MB).
            </p>

            {/* Drag & Drop Area */}
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={`relative border-2 border-dashed rounded-xl p-6 sm:p-8 text-center cursor-pointer transition-all duration-200 ${
                isDragging
                  ? 'border-[#1B3B2B] bg-[#EAF2ED]/50 scale-[0.99]'
                  : previewUrl
                  ? 'border-[#C5DDD0] bg-[#FBF9F5]'
                  : 'border-[#D1CABE] hover:border-[#1B3B2B] bg-[#FAF8F5]'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".jpg,.jpeg,.png,.webp"
                onChange={handleInputChange}
                className="hidden"
              />

              {previewUrl ? (
                <div className="relative group max-h-[380px] flex flex-col items-center justify-center">
                  <img
                    src={previewUrl}
                    alt="Uploaded preview"
                    className="max-h-[320px] w-auto max-w-full rounded-lg object-contain shadow-sm border border-[#E6E1D8]"
                  />
                  <div className="mt-3 flex items-center justify-between w-full max-w-md px-2 text-xs text-[#4A5450]">
                    <span className="font-mono truncate">{fileName}</span>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReset();
                      }}
                      className="text-[#991B1B] hover:text-[#7F1D1D] font-medium flex items-center gap-1 ml-2"
                    >
                      <X className="w-3.5 h-3.5" />
                      Remove
                    </button>
                  </div>
                </div>
              ) : (
                <div className="py-8 flex flex-col items-center">
                  <div className="w-14 h-14 rounded-full bg-[#EAF2ED] flex items-center justify-center text-[#1B3B2B] mb-4">
                    <UploadCloud className="w-7 h-7" />
                  </div>
                  <p className="text-sm font-semibold text-[#1A1E1C]">
                    Drag and drop your image here, or <span className="text-[#1B3B2B] underline">browse files</span>
                  </p>
                  <p className="text-xs text-[#6B7570] mt-1.5">
                    JPEG, JPG, PNG, WEBP up to 15 MB
                  </p>
                </div>
              )}
            </div>

            {/* Error Message Alert */}
            {errorMessage && (
              <div className="mt-4 p-4 rounded-lg bg-[#FEF2F2] border border-[#FCA5A5] flex items-start gap-3 text-xs text-[#991B1B]">
                <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
                <div className="flex-1">
                  <span className="font-semibold block mb-0.5">Analysis Request Error</span>
                  {errorMessage}
                </div>
              </div>
            )}

            {/* Primary Action Button */}
            <div className="mt-6 flex flex-col sm:flex-row gap-3">
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={!selectedFile || isLoading}
                className={`flex-1 py-3 px-6 rounded-lg text-sm font-semibold tracking-wide flex items-center justify-center gap-2 shadow-sm transition-all ${
                  !selectedFile || isLoading
                    ? 'bg-[#E6E1D8] text-[#8C8476] cursor-not-allowed'
                    : 'bg-[#1B3B2B] text-white hover:bg-[#132A1F] active:scale-[0.99] cursor-pointer'
                }`}
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Analyzing image authenticity...</span>
                  </>
                ) : (
                  <>
                    <FileImage className="w-4 h-4" />
                    <span>Analyze Image</span>
                  </>
                )}
              </button>

              {(selectedFile || result) && !isLoading && (
                <button
                  type="button"
                  onClick={handleReset}
                  className="py-3 px-4 rounded-lg text-sm font-medium text-[#4A5450] hover:text-[#1A1E1C] bg-[#F4F1EA] hover:bg-[#EAE5DC] transition-colors border border-[#DCD5C9] flex items-center justify-center gap-1.5"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Analyze Another Image</span>
                </button>
              )}
            </div>
          </div>

          {/* Quick Benchmark Samples */}
          <div className="bg-white rounded-xl border border-[#E6E1D8] p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-[#1B3B2B]">
                Benchmark Evaluation Samples
              </span>
              <span className="text-[11px] text-[#6B7570]">Click to load instantly</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              {SAMPLE_BENCHMARKS.map((s, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectSample(s)}
                  disabled={isLoading}
                  className="p-2 text-left rounded-lg border border-[#E6E1D8] hover:border-[#1B3B2B] bg-[#FAF8F5] hover:bg-[#F3EFE8] transition-all group focus:outline-none"
                >
                  <img
                    src={s.url}
                    alt={s.title}
                    className="w-full h-16 object-cover rounded mb-1.5 border border-[#E6E1D8]"
                  />
                  <p className="text-[11px] font-medium text-[#1A1E1C] line-clamp-1 group-hover:text-[#1B3B2B]">
                    {s.title.split(':')[1]?.trim() || s.title}
                  </p>
                  <span
                    className={`inline-block text-[9px] font-semibold uppercase px-1 py-0.5 rounded mt-0.5 ${
                      s.type === 'ai' ? 'bg-[#EDE9FE] text-[#6D28D9]' : 'bg-[#DCFCE7] text-[#166534]'
                    }`}
                  >
                    {s.type === 'ai' ? 'AI Sample' : 'Real Photo'}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Result Panel & Explanations */}
        <div className="lg:col-span-5 space-y-6">
          {isLoading && (
            <div className="bg-white rounded-xl border border-[#E6E1D8] p-8 text-center shadow-sm">
              <div className="w-12 h-12 rounded-full bg-[#EAF2ED] text-[#1B3B2B] flex items-center justify-center mx-auto mb-4 animate-bounce">
                <RefreshCw className="w-6 h-6 animate-spin" />
              </div>
              <h3 className="text-base font-semibold text-[#1A1E1C]">
                Analyzing image authenticity...
              </h3>
              <p className="text-xs text-[#6B7570] mt-1 max-w-sm mx-auto">
                Running Swin Transformer image forensics, extracting spatial frequency embeddings, and evaluating generative noise distributions.
              </p>
              <div className="w-full bg-[#E6E1D8] h-1.5 rounded-full overflow-hidden mt-6">
                <div className="bg-[#1B3B2B] h-full w-2/3 animate-pulse rounded-full" />
              </div>
            </div>
          )}

          {!isLoading && result && (
            <div className="bg-white rounded-xl border border-[#E6E1D8] shadow-sm overflow-hidden">
              {/* Verdict Header Header Card */}
              <div
                className={`p-6 border-b ${
                  result.prediction === 'likely_ai_generated'
                    ? 'bg-[#FAF5FF] border-[#E9D5FF]'
                    : result.prediction === 'likely_real_photograph'
                    ? 'bg-[#F0FDF4] border-[#BBF7D0]'
                    : 'bg-[#FFFBEB] border-[#FDE68A]'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  {result.prediction === 'likely_ai_generated' ? (
                    <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#8B5CF6] text-white text-xs font-bold uppercase tracking-wider shadow-sm">
                      <Sparkles className="w-3.5 h-3.5" />
                      Likely AI-Generated
                    </span>
                  ) : result.prediction === 'likely_real_photograph' ? (
                    <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#16A34A] text-white text-xs font-bold uppercase tracking-wider shadow-sm">
                      <CheckCircle className="w-3.5 h-3.5" />
                      Likely Real Photograph
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#D97706] text-white text-xs font-bold uppercase tracking-wider shadow-sm">
                      <HelpCircle className="w-3.5 h-3.5" />
                      Uncertain Result
                    </span>
                  )}
                </div>

                <div className="mt-4">
                  <div className="flex items-baseline justify-between">
                    <span className="text-xs font-medium text-[#4A5450] uppercase tracking-wide">
                      Model Confidence Score
                    </span>
                    <span className="text-2xl font-bold font-mono text-[#1A1E1C]">
                      {(result.confidence * 100).toFixed(1)}%
                    </span>
                  </div>

                  {/* Probability Bar */}
                  {result.probabilities && (
                    <div className="mt-3">
                      <div className="w-full h-3 rounded-full bg-[#E5E7EB] flex overflow-hidden border border-[#D1D5DB]">
                        <div
                          style={{ width: `${result.probabilities.ai_generated * 100}%` }}
                          className="bg-[#8B5CF6] transition-all duration-500"
                          title={`AI-Generated: ${(result.probabilities.ai_generated * 100).toFixed(1)}%`}
                        />
                        <div
                          style={{ width: `${result.probabilities.real_photograph * 100}%` }}
                          className="bg-[#16A34A] transition-all duration-500"
                          title={`Real Photograph: ${(result.probabilities.real_photograph * 100).toFixed(1)}%`}
                        />
                      </div>
                      <div className="flex justify-between text-[11px] font-mono mt-1 text-[#4A5450]">
                        <span>Synthetic: {(result.probabilities.ai_generated * 100).toFixed(1)}%</span>
                        <span>Authentic: {(result.probabilities.real_photograph * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Explanation Body */}
              <div className="p-6 space-y-5">
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-[#1B3B2B] mb-1.5">
                    Forensic Explanation
                  </h4>
                  <p className="text-sm text-[#2E3532] leading-relaxed bg-[#FAF8F5] p-3.5 rounded-lg border border-[#E6E1D8]">
                    {result.explanation}
                  </p>
                </div>

                {/* Model & Metadata details */}
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3 rounded-lg bg-[#FAF8F5] border border-[#E6E1D8]">
                    <span className="text-[10px] font-semibold text-[#6B7570] uppercase block mb-0.5">
                      Model Identifier
                    </span>
                    <span className="font-mono text-[#1A1E1C] truncate block" title={result.model_name}>
                      {result.model_name.split(' ')[0]}
                    </span>
                  </div>

                  <div className="p-3 rounded-lg bg-[#FAF8F5] border border-[#E6E1D8]">
                    <span className="text-[10px] font-semibold text-[#6B7570] uppercase block mb-0.5">
                      Dimensions / Format
                    </span>
                    <span className="font-mono text-[#1A1E1C]">
                      {result.image_metadata?.width}x{result.image_metadata?.height} ({result.image_metadata?.format})
                    </span>
                  </div>
                </div>

                {/* Important Limitations */}
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-[#991B1B] flex items-center gap-1.5 mb-2">
                    <ShieldAlert className="w-3.5 h-3.5" />
                    Important Scientific Limitations
                  </h4>
                  <ul className="space-y-1.5 text-xs text-[#4A5450] bg-[#FFFBF8] p-3.5 rounded-lg border border-[#FEE2E2]">
                    {result.limitations.map((lim, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-[#991B1B] font-bold">•</span>
                        <span>{lim}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Action Button: Analyze Another */}
                <button
                  type="button"
                  onClick={handleReset}
                  className="w-full py-2.5 px-4 rounded-lg bg-[#1B3B2B] text-white hover:bg-[#132A1F] text-xs font-semibold tracking-wide transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-sm"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Analyze Another Image</span>
                </button>
              </div>
            </div>
          )}

          {/* Fallback / Initial State Guide */}
          {!isLoading && !result && (
            <div className="bg-white rounded-xl border border-[#E6E1D8] p-6 shadow-sm space-y-4">
              <h3 className="text-sm font-semibold text-[#1A1E1C] flex items-center gap-2">
                <Info className="w-4 h-4 text-[#1B3B2B]" />
                How TRUTHLENS Evaluates Images
              </h3>
              <p className="text-xs text-[#4A5450] leading-relaxed">
                The detector executes Swin Transformer feature extraction on the uploaded image pixels. It inspects:
              </p>
              <ul className="space-y-2 text-xs text-[#4A5450]">
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#1B3B2B] mt-1.5 shrink-0" />
                  <span><strong>Synthetic Noise Signatures:</strong> Detects repetitive grid or frequency traces left by latent diffusion synthesis.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#1B3B2B] mt-1.5 shrink-0" />
                  <span><strong>Optical Sensor Grain:</strong> Verifies natural Bayer filter sensor noise distributions present in physical camera sensors.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#1B3B2B] mt-1.5 shrink-0" />
                  <span><strong>Calibrated Epistemic Abstention:</strong> If probabilities remain between 40% and 60%, the system refrains from guessing and presents an <em>Uncertain Result</em>.</span>
                </li>
              </ul>

              {modelInfo && (
                <div className="pt-4 border-t border-[#E6E1D8] text-[11px] text-[#6B7570] space-y-1">
                  <div className="flex justify-between">
                    <span>Configured Model:</span>
                    <span className="font-mono text-[#1A1E1C]">{modelInfo.model_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Inference Hardware:</span>
                    <span className="font-mono text-[#1A1E1C] uppercase">{modelInfo.device}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <span className="text-[#16A34A] font-medium">Ready & Cached In-Memory</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
