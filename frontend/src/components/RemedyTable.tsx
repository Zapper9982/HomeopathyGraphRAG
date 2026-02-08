"use client";

import Link from "next/link";
import type { RankedRemedy, UncertaintyResult } from "@/lib/types";

interface Props {
  remedies: RankedRemedy[];
  uncertainty?: UncertaintyResult;
}

export function RemedyTable({ remedies, uncertainty }: Props) {
  if (!remedies.length) {
    return (
      <div className="glass-card p-5 text-muted text-sm">
        No remedies found for these symptoms.
      </div>
    );
  }

  const hasCI = remedies.some((r) => r.confidence_interval);
  const topScore = Math.max(...remedies.map((r) => r.mean_score ?? r.score));

  return (
    <div className="glass-card overflow-hidden">
      <div className="px-5 py-4 border-b border-border/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="section-label">Remedy Rankings</span>
          <span className="tag bg-accent-light text-accent font-semibold">{remedies.length}</span>
        </div>
        {uncertainty && (
          <span className="tag bg-accent-light text-accent">
            Certainty: {(uncertainty.overall_certainty * 100).toFixed(0)}%
          </span>
        )}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-[11px] uppercase tracking-wider text-muted border-b border-border/60">
              <th className="px-5 py-3 text-left w-10">#</th>
              <th className="px-5 py-3 text-left">Remedy</th>
              <th className="px-5 py-3 text-right">Score</th>
              {hasCI && <th className="px-5 py-3 text-center">Confidence</th>}
              {hasCI && <th className="px-5 py-3 text-right">Stability</th>}
              <th className="px-5 py-3 text-right">Hits</th>
            </tr>
          </thead>
          <tbody>
            {remedies.slice(0, 15).map((r, i) => {
              const score = r.mean_score ?? r.score;
              const ci = r.confidence_interval;
              const barWidth = topScore > 0 ? Math.round((score / topScore) * 100) : 0;

              return (
                <tr
                  key={r.remedy}
                  className="border-b border-border/30 hover:bg-accent/3 transition-colors group"
                >
                  <td className="px-5 py-3.5">
                    <span className={`inline-flex items-center justify-center w-6 h-6 rounded-lg text-xs font-bold ${
                      i === 0 ? "bg-linear-to-br from-accent to-purple-500 text-white" :
                      i < 3 ? "bg-accent-light text-accent" : "bg-card-hover text-muted"
                    }`}>
                      {i + 1}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <Link
                      href={`/explore?q=${encodeURIComponent(r.remedy)}`}
                      className="text-foreground font-medium hover:text-accent transition-colors"
                    >
                      {r.remedy}
                    </Link>
                  </td>
                  <td className="px-5 py-3.5 text-right font-mono text-[13px]">
                    <div className="flex items-center justify-end gap-2.5">
                      <div className="w-20 confidence-bar">
                        <div
                          className="confidence-bar-fill bar-gradient"
                          style={{ width: `${barWidth}%` }}
                        />
                      </div>
                      <span className="text-foreground/80">{score.toFixed(3)}</span>
                    </div>
                  </td>
                  {hasCI && (
                    <td className="px-5 py-3.5 text-center font-mono text-xs text-muted">
                      {ci
                        ? `[${ci[0].toFixed(3)}, ${ci[1].toFixed(3)}]`
                        : "—"}
                    </td>
                  )}
                  {hasCI && (
                    <td className="px-5 py-3.5 text-right font-mono text-xs">
                      {r.rank_stability !== undefined
                        ? r.rank_stability.toFixed(2)
                        : "—"}
                    </td>
                  )}
                  <td className="px-5 py-3.5 text-right font-mono text-muted">
                    {r.rubric_hits}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
