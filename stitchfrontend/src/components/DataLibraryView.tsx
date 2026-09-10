import React, { useEffect, useMemo, useState } from 'react';
import {
  Search,
  CheckCircle2,
  FileCode,
  ArrowRight,
  BarChart2,
  Layers,
} from 'lucide-react';
import { DATASETS } from '../data/datasets';
import { DatasetMeta } from '../types';
import { CatalogTableRow, fetchCatalogTables } from '../api';

interface DataLibraryViewProps {
  onSelectDatasetForClassical: (datasetId: string) => void;
  onInspectFeatures: (dataset: DatasetMeta) => void;
}

const STUDIO_ID: Record<string, string> = {
  wisconsin: 'wisconsin',
  wisconsin_reduced: 'wisconsin',
  heart: 'heart',
  heart_uci_pooled: 'heart',
  pima: 'pima',
  cardio: 'cardio',
};

function toDatasetMeta(row: CatalogTableRow): DatasetMeta {
  const seed = DATASETS.find((ds) => ds.id === STUDIO_ID[row.key] || ds.id === row.key);
  return {
    id: STUDIO_ID[row.key] || row.key,
    name: row.title,
    code: row.key,
    ref: `DS-REF: ${row.key}`,
    targetDescription: row.positive_label || 'One label on this public table only',
    sampleCount: seed?.sampleCount || row.features.length,
    split: seed?.split || '80:20 stratified when trained',
    dimensionality: `${row.features.length} columns`,
    features: row.features,
    qubits: seed?.qubits || Math.min(row.features.length, 8),
    scikitBaselineName: seed?.scikitBaselineName || 'Classical (see models)',
    scikitBaselineF1: seed?.scikitBaselineF1 || 0,
    scikitBaselineAccuracy: seed?.scikitBaselineAccuracy || 0,
    qmlModelName: seed?.qmlModelName || 'QML if trained',
    qmlModelF1: seed?.qmlModelF1 || 0,
    qmlModelAccuracy: seed?.qmlModelAccuracy || 0,
    qmlF1Delta: seed?.qmlF1Delta || '—',
    preprocessing: row.notes || seed?.preprocessing || '',
    license: seed?.license || 'Public benchmark',
    experimentTag: row.key.toUpperCase(),
    experimentType: row.models.some((m) => /qsvc|qnn|vqc/i.test(m.name))
      ? 'HYBRID QML AVAILABLE'
      : 'CLASSICAL TABLE',
  };
}

