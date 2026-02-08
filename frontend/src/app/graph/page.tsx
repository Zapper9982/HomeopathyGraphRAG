"use client";

import { useEffect, useState } from "react";
import { getGraphStats } from "@/lib/api";
import type { GraphStats } from "@/lib/types";

const NODE_ICONS: Record<string, string> = {
  Remedy: "💊",
  Rubric: "📋",
  Symptom: "🩺",
  Case: "📁",
};

const EDGE_COLORS: Record<string, string> = {
  INDICATES: "text-accent",
  BELONGS_TO: "text-foreground",
  CORRELATED_WITH: "text-accent-dim",
  ANTIDOTES: "text-danger",
  COMPLEMENTARY: "text-success",
  INCOMPATIBLE: "text-warning",
  FOLLOWS_WELL: "text-accent",
};

export default function GraphPage() {
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getGraphStats()
      .then(setStats)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <div className="spinner" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card border-danger/30! p-4 text-danger bg-danger/5">
        Failed to load stats: {error}
      </div>
    );
  }

  if (!stats) return null;

  const totalNodes = Object.values(stats.nodes).reduce((a, b) => a + b, 0);
  const totalEdges = Object.values(stats.edges).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-2 animate-fade-in">
        <h1 className="text-3xl font-bold tracking-tight">
          <span className="text-gradient">Knowledge Graph</span>
        </h1>
        <p className="text-muted text-sm">Real-time statistics from the Neo4j knowledge graph</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <StatCard label="Total Nodes" value={totalNodes.toLocaleString()} icon="○" />
        <StatCard label="Total Edges" value={totalEdges.toLocaleString()} icon="━" />
        <StatCard label="Reachable" value={stats.reachable_remedies.toString()} icon="◉" />
        <StatCard
          label="Coverage"
          value={`${Math.round((stats.reachable_remedies / (stats.nodes.Remedy || 1)) * 100)}%`}
          icon="◐"
        />
      </div>

      {/* Node breakdown */}
      <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: '0.15s' }}>
        <span className="section-label">Node Types</span>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mt-4">
          {Object.entries(stats.nodes).map(([label, count]) => (
            <div key={label} className="flex items-center gap-3 group">
              <span className="text-2xl">{NODE_ICONS[label] || "📦"}</span>
              <div>
                <p className="text-xs text-muted font-medium">{label}</p>
                <p className="text-xl font-bold tracking-tight">{count.toLocaleString()}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Edge breakdown */}
      <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: '0.2s' }}>
        <span className="section-label">Edge Types</span>
        <div className="space-y-3 mt-4">
          {Object.entries(stats.edges)
            .sort(([, a], [, b]) => b - a)
            .map(([type, count]) => {
              const pct = totalEdges > 0 ? (count / totalEdges) * 100 : 0;
              return (
                <div key={type} className="flex items-center gap-4 group">
                  <span className={`w-40 text-sm font-mono font-medium ${EDGE_COLORS[type] || "text-muted"}`}>
                    {type}
                  </span>
                  <div className="flex-1 confidence-bar h-2.5">
                    <div
                      className="confidence-bar-fill bar-gradient"
                      style={{ width: `${Math.max(pct, 0.5)}%` }}
                    />
                  </div>
                  <span className="text-sm font-mono text-muted w-20 text-right tabular-nums">
                    {count.toLocaleString()}
                  </span>
                </div>
              );
            })}
        </div>
      </div>

      {/* Architecture info */}
      <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: '0.25s' }}>
        <span className="section-label">Architecture</span>
        <div className="grid md:grid-cols-2 gap-8 text-sm mt-4">
          <div>
            <h3 className="font-semibold mb-3 text-foreground">Intelligence Layers</h3>
            <ul className="space-y-2.5 text-foreground/70">
              <li className="flex items-center gap-2.5"><span className="w-2 h-2 rounded-full bg-success" /> Symptom Reliability & Contradiction Detection</li>
              <li className="flex items-center gap-2.5"><span className="w-2 h-2 rounded-full bg-success" /> Uncertainty Estimation (Bootstrap)</li>
              <li className="flex items-center gap-2.5"><span className="w-2 h-2 rounded-full bg-success" /> Temporal Evolution Reasoning</li>
              <li className="flex items-center gap-2.5"><span className="w-2 h-2 rounded-full bg-success" /> Rare Pattern Discovery (Graph Mining)</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-3 text-foreground">Design Principles</h3>
            <ul className="space-y-2.5 text-foreground/70">
              <li className="flex items-center gap-2.5"><span className="w-2 h-2 rounded-full bg-accent" /> All reasoning is graph-based — never LLM</li>
              <li className="flex items-center gap-2.5"><span className="w-2 h-2 rounded-full bg-accent" /> LLMs only structure input & explain output</li>
              <li className="flex items-center gap-2.5"><span className="w-2 h-2 rounded-full bg-accent" /> Traversal: Symptom → Rubric → Remedy</li>
              <li className="flex items-center gap-2.5"><span className="w-2 h-2 rounded-full bg-accent" /> Data: Boericke&apos;s Materia Medica (1927)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: string; icon: string }) {
  return (
    <div className="glass-card p-5 text-center">
      <span className="text-gradient text-2xl">{icon}</span>
      <p className="text-2xl font-bold mt-2 tracking-tight">{value}</p>
      <p className="text-[11px] text-muted uppercase tracking-wider font-medium mt-1">{label}</p>
    </div>
  );
}
