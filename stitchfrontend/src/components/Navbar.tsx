import React, { useState } from 'react';
import { Shield, ChevronDown, User, Edit3, BarChart2, CheckCircle2 } from 'lucide-react';
import { TabType } from '../types';

interface NavbarProps {
  currentTab: TabType;
  onSelectTab: (tab: TabType) => void;
  onOpenModal: (modal: 'metrics-guide' | 'about-and-boundaries') => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onSelectTab,
  onOpenModal,
}) => {
  const [moreOpen, setMoreOpen] = useState(false);

  return (
    <>
      {/* Top Advisory Strip */}
      <aside className="fixed top-0 left-0 right-0 h-9 z-50 bg-[#0a0e17]/95 backdrop-blur-md flex items-center justify-between px-4 border-b border-[#31353f]/40 shadow-[0_1px_8px_rgba(0,0,0,0.6)]">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-[#00dbe9]" />
          <span className="font-mono text-[11px] text-[#b9cacb] tracking-wider">
            Research risk classification — not a medical device, not for clinical use.
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#262a34] font-mono text-[11px] text-[#00dbe9]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#00dbe9] animate-pulse"></span>
            SIH26139 · RESEARCH ONLY
          </span>
          <span className="hidden md:inline-flex font-mono text-[11px] text-[#849495]">
            v0.9.4-quantum-kernel
          </span>
        </div>
      </aside>

      {/* Main Header */}
      <header className="fixed top-9 left-0 right-0 h-16 z-40 bg-[#070b13]/90 backdrop-blur-xl border-b border-[#31353f]/40 shadow-[0_1px_12px_rgba(0,0,0,0.7)]">
        <div className="w-full h-full px-4 md:px-6 flex items-center justify-between gap-4">
          {/* Logo & Identity */}
          <div
            onClick={() => onSelectTab('story')}
            className="flex items-center gap-3 min-w-max cursor-pointer select-none"
          >
            <img
              alt="LAKSHYA Quantum Biomedical Logo"
              className="h-8 w-auto object-contain drop-shadow-[0_0_8px_rgba(0,219,233,0.4)]"
              src="https://lh3.googleusercontent.com/aida/AEtjO1UzG1gqLTNgstlLKUoTkk_X1KDkt5v26p8heySHbqaBoGo4a8xfLaZx6n8ECkiv6OkggusbPIHRmkbZBxA96jzhM8A3sMh3tq8hKmjIimBdKvHKJF7bEItBkWJ57htCsQsVP51ExFx2jC6BC225-OCLgL5n5Y84ABc6DPFxJ976eFZsTcqNKxaNUO7T_qwQmcCr5JZzDWaFiAf3JmdfREoxSphqTFsF-k312CDQLQ7UVMofNw9Uy-_R6DM"
            />
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-[#dbfcff] tracking-wider uppercase">
                  LAKSHYA
                </span>
                <span className="px-1.5 py-0.5 rounded bg-[#262a34] font-mono text-[10px] text-[#00dbe9] uppercase">
                  SIH26139
                </span>
                <span className="px-1.5 py-0.5 rounded bg-[#571bc1]/40 font-mono text-[10px] text-[#e9ddff] uppercase">
                  RESEARCH ONLY
                </span>
              </div>
              <span className="text-xs text-[#b9cacb]">
                Q-Care Detect · SIH 2026 SIH26139 · Team Mirage
              </span>
            </div>
          </div>

          {/* Center Navigation Tabs */}
          <nav className="hidden lg:flex items-center gap-1 p-1 rounded-xl bg-[#0a0e17]/90 border border-[#31353f]/50">
            <button
              onClick={() => onSelectTab('story')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                currentTab === 'story'
                  ? 'bg-[#262a34] text-[#dbfcff] font-semibold shadow-sm'
                  : 'text-[#b9cacb] hover:text-[#dfe2f0] hover:bg-[#171c25]'
              }`}
            >
              Story
            </button>
            <button
              onClick={() => onSelectTab('data')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                currentTab === 'data'
                  ? 'bg-[#262a34] text-[#dbfcff] font-semibold shadow-sm'
                  : 'text-[#b9cacb] hover:text-[#dfe2f0] hover:bg-[#171c25]'
              }`}
            >
              Data
            </button>
            <button
              onClick={() => onSelectTab('classical')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                currentTab === 'classical'
                  ? 'bg-[#262a34] text-[#dbfcff] font-semibold shadow-sm'
                  : 'text-[#b9cacb] hover:text-[#dfe2f0] hover:bg-[#171c25]'
              }`}
            >
              Classical
            </button>
            <button
              onClick={() => onSelectTab('qml-studio')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                currentTab === 'qml-studio'
                  ? 'bg-[#262a34] text-[#dbfcff] font-semibold shadow-sm'
                  : 'text-[#b9cacb] hover:text-[#dfe2f0] hover:bg-[#171c25]'
              }`}
            >
              QML Studio
            </button>
            <button
              onClick={() => onSelectTab('cost-latency')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                currentTab === 'cost-latency'
                  ? 'bg-[#262a34] text-[#dbfcff] font-semibold shadow-sm'
                  : 'text-[#b9cacb] hover:text-[#dfe2f0] hover:bg-[#171c25]'
              }`}
            >
              Cost
            </button>
            <button
              onClick={() => onSelectTab('simulator-demo')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                currentTab === 'simulator-demo'
                  ? 'bg-[#262a34] text-[#dbfcff] font-semibold shadow-sm'
                  : 'text-[#b9cacb] hover:text-[#dfe2f0] hover:bg-[#171c25]'
              }`}
            >
              Simulator Demo
            </button>
          </nav>

          {/* Right Action Tools */}
          <div className="flex items-center gap-3 min-w-max">
            {/* Aer Simulator status badge */}
            <div className="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#0a0e17] border border-[#31353f]/40">
              <span className="w-2 h-2 rounded-full bg-[#00dbe9] shadow-[0_0_8px_#00dbe9]"></span>
              <span className="font-mono text-xs text-[#00dbe9]">
                Aer Simulator · Statevector (No QPU)
              </span>
            </div>

            {/* More dropdown */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setMoreOpen(!moreOpen)}
                onBlur={() => setTimeout(() => setMoreOpen(false), 200)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#171c25] text-xs font-medium text-[#b9cacb] hover:text-[#dfe2f0] hover:bg-[#262a34] border border-[#31353f]/40 transition-all"
              >
                <span>More</span>
                <ChevronDown className="w-4 h-4 text-[#849495]" />
              </button>

              {moreOpen && (
                <div className="absolute right-0 top-full mt-2 w-56 p-1.5 rounded-xl bg-[#262a34]/95 backdrop-blur-xl border border-[#31353f] shadow-[0_8px_32px_rgba(0,0,0,0.8)] flex flex-col z-50 animate-in fade-in zoom-in-95 duration-100">
                  <button
                    onClick={() => {
                      onSelectTab('paste-a-record');
                      setMoreOpen(false);
                    }}
                    className="px-3 py-2 rounded-lg text-xs text-left text-[#b9cacb] hover:text-[#dfe2f0] hover:bg-[#1b2029] transition-all flex items-center justify-between"
                  >
                    <span>Paste a record</span>
                    <Edit3 className="w-3.5 h-3.5 text-[#849495]" />
                  </button>
                  <button
                    onClick={() => {
                      onOpenModal('metrics-guide');
                      setMoreOpen(false);
                    }}
                    className="px-3 py-2 rounded-lg text-xs text-left text-[#b9cacb] hover:text-[#dfe2f0] hover:bg-[#1b2029] transition-all flex items-center justify-between"
                  >
                    <span>Metrics Guide</span>
                    <BarChart2 className="w-3.5 h-3.5 text-[#849495]" />
                  </button>
                  <button
                    onClick={() => {
                      onOpenModal('about-and-boundaries');
                      setMoreOpen(false);
                    }}
                    className="px-3 py-2 rounded-lg text-xs text-left text-[#b9cacb] hover:text-[#dfe2f0] hover:bg-[#1b2029] transition-all flex items-center justify-between"
                  >
                    <span>About & Boundaries</span>
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#849495]" />
                  </button>
                </div>
              )}
            </div>

            {/* Profile / Avatar */}
            <div className="w-8 h-8 rounded-full bg-[#dbfcff] flex items-center justify-center text-[#00363a] font-bold shadow-sm">
              <User className="w-4 h-4" />
            </div>
          </div>
        </div>

        {/* Mobile Navigation bar */}
        <div className="lg:hidden flex items-center justify-around px-2 py-1 bg-[#0a0e17] border-t border-[#31353f]/50 overflow-x-auto text-xs">
          {(
            ['story', 'data', 'classical', 'qml-studio', 'cost-latency', 'simulator-demo'] as TabType[]
          ).map((tab) => (
              <button
                key={tab}
                onClick={() => onSelectTab(tab)}
                className={`px-2 py-1 rounded whitespace-nowrap ${
                  currentTab === tab
                    ? 'text-[#00dbe9] font-bold bg-[#1b2029]'
                    : 'text-[#b9cacb]'
                }`}
              >
                {tab === 'qml-studio'
                  ? 'QML'
                  : tab === 'cost-latency'
                  ? 'Cost'
                  : tab === 'simulator-demo'
                  ? 'Simulator'
                  : tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
        </div>
      </header>
    </>
  );
};