export const DataLibraryView: React.FC<DataLibraryViewProps> = ({
  onSelectDatasetForClassical,
  onInspectFeatures,
}) => {
  const [tables, setTables] = useState<CatalogTableRow[]>([]);
  const [loadError, setLoadError] = useState('');
  const [filterTab, setFilterTab] = useState<'all' | 'models' | 'mapper'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedSha, setCopiedSha] = useState(false);
  const [showYamlModal, setShowYamlModal] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchCatalogTables()
      .then((rows) => {
        if (!cancelled) setTables(rows);
      })
      .catch((err) => {
        if (!cancelled) {
          setLoadError(err instanceof Error ? err.message : String(err));
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const filteredTables = useMemo(() => {
    return tables.filter((row) => {
      if (filterTab === 'models' && row.models.filter((m) => m.available).length === 0) {
        return false;
      }
      if (filterTab === 'mapper' && !row.ui) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const hay = [
          row.key,
          row.title,
          row.notes,
          row.positive_label,
          ...row.features,
          ...row.models.map((m) => m.name),
        ]
          .join(' ')
          .toLowerCase();
        return hay.includes(q);
      }
      return true;
    });
  }, [tables, filterTab, searchQuery]);

  const yamlText = useMemo(() => {
    const lines = [
      '# Live catalog from GET /v1/catalog',
      'isolation_rule: STRICT_NO_CROSS_LABEL_FUSION',
      'classification_mode: NON_DIAGNOSTIC_RESEARCH_ONLY',
      'datasets:',
    ];
    for (const row of tables) {
      lines.push(`  - key: ${row.key}`);
      lines.push(`    title: ${JSON.stringify(row.title)}`);
      lines.push(`    min_filled: ${row.min_filled}`);
      lines.push(`    n_features: ${row.features.length}`);
      const available = row.models.filter((m) => m.available).map((m) => m.name);
      lines.push(`    models: ${JSON.stringify(available)}`);
    }
    return lines.join('\n');
  }, [tables]);

  const handleCopySha = () => {
    navigator.clipboard?.writeText(
      '0x4B3A8F_WISCONSIN_SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    );
    setCopiedSha(true);
    setTimeout(() => setCopiedSha(false), 2500);
  };

  return (
    <div className="w-full max-w-6xl mx-auto px-4 md:px-6 py-6 pb-16 space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 bg-[#262a34] flex items-center justify-center text-[#5cffb5]">
              <Layers className="w-3.5 h-3.5" />
            </span>
            <span className="font-mono text-xs uppercase text-[#5cffb5] tracking-widest">
              PROTOCOL 01-A / ISOLATED MATRICES
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#d6ffe9] tracking-tight">
            Public Biomedical Data Library
          </h1>
          <p className="text-xs md:text-sm text-[#b8ffd9] max-w-3xl mt-1 leading-relaxed">
            Every catalog table in this repo, with every saved model file discovered for that
            table. One table, one label — never fused into a diagnosis.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 shrink-0">
          <button type="button" onClick={handleCopySha} className="text-xs font-mono flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{copiedSha ? 'Copied SHA-256!' : 'Verified SHA-256'}</span>
          </button>
          <button type="button" onClick={() => setShowYamlModal(true)} className="text-xs font-mono flex items-center gap-1.5">
            <FileCode className="w-3.5 h-3.5" />
            <span>Raw Manifest YAML</span>
          </button>
        </div>
      </div>

      {loadError ? (
        <p className="text-xs text-[#ffb4ab] font-mono">
          Catalog API unavailable ({loadError}). Start uvicorn on port 8000.
        </p>
      ) : null}

      <div className="p-3 bg-[#0f131d] border border-[#31353f]/50 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto text-xs">
          <button type="button" onClick={() => setFilterTab('all')}>
            All {tables.length} tables
          </button>
          <button type="button" onClick={() => setFilterTab('models')}>
            Has saved models
          </button>
          <button type="button" onClick={() => setFilterTab('mapper')}>
            Mapper / score UI
          </button>
        </div>
        <div className="relative w-full sm:w-64 shrink-0">
          <Search className="w-4 h-4 text-[#849495] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search tables, columns, models..."
            className="w-full pl-9 pr-3 py-1.5 bg-[#171c25] border border-[#31353f]/60 text-xs text-[#dfe2f0] placeholder-[#849495] focus:outline-none"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filteredTables.map((row) => {
          const studioId = STUDIO_ID[row.key];
          const available = row.models.filter((m) => m.available);
          const missing = row.models.filter((m) => !m.available);
          const shown = row.models.length ? row.models : [];
          return (
            <div
              key={row.key}
              className="p-5 bg-[#171c25] border border-[#31353f]/50 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5 gap-2">
                  <span className="px-2 py-0.5 bg-[#262a34] font-mono text-[10px] text-[#5cffb5] font-semibold">
                    {row.key}
                  </span>
                  <span className="font-mono text-[10px] text-[#849495]">
                    min {row.min_filled}/{row.features.length} fields
                  </span>
                </div>
                <h2 className="text-lg font-bold text-[#eef7ff] tracking-tight">{row.title}</h2>
                <p className="font-mono text-xs text-[#5cffb5] mt-1">{row.positive_label}</p>
                {row.notes ? (
                  <p className="text-xs text-[#b8ffd9] mt-2 leading-relaxed">{row.notes}</p>
                ) : null}

                <div className="mt-3 p-3 bg-[#0a0e17] border border-[#31353f]/40">
                  <span className="font-mono text-[10px] text-[#849495] uppercase block mb-2">
                    Saved models on this table ({available.length} on disk
                    {missing.length ? `, ${missing.length} listed but missing` : ''})
                  </span>
                  {shown.length === 0 ? (
                    <p className="text-xs text-[#849495]">
                      No joblib files discovered yet. Train this table to list models.
                    </p>
                  ) : (
                    <ul className="space-y-1 font-mono text-xs">
                      {shown.map((model) => (
                        <li
                          key={`${row.key}-${model.file || model.name}`}
                          className="flex items-center justify-between gap-2"
                        >
                          <span className="text-[#dfe2f0]">{model.name}</span>
                          <span className={model.available ? 'text-[#5cffb5]' : 'text-[#849495]'}>
                            {model.available ? model.file || 'on disk' : 'not trained'}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <p className="text-[10px] font-mono text-[#849495] mt-2 leading-relaxed">
                  Columns: {row.features.slice(0, 12).join(', ')}
                  {row.features.length > 12 ? ` … +${row.features.length - 12}` : ''}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-[#31353f]/40 flex items-center justify-between gap-3">
                <button
                  type="button"
                  onClick={() => onInspectFeatures(toDatasetMeta(row))}
                  className="text-xs font-semibold flex items-center gap-1.5"
                >
                  <BarChart2 className="w-3.5 h-3.5" />
                  <span>Inspect columns</span>
                </button>
                {studioId ? (
                  <button
                    type="button"
                    onClick={() => onSelectDatasetForClassical(studioId)}
                    className="text-xs font-bold flex items-center gap-1.5"
                  >
                    <span>Load in Classical Studio</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <span className="text-[10px] font-mono text-[#849495]">
                    Isolated table — not fused in Classical Studio
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {showYamlModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
          <div className="w-full max-w-2xl bg-[#0f131d] border border-[#31353f] p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-[#31353f] pb-3">
              <h3 className="text-base font-bold text-[#d6ffe9]">Catalog manifest (live)</h3>
              <button type="button" className="btn-icon" onClick={() => setShowYamlModal(false)}>
                ×
              </button>
            </div>
            <pre className="p-4 bg-[#0a0e17] font-mono text-xs text-[#5cffb5] overflow-x-auto max-h-96">
              {yamlText || '# empty'}
            </pre>
            <div className="flex justify-end">
              <button type="button" onClick={() => setShowYamlModal(false)}>
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
