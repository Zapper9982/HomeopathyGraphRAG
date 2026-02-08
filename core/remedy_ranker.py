"""
Graph-based Remedy Ranker.

Purely algorithmic — traverses Symptom → Rubric → Remedy
and aggregates weighted grades to produce a ranked list.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.graph_client import GraphClient


@dataclass
class RemedyScore:
    name: str
    raw_score: float = 0.0
    rubric_hits: int = 0
    grade_details: list[dict[str, Any]] = field(default_factory=list)


def rank_remedies(
    graph: GraphClient,
    symptom_ids: list[str],
) -> list[RemedyScore]:
    """
    For each symptom → find rubrics → find remedy indications.
    Score = Σ grade  (grade 3 = strong, 1 = weak)
    Normalized by total possible score.

    Returns descending-sorted list of RemedyScore.
    """
    if not symptom_ids:
        return []

    records = graph.run_query(
        """
        UNWIND $ids AS sid
        MATCH (s:Symptom {id: sid})-[:BELONGS_TO]->(r:Rubric)-[ind:INDICATES]->(rem:Remedy)
        RETURN rem.name AS remedy, ind.grade AS grade, r.text AS rubric, s.id AS symptom_id
        """,
        ids=symptom_ids,
    )

    # Aggregate
    scores: dict[str, RemedyScore] = {}
    for rec in records:
        name = rec["remedy"]
        if name not in scores:
            scores[name] = RemedyScore(name=name)
        rs = scores[name]
        rs.raw_score += rec["grade"]
        rs.rubric_hits += 1
        rs.grade_details.append(
            {
                "symptom_id": rec["symptom_id"],
                "rubric": rec["rubric"],
                "grade": rec["grade"],
            }
        )

    # Normalize: max possible = 3 * len(symptom_ids)
    max_possible = 3 * len(symptom_ids)
    for rs in scores.values():
        rs.raw_score = round(rs.raw_score / max_possible, 4) if max_possible else 0.0

    ranked = sorted(scores.values(), key=lambda r: r.raw_score, reverse=True)
    return ranked


def rank_remedies_from_ids(
    graph: GraphClient,
    symptom_ids: list[str],
) -> list[dict[str, Any]]:
    """Convenience wrapper returning plain dicts."""
    ranked = rank_remedies(graph, symptom_ids)
    return [
        {
            "remedy": r.name,
            "score": r.raw_score,
            "rubric_hits": r.rubric_hits,
            "details": r.grade_details,
        }
        for r in ranked
    ]
