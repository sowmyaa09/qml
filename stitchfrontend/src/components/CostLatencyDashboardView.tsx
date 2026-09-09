import React, { useEffect, useMemo, useState } from 'react';
import { Clock, Cpu, TrendingUp, Zap, AlertTriangle, RefreshCw } from 'lucide-react';
import { fetchQmlCostLatency, QmlCostLatencyPayload } from '../api';

type AblationRow = {
  k: number;
  model: string;
  f1: number;
  fit_seconds?: number;
  predict_seconds?: number;
  total_seconds?: number;
};

type ModelRow = {
  model: string;
  f1: number;
  fit_seconds?: number;
  predict_seconds?: number;
  total_seconds?: number;
};

function totalSeconds(row: { fit_seconds?: number; predict_seconds?: number; total_seconds?: number }) {
  if (row.total_seconds != null) return row.total_seconds;
  return (row.fit_seconds ?? 0) + (row.predict_seconds ?? 0);
}

function AblationChart({ rows }: { rows: AblationRow[] }) {
  const ks = [...new Set(rows.map((r) => r.k))].sort((a, b) => a - b);
  const qsvc = ks.map((k) => rows.find((r) => r.k === k && r.model === 'QSVC')).filter(Boolean) as AblationRow[];
  const rbf = ks.map((k) => rows.find((r) => r.k === k && r.model === 'RBF SVM')).filter(Boolean) as AblationRow[];

  const w = 520;
  const h = 220;
  const pad = { l: 44, r: 44, t: 16, b: 36 };
  const innerW = w - pad.l - pad.r;
  const innerH = h - pad.t - pad.b;

  const xAt = (i: number) => pad.l + (i / Math.max(ks.length - 1, 1)) * innerW;
  const yF1 = (f1: number) => pad.t + (1 - f1) * innerH;
  const maxSec = Math.max(...qsvc.map((r) => totalSeconds(r)), 0.1);
  const ySec = (sec: number) => pad.t + (1 - sec / maxSec) * innerH;

  const line = (pts: { x: number; y: number }[]) =>
    pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ');

  const qsvcF1Pts = qsvc.map((r, i) => ({ x: xAt(i), y: yF1(r.f1) }));
  const rbfF1Pts = rbf.map((r, i) => ({ x: xAt(i), y: yF1(r.f1) }));
  const qsvcSecPts = qsvc.map((r, i) => ({ x: xAt(i), y: ySec(totalSeconds(r)) }));

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-auto" role="img" aria-label="Ablation F1 and latency by qubit count">
      {[0, 0.25, 0.5, 0.75, 1].map((t) => {
        const y = pad.t + t * innerH;
        return (
          <line key={t} x1={pad.l} y1={y} x2={w - pad.r} y2={y} stroke="#31353f" strokeWidth="1" />
        );
      })}
      <path d={line(qsvcF1Pts)} fill="none" stroke="#00f0ff" strokeWidth="2.5" />
      <path d={line(rbfF1Pts)} fill="none" stroke="#a78bfa" strokeWidth="2" strokeDasharray="6 4" />
      <path d={line(qsvcSecPts)} fill="none" stroke="#849495" strokeWidth="2" strokeDasharray="2 3" />
      {qsvcF1Pts.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r="4" fill="#00f0ff" />
      ))}
      {ks.map((k, i) => (
        <text key={k} x={xAt(i)} y={h - 10} textAnchor="middle" fill="#849495" fontSize="11" fontFamily="monospace">
          k={k}
        </text>
      ))}
      <text x={8} y={pad.t + 8} fill="#849495" fontSize="10" fontFamily="monospace">
        F1
      </text>
      <text x={w - 36} y={pad.t + 8} fill="#849495" fontSize="10" fontFamily="monospace">
        sec
      </text>
    </svg>
  );
}

