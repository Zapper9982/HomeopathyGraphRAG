"""
Symptom Reliability Scorer — purely algorithmic.

Computes a reliability score for the case's symptom set
based on internal consistency (contradictions, correlations).

NO LLM reasoning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.graph_client import GraphClient
from reasoning.reliability.contradiction_detector import (
    Contradiction,
    detect_contradictions,
    find_correlated_missing,
)
import config


@dataclass
class ReliabilityReport:
    """Structured output of the reliability engine."""

    reliability_score: float
    alerts: list[str] = field(default_factory=list)
    suggestion: str = ""
    contradictions: list[Contradiction] = field(default_factory=list)
    correlated_missing: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reliability_score": round(self.reliability_score, 2),
            "alerts": self.alerts,
            "suggestion": self.suggestion,
            "contradictions": [
                {
                    "symptom_a": c.symptom_a_name,
                    "symptom_b": c.symptom_b_name,
                    "strength": c.strength,
                    "source": c.source,
                }
                for c in self.contradictions
            ],
            "correlated_missing": self.correlated_missing,
        }


def compute_reliability(
    graph: GraphClient,
    symptom_ids: list[str],
) -> ReliabilityReport:
    """
    Algorithm:
      1. Start with score = 1.0
      2. For each contradiction found, subtract penalty * strength
      3. Bonus if correlated symptoms are present (internal consistency)
      4. Flag missing correlated symptoms as potential inquiry points

    Returns a ReliabilityReport.
    """
    if not symptom_ids:
        return ReliabilityReport(
            reliability_score=0.0,
            alerts=["No symptoms provided"],
            suggestion="Please provide at least one symptom",
        )

    # ── Step 1: detect contradictions ────────────────────
    contradictions = detect_contradictions(graph, symptom_ids)

    # ── Step 2: compute base score ───────────────────────
    score = 1.0
    alerts: list[str] = []

    for c in contradictions:
        penalty = config.RELIABILITY_PENALTY_PER_CONTRADICTION * c.strength
        score -= penalty
        alerts.append(c.alert_text)

    # ── Step 3: correlation bonus ────────────────────────
    # Check how many expected correlated symptoms are present
    correlation_records = graph.run_query(
        """
        UNWIND $ids AS sid
        MATCH (s:Symptom {id: sid})-[r:CORRELATED_WITH]-(other:Symptom)
        WHERE other.id IN $ids AND r.strength >= 0.5
        RETURN count(DISTINCT r) AS corr_count
        """,
        ids=symptom_ids,
    )
    corr_count = correlation_records[0]["corr_count"] if correlation_records else 0
    # Small bonus for internal consistency (max +0.1)
    consistency_bonus = min(corr_count * 0.03, 0.1)
    score += consistency_bonus

    # ── Step 4: find missing correlated symptoms ─────────
    missing = find_correlated_missing(graph, symptom_ids)

    # ── Assemble suggestion ──────────────────────────────
    score = max(0.0, min(1.0, score))  # clamp

    suggestion = ""
    if contradictions:
        categories = set()
        for c in contradictions:
            for cat in _symptom_categories(graph, [c.symptom_a_id, c.symptom_b_id]):
                categories.add(cat)
        if categories:
            suggestion = f"Reconfirm {', '.join(sorted(categories))}"
        else:
            suggestion = "Reconfirm conflicting symptoms with patient"
    elif missing:
            missing_names = [
                m.get("missing_name", str(m)) if isinstance(m, dict) else str(m)
                for m in missing[:3]
            ]

    return ReliabilityReport(
        reliability_score=score,
        alerts=alerts,
        suggestion=suggestion,
        contradictions=contradictions,
        correlated_missing=missing,
    )


def _symptom_categories(
    graph: GraphClient,
    symptom_ids: list[str],
) -> list[str]:
    """Return distinct categories for given symptom IDs."""
    records = graph.run_query(
        """
        UNWIND $ids AS sid
        MATCH (s:Symptom {id: sid})
        RETURN DISTINCT s.category AS cat
        """,
        ids=symptom_ids,
    )
    return [r["cat"] for r in records if r["cat"]]
