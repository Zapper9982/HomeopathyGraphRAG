"""
Neo4j bulk loader — load normalised graph entities into Neo4j.

Uses MERGE for idempotent upserts.  Runs in batches to avoid transaction
timeouts on large datasets.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from neo4j import GraphDatabase, Session

from data_pipeline.normalizer.graph_mapper import GraphPayload

logger = logging.getLogger(__name__)


@dataclass
class LoadStats:
    """Statistics from a bulk load."""
    remedies_loaded: int = 0
    symptoms_loaded: int = 0
    rubrics_loaded: int = 0
    edges_loaded: int = 0
    errors: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def __str__(self) -> str:
        return (
            f"Loaded: {self.remedies_loaded} remedies, "
            f"{self.rubrics_loaded} rubrics, "
            f"{self.symptoms_loaded} symptoms, "
            f"{self.edges_loaded} edges"
            + (f" ({len(self.errors)} errors)" if self.errors else "")
        )


class Neo4jLoader:
    """Bulk-load GraphPayload into Neo4j."""

    BATCH_SIZE = 200

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "homeopathy_graph_2026",
    ):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def load(self, payload: GraphPayload, *, dry_run: bool = False) -> LoadStats:
        """
        Load all entities from a GraphPayload into Neo4j.

        Args:
            payload: The normalised data to load.
            dry_run: If True, print what *would* be loaded without writing.
        """
        stats = LoadStats()

        if dry_run:
            s = payload.stats()
            logger.info("[DRY RUN] Would load: %s", s)
            return stats

        with self._driver.session() as session:
            # 1. Remedies
            stats.remedies_loaded = self._load_remedies(session, payload)

            # 2. Rubrics
            stats.rubrics_loaded = self._load_rubrics(session, payload)

            # 3. Symptoms
            stats.symptoms_loaded = self._load_symptoms(session, payload)

            # 4. Edges
            stats.edges_loaded = self._load_edges(session, payload, stats)

        logger.info("Load complete: %s", stats)
        return stats

    # ── node loaders ─────────────────────────────────────

    def _load_remedies(self, session: Session, payload: GraphPayload) -> int:
        count = 0
        for batch in self._batches(payload.remedies):
            params = []
            for r in batch:
                params.append({
                    "abbrev": r.abbrev,
                    "name": r.name,
                    "common_name": r.common_name,
                    "overview": r.overview,
                    "thermal_state": r.thermal_state,
                    "thirst": r.thirst,
                    "desires": r.desires,
                    "aversions": r.aversions,
                    "dose": r.dose,
                    "source_url": r.source_url,
                })
            result = session.run(
                """
                UNWIND $batch AS r
                MERGE (rem:Remedy {abbrev: r.abbrev})
                SET rem.name         = r.name,
                    rem.common_name  = r.common_name,
                    rem.overview     = r.overview,
                    rem.thermal_state = r.thermal_state,
                    rem.thirst       = r.thirst,
                    rem.desires      = r.desires,
                    rem.aversions    = r.aversions,
                    rem.dose         = r.dose,
                    rem.source_url   = r.source_url,
                    rem.source       = 'boericke'
                RETURN count(rem) AS cnt
                """,
                batch=params,
            )
            count += result.single()["cnt"]
        return count

    def _load_rubrics(self, session: Session, payload: GraphPayload) -> int:
        count = 0
        for batch in self._batches(payload.rubrics):
            params = [
                {"id": r.id, "text": r.text, "chapter": r.chapter}
                for r in batch
            ]
            result = session.run(
                """
                UNWIND $batch AS r
                MERGE (rub:Rubric {id: r.id})
                SET rub.text    = r.text,
                    rub.chapter = r.chapter,
                    rub.source  = 'boericke'
                RETURN count(rub) AS cnt
                """,
                batch=params,
            )
            count += result.single()["cnt"]
        return count

    def _load_symptoms(self, session: Session, payload: GraphPayload) -> int:
        count = 0
        for batch in self._batches(payload.symptoms):
            params = [
                {
                    "id": s.id,
                    "text": s.text,
                    "category": s.category,
                    "source_remedy": s.source_remedy,
                }
                for s in batch
            ]
            result = session.run(
                """
                UNWIND $batch AS s
                MERGE (sym:Symptom {id: s.id})
                SET sym.text          = s.text,
                    sym.category      = s.category,
                    sym.source_remedy = s.source_remedy,
                    sym.source        = 'boericke'
                RETURN count(sym) AS cnt
                """,
                batch=params,
            )
            count += result.single()["cnt"]
        return count

    # ── edge loaders ─────────────────────────────────────

    def _load_edges(
        self, session: Session, payload: GraphPayload, stats: LoadStats
    ) -> int:
        count = 0
        # Group edges by type for different Cypher queries
        by_type: dict[str, list] = {}
        for e in payload.edges:
            by_type.setdefault(e.edge_type, []).append(e)

        for edge_type, edges in by_type.items():
            for batch in self._batches(edges):
                try:
                    n = self._load_edge_batch(session, edge_type, batch)
                    count += n
                except Exception as exc:
                    msg = f"Error loading {edge_type} edges: {exc}"
                    logger.warning(msg)
                    stats.errors.append(msg)

        return count

    def _load_edge_batch(
        self, session: Session, edge_type: str, edges: list
    ) -> int:
        """Load a batch of edges of the same type."""

        if edge_type == "BELONGS_TO":
            return self._load_belongs_to(session, edges)
        elif edge_type == "INDICATES":
            return self._load_indicates(session, edges)
        else:
            # Remedy-to-Remedy relationships
            return self._load_remedy_relationship(session, edge_type, edges)

    def _load_belongs_to(self, session: Session, edges: list) -> int:
        params = [
            {"source_id": e.source_id, "target_id": e.target_id}
            for e in edges
        ]
        result = session.run(
            """
            UNWIND $batch AS e
            MATCH (sym:Symptom {id: e.source_id})
            MATCH (rub:Rubric {id: e.target_id})
            MERGE (sym)-[:BELONGS_TO]->(rub)
            RETURN count(*) AS cnt
            """,
            batch=params,
        )
        return result.single()["cnt"]

    def _load_indicates(self, session: Session, edges: list) -> int:
        """Load INDICATES edges as (Rubric)-[:INDICATES]->(Remedy).

        Note: In the mapper, source_id = remedy_abbrev, target_id = rubric_id.
        We swap them here because the graph convention (matching the ranker
        query and Kent's Repertory) is  Rubric → Remedy.
        """
        params = [
            {
                "remedy_abbrev": e.source_id,
                "rubric_id": e.target_id,
                "grade": e.properties.get("grade", 2),
                "source": e.properties.get("source", "boericke"),
            }
            for e in edges
        ]
        result = session.run(
            """
            UNWIND $batch AS e
            MATCH (rub:Rubric {id: e.rubric_id})
            MATCH (rem:Remedy {abbrev: e.remedy_abbrev})
            MERGE (rub)-[ind:INDICATES]->(rem)
            SET ind.grade  = e.grade,
                ind.source = e.source
            RETURN count(*) AS cnt
            """,
            batch=params,
        )
        return result.single()["cnt"]

    def _load_remedy_relationship(
        self, session: Session, edge_type: str, edges: list
    ) -> int:
        """Load remedy-to-remedy relationships dynamically."""
        # Use APOC to create dynamic relationship types if available,
        # otherwise fall back to parameterized TYPE()
        params = [
            {
                "source_id": e.source_id,
                "target_id": e.target_id,
                "context": e.properties.get("context", ""),
                "source": e.properties.get("source", "boericke"),
            }
            for e in edges
        ]

        # For safety, validate edge_type is alphanumeric
        safe_type = "".join(c for c in edge_type if c.isalnum() or c == "_")

        query = f"""
            UNWIND $batch AS e
            MATCH (a:Remedy {{abbrev: e.source_id}})
            MATCH (b:Remedy) WHERE b.abbrev = e.target_id OR b.name = e.target_id
            MERGE (a)-[r:{safe_type}]->(b)
            SET r.context = e.context,
                r.source  = e.source
            RETURN count(*) AS cnt
        """
        result = session.run(query, batch=params)
        return result.single()["cnt"]

    # ── utilities ────────────────────────────────────────

    def _batches(self, items: list, size: int = None):
        """Yield successive batches from a list."""
        size = size or self.BATCH_SIZE
        for i in range(0, len(items), size):
            yield items[i : i + size]

    def ensure_constraints(self, session: Optional[Session] = None):
        """Create indexes/constraints if they don't exist."""
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Remedy) REQUIRE r.abbrev IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (r:Rubric) ON (r.id)",
            "CREATE INDEX IF NOT EXISTS FOR (s:Symptom) ON (s.id)",
            "CREATE INDEX IF NOT EXISTS FOR (s:Symptom) ON (s.category)",
            "CREATE INDEX IF NOT EXISTS FOR (r:Rubric) ON (r.chapter)",
        ]
        close = False
        if session is None:
            session = self._driver.session()
            close = True
        try:
            for q in queries:
                session.run(q)
        finally:
            if close:
                session.close()
