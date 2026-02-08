"""
Seed data — a realistic homeopathic knowledge graph fragment
for development and testing.
"""

SYMPTOMS = [
    {"id": "SYM001", "name": "Throbbing headache", "category": "head"},
    {"id": "SYM002", "name": "Worse by heat", "category": "modality"},
    {"id": "SYM003", "name": "Desire for warmth", "category": "modality"},
    {"id": "SYM004", "name": "Dilated pupils", "category": "eye"},
    {"id": "SYM005", "name": "Red flushed face", "category": "face"},
    {"id": "SYM006", "name": "Sudden onset", "category": "onset"},
    {"id": "SYM007", "name": "Restlessness", "category": "mental"},
    {"id": "SYM008", "name": "Anxiety about health", "category": "mental"},
    {"id": "SYM009", "name": "Chilly patient", "category": "thermal"},
    {"id": "SYM010", "name": "Hot patient", "category": "thermal"},
    {"id": "SYM011", "name": "Worse at night", "category": "modality"},
    {"id": "SYM012", "name": "Better by pressure", "category": "modality"},
    {"id": "SYM013", "name": "Burning pains", "category": "sensation"},
    {"id": "SYM014", "name": "Better by cold application", "category": "modality"},
    {"id": "SYM015", "name": "Worse by cold", "category": "modality"},
    {"id": "SYM016", "name": "Emotional numbness", "category": "mental"},
    {"id": "SYM017", "name": "Sun aggravation", "category": "modality"},
    {"id": "SYM018", "name": "Grief suppressed", "category": "mental"},
    {"id": "SYM019", "name": "Weeping ameliorates", "category": "modality"},
    {"id": "SYM020", "name": "Thirstlessness", "category": "stomach"},
]

RUBRICS = [
    {"id": "RUB001", "chapter": "Head", "text": "Head; pain; throbbing"},
    {"id": "RUB002", "chapter": "Generalities", "text": "Generalities; heat; agg"},
    {"id": "RUB003", "chapter": "Generalities", "text": "Generalities; warmth; desire"},
    {"id": "RUB004", "chapter": "Eye", "text": "Eye; pupils; dilated"},
    {"id": "RUB005", "chapter": "Face", "text": "Face; red"},
    {"id": "RUB006", "chapter": "Generalities", "text": "Generalities; sudden onset"},
    {"id": "RUB007", "chapter": "Mind", "text": "Mind; restlessness"},
    {"id": "RUB008", "chapter": "Mind", "text": "Mind; anxiety; health about"},
    {"id": "RUB009", "chapter": "Generalities", "text": "Generalities; cold; agg"},
    {"id": "RUB010", "chapter": "Generalities", "text": "Generalities; night; agg"},
    {"id": "RUB011", "chapter": "Mind", "text": "Mind; emotional numbness"},
    {"id": "RUB012", "chapter": "Generalities", "text": "Generalities; sun; agg"},
]

REMEDIES = [
    {"name": "Belladonna", "abbrev": "Bell"},
    {"name": "Aconitum Napellus", "abbrev": "Acon"},
    {"name": "Arsenicum Album", "abbrev": "Ars"},
    {"name": "Natrum Muriaticum", "abbrev": "Nat-m"},
    {"name": "Bryonia Alba", "abbrev": "Bry"},
    {"name": "Pulsatilla", "abbrev": "Puls"},
    {"name": "Nux Vomica", "abbrev": "Nux-v"},
    {"name": "Sulphur", "abbrev": "Sulph"},
    {"name": "Lycopodium", "abbrev": "Lyc"},
    {"name": "Phosphorus", "abbrev": "Phos"},
]

# Symptom → Rubric mappings
SYMPTOM_RUBRIC_LINKS = [
    ("SYM001", "RUB001"),
    ("SYM002", "RUB002"),
    ("SYM003", "RUB003"),
    ("SYM004", "RUB004"),
    ("SYM005", "RUB005"),
    ("SYM006", "RUB006"),
    ("SYM007", "RUB007"),
    ("SYM008", "RUB008"),
    ("SYM009", "RUB009"),
    ("SYM010", "RUB002"),
    ("SYM011", "RUB010"),
    ("SYM016", "RUB011"),
    ("SYM017", "RUB012"),
]

