import React, { useState, useEffect } from 'react';
import { Eye, ShieldCheck, Database, History, FlaskConical, Lock, Menu, X, ArrowUpRight, Sparkles } from 'lucide-react';
import { fetchCapabilities } from '../services/api';

import { Capabilities } from '../types';

interface NavbarProps {
  currentTab: string;
  onNavigate: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, onNavigate }) => {
  const [capabilities, setCapabilities] = useState<Capabilities | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    fetchCapabilities()
      .then(setCapabilities)
      .catch(() => {});
  }, []);

  const navItems = [
    { id: 'detector', label: 'AI Authenticity Detector', icon: Sparkles },
    { id: 'research-lab', label: 'Research Lab & Metrics', icon: FlaskConical },
    { id: 'privacy', label: 'Privacy & Integrity', icon: Lock },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#FBF9F5]/95 backdrop-blur-md border-b border-[#E6E1D8]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Tagline */}
          <div className="flex items-center gap-6">
            <button
              onClick={() => onNavigate('detector')}
              className="flex items-center gap-3 text-left group focus:outline-none cursor-pointer"
            >
              <div className="w-9 h-9 rounded-md bg-[#1B3B2B] flex items-center justify-center text-[#FBF9F5] shadow-sm transition-transform group-hover:scale-105">
                <Eye className="w-5 h-5 stroke-[2.2]" />
              </div>
              <div>
                <span className="font-editorial text-xl font-bold tracking-tight text-[#1A1E1C] block leading-none">
                  TRUTHLENS
                </span>
                <span className="text-[10px] tracking-widest uppercase font-semibold text-[#1B3B2B] block mt-0.5">
                  AI Image Authenticity Detector
                </span>
              </div>
            </button>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-1 pl-4 border-l border-[#E6E1D8]">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onNavigate(item.id)}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-colors cursor-pointer ${
                      isActive
                        ? 'bg-[#1B3B2B] text-[#FBF9F5]'
                        : 'text-[#4A5450] hover:text-[#1A1E1C] hover:bg-[#F4F1EA]'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Right Status & Action */}
          <div className="hidden lg:flex items-center gap-4">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#EAF2ED] text-[#1B3B2B] text-[11px] font-medium border border-[#C5DDD0]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#1B7A43] animate-pulse" />
              <span>Swin Transformer Model Active</span>
            </div>
            <button
              onClick={() => onNavigate('detector')}
              className="flex items-center gap-1.5 bg-[#1B3B2B] text-[#FBF9F5] hover:bg-[#132E20] px-4 py-2 rounded-md text-xs font-semibold tracking-wide shadow-sm transition-all hover:shadow cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Detect Image</span>
            </button>
          </div>


          {/* Mobile hamburger */}
          <div className="flex md:hidden items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-[#4A5450] hover:text-[#1A1E1C] rounded-md focus:outline-none"
              aria-label="Toggle Navigation"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-[#E6E1D8] bg-[#FBF9F5] px-4 pt-2 pb-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onNavigate(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium ${
                  isActive
                    ? 'bg-[#1B3B2B] text-[#FBF9F5]'
                    : 'text-[#4A5450] hover:bg-[#F4F1EA]'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
};
