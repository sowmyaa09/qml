/** Same-origin API when served from uvicorn; Vite proxies /v1 in npm run dev. */

export function apiUrl(path: string): string {
  return path.startsWith("/") ? path : `/${path}`;
}

export function formatApiError(detail: unknown, fallback: string): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const parts = detail.map((item) => {
      if (!item || typeof item !== "object") return String(item);
      const rec = item as { loc?: unknown; msg?: unknown };
      const loc = Array.isArray(rec.loc)
        ? rec.loc.filter((part) => part !== "body").join(".")
        : "";
      if (loc.includes("subject_name")) {
        return "Enter a name (label on the PDF only).";
      }
      if (loc.includes("date_of_birth")) {
        return "Enter a date of birth (label on the PDF only).";
      }
      const msg = typeof rec.msg === "string" ? rec.msg : "";
      return loc && msg ? `${loc}: ${msg}` : msg || JSON.stringify(item);
    });
    return parts.filter(Boolean).join(" ");
  }
  if (detail && typeof detail === "object") {
    return JSON.stringify(detail);
  }
  return fallback;
}

export type ScorePayload = {
  extracted?: Record<string, unknown>;
  extracted_text?: string;
  refused_symptom_checker?: boolean;
  detected_catalog_key?: string | null;
  detect_confident?: boolean;
  table_was_auto_detected?: boolean;
  schema_title?: string;
  result?: {
    research_positive_percent?: number | null;
    insufficient?: boolean;
    title?: string;
    specialty_hint?: string;
    message?: string;
    key?: string;
    models?: { name: string; percent: number | null; error?: string | null }[];
  };
};

export type CatalogSlider = {
  name?: string;
  label?: string;
  description?: string;
  default?: number;
};

export type CatalogModelRow = {
  name: string;
  file: string;
  available: boolean;
};

export type CatalogTableRow = {
  key: string;
  title: string;
  min_filled: number;
  features: string[];
  notes: string;
  positive_label: string;
  specialty_hint: string;
  ui: boolean;
  sliders: CatalogSlider[];
  models: CatalogModelRow[];
};

export async function fetchCatalogTables(): Promise<CatalogTableRow[]> {
  const res = await fetch(apiUrl("/v1/catalog"));
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(formatApiError(data.detail, res.statusText));
  }
  const tables = Array.isArray(data.tables) ? data.tables : [];
  return tables
    .map((row: Record<string, unknown>) => ({
      key: String(row.key || ""),
      title: String(row.title || row.key || ""),
      min_filled: Number(row.min_filled || 0),
      features: Array.isArray(row.features)
        ? row.features.map((item) => String(item))
        : [],
      notes: String(row.notes || ""),
      positive_label: String(row.positive_label || ""),
      specialty_hint: String(row.specialty_hint || ""),
      ui: Boolean(row.ui),
      sliders: Array.isArray(row.sliders) ? (row.sliders as CatalogSlider[]) : [],
      models: Array.isArray(row.models)
        ? (row.models as Record<string, unknown>[]).map((item) => ({
            name: String(item.name || item.file || "model"),
            file: String(item.file || ""),
            available: Boolean(item.available),
          }))
        : [],
    }))
    .filter((row) => row.key);
}

export type QmlCostLatencyPayload = {
  disclaimer: string;
  dataset: string;
  hardware_note: string;
  ablation: Record<string, unknown>[];
  ablation_source: string;
  headline_models: Record<string, unknown>[];
  headline_source: string;
  insight: {
    qsvc_f1?: number;
    rbf_f1?: number;
    f1_delta?: number;
    qsvc_seconds?: number;
    rbf_seconds?: number;
    latency_ratio?: number;
    verdict?: string;
  };
  figure_available: boolean;
  figure_url: string | null;
  train_commands: string[];
};

export async function fetchQmlCostLatency(): Promise<QmlCostLatencyPayload> {
  const res = await fetch(apiUrl("/v1/qml-cost-latency"));
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(formatApiError(err.detail, res.statusText));
  }
  return res.json() as Promise<QmlCostLatencyPayload>;
}

export async function scoreRecord(
  catalogKey: string,
  text: string
): Promise<ScorePayload> {
  const res = await fetch(apiUrl("/v1/research-record"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ catalog_key: catalogKey, text }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(formatApiError(data.detail, res.statusText));
  }
  return data as ScorePayload;
}

export async function scoreRecordPdf(
  catalogKey: string,
  file: File,
  useNvidia = false
): Promise<ScorePayload> {
  const body = new FormData();
  body.append("catalog_key", catalogKey);
  body.append("use_nvidia", useNvidia ? "true" : "false");
  body.append("file", file);
  const res = await fetch(apiUrl("/v1/research-record-pdf"), {
    method: "POST",
    body,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(formatApiError(data.detail, res.statusText));
  }
  return data as ScorePayload;
}

export async function downloadLockedPdf(body: {
  catalog_key: string;
  subject_name: string;
  date_of_birth: string;
  text: string;
}): Promise<{ blob: Blob; unlockKey: string; stored: boolean }> {
  const res = await fetch(apiUrl("/v1/research-report"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err.detail;
    throw new Error(formatApiError(detail, res.statusText));
  }
  const unlockKey = res.headers.get("X-Unlock-Key") || "";
  const stored = res.headers.get("X-Report-Stored") === "true";
  const blob = await res.blob();
  return { blob, unlockKey, stored };
}