# Rubric → Remedy indications (rubric_id, remedy_name, grade 1-3)
RUBRIC_REMEDY_INDICATIONS = [
    ("RUB001", "Belladonna", 3), ("RUB001", "Bryonia Alba", 2),
    ("RUB002", "Belladonna", 3), ("RUB002", "Pulsatilla", 2), ("RUB002", "Sulphur", 2),
    ("RUB003", "Arsenicum Album", 3), ("RUB003", "Nux Vomica", 2),
    ("RUB004", "Belladonna", 3), ("RUB004", "Aconitum Napellus", 1),
    ("RUB005", "Belladonna", 3), ("RUB005", "Aconitum Napellus", 2),
    ("RUB006", "Aconitum Napellus", 3), ("RUB006", "Belladonna", 2),
    ("RUB007", "Arsenicum Album", 3), ("RUB007", "Aconitum Napellus", 2),
    ("RUB008", "Arsenicum Album", 3), ("RUB008", "Phosphorus", 2),
    ("RUB009", "Arsenicum Album", 3), ("RUB009", "Nux Vomica", 3),
    ("RUB010", "Arsenicum Album", 2), ("RUB010", "Aconitum Napellus", 2),
    ("RUB011", "Natrum Muriaticum", 3), ("RUB011", "Phosphorus", 1),
    ("RUB012", "Natrum Muriaticum", 3), ("RUB012", "Belladonna", 1),
]

# Contradiction pairs
CONTRADICTION_PAIRS = [
    {"a": "SYM002", "b": "SYM003", "strength": 0.9, "source": "clinical"},   # heat agg vs desire warmth
    {"a": "SYM009", "b": "SYM010", "strength": 1.0, "source": "clinical"},   # chilly vs hot
    {"a": "SYM002", "b": "SYM015", "strength": 0.85, "source": "literature"}, # heat agg vs cold agg
    {"a": "SYM014", "b": "SYM015", "strength": 0.8, "source": "clinical"},   # better cold vs worse cold
]

# Correlation pairs
CORRELATION_PAIRS = [
    {"a": "SYM001", "b": "SYM005", "strength": 0.75, "source": "clinical"},   # throbbing HA + red face
    {"a": "SYM001", "b": "SYM004", "strength": 0.65, "source": "clinical"},   # throbbing HA + dilated pupils
    {"a": "SYM007", "b": "SYM008", "strength": 0.7, "source": "literature"},  # restlessness + anxiety
    {"a": "SYM016", "b": "SYM018", "strength": 0.8, "source": "clinical"},    # emotional numbness + grief
    {"a": "SYM017", "b": "SYM016", "strength": 0.6, "source": "literature"},  # sun agg + emotional numbness
]

# Sample cases for temporal + pattern mining seeding
SAMPLE_CASES = [
    {
        "case_id": "CASE001",
        "patient_id": "PAT001",
        "snapshots": [
            {
                "snapshot_id": "SNAP001A",
                "day": 0,
                "symptoms": [("SYM001", 0.8), ("SYM005", 0.7), ("SYM006", 0.9)],
                "prescribed": ("Belladonna", "200C"),
            },
            {
                "snapshot_id": "SNAP001B",
                "day": 7,
                "symptoms": [("SYM001", 0.3), ("SYM005", 0.2), ("SYM007", 0.6)],
                "prescribed": None,
            },
        ],
        "outcome": "Improved",
    },
    {
        "case_id": "CASE002",
        "patient_id": "PAT002",
        "snapshots": [
            {
                "snapshot_id": "SNAP002A",
                "day": 0,
                "symptoms": [("SYM007", 0.9), ("SYM008", 0.8), ("SYM009", 0.7), ("SYM011", 0.6)],
                "prescribed": ("Arsenicum Album", "30C"),
            },
            {
                "snapshot_id": "SNAP002B",
                "day": 14,
                "symptoms": [("SYM007", 0.4), ("SYM008", 0.3), ("SYM009", 0.5)],
                "prescribed": None,
            },
        ],
        "outcome": "Improved",
    },
    {
        "case_id": "CASE003",
        "patient_id": "PAT003",
        "snapshots": [
            {
                "snapshot_id": "SNAP003A",
                "day": 0,
                "symptoms": [("SYM016", 0.9), ("SYM017", 0.7), ("SYM018", 0.8)],
                "prescribed": ("Natrum Muriaticum", "1M"),
            },
        ],
        "outcome": "Improved",
    },
    {
        "case_id": "CASE004",
        "patient_id": "PAT004",
        "snapshots": [
            {
                "snapshot_id": "SNAP004A",
                "day": 0,
                "symptoms": [("SYM016", 0.8), ("SYM017", 0.6)],
                "prescribed": ("Natrum Muriaticum", "200C"),
            },
        ],
        "outcome": "Improved",
    },
    {
        "case_id": "CASE005",
        "patient_id": "PAT005",
        "snapshots": [
            {
                "snapshot_id": "SNAP005A",
                "day": 0,
                "symptoms": [("SYM001", 0.9), ("SYM002", 0.8), ("SYM004", 0.7), ("SYM005", 0.9)],
                "prescribed": ("Belladonna", "30C"),
            },
            {
                "snapshot_id": "SNAP005B",
                "day": 3,
                "symptoms": [("SYM001", 0.2), ("SYM002", 0.1)],
                "prescribed": None,
            },
        ],
        "outcome": "Improved",
    },
]


