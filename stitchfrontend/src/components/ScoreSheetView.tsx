import React, { useEffect, useMemo, useState } from 'react';
import {
  FileText,
  Lock,
  Copy,
  Check,
  Download,
  AlertTriangle,
  CheckCircle2,
  Upload,
} from 'lucide-react';
import {
  downloadLockedPdf,
  fetchCatalogTables,
  scoreRecord,
  scoreRecordPdf,
  type CatalogTableRow,
} from '../api';
import { WISCONSIN_REDUCED_FIELDS } from '../data/fieldLabels';

const HIGH_RANGE = `mean perimeter: 122.8
mean concave points: 0.1471
worst radius: 25.38
worst perimeter: 184.6
worst area: 2019.0
worst concave points: 0.2654`;

const LOW_RANGE = `mean perimeter: 75.0
mean concave points: 0.02
worst radius: 13.0
worst perimeter: 85.0
worst area: 520.0
worst concave points: 0.07`;

const MID_RANGE = `mean perimeter: 92.0
mean concave points: 0.05
worst radius: 16.0
worst perimeter: 105.0
worst area: 800.0
worst concave points: 0.12`;

function countParsedLines(text: string): number {
  let n = 0;
  for (const line of text.split('\n')) {
    if (/^.+?\s*[:=]\s*[-+]?\d/.test(line)) n += 1;
  }
  return n;
}

function modelPercent(
  models: { name: string; percent: number | null }[] | undefined,
  needles: string[]
): number | null {
  for (const item of models || []) {
    const name = (item.name || '').toLowerCase();
    if (needles.some((n) => name.includes(n)) && item.percent != null) {
      return item.percent;
    }
  }
  return null;
}

function bandLabel(score: number | null): string {
  if (score == null) return '—';
  if (score >= 70) return 'Higher (70–100)';
  if (score >= 40) return 'Middle (40–69)';
  return 'Lower (0–39)';
}

