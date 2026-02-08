"""
Contradiction Detector — graph-only logic.

Queries the (Symptom)-[:CONTRADICTS]->(Symptom) edges
to detect conflicting symptoms within a case.

NO LLM reasoning.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.graph_client import GraphClient
import config


@dataclass
class Contradiction:
    symptom_a_id: str
    symptom_a_name: str
    symptom_b_id: str
    symptom_b_name: str
    strength: float
    source: str

    @property
    def alert_text(self) -> str:
        return (
            f"'{self.symptom_a_name}' contradicts '{self.symptom_b_name}' "
            f"(strength={self.strength:.2f}, source={self.source})"
        )


def detect_contradictions(
    graph: GraphClient,
    symptom_ids: list[str],
    threshold: float = config.CONTRADICTION_STRENGTH_THRESHOLD,
) -> list[Contradiction]:
    """
    Given a set of symptom IDs observed in a case, find all
    CONTRADICTS edges between them with strength ≥ threshold.

    Returns list of Contradiction objects.
    """
    if len(symptom_ids) < 2:
        return []

    records = graph.run_query(
        """
        UNWIND $ids AS id_a
        UNWIND $ids AS id_b
        WITH id_a, id_b WHERE id_a < id_b
        MATCH (a:Symptom {id: id_a})-[r:CONTRADICTS]-(b:Symptom {id: id_b})
        WHERE r.strength >= $threshold
        RETURN DISTINCT
            a.id AS a_id, a.name AS a_name,
            b.id AS b_id, b.name AS b_name,
            r.strength AS strength, r.source AS source
        ORDER BY r.strength DESC
        """,
        ids=symptom_ids,
        threshold=threshold,
    )

    return [
        Contradiction(
            symptom_a_id=rec["a_id"],
            symptom_a_name=rec["a_name"],
            symptom_b_id=rec["b_id"],
            symptom_b_name=rec["b_name"],
            strength=rec["strength"],
            source=rec["source"],
        )
        for rec in records
    ]


def find_correlated_missing(
    graph: GraphClient,
    symptom_ids: list[str],
    min_strength: float = 0.6,
) -> list[dict[str, Any]]:
    """
    Find symptoms strongly correlated with present symptoms
    but NOT in the current set — suggesting under-reporting
    or additional inquiry needed.
    """
    if not symptom_ids:
        return []

    records = graph.run_query(
        """
        UNWIND $ids AS sid
        MATCH (s:Symptom {id: sid})-[r:CORRELATED_WITH]-(other:Symptom)
        WHERE NOT other.id IN $ids AND r.strength >= $min_strength
        RETURN DISTINCT
            other.id AS missing_id, other.name AS missing_name,
            s.id AS anchor_id, s.name AS anchor_name,
            r.strength AS correlation_strength
        ORDER BY r.strength DESC
        """,
        ids=symptom_ids,
        min_strength=min_strength,
    )
    return [dict(rec) for rec in records]
