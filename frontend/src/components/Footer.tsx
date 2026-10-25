import React from 'react';
import { Eye, Shield, BookOpen, Lock, Terminal } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-[#F4F1EA] border-t border-[#E6E1D8] mt-24 py-12 text-[#4A5450]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Col 1 */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-6 h-6 rounded bg-[#1B3B2B] flex items-center justify-center text-[#FBF9F5]">
                <Eye className="w-3.5 h-3.5" />
              </div>
              <span className="font-editorial font-bold text-lg text-[#1A1E1C]">
                TRUTHLENS
              </span>
            </div>
            <p className="text-xs text-[#5C6661] max-w-md leading-relaxed mb-4">
              An academic and investigative platform dedicated to scrutinizing visual misinformation,
              decoupling image authenticity from claim accuracy, and enforcing strict evidence-based reasoning.
            </p>
            <div className="p-3 bg-[#EAE5DA] rounded-md border border-[#D9D3C7] text-[11px] text-[#2C332F] leading-normal">
              <strong>Responsible AI Commitment:</strong> TRUTHLENS never hallucinates sources, fabricates publication dates, or converts absence of evidence into an unfounded verdict of falsity.
            </div>
          </div>

          {/* Col 2 */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[#1A1E1C] mb-3">
              Methodology
            </h4>
            <ul className="space-y-2 text-xs">
              <li className="hover:text-[#1B3B2B] cursor-pointer">Perceptual Image Hashing</li>
              <li className="hover:text-[#1B3B2B] cursor-pointer">EXIF Provenance Forensics</li>
              <li className="hover:text-[#1B3B2B] cursor-pointer">Lexical-Semantic Passage Retrieval</li>
              <li className="hover:text-[#1B3B2B] cursor-pointer">Epistemic Uncertainty Framework</li>
            </ul>
          </div>

          {/* Col 3 */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[#1A1E1C] mb-3">
              Ethical Standards
            </h4>
            <ul className="space-y-2 text-xs">
              <li className="hover:text-[#1B3B2B] cursor-pointer">Zero Data Selling</li>
              <li className="hover:text-[#1B3B2B] cursor-pointer">GPS Redaction by Default</li>
              <li className="hover:text-[#1B3B2B] cursor-pointer">One-Click Dossier Deletion</li>
              <li className="hover:text-[#1B3B2B] cursor-pointer">VERITE Benchmark Compatibility</li>
            </ul>
          </div>
        </div>

        <div className="pt-6 border-t border-[#DFD9CE] flex flex-col sm:flex-row items-center justify-between text-[11px] text-[#737E79]">
          <p>© {new Date().getFullYear()} TRUTHLENS Academic Research Initiative. Designed for evaluators, journalists, and researchers.</p>
          <p className="mt-2 sm:mt-0 font-mono text-[10px]">BUILD: 1.0.0-PROD (CPU-EMBED)</p>
        </div>
      </div>
    </footer>
  );
};
