"""
Base graph schema — Symptom, Rubric, Remedy, and core relationships.
Executed via Neo4j to create constraints and indexes.
"""

BASE_CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Symptom) REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Rubric) REQUIRE r.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (rem:Remedy) REQUIRE rem.abbrev IS UNIQUE",
]

BASE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS FOR (s:Symptom) ON (s.name)",
    "CREATE INDEX IF NOT EXISTS FOR (s:Symptom) ON (s.category)",
    "CREATE INDEX IF NOT EXISTS FOR (r:Rubric) ON (r.chapter)",
    "CREATE INDEX IF NOT EXISTS FOR (rem:Remedy) ON (rem.name)",
]

# Core node labels and relationship types used by the base pipeline.
# (Symptom)-[:BELONGS_TO]->(Rubric)
# (Rubric)-[:INDICATES {grade: int 1-3}]->(Remedy)
# (Symptom)-[:MAPPED_TO]->(Rubric)     — LLM extraction links raw symptom to canonical rubric

NODE_LABELS = ["Symptom", "Rubric", "Remedy"]

RELATIONSHIP_TYPES = [
    "BELONGS_TO",   # Symptom → Rubric
    "INDICATES",    # Rubric  → Remedy  (grade 1-3)
    "MAPPED_TO",    # Symptom → Rubric  (runtime)
]


def apply_base_schema(tx):
    """Run inside a Neo4j session to apply base constraints + indexes."""
    for stmt in BASE_CONSTRAINTS + BASE_INDEXES:
        tx.run(stmt)
