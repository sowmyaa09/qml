import React, { useState } from 'react';
import {
  Scale,
  CheckCircle2,
  ChevronDown,
  Activity,
  Award,
  Zap,
  Info,
  Layers,
  ArrowRight,
} from 'lucide-react';
import { DATASETS } from '../data/datasets';
import { TabType } from '../types';

interface ClassicalBaselinesViewProps {
  selectedDatasetId: string;
  onSelectDatasetId: (id: string) => void;
  onNavigate: (tab: TabType) => void;
}

export const ClassicalBaselinesView: React.FC<ClassicalBaselinesViewProps> = ({
  selectedDatasetId,
  onSelectDatasetId,
  onNavigate,
}) => {
  const [curveMode, setCurveMode] = useState<'roc' | 'pr'>('roc');
  const [hoverCoord, setHoverCoord] = useState<{ x: string; y: string } | null>(null);

  const activeDataset =
    DATASETS.find((d) => d.id === selectedDatasetId) || DATASETS[0];

  return (
    <div className="w-full max-w-6xl mx-auto px-4 md:px-6 py-6 pb-16 space-y-6">
      {/* Header with Dataset Selector */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
              <Scale className="w-3.5 h-3.5" />
            </span>
            <span className="font-mono text-xs uppercase text-[#00dbe9] tracking-widest">
              PROTOCOL 02-B / DETERMINISTIC BASELINES
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
            Classical Baselines Studio
          </h1>
        </div>

        {/* Dataset Switcher Dropdown */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <select
              value={selectedDatasetId}
              onChange={(e) => onSelectDatasetId(e.target.value)}
              className="appearance-none pl-3.5 pr-9 py-2 rounded-xl bg-[#171c25] border border-[#31353f] font-mono text-xs text-[#dbfcff] focus:outline-none focus:border-[#00f0ff] transition-all cursor-pointer shadow-sm"
            >
              {DATASETS.map((ds) => (
                <option key={ds.id} value={ds.id}>
                  {ds.name} ({ds.dimensionality}, N={ds.sampleCount})
                </option>
              ))}
            </select>
            <ChevronDown className="w-4 h-4 text-[#849495] absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          <span className="px-3 py-1.5 rounded-xl bg-[#571bc1]/30 border border-[#571bc1]/60 font-mono text-xs text-[#e9ddff] font-semibold">
            NOT CLINICAL · RESEARCH BENCHMARK ONLY
          </span>
        </div>
      </div>

      {/* Audit Pipeline parameters strip */}
      <div className="px-4 py-2.5 rounded-xl bg-[#0f131d] border border-[#31353f]/50 flex flex-wrap items-center justify-between gap-2 font-mono text-xs text-[#b9cacb] shadow-sm">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#00dbe9]"></span>
          <span>random_state=42 | Split: 80/20 Stratified | CV: 5-Fold Repeated | StandardScaler(with_mean=True)</span>
        </div>
        <span className="text-[#849495]">Target: {activeDataset.targetDescription}</span>
      </div>

      {/* Top 4 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-[#849495] uppercase">
              CLASSIFICATION ACCURACY
            </span>
            <span className="px-1.5 py-0.5 rounded bg-[#262a34] font-mono text-[9px] text-[#00dbe9]">
              N=114
            </span>
          </div>
          <div className="my-2">
            <span className="font-mono text-3xl font-bold text-[#dbfcff]">
              {(activeDataset.scikitBaselineAccuracy * 100).toFixed(2)}%
            </span>
          </div>
          <span className="text-xs text-[#b9cacb]">
            {activeDataset.scikitBaselineName} (Test Split)
          </span>
        </div>

        {/* Metric 2 */}
        <div className="p-4 rounded-xl bg-[#171c25] border border-[#00f0ff]/40 shadow-md flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 px-2 py-0.5 rounded-bl bg-[#00f0ff] font-mono text-[9px] text-[#00363a] font-bold">
            CHAMPION F1
          </div>
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-[#00dbe9] uppercase font-bold">
              F1-SCORE
            </span>
          </div>
          <div className="my-2 flex items-baseline gap-2">
            <span className="font-mono text-3xl font-bold text-[#00f0ff]">
              {activeDataset.scikitBaselineF1.toFixed(3)}
            </span>
            <span className="font-mono text-xs text-[#00dbe9] font-semibold">
              +{Math.abs(activeDataset.scikitBaselineF1 - activeDataset.qmlModelF1).toFixed(3)} vs QSVC
            </span>
          </div>
          <span className="text-xs text-[#b9cacb]">Stratified Test Evaluation</span>
        </div>

        {/* Metric 3 */}
        <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-[#849495] uppercase">
              ROC-AUC INTEGRAL
            </span>
            <span className="font-mono text-[9px] text-[#d0bcff]">p &lt; 0.001</span>
          </div>
          <div className="my-2">
            <span className="font-mono text-3xl font-bold text-[#d0bcff]">0.984</span>
          </div>
          <span className="text-xs text-[#b9cacb]">Wilcoxon Signed-Rank Test</span>
        </div>

        {/* Metric 4 */}
        <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] text-[#849495] uppercase">
              SPECIFICITY
            </span>
            <span className="font-mono text-[9px] text-[#849495]">TNR</span>
          </div>
          <div className="my-2">
            <span className="font-mono text-3xl font-bold text-[#dfe2f0]">0.958</span>
          </div>
          <span className="text-xs text-[#b9cacb]">68 / 71 Negative (Benign)</span>
        </div>
      </div>

      {/* Classical Algorithm Verification Matrix Table */}
      <div className="p-5 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-[#eef7ff]">
              Classical Algorithm Verification Matrix
            </h2>
            <p className="text-xs text-[#b9cacb]">
              Direct evaluations conducted on identical 80:20 stratified split (Seed: 0x4B3A8F, test N=114).
            </p>
          </div>
          <span className="font-mono text-xs text-[#00dbe9]">Repeated 5-Fold Stratified</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#31353f]/60 text-[#849495] uppercase text-[10px]">
                <th className="py-2.5 px-3">ALGORITHM</th>
                <th className="py-2.5 px-3">FAMILY</th>
                <th className="py-2.5 px-3">ACCURACY</th>
                <th className="py-2.5 px-3">PRECISION</th>
                <th className="py-2.5 px-3">RECALL</th>
                <th className="py-2.5 px-3">F1-SCORE</th>
                <th className="py-2.5 px-3">ROC-AUC</th>
                <th className="py-2.5 px-3">TRAIN TIME</th>
                <th className="py-2.5 px-3">STATUS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#31353f]/40 text-[#dfe2f0]">
              {/* Row 1: Logistic Regression */}
              <tr className="bg-[#1b2029]/80 hover:bg-[#262a34]/60 transition-colors">
                <td className="py-3 px-3 font-semibold text-[#dbfcff]">
                  Logistic Regression (L2)
                </td>
                <td className="py-3 px-3 text-[#b9cacb]">Generalized Linear</td>
                <td className="py-3 px-3">0.9474</td>
                <td className="py-3 px-3">0.9302</td>
                <td className="py-3 px-3">0.9302</td>
                <td className="py-3 px-3 text-[#00f0ff] font-bold text-sm">0.9320</td>
                <td className="py-3 px-3">0.9841</td>
                <td className="py-3 px-3 text-[#00dbe9]">3.2ms</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 rounded bg-[#00dbe9]/20 text-[#00dbe9] border border-[#00dbe9]/40 text-[10px] font-bold">
                    Champion F1
                  </span>
                </td>
              </tr>

              {/* Row 2: SVC RBF */}
              <tr className="hover:bg-[#1b2029]/60 transition-colors">
                <td className="py-3 px-3 font-semibold text-[#eef7ff]">
                  Support Vector Classifier (RBF)
                </td>
                <td className="py-3 px-3 text-[#b9cacb]">Kernel Machine</td>
                <td className="py-3 px-3">0.9386</td>
                <td className="py-3 px-3">0.9286</td>
                <td className="py-3 px-3">0.9070</td>
                <td className="py-3 px-3 text-[#dfe2f0] font-bold">0.9272</td>
                <td className="py-3 px-3">0.9792</td>
                <td className="py-3 px-3 text-[#b9cacb]">6.1ms</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 rounded bg-[#262a34] text-[#b9cacb] text-[10px]">
                    Verified Control
                  </span>
                </td>
              </tr>

              {/* Row 3: Random Forest */}
              <tr className="hover:bg-[#1b2029]/60 transition-colors">
                <td className="py-3 px-3 font-semibold text-[#eef7ff]">
                  Random Forest Ensemble
                </td>
                <td className="py-3 px-3 text-[#b9cacb]">Bagged Trees</td>
                <td className="py-3 px-3">0.9298</td>
                <td className="py-3 px-3">0.9091</td>
                <td className="py-3 px-3">0.9091</td>
                <td className="py-3 px-3 text-[#dfe2f0] font-bold">0.9264</td>
                <td className="py-3 px-3">0.9744</td>
                <td className="py-3 px-3 text-[#b9cacb]">48.6ms</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 rounded bg-[#262a34] text-[#b9cacb] text-[10px]">
                    Verified Control
                  </span>
                </td>
              </tr>

              {/* Row 4: Linear Ridge */}
              <tr className="hover:bg-[#1b2029]/60 transition-colors">
                <td className="py-3 px-3 font-semibold text-[#eef7ff]">
                  Linear Ridge Classifier
                </td>
                <td className="py-3 px-3 text-[#b9cacb]">L2 Regularized</td>
                <td className="py-3 px-3">0.9211</td>
                <td className="py-3 px-3">0.8864</td>
                <td className="py-3 px-3">0.9070</td>
                <td className="py-3 px-3 text-[#dfe2f0]">0.8966</td>
                <td className="py-3 px-3">0.9610</td>
                <td className="py-3 px-3 text-[#00dbe9]">2.4ms</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 rounded bg-[#262a34] text-[#849495] text-[10px]">
                    Baseline
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Middle Split: ROC Space vs Confusion Matrix & Logistic Coefficients */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: ROC Curve / Precision-Recall (7 cols) */}
        <div className="lg:col-span-7 p-5 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-[#eef7ff]">
                ROC Space & Separation Dynamics
              </h3>
              <p className="text-xs text-[#b9cacb]">
                Paired comparison against kernel separation threshold.
              </p>
            </div>
            {/* Toggle buttons */}
            <div className="p-0.5 rounded-lg bg-[#0a0e17] border border-[#31353f]/60 flex items-center text-xs">
              <button
                onClick={() => setCurveMode('roc')}
                className={`px-2.5 py-1 rounded font-medium transition-all ${
                  curveMode === 'roc'
                    ? 'bg-[#262a34] text-[#00dbe9] font-bold shadow-sm'
                    : 'text-[#849495] hover:text-[#dfe2f0]'
                }`}
              >
                ROC Curve
              </button>
              <button
                onClick={() => setCurveMode('pr')}
                className={`px-2.5 py-1 rounded font-medium transition-all ${
                  curveMode === 'pr'
                    ? 'bg-[#262a34] text-[#00dbe9] font-bold shadow-sm'
                    : 'text-[#849495] hover:text-[#dfe2f0]'
                }`}
              >
                Precision-Recall
              </button>
            </div>
          </div>

          {/* Interactive SVG Chart */}
          <div className="w-full bg-[#0a0e17] p-4 rounded-xl border border-[#31353f]/40 relative">
            {hoverCoord && (
              <div className="absolute top-6 right-6 px-2.5 py-1 rounded bg-[#262a34] font-mono text-[11px] text-[#00f0ff] border border-[#00f0ff]/40 shadow-lg">
                FPR: {hoverCoord.x} · TPR: {hoverCoord.y}
              </div>
            )}
            <svg
              className="w-full h-64 overflow-visible font-mono text-xs"
              viewBox="0 0 450 260"
            >
              {/* Grid Lines */}
              <line x1="50" y1="20" x2="50" y2="220" stroke="#262a34" strokeWidth="1" />
              <line x1="50" y1="220" x2="430" y2="220" stroke="#262a34" strokeWidth="1" />

              <line x1="145" y1="20" x2="145" y2="220" stroke="#1b2029" strokeDasharray="3 3" />
              <line x1="240" y1="20" x2="240" y2="220" stroke="#1b2029" strokeDasharray="3 3" />
              <line x1="335" y1="20" x2="335" y2="220" stroke="#1b2029" strokeDasharray="3 3" />

              <line x1="50" y1="170" x2="430" y2="170" stroke="#1b2029" strokeDasharray="3 3" />
              <line x1="50" y1="120" x2="430" y2="120" stroke="#1b2029" strokeDasharray="3 3" />
              <line x1="50" y1="70" x2="430" y2="70" stroke="#1b2029" strokeDasharray="3 3" />

              {/* Axis Labels */}
              <text x="50" y="238" fill="#849495" fontSize="10" textAnchor="middle">0.0</text>
              <text x="145" y="238" fill="#849495" fontSize="10" textAnchor="middle">0.25</text>
              <text x="240" y="238" fill="#849495" fontSize="10" textAnchor="middle">0.50</text>
              <text x="335" y="238" fill="#849495" fontSize="10" textAnchor="middle">0.75</text>
              <text x="430" y="238" fill="#849495" fontSize="10" textAnchor="middle">1.0</text>

              <text x="38" y="224" fill="#849495" fontSize="10" textAnchor="end">0.0</text>
              <text x="38" y="174" fill="#849495" fontSize="10" textAnchor="end">0.25</text>
              <text x="38" y="124" fill="#849495" fontSize="10" textAnchor="end">0.50</text>
              <text x="38" y="74" fill="#849495" fontSize="10" textAnchor="end">0.75</text>
              <text x="38" y="24" fill="#849495" fontSize="10" textAnchor="end">1.0</text>

              {/* Diagonal Random Classifier Reference */}
              <line
                x1="50"
                y1="220"
                x2="430"
                y2="20"
                stroke="#849495"
                strokeWidth="1.2"
                strokeDasharray="4 4"
                opacity="0.6"
              />

              {/* Logistic Regression Path (Cyan) */}
              <path
                d="M50,220 C60,60 80,30 430,20"
                fill="none"
                stroke="#00f0ff"
                strokeWidth="2.5"
                className="transition-all duration-300 drop-shadow-[0_0_8px_#00dbe9]"
              />

              {/* SVC RBF Path (Purple) */}
              <path
                d="M50,220 C70,75 95,40 430,20"
                fill="none"
                stroke="#d0bcff"
                strokeWidth="1.8"
                opacity="0.85"
              />

              {/* Random Forest (Blue) */}
              <path
                d="M50,220 C80,90 110,50 430,20"
                fill="none"
                stroke="#7bd0ff"
                strokeWidth="1.5"
                opacity="0.7"
              />

              {/* Interactive Hover Point */}
              <circle
                cx="66"
                cy="34"
                r="5"
                fill="#00f0ff"
                stroke="#00363a"
                strokeWidth="2"
                className="cursor-pointer animate-pulse"
                onMouseEnter={() => setHoverCoord({ x: '0.042', y: '0.930' })}
                onMouseLeave={() => setHoverCoord(null)}
              />
            </svg>

            {/* Legend */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[#31353f]/40 font-mono text-[11px]">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1.5 text-[#dbfcff]">
                  <span className="w-3 h-0.5 bg-[#00f0ff]"></span>
                  Logistic Regression (AUC 0.984)
                </span>
                <span className="flex items-center gap-1.5 text-[#d0bcff]">
                  <span className="w-3 h-0.5 bg-[#d0bcff]"></span>
                  SVC RBF (0.979)
                </span>
                <span className="flex items-center gap-1.5 text-[#7bd0ff]">
                  <span className="w-3 h-0.5 bg-[#7bd0ff]"></span>
                  Random Forest (0.974)
                </span>
              </div>
              <span className="text-[#849495]">Random Guess (0.50)</span>
            </div>
          </div>

          <div className="font-mono text-xs text-[#b9cacb] flex items-center justify-between">
            <span>Discrimination Threshold: τ = 0.500</span>
            <span>Decision Boundary: w·x + b = 0</span>
            <span className="text-[#00dbe9]">Area Under Curve: 0.9841</span>
          </div>
        </div>

        {/* Right: Confusion Matrix + Feature Weights (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Confusion Matrix */}
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs text-[#849495] uppercase tracking-wider">
                Test Confusion Matrix (N=114)
              </span>
              <span className="font-mono text-[10px] text-[#00dbe9]">Champion LR</span>
            </div>

            <div className="grid grid-cols-2 gap-2 mt-2 font-mono">
              {/* True Negative */}
              <div className="p-3 rounded-lg bg-[#0a0e17] border border-[#31353f]/40 flex flex-col justify-between">
                <div className="flex justify-between text-[10px] text-[#849495]">
                  <span>TRUE BENIGN (TN)</span>
                  <span className="text-[#00dbe9]">0.958</span>
                </div>
                <span className="text-2xl font-bold text-[#dbfcff] my-1">68</span>
                <span className="text-[10px] text-[#849495]">Predicted Negative</span>
              </div>

              {/* False Positive */}
              <div className="p-3 rounded-lg bg-[#1b2029] border border-[#31353f]/40 flex flex-col justify-between">
                <div className="flex justify-between text-[10px] text-[#849495]">
                  <span>FALSE MALIGNANT (FP)</span>
                  <span className="text-[#d0bcff]">0.042</span>
                </div>
                <span className="text-2xl font-bold text-[#dfe2f0] my-1">3</span>
                <span className="text-[10px] text-[#849495]">Type I Error</span>
              </div>

              {/* False Negative */}
              <div className="p-3 rounded-lg bg-[#1b2029] border border-[#31353f]/40 flex flex-col justify-between">
                <div className="flex justify-between text-[10px] text-[#849495]">
                  <span>FALSE BENIGN (FN)</span>
                  <span className="text-[#d0bcff]">0.070</span>
                </div>
                <span className="text-2xl font-bold text-[#dfe2f0] my-1">3</span>
                <span className="text-[10px] text-[#849495]">Type II Error</span>
              </div>

              {/* True Positive */}
              <div className="p-3 rounded-lg bg-[#0a0e17] border border-[#00f0ff]/30 flex flex-col justify-between">
                <div className="flex justify-between text-[10px] text-[#849495]">
                  <span>TRUE MALIGNANT (TP)</span>
                  <span className="text-[#00dbe9]">0.930</span>
                </div>
                <span className="text-2xl font-bold text-[#00f0ff] my-1">40</span>
                <span className="text-[10px] text-[#849495]">Predicted Positive</span>
              </div>
            </div>

            <div className="mt-3 pt-2 border-t border-[#31353f]/40 font-mono text-[11px] text-[#b9cacb] flex justify-between">
              <span>Recall: 93.0%</span>
              <span>Precision: 93.0%</span>
              <span>Specificity: 95.8%</span>
            </div>
          </div>

          {/* Standardized Beta Weights */}
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md">
            <div className="flex items-center justify-between mb-3">
              <span className="font-mono text-xs text-[#849495] uppercase tracking-wider">
                Logistic Model Coefficients (Standardized β)
              </span>
              <span className="font-mono text-[10px] text-[#00dbe9]">L2 Penalty</span>
            </div>

            <div className="space-y-2.5 font-mono text-xs">
              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-[#dfe2f0]">PCA Dim 0 (radius_mean)</span>
                  <span className="text-[#00dbe9] font-bold">+1.842</span>
                </div>
                <div className="h-2 w-full rounded bg-[#0a0e17] overflow-hidden">
                  <div className="h-full rounded bg-[#00f0ff]" style={{ width: '92%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-[#dfe2f0]">PCA Dim 1 (concavity_mean)</span>
                  <span className="text-[#00dbe9] font-bold">+1.419</span>
                </div>
                <div className="h-2 w-full rounded bg-[#0a0e17] overflow-hidden">
                  <div className="h-full rounded bg-[#00dbe9]" style={{ width: '71%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-[#dfe2f0]">PCA Dim 2 (texture_mean)</span>
                  <span className="text-[#00dbe9] font-bold">+0.978</span>
                </div>
                <div className="h-2 w-full rounded bg-[#0a0e17] overflow-hidden">
                  <div className="h-full rounded bg-[#7df4ff]" style={{ width: '49%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-[#dfe2f0]">PCA Dim 3 (perimeter_mean)</span>
                  <span className="text-[#00dbe9] font-bold">+0.651</span>
                </div>
                <div className="h-2 w-full rounded bg-[#0a0e17] overflow-hidden">
                  <div className="h-full rounded bg-[#aee0ff]" style={{ width: '33%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom 3 Summary Protocol Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
        <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 space-y-1">
          <span className="text-[#849495] text-[10px] block uppercase">01 // PRE-CONDITIONING</span>
          <h4 className="text-sm font-semibold text-[#dfe2f0]">Data Pre-Conditioning</h4>
          <p className="text-[#b9cacb] leading-relaxed text-[11px] font-sans">
            10 original nuclear morphology features reduced to 4 orthogonal principal components via PCA. Retains 91.2% total variance.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 space-y-1">
          <span className="text-[#849495] text-[10px] block uppercase">02 // KERNEL EQUIVALENCE</span>
          <h4 className="text-sm font-semibold text-[#dfe2f0]">Kernel Equivalence Test</h4>
          <p className="text-[#b9cacb] leading-relaxed text-[11px] font-sans">
            Classical RBF SVM (gamma=‘scale’, C=1.0) achieves F1=0.9272. Outperforms simulated quantum kernel QSVC by +0.0182.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/40 space-y-1">
          <span className="text-[#849495] text-[10px] block uppercase">03 // DETERMINISM AUDIT</span>
          <h4 className="text-sm font-semibold text-[#dfe2f0]">Audit Trail Complete</h4>
          <p className="text-[#b9cacb] leading-relaxed text-[11px] font-sans">
            All 114 test samples evaluated under random_state=42. Deterministic execution seed verified: 0x4B3A8F.
          </p>
        </div>
      </div>
    </div>
  );
};