def seed_graph(session):
    """Populate Neo4j with the complete seed dataset."""

    # ── Nodes ────────────────────────────────────────────
    session.run(
        "UNWIND $items AS s MERGE (n:Symptom {id: s.id}) SET n.name = s.name, n.category = s.category",
        items=SYMPTOMS,
    )
    session.run(
        "UNWIND $items AS r MERGE (n:Rubric {id: r.id}) SET n.chapter = r.chapter, n.text = r.text",
        items=RUBRICS,
    )
    session.run(
        "UNWIND $items AS r MERGE (n:Remedy {name: r.name}) SET n.abbrev = r.abbrev",
        items=REMEDIES,
    )

    # ── Symptom → Rubric ─────────────────────────────────
    session.run(
        """UNWIND $links AS l
           MATCH (s:Symptom {id: l[0]}), (r:Rubric {id: l[1]})
           MERGE (s)-[:BELONGS_TO]->(r)""",
        links=SYMPTOM_RUBRIC_LINKS,
    )

    # ── Rubric → Remedy ──────────────────────────────────
    session.run(
        """UNWIND $indications AS i
           MATCH (r:Rubric {id: i[0]}), (rem:Remedy {name: i[1]})
           MERGE (r)-[rel:INDICATES]->(rem)
           SET rel.grade = i[2]""",
        indications=RUBRIC_REMEDY_INDICATIONS,
    )

    # ── Contradictions ───────────────────────────────────
    session.run(
        """UNWIND $pairs AS pair
           MATCH (a:Symptom {id: pair.a}), (b:Symptom {id: pair.b})
           MERGE (a)-[r:CONTRADICTS]->(b)
           SET r.strength = pair.strength, r.source = pair.source""",
        pairs=CONTRADICTION_PAIRS,
    )

    # ── Correlations ─────────────────────────────────────
    session.run(
        """UNWIND $pairs AS pair
           MATCH (a:Symptom {id: pair.a}), (b:Symptom {id: pair.b})
           MERGE (a)-[r:CORRELATED_WITH]->(b)
           SET r.strength = pair.strength, r.source = pair.source""",
        pairs=CORRELATION_PAIRS,
    )

    # ── Outcomes ─────────────────────────────────────────
    session.run(
        "UNWIND $types AS t MERGE (o:Outcome {type: t})",
        types=["Improved", "NoChange", "Worsened"],
    )

    # ── Cases + Snapshots ────────────────────────────────
    for case in SAMPLE_CASES:
        session.run(
            "MERGE (c:Case {id: $cid}) SET c.patient_id = $pid",
            cid=case["case_id"],
            pid=case["patient_id"],
        )
        # Link outcome
        session.run(
            """MATCH (c:Case {id: $cid}), (o:Outcome {type: $outcome})
               MERGE (c)-[:OUTCOME]->(o)""",
            cid=case["case_id"],
            outcome=case["outcome"],
        )
        for snap in case["snapshots"]:
            session.run(
                """MATCH (c:Case {id: $cid})
                   MERGE (cs:CaseSnapshot {id: $sid})
                   MERGE (c)-[:HAS_SNAPSHOT {day: $day}]->(cs)""",
                cid=case["case_id"],
                sid=snap["snapshot_id"],
                day=snap["day"],
            )
            for sym_id, intensity in snap["symptoms"]:
                session.run(
                    """MATCH (cs:CaseSnapshot {id: $sid}), (s:Symptom {id: $sym_id})
                       MERGE (cs)-[:OBSERVED_SYMPTOM {intensity: $intensity}]->(s)""",
                    sid=snap["snapshot_id"],
                    sym_id=sym_id,
                    intensity=intensity,
                )
            if snap["prescribed"]:
                remedy_name, potency = snap["prescribed"]
                session.run(
                    """MATCH (cs:CaseSnapshot {id: $sid}), (rem:Remedy {name: $remedy})
                       MERGE (cs)-[:PRESCRIBED {potency: $potency}]->(rem)""",
                    sid=snap["snapshot_id"],
                    remedy=remedy_name,
                    potency=potency,
                )
