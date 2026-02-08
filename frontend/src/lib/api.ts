import type {
  ConsultResult,
  GraphStats,
  RemedyDetail,
  SearchResult,
  NetworkData,
} from "./types";

const BASE = "/api";

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json();
}

export async function healthCheck(): Promise<{ status: string; neo4j: string }> {
  return fetchJSON(`${BASE}/health`);
}

export async function getGraphStats(): Promise<GraphStats> {
  return fetchJSON(`${BASE}/graph/stats`);
}

export async function consult(
  complaint: string,
  options: {
    enableReliability?: boolean;
    enableUncertainty?: boolean;
    enablePatterns?: boolean;
    explain?: boolean;
  } = {}
): Promise<ConsultResult> {
  return fetchJSON(`${BASE}/consult`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      complaint,
      enable_reliability: options.enableReliability ?? true,
      enable_uncertainty: options.enableUncertainty ?? true,
      enable_pattern_mining: options.enablePatterns ?? true,
      explain: options.explain ?? true,
    }),
  });
}

export async function searchRemedies(
  q: string,
  limit = 20
): Promise<{ results: SearchResult[]; count: number }> {
  return fetchJSON(`${BASE}/search/remedies?q=${encodeURIComponent(q)}&limit=${limit}`);
}

export async function searchSymptoms(
  q: string,
  limit = 20
): Promise<{ results: Array<{ id: string; name: string; category: string }>; count: number }> {
  return fetchJSON(`${BASE}/search/symptoms?q=${encodeURIComponent(q)}&limit=${limit}`);
}

export async function getRemedyDetail(abbrev: string): Promise<RemedyDetail> {
  return fetchJSON(`${BASE}/remedy/${encodeURIComponent(abbrev)}`);
}

export async function getRemedyNetwork(abbrev: string): Promise<NetworkData> {
  return fetchJSON(`${BASE}/remedy/${encodeURIComponent(abbrev)}/network`);
}
