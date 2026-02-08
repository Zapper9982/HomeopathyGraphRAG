"""
Schema extensions for Temporal Case Memory & Evolution Reasoning.

New nodes:
  Case          — represents a patient case over time
  CaseSnapshot  — a point-in-time observation within a case

New relationships:
  (Case)-[:HAS_SNAPSHOT {day: int}]->(CaseSnapshot)
  (CaseSnapshot)-[:OBSERVED_SYMPTOM {intensity: float 0-1}]->(Symptom)
  (CaseSnapshot)-[:PRESCRIBED {potency: str}]->(Remedy)
"""

TEMPORAL_CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Case) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (cs:CaseSnapshot) REQUIRE cs.id IS UNIQUE",
]

TEMPORAL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS FOR (c:Case) ON (c.patient_id)",
    "CREATE INDEX IF NOT EXISTS FOR ()-[r:HAS_SNAPSHOT]-() ON (r.day)",
]


def apply_temporal_schema(tx):
    for stmt in TEMPORAL_CONSTRAINTS + TEMPORAL_INDEXES:
        tx.run(stmt)
