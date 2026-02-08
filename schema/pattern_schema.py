"""
Schema extensions for Rare Pattern Discovery.

New nodes:
  Outcome — labels: Improved, NoChange, Worsened  (also carry :Outcome label)

New relationships:
  (Case)-[:OUTCOME]->(Outcome)
"""

PATTERN_CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (o:Outcome) REQUIRE o.type IS UNIQUE",
]

OUTCOME_TYPES = ["Improved", "NoChange", "Worsened"]

SEED_OUTCOMES_CYPHER = """
UNWIND $types AS t
MERGE (o:Outcome {type: t})
"""


def apply_pattern_schema(tx):
    for stmt in PATTERN_CONSTRAINTS:
        tx.run(stmt)
