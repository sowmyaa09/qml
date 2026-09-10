import React, { useEffect, useRef } from 'react';
import {
  BookOpen,
  CheckCircle2,
  Scale,
  Cpu,
  Layers,
  Activity,
  ArrowDown,
  Play,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { TabType } from '../types';

interface StoryViewProps {
  onNavigate: (tab: TabType) => void;
}

function Reveal({
  children,
  delayMs = 0,
  className = '',
}: {
  children: React.ReactNode;
  delayMs?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`story-reveal ${className}`}
      style={{ transitionDelay: `${delayMs}ms` }}
    >
      {children}
    </div>
  );
}

export const StoryView: React.FC<StoryViewProps> = ({ onNavigate }) => {
  return (
    <div className="w-full max-w-6xl mx-auto px-4 md:px-8 pb-24">
      <div className="pointer-events-none fixed right-5 bottom-8 z-30 hidden md:flex flex-col items-center gap-1 text-[#849495]">
        <ArrowDown className="w-4 h-4 animate-bounce text-[#00dbe9]" />
        <span className="font-mono text-[9px] tracking-widest uppercase">Scroll</span>
      </div>

      <section className="relative min-h-[70vh] flex flex-col justify-center py-8">
        <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-25">
          <div className="absolute -top-24 left-1/4 w-96 h-96 rounded-full bg-[#00f0ff]/10 blur-3xl" />
          <div className="absolute top-1/3 right-1/4 w-80 h-80 rounded-full bg-[#571bc1]/20 blur-3xl" />
        </div>

        <Reveal>
          <div className="flex items-center gap-2 mb-3">
            <span className="w-7 h-7 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
              <BookOpen className="w-4 h-4" />
            </span>
            <span className="font-mono text-xs uppercase text-[#00dbe9] tracking-widest">
              SIH 2026 SIH26139 · Q-Care Detect / LAKSHYA
            </span>
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold text-[#dbfcff] tracking-widest drop-shadow-[0_0_24px_rgba(0,219,233,0.35)]">
            LAKSHYA
          </h1>
          <p className="text-lg md:text-2xl text-[#b9cacb] font-medium tracking-tight mt-2 max-w-3xl">
            Hybrid quantum–classical research on public biomedical tables. Scroll this page for the full pitch.
          </p>
        </Reveal>

        <Reveal delayMs={80}>
          <p className="mt-4 text-sm text-[#9a3412] font-medium max-w-3xl">
            Research risk classification — not for clinical use. Not a medical device. Not a diagnosis.
          </p>
        </Reveal>

        <Reveal delayMs={120}>
          <div className="mt-6 p-4 rounded-xl bg-[#0a0e17]/90 border border-[#31353f]/60 relative overflow-hidden">
            <div className="absolute inset-y-0 left-0 w-1.5 bg-gradient-to-b from-[#00f0ff] to-[#d0bcff]" />
            <div className="pl-4 flex items-start gap-3">
              <CheckCircle2 className="w-6 h-6 text-[#00dbe9] shrink-0 mt-0.5" />
              <div>
                <span className="font-mono text-xs uppercase text-[#d0bcff] tracking-wider font-semibold">
                  What to tell judges first
                </span>
                <p className="text-base md:text-lg text-[#dfe2f0] font-semibold mt-1">
                  On Wisconsin, logistic regression beat VQC/QSVC on F1. QSVC matched RBF SVM (McNemar p = 1.000). Pitch cost, not quantum accuracy.
                </p>
              </div>
            </div>
          </div>
        </Reveal>

        <Reveal delayMs={160}>
          <p className="mt-6 font-mono text-xs text-[#849495] flex items-center gap-2">
            <ArrowDown className="w-4 h-4 text-[#00dbe9]" />
            Keep scrolling — one continuous story
          </p>
        </Reveal>
      </section>

      <Reveal>
        <h2 className="text-2xl md:text-3xl font-bold text-[#dbfcff] mt-4 mb-3">What this is</h2>
        <p className="text-sm md:text-base text-[#b9cacb] leading-relaxed max-w-3xl">
          Classical code loads a public table, splits 80/20 (seed 42), scales, and selects about 4–8 features. A small Qiskit Aer <strong className="text-[#dfe2f0]">simulator</strong> circuit (not a hospital QPU) then runs QSVC or VQC on those numbers. Each experiment is <strong className="text-[#dfe2f0]">one table, one label</strong>.
        </p>
      </Reveal>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mt-6">
        {[
          {
            icon: Scale,
            title: 'Honest baseline',
            body: 'LR, random forest, and RBF SVM on the same split and the same k columns as QSVC.',
          },
          {
            icon: Cpu,
            title: 'Hybrid, not pure QML',
            body: 'Near-term circuits cannot eat 30 raw FNA columns. SelectKBest keeps ~6 qubits.',
          },
          {
            icon: Layers,
            title: 'No fused diagnosis',
            body: 'Wisconsin is never mixed with heart or diabetes into “what disease do I have?”',
          },
        ].map((card, i) => (
          <Reveal key={card.title} delayMs={i * 90}>
            <div className="h-full p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40">
              <card.icon className="w-5 h-5 text-[#00dbe9] mb-2" />
              <h3 className="text-sm font-semibold text-[#dbfcff]">{card.title}</h3>
              <p className="text-xs text-[#b9cacb] mt-1 leading-relaxed">{card.body}</p>
            </div>
          </Reveal>
        ))}
      </div>

      <Reveal>
        <h2 className="text-2xl md:text-3xl font-bold text-[#dbfcff] mt-16 mb-2">One table, one label</h2>
        <p className="text-sm text-[#b9cacb] max-w-3xl leading-relaxed mb-6">
          Public teaching sets only. Scores are research rankings on that table’s positive class — not a personal diagnosis.
        </p>
      </Reveal>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          {
            tag: '01-WISC',
            name: 'Wisconsin Diagnostic (reduced)',
            target: 'Malignant class on this FNA benchmark only',
            n: '569',
            dim: '30 → 6 selected',
            note: 'sklearn / UCI WDBC. QML v1 uses these 6 columns.',
          },
          {
            tag: '02-HEART',
            name: 'UCI heart (4 cohorts pooled)',
            target: 'num > 0 on these UCI files only',
            n: '918',
            dim: '14 attributes',
            note: 'Cleveland + Hungary + Switzerland + VA. Not the leaky Kaggle copy.',
          },
          {
            tag: '03-PIMA',
            name: 'Pima Indians diabetes',
            target: 'Outcome=1 on this UCI table only',
            n: '768',
            dim: '8 fields',
            note: 'Separate from the large BRFSS diabetes survey.',
          },
          {
            tag: '04-COIMBRA',
            name: 'Breast Cancer Coimbra',
            target: 'Patient class on blood-marker table',
            n: 'UCI 451',
            dim: '9 fields',
            note: 'Second hybrid table. Not Wisconsin FNA.',
          },
        ].map((ds, i) => (
          <Reveal key={ds.tag} delayMs={i * 70}>
            <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 relative">
              <span className="absolute top-0 right-0 px-2.5 py-0.5 rounded-bl-lg bg-[#1b2029] font-mono text-[10px] text-[#00dbe9]">
                {ds.tag}
              </span>
              <h3 className="text-base font-semibold text-[#eef7ff] pr-24">{ds.name}</h3>
              <p className="font-mono text-xs text-[#00dbe9] mt-1">{ds.target}</p>
              <div className="grid grid-cols-2 gap-2 mt-3">
                <div className="p-2.5 rounded-lg bg-[#1b2029]">
                  <span className="font-mono text-[10px] text-[#849495] block">ROWS</span>
                  <span className="font-mono text-xl font-bold text-[#dfe2f0]">{ds.n}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#1b2029]">
                  <span className="font-mono text-[10px] text-[#849495] block">COLUMNS</span>
                  <span className="font-mono text-xl font-bold text-[#dfe2f0]">{ds.dim}</span>
                </div>
              </div>
              <p className="mt-3 text-xs text-[#b9cacb] flex items-start gap-1">
                <ArrowRight className="w-3.5 h-3.5 shrink-0 mt-0.5 text-[#849495]" />
                {ds.note}
              </p>
            </div>
          </Reveal>
        ))}
      </div>

      <Reveal>
        <h2 className="text-2xl md:text-3xl font-bold text-[#dbfcff] mt-16 mb-2">Classical first</h2>
        <p className="text-sm text-[#b9cacb] max-w-3xl leading-relaxed mb-6">
          Wisconsin reduced, same split, random_state=42. These numbers are the bar hybrid QML has to beat.
        </p>
      </Reveal>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        {[
          { name: 'Logistic Regression', f1: '0.932', extra: 'Champion F1 · milliseconds', tag: 'LINEAR' },
          { name: 'Random Forest', f1: '0.926', extra: 'Tree ensemble', tag: 'ENSEMBLE' },
          { name: 'RBF SVM', f1: '0.927', extra: 'Honest kernel control for QSVC', tag: 'KERNEL' },
        ].map((m, i) => (
          <Reveal key={m.name} delayMs={i * 80}>
            <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40">
              <span className="font-mono text-[10px] text-[#00dbe9]">{m.tag}</span>
              <div className="font-mono text-4xl font-bold text-[#dfe2f0] mt-1">{m.f1}</div>
              <div className="text-xs text-[#00dbe9] font-bold">F1</div>
              <h3 className="text-base font-semibold text-[#eef7ff] mt-2">{m.name}</h3>
              <p className="text-xs text-[#b9cacb] mt-1">{m.extra}</p>
            </div>
          </Reveal>
        ))}
      </div>

      <Reveal delayMs={100}>
        <div className="mt-4 p-3 rounded-lg bg-[#262a34]/60 border border-[#31353f]/30 flex items-start gap-2.5 text-xs text-[#b9cacb]">
          <Sparkles className="w-4 h-4 text-[#00dbe9] shrink-0 mt-0.5" />
          <p>
            <strong className="text-[#dfe2f0]">Integrity:</strong> well-tuned linear and kernel models are strong on this small table. A quantum demo that skips this comparison is not science.
          </p>
        </div>
      </Reveal>

      <Reveal>
        <h2 className="text-2xl md:text-3xl font-bold text-[#dbfcff] mt-16 mb-2">Hybrid QML on a simulator</h2>
        <p className="text-sm text-[#b9cacb] max-w-3xl leading-relaxed mb-6">
          ZZFeatureMap + FidelityStatevectorKernel for QSVC; RealAmplitudes + COBYLA for VQC. Aer statevector — no physical QPU in this delivery.
        </p>
      </Reveal>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <Reveal className="lg:col-span-7">
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 space-y-2">
            {[
              { name: 'RBF SVM (same k)', f1: '0.927', hi: false },
              { name: 'QSVC (quantum kernel)', f1: '0.909', hi: true },
              { name: 'VQC (variational)', f1: 'worse / slower', hi: false },
            ].map((row) => (
              <div
                key={row.name}
                className={`p-2.5 rounded-lg flex items-center justify-between ${
                  row.hi
                    ? 'bg-[#262a34] border border-[#00f0ff]/40'
                    : 'bg-[#1b2029] border border-[#31353f]/40'
                }`}
              >
                <span className="text-sm font-semibold text-[#eef7ff]">{row.name}</span>
                <span className="font-mono text-base font-bold text-[#00f0ff]">{row.f1}</span>
              </div>
            ))}
            <div className="p-2.5 rounded-lg bg-[#262a34]/70 flex items-start gap-2.5 mt-2">
              <Scale className="w-4 h-4 text-[#d0bcff] shrink-0 mt-0.5" />
              <p className="font-mono text-xs text-[#dfe2f0]">
                McNemar <strong className="text-[#00dbe9]">p = 1.000</strong> (QSVC vs RBF) — indistinguishable on this split. Not a quantum win.
              </p>
            </div>
          </div>
        </Reveal>
        <Reveal delayMs={100} className="lg:col-span-5">
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 h-full">
            <div className="flex items-center gap-2 mb-2 font-mono text-xs text-[#00dbe9]">
              <Activity className="w-3.5 h-3.5" />
              Aer statevector · ~6 qubits
            </div>
            <p className="text-xs text-[#b9cacb] leading-relaxed">
              Feature map encodes the six selected FNA numbers as rotation angles and ZZ entangling gates. The SVM then uses state overlap as a kernel. That is hybrid: classical SVM, quantum-inspired kernel, classical computer simulating the circuit.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => onNavigate('qml-studio')}
                className="px-4 py-2 rounded-lg bg-[#00f0ff] text-[#00363a] font-bold text-xs hover:bg-[#7df4ff]"
              >
                Open QML Studio
              </button>
              <button
                type="button"
                onClick={() => onNavigate('cost-latency')}
                className="px-4 py-2 rounded-lg bg-[#262a34] border border-[#31353f] text-xs font-semibold text-[#dfe2f0]"
              >
                Cost vs F1
              </button>
            </div>
          </div>
        </Reveal>
      </div>

      <Reveal>
        <h2 className="text-2xl md:text-3xl font-bold text-[#dbfcff] mt-16 mb-2">Live demo next</h2>
        <p className="text-sm text-[#b9cacb] max-w-3xl leading-relaxed mb-4">
          Paste a record scores the six Wisconsin-reduced columns. Upload{' '}
          <span className="font-mono text-[#00dbe9]">demo/synthetic_wisconsin_reduced_demo.pdf</span> or the high-range sample. Name and date of birth are labels only. Not a symptom checker.
        </p>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => onNavigate('paste-a-record')}
            className="px-5 py-2.5 rounded-lg bg-[#00f0ff] text-[#00363a] font-bold text-sm hover:bg-[#7df4ff] flex items-center gap-2"
          >
            Paste a record
            <Play className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => onNavigate('data')}
            className="px-5 py-2.5 rounded-lg bg-[#262a34] border border-[#31353f] text-sm font-semibold text-[#dfe2f0]"
          >
            Data library
          </button>
        </div>
      </Reveal>
    </div>
  );
};
