import React from 'react';
import { X, BarChart2, ArrowRight, Layers, Database } from 'lucide-react';
import { DatasetMeta } from '../types';

interface FeatureDistributionModalProps {
  dataset: DatasetMeta | null;
  onClose: () => void;
  onLoadInClassical: (datasetId: string) => void;
}

export const FeatureDistributionModal: React.FC<FeatureDistributionModalProps> = ({
  dataset,
  onClose,
  onLoadInClassical,
}) => {
  if (!dataset) return null;

  // Mock statistical distributions for the features
  const stats = dataset.features.map((feat, idx) => ({
    name: feat,
    mean: (12.4 + idx * 4.2).toFixed(2),
    std: (2.1 + idx * 1.1).toFixed(2),
    min: (6.8 + idx * 2.0).toFixed(2),
    median: (11.9 + idx * 3.8).toFixed(2),
    max: (24.5 + idx * 6.5).toFixed(2),
    pcaWeight: (0.48 - idx * 0.08).toFixed(3),
  }));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-150">
      <div className="w-full max-w-3xl max-h-[85vh] overflow-y-auto bg-[#0f131d] rounded-2xl border border-[#31353f] p-6 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#31353f] pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
              <BarChart2 className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-[#dbfcff]">{dataset.name}</h2>
                <span className="px-2 py-0.5 rounded bg-[#262a34] font-mono text-[10px] text-[#00dbe9]">
                  {dataset.dimensionality}
                </span>
              </div>
              <p className="text-xs text-[#b9cacb]">
                Empirical feature distribution matrix & PCA variance loading scores.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="btn-icon"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Feature Distribution Table */}
        <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 space-y-3">
          <div className="flex items-center justify-between font-mono text-xs text-[#849495]">
            <span>FEATURE SUMMARY (N={dataset.sampleCount})</span>
            <span className="text-[#00dbe9]">Standardized via StandardScaler</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs border-collapse">
              <thead>
                <tr className="border-b border-[#31353f]/60 text-[#849495] text-[10px] uppercase">
                  <th className="py-2 px-3">FEATURE</th>
                  <th className="py-2 px-3">MEAN</th>
                  <th className="py-2 px-3">STD</th>
                  <th className="py-2 px-3">MIN</th>
                  <th className="py-2 px-3">MEDIAN</th>
                  <th className="py-2 px-3">MAX</th>
                  <th className="py-2 px-3 text-[#00dbe9]">PCA LOADING</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#31353f]/40 text-[#dfe2f0]">
                {stats.map((row, i) => (
                  <tr key={i} className="hover:bg-[#1b2029] transition-colors">
                    <td className="py-2.5 px-3 font-semibold text-[#dbfcff]">{row.name}</td>
                    <td className="py-2.5 px-3">{row.mean}</td>
                    <td className="py-2.5 px-3 text-[#849495]">{row.std}</td>
                    <td className="py-2.5 px-3">{row.min}</td>
                    <td className="py-2.5 px-3">{row.median}</td>
                    <td className="py-2.5 px-3">{row.max}</td>
                    <td className="py-2.5 px-3 text-[#00f0ff] font-bold">+{row.pcaWeight}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Visual density histograms */}
        <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 space-y-3 font-mono text-xs">
          <span className="text-[#849495] uppercase text-[10px] block">
            NORMALIZED CLASS SEPARATION DENSITY BY DIMENSION
          </span>

          <div className="space-y-3">
            {stats.slice(0, 4).map((feat, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-[11px]">
                  <span className="text-[#dfe2f0]">{feat.name}</span>
                  <span className="text-[#00dbe9]">Separation Index: {(0.85 - idx * 0.12).toFixed(2)}</span>
                </div>
                <div className="h-3 w-full rounded bg-[#0a0e17] overflow-hidden flex gap-0.5 p-0.5 border border-[#31353f]/30">
                  <div
                    className="h-full rounded bg-[#00f0ff]"
                    style={{ width: `${Math.max(15, 65 - idx * 12)}%` }}
                  ></div>
                  <div
                    className="h-full rounded bg-[#d0bcff]"
                    style={{ width: `${Math.min(50, 20 + idx * 8)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>

          <div className="flex items-center gap-4 text-[10px] text-[#849495] pt-2 border-t border-[#31353f]/30">
            <span className="flex items-center gap-1.5 text-[#00dbe9]">
              <span className="w-2 h-2 rounded-full bg-[#00f0ff]"></span>
              Class 0 (Negative / Benign Density)
            </span>
            <span className="flex items-center gap-1.5 text-[#d0bcff]">
              <span className="w-2 h-2 rounded-full bg-[#d0bcff]"></span>
              Class 1 (Positive / Malignant Density)
            </span>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-3 border-t border-[#31353f]">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-[#171c25] hover:bg-[#262a34] text-xs font-semibold text-[#b9cacb] transition-all"
          >
            Close
          </button>
          <button
            onClick={() => {
              onLoadInClassical(dataset.id);
              onClose();
            }}
            className="px-5 py-2 rounded-lg bg-[#00f0ff] hover:bg-[#7df4ff] text-[#00363a] font-bold text-xs transition-all flex items-center gap-1.5 shadow-sm"
          >
            <span>Load in Classical Studio</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
