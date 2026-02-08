"""
Case Memory — graph operations for temporal case tracking.

Stores and retrieves time-indexed snapshots of a patient case
including observed symptoms, their intensities, and prescriptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.graph_client import GraphClient


@dataclass
class SnapshotData:
    snapshot_id: str
    day: int
    symptoms: list[dict[str, Any]] = field(default_factory=list)
    # Each symptom: {"id": str, "name": str, "intensity": float, "category": str}
    prescription: dict[str, Any] | None = None
    # {"remedy": str, "potency": str}


@dataclass
class CaseTimeline:
    case_id: str
    patient_id: str
    snapshots: list[SnapshotData] = field(default_factory=list)
    outcome: str | None = None


def get_case_timeline(
    graph: GraphClient,
    case_id: str,
) -> CaseTimeline | None:
    """
    Retrieve full timeline for a case: all snapshots with
    their symptoms, intensities, and prescriptions.
    """
    # Basic case info
    case_records = graph.run_query(
        """
        MATCH (c:Case {id: $case_id})
        OPTIONAL MATCH (c)-[:OUTCOME]->(o:Outcome)
        RETURN c.patient_id AS patient_id, o.type AS outcome
        """,
        case_id=case_id,
    )
    if not case_records:
        return None

    patient_id = case_records[0]["patient_id"]
    outcome = case_records[0]["outcome"]

    # Snapshots
    snap_records = graph.run_query(
        """
        MATCH (c:Case {id: $case_id})-[hs:HAS_SNAPSHOT]->(cs:CaseSnapshot)
        RETURN cs.id AS snap_id, hs.day AS day
        ORDER BY hs.day
        """,
        case_id=case_id,
    )

    snapshots: list[SnapshotData] = []
    for sr in snap_records:
        snap_id = sr["snap_id"]
        day = sr["day"]

        # Symptoms
        sym_records = graph.run_query(
            """
            MATCH (cs:CaseSnapshot {id: $snap_id})-[os:OBSERVED_SYMPTOM]->(s:Symptom)
            RETURN s.id AS id, s.name AS name, s.category AS category, os.intensity AS intensity
            ORDER BY os.intensity DESC
            """,
            snap_id=snap_id,
        )

        # Prescription
        presc_records = graph.run_query(
            """
            MATCH (cs:CaseSnapshot {id: $snap_id})-[p:PRESCRIBED]->(rem:Remedy)
            RETURN rem.name AS remedy, p.potency AS potency
            """,
            snap_id=snap_id,
        )

        prescription = None
        if presc_records:
            prescription = {
                "remedy": presc_records[0]["remedy"],
                "potency": presc_records[0]["potency"],
            }

        snapshots.append(
            SnapshotData(
                snapshot_id=snap_id,
                day=day,
                symptoms=[dict(r) for r in sym_records],
                prescription=prescription,
            )
        )

    return CaseTimeline(
        case_id=case_id,
        patient_id=patient_id,
        snapshots=snapshots,
        outcome=outcome,
    )


def store_snapshot(
    graph: GraphClient,
    case_id: str,
    patient_id: str,
    snapshot_id: str,
    day: int,
    symptoms: list[tuple[str, float]],  # (symptom_id, intensity)
    prescription: tuple[str, str] | None = None,  # (remedy_name, potency)
):
    """Persist a new case snapshot into the graph."""
    graph.run_write(
        "MERGE (c:Case {id: $cid}) SET c.patient_id = $pid",
        cid=case_id,
        pid=patient_id,
    )
    graph.run_write(
        """
        MATCH (c:Case {id: $cid})
        MERGE (cs:CaseSnapshot {id: $sid})
        MERGE (c)-[:HAS_SNAPSHOT {day: $day}]->(cs)
        """,
        cid=case_id,
        sid=snapshot_id,
        day=day,
    )
    for sym_id, intensity in symptoms:
        graph.run_write(
            """
            MATCH (cs:CaseSnapshot {id: $sid}), (s:Symptom {id: $sym_id})
            MERGE (cs)-[:OBSERVED_SYMPTOM {intensity: $intensity}]->(s)
            """,
            sid=snapshot_id,
            sym_id=sym_id,
            intensity=intensity,
        )
    if prescription:
        remedy_name, potency = prescription
        graph.run_write(
            """
            MATCH (cs:CaseSnapshot {id: $sid}), (rem:Remedy {name: $remedy})
            MERGE (cs)-[:PRESCRIBED {potency: $potency}]->(rem)
            """,
            sid=snapshot_id,
            remedy=remedy_name,
            potency=potency,
        )


def record_outcome(
    graph: GraphClient,
    case_id: str,
    outcome: str,
):
    """Link a case to its outcome."""
    graph.run_write(
        """
        MATCH (c:Case {id: $cid}), (o:Outcome {type: $outcome})
        MERGE (c)-[:OUTCOME]->(o)
        """,
        cid=case_id,
        outcome=outcome,
    )
