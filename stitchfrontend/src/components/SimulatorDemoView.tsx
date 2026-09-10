import React, { useState, useMemo } from 'react';
import {
  Sliders,
  Play,
  RotateCcw,
  Sparkles,
  Download,
  Share2,
  Cpu,
  Scale,
  Activity,
  CheckCircle2,
  FileText,
  Copy,
  Check,
} from 'lucide-react';
import { WISCONSIN_SLIDERS, PRESET_VECTORS } from '../data/datasets';
import { TabType } from '../types';

interface SimulatorDemoViewProps {
  onNavigateToScoreSheet: () => void;
}

export const SimulatorDemoView: React.FC<SimulatorDemoViewProps> = ({
  onNavigateToScoreSheet,
}) => {
  // Feature slider z-scores
  const [vector, setVector] = useState<Record<string, number>>({
    radius_mean: 0.42,
    concavity_mean: -0.15,
    texture_mean: 0.88,
    perimeter_mean: 0.21,
  });

  const [activeModel, setActiveModel] = useState<'lr' | 'tree' | 'qsvc'>('lr');
  const [showJsonModal, setShowJsonModal] = useState(false);
  const [copiedJson, setCopiedJson] = useState(false);

  // Dynamic calculations based on logistic regression beta weights
  const { lrMargin, lrScore, lrBand, treeScore, qsvcScore, qsvcOverlap } = useMemo(() => {
    const rawMargin =
      vector.radius_mean * 1.842 +
      vector.concavity_mean * 1.419 +
      vector.texture_mean * 0.978 +
      vector.perimeter_mean * 0.651;

    // Sigmoid function mapping rawMargin to 0-100 score
    const sigmoid = 1 / (1 + Math.exp(-rawMargin));
    const score = Math.round(sigmoid * 100);

    let band: 'Lower' | 'Middle' | 'Higher' = 'Middle';
    if (score < 40) band = 'Lower';
    else if (score >= 70) band = 'Higher';

    // Tree score: slightly non-linear step-like
    const treeS = Math.min(
      98,
      Math.max(
        2,
        Math.round(
          50 +
            (vector.radius_mean > 0.5 ? 25 : -20) +
            (vector.concavity_mean > 0 ? 15 : -10) +
            vector.texture_mean * 8
        )
      )
    );

    // QSVC score: kernel overlap
    const kernelNorm = Math.sqrt(
      vector.radius_mean ** 2 +
        vector.concavity_mean ** 2 +
        vector.texture_mean ** 2 +
        vector.perimeter_mean ** 2
    );
    const overlap = Math.exp(-0.5 * (kernelNorm - 1.2) ** 2);
    const qsvcS = Math.min(99, Math.max(1, Math.round(overlap * 85 + 10)));

    return {
      lrMargin: rawMargin,
      lrScore: score,
      lrBand: band,
      treeScore: treeS,
      qsvcScore: qsvcS,
      qsvcOverlap: overlap,
    };
  }, [vector]);

  // Selected display score based on active model pill
  const currentScore =
    activeModel === 'lr' ? lrScore : activeModel === 'tree' ? treeScore : qsvcScore;

  const handleSliderChange = (id: string, value: number) => {
    setVector((prev) => ({ ...prev, [id]: value }));
  };

  const handleApplyPreset = (presetKey: keyof typeof PRESET_VECTORS) => {
    setVector(PRESET_VECTORS[presetKey]);
  };

  const handlePerturb = () => {
    setVector((prev) => ({
      radius_mean: parseFloat((prev.radius_mean + (Math.random() * 0.4 - 0.2)).toFixed(2)),
      concavity_mean: parseFloat((prev.concavity_mean + (Math.random() * 0.4 - 0.2)).toFixed(2)),
      texture_mean: parseFloat((prev.texture_mean + (Math.random() * 0.4 - 0.2)).toFixed(2)),
      perimeter_mean: parseFloat((prev.perimeter_mean + (Math.random() * 0.4 - 0.2)).toFixed(2)),
    }));
  };

  // Simulated Qubit Phase rotations in radians [-π, π]
  const qPhases = [
    { name: '|q₀⟩ Phase θ₀', val: ((vector.radius_mean * Math.PI) / 3).toFixed(2), feat: 'Radius' },
    { name: '|q₁⟩ Phase θ₁', val: ((vector.concavity_mean * Math.PI) / 3).toFixed(2), feat: 'Concavity' },
    { name: '|q₂⟩ Phase θ₂', val: ((vector.texture_mean * Math.PI) / 3).toFixed(2), feat: 'Texture' },
    { name: '|q₃⟩ Phase θ₃', val: ((vector.perimeter_mean * Math.PI) / 3).toFixed(2), feat: 'Mean perimeter (nuclei edge)' },
  ];

  return (
    <div className="w-full max-w-6xl mx-auto px-4 md:px-6 py-6 pb-16 space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
              <Sliders className="w-3.5 h-3.5" />
            </span>
            <span className="font-mono text-xs uppercase text-[#00dbe9] tracking-widest">
              PROTOCOL 05-D / DETERMINISTIC INFERENCE SIMULATOR
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
            Deterministic Inference Simulator
          </h1>
          <p className="text-xs md:text-sm text-[#b9cacb] max-w-3xl mt-1 leading-relaxed">
            Interactive feature exploration across classical models and simulated quantum statevectors. Adjust standardized values (z-scores) or select canonical test vectors.
          </p>
        </div>

        {/* Dataset badge */}
        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="px-3 py-1.5 rounded-xl bg-[#171c25] border border-[#31353f] text-[#dbfcff]">
            Wisconsin Diagnostic Tabular (4-Dim PCA)
          </span>
        </div>
      </div>

      {/* Model Selection Bar */}
      <div className="p-3 rounded-xl bg-[#0f131d] border border-[#31353f]/50 flex flex-wrap items-center justify-between gap-3 shadow-md">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs text-[#849495] uppercase">ACTIVE INFERENCE ENGINE:</span>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setActiveModel('lr')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all flex items-center gap-1.5 ${
                activeModel === 'lr'
                  ? 'bg-[#00f0ff] text-[#00363a] font-bold shadow-[0_0_12px_rgba(0,219,233,0.3)]'
                  : 'bg-[#171c25] text-[#b9cacb] hover:text-[#dfe2f0]'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-current"></span>
              <span>Linear LR Champion</span>
            </button>
            <button
              onClick={() => setActiveModel('tree')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all flex items-center gap-1.5 ${
                activeModel === 'tree'
                  ? 'bg-[#d0bcff] text-[#1b2029] font-bold shadow-[0_0_12px_rgba(208,188,255,0.3)]'
                  : 'bg-[#171c25] text-[#b9cacb] hover:text-[#dfe2f0]'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-current"></span>
              <span>Tree Ensemble</span>
            </button>
            <button
              onClick={() => setActiveModel('qsvc')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all flex items-center gap-1.5 ${
                activeModel === 'qsvc'
                  ? 'bg-[#7df4ff] text-[#00363a] font-bold shadow-[0_0_12px_rgba(125,244,255,0.3)]'
                  : 'bg-[#171c25] text-[#b9cacb] hover:text-[#dfe2f0]'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-current"></span>
              <span>Quantum Kernel (QSVC)</span>
            </button>
          </div>
        </div>

        <span className="font-mono text-xs text-[#849495]">Statevector Simulation · Zero Hardware Shots</span>
      </div>

      {/* Main Grid: Controls vs Model Output */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Sliders & Presets (7 cols) */}
        <div className="lg:col-span-7 p-5 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md space-y-5">
          {/* Preset Buttons */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs text-[#849495] uppercase tracking-wider">
                CANONICAL VECTOR PRESETS
              </span>
              <span className="font-mono text-[10px] text-[#00dbe9]">Click to apply</span>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={() => handleApplyPreset('median')}
                className="px-2.5 py-1.5 rounded-lg bg-[#262a34] hover:bg-[#353944] text-xs font-mono text-[#dfe2f0] transition-all border border-[#31353f]/50"
              >
                Median Benchmark [x]
              </button>
              <button
                onClick={() => handleApplyPreset('decisionSurface')}
                className="px-2.5 py-1.5 rounded-lg bg-[#262a34] hover:bg-[#353944] text-xs font-mono text-[#dfe2f0] transition-all border border-[#31353f]/50"
              >
                Decision Surface (w·x ≈ 0)
              </button>
              <button
                onClick={() => handleApplyPreset('polarCentroid')}
                className="px-2.5 py-1.5 rounded-lg bg-[#262a34] hover:bg-[#353944] text-xs font-mono text-[#dfe2f0] transition-all border border-[#31353f]/50"
              >
                Polar Centroid (+2.0σ)
              </button>
              <button
                onClick={handlePerturb}
                className="px-2.5 py-1.5 rounded-lg bg-[#1b2029] hover:bg-[#262a34] text-xs font-mono text-[#00dbe9] transition-all border border-[#00dbe9]/30 flex items-center gap-1"
              >
                <Sparkles className="w-3 h-3" />
                <span>Perturb</span>
              </button>
              <button
                onClick={() => handleApplyPreset('zero')}
                className="px-2.5 py-1.5 rounded-lg bg-[#1b2029] hover:bg-[#262a34] text-xs font-mono text-[#849495] transition-all border border-[#31353f]/30 flex items-center gap-1"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Origin (0σ)</span>
              </button>
            </div>
          </div>

          {/* 4 Feature Sliders */}
          <div className="space-y-4 pt-2 border-t border-[#31353f]/40">
            {WISCONSIN_SLIDERS.map((cfg) => {
              const currentZ = vector[cfg.id] ?? 0;
              const isPositive = currentZ >= 0;
              return (
                <div key={cfg.id} className="p-3.5 rounded-xl bg-[#0a0e17] border border-[#31353f]/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-[#eef7ff]">{cfg.name}</span>
                        <span className="font-mono text-[10px] text-[#849495]">{cfg.dimLabel}</span>
                      </div>
                      <span className="font-mono text-xs text-[#00dbe9]">
                        {cfg.formatRaw(currentZ)}
                      </span>
                    </div>

                    <div className="text-right">
                      <span className="font-mono text-sm font-bold text-[#dbfcff]">
                        {isPositive ? `+${currentZ.toFixed(2)}` : currentZ.toFixed(2)} σ
                      </span>
                      <span className="font-mono text-[10px] text-[#849495] block">
                        β weight = +{cfg.weight.toFixed(3)}
                      </span>
                    </div>
                  </div>

                  <input
                    type="range"
                    min={cfg.min}
                    max={cfg.max}
                    step={cfg.step}
                    value={currentZ}
                    onChange={(e) => handleSliderChange(cfg.id, parseFloat(e.target.value))}
                    className="w-full accent-[#00f0ff] cursor-pointer h-2 bg-[#262a34] rounded-lg"
                  />

                  <div className="flex justify-between font-mono text-[10px] text-[#849495]">
                    <span>-3.0 σ (Low)</span>
                    <span>0.0 σ (Mean)</span>
                    <span>+3.0 σ (High)</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Bottom Control Actions */}
          <div className="pt-2 border-t border-[#31353f]/40 flex flex-wrap items-center justify-between gap-3">
            <button
              onClick={() => setShowJsonModal(true)}
              className="px-4 py-2 rounded-lg bg-[#262a34] hover:bg-[#353944] border border-[#31353f] text-xs font-mono text-[#b9cacb] hover:text-[#dfe2f0] transition-all flex items-center gap-1.5"
            >
              <FileText className="w-3.5 h-3.5 text-[#00dbe9]" />
              <span>Export Vector (JSON)</span>
            </button>

            <button
              type="button"
              onClick={() => onNavigateToScoreSheet()}
              className="relative z-30 px-5 py-2.5 text-xs font-bold flex items-center gap-2"
            >
              <span>Send to Score Sheet</span>
              <Share2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Right Column: Dynamic Gauge & Model Divergence (5 cols) */}
        <div className="lg:col-span-5 space-y-5">
          {/* Main Experimental Output Gauge */}
          <div className="p-5 rounded-xl bg-[#171c25] border border-[#00f0ff]/40 shadow-lg relative overflow-hidden">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs text-[#849495] uppercase tracking-wider">
                EXPERIMENTAL MODEL OUTPUT
              </span>
              <span
                className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold ${
                  lrBand === 'Higher'
                    ? 'bg-[#571bc1]/40 text-[#e9ddff]'
                    : lrBand === 'Middle'
                    ? 'bg-[#006970]/40 text-[#7df4ff]'
                    : 'bg-[#262a34] text-[#849495]'
                }`}
              >
                {lrBand} Band
              </span>
            </div>

            {/* Huge Score Readout */}
            <div className="my-4 flex items-baseline gap-3">
              <span className="font-mono text-6xl font-extrabold text-[#dbfcff] drop-shadow-[0_0_20px_rgba(0,219,233,0.4)]">
                {currentScore}
              </span>
              <span className="font-mono text-xl text-[#849495] font-semibold">/ 100</span>
            </div>

            <div className="font-mono text-xs text-[#00dbe9] font-medium flex items-center justify-between">
              <span>Normalized Margin:</span>
              <span className="text-sm font-bold">
                {lrMargin >= 0 ? `+${lrMargin.toFixed(2)}` : lrMargin.toFixed(2)} σ
              </span>
            </div>

            {/* Density Distribution Bar */}
            <div className="mt-4 space-y-1.5">
              <div className="flex justify-between font-mono text-[10px] text-[#849495]">
                <span>Lower (0–39)</span>
                <span>Middle (40–69)</span>
                <span>Higher (70–100)</span>
              </div>
              <div className="h-3.5 w-full rounded-md bg-[#0a0e17] overflow-hidden flex relative p-0.5 border border-[#31353f]/40">
                <div className="h-full w-[40%] bg-[#262a34] rounded-l"></div>
                <div className="h-full w-[30%] bg-[#006970]/60"></div>
                <div className="h-full w-[30%] bg-[#571bc1]/60 rounded-r"></div>

                {/* Score Marker Needle */}
                <div
                  className="absolute top-0 bottom-0 w-1.5 bg-[#00f0ff] rounded shadow-[0_0_8px_#00f0ff] transition-all duration-200 -ml-0.5"
                  style={{ left: `${Math.min(99, Math.max(1, currentScore))}%` }}
                />
              </div>
            </div>

            {/* Non-clinical disclaimer */}
            <p className="text-[11px] text-[#b9cacb] mt-4 pt-3 border-t border-[#31353f]/40 leading-relaxed">
              <strong className="text-[#dfe2f0]">Notice:</strong> Research score generated for demonstration purposes. Not a clinical diagnosis.
            </p>
          </div>

          {/* Model Comparison & Kernel Divergence Card */}
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between">
              <span className="text-[#849495] uppercase text-[10px]">
                MODEL COMPARISON & KERNEL DIVERGENCE
              </span>
              <span className="text-[#00dbe9]">Zero Noise Sim</span>
            </div>

            <div className="space-y-2">
              <div className="p-2.5 rounded-lg bg-[#0a0e17] border border-[#31353f]/30 flex items-center justify-between">
                <div>
                  <span className="font-semibold text-[#dbfcff] block">Linear LR</span>
                  <span className="text-[10px] text-[#849495]">Margin: +{lrMargin.toFixed(2)}σ</span>
                </div>
                <span className="text-base font-bold text-[#00f0ff]">{lrScore} / 100</span>
              </div>

              <div className="p-2.5 rounded-lg bg-[#0a0e17] border border-[#31353f]/30 flex items-center justify-between">
                <div>
                  <span className="font-semibold text-[#dfe2f0] block">Tree Ensemble</span>
                  <span className="text-[10px] text-[#849495]">Gini partition vote</span>
                </div>
                <span className="text-base font-bold text-[#d0bcff]">{treeScore} / 100</span>
              </div>

              <div className="p-2.5 rounded-lg bg-[#0a0e17] border border-[#31353f]/30 flex items-center justify-between">
                <div>
                  <span className="font-semibold text-[#dfe2f0] block">Quantum Kernel (QSVC)</span>
                  <span className="text-[10px] text-[#849495]">Overlap: {qsvcOverlap.toFixed(4)}</span>
                </div>
                <span className="text-base font-bold text-[#7df4ff]">{qsvcScore} / 100</span>
              </div>
            </div>

            <div className="pt-2 border-t border-[#31353f]/30 text-[11px] text-[#849495] flex justify-between">
              <span>Hyperplane Delta Variance:</span>
              <span className="text-[#dfe2f0]">Var(Δ) = 0.042</span>
            </div>
          </div>

          {/* Qubit Phase Display */}
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between">
              <span className="text-[#849495] uppercase text-[10px]">
                QUBIT PHASE DISPLAY (SIMULATED STATEVECTOR)
              </span>
              <span className="text-[#00dbe9]">4 Qubits</span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              {qPhases.map((qp, idx) => (
                <div key={idx} className="p-2 rounded-lg bg-[#0a0e17] border border-[#31353f]/30">
                  <div className="flex justify-between text-[10px] text-[#849495]">
                    <span>{qp.name}</span>
                    <span className="text-[#00dbe9]">{qp.feat}</span>
                  </div>
                  <span className="text-sm font-bold text-[#dbfcff] block mt-0.5">
                    {qp.val} rad
                  </span>
                </div>
              ))}
            </div>

            <div className="pt-2 border-t border-[#31353f]/30 text-[10px] text-[#849495] flex justify-between">
              <span>Unitary Phase Coherence: 0.9998</span>
              <span>State: |ψ(x)⟩ ∈ ℂ¹⁶</span>
            </div>
          </div>
        </div>
      </div>

      {/* JSON Export Modal */}
      {showJsonModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-xl bg-[#0f131d] rounded-2xl border border-[#31353f] p-5 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-[#31353f] pb-3">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-[#00dbe9]" />
                <h3 className="text-base font-bold text-[#dbfcff]">
                  Standardized Vector JSON
                </h3>
              </div>
              <button
                onClick={() => setShowJsonModal(false)}
                className="text-xs text-[#849495] hover:text-[#dfe2f0] px-2 py-1 rounded bg-[#171c25]"
              >
                Close
              </button>
            </div>

            <pre className="p-4 rounded-xl bg-[#0a0e17] font-mono text-xs text-[#00dbe9] overflow-x-auto border border-[#31353f]/50 leading-relaxed">
{JSON.stringify(
  {
    schema: "lakshya.research.vector.v1",
    dataset: "Wisconsin Diagnostic Tabular",
    protocol: "05-D",
    timestamp: new Date().toISOString(),
    standardized_z_scores: vector,
    inferred_margin: lrMargin,
    scores: {
      linear_lr: lrScore,
      tree_ensemble: treeScore,
      quantum_kernel: qsvcScore,
    },
    qubit_phases_radians: {
      q0: ((vector.radius_mean * Math.PI) / 3).toFixed(4),
      q1: ((vector.concavity_mean * Math.PI) / 3).toFixed(4),
      q2: ((vector.texture_mean * Math.PI) / 3).toFixed(4),
      q3: ((vector.perimeter_mean * Math.PI) / 3).toFixed(4),
    }
  },
  null,
  2
)}
            </pre>

            <div className="flex justify-between items-center">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(JSON.stringify(vector, null, 2));
                  setCopiedJson(true);
                  setTimeout(() => setCopiedJson(false), 2000);
                }}
                className="px-3 py-1.5 rounded-lg bg-[#262a34] text-xs font-mono text-[#b9cacb] hover:text-[#dfe2f0] transition-all flex items-center gap-1.5"
              >
                {copiedJson ? <Check className="w-3.5 h-3.5 text-[#00dbe9]" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedJson ? 'Copied to clipboard' : 'Copy JSON'}</span>
              </button>
              <button
                onClick={() => setShowJsonModal(false)}
                className="px-4 py-2 rounded-lg bg-[#00f0ff] text-[#00363a] text-xs font-bold"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
