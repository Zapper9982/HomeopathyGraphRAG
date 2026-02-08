"""
Subgraph Miner — discovers low-frequency symptom subgraphs
from historical case data in the knowledge graph.

Uses an Apriori-like algorithm on the case→snapshot→symptom
graph to find co-occurring symptom sets, then filters for
rare (low-frequency) patterns.

Purely algorithmic — NO LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Any

from core.graph_client import GraphClient
import config


@dataclass
class SymptomPattern:
    """A set of symptoms observed together across cases."""
    symptom_ids: frozenset[str]
    symptom_names: list[str]
    frequency: int        # number of cases containing this pattern
    total_cases: int      # total cases in the database
    support: float        # frequency / total_cases

    def to_dict(self) -> dict[str, Any]:
        return {
            "symptoms": self.symptom_names,
            "frequency": self.frequency,
            "total_cases": self.total_cases,
            "support": round(self.support, 4),
        }


def mine_symptom_subgraphs(
    graph: GraphClient,
    min_frequency: int = config.MIN_PATTERN_FREQUENCY,
    max_pattern_size: int = config.MAX_PATTERN_SIZE,
) -> list[SymptomPattern]:
    """
    Mine frequent and rare symptom subgraphs from case history.

    Algorithm (Apriori-inspired):
      1. Extract all case → symptom sets from the graph
      2. For k = 2 to max_pattern_size:
         a. Generate candidate k-itemsets from (k-1)-itemsets
         b. Count support across cases
         c. Keep patterns with frequency >= min_frequency
      3. Return all patterns, tagged with frequency info
    """
    # ── Step 1: extract case → symptom sets ──────────────
    records = graph.run_query(
        """
        MATCH (c:Case)-[:HAS_SNAPSHOT]->(:CaseSnapshot)-[:OBSERVED_SYMPTOM]->(s:Symptom)
        RETURN c.id AS case_id, collect(DISTINCT s.id) AS symptom_ids
        """
    )

    if not records:
        return []

    case_symptom_sets: list[frozenset[str]] = [
        frozenset(r["symptom_ids"]) for r in records
    ]
    total_cases = len(case_symptom_sets)

    # Symptom name lookup
    name_records = graph.run_query(
        "MATCH (s:Symptom) RETURN s.id AS id, s.name AS name"
    )
    id_to_name = {r["id"]: r["name"] for r in name_records}

    # ── Step 2: Apriori-style mining ─────────────────────
    # Level 1: individual symptoms
    item_counts: dict[frozenset[str], int] = {}
    for case_syms in case_symptom_sets:
        for sym in case_syms:
            key = frozenset([sym])
            item_counts[key] = item_counts.get(key, 0) + 1

    # Filter level 1
    frequent: dict[frozenset[str], int] = {
        k: v for k, v in item_counts.items() if v >= min_frequency
    }

    all_patterns: list[SymptomPattern] = []

    # Levels 2 to max_pattern_size
    prev_level_items = frequent
    for k in range(2, max_pattern_size + 1):
        candidates = _generate_candidates(prev_level_items, k)
        if not candidates:
            break

        level_counts: dict[frozenset[str], int] = {}
        for case_syms in case_symptom_sets:
            for cand in candidates:
                if cand.issubset(case_syms):
                    level_counts[cand] = level_counts.get(cand, 0) + 1

        level_frequent = {
            k: v for k, v in level_counts.items() if v >= min_frequency
        }

        for pattern_ids, freq in level_frequent.items():
            names = [id_to_name.get(sid, sid) for sid in sorted(pattern_ids)]
            all_patterns.append(
                SymptomPattern(
                    symptom_ids=pattern_ids,
                    symptom_names=names,
                    frequency=freq,
                    total_cases=total_cases,
                    support=freq / total_cases,
                )
            )

        prev_level_items = level_frequent

    # Sort by support ascending (rarest first)
    all_patterns.sort(key=lambda p: (p.support, -len(p.symptom_ids)))

    return all_patterns


def find_patterns_matching(
    patterns: list[SymptomPattern],
    symptom_ids: list[str],
) -> list[SymptomPattern]:
    """
    Given current case symptoms, find all mined patterns
    that are subsets of the current symptom set.
    """
    current = frozenset(symptom_ids)
    return [p for p in patterns if p.symptom_ids.issubset(current)]


# ── Internal helpers ─────────────────────────────────────

def _generate_candidates(
    prev_frequent: dict[frozenset[str], int],
    k: int,
) -> list[frozenset[str]]:
    """Generate candidate k-itemsets from (k-1)-itemsets."""
    items = list(prev_frequent.keys())
    candidates = set()

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            union = items[i] | items[j]
            if len(union) == k:
                # Check all (k-1)-subsets are in prev_frequent (Apriori property)
                valid = True
                for subset in combinations(union, k - 1):
                    if frozenset(subset) not in prev_frequent:
                        valid = False
                        break
                if valid:
                    candidates.add(union)

    return list(candidates)
