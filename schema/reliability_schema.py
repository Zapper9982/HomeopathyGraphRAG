"""
Schema extensions for Symptom Reliability & Contradiction Detection.

New relationships:
  (Symptom)-[:CORRELATED_WITH {strength, source}]->(Symptom)
  (Symptom)-[:CONTRADICTS     {strength, source}]->(Symptom)
"""

RELIABILITY_INDEXES = [
    "CREATE INDEX IF NOT EXISTS FOR ()-[r:CONTRADICTS]-() ON (r.strength)",
    "CREATE INDEX IF NOT EXISTS FOR ()-[r:CORRELATED_WITH]-() ON (r.strength)",
]

SEED_CONTRADICTIONS_CYPHER = """
// Example clinical contradictions seeded from materia medica
UNWIND $pairs AS pair
MATCH (a:Symptom {id: pair.a})
MATCH (b:Symptom {id: pair.b})
MERGE (a)-[r:CONTRADICTS]->(b)
SET r.strength = pair.strength, r.source = pair.source
"""

SEED_CORRELATIONS_CYPHER = """
UNWIND $pairs AS pair
MATCH (a:Symptom {id: pair.a})
MATCH (b:Symptom {id: pair.b})
MERGE (a)-[r:CORRELATED_WITH]->(b)
SET r.strength = pair.strength, r.source = pair.source
"""


def apply_reliability_schema(tx):
    for stmt in RELIABILITY_INDEXES:
        tx.run(stmt)
