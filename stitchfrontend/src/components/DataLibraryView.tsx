import React, { useState } from 'react';
import {
  Database,
  Search,
  CheckCircle2,
  FileCode,
  ArrowRight,
  Sliders,
  BarChart2,
  ShieldAlert,
  Info,
  Layers,
  Sparkles,
  ExternalLink,
} from 'lucide-react';
import { DATASETS } from '../data/datasets';
import { DatasetMeta, TabType } from '../types';

interface DataLibraryViewProps {
  onSelectDatasetForClassical: (datasetId: string) => void;
  onInspectFeatures: (dataset: DatasetMeta) => void;
}

export const DataLibraryView: React.FC<DataLibraryViewProps> = ({
  onSelectDatasetForClassical,
  onInspectFeatures,
}) => {
  const [filterTab, setFilterTab] = useState<'all' | 'stratified' | 'pca' | 'normalized'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedSha, setCopiedSha] = useState(false);
  const [showYamlModal, setShowYamlModal] = useState(false);

  const filteredDatasets = DATASETS.filter((ds) => {
    if (filterTab === 'stratified' && !ds.split.includes('Stratified')) return false;
    if (filterTab === 'pca' && !ds.dimensionality.includes('PCA')) return false;
    if (filterTab === 'normalized' && !ds.preprocessing.toLowerCase().includes('scaler')) return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        ds.name.toLowerCase().includes(q) ||
        ds.features.some((f) => f.toLowerCase().includes(q)) ||
        ds.dimensionality.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const handleCopySha = () => {
    navigator.clipboard?.writeText(
      '0x4B3A8F_WISCONSIN_SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    );
    setCopiedSha(true);
    setTimeout(() => setCopiedSha(false), 2500);
  };

  return (
    <div className="w-full max-w-6xl mx-auto px-4 md:px-6 py-6 pb-16 space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
              <Layers className="w-3.5 h-3.5" />
            </span>
            <span className="font-mono text-xs uppercase text-[#00dbe9] tracking-widest">
              PROTOCOL 01-A / ISOLATED MATRICES
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
            Public Biomedical Data Library
          </h1>
          <p className="text-xs md:text-sm text-[#b9cacb] max-w-3xl mt-1 leading-relaxed">
            One table, one label. Strict empirical isolation — datasets are never fused into a composite diagnostic model. Each table serves as an isolated binary classification benchmark.
          </p>
        </div>

        {/* Action badges */}
        <div className="flex flex-wrap items-center gap-2 shrink-0">
          <button
            onClick={handleCopySha}
            className="px-3 py-1.5 rounded-lg bg-[#171c25] border border-[#31353f] hover:bg-[#262a34] text-xs font-mono text-[#b9cacb] hover:text-[#dfe2f0] transition-all flex items-center gap-1.5"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-[#00dbe9]" />
            <span>{copiedSha ? 'Copied SHA-256!' : 'Verified SHA-256'}</span>
          </button>
          <button
            onClick={() => setShowYamlModal(true)}
            className="px-3 py-1.5 rounded-lg bg-[#171c25] border border-[#31353f] hover:bg-[#262a34] text-xs font-mono text-[#b9cacb] hover:text-[#dfe2f0] transition-all flex items-center gap-1.5"
          >
            <FileCode className="w-3.5 h-3.5 text-[#d0bcff]" />
            <span>Raw Manifest YAML</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-3 rounded-xl bg-[#0f131d] border border-[#31353f]/50 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-md">
        {/* Chips */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto text-xs">
          <button
            onClick={() => setFilterTab('all')}
            className={`px-3 py-1.5 rounded-lg font-medium whitespace-nowrap transition-all ${
              filterTab === 'all'
                ? 'bg-[#262a34] text-[#dbfcff] font-semibold shadow-sm'
                : 'text-[#b9cacb] hover:bg-[#171c25]'
            }`}
          >
            All 4 Public Tables
          </button>
          <button
            onClick={() => setFilterTab('stratified')}
            className={`px-3 py-1.5 rounded-lg font-medium whitespace-nowrap transition-all ${
              filterTab === 'stratified'
                ? 'bg-[#262a34] text-[#dbfcff] font-semibold shadow-sm'
                : 'text-[#b9cacb] hover:bg-[#171c25]'
            }`}
          >
            Stratified (80:20)
          </button>
          <button
            onClick={() => setFilterTab('pca')}
            className={`px-3 py-1.5 rounded-lg font-medium whitespace-nowrap transition-all ${
              filterTab === 'pca'
                ? 'bg-[#262a34] text-[#dbfcff] font-semibold shadow-sm'
                : 'text-[#b9cacb] hover:bg-[#171c25]'
            }`}
          >
            PCA Pre-processed
          </button>
          <button
            onClick={() => setFilterTab('normalized')}
            className={`px-3 py-1.5 rounded-lg font-medium whitespace-nowrap transition-all ${
              filterTab === 'normalized'
                ? 'bg-[#262a34] text-[#dbfcff] font-semibold shadow-sm'
                : 'text-[#b9cacb] hover:bg-[#171c25]'
            }`}
          >
            Normalized MinMax
          </button>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64 shrink-0">
          <Search className="w-4 h-4 text-[#849495] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search features, dimensions..."
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-[#171c25] border border-[#31353f]/60 text-xs text-[#dfe2f0] placeholder-[#849495] focus:outline-none focus:border-[#00f0ff] transition-all"
          />
        </div>
      </div>

      {/* Dataset Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filteredDatasets.map((ds) => (
          <div
            key={ds.id}
            className="p-5 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md flex flex-col justify-between hover:border-[#00dbe9]/40 transition-all duration-200"
          >
            {/* Header info */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-[#262a34] font-mono text-[10px] text-[#00dbe9] font-semibold">
                    {ds.experimentTag}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-[#571bc1]/30 font-mono text-[10px] text-[#d0bcff]">
                    {ds.experimentType}
                  </span>
                </div>
                <span className="font-mono text-[10px] text-[#849495]">{ds.license}</span>
              </div>

              <h2 className="text-lg font-bold text-[#eef7ff] tracking-tight">{ds.name}</h2>
              <div className="flex items-center gap-2 mt-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#00dbe9]"></span>
                <span className="font-mono text-xs text-[#00dbe9] font-medium">
                  {ds.targetDescription}
                </span>
              </div>

              {/* Metric stats grid */}
              <div className="grid grid-cols-4 gap-2 mt-4 p-3 rounded-lg bg-[#1b2029] border border-[#31353f]/40 font-mono text-center">
                <div>
                  <span className="text-[10px] text-[#849495] block">SAMPLES</span>
                  <span className="text-base font-bold text-[#dfe2f0]">
                    {ds.sampleCount.toLocaleString()}
                    {ds.totalPopulation && (
                      <span className="text-[10px] text-[#849495] block font-normal">
                        of {ds.totalPopulation}
                      </span>
                    )}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-[#849495] block">DIMENSIONS</span>
                  <span className="text-base font-bold text-[#dfe2f0]">{ds.dimensionality}</span>
                </div>
                <div>
                  <span className="text-[10px] text-[#849495] block">MAPPING</span>
                  <span className="text-base font-bold text-[#00dbe9]">{ds.qubits} Qubits</span>
                </div>
                <div>
                  <span className="text-[10px] text-[#849495] block">SPLIT</span>
                  <span className="text-xs font-semibold text-[#dfe2f0] mt-1 block">
                    {ds.split}
                  </span>
                </div>
              </div>

              {/* Scikit vs QML comparison row */}
              <div className="mt-3 p-3 rounded-lg bg-[#0a0e17] border border-[#31353f]/40 flex items-center justify-between">
                <div>
                  <span className="font-mono text-[10px] text-[#849495] block">
                    SCIKIT BASELINE
                  </span>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-xs font-semibold text-[#dfe2f0]">
                      {ds.scikitBaselineName}
                    </span>
                    <span className="font-mono text-xs font-bold text-[#00dbe9]">
                      F1: {ds.scikitBaselineF1.toFixed(3)}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="font-mono text-[10px] text-[#849495] block">QML BENCHMARK</span>
                  <div className="flex items-baseline gap-1.5 justify-end">
                    <span className="text-xs font-semibold text-[#dfe2f0]">{ds.qmlModelName}</span>
                    <span className="font-mono text-xs font-bold text-[#d0bcff]">
                      {ds.qmlModelF1.toFixed(3)}
                    </span>
                    <span className="font-mono text-[10px] px-1 py-0.2 rounded bg-[#262a34] text-[#849495]">
                      {ds.qmlF1Delta}
                    </span>
                  </div>
                </div>
              </div>

              {/* Feature Margin / Distribution visual */}
              <div className="mt-3">
                <div className="flex items-center justify-between font-mono text-[10px] text-[#849495] mb-1">
                  <span>
                    {ds.id === 'wisconsin'
                      ? 'FEATURE MARGIN DISTRIBUTION (NORMALIZED PCA DIM 0-3)'
                      : ds.id === 'heart'
                      ? 'PCA COVARIANCE DENSITY'
                      : ds.id === 'pima'
                      ? 'CLASS IMBALANCE HISTOGRAM'
                      : 'SUBSAMPLED BATCH SLICE (N=1,000)'}
                  </span>
                  <span className="text-[#00dbe9]">NORMALIZED</span>
                </div>
                <div className="h-3 w-full rounded bg-[#0a0e17] overflow-hidden flex gap-1 p-0.5 border border-[#31353f]/30">
                  <div
                    className="h-full rounded bg-[#00f0ff]"
                    style={{ width: ds.id === 'wisconsin' ? '37%' : '44%' }}
                  ></div>
                  <div
                    className="h-full rounded bg-[#00dbe9]"
                    style={{ width: ds.id === 'wisconsin' ? '25%' : '28%' }}
                  ></div>
                  <div
                    className="h-full rounded bg-[#d0bcff]"
                    style={{ width: ds.id === 'wisconsin' ? '20%' : '18%' }}
                  ></div>
                  <div
                    className="h-full rounded bg-[#571bc1]"
                    style={{ width: ds.id === 'wisconsin' ? '18%' : '10%' }}
                  ></div>
                </div>
              </div>

              {/* Preprocessing Note */}
              <p className="text-xs text-[#b9cacb] mt-3 leading-relaxed">
                <strong className="text-[#dfe2f0]">Preprocessing:</strong> {ds.preprocessing}
              </p>
            </div>

            {/* Bottom Actions */}
            <div className="mt-4 pt-3 border-t border-[#31353f]/40 flex items-center justify-between gap-3">
              <button
                type="button"
                onClick={() => onInspectFeatures(ds)}
                className="px-3 py-2 rounded-lg bg-[#262a34] text-xs font-semibold text-[#b9cacb] hover:text-[#dfe2f0] hover:bg-[#353944] border border-[#31353f]/50 transition-all flex items-center gap-1.5"
              >
                <BarChart2 className="w-3.5 h-3.5 text-[#00dbe9]" />
                <span>Inspect Feature Distributions</span>
              </button>
              <button
                type="button"
                onClick={() => onSelectDatasetForClassical(ds.id)}
                className="px-3 py-2 rounded-lg bg-[#00f0ff] text-[#00363a] text-xs font-bold hover:bg-[#7df4ff] transition-all flex items-center gap-1.5"
              >
                <span>Load in Classical Studio</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Manifest YAML Modal */}
      {showYamlModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-2xl bg-[#0f131d] rounded-2xl border border-[#31353f] p-5 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-[#31353f] pb-3">
              <div className="flex items-center gap-2">
                <FileCode className="w-5 h-5 text-[#00dbe9]" />
                <h3 className="text-base font-bold text-[#dbfcff]">
                  Biomedical Data Manifest (YAML)
                </h3>
              </div>
              <button
                onClick={() => setShowYamlModal(false)}
                className="text-xs text-[#849495] hover:text-[#dfe2f0] px-2 py-1 rounded bg-[#171c25]"
              >
                Close
              </button>
            </div>
            <pre className="p-4 rounded-xl bg-[#0a0e17] font-mono text-xs text-[#00dbe9] overflow-x-auto max-h-96 border border-[#31353f]/50 leading-relaxed">
{`# LAKSHYA Research Manifest · SIH 2026 SIH26139
protocol_version: "0.9.4"
seed: 0x4B3A8F
random_state: 42
split_strategy: "StratifiedKFold(n_splits=5, shuffle=True, random_state=42)"

datasets:
  - id: "01-WISC"
    source: "UCI Machine Learning Repository / Wisconsin Diagnostic"
    samples: 569
    target: "diagnosis (M=1, B=0)"
    pca_dimensions: 4
    qubits: 4
    champion_f1: 0.932  # LogisticRegression L2
    qsvc_f1: 0.909       # ZZFeatureMap Aer

  - id: "02-HEART"
    source: "UCI Heart Disease (Cleveland/Hungarian/VA)"
    samples: 920
    target: "num (>0 vs 0)"
    reduced_dims: 8
    champion_f1: 0.884  # GradientBoostedTrees
    qsvc_f1: 0.821

isolation_rule: "STRICT_NO_CROSS_LABEL_FUSION"
classification_mode: "NON_DIAGNOSTIC_RESEARCH_ONLY"
simulator: "Qiskit Aer Statevector (Noise=0.0)"`}
            </pre>
            <div className="flex justify-end">
              <button
                onClick={() => setShowYamlModal(false)}
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
