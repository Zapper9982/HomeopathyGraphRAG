"use client";

import { useState, useEffect, Suspense } from "react";
import { searchRemedies, getRemedyDetail } from "@/lib/api";
import type { SearchResult, RemedyDetail } from "@/lib/types";
import { useSearchParams } from "next/navigation";

export default function ExplorePage() {
  return (
    <Suspense fallback={<div className="flex justify-center py-20"><div className="spinner" /></div>}>
      <ExploreInner />
    </Suspense>
  );
}

const REL_COLORS: Record<string, string> = {
  CORRELATED_WITH: "bg-accent/8 text-accent border border-accent/15",
  ANTIDOTES: "bg-danger/8 text-danger border border-danger/15",
  COMPLEMENTARY: "bg-success/8 text-success border border-success/15",
  INCOMPATIBLE: "bg-warning/8 text-warning border border-warning/15",
  FOLLOWS_WELL: "bg-accent/5 text-accent-dim border border-accent/10",
};

const REL_LABELS: Record<string, string> = {
  CORRELATED_WITH: "Compare",
  ANTIDOTES: "Antidote",
  COMPLEMENTARY: "Complementary",
  INCOMPATIBLE: "Incompatible",
  FOLLOWS_WELL: "Follows well",
};

function ExploreInner() {
  const searchParams = useSearchParams();
  const initialQ = searchParams.get("q") || "";

  const [query, setQuery] = useState(initialQ);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [detail, setDetail] = useState<RemedyDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => {
    if (initialQ) {
      doSearch(initialQ);
    }
  }, [initialQ]);

  async function doSearch(q: string) {
    if (!q.trim()) return;
    setSearching(true);
    setDetail(null);
    try {
      const res = await searchRemedies(q);
      setResults(res.results);
      // Auto-open if single result
      if (res.results.length === 1) {
        openDetail(res.results[0].abbrev);
      }
    } catch {
      setResults([]);
    } finally {
      setSearching(false);
    }
  }

  async function openDetail(abbrev: string) {
    setLoadingDetail(true);
    try {
      const d = await getRemedyDetail(abbrev);
      setDetail(d);
    } catch {
      setDetail(null);
    } finally {
      setLoadingDetail(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") doSearch(query);
  }

  // Group relationships by type
  const relGroups: Record<string, Array<{ target: string; target_abbrev: string }>> = {};
  if (detail) {
    for (const r of detail.relationships) {
      const group = relGroups[r.type] || [];
      group.push(r);
      relGroups[r.type] = group;
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2 animate-fade-in">
        <h1 className="text-3xl font-bold tracking-tight">
          <span className="text-gradient">Explore Remedies</span>
        </h1>
        <p className="text-muted text-sm">Search by name, abbreviation, or common name</p>
      </div>

      {/* Search bar */}
      <div className="flex gap-2.5 animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g. Belladonna, Ars., Nux Vomica..."
          className="flex-1 bg-white border border-border rounded-xl px-5 py-3 text-foreground placeholder:text-muted/50 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent/40 transition-all shadow-sm"
        />
        <button
          onClick={() => doSearch(query)}
          disabled={searching}
          className="btn-gradient px-6 py-3 cursor-pointer"
        >
          {searching ? "..." : "Search"}
        </button>
      </div>

      {/* Search results */}
      {results.length > 0 && !detail && (
        <div className="glass-card overflow-hidden animate-fade-in">
          <div className="px-5 py-3 border-b border-border/60">
            <span className="section-label">{results.length} remedies found</span>
          </div>
          <div className="divide-y divide-border/30 max-h-[60vh] overflow-y-auto">
            {results.map((r) => (
              <button
                key={r.abbrev}
                onClick={() => openDetail(r.abbrev)}
                className="w-full px-5 py-3.5 flex items-center justify-between hover:bg-accent/3 transition-colors text-left cursor-pointer group"
              >
                <div>
                  <span className="font-medium text-foreground group-hover:text-accent transition-colors">
                    {r.name || r.abbrev}
                  </span>
                  {r.common_name && (
                    <span className="text-muted text-sm ml-2">({r.common_name})</span>
                  )}
                </div>
                <span className="tag bg-card-hover text-muted font-mono text-[11px]">{r.abbrev}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {results.length === 0 && !searching && query && (
        <p className="text-muted text-sm text-center py-12">No remedies found for &quot;{query}&quot;</p>
      )}

      {/* Loading detail */}
      {loadingDetail && (
        <div className="flex justify-center py-16">
          <div className="spinner" />
        </div>
      )}

      {detail && (
        <div className="space-y-5 animate-fade-in">
          {/* Header */}
          <div className="glass-card p-6">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">{detail.name || detail.abbrev}</h2>
                {detail.common_name && (
                  <p className="text-muted mt-1 text-[15px]">{detail.common_name}</p>
                )}
              </div>
              <div className="text-right">
                <span className="tag bg-card-hover text-muted font-mono">{detail.abbrev}</span>
                {detail.source && (
                  <p className="text-xs text-muted mt-2">Source: {detail.source}</p>
                )}
              </div>
            </div>
            <div className="mt-5 flex gap-3">
              <div className="px-4 py-2.5 bg-accent-light rounded-xl">
                <span className="text-[11px] text-muted font-medium uppercase tracking-wider block">Indications</span>
                <span className="text-2xl font-bold text-gradient">{detail.indications_count}</span>
              </div>
              <div className="px-4 py-2.5 bg-accent-light rounded-xl">
                <span className="text-[11px] text-muted font-medium uppercase tracking-wider block">Relations</span>
                <span className="text-2xl font-bold text-gradient">{detail.relationships.length}</span>
              </div>
            </div>
            <button
              onClick={() => setDetail(null)}
              className="mt-4 text-sm text-muted hover:text-accent transition-colors cursor-pointer"
            >
              ← Back to results
            </button>
          </div>

          {/* Top rubrics */}
          {detail.top_rubrics.length > 0 && (
            <div className="glass-card p-5">
              <span className="section-label">Top Rubrics ({detail.top_rubrics.length})</span>
              <div className="space-y-2 mt-3">
                {detail.top_rubrics.map((r, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span
                      className={`text-[11px] font-bold px-2.5 py-0.5 rounded-md grade-${r.grade}`}
                    >
                      G{r.grade}
                    </span>
                    <span className="text-sm text-foreground/80">{r.rubric}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Relationships */}
          {Object.keys(relGroups).length > 0 && (
            <div className="glass-card p-5">
              <span className="section-label">Relationships ({detail.relationships.length})</span>
              <div className="space-y-5 mt-3">
                {Object.entries(relGroups).map(([type, rels]) => (
                  <div key={type}>
                    <h4 className="text-xs font-semibold text-foreground/60 mb-2">
                      {REL_LABELS[type] || type} <span className="text-muted">({rels.length})</span>
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {rels.map((r, i) => (
                        <button
                          key={i}
                          onClick={() => {
                            setQuery(r.target || r.target_abbrev);
                            openDetail(r.target_abbrev);
                          }}
                          className={`tag cursor-pointer hover:opacity-80 transition-opacity ${
                            REL_COLORS[type] || "bg-card-hover text-muted"
                          }`}
                        >
                          {r.target || r.target_abbrev}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
