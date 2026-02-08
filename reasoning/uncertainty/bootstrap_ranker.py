"""
Bootstrap Ranker — perturb symptom subsets and re-rank
across multiple graph traversals to measure ranking stability.

Purely algorithmic — NO LLM.
"""

from __future__ import annotations

import random
from typing import Any

from core.graph_client import GraphClient
from core.remedy_ranker import rank_remedies_from_ids
import config


def bootstrap_rank(
    graph: GraphClient,
    symptom_ids: list[str],
    n_iterations: int = config.BOOTSTRAP_ITERATIONS,
    drop_fraction: float = config.SYMPTOM_DROP_FRACTION,
    seed: int | None = None,
) -> dict[str, list[float]]:
    """
    Run n_iterations of:
      1. Randomly drop `drop_fraction` of symptoms
      2. Rank remedies on the remaining subset
      3. Record each remedy's score

    Returns:
      { remedy_name: [score_iter_0, score_iter_1, ...] }
    """
    if not symptom_ids:
        return {}

    rng = random.Random(seed)
    n_drop = max(1, int(len(symptom_ids) * drop_fraction))
    # Ensure at least 1 symptom remains
    n_drop = min(n_drop, len(symptom_ids) - 1)
    if n_drop <= 0:
        n_drop = 0  # single symptom — no perturbation possible

    remedy_scores: dict[str, list[float]] = {}

    for _ in range(n_iterations):
        # Perturb: drop random subset
        if n_drop > 0:
            subset = list(symptom_ids)
            rng.shuffle(subset)
            subset = subset[n_drop:]
        else:
            subset = list(symptom_ids)

        # Rank on perturbed subset
        ranked = rank_remedies_from_ids(graph, subset)

        # Record scores
        seen = set()
        for r in ranked:
            name = r["remedy"]
            seen.add(name)
            if name not in remedy_scores:
                remedy_scores[name] = []
            remedy_scores[name].append(r["score"])

        # Remedies NOT in this subset's ranking get a 0
        for name in remedy_scores:
            if name not in seen:
                remedy_scores[name].append(0.0)

    return remedy_scores


def bootstrap_rank_optimized(
    graph: GraphClient,
    symptom_ids: list[str],
    n_iterations: int = config.BOOTSTRAP_ITERATIONS,
    drop_fraction: float = config.SYMPTOM_DROP_FRACTION,
    seed: int | None = None,
) -> dict[str, list[float]]:
    """
    Optimized version: batch-queries the graph once for the
    full symptom→rubric→remedy map, then re-ranks in memory.

    Significant speedup for large iteration counts.
    """
    if not symptom_ids:
        return {}

    # Pre-fetch full indication map
    records = graph.run_query(
        """
        UNWIND $ids AS sid
        MATCH (s:Symptom {id: sid})-[:BELONGS_TO]->(r:Rubric)-[ind:INDICATES]->(rem:Remedy)
        RETURN sid AS symptom_id, rem.name AS remedy, ind.grade AS grade
        """,
        ids=symptom_ids,
    )

    # Build index: symptom_id → [(remedy, grade)]
    symptom_to_indications: dict[str, list[tuple[str, int]]] = {}
    for rec in records:
        sid = rec["symptom_id"]
        if sid not in symptom_to_indications:
            symptom_to_indications[sid] = []
        symptom_to_indications[sid].append((rec["remedy"], rec["grade"]))

    rng = random.Random(seed)
    n_drop = max(1, int(len(symptom_ids) * drop_fraction))
    n_drop = min(n_drop, len(symptom_ids) - 1)
    if n_drop <= 0:
        n_drop = 0

    remedy_scores: dict[str, list[float]] = {}

    for _ in range(n_iterations):
        if n_drop > 0:
            subset = list(symptom_ids)
            rng.shuffle(subset)
            subset = subset[n_drop:]
        else:
            subset = list(symptom_ids)

        # In-memory ranking
        max_possible = 3 * len(subset)
        tallies: dict[str, float] = {}
        for sid in subset:
            for remedy, grade in symptom_to_indications.get(sid, []):
                tallies[remedy] = tallies.get(remedy, 0.0) + grade

        # Normalize
        scored: dict[str, float] = {}
        for remedy, raw in tallies.items():
            scored[remedy] = round(raw / max_possible, 4) if max_possible else 0.0

        seen = set(scored.keys())
        for name, score in scored.items():
            if name not in remedy_scores:
                remedy_scores[name] = []
            remedy_scores[name].append(score)

        for name in remedy_scores:
            if name not in seen:
                remedy_scores[name].append(0.0)

    return remedy_scores