function HeadlineBars({ rows }: { rows: ModelRow[] }) {
  const sorted = [...rows].sort((a, b) => totalSeconds(b) - totalSeconds(a));
  const maxSec = Math.max(...sorted.map(totalSeconds), 0.01);

  return (
    <div className="space-y-3">
      {sorted.map((row) => {
        const sec = totalSeconds(row);
        const widthPct = Math.min(100, (sec / maxSec) * 100);
        const isQuantum = /QSVC|VQC|QNN/i.test(row.model);
        return (
          <div key={row.model} className="space-y-1">
            <div className="flex justify-between font-mono text-xs">
              <span className={isQuantum ? 'text-[#00dbe9]' : 'text-[#dfe2f0]'}>{row.model}</span>
              <span className="text-[#849495]">
                F1 {(row.f1 * 100).toFixed(1)}% · {sec < 1 ? sec.toFixed(2) : sec.toFixed(0)}s fit
              </span>
            </div>
            <div className="h-2 rounded-full bg-[#0a0e17] overflow-hidden">
              <div
                className={`h-full rounded-full ${isQuantum ? 'bg-[#00f0ff]/70' : 'bg-[#571bc1]/60'}`}
                style={{ width: `${widthPct}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export const CostLatencyDashboardView: React.FC = () => {
  const [data, setData] = useState<QmlCostLatencyPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = () => {
    setLoading(true);
    setError('');
    fetchQmlCostLatency()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const insight = data?.insight;
  const usingFallback = data?.ablation_source === 'fallback' || data?.headline_source === 'fallback';

  const legend = useMemo(
    () => [
      { color: 'bg-[#00f0ff]', label: 'QSVC F1' },
      { color: 'bg-[#a78bfa]', label: 'RBF SVM F1' },
      { color: 'bg-[#849495]', label: 'QSVC seconds (right scale)' },
    ],
    []
  );

  return (
    <div className="w-full max-w-6xl mx-auto px-4 md:px-6 py-6 pb-16 space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
              <Clock className="w-3.5 h-3.5" />
            </span>
            <span className="font-mono text-xs uppercase text-[#00dbe9] tracking-widest">
              PROTOCOL 03-C / COST & LATENCY BENCHMARK
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
            Quantum Cost & Latency Dashboard
          </h1>
          <p className="text-xs md:text-sm text-[#b9cacb] max-w-3xl mt-1 leading-relaxed">
            F1 vs wall-clock seconds vs qubit count on Wisconsin (simulator). Pitch efficiency and
            honesty — QSVC can tie classical F1 while costing orders of magnitude longer to train.
          </p>
        </div>
        <button
          type="button"
          onClick={load}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-2 rounded-xl bg-[#262a34] border border-[#31353f] text-xs font-mono text-[#b9cacb] hover:text-[#dfe2f0] disabled:opacity-60"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error ? (
        <p className="text-sm text-[#ffb4ab] font-mono">{error}</p>
      ) : null}

      {usingFallback && data ? (
        <div className="flex items-start gap-2 p-3 rounded-xl bg-[#571bc1]/20 border border-[#571bc1]/40 text-xs text-[#e9ddff]">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Showing documented fallback metrics</p>
            <p className="text-[#c9b8ff] mt-1 font-mono">
              Run: {data.train_commands.join(' · ')} to load live CSVs from this machine.
            </p>
          </div>
        </div>
      ) : null}

      {insight && Object.keys(insight).length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#00f0ff]/30">
            <span className="font-mono text-[10px] text-[#849495] uppercase">F1 parity</span>
            <p className="text-2xl font-bold text-[#dbfcff] mt-1">
              QSVC {(insight.qsvc_f1! * 100).toFixed(1)}% · RBF {(insight.rbf_f1! * 100).toFixed(1)}%
            </p>
            <p className="text-xs text-[#b9cacb] mt-1">ΔF1 {(insight.f1_delta! * 100).toFixed(2)} pp</p>
          </div>
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#571bc1]/40">
            <span className="font-mono text-[10px] text-[#849495] uppercase">Fit latency</span>
            <p className="text-2xl font-bold text-[#e9ddff] mt-1">
              ~{insight.latency_ratio!.toFixed(0)}× slower
            </p>
            <p className="text-xs text-[#b9cacb] mt-1">
              QSVC {insight.qsvc_seconds!.toFixed(2)}s vs RBF {insight.rbf_seconds!.toFixed(2)}s
            </p>
          </div>
          <div className="p-4 rounded-xl bg-[#171c25] border border-[#31353f]/50 flex items-center gap-3">
            <Zap className="w-8 h-8 text-[#00dbe9] shrink-0" />
            <p className="text-xs text-[#b9cacb] leading-relaxed">{insight.verdict}</p>
          </div>
        </div>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-5 rounded-xl bg-[#171c25] border border-[#31353f]/50 space-y-4">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-[#00dbe9]" />
            <h2 className="font-bold text-[#dbfcff]">Qubits vs F1 &amp; seconds</h2>
          </div>
          <p className="text-xs text-[#849495]">
            Ablation sweep (k = 4, 6, 8). One qubit per SelectKBest column; same train/test split.
          </p>
          {data?.ablation?.length ? <AblationChart rows={data.ablation as AblationRow[]} /> : null}
          <div className="flex flex-wrap gap-3">
            {legend.map((item) => (
              <span key={item.label} className="flex items-center gap-1.5 text-[10px] font-mono text-[#849495]">
                <span className={`w-3 h-1 rounded ${item.color}`} />
                {item.label}
              </span>
            ))}
          </div>
          {data?.figure_url ? (
            <img
              src={data.figure_url}
              alt="QML ablation plot from training run"
              className="w-full rounded-lg border border-[#31353f]/40"
            />
          ) : null}
        </div>

        <div className="p-5 rounded-xl bg-[#171c25] border border-[#31353f]/50 space-y-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-[#00dbe9]" />
            <h2 className="font-bold text-[#dbfcff]">Headline models (k=6)</h2>
          </div>
          <p className="text-xs text-[#849495]">Bar length = fit wall-clock seconds (log-scale feel).</p>
          {data?.headline_models?.length ? (
            <HeadlineBars rows={data.headline_models as ModelRow[]} />
          ) : null}
        </div>
      </div>

      <p className="text-[10px] font-mono text-[#849495] text-center">
        {data?.disclaimer ?? 'Research risk classification — not for clinical use.'}
      </p>
    </div>
  );
};
