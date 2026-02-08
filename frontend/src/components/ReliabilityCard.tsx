"use client";

import type { ReliabilityResult } from "@/lib/types";

interface Props {
  data: ReliabilityResult;
}

export function ReliabilityCard({ data }: Props) {
  const score = data.reliability_score;
  const pct = Math.round(score * 100);
  const color =
    pct >= 80 ? "bg-success" : pct >= 50 ? "bg-warning" : "bg-danger";
  const textColor =
    pct >= 80 ? "text-success" : pct >= 50 ? "text-warning" : "text-danger";

  return (
    <div className="glass-card p-5">
      <span className="section-label">Symptom Reliability</span>
      <div className="flex items-center gap-4 mt-3">
        <div className="flex-1">
          <div className="confidence-bar h-2.5">
            <div
              className={`confidence-bar-fill ${color}`}
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>
        <span className={`text-xl font-bold tabular-nums ${textColor}`}>
          {pct}%
        </span>
      </div>

      {data.alerts.length > 0 && (
        <div className="mt-3 space-y-1">
          {data.alerts.map((alert, i) => (
            <div key={i} className="flex items-start gap-2 text-sm text-warning">
              <span>⚠</span>
              <span>{alert}</span>
            </div>
          ))}
        </div>
      )}

      {data.suggestion && (
        <p className="mt-2 text-sm text-muted">→ {data.suggestion}</p>
      )}
    </div>
  );
}
