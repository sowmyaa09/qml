import React, { useEffect, useRef, useState } from 'react';
import { Shield, ChevronDown, User, Edit3, BarChart2, CheckCircle2 } from 'lucide-react';
import { TabType } from '../types';

interface NavbarProps {
  currentTab: TabType;
  onSelectTab: (tab: TabType) => void;
  onOpenModal: (modal: 'metrics-guide' | 'about-and-boundaries') => void;
}

const NAV_TABS: { id: TabType; label: string }[] = [
  { id: 'story', label: 'Story' },
  { id: 'data', label: 'Data' },
  { id: 'classical', label: 'Classical' },
  { id: 'qml-studio', label: 'QML Studio' },
  { id: 'cost-latency', label: 'Cost' },
  { id: 'simulator-demo', label: 'Simulator' },
  { id: 'paste-a-record', label: 'Score sheet' },
];

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onSelectTab,
  onOpenModal,
}) => {
  const [moreOpen, setMoreOpen] = useState(false);
  const moreRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!moreOpen) return;
    const onDocClick = (event: MouseEvent) => {
      if (moreRef.current && !moreRef.current.contains(event.target as Node)) {
        setMoreOpen(false);
      }
    };
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, [moreOpen]);

  return (
    <>
      <aside className="fixed top-0 left-0 right-0 h-9 z-50 bg-[#02110c]/90 backdrop-blur-md flex items-center justify-between px-4 border-b-2 border-[#5cffb5]/40">
        <div className="flex items-center gap-2 min-w-0">
          <Shield className="w-4 h-4 text-[#5cffb5] shrink-0" />
          <span className="font-mono text-[11px] text-[#b8ffd9] tracking-wider truncate">
            Research risk classification — not a medical device, not for clinical use.
          </span>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-[#082a21] font-mono text-[11px] text-[#5cffb5] border border-[#5cffb5]/50">
            <span className="w-1.5 h-1.5 rounded-full bg-[#5cffb5] animate-pulse"></span>
            SIH26139 · RESEARCH ONLY
          </span>
        </div>
      </aside>

      <header className="fixed top-9 left-0 right-0 z-50 overflow-visible bg-[#02110c]/90 backdrop-blur-xl border-b-2 border-[#5cffb5]/35">
        <div className="w-full min-h-[4.25rem] px-2 md:px-3 py-2 flex items-center gap-2 md:gap-3">
          <div
            onClick={() => onSelectTab('story')}
            className="flex items-center gap-2 min-w-0 cursor-pointer select-none shrink-0"
          >
            <img
              alt="LAKSHYA Quantum Biomedical Logo"
              className="h-9 w-auto object-contain drop-shadow-[0_0_10px_rgba(94,255,181,0.7)] shrink-0"
              src="https://lh3.googleusercontent.com/aida/AEtjO1UzG1gqLTNgstlLKUoTkk_X1KDkt5v26p8heySHbqaBoGo4a8xfLaZx6n8ECkiv6OkggusbPIHRmkbZBxA96jzhM8A3sMh3tq8hKmjIimBdKvHKJF7bEItBkWJ57htCsQsVP51ExFx2jC6BC225-OCLgL5n5Y84ABc6DPFxJ976eFZsTcqNKxaNUO7T_qwQmcCr5JZzDWaFiAf3JmdfREoxSphqTFsF-k312CDQLQ7UVMofNw9Uy-_R6DM"
            />
            <div className="hidden xl:flex flex-col min-w-0">
              <span className="font-bold text-base text-[#d6ffe9] tracking-wider uppercase">
                LAKSHYA
              </span>
              <span className="text-[10px] text-[#b8ffd9] truncate">
                Q-Care Detect · SIH26139
              </span>
            </div>
          </div>

          <nav className="hidden md:flex flex-1 min-w-0 items-center gap-1.5 lg:gap-2">
            {NAV_TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => onSelectTab(tab.id)}
                className={`nav-tab ${
                  currentTab === tab.id ? 'nav-tab-active' : ''
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          <div className="relative flex items-center gap-2 shrink-0" ref={moreRef}>
            <button
              type="button"
              onClick={() => setMoreOpen((open) => !open)}
              className={`nav-tab nav-tab-more ${moreOpen ? 'nav-tab-active' : ''}`}
              aria-expanded={moreOpen}
            >
              More
              <ChevronDown className="w-4 h-4 ml-1" />
            </button>

            {moreOpen && (
              <div className="absolute right-0 top-[calc(100%+8px)] w-56 max-w-[calc(100vw-1.5rem)] p-2 bg-[#06241c] border-4 border-[#06281c] shadow-[4px_4px_0_#041910] flex flex-col gap-2 z-[80]">
                <button
                  type="button"
                  className="btn-menu"
                  onClick={() => {
                    onSelectTab('paste-a-record');
                    setMoreOpen(false);
                  }}
                >
                  <span>Paste a record</span>
                  <Edit3 className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  className="btn-menu"
                  onClick={() => {
                    onOpenModal('metrics-guide');
                    setMoreOpen(false);
                  }}
                >
                  <span>Metrics Guide</span>
                  <BarChart2 className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  className="btn-menu"
                  onClick={() => {
                    onOpenModal('about-and-boundaries');
                    setMoreOpen(false);
                  }}
                >
                  <span>About & Boundaries</span>
                  <CheckCircle2 className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            <div className="w-8 h-8 rounded-full bg-[#d6ffe9] flex items-center justify-center text-[#032016] font-bold shrink-0">
              <User className="w-4 h-4" />
            </div>
          </div>
        </div>

        <div className="md:hidden flex items-center gap-2 px-2 py-2 overflow-x-auto border-t border-[#5cffb5]/20">
          {NAV_TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => onSelectTab(tab.id)}
              className={`nav-tab shrink-0 !flex-[0_0_auto] !min-w-[7.5rem] ${
                currentTab === tab.id ? 'nav-tab-active' : ''
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </header>
    </>
  );
};
