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
  refused_symptom_checker?: boolean;
  result?: {
    research_positive_percent?: number | null;
    insufficient?: boolean;
    title?: string;
    specialty_hint?: string;
    message?: string;
    models?: { name: string; percent: number | null; error?: string | null }[];
  };
};

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
