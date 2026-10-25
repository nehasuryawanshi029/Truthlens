import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { DetectorPage } from './pages/DetectorPage';
import { ResearchLabPage } from './pages/ResearchLabPage';
import { PrivacyPage } from './pages/PrivacyPage';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('detector');

  const handleNavigate = (tab: string) => {
    setCurrentTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#FBF9F5] text-[#1A1E1C]">
      <Navbar currentTab={currentTab} onNavigate={handleNavigate} />

      <main className="flex-1">
        {currentTab === 'detector' && <DetectorPage />}

        {currentTab === 'research-lab' && <ResearchLabPage />}

        {currentTab === 'privacy' && <PrivacyPage />}
      </main>

      <Footer />
    </div>
  );
}

export default App;

