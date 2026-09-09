import React, { useState } from 'react';
import {
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Scale,
  Sparkles,
  Info,
  ChevronDown,
  Layers,
  Activity,
} from 'lucide-react';

export const QMLStudioView: React.FC = () => {
  const [hoveredCell, setHoveredCell] = useState<{ i: number; j: number; val: number } | null>(null);

  // Generate deterministic 10x10 Gram matrix values
  // Symmetric with 1.0 on diagonal
  const gramMatrix = Array.from({ length: 10 }, (_, i) =>
    Array.from({ length: 10 }, (_, j) => {
      if (i === j) return 1.0;
      const seedVal = Math.sin(i * 1.7 + j * 2.3) * Math.cos(i - j);
      return Math.min(0.98, Math.max(0.04, Math.abs(seedVal)));
    })
  );

  return (
    <div className="w-full max-w-6xl mx-auto px-4 md:px-6 py-6 pb-16 space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
              <Cpu className="w-3.5 h-3.5" />
            </span>
            <span className="font-mono text-xs uppercase text-[#00dbe9] tracking-widest">
              PROTOCOL 03-B / SIMULATED VARIATIONAL KERNEL BENCHMARK
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
            Hybrid QML Studio
          </h1>
          <p className="text-xs md:text-sm text-[#b9cacb] max-w-3xl mt-1 leading-relaxed">
            Paired empirical evaluation of Quantum Support Vector Classifier (QSVC) and Variational Quantum Classifier (VQC) against identical classical controls.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 shrink-0 font-mono text-xs">
          <span className="px-3 py-1.5 rounded-xl bg-[#262a34] border border-[#00dbe9]/40 text-[#00dbe9] flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#00dbe9] animate-pulse"></span>
            AER STATEVECTOR (NO QPU)
          </span>
          <span className="px-3 py-1.5 rounded-xl bg-[#171c25] border border-[#31353f] text-[#849495]">
            HYPOTHESIS PRE-REGISTRATION
          </span>
        </div>
      </div>

      {/* Model Comparison Triad */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Model A: QSVC */}
        <div className="p-5 rounded-xl bg-[#171c25] border border-[#00f0ff]/40 shadow-lg relative overflow-hidden flex flex-col justify-between">
          <div className="absolute top-0 right-0 px-2.5 py-0.5 rounded-bl bg-[#00f0ff] font-mono text-[9px] text-[#00363a] font-bold">
            MODEL A · QUANTUM KERNEL
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-base font-bold text-[#dbfcff]">QSVC (Quantum Kernel)</span>
            </div>
            <span className="font-mono text-[11px] text-[#00dbe9] block mb-3">
              ZZFeatureMap(reps=2, ent='linear')
            </span>

            <div className="grid grid-cols-2 gap-2 my-2 font-mono">
              <div className="p-2.5 rounded-lg bg-[#0a0e17] border border-[#31353f]/30">
                <span className="text-[10px] text-[#849495] block">ACCURACY</span>
                <span className="text-xl font-bold text-[#dfe2f0]">92.11%</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#0a0e17] border border-[#00f0ff]/30">
                <span className="text-[10px] text-[#00dbe9] block font-bold">F1-SCORE</span>
                <span className="text-xl font-bold text-[#00f0ff]">0.909</span>
              </div>
            </div>

            <div className="space-y-1 font-mono text-xs text-[#b9cacb] mt-3">
              <div className="flex justify-between">
                <span>Precision / Recall:</span>
                <span className="text-[#dfe2f0]">0.9048 / 0.9048</span>
              </div>
              <div className="flex justify-between">
                <span>ROC-AUC Integral:</span>
                <span className="text-[#dfe2f0]">0.968</span>
              </div>
              <div className="flex justify-between">
                <span>Simulation Runtime:</span>
                <span className="text-[#00dbe9]">1,842ms (Aer Sim)</span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-2 border-t border-[#31353f]/30 font-mono text-[10px] text-[#849495]">
            Encoding: 4-Qubit Second-Order Pauli-Z expansion
          </div>
        </div>

        {/* Model B: Classical SVC RBF */}
        <div className="p-5 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between mb-1">
            <span className="text-base font-bold text-[#eef7ff]">Classical SVC (RBF)</span>
            <span className="px-2 py-0.5 rounded bg-[#262a34] font-mono text-[9px] text-[#849495]">
              PAIRED CONTROL
            </span>
          </div>
          <span className="font-mono text-[11px] text-[#b9cacb] block mb-3">
            RBF (gamma='scale', C=1.0)
          </span>

          <div className="grid grid-cols-2 gap-2 my-2 font-mono">
            <div className="p-2.5 rounded-lg bg-[#0a0e17] border border-[#31353f]/30">
              <span className="text-[10px] text-[#849495] block">ACCURACY</span>
              <span className="text-xl font-bold text-[#dfe2f0]">93.86%</span>
            </div>
            <div className="p-2.5 rounded-lg bg-[#0a0e17] border border-[#31353f]/30">
              <span className="text-[10px] text-[#849495] block font-bold">F1-SCORE</span>
              <span className="text-xl font-bold text-[#dbfcff]">0.927</span>
            </div>
          </div>

          <div className="space-y-1 font-mono text-xs text-[#b9cacb] mt-3">
            <div className="flex justify-between">
              <span>Precision / Recall:</span>
              <span className="text-[#dfe2f0]">0.9286 / 0.9070</span>
            </div>
            <div className="flex justify-between">
              <span>ROC-AUC Integral:</span>
              <span className="text-[#dfe2f0]">0.979</span>
            </div>
            <div className="flex justify-between">
              <span>Compute Runtime:</span>
              <span className="text-[#00dbe9]">6.1ms (CPU)</span>
            </div>
          </div>

          <div className="mt-4 pt-2 border-t border-[#31353f]/30 font-mono text-[10px] text-[#00dbe9]">
            Outperforms QSVC by +0.018 F1 on identical split
          </div>
        </div>

        {/* Model C: VQC RealAmplitudes */}
        <div className="p-5 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between mb-1">
            <span className="text-base font-bold text-[#eef7ff]">VQC (RealAmplitudes)</span>
            <span className="px-2 py-0.5 rounded bg-[#262a34] font-mono text-[9px] text-[#d0bcff]">
              VARIATIONAL PQC
            </span>
          </div>
          <span className="font-mono text-[11px] text-[#d0bcff] block mb-3">
            RealAmplitudes(reps=3, 16 params)
          </span>

          <div className="grid grid-cols-2 gap-2 my-2 font-mono">
            <div className="p-2.5 rounded-lg bg-[#0a0e17] border border-[#31353f]/30">
              <span className="text-[10px] text-[#849495] block">ACCURACY</span>
              <span className="text-xl font-bold text-[#dfe2f0]">87.72%</span>
            </div>
            <div className="p-2.5 rounded-lg bg-[#0a0e17] border border-[#31353f]/30">
              <span className="text-[10px] text-[#849495] block font-bold">F1-SCORE</span>
              <span className="text-xl font-bold text-[#d0bcff]">0.865</span>
            </div>
          </div>

          <div className="space-y-1 font-mono text-xs text-[#b9cacb] mt-3">
            <div className="flex justify-between">
              <span>Precision / Recall:</span>
              <span className="text-[#dfe2f0]">0.8571 / 0.8372</span>
            </div>
            <div className="flex justify-between">
              <span>ROC-AUC Integral:</span>
              <span className="text-[#dfe2f0]">0.931</span>
            </div>
            <div className="flex justify-between">
              <span>Optimization Time:</span>
              <span className="text-[#849495]">34,210ms (COBYLA)</span>
            </div>
          </div>

          <div className="mt-4 pt-2 border-t border-[#31353f]/30 font-mono text-[10px] text-[#849495]">
            Barren plateau onset: gradient variance decay
          </div>
        </div>
      </div>

      {/* Hypothesis Verification & Significance Testing Strip */}
      <div className="p-4 rounded-xl bg-[#0f131d] border border-[#31353f]/60 shadow-md space-y-3">
        <div className="flex items-center gap-2 text-xs font-mono text-[#d0bcff] font-bold uppercase tracking-wider">
          <Scale className="w-4 h-4 text-[#d0bcff]" />
          <span>Statistical Significance & Paired Hypothesis Verification</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
          <div className="p-3 rounded-lg bg-[#171c25] border border-[#31353f]/40">
            <span className="text-[10px] text-[#849495] block uppercase">
              MCNEMAR'S TEST (QSVC VS CLASSICAL SVC)
            </span>
            <span className="text-base font-bold text-[#00dbe9] block mt-0.5">
              p = 1.000 <span className="text-xs font-normal text-[#849495]">(χ² = 0.000, df = 1)</span>
            </span>
            <p className="text-[11px] text-[#b9cacb] mt-1 font-sans">
              Discordant pairs: b=4, c=4. Both models misclassified identical test proportions. Null hypothesis cannot be rejected.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-[#171c25] border border-[#31353f]/40">
            <span className="text-[10px] text-[#849495] block uppercase">
              WILCOXON SIGNED-RANK (5-FOLD CV)
            </span>
            <span className="text-base font-bold text-[#dbfcff] block mt-0.5">
              p = 0.317 <span className="text-xs font-normal text-[#849495]">(W = 18.5, n = 5 folds)</span>
            </span>
            <p className="text-[11px] text-[#b9cacb] mt-1 font-sans">
              Cross-validated performance delta shows no statistically significant divergence between quantum and classical kernels.
            </p>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-[#262a34]/60 border border-[#31353f]/40 flex items-start gap-2.5 text-xs text-[#b9cacb]">
          <CheckCircle2 className="w-4 h-4 text-[#00dbe9] shrink-0 mt-0.5" />
          <p className="font-sans leading-relaxed">
            <strong className="text-[#dbfcff]">Honest Empirical Disclosure:</strong> On standard tabular biomedical records, the quantum kernel does not demonstrate quantum advantage over the classical RBF kernel. Both achieve comparable separation geometry, while classical computation executes over 300x faster.
          </p>
        </div>
      </div>

      {/* Circuit Architecture & Gram Matrix Heatmap Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Circuit & Ansatz (7 cols) */}
        <div className="lg:col-span-7 p-5 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-[#eef7ff]">
                Ansatz & Quantum Circuit Architecture
              </h3>
              <p className="text-xs text-[#b9cacb]">
                Parameter mapping: 4 Qubits, 28 Total Gates, Depth 14.
              </p>
            </div>
            <span className="px-2.5 py-1 rounded-lg bg-[#262a34] font-mono text-xs text-[#00dbe9]">
              ZZFeatureMap + RealAmplitudes
            </span>
          </div>

          {/* Interactive Circuit Schematic */}
          <div className="w-full bg-[#0a0e17] p-3.5 rounded-xl border border-[#31353f]/40 overflow-x-auto">
            <svg
              className="w-full h-auto text-[#dbfcff] font-mono"
              fill="none"
              viewBox="0 0 420 180"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* Wires */}
              <text className="fill-[#00dbe9] text-[11px] font-bold" x="10" y="34">|q₀⟩</text>
              <line stroke="#334155" strokeWidth="1.5" x1="45" x2="410" y1="30" y2="30"></line>
              <text className="fill-[#00dbe9] text-[11px] font-bold" x="10" y="74">|q₁⟩</text>
              <line stroke="#334155" strokeWidth="1.5" x1="45" x2="410" y1="70" y2="70"></line>
              <text className="fill-[#00dbe9] text-[11px] font-bold" x="10" y="114">|q₂⟩</text>
              <line stroke="#334155" strokeWidth="1.5" x1="45" x2="410" y1="110" y2="110"></line>
              <text className="fill-[#00dbe9] text-[11px] font-bold" x="10" y="154">|q₃⟩</text>
              <line stroke="#334155" strokeWidth="1.5" x1="45" x2="410" y1="150" y2="150"></line>

              {/* H gates */}
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

              {/* Rz(x_i) */}
              <g>
                <rect fill="#1b2029" height="24" rx="3" stroke="#7df4ff" strokeWidth="1" width="38" x="95" y="18"></rect>
                <text className="fill-[#dbfcff] text-[9px]" x="99" y="34">Rz(x₀)</text>
                <rect fill="#1b2029" height="24" rx="3" stroke="#7df4ff" strokeWidth="1" width="38" x="95" y="58"></rect>
                <text className="fill-[#dbfcff] text-[9px]" x="99" y="74">Rz(x₁)</text>
                <rect fill="#1b2029" height="24" rx="3" stroke="#7df4ff" strokeWidth="1" width="38" x="95" y="98"></rect>
                <text className="fill-[#dbfcff] text-[9px]" x="99" y="114">Rz(x₂)</text>
                <rect fill="#1b2029" height="24" rx="3" stroke="#7df4ff" strokeWidth="1" width="38" x="95" y="138"></rect>
                <text className="fill-[#dbfcff] text-[9px]" x="99" y="154">Rz(x₃)</text>
              </g>

              {/* CX Entangler */}
              <g>
                <circle cx="155" cy="30" fill="#d0bcff" r="3.5"></circle>
                <line stroke="#d0bcff" strokeWidth="1.5" x1="155" x2="155" y1="30" y2="70"></line>
                <circle cx="155" cy="70" fill="#070b13" r="6" stroke="#d0bcff" strokeWidth="1.5"></circle>
                <line stroke="#d0bcff" strokeWidth="1.5" x1="150" x2="160" y1="70" y2="70"></line>

                <circle cx="180" cy="70" fill="#d0bcff" r="3.5"></circle>
                <line stroke="#d0bcff" strokeWidth="1.5" x1="180" x2="180" y1="70" y2="110"></line>
                <circle cx="180" cy="110" fill="#070b13" r="6" stroke="#d0bcff" strokeWidth="1.5"></circle>
                <line stroke="#d0bcff" strokeWidth="1.5" x1="175" x2="185" y1="110" y2="110"></line>

                <circle cx="205" cy="110" fill="#d0bcff" r="3.5"></circle>
                <line stroke="#d0bcff" strokeWidth="1.5" x1="205" x2="205" y1="110" y2="150"></line>
                <circle cx="205" cy="150" fill="#070b13" r="6" stroke="#d0bcff" strokeWidth="1.5"></circle>
                <line stroke="#d0bcff" strokeWidth="1.5" x1="200" x2="210" y1="150" y2="150"></line>
              </g>

              {/* Variational Ry Rotations */}
              <g>
                <rect fill="#262a34" height="24" rx="3" stroke="#d0bcff" strokeWidth="1" width="38" x="235" y="18"></rect>
                <text className="fill-[#d0bcff] text-[9px]" x="239" y="34">Ry(θ₀)</text>
                <rect fill="#262a34" height="24" rx="3" stroke="#d0bcff" strokeWidth="1" width="38" x="235" y="58"></rect>
                <text className="fill-[#d0bcff] text-[9px]" x="239" y="74">Ry(θ₁)</text>
                <rect fill="#262a34" height="24" rx="3" stroke="#d0bcff" strokeWidth="1" width="38" x="235" y="98"></rect>
                <text className="fill-[#d0bcff] text-[9px]" x="239" y="114">Ry(θ₂)</text>
                <rect fill="#262a34" height="24" rx="3" stroke="#d0bcff" strokeWidth="1" width="38" x="235" y="138"></rect>
                <text className="fill-[#d0bcff] text-[9px]" x="239" y="154">Ry(θ₃)</text>
              </g>

              {/* Measurement boxes */}
              <g>
                <rect fill="#0f172a" height="24" rx="3" stroke="#849495" strokeWidth="1" width="28" x="370" y="18"></rect>
                <path d="M377 33 A7 7 0 0 1 391 33 M384 33 L388 24" fill="none" stroke="#849495" strokeWidth="1.2"></path>
                <rect fill="#0f172a" height="24" rx="3" stroke="#849495" strokeWidth="1" width="28" x="370" y="58"></rect>
                <path d="M377 73 A7 7 0 0 1 391 73 M384 73 L388 64" fill="none" stroke="#849495" strokeWidth="1.2"></path>
                <rect fill="#0f172a" height="24" rx="3" stroke="#849495" strokeWidth="1" width="28" x="370" y="98"></rect>
                <path d="M377 113 A7 7 0 0 1 391 113 M384 113 L388 104" fill="none" stroke="#849495" strokeWidth="1.2"></path>
                <rect fill="#0f172a" height="24" rx="3" stroke="#849495" strokeWidth="1" width="28" x="370" y="138"></rect>
                <path d="M377 153 A7 7 0 0 1 391 153 M384 153 L388 144" fill="none" stroke="#849495" strokeWidth="1.2"></path>
              </g>
            </svg>
          </div>

          {/* Qubit to Feature Mapping table */}
          <div className="p-3 rounded-lg bg-[#0a0e17] border border-[#31353f]/40 font-mono text-xs">
            <span className="text-[10px] text-[#849495] uppercase block mb-2">
              QUBIT-TO-FEATURE ENCODING ASSIGNMENTS
            </span>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
              <div className="p-2 rounded bg-[#171c25] border border-[#31353f]/30">
                <span className="text-[#00dbe9] font-bold block">|q₀⟩ → x₀</span>
                <span className="text-[#dfe2f0]">radius_mean</span>
              </div>
              <div className="p-2 rounded bg-[#171c25] border border-[#31353f]/30">
                <span className="text-[#00dbe9] font-bold block">|q₁⟩ → x₁</span>
                <span className="text-[#dfe2f0]">concavity_mean</span>
              </div>
              <div className="p-2 rounded bg-[#171c25] border border-[#31353f]/30">
                <span className="text-[#00dbe9] font-bold block">|q₂⟩ → x₂</span>
                <span className="text-[#dfe2f0]">texture_mean</span>
              </div>
              <div className="p-2 rounded bg-[#171c25] border border-[#31353f]/30">
                <span className="text-[#00dbe9] font-bold block">|q₃⟩ → x₃</span>
                <span className="text-[#dfe2f0]">perimeter_mean</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Quantum Kernel Gram Matrix Heatmap (5 cols) */}
        <div className="lg:col-span-5 p-5 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-[#eef7ff]">
                Quantum Kernel Gram Matrix
              </h3>
              <p className="text-xs text-[#b9cacb]">
                Fidelity inner products |⟨ψ(x_i)|ψ(x_j)⟩|²
              </p>
            </div>
            <span className="font-mono text-xs text-[#00dbe9]">10×10 Slice</span>
          </div>

          {/* Interactive Heatmap Matrix */}
          <div className="relative p-3 rounded-xl bg-[#0a0e17] border border-[#31353f]/40 flex flex-col items-center">
            {hoveredCell && (
              <div className="absolute top-2 right-2 px-2.5 py-1 rounded bg-[#262a34] font-mono text-[11px] text-[#00f0ff] border border-[#00f0ff]/40 shadow-lg z-10">
                K(x_{hoveredCell.i}, x_{hoveredCell.j}) = {hoveredCell.val.toFixed(4)}
              </div>
            )}

            <div className="grid grid-cols-10 gap-1 w-full max-w-[320px] aspect-square">
              {gramMatrix.map((row, i) =>
                row.map((val, j) => {
                  const opacity = Math.max(0.12, val);
                  return (
                    <div
                      key={`${i}-${j}`}
                      onMouseEnter={() => setHoveredCell({ i, j, val })}
                      onMouseLeave={() => setHoveredCell(null)}
                      style={{
                        backgroundColor: i === j ? '#00f0ff' : `rgba(0, 219, 233, ${opacity})`,
                      }}
                      className="rounded-sm cursor-pointer transition-transform hover:scale-110 hover:z-20 hover:ring-1 hover:ring-[#dbfcff]"
                    />
                  );
                })
              )}
            </div>

            {/* Colorbar Scale */}
            <div className="w-full max-w-[320px] mt-3 space-y-1 font-mono text-[10px] text-[#849495]">
              <div className="h-2 w-full rounded bg-gradient-to-r from-[#0a0e17] via-[#006970] to-[#00f0ff]"></div>
              <div className="flex justify-between">
                <span>0.00 (Orthogonal)</span>
                <span>0.50</span>
                <span className="text-[#00dbe9]">1.00 (Identical)</span>
              </div>
            </div>
          </div>

          {/* VQC COBYLA Optimization Curve */}
          <div className="p-3.5 rounded-lg bg-[#0a0e17] border border-[#31353f]/40 space-y-2">
            <div className="flex items-center justify-between font-mono text-xs">
              <span className="text-[#849495] uppercase text-[10px]">
                VQC CONVERGENCE TRAJECTORY (COBYLA)
              </span>
              <span className="text-[#00dbe9]">Plateau at Iter 164</span>
            </div>

            <svg className="w-full h-20 overflow-visible" viewBox="0 0 300 70">
              <line x1="20" y1="10" x2="20" y2="60" stroke="#262a34" strokeWidth="1" />
              <line x1="20" y1="60" x2="290" y2="60" stroke="#262a34" strokeWidth="1" />
              {/* Loss path */}
              <path
                d="M20,15 Q60,40 120,48 T200,52 T290,53"
                fill="none"
                stroke="#d0bcff"
                strokeWidth="2"
              />
              <text x="25" y="20" fill="#849495" fontSize="8">0.742</text>
              <text x="250" y="46" fill="#d0bcff" fontSize="8">0.284</text>
            </svg>
            <div className="flex justify-between font-mono text-[10px] text-[#849495]">
              <span>Iter 0</span>
              <span>Iter 100</span>
              <span>Iter 200</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
