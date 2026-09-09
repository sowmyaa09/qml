import React, { useState, useEffect, useRef } from 'react';
import {
  BookOpen,
  CheckCircle2,
  Scale,
  Cpu,
  Layers,
  Activity,
  ArrowDown,
  Play,
  Database,
  ArrowRight,
  Sliders,
  Sparkles,
  ChevronUp,
  ChevronDown,
} from 'lucide-react';
import { TabType } from '../types';

interface StoryViewProps {
  onNavigate: (tab: TabType) => void;
}

export const StoryView: React.FC<StoryViewProps> = ({ onNavigate }) => {
  const [activeSlide, setActiveSlide] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const slideIds = ['slide-1', 'slide-2', 'slide-3', 'slide-4'];
  const slideLabels = ['01 // PITCH', '02 // DATASETS', '03 // BASELINES', '04 // SIMULATOR'];

  const scrollToSlide = (index: number) => {
    const el = document.getElementById(slideIds[index]);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const scrollPos = container.scrollTop;
      const height = container.clientHeight;
      const idx = Math.min(3, Math.max(0, Math.round(scrollPos / height)));
      setActiveSlide(idx);
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (['input', 'textarea'].includes((document.activeElement?.tagName || '').toLowerCase())) return;

      if (e.key === 'ArrowDown' || e.key === 'PageDown' || e.key.toLowerCase() === 'j') {
        if (activeSlide < 3) {
          e.preventDefault();
          scrollToSlide(activeSlide + 1);
        }
      } else if (e.key === 'ArrowUp' || e.key === 'PageUp' || e.key.toLowerCase() === 'k') {
        if (activeSlide > 0) {
          e.preventDefault();
          scrollToSlide(activeSlide - 1);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeSlide]);

  return (
    <div className="relative w-full select-none">
      {/* Right-Side Floating Navigation Dots / Slide Counter */}
      <aside
        aria-label="Slide navigation"
        className="fixed right-6 top-1/2 -translate-y-1/2 z-40 hidden md:flex flex-col items-end gap-3 p-2 rounded-full bg-[#0a0e17]/85 backdrop-blur-md border border-[#31353f]/60 shadow-2xl"
      >
        <div className="px-2 py-0.5 rounded bg-[#262a34] text-center">
          <span className="font-mono text-[11px] text-[#00dbe9] tracking-widest">
            {`0${activeSlide + 1}/04`}
          </span>
        </div>
        <div className="flex flex-col gap-2 items-center py-1">
          {slideIds.map((_, idx) => (
            <button
              key={idx}
              onClick={() => scrollToSlide(idx)}
              aria-label={`Go to slide ${idx + 1}`}
              className="group relative flex items-center justify-end w-8 h-8 focus:outline-none"
            >
              <span className="absolute right-10 px-2 py-0.5 rounded bg-[#31353f] font-mono text-[10px] text-[#dbfcff] opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none shadow-md">
                {slideLabels[idx]}
              </span>
              <span
                className={`transition-all duration-300 rounded-full ${
                  activeSlide === idx
                    ? 'w-2 h-6 bg-[#00f0ff] shadow-[0_0_12px_#00dbe9]'
                    : 'w-2 h-2 bg-[#31353f] hover:bg-[#849495]'
                }`}
              />
            </button>
          ))}
        </div>
        <div className="flex flex-col items-center gap-0.5 text-[#849495]">
          <ChevronDown className="w-3.5 h-3.5" />
          <span className="font-mono text-[9px] uppercase tracking-tighter">Keys ↑↓</span>
        </div>
      </aside>

      {/* Snap Scroll Container */}
      <div
        ref={containerRef}
        className="w-full h-[calc(100vh-8rem)] overflow-y-scroll snap-y snap-mandatory scroll-smooth focus:outline-none no-scrollbar"
      >
        {/* ==================== SLIDE 01 ==================== */}
        <section
          id="slide-1"
          className="w-full h-full snap-start snap-always flex flex-col justify-between py-6 md:py-8 px-4 md:px-8 max-w-6xl mx-auto relative"
        >
          {/* Ambient Glows */}
          <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-25">
            <div className="absolute -top-24 left-1/4 w-96 h-96 rounded-full bg-[#00f0ff]/10 blur-3xl"></div>
            <div className="absolute top-1/2 right-1/4 w-80 h-80 rounded-full bg-[#571bc1]/20 blur-3xl"></div>
          </div>

          <div className="flex flex-col w-full z-10 my-auto">
            {/* Top Tag */}
            <div className="flex items-center gap-2 mb-2">
              <span className="w-7 h-7 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
                <BookOpen className="w-4 h-4" />
              </span>
              <span className="font-mono text-xs uppercase text-[#00dbe9] tracking-widest">
                SHOWCASE REPORT 01 · EMPIRICAL VERIFICATION
              </span>
              <span className="px-2 py-0.5 rounded bg-[#171c25] font-mono text-[10px] text-[#849495] border border-[#31353f]/40">
                QISKIT-AER-1024S
              </span>
            </div>

            {/* Wordmark */}
            <div className="relative mb-2">
              <h1 className="text-4xl md:text-6xl font-extrabold text-[#dbfcff] tracking-widest drop-shadow-[0_0_24px_rgba(0,219,233,0.35)]">
                LAKSHYA
              </h1>
              <p className="text-lg md:text-2xl text-[#b9cacb] font-medium tracking-tight mt-1">
                Classical vs hybrid QML research on public tables.
              </p>
            </div>

            {/* Foundational Observation Box */}
            <div className="mt-3 p-4 rounded-xl bg-[#0a0e17]/90 backdrop-blur-md border border-[#31353f]/60 shadow-xl relative overflow-hidden">
              <div className="absolute inset-y-0 left-0 w-1.5 bg-gradient-to-b from-[#00f0ff] via-[#00dbe9] to-[#d0bcff]"></div>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pl-3">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-6 h-6 text-[#00dbe9] shrink-0 mt-0.5" />
                  <div>
                    <span className="font-mono text-xs uppercase text-[#d0bcff] tracking-wider block font-semibold">
                      Foundational Empirical Observation
                    </span>
                    <p className="text-base md:text-lg text-[#dfe2f0] font-semibold mt-0.5">
                      “On Wisconsin, Logistic Regression beat VQC/QSVC on F1; do not claim quantum is more accurate.”
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0 self-start md:self-auto font-mono text-xs">
                  <span className="px-2.5 py-1 rounded bg-[#1b2029] border border-[#31353f]/50 text-[#00dbe9]">
                    SEED: 0x4B3A8F
                  </span>
                  <span className="px-2.5 py-1 rounded bg-[#1b2029] border border-[#31353f]/50 text-[#b9cacb]">
                    METRIC: STRATIFIED F1
                  </span>
                </div>
              </div>
            </div>

            {/* 5 Pillars Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 mt-5">
              <div className="p-3.5 rounded-xl bg-[#171c25]/90 border border-[#31353f]/40 flex flex-col justify-between hover:bg-[#1b2029] transition-all">
                <div>
                  <span className="font-mono text-[10px] text-[#849495] block mb-1">PILLAR 01</span>
                  <h2 className="text-sm font-semibold text-[#dbfcff] mb-1">Research Transparency</h2>
                  <p className="text-xs text-[#b9cacb] leading-relaxed">
                    No black-box overclaiming; verifiable metrics and public evaluation curves.
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-[#31353f]/40 flex items-center justify-between text-[#849495]">
                  <span className="font-mono text-[9px]">VERIFIED</span>
                  <CheckCircle2 className="w-4 h-4 text-[#00dbe9]" />
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#171c25]/90 border border-[#31353f]/40 flex flex-col justify-between hover:bg-[#1b2029] transition-all">
                <div>
                  <span className="font-mono text-[10px] text-[#849495] block mb-1">PILLAR 02</span>
                  <h2 className="text-sm font-semibold text-[#dbfcff] mb-1">Model Comparison</h2>
                  <p className="text-xs text-[#b9cacb] leading-relaxed">
                    Direct paired evaluations against standard pipelines on identical test splits.
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-[#31353f]/40 flex items-center justify-between text-[#849495]">
                  <span className="font-mono text-[9px]">PAIRED 80:20</span>
                  <Scale className="w-4 h-4 text-[#00dbe9]" />
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#171c25]/90 border border-[#31353f]/40 flex flex-col justify-between hover:bg-[#1b2029] transition-all">
                <div>
                  <span className="font-mono text-[10px] text-[#849495] block mb-1">PILLAR 03</span>
                  <h2 className="text-sm font-semibold text-[#dbfcff] mb-1">Architecture</h2>
                  <p className="text-xs text-[#b9cacb] leading-relaxed">
                    Parameterized Quantum Circuits (PQC) & Quantum Kernel Estimation via ZZFeatureMap.
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-[#31353f]/40 flex items-center justify-between text-[#849495]">
                  <span className="font-mono text-[9px]">N=4 QUBITS</span>
                  <Cpu className="w-4 h-4 text-[#d0bcff]" />
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#171c25]/90 border border-[#31353f]/40 flex flex-col justify-between hover:bg-[#1b2029] transition-all">
                <div>
                  <span className="font-mono text-[10px] text-[#849495] block mb-1">PILLAR 04</span>
                  <h2 className="text-sm font-semibold text-[#dbfcff] mb-1">Computational Cost</h2>
                  <p className="text-xs text-[#b9cacb] leading-relaxed">
                    Quantifying shot noise, circuit depth, and qubit scaling vs linear CPU runtime.
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-[#31353f]/40 flex items-center justify-between text-[#849495]">
                  <span className="font-mono text-[9px]">1024 SHOTS</span>
                  <Activity className="w-4 h-4 text-[#00dbe9]" />
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#171c25]/90 border border-[#31353f]/40 flex flex-col justify-between hover:bg-[#1b2029] transition-all">
                <div>
                  <span className="font-mono text-[10px] text-[#849495] block mb-1">PILLAR 05</span>
                  <h2 className="text-sm font-semibold text-[#dbfcff] mb-1">Hybrid Rigor</h2>
                  <p className="text-xs text-[#b9cacb] leading-relaxed">
                    Empirical testing strictly bounded to structured public tabular records.
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-[#31353f]/40 flex items-center justify-between text-[#849495]">
                  <span className="font-mono text-[9px]">TABULAR ONLY</span>
                  <Layers className="w-4 h-4 text-[#d0bcff]" />
                </div>
              </div>
            </div>

            {/* Actions Bar */}
            <div className="flex flex-wrap items-center gap-3 mt-6">
              <button
                type="button"
                onClick={() => scrollToSlide(1)}
                className="px-5 py-2.5 rounded-lg bg-[#00f0ff] text-[#00363a] font-bold text-sm shadow-[0_0_16px_rgba(0,219,233,0.3)] hover:bg-[#7df4ff] transition-all flex items-center gap-2"
              >
                <span>Scroll to explore</span>
                <ArrowDown className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => onNavigate('simulator-demo')}
                className="px-5 py-2.5 rounded-lg bg-[#262a34] text-[#dfe2f0] font-semibold text-sm hover:bg-[#353944] border border-[#31353f] transition-all flex items-center gap-2"
              >
                <span>Open interactive demo</span>
                <Play className="w-4 h-4 text-[#00dbe9] fill-[#00dbe9]" />
              </button>
              <span className="font-mono text-xs text-[#849495]">Section 01 of 04 · SIH 2026</span>
            </div>
          </div>

          <div className="w-full flex items-center justify-between pt-2 border-t border-[#31353f]/40 text-[#849495] z-10 text-xs font-mono">
            <span>[AUDIT FRAMEWORK] Pre-registered Hypotheses</span>
            <span>Navigate: [J] Next · [K] Prev</span>
          </div>
        </section>

        {/* ==================== SLIDE 02 ==================== */}
        <section
          id="slide-2"
          className="w-full h-full snap-start snap-always flex flex-col justify-between py-6 md:py-8 px-4 md:px-8 max-w-6xl mx-auto relative"
        >
          <div className="flex flex-col w-full z-10 my-auto">
            <div className="flex items-center gap-2 mb-1">
              <span className="w-7 h-7 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
                <Layers className="w-4 h-4" />
              </span>
              <span className="font-mono text-xs uppercase text-[#00dbe9] tracking-widest">
                ISOLATED BENCHMARK ENVIRONMENTS
              </span>
            </div>
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-3 mb-5">
              <div>
                <h2 className="text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
                  One table, one label.
                </h2>
                <p className="text-xs md:text-sm text-[#b9cacb] max-w-3xl mt-1 leading-relaxed">
                  Each biomedical dataset is treated as an isolated, single-target binary classification benchmark. Never display or imply a fused “what disease” classification.
                </p>
              </div>
              <div className="px-3 py-1.5 rounded-lg bg-[#262a34] font-mono text-xs text-[#d0bcff] border border-[#31353f]/50 shrink-0">
                NO LABEL CROSS-CONTAMINATION
              </div>
            </div>

            {/* 4 Dataset Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Dataset 1 */}
              <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 shadow-md flex flex-col justify-between relative overflow-hidden">
                <div className="absolute top-0 right-0 px-2.5 py-0.5 rounded-bl-lg bg-[#1b2029] font-mono text-[10px] text-[#00dbe9]">
                  DS-REF: 01-WISC
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-base font-semibold text-[#eef7ff]">Wisconsin Diagnostic</span>
                    <span className="font-mono text-xs text-[#849495]">(Reduced PCA-4)</span>
                  </div>
                  <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#262a34] font-mono text-xs text-[#00dbe9] mb-3">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#00dbe9]"></span>
                    <span>Single Target: Benign / Malignant classification</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 mt-1">
                    <div className="p-2.5 rounded-lg bg-[#1b2029] border border-[#31353f]/30">
                      <span className="font-mono text-[10px] text-[#849495] block">SAMPLE POPULATION</span>
                      <span className="font-mono text-xl font-bold text-[#dfe2f0]">569</span>
                      <span className="font-mono text-[10px] text-[#849495] block">80:20 Stratified Split</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[#1b2029] border border-[#31353f]/30">
                      <span className="font-mono text-[10px] text-[#849495] block">DIMENSIONALITY</span>
                      <span className="font-mono text-xl font-bold text-[#dfe2f0]">10 → 4</span>
                      <span className="font-mono text-[10px] text-[#849495] block">Nuclear mean features</span>
                    </div>
                  </div>
                </div>
                <div className="mt-3 pt-2 border-t border-[#31353f]/30 font-mono text-xs text-[#b9cacb] flex items-center justify-between">
                  <span>Preprocessing: Normalised z-score scaling, PCA reduction for qubit mapping</span>
                  <ArrowRight className="w-4 h-4 text-[#849495]" />
                </div>
              </div>

              {/* Dataset 2 */}
              <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 shadow-md flex flex-col justify-between relative overflow-hidden">
                <div className="absolute top-0 right-0 px-2.5 py-0.5 rounded-bl-lg bg-[#1b2029] font-mono text-[10px] text-[#00dbe9]">
                  DS-REF: 02-HEART
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-base font-semibold text-[#eef7ff]">UCI Heart Disease</span>
                    <span className="font-mono text-xs text-[#849495]">(Pooled Baseline)</span>
                  </div>
                  <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#262a34] font-mono text-xs text-[#00dbe9] mb-3">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#00dbe9]"></span>
                    <span>Single Target: Presence (≥1) vs Absence (0)</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 mt-1">
                    <div className="p-2.5 rounded-lg bg-[#1b2029] border border-[#31353f]/30">
                      <span className="font-mono text-[10px] text-[#849495] block">SAMPLE POPULATION</span>
                      <span className="font-mono text-xl font-bold text-[#dfe2f0]">920</span>
                      <span className="font-mono text-[10px] text-[#849495] block">Cleveland cohort baseline</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[#1b2029] border border-[#31353f]/30">
                      <span className="font-mono text-[10px] text-[#849495] block">DIMENSIONALITY</span>
                      <span className="font-mono text-xl font-bold text-[#dfe2f0]">14 → 8</span>
                      <span className="font-mono text-[10px] text-[#849495] block">Clinical & physiological</span>
                    </div>
                  </div>
                </div>
                <div className="mt-3 pt-2 border-t border-[#31353f]/30 font-mono text-xs text-[#b9cacb] flex items-center justify-between">
                  <span>Preprocessing: Categorical encoding, one-hot continuous features</span>
                  <ArrowRight className="w-4 h-4 text-[#849495]" />
                </div>
              </div>

              {/* Dataset 3 */}
              <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 shadow-md flex flex-col justify-between relative overflow-hidden">
                <div className="absolute top-0 right-0 px-2.5 py-0.5 rounded-bl-lg bg-[#1b2029] font-mono text-[10px] text-[#00dbe9]">
                  DS-REF: 03-DIAB
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-base font-semibold text-[#eef7ff]">Pima Indians Tabular</span>
                    <span className="font-mono text-xs text-[#849495]">(Standard NIDDK)</span>
                  </div>
                  <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#262a34] font-mono text-xs text-[#00dbe9] mb-3">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#00dbe9]"></span>
                    <span>Single Target: Outcome 0 vs 1</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 mt-1">
                    <div className="p-2.5 rounded-lg bg-[#1b2029] border border-[#31353f]/30">
                      <span className="font-mono text-[10px] text-[#849495] block">SAMPLE POPULATION</span>
                      <span className="font-mono text-xl font-bold text-[#dfe2f0]">768</span>
                      <span className="font-mono text-[10px] text-[#849495] block">Stratified 80:20 holdout</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[#1b2029] border border-[#31353f]/30">
                      <span className="font-mono text-[10px] text-[#849495] block">DIMENSIONALITY</span>
                      <span className="font-mono text-xl font-bold text-[#dfe2f0]">8</span>
                      <span className="font-mono text-[10px] text-[#849495] block">Diagnostic risk metrics</span>
                    </div>
                  </div>
                </div>
                <div className="mt-3 pt-2 border-t border-[#31353f]/30 font-mono text-xs text-[#b9cacb] flex items-center justify-between">
                  <span>Preprocessing: Median imputed zeros, robust scaler quantile alignment</span>
                  <ArrowRight className="w-4 h-4 text-[#849495]" />
                </div>
              </div>

              {/* Dataset 4 */}
              <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 shadow-md flex flex-col justify-between relative overflow-hidden">
                <div className="absolute top-0 right-0 px-2.5 py-0.5 rounded-bl-lg bg-[#1b2029] font-mono text-[10px] text-[#00dbe9]">
                  DS-REF: 04-CARDIO
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-base font-semibold text-[#eef7ff]">Cardio Artery Public Table</span>
                    <span className="font-mono text-xs text-[#849495]">(Benchmark Slice)</span>
                  </div>
                  <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#262a34] font-mono text-xs text-[#00dbe9] mb-3">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#00dbe9]"></span>
                    <span>Single Target: Cardio event target 0 / 1</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 mt-1">
                    <div className="p-2.5 rounded-lg bg-[#1b2029] border border-[#31353f]/30">
                      <span className="font-mono text-[10px] text-[#849495] block">SAMPLE POPULATION</span>
                      <span className="font-mono text-xl font-bold text-[#dfe2f0]">
                        1,000 <span className="text-xs text-[#849495] font-normal">/ 70k</span>
                      </span>
                      <span className="font-mono text-[10px] text-[#849495] block">Representative slice</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[#1b2029] border border-[#31353f]/30">
                      <span className="font-mono text-[10px] text-[#849495] block">DIMENSIONALITY</span>
                      <span className="font-mono text-xl font-bold text-[#dfe2f0]">11</span>
                      <span className="font-mono text-[10px] text-[#849495] block">Physical & lifestyle tags</span>
                    </div>
                  </div>
                </div>
                <div className="mt-3 pt-2 border-t border-[#31353f]/30 font-mono text-xs text-[#b9cacb] flex items-center justify-between">
                  <span>Preprocessing: Binary thresholded, simulated NISQ statevector batching</span>
                  <ArrowRight className="w-4 h-4 text-[#849495]" />
                </div>
              </div>
            </div>
          </div>

          <div className="w-full flex items-center justify-between pt-2 border-t border-[#31353f]/40 text-[#849495] z-10 text-xs font-mono">
            <span>Feature Normalization: Scikit-Learn Pipeline</span>
            <button
              onClick={() => scrollToSlide(2)}
              className="text-[#00dbe9] hover:text-[#7df4ff] flex items-center gap-1 cursor-pointer"
            >
              <span>Explore Baselines</span>
              <ArrowDown className="w-3.5 h-3.5" />
            </button>
          </div>
        </section>

        {/* ==================== SLIDE 03 ==================== */}
        <section
          id="slide-3"
          className="w-full h-full snap-start snap-always flex flex-col justify-between py-6 md:py-8 px-4 md:px-8 max-w-6xl mx-auto relative"
        >
          <div className="flex flex-col w-full z-10 my-auto">
            <div className="flex items-center gap-2 mb-1">
              <span className="w-7 h-7 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
                <Scale className="w-4 h-4" />
              </span>
              <span className="font-mono text-xs uppercase text-[#00dbe9] tracking-widest">
                CONTROL EXPERIMENTS
              </span>
            </div>
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-3 mb-4">
              <div>
                <h2 className="text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
                  Baselines first.
                </h2>
                <p className="text-xs md:text-sm text-[#b9cacb] max-w-2xl mt-1 leading-relaxed">
                  Classical baselines establish the rigorous reference point before evaluating hybrid QML. Without competitive linear and kernel controls, quantum evaluations lack scientific validity.
                </p>
              </div>
              <div className="px-3 py-1.5 rounded-xl bg-[#262a34] border border-[#31353f]/50 flex items-center gap-2 text-xs font-mono text-[#dfe2f0] shrink-0">
                <Sliders className="w-4 h-4 text-[#00dbe9]" />
                <span>Wisconsin reduced · same split · random_state=42</span>
              </div>
            </div>

            {/* 3 Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 mb-4">
              {/* Baseline 1 */}
              <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 shadow-md relative overflow-hidden group hover:bg-[#1b2029] transition-all">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-[10px] text-[#849495] uppercase tracking-wider">BASELINE 01</span>
                  <span className="px-2 py-0.5 rounded bg-[#262a34] font-mono text-[10px] text-[#00dbe9] font-bold">
                    CHAMPION F1
                  </span>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="font-mono text-3xl md:text-4xl font-bold text-[#dfe2f0] tracking-tight">
                    0.932
                  </span>
                  <span className="font-mono text-xs text-[#00dbe9] font-bold">F1 SCORE</span>
                </div>
                <h3 className="text-base font-semibold text-[#eef7ff] mt-1">Logistic Regression</h3>
                <p className="text-xs text-[#b9cacb] mt-1 leading-relaxed">
                  Linear baseline, L2 penalty, C=1.0, liblinear solver with stratified k-fold convergence.
                </p>
                <div className="mt-3 pt-2 border-t border-[#31353f]/30 flex items-center justify-between text-[#849495] font-mono text-xs">
                  <span>AUC: 0.981</span>
                  <span className="text-[#00dbe9] font-bold">CPU: 3.2ms</span>
                </div>
              </div>

              {/* Baseline 2 */}
              <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 shadow-md relative overflow-hidden group hover:bg-[#1b2029] transition-all">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-[10px] text-[#849495] uppercase tracking-wider">BASELINE 02</span>
                  <span className="px-2 py-0.5 rounded bg-[#262a34] font-mono text-[10px] text-[#849495]">
                    ENSEMBLE
                  </span>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="font-mono text-3xl md:text-4xl font-bold text-[#dfe2f0] tracking-tight">
                    0.926
                  </span>
                  <span className="font-mono text-xs text-[#d0bcff] font-bold">F1 SCORE</span>
                </div>
                <h3 className="text-base font-semibold text-[#eef7ff] mt-1">Random Forest</h3>
                <p className="text-xs text-[#b9cacb] mt-1 leading-relaxed">
                  100 estimators, max depth 4, Gini impurity criterion, balanced sample weighting.
                </p>
                <div className="mt-3 pt-2 border-t border-[#31353f]/30 flex items-center justify-between text-[#849495] font-mono text-xs">
                  <span>AUC: 0.974</span>
                  <span className="text-[#d0bcff] font-bold">CPU: 48.6ms</span>
                </div>
              </div>

              {/* Baseline 3 */}
              <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 shadow-md relative overflow-hidden group hover:bg-[#1b2029] transition-all">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-[10px] text-[#849495] uppercase tracking-wider">BASELINE 03</span>
                  <span className="px-2 py-0.5 rounded bg-[#262a34] font-mono text-[10px] text-[#849495]">
                    CLASSICAL KERNEL
                  </span>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="font-mono text-3xl md:text-4xl font-bold text-[#dfe2f0] tracking-tight">
                    0.927
                  </span>
                  <span className="font-mono text-xs text-[#00dbe9] font-bold">F1 SCORE</span>
                </div>
                <h3 className="text-base font-semibold text-[#eef7ff] mt-1">Support Vector (RBF)</h3>
                <p className="text-xs text-[#b9cacb] mt-1 leading-relaxed">
                  Radial Basis Function kernel, C=1.0, gamma=‘scale’, exact paired control for QSVC.
                </p>
                <div className="mt-3 pt-2 border-t border-[#31353f]/30 flex items-center justify-between text-[#849495] font-mono text-xs">
                  <span>AUC: 0.979</span>
                  <span className="text-[#00dbe9] font-bold">CPU: 6.1ms</span>
                </div>
              </div>
            </div>

            {/* Diagnostic Bar Box */}
            <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs uppercase text-[#dfe2f0] tracking-wider font-semibold">
                  Linear Baseline Comprehensive Diagnostics
                </span>
                <span className="font-mono text-xs text-[#00dbe9]">TEST SET EVALUATION (N=114)</span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="space-y-1">
                  <div className="flex justify-between font-mono text-xs">
                    <span className="text-[#b9cacb]">Accuracy</span>
                    <span className="text-[#dbfcff] font-bold">0.947</span>
                  </div>
                  <div className="h-2 w-full rounded bg-[#262a34] overflow-hidden">
                    <div className="h-full bg-[#00f0ff] rounded" style={{ width: '94.7%' }}></div>
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between font-mono text-xs">
                    <span className="text-[#b9cacb]">F1-Score</span>
                    <span className="text-[#dbfcff] font-bold">0.932</span>
                  </div>
                  <div className="h-2 w-full rounded bg-[#262a34] overflow-hidden">
                    <div className="h-full bg-[#00f0ff] rounded" style={{ width: '93.2%' }}></div>
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between font-mono text-xs">
                    <span className="text-[#b9cacb]">ROC-AUC</span>
                    <span className="text-[#d0bcff] font-bold">0.981</span>
                  </div>
                  <div className="h-2 w-full rounded bg-[#262a34] overflow-hidden">
                    <div className="h-full bg-[#d0bcff] rounded" style={{ width: '98.1%' }}></div>
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between font-mono text-xs">
                    <span className="text-[#b9cacb]">Specificity</span>
                    <span className="text-[#00dbe9] font-bold">0.952</span>
                  </div>
                  <div className="h-2 w-full rounded bg-[#262a34] overflow-hidden">
                    <div className="h-full bg-[#00dbe9] rounded" style={{ width: '95.2%' }}></div>
                  </div>
                </div>
              </div>
              <div className="mt-3 p-2.5 rounded-lg bg-[#262a34]/60 border border-[#31353f]/30 flex items-start gap-2.5 text-xs text-[#b9cacb]">
                <Sparkles className="w-4 h-4 text-[#00dbe9] shrink-0 mt-0.5" />
                <p>
                  <strong className="text-[#dfe2f0]">Scientific Integrity Note:</strong> In low-dimensional tabular regimes, well-tuned linear and tree baselines demonstrate superior sample efficiency and lower variance. Hybrid QML must be evaluated against this real bar.
                </p>
              </div>
            </div>
          </div>

          <div className="w-full flex items-center justify-between pt-2 border-t border-[#31353f]/40 text-[#849495] z-10 text-xs font-mono">
            <span>K-Fold: 5-fold Stratified CV</span>
            <button
              onClick={() => scrollToSlide(3)}
              className="text-[#00dbe9] hover:text-[#7df4ff] flex items-center gap-1 cursor-pointer"
            >
              <span>Compare QML Results</span>
              <ArrowDown className="w-3.5 h-3.5" />
            </button>
          </div>
        </section>

        {/* ==================== SLIDE 04 ==================== */}
        <section
          id="slide-4"
          className="w-full h-full snap-start snap-always flex flex-col justify-between py-6 md:py-8 px-4 md:px-8 max-w-6xl mx-auto relative"
        >
          <div className="flex flex-col w-full z-10 my-auto">
            <div className="flex items-center gap-2 mb-1">
              <span className="w-7 h-7 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
                <Cpu className="w-4 h-4" />
              </span>
              <span className="font-mono text-xs uppercase text-[#00dbe9] tracking-widest">
                QISKIT AER SIMULATOR ENVIRONMENT
              </span>
            </div>
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-3 mb-4">
              <div>
                <h2 className="text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
                  Simulator, not a QPU.
                </h2>
                <p className="text-xs md:text-sm text-[#b9cacb] max-w-2xl mt-1 leading-relaxed">
                  Clear communication that this QML environment runs on Qiskit Aer Statevector simulator, with no physical quantum hardware accessed or claimed.
                </p>
              </div>
              <div className="flex items-center gap-2 font-mono text-xs text-[#00dbe9]">
                <span className="w-2 h-2 rounded-full bg-[#00dbe9] shadow-[0_0_8px_#00dbe9]"></span>
                <span>AER STATEVECTOR · 0 NOISE MODEL</span>
              </div>
            </div>

            {/* Split View */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch">
              {/* Left Matrix: 7 cols */}
              <div className="lg:col-span-7 p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 shadow-md flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-mono text-xs text-[#849495] uppercase tracking-wider">
                      Model Benchmarking Matrix
                    </span>
                    <span className="font-mono text-xs text-[#849495]">Target: Malignant / Benign</span>
                  </div>
                  <div className="space-y-2">
                    {/* Row 1: Classical SVM */}
                    <div className="p-2.5 rounded-lg bg-[#1b2029] border border-[#31353f]/40 flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <span className="w-2 h-2 rounded-full bg-[#849495]"></span>
                        <div>
                          <span className="text-sm font-semibold text-[#eef7ff]">Classical SVM (RBF)</span>
                          <span className="font-mono text-[10px] text-[#849495] block">Paired Classical Control</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-4 text-right">
                        <div>
                          <span className="font-mono text-[9px] text-[#849495] block">ACCURACY</span>
                          <span className="font-mono text-base font-bold text-[#dfe2f0]">0.938</span>
                        </div>
                        <div>
                          <span className="font-mono text-[9px] text-[#00dbe9] block">F1 SCORE</span>
                          <span className="font-mono text-base font-bold text-[#dbfcff]">0.927</span>
                        </div>
                      </div>
                    </div>

                    {/* Row 2: QSVC */}
                    <div className="p-2.5 rounded-lg bg-[#262a34] border border-[#00f0ff]/40 flex items-center justify-between relative overflow-hidden">
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#00f0ff]"></div>
                      <div className="flex items-center gap-2.5 pl-2">
                        <span className="w-2 h-2 rounded-full bg-[#00dbe9] shadow-[0_0_6px_#00dbe9]"></span>
                        <div>
                          <div className="flex items-center gap-1.5">
                            <span className="text-sm font-bold text-[#dbfcff]">QSVC (Quantum Kernel)</span>
                            <span className="px-1.5 py-0.2 rounded bg-[#31353f] font-mono text-[9px] text-[#00dbe9]">
                              ZZFeatureMap
                            </span>
                          </div>
                          <span className="font-mono text-[10px] text-[#b9cacb] block">
                            Statevector fidelity inner product
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-4 text-right">
                        <div>
                          <span className="font-mono text-[9px] text-[#849495] block">ACCURACY</span>
                          <span className="font-mono text-base font-bold text-[#dfe2f0]">0.921</span>
                        </div>
                        <div>
                          <span className="font-mono text-[9px] text-[#00dbe9] block">F1 SCORE</span>
                          <span className="font-mono text-base font-bold text-[#00f0ff]">0.909</span>
                        </div>
                      </div>
                    </div>

                    {/* Row 3: VQC */}
                    <div className="p-2.5 rounded-lg bg-[#1b2029] border border-[#31353f]/40 flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <span className="w-2 h-2 rounded-full bg-[#d0bcff]"></span>
                        <div>
                          <div className="flex items-center gap-1.5">
                            <span className="text-sm font-semibold text-[#eef7ff]">VQC (Variational PQC)</span>
                            <span className="px-1.5 py-0.2 rounded bg-[#31353f] font-mono text-[9px] text-[#d0bcff]">
                              RealAmplitudes
                            </span>
                          </div>
                          <span className="font-mono text-[10px] text-[#849495] block">
                            COBYLA Optimizer · 4 Layers · 16 Params
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-4 text-right">
                        <div>
                          <span className="font-mono text-[9px] text-[#849495] block">ACCURACY</span>
                          <span className="font-mono text-base font-bold text-[#dfe2f0]">0.877</span>
                        </div>
                        <div>
                          <span className="font-mono text-[9px] text-[#d0bcff] block">F1 SCORE</span>
                          <span className="font-mono text-base font-bold text-[#d0bcff]">0.865</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* McNemar Callout */}
                <div className="mt-3 p-2.5 rounded-lg bg-[#262a34]/70 border border-[#31353f]/50 flex items-start gap-2.5">
                  <Scale className="w-4 h-4 text-[#d0bcff] shrink-0 mt-0.5" />
                  <div>
                    <span className="font-mono text-[10px] text-[#d0bcff] uppercase tracking-wider block font-bold">
                      Null-Hypothesis Significance Test
                    </span>
                    <p className="font-mono text-xs text-[#dfe2f0] mt-0.5">
                      McNemar test: <strong className="text-[#00dbe9]">p = 1.000</strong> (QSVC vs Classical RBF) — No statistically significant quantum advantage demonstrated on this table.
                    </p>
                  </div>
                </div>
              </div>

              {/* Right Circuit Schematic: 5 cols */}
              <div className="lg:col-span-5 p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 shadow-md flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-xs text-[#849495] uppercase tracking-wider">
                      Ansatz Structure (4-Qubit Circuit)
                    </span>
                    <span className="font-mono text-xs text-[#00dbe9]">Depth: 18 Gates</span>
                  </div>

                  {/* SVG Circuit Diagram */}
                  <div className="w-full bg-[#0a0e17] p-2.5 rounded-xl overflow-x-auto border border-[#31353f]/40">
                    <svg
                      className="w-full h-auto text-[#dbfcff] font-mono"
                      fill="none"
                      viewBox="0 0 380 180"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      {/* Wires */}
                      <text className="fill-[#00dbe9] text-[11px] font-bold" x="10" y="34">|q₀⟩</text>
                      <line stroke="#334155" strokeWidth="1.5" x1="45" x2="370" y1="30" y2="30"></line>
                      <text className="fill-[#00dbe9] text-[11px] font-bold" x="10" y="74">|q₁⟩</text>
                      <line stroke="#334155" strokeWidth="1.5" x1="45" x2="370" y1="70" y2="70"></line>
                      <text className="fill-[#00dbe9] text-[11px] font-bold" x="10" y="114">|q₂⟩</text>
                      <line stroke="#334155" strokeWidth="1.5" x1="45" x2="370" y1="110" y2="110"></line>
                      <text className="fill-[#00dbe9] text-[11px] font-bold" x="10" y="154">|q₃⟩</text>
                      <line stroke="#334155" strokeWidth="1.5" x1="45" x2="370" y1="150" y2="150"></line>

                      {/* Hadamard Column */}
                      <g>
                        <rect fill="#0f172a" height="24" rx="3" stroke="#00dbe9" strokeWidth="1" width="24" x="55" y="18"></rect>
                        <text className="fill-[#00dbe9] text-[10px] font-bold" x="63" y="34">H</text>
                        <rect fill="#0f172a" height="24" rx="3" stroke="#00dbe9" strokeWidth="1" width="24" x="55" y="58"></rect>
                        <text className="fill-[#00dbe9] text-[10px] font-bold" x="63" y="74">H</text>
                        <rect fill="#0f172a" height="24" rx="3" stroke="#00dbe9" strokeWidth="1" width="24" x="55" y="98"></rect>
                        <text className="fill-[#00dbe9] text-[10px] font-bold" x="63" y="114">H</text>
                        <rect fill="#0f172a" height="24" rx="3" stroke="#00dbe9" strokeWidth="1" width="24" x="55" y="138"></rect>
                        <text className="fill-[#00dbe9] text-[10px] font-bold" x="63" y="154">H</text>
                      </g>

                      {/* Angle Embedding Rz */}
                      <g>
                        <rect fill="#1b2029" height="24" rx="3" stroke="#7df4ff" strokeWidth="1" width="34" x="95" y="18"></rect>
                        <text className="fill-[#dbfcff] text-[9px]" x="100" y="34">Rz(x₀)</text>
                        <rect fill="#1b2029" height="24" rx="3" stroke="#7df4ff" strokeWidth="1" width="34" x="95" y="58"></rect>
                        <text className="fill-[#dbfcff] text-[9px]" x="100" y="74">Rz(x₁)</text>
                        <rect fill="#1b2029" height="24" rx="3" stroke="#7df4ff" strokeWidth="1" width="34" x="95" y="98"></rect>
                        <text className="fill-[#dbfcff] text-[9px]" x="100" y="114">Rz(x₂)</text>
                        <rect fill="#1b2029" height="24" rx="3" stroke="#7df4ff" strokeWidth="1" width="34" x="95" y="138"></rect>
                        <text className="fill-[#dbfcff] text-[9px]" x="100" y="154">Rz(x₃)</text>
                      </g>

                      {/* CNOT ladder */}
                      <g>
                        <circle cx="150" cy="30" fill="#d0bcff" r="3.5"></circle>
                        <line stroke="#d0bcff" strokeWidth="1.5" x1="150" x2="150" y1="30" y2="70"></line>
                        <circle cx="150" cy="70" fill="#070b13" r="6" stroke="#d0bcff" strokeWidth="1.5"></circle>
                        <line stroke="#d0bcff" strokeWidth="1.5" x1="145" x2="155" y1="70" y2="70"></line>

                        <circle cx="175" cy="70" fill="#d0bcff" r="3.5"></circle>
                        <line stroke="#d0bcff" strokeWidth="1.5" x1="175" x2="175" y1="70" y2="110"></line>
                        <circle cx="175" cy="110" fill="#070b13" r="6" stroke="#d0bcff" strokeWidth="1.5"></circle>
                        <line stroke="#d0bcff" strokeWidth="1.5" x1="170" x2="180" y1="110" y2="110"></line>

                        <circle cx="200" cy="110" fill="#d0bcff" r="3.5"></circle>
                        <line stroke="#d0bcff" strokeWidth="1.5" x1="200" x2="200" y1="110" y2="150"></line>
                        <circle cx="200" cy="150" fill="#070b13" r="6" stroke="#d0bcff" strokeWidth="1.5"></circle>
                        <line stroke="#d0bcff" strokeWidth="1.5" x1="195" x2="205" y1="150" y2="150"></line>
                      </g>

                      {/* Variational Ry */}
                      <g>
                        <rect fill="#262a34" height="24" rx="3" stroke="#d0bcff" strokeWidth="1" width="34" x="225" y="18"></rect>
                        <text className="fill-[#d0bcff] text-[9px]" x="230" y="34">Ry(θ₀)</text>
                        <rect fill="#262a34" height="24" rx="3" stroke="#d0bcff" strokeWidth="1" width="34" x="225" y="58"></rect>
                        <text className="fill-[#d0bcff] text-[9px]" x="230" y="74">Ry(θ₁)</text>
                        <rect fill="#262a34" height="24" rx="3" stroke="#d0bcff" strokeWidth="1" width="34" x="225" y="98"></rect>
                        <text className="fill-[#d0bcff] text-[9px]" x="230" y="114">Ry(θ₂)</text>
                        <rect fill="#262a34" height="24" rx="3" stroke="#d0bcff" strokeWidth="1" width="34" x="225" y="138"></rect>
                        <text className="fill-[#d0bcff] text-[9px]" x="230" y="154">Ry(θ₃)</text>
                      </g>

                      {/* Measurement */}
                      <g>
                        <rect fill="#0f172a" height="24" rx="3" stroke="#849495" strokeWidth="1" width="26" x="330" y="18"></rect>
                        <path d="M336 33 A7 7 0 0 1 350 33 M343 33 L347 24" fill="none" stroke="#849495" strokeWidth="1.2"></path>
                        <rect fill="#0f172a" height="24" rx="3" stroke="#849495" strokeWidth="1" width="26" x="330" y="58"></rect>
                        <path d="M336 73 A7 7 0 0 1 350 73 M343 73 L347 64" fill="none" stroke="#849495" strokeWidth="1.2"></path>
                        <rect fill="#0f172a" height="24" rx="3" stroke="#849495" strokeWidth="1" width="26" x="330" y="98"></rect>
                        <path d="M336 113 A7 7 0 0 1 350 113 M343 113 L347 104" fill="none" stroke="#849495" strokeWidth="1.2"></path>
                        <rect fill="#0f172a" height="24" rx="3" stroke="#849495" strokeWidth="1" width="26" x="330" y="138"></rect>
                        <path d="M336 153 A7 7 0 0 1 350 153 M343 153 L347 144" fill="none" stroke="#849495" strokeWidth="1.2"></path>
                      </g>
                    </svg>
                  </div>
                  <div className="mt-2 flex items-center justify-between text-[#849495] font-mono text-[10px]">
                    <span>Entangler: Circular CNOT</span>
                    <span>Measurement: Computational Basis</span>
                  </div>
                </div>

                <div className="mt-4 pt-2 border-t border-[#31353f]/30 flex items-center gap-2">
                  <button
                    onClick={() => onNavigate('qml-studio')}
                    className="flex-1 py-2.5 rounded-lg bg-[#00f0ff] text-[#00363a] font-bold text-xs hover:bg-[#7df4ff] transition-all text-center"
                  >
                    Open QML Studio
                  </button>
                  <button
                    onClick={() => onNavigate('simulator-demo')}
                    className="px-4 py-2.5 rounded-lg bg-[#262a34] text-[#dfe2f0] font-semibold text-xs hover:bg-[#353944] border border-[#31353f] transition-all text-center flex items-center gap-1"
                  >
                    <span>Try Demo</span>
                    <Play className="w-3.5 h-3.5 text-[#00dbe9]" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="w-full flex items-center justify-between pt-2 border-t border-[#31353f]/40 text-[#849495] z-10 text-xs font-mono">
            <span>Reproducibility Seed: 0x4B3A8F · Aer v0.13</span>
            <button
              onClick={() => scrollToSlide(0)}
              className="text-[#00dbe9] hover:text-[#7df4ff] flex items-center gap-1 cursor-pointer"
            >
              <span>Back to top [01]</span>
              <ChevronUp className="w-3.5 h-3.5" />
            </button>
          </div>
        </section>
      </div>
    </div>
  );
};
