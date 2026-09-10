import React from 'react';
import { X, BookOpen, Scale, Cpu, Activity, Info } from 'lucide-react';

interface MetricsGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MetricsGuideModal: React.FC<MetricsGuideModalProps> = ({
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-150">
      <div className="w-full max-w-3xl max-h-[85vh] overflow-y-auto bg-[#0f131d] rounded-2xl border border-[#31353f] p-6 shadow-2xl space-y-6">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-[#31353f] pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
              <BookOpen className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-[#dbfcff]">
                Research Metrics & Formulation Guide
              </h2>
              <p className="text-xs text-[#b9cacb]">
                Mathematical standards for evaluating classical vs hybrid quantum classifiers.
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

        {/* Content Sections */}
        <div className="space-y-4 font-sans text-xs text-[#b9cacb] leading-relaxed">
          {/* Item 1: F1 Score vs ROC-AUC */}
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 space-y-2">
            <div className="flex items-center gap-2 text-sm font-bold text-[#eef7ff]">
              <Scale className="w-4 h-4 text-[#00dbe9]" />
              <span>1. Stratified F1-Score vs. ROC-AUC in Medical Tabular Data</span>
            </div>
            <p>
              In biomedical tabular tasks with potential class imbalance (e.g. 63% benign, 37% malignant), raw accuracy can be deceptive. The harmonic mean of precision and recall:
            </p>
            <div className="p-2.5 rounded-lg bg-[#0a0e17] font-mono text-center text-[#00f0ff] border border-[#31353f]/40">
              F₁ = 2 · (Precision · Recall) / (Precision + Recall)
            </div>
            <p>
              Our primary evaluation benchmark prioritizes F1 over raw accuracy because false negatives in risk indicators have disproportionate empirical weight.
            </p>
          </div>

          {/* Item 2: McNemar's Test */}
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 space-y-2">
            <div className="flex items-center gap-2 text-sm font-bold text-[#eef7ff]">
              <Activity className="w-4 h-4 text-[#d0bcff]" />
              <span>2. McNemar's Test for Paired Classifier Comparison</span>
            </div>
            <p>
              Rather than comparing aggregate accuracies, McNemar's non-parametric test evaluates the contingency matrix of discordant predictions between Model A (QSVC) and Model B (Classical SVC):
            </p>
            <div className="p-2.5 rounded-lg bg-[#0a0e17] font-mono text-center text-[#d0bcff] border border-[#31353f]/40">
              χ² = (|b - c| - 1)² / (b + c)
            </div>
            <p>
              Where <em>b</em> is instances where Model A is correct and Model B incorrect, and <em>c</em> vice versa. On Wisconsin (b=4, c=4), p=1.000 confirms neither model has a statistically significant advantage.
            </p>
          </div>

          {/* Item 3: Quantum Kernel Estimation */}
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 space-y-2">
            <div className="flex items-center gap-2 text-sm font-bold text-[#eef7ff]">
              <Cpu className="w-4 h-4 text-[#00dbe9]" />
              <span>3. Quantum Kernel Estimation via Pauli Feature Mapping</span>
            </div>
            <p>
              Classical tabular feature vector x is embedded into 2ⁿ-dimensional Hilbert state space via unitary transformation U(x):
            </p>
            <div className="p-2.5 rounded-lg bg-[#0a0e17] font-mono text-center text-[#00f0ff] border border-[#31353f]/40">
              K(xᵢ, xⱼ) = |⟨0| U†(xᵢ) U(xⱼ) |0⟩|² = |⟨ψ(xᵢ)|ψ(xⱼ)⟩|²
            </div>
            <p>
              The resulting Gram matrix is fed into a classical dual quadratic solver. In tabular domains without periodic structure, classical RBF achieves equal or superior fidelity.
            </p>
          </div>

          {/* Item 4: Barren Plateaus */}
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 space-y-2">
            <div className="flex items-center gap-2 text-sm font-bold text-[#eef7ff]">
              <Info className="w-4 h-4 text-[#7df4ff]" />
              <span>4. Barren Plateaus in Variational Quantum Classifiers (VQC)</span>
            </div>
            <p>
              As the number of qubits and circuit depth scale, random Haar-distributed parameterized quantum circuits experience an exponential decay in gradient variance:
            </p>
            <div className="p-2.5 rounded-lg bg-[#0a0e17] font-mono text-center text-[#7df4ff] border border-[#31353f]/40">
              Var[∂θᵢ C] ~ O(1 / 2ⁿ)
            </div>
            <p>
              This explains why VQC (RealAmplitudes) required 34s of optimization and plateaued at F1=0.865, underperforming both QSVC and classical Logistic Regression.
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex justify-end pt-3 border-t border-[#31353f]">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-lg bg-[#00f0ff] text-[#00363a] font-bold text-xs hover:bg-[#7df4ff] transition-all"
          >
            Understood
          </button>
        </div>
      </div>
    </div>
  );
};