export const ScoreSheetView: React.FC = () => {
  const [subjectName, setSubjectName] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [rawText, setRawText] = useState(HIGH_RANGE);
  const [copiedKey, setCopiedKey] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [scoring, setScoring] = useState(false);
  const [useNvidia, setUseNvidia] = useState(false);
  const [scoreSuccess, setScoreSuccess] = useState(false);
  const [unlockKey, setUnlockKey] = useState('');
  const [stored, setStored] = useState(false);
  const [error, setError] = useState('');
  const [headline, setHeadline] = useState<number | null>(null);
  const [lrScore, setLrScore] = useState<number | null>(null);
  const [rfScore, setRfScore] = useState<number | null>(null);
  const [qkScore, setQkScore] = useState<number | null>(null);
  const [specialtyHint, setSpecialtyHint] = useState('');
  const [statusNote, setStatusNote] = useState(
    'Scores come from saved models on this table only — not a diagnosis.'
  );
  const [catalogMode, setCatalogMode] = useState('auto');
  const [activeTable, setActiveTable] = useState('wisconsin_reduced');
  const [catalogRows, setCatalogRows] = useState<CatalogTableRow[]>([]);

  useEffect(() => {
    void fetchCatalogTables()
      .then((rows) => setCatalogRows(rows.filter((row) => row.key)))
      .catch(() => setCatalogRows([]));
  }, []);

  const activeMeta = useMemo(
    () => catalogRows.find((row) => row.key === activeTable),
    [catalogRows, activeTable]
  );
  const fieldGuide = useMemo(() => {
    const sliders = activeMeta?.sliders || [];
    if (sliders.length) {
      const cap = Math.min(sliders.length, 12);
      return sliders.slice(0, cap).map((slider, idx) => ({
        key: String(slider.name || activeMeta?.features[idx] || `field_${idx}`),
        label: String(slider.label || slider.name || ''),
        description: String(slider.description || ''),
      }));
    }
    return WISCONSIN_REDUCED_FIELDS;
  }, [activeMeta]);
  const validCount = useMemo(() => countParsedLines(rawText), [rawText]);
  const displayScore = headline;
  const requestKey = catalogMode === 'auto' ? 'auto' : catalogMode;

  const fillSampleForTable = (key: string) => {
    const row = catalogRows.find((item) => item.key === key);
    if (!row) return;
    const sliders = row.sliders || [];
    const names = row.features.length ? row.features : sliders.map((s) => s.name || '');
    const limit = Math.min(Math.max(row.min_filled, 6), 20, names.length);
    const lines = names.slice(0, limit).map((name, idx) => {
      const slider = sliders[idx];
      const value = slider?.default ?? 1;
      return `${name}: ${value}`;
    });
    if (lines.length) {
      setRawText(lines.join('\n'));
      setActiveTable(key);
    }
    setUnlockKey('');
    setError('');
  };

  const handlePreFill = (type: 'high' | 'low' | 'mid' | 'ddd' | 'table') => {
    if (type === 'high') setRawText(HIGH_RANGE);
    else if (type === 'low') setRawText(LOW_RANGE);
    else if (type === 'ddd') {
      fillSampleForTable('ddd');
      return;
    } else if (type === 'table') {
      fillSampleForTable(catalogMode === 'auto' ? activeTable : catalogMode);
      return;
    } else setRawText(MID_RANGE);
    setUnlockKey('');
    setError('');
  };

  const applyScorePayload = (data: Awaited<ReturnType<typeof scoreRecord>>) => {
    if (data.refused_symptom_checker) {
      setHeadline(null);
      setLrScore(null);
      setRfScore(null);
      setQkScore(null);
      setStatusNote(
        'This is not a symptom checker. The PDF or paste must contain this table’s field: number lines — not fever or other symptoms.'
      );
      return;
    }
    const result = data.result;
    if (!result) {
      setStatusNote('No score payload returned.');
      return;
    }
    setSpecialtyHint(result.specialty_hint || '');
    const models = result.models || [];
    const pct = result.research_positive_percent ?? null;
    setHeadline(pct);
    setLrScore(modelPercent(models, ['logistic', 'lr']));
    setRfScore(modelPercent(models, ['random forest', 'rf']));
    setQkScore(modelPercent(models, ['qsvc']));
    const detected = data.detected_catalog_key || result.key || activeTable;
    if (detected) setActiveTable(detected);
    if (result.insufficient) {
      setStatusNote(
        result.message ||
          'Not enough of this table’s columns yet — no research score.'
      );
    } else {
      const how = data.table_was_auto_detected
        ? 'Matched by field names (not by the score value). '
        : '';
      setStatusNote(
        `${how}${result.title || detected} — one table, one label.`
      );
      setScoreSuccess(true);
      setTimeout(() => setScoreSuccess(false), 2000);
    }
  };

  const handleScore = async () => {
    setScoring(true);
    setError('');
    try {
      const data = await scoreRecord(requestKey, rawText);
      applyScorePayload(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setScoring(false);
    }
  };

  const handlePdfUpload = async (file: File | undefined) => {
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      const data = await scoreRecordPdf(requestKey, file, useNvidia);
      if (data.extracted_text) setRawText(data.extracted_text);
      applyScorePayload(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setUploading(false);
    }
  };

  const handleCopyKey = () => {
    if (!unlockKey) return;
    navigator.clipboard?.writeText(unlockKey);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2500);
  };

  const handleDownloadPdf = async () => {
    if (!subjectName.trim() || !dateOfBirth.trim()) {
      setError(
        "Enter a full name and date of birth first. They are labels on the PDF only — not the unlock password."
      );
      return;
    }
    setDownloading(true);
    setError('');
    try {
      const { blob, unlockKey: key, stored: didStore } = await downloadLockedPdf({
        catalog_key: requestKey,
        subject_name: subjectName.trim(),
        date_of_birth: dateOfBirth.trim(),
        text: rawText,
      });
      setUnlockKey(key);
      setStored(didStore);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'lakshya_research_score_sheet.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setDownloading(false);
    }
  };

  const fmt = (n: number | null) => (n == null ? '—' : `${Math.round(n)}`);

  return (
    <div className="w-full max-w-6xl mx-auto px-4 md:px-6 py-6 pb-16 space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9]">
              <FileText className="w-3.5 h-3.5" />
            </span>
            <span className="font-mono text-xs uppercase text-[#00dbe9] tracking-widest">
              PROTOCOL 04-R / BENCHMARK SCORE SHEET EXPORT
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#dbfcff] tracking-tight">
            Paste a Record & Research Score Sheet
          </h1>
          <p className="text-xs md:text-sm text-[#b9cacb] max-w-3xl mt-1 leading-relaxed">
            Score any public catalog table from field: number lines. Auto matches
            those <span className="text-[#dbfcff]">column names</span> to one table
            — never from the score value, never as a diagnosis. Pick a table to lock
            it. Name and date of birth are PDF labels only.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 shrink-0 font-mono text-xs">
          <span className="px-3 py-1.5 rounded-xl bg-[#262a34] border border-[#31353f] text-[#00dbe9] flex items-center gap-1.5">
            <Lock className="w-3.5 h-3.5 text-[#00dbe9]" />
            <span>PDF OPEN-PASSWORD</span>
          </span>
          <span className="px-3 py-1.5 rounded-xl bg-[#571bc1]/30 border border-[#571bc1]/50 text-[#e9ddff]">
            NON-CLINICAL ARTIFACT
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-7 p-5 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="font-mono text-xs text-[#849495] uppercase tracking-wider">
              TABULAR VECTOR INPUT
            </span>
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="text-[#849495] text-[10px]">PRE-FILL:</span>
              <button
                onClick={() => handlePreFill('high')}
                className="px-2 py-0.5 rounded bg-[#262a34] hover:bg-[#353944] text-[#dfe2f0] transition-all"
              >
                High-range sample
              </button>
              <button
                onClick={() => handlePreFill('low')}
                className="px-2 py-0.5 rounded bg-[#262a34] hover:bg-[#353944] text-[#dfe2f0] transition-all"
              >
                Low-range sample
              </button>
              <button
                onClick={() => handlePreFill('mid')}
                className="px-2 py-0.5 rounded bg-[#262a34] hover:bg-[#353944] text-[#849495] transition-all"
              >
                Mid-range sample
              </button>
              <button
                onClick={() => handlePreFill('table')}
                className="px-2 py-0.5 rounded bg-[#262a34] hover:bg-[#353944] text-[#dfe2f0] transition-all"
              >
                Sample this table
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block font-mono text-[10px] text-[#849495] uppercase mb-1">
                Full name (label on PDF only)
              </label>
              <input
                type="text"
                required
                value={subjectName}
                onChange={(e) => setSubjectName(e.target.value)}
                placeholder="Required to generate PDF"
                className="w-full px-3 py-2 rounded-lg bg-[#0a0e17] border border-[#31353f]/60 font-mono text-xs text-[#dfe2f0] focus:outline-none focus:border-[#00f0ff]"
              />
            </div>
            <div>
              <label className="block font-mono text-[10px] text-[#849495] uppercase mb-1">
                Date of birth (label on PDF only)
              </label>
              <input
                type="date"
                required
                value={dateOfBirth}
                onChange={(e) => setDateOfBirth(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#0a0e17] border border-[#31353f]/60 font-mono text-xs text-[#dfe2f0] focus:outline-none focus:border-[#00f0ff]"
              />
            </div>
          </div>

          <div className="p-3 rounded-lg bg-[#0a0e17] border border-[#31353f]/40 space-y-2 font-mono text-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[#849495]">
              <span>ACTIVE BENCHMARK DATASET:</span>
              <select
                value={catalogMode}
                onChange={(e) => {
                  const next = e.target.value;
                  setCatalogMode(next);
                  if (next !== 'auto') setActiveTable(next);
                }}
                className="bg-[#171c25] border border-[#31353f] rounded-lg px-2 py-1 text-[#dbfcff] max-w-full"
              >
                <option value="auto">Auto (any catalog table, by field names)</option>
                {catalogRows.map((row) => (
                  <option key={row.key} value={row.key}>
                    {row.key} — {row.title}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center justify-between text-[#849495]">
              <span>LAST MATCHED TABLE:</span>
              <span className="text-[#dbfcff]">{activeTable}</span>
            </div>
            <div className="flex items-center justify-between text-[#849495]">
              <span>SCORING:</span>
              <span className="text-[#00dbe9]">POST /v1/research-record</span>
            </div>
          </div>

          <div className="rounded-lg bg-[#0a0e17] border border-[#31353f]/40 p-3 space-y-2">
            <span className="font-mono text-[10px] text-[#849495] uppercase tracking-wider block">
              Field guide — what these columns mean
            </span>
            <ul className="space-y-2 text-xs text-[#b9cacb] leading-relaxed">
              {fieldGuide.map((field) => (
                <li key={field.key}>
                  <span className="font-mono text-[#00dbe9]">{field.key}</span>
                  <span className="text-[#849495]"> — </span>
                  <span className="font-semibold text-[#dbfcff]">{field.label}</span>
                  <span className="block text-[#849495] mt-0.5 pl-0">{field.description}</span>
                </li>
              ))}
            </ul>
            {(activeMeta?.features.length || 0) > 12 ? (
              <p className="font-mono text-[10px] text-[#849495]">
                Showing 12 of {activeMeta?.features.length} columns. Need{' '}
                {activeMeta?.min_filled} named numbers to score. Not a diagnosis.
              </p>
            ) : null}
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between font-mono text-[10px] text-[#849495]">
              <span>COLUMNS FOR {activeTable} (need {activeMeta?.min_filled ?? 6}+ named fields)</span>
              <span>Text PDF upload extracts named numbers only</span>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <label className="px-3 py-1.5 rounded-lg bg-[#262a34] hover:bg-[#353944] border border-[#31353f] text-xs font-semibold text-[#dfe2f0] cursor-pointer inline-flex items-center gap-1.5">
                <Upload className="w-3.5 h-3.5 text-[#00dbe9]" />
                {uploading ? 'Reading PDF…' : 'Upload text PDF'}
                <input
                  type="file"
                  accept="application/pdf,.pdf"
                  className="hidden"
                  disabled={uploading}
                  onChange={(e) => {
                    const chosen = e.target.files?.[0];
                    void handlePdfUpload(chosen);
                    e.target.value = '';
                  }}
                />
              </label>
              <label className="flex items-center gap-1.5 font-mono text-[10px] text-[#849495]">
                <input
                  type="checkbox"
                  checked={useNvidia}
                  onChange={(e) => setUseNvidia(e.target.checked)}
                />
                NVIDIA: extract numbers already in the wording (never from symptoms)
              </label>
            </div>
            <textarea
              rows={8}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              className="w-full p-3 rounded-xl bg-[#0a0e17] border border-[#31353f]/60 font-mono text-xs text-[#00f0ff] focus:outline-none focus:border-[#00f0ff] leading-relaxed resize-y"
              placeholder={HIGH_RANGE}
            />
          </div>

          <div className="flex items-center gap-2 font-mono text-xs text-[#00dbe9]">
            <CheckCircle2 className="w-4 h-4 text-[#00dbe9]" />
            <span>{validCount} field: number lines detected · score uses saved LR/RF (and QSVC if trained)</span>
          </div>

          {error ? (
            <p className="text-xs text-[#ffb4ab] font-mono">{error}</p>
          ) : null}

          <div className="pt-2 border-t border-[#31353f]/40 flex flex-wrap items-center justify-between gap-3">
            <button
              onClick={handleScore}
              disabled={scoring}
              className="px-5 py-2.5 rounded-lg bg-[#00f0ff] hover:bg-[#7df4ff] text-[#00363a] text-xs font-bold transition-all shadow-[0_0_16px_rgba(0,219,233,0.3)] flex items-center gap-2 disabled:opacity-60"
            >
              <span>
                {scoring ? 'Scoring…' : scoreSuccess ? 'Scored' : 'Score this table'}
              </span>
            </button>

            <button
              onClick={handleDownloadPdf}
              disabled={downloading}
              className="px-4 py-2.5 rounded-lg bg-[#262a34] hover:bg-[#353944] border border-[#31353f] text-xs font-semibold text-[#dfe2f0] transition-all flex items-center gap-1.5 disabled:opacity-60"
            >
              <Lock className="w-3.5 h-3.5 text-[#d0bcff]" />
              <span>{downloading ? 'Generating…' : 'Generate Locked PDF'}</span>
            </button>
          </div>
        </div>

        <div className="lg:col-span-5 space-y-5">
          <div className="p-5 rounded-xl bg-[#171c25] border border-[#00f0ff]/40 shadow-lg relative overflow-hidden">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs text-[#849495] uppercase tracking-wider">
                RESEARCH SCORE (THIS TABLE)
              </span>
              <span
                className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold ${
                  displayScore != null && displayScore >= 70
                    ? 'bg-[#571bc1]/40 text-[#e9ddff]'
                    : displayScore != null && displayScore >= 40
                    ? 'bg-[#006970]/40 text-[#7df4ff]'
                    : 'bg-[#262a34] text-[#849495]'
                }`}
              >
                {bandLabel(displayScore)}
              </span>
            </div>

            <div className="my-3 flex items-baseline gap-3">
              <span className="font-mono text-5xl font-extrabold text-[#dbfcff] drop-shadow-[0_0_20px_rgba(0,219,233,0.4)]">
                {fmt(displayScore)}
              </span>
              <span className="font-mono text-xl text-[#849495] font-semibold">/ 100</span>
            </div>

            <p className="font-mono text-xs text-[#b9cacb] leading-relaxed">{statusNote}</p>
            {specialtyHint ? (
              <p className="mt-2 font-mono text-[10px] text-[#849495] leading-relaxed">
                {specialtyHint}
              </p>
            ) : null}

            <div className="mt-3 space-y-1 font-mono text-[10px] text-[#849495]">
              <div className="flex justify-between">
                <span>Lower (0–39)</span>
                <span>Middle (40–69)</span>
                <span>Higher (70–100)</span>
              </div>
              <div className="h-3 w-full rounded-md bg-[#0a0e17] overflow-hidden flex relative p-0.5 border border-[#31353f]/40">
                <div className="h-full w-[40%] bg-[#262a34] rounded-l"></div>
                <div className="h-full w-[30%] bg-[#006970]/60"></div>
                <div className="h-full w-[30%] bg-[#571bc1]/60 rounded-r"></div>
                {displayScore != null ? (
                  <div
                    className="absolute top-0 bottom-0 w-1.5 bg-[#00f0ff] rounded shadow-[0_0_8px_#00f0ff] transition-all duration-200 -ml-0.5"
                    style={{ left: `${Math.min(99, Math.max(1, displayScore))}%` }}
                  />
                ) : null}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-[#31353f]/40 space-y-1.5 font-mono text-xs">
              <span className="text-[#849495] text-[10px] uppercase block">
                SAVED MODELS ON THIS TABLE
              </span>
              <div className="flex justify-between text-[#b9cacb]">
                <span>Linear LR:</span>
                <span className="text-[#00f0ff] font-bold">{fmt(lrScore)} / 100</span>
              </div>
              <div className="flex justify-between text-[#b9cacb]">
                <span>Random Forest:</span>
                <span className="text-[#d0bcff] font-bold">{fmt(rfScore)} / 100</span>
              </div>
              <div className="flex justify-between text-[#b9cacb]">
                <span>Quantum kernel (QSVC):</span>
                <span className="text-[#7df4ff] font-bold">{fmt(qkScore)} / 100</span>
              </div>
            </div>
          </div>

          <div className="p-5 rounded-xl bg-[#171c25] border border-[#31353f]/50 shadow-md space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-[#eef7ff]">Locked research PDF</h3>
              <span className="px-2 py-0.5 rounded bg-[#00dbe9]/20 text-[#00dbe9] border border-[#00dbe9]/40 font-mono text-[10px] font-bold">
                OPEN-PASSWORD
              </span>
            </div>

            <p className="text-xs text-[#b9cacb] leading-relaxed">
              <strong className="text-[#dfe2f0]">Shown once after generate.</strong> The
              password is a random token from the API. It is not derived from name or date
              of birth.
            </p>

            <div className="p-3 rounded-lg bg-[#0a0e17] border border-[#00f0ff]/30 flex items-center justify-between font-mono">
              <div>
                <span className="text-[10px] text-[#849495] block">PDF OPEN-PASSWORD</span>
                <span className="text-sm font-bold text-[#00f0ff] tracking-wider select-all">
                  {unlockKey || 'Generate the PDF to receive a key'}
                </span>
              </div>
              <button
                onClick={handleCopyKey}
                disabled={!unlockKey}
                className="p-2 rounded-lg bg-[#262a34] hover:bg-[#353944] text-[#b9cacb] hover:text-[#dfe2f0] transition-all flex items-center gap-1 text-xs disabled:opacity-40"
              >
                {copiedKey ? <Check className="w-3.5 h-3.5 text-[#00dbe9]" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedKey ? 'Copied' : 'Copy Key'}</span>
              </button>
            </div>

            <div className="p-3 rounded-lg bg-[#262a34]/60 border border-[#31353f]/40 flex items-start gap-2.5 text-xs text-[#b9cacb]">
              <AlertTriangle className="w-4 h-4 text-[#d0bcff] shrink-0 mt-0.5" />
              <p className="leading-relaxed">
                <strong className="text-[#e9ddff]">Keep the key.</strong> Lost passwords
                cannot be recovered from name or date of birth.
                {stored ? ' A fingerprint was stored for this run.' : ''}
              </p>
            </div>

            <div className="p-3 rounded-lg bg-[#0a0e17] border border-[#31353f]/40 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-8 h-8 rounded-lg bg-[#262a34] flex items-center justify-center text-[#00dbe9] shrink-0">
                  <FileText className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <span className="font-mono text-xs font-semibold text-[#dfe2f0] truncate block">
                    lakshya_research_score_sheet.pdf
                  </span>
                  <span className="font-mono text-[10px] text-[#849495] block">
                    Password-locked research score sheet
                  </span>
                </div>
              </div>

              <button
                onClick={handleDownloadPdf}
                disabled={downloading}
                className="px-3 py-2 rounded-lg bg-[#00f0ff] hover:bg-[#7df4ff] text-[#00363a] text-xs font-bold transition-all shrink-0 flex items-center gap-1.5 shadow-sm disabled:opacity-60"
              >
                <Download className="w-3.5 h-3.5" />
                <span>{downloading ? 'Exporting…' : 'Download locked PDF'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
