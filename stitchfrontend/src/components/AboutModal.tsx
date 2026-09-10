import React from 'react';
import { X, ShieldAlert, CheckCircle2, Award, Info, ExternalLink } from 'lucide-react';

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AboutModal: React.FC<AboutModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-150">
      <div className="w-full max-w-2xl max-h-[85vh] overflow-y-auto bg-[#0f131d] rounded-2xl border border-[#31353f] p-6 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#31353f] pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#571bc1]/30 flex items-center justify-center text-[#d0bcff]">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-[#dbfcff]">
                About LAKSHYA & Research Boundaries
              </h2>
              <p className="text-xs text-[#b9cacb]">
                SIH 2026 Problem Statement SIH26139 · Team Mirage declaration.
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

        {/* Declaration content */}
        <div className="space-y-4 font-sans text-xs text-[#b9cacb] leading-relaxed">
          <div className="p-4 rounded-xl bg-[#262a34]/60 border border-[#00f0ff]/30 space-y-2">
            <span className="font-mono text-[10px] text-[#00dbe9] uppercase font-bold block">
              1. MANDATORY NON-CLINICAL DISCLAIMER
            </span>
            <p className="text-[#dfe2f0]">
              LAKSHYA is an academic, exploratory machine learning benchmarking sandbox created exclusively for Smart India Hackathon (SIH) 2026.
            </p>
            <p className="text-[#dfe2f0] font-semibold">
              It is NOT a medical device, NOT software as a medical device (SaMD), NOT cleared or approved by the FDA, CDSCO, or any health authority, and MUST NEVER be used for diagnostic, prognostic, or clinical treatment decisions.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 space-y-2">
            <span className="font-mono text-[10px] text-[#d0bcff] uppercase font-bold block">
              2. SCIENTIFIC OBJECTIVE & HYPOTHESIS
            </span>
            <p>
              The central hypothesis of this study asks: <em>"Does embedding tabular clinical records into a simulated Hilbert feature space via parameterized quantum circuits yield an empirical advantage over optimal classical baselines?"</em>
            </p>
            <p>
              Our rigorous empirical finding reveals that standard Logistic Regression (F1 = 0.932) and Support Vector Machines (F1 = 0.927) meet or exceed the performance of Quantum Support Vector Classifiers (F1 = 0.909) and Variational Quantum Classifiers (F1 = 0.865) on public Wisconsin tabular data. We explicitly report this result to resist misleading claims of "quantum superiority" on tabular biomedical datasets.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 space-y-2">
            <span className="font-mono text-[10px] text-[#849495] uppercase font-bold block">
              3. TEAM & COMPETITION METADATA
            </span>
            <div className="grid grid-cols-2 gap-2 font-mono text-[11px] text-[#dfe2f0]">
              <div>
                <span className="text-[#849495] block text-[10px]">ORGANIZATION</span>
                <span>Smart India Hackathon 2026</span>
              </div>
              <div>
                <span className="text-[#849495] block text-[10px]">TEAM NAME</span>
                <span className="text-[#00dbe9]">Team Mirage</span>
              </div>
              <div>
                <span className="text-[#849495] block text-[10px]">PROBLEM STATEMENT</span>
                <span>SIH26139</span>
              </div>
              <div>
                <span className="text-[#849495] block text-[10px]">SIMULATOR BACKEND</span>
                <span>Qiskit Aer Statevector (Noise=0.0)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-3 border-t border-[#31353f]">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-lg bg-[#00f0ff] text-[#00363a] font-bold text-xs hover:bg-[#7df4ff] transition-all"
          >
            Acknowledge
          </button>
        </div>
      </div>
    </div>
  );
};
