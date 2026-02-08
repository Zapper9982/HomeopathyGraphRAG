"""
Outcome Correlator — links mined symptom patterns to case outcomes
and computes success rates per pattern×remedy combination.

Purely algorithmic — NO LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.graph_client import GraphClient
from reasoning.pattern_mining.subgraph_miner import (
    SymptomPattern,
    mine_symptom_subgraphs,
    find_patterns_matching,
)
import config


@dataclass
class PatternOutcome:
    """A symptom pattern correlated with a remedy and its success rate."""
    pattern: SymptomPattern
    remedy: str
    success_count: int       # cases with this pattern + remedy → Improved
    total_count: int         # cases with this pattern + remedy
    success_rate: float
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "symptoms": self.pattern.symptom_names,
            "remedy": self.remedy,
            "success_rate": round(self.success_rate, 2),
            "success_count": self.success_count,
            "total_count": self.total_count,
            "pattern_support": round(self.pattern.support, 4),
            "description": self.description,
        }


@dataclass
class RarePatternReport:
    discoveries: list[PatternOutcome] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rare_patterns": [d.to_dict() for d in self.discoveries],
        }


def discover_rare_patterns(
    graph: GraphClient,
    symptom_ids: list[str] | None = None,
    min_frequency: int = config.MIN_PATTERN_FREQUENCY,
    min_success_rate: float = config.MIN_SUCCESS_RATE,
    max_pattern_size: int = config.MAX_PATTERN_SIZE,
) -> RarePatternReport:
    """
    1. Mine symptom subgraphs from all case history
    2. For each pattern, find cases with that pattern
    3. For each case, find prescribed remedy and outcome
    4. Compute success rate per pattern×remedy
    5. Filter by min_success_rate
    6. Optionally filter to patterns matching current symptoms

    Returns RarePatternReport with ranked discoveries.
    """
    # ── Step 1: mine patterns ────────────────────────────
    all_patterns = mine_symptom_subgraphs(
        graph,
        min_frequency=min_frequency,
        max_pattern_size=max_pattern_size,
    )

    if not all_patterns:
        return RarePatternReport()

    # If symptom_ids given, filter to matching patterns
    if symptom_ids:
        relevant_patterns = find_patterns_matching(all_patterns, symptom_ids)
    else:
        relevant_patterns = all_patterns

    if not relevant_patterns:
        return RarePatternReport()

    # ── Step 2–4: correlate with outcomes ────────────────
    discoveries: list[PatternOutcome] = []

    for pattern in relevant_patterns:
        pattern_syms = list(pattern.symptom_ids)

        # Find cases containing this pattern and their outcome + remedy
        records = graph.run_query(
            """
            MATCH (c:Case)-[:HAS_SNAPSHOT]->(cs:CaseSnapshot)-[:OBSERVED_SYMPTOM]->(s:Symptom)
            WHERE s.id IN $pattern_syms
            WITH c, cs, collect(DISTINCT s.id) AS observed_syms
            WHERE size($pattern_syms) <= size(observed_syms)
              AND all(ps IN $pattern_syms WHERE ps IN observed_syms)
            MATCH (cs)-[:PRESCRIBED]->(rem:Remedy)
            MATCH (c)-[:OUTCOME]->(o:Outcome)
            RETURN c.id AS case_id, rem.name AS remedy, o.type AS outcome
            """,
            pattern_syms=pattern_syms,
        )

        if not records:
            continue

        # Group by remedy
        remedy_outcomes: dict[str, dict[str, int]] = {}
        for rec in records:
            remedy = rec["remedy"]
            outcome = rec["outcome"]
            if remedy not in remedy_outcomes:
                remedy_outcomes[remedy] = {"Improved": 0, "NoChange": 0, "Worsened": 0, "_total": 0}
            remedy_outcomes[remedy][outcome] = remedy_outcomes[remedy].get(outcome, 0) + 1
            remedy_outcomes[remedy]["_total"] += 1

        for remedy, outcomes in remedy_outcomes.items():
            total = outcomes["_total"]
            success = outcomes.get("Improved", 0)
            if total < 1:
                continue
            success_rate = success / total

            if success_rate >= min_success_rate:
                symptom_str = " + ".join(pattern.symptom_names)
                desc = (
                    f"Rare pattern detected: {symptom_str} "
                    f"→ {remedy} ({success_rate:.0%} success, n={total} cases)"
                )
                discoveries.append(
                    PatternOutcome(
                        pattern=pattern,
                        remedy=remedy,
                        success_count=success,
                        total_count=total,
                        success_rate=success_rate,
                        description=desc,
                    )
                )

    # Sort by success rate descending, then by total cases
    discoveries.sort(key=lambda d: (-d.success_rate, -d.total_count))

    return RarePatternReport(discoveries=discoveries)


def discover_for_current_case(
    graph: GraphClient,
    symptom_ids: list[str],
) -> RarePatternReport:
    """Convenience: discover rare patterns relevant to the current case."""
    return discover_rare_patterns(graph, symptom_ids=symptom_ids)
