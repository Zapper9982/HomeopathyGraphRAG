"use client";

import { useState } from "react";
import { consult } from "@/lib/api";
import type { ConsultResult } from "@/lib/types";
import { RemedyTable } from "@/components/RemedyTable";
import { ReliabilityCard } from "@/components/ReliabilityCard";
import { ExplanationCard } from "@/components/ExplanationCard";
import { ReasoningGraph } from "@/components/ReasoningGraph";

const EXAMPLES = [
  "Patient has throbbing headache worse from light and noise, high fever with red flushed face, sudden onset",
  "Burning pains in stomach, restlessness, anxiety at night, thirst for small sips of water",
  "Irritability, constipation, sensitivity to noise and odours, chilly, worse in morning",
  "Weeping easily, changeable symptoms, thirstlessness, worse in warm room, craves open air",
];

export default function ConsultPage() {
  const [complaint, setComplaint] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ConsultResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [reliability, setReliability] = useState(true);
  const [uncertainty, setUncertainty] = useState(true);
  const [patterns, setPatterns] = useState(true);
  const [explain, setExplain] = useState(true);
  const [showGraph, setShowGraph] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!complaint.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await consult(complaint, {
        enableReliability: reliability,
        enableUncertainty: uncertainty,
        enablePatterns: patterns,
        explain,
      });
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      {/* Hero header */}
      <div className="text-center space-y-2 animate-fade-in">
        <h1 className="text-3xl font-bold tracking-tight">
          <span className="text-gradient">Clinical Analysis</span>
        </h1>
        <p className="text-muted text-sm max-w-md mx-auto">
          Describe patient symptoms and let the knowledge graph find the best remedies
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="glass-card p-6 space-y-5 animate-fade-in" style={{ animationDelay: '0.1s' }}>
          <textarea
            value={complaint}
            onChange={(e) => setComplaint(e.target.value)}
            rows={4}
            placeholder="Describe the patient's symptoms in natural language..."
            className="w-full bg-card-hover/50 border border-border rounded-xl px-4 py-3.5 text-foreground placeholder:text-muted/60 resize-none focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent/40 transition-all text-[15px] leading-relaxed"
          />

          <div className="flex flex-wrap gap-2">
            <span className="section-label self-center mr-1">Examples</span>
            {EXAMPLES.map((ex, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setComplaint(ex)}
                className="tag bg-accent-light text-accent hover:bg-accent/10 cursor-pointer"
              >
                {ex.slice(0, 45)}...
              </button>
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-5 pt-1">
            <span className="section-label">Options</span>
            {[
              { label: "Reliability", state: reliability, set: setReliability },
              { label: "Uncertainty", state: uncertainty, set: setUncertainty },
              { label: "Patterns", state: patterns, set: setPatterns },
              { label: "AI Explain", state: explain, set: setExplain },
            ].map((opt) => (
              <label key={opt.label} className="flex items-center gap-2 cursor-pointer text-sm text-foreground/70 hover:text-foreground transition-colors">
                <input type="checkbox" checked={opt.state} onChange={(e) => opt.set(e.target.checked)} />
                {opt.label}
              </label>
            ))}
          </div>

          <button
            type="submit"
            disabled={loading || !complaint.trim()}
            className="btn-gradient px-7 py-3 text-[15px] cursor-pointer"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Analyzing...
              </span>
            ) : (
              "⚡ Analyze Symptoms"
            )}
          </button>
        </div>
      </form>

      {error && (
        <div className="glass-card border-danger/30! p-4 text-danger bg-danger/5 animate-fade-in">
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading && (
        <div className="flex flex-col items-center justify-center py-16 gap-4 animate-fade-in">
          <div className="spinner pulse-glow" />
          <p className="text-muted text-sm">Traversing the knowledge graph...</p>
        </div>
      )}

      {result && (
        <div className="space-y-5 animate-fade-in">
          {/* Matched symptoms */}
          <div className="glass-card p-5">
            <div className="flex items-center gap-2 mb-3">
              <span className="section-label">Matched Symptoms</span>
              <span className="tag bg-accent-light text-accent font-semibold">
                {result.symptom_ids.length} found
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {result.symptom_ids.map((id) => (
                <span key={id} className="tag bg-accent/5 text-accent border border-accent/15 font-mono text-[11px]">
                  {id}
                </span>
              ))}
              {result.symptom_ids.length === 0 && (
                <span className="text-muted text-sm">No symptoms matched in the graph</span>
              )}
            </div>
          </div>

          {result.reliability && <ReliabilityCard data={result.reliability} />}

          <RemedyTable remedies={result.ranked_remedies} uncertainty={result.uncertainty} />

          {/* Reasoning Graph Toggle */}
          {result.ranked_remedies.length > 0 && (
            <div className="space-y-3">
              <button
                onClick={() => setShowGraph(!showGraph)}
                className="glass-card px-5 py-3 text-sm font-medium hover:border-accent/30 transition-all flex items-center gap-3 w-full text-left cursor-pointer"
              >
                <span className="w-6 h-6 rounded-md bg-linear-to-br from-accent to-purple-500 flex items-center justify-center text-white text-xs">
                  {showGraph ? "−" : "+"}
                </span>
                <span className="text-foreground">{showGraph ? "Hide" : "Show"} Reasoning Graph</span>
                <span className="text-xs text-muted">
                  — visualize how the graph reached this conclusion
                </span>
              </button>
              {showGraph && <ReasoningGraph result={result} />}
            </div>
          )}

          {result.rare_patterns && result.rare_patterns.length > 0 && (
            <div className="glass-card p-5">
              <span className="section-label">Rare Pattern Discoveries</span>
              <div className="mt-3 space-y-2">
                {result.rare_patterns.map((p, i) => (
                  <div key={i} className="flex items-start gap-2.5">
                    <span className="text-warning text-lg leading-none">★</span>
                    <span className="text-sm text-foreground/80">{p.description}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.explanation && <ExplanationCard text={result.explanation} />}

          {result.elapsed_seconds && (
            <p className="text-xs text-muted text-right">
              Completed in {result.elapsed_seconds.toFixed(1)}s
            </p>
          )}
        </div>
      )}
    </div>
  );
}
