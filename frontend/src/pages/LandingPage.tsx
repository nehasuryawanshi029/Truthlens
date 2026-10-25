import React, { useState, useEffect } from 'react';
import {
  ArrowRight,
  Shield,
  Search,
  Scale,
  Sparkles,
  Compass,
  FileText,
  AlertTriangle,
  CheckCircle,
  Eye,
  Layers,
  ChevronRight,
  Database
} from 'lucide-react';
import { DemoCase } from '../types';
import { fetchDemoCases } from '../services/api';

interface LandingPageProps {
  onStartInvestigation: () => void;
  onSelectDemo: (demo: DemoCase) => void;
  onOpenResearchLab: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onStartInvestigation,
  onSelectDemo,
  onOpenResearchLab
}) => {
  const [demos, setDemos] = useState<DemoCase[]>([]);

  useEffect(() => {
    fetchDemoCases()
      .then(setDemos)
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-20 pb-12">
      {/* 1. Hero Section */}
      <section className="pt-12 sm:pt-20 pb-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#EAF2ED] text-[#1B3B2B] text-xs font-semibold uppercase tracking-wider border border-[#C5DDD0]">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Academic Multimodal Investigation Platform</span>
            </div>

            <h1 className="font-editorial text-4xl sm:text-6xl font-extrabold text-[#1A1E1C] leading-[1.08] tracking-tight">
              Every Image Has a Story.{' '}
              <span className="italic font-serif font-normal text-[#1B3B2B] block">
                Find the Evidence.
              </span>
            </h1>

            <p className="text-base sm:text-lg text-[#4A5450] max-w-xl leading-relaxed">
              Investigate suspicious images, uncover missing context, and examine the grounded evidence behind viral social media claims.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                onClick={onStartInvestigation}
                className="bg-[#1B3B2B] hover:bg-[#132E20] text-[#FBF9F5] px-6 py-3.5 rounded-md text-sm font-semibold tracking-wide shadow-md transition-all flex items-center gap-2"
              >
                <span>Start an Investigation</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <a
                href="#demo-section"
                className="bg-[#FFFFFF] hover:bg-[#F4F1EA] text-[#1A1E1C] border border-[#D9D3C7] px-5 py-3.5 rounded-md text-sm font-semibold transition-all flex items-center gap-2"
              >
                <span>Explore Sample Dossiers</span>
              </a>
            </div>

            {/* Core Epistemic Tenet Pill */}
            <div className="pt-4 flex items-start gap-2.5 text-xs text-[#5C6661] border-t border-[#E6E1D8]">
              <Scale className="w-4 h-4 text-[#1B3B2B] shrink-0 mt-0.5" />
              <span>
                <strong>First Principle:</strong> Image authenticity and claim accuracy are independent questions. A genuine 2019 photo can be shared with a completely fabricated 2026 caption.
              </span>
            </div>
          </div>

          {/* Hero Visual: Editorial Forensic Dossier Card */}
          <div className="lg:col-span-5">
            <div className="editorial-card-elevated p-5 relative overflow-hidden bg-[#FFFFFF]">
              <div className="flex items-center justify-between pb-3 border-b border-[#F4F1EA] text-xs">
                <span className="font-mono text-[#1B3B2B] font-bold">CASE #TL-2019-9481</span>
                <span className="editorial-badge status-contradicted">Contradicted</span>
              </div>

              <div className="mt-3 relative aspect-video bg-[#262C28] rounded overflow-hidden border border-[#D9D3C7]">
                <img
                  src="/samples/mumbai_flooding_2019.jpg"
                  alt="Forensic Target Preview"
                  className="w-full h-full object-cover"
                />
                <div className="absolute bottom-2 left-2 right-2 bg-[#1A1E1C]/85 backdrop-blur-xs p-2 rounded text-[11px] text-[#FBF9F5]">
                  <span className="font-semibold block truncate">Claim: "This photograph shows flooding in Pune today."</span>
                  <span className="text-[#A7F3D0] block text-[10px]">Grounded Finding: Captured in Mumbai (July 2019)</span>
                </div>
              </div>

              <div className="mt-4 space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-[#F4F1EA]">
                  <span className="text-[#737E79]">Visual Hash Distance:</span>
                  <span className="font-mono font-medium text-[#1A1E1C]">0 bits (Exact Archival Match)</span>
                </div>
                <div className="flex justify-between py-1 border-b border-[#F4F1EA]">
                  <span className="text-[#737E79]">Temporal Delta:</span>
                  <span className="font-mono font-medium text-[#9B2C2C]">7 Years Out of Context</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-[#737E79]">Corroborating Dispatches:</span>
                  <span className="font-mono font-medium text-[#1B7A43]">3 Verified Records</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Trust Architecture Section */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="editorial-card p-8 bg-[#FFFFFF]">
          <div className="max-w-2xl mx-auto text-center space-y-3 mb-10">
            <h2 className="font-editorial text-2xl sm:text-3xl font-bold text-[#1A1E1C]">
              Built for Scrutiny, Not Sensationalism
            </h2>
            <p className="text-sm text-[#4A5450] leading-relaxed">
              Unlike generic chatbot tools that generate probabilistic text, TRUTHLENS separates visual provenance from text claims and anchors all conclusions to verified documents.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-5 bg-[#FBF9F5] rounded-md border border-[#E6E1D8] space-y-2">
              <div className="w-8 h-8 rounded bg-[#1B3B2B] text-[#FBF9F5] flex items-center justify-center font-bold text-xs mb-3">
                01
              </div>
              <h3 className="font-editorial text-base font-bold text-[#1A1E1C]">
                Perceptual Similarity Retrieval
              </h3>
              <p className="text-xs text-[#5C6661] leading-relaxed">
                Computes invariant difference hashes and spatial color vectors to uncover when a photo originally appeared on the internet.
              </p>
            </div>

            <div className="p-5 bg-[#FBF9F5] rounded-md border border-[#E6E1D8] space-y-2">
              <div className="w-8 h-8 rounded bg-[#1B3B2B] text-[#FBF9F5] flex items-center justify-center font-bold text-xs mb-3">
                02
              </div>
              <h3 className="font-editorial text-base font-bold text-[#1A1E1C]">
                Grounded Passage Matching
              </h3>
              <p className="text-xs text-[#5C6661] leading-relaxed">
                Lexical-semantic search retrieves news wire reports, official bulletins, and fact-checking archives without inventing quotes.
              </p>
            </div>

            <div className="p-5 bg-[#FBF9F5] rounded-md border border-[#E6E1D8] space-y-2">
              <div className="w-8 h-8 rounded bg-[#1B3B2B] text-[#FBF9F5] flex items-center justify-center font-bold text-xs mb-3">
                03
              </div>
              <h3 className="font-editorial text-base font-bold text-[#1A1E1C]">
                Explicit Epistemic Abstention
              </h3>
              <p className="text-xs text-[#5C6661] leading-relaxed">
                When evidence is sparse, the system explicitly reports <em>Insufficient Evidence</em>. Missing reports are never treated as proof of falsehood.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 3. How It Works Workflow Diagram */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="max-w-2xl mx-auto text-center space-y-3 mb-12">
          <h2 className="font-editorial text-2xl sm:text-3xl font-bold text-[#1A1E1C]">
            Four Steps to Grounded Verification
          </h2>
          <p className="text-sm text-[#4A5450]">
            The exact methodology executed across our multimodal Python and computer vision pipeline.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="editorial-card p-5 bg-[#FFFFFF] space-y-2 relative">
            <span className="font-mono text-xs font-bold text-[#1B3B2B]">STEP 01</span>
            <h4 className="font-editorial text-sm font-bold text-[#1A1E1C]">Ingest & Extract</h4>
            <p className="text-xs text-[#5C6661] leading-relaxed">
              Accepts uploaded image, calculates SHA-256 and perceptual hash, and parses camera EXIF/GPS tags.
            </p>
          </div>

          <div className="editorial-card p-5 bg-[#FFFFFF] space-y-2 relative">
            <span className="font-mono text-xs font-bold text-[#1B3B2B]">STEP 02</span>
            <h4 className="font-editorial text-sm font-bold text-[#1A1E1C]">Deconstruct Claim</h4>
            <p className="text-xs text-[#5C6661] leading-relaxed">
              Splits user claim into target event, claimed location, temporal reference, and core assertion.
            </p>
          </div>

          <div className="editorial-card p-5 bg-[#FFFFFF] space-y-2 relative">
            <span className="font-mono text-xs font-bold text-[#1B3B2B]">STEP 03</span>
            <h4 className="font-editorial text-sm font-bold text-[#1A1E1C]">Retrieve Evidence</h4>
            <p className="text-xs text-[#5C6661] leading-relaxed">
              Executes hybrid semantic search over curated archives, ranking passages and source credibility.
            </p>
          </div>

          <div className="editorial-card p-5 bg-[#FFFFFF] space-y-2 relative">
            <span className="font-mono text-xs font-bold text-[#1B3B2B]">STEP 04</span>
            <h4 className="font-editorial text-sm font-bold text-[#1A1E1C]">Synthesize Dossier</h4>
            <p className="text-xs text-[#5C6661] leading-relaxed">
              Evaluates temporal/geographic consistency, produces timeline, and outputs downloadable PDF.
            </p>
          </div>
        </div>
      </section>

      {/* 4. Interactive Demonstration Cases */}
      <section id="demo-section" className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto scroll-mt-20">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8 pb-4 border-b border-[#E6E1D8]">
          <div>
            <h2 className="font-editorial text-2xl sm:text-3xl font-bold text-[#1A1E1C]">
              Curated Demonstration Cases
            </h2>
            <p className="text-sm text-[#4A5450] mt-1">
              Select any benchmark scenario to immediately launch a live investigation.
            </p>
          </div>
          <button
            onClick={onOpenResearchLab}
            className="text-xs font-semibold text-[#1B3B2B] hover:underline flex items-center gap-1 self-start sm:self-auto"
          >
            <span>View Benchmark Metrics & PCA</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {demos.map((demo) => (
            <div
              key={demo.id}
              className="editorial-card overflow-hidden transition-all hover:shadow-md hover:border-[#1B3B2B]/40 flex flex-col justify-between"
            >
              <div>
                <div className="aspect-video bg-[#2D3330] overflow-hidden relative">
                  <img
                    src={demo.image_url}
                    alt={demo.title}
                    className="w-full h-full object-cover transition-transform hover:scale-105 duration-300"
                  />
                  <div className="absolute top-2 left-2">
                    <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-[#1A1E1C]/80 text-[#FBF9F5] backdrop-blur-xs">
                      {demo.case_type}
                    </span>
                  </div>
                </div>

                <div className="p-5 space-y-2">
                  <h3 className="font-editorial text-base font-bold text-[#1A1E1C]">
                    {demo.title}
                  </h3>
                  <div className="p-2.5 bg-[#FBF9F5] rounded border border-[#E6E1D8] text-xs text-[#2D3330] italic">
                    "{demo.claim}"
                  </div>
                  <p className="text-xs text-[#5C6661] leading-relaxed pt-1">
                    {demo.description}
                  </p>
                </div>
              </div>

              <div className="p-5 pt-0">
                <button
                  onClick={() => onSelectDemo(demo)}
                  className="w-full bg-[#F4F1EA] hover:bg-[#1B3B2B] text-[#1A1E1C] hover:text-[#FBF9F5] py-2 px-3 rounded text-xs font-semibold transition-colors flex items-center justify-center gap-1.5"
                >
                  <span>Launch Investigation</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 5. Academic Research & Limitations */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="editorial-card p-6 bg-[#F4F1EA] border border-[#D9D3C7]">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-[#C97A1E] shrink-0 mt-0.5" />
            <div className="space-y-1.5 text-xs text-[#2C332F] leading-relaxed">
              <h4 className="font-editorial text-sm font-bold text-[#1A1E1C]">
                Platform Limitations & Academic Context
              </h4>
              <p>
                Image similarity scores reflect nearest-neighbor metric distances in perceptual hash space; they do not constitute mathematical certainty of authenticity.
                AI detectors can be fooled by compression or synthetic diffusion textures.
                TRUTHLENS is an investigative assistive tool designed for researchers and evaluators, not an infallible automated judge.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
