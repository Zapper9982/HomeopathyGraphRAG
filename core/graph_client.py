"""
Neo4j driver wrapper — single connection point for the whole system.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from neo4j import GraphDatabase

import config


class GraphClient:
    """Thin wrapper around the Neo4j Python driver."""

    def __init__(
        self,
        uri: str = config.NEO4J_URI,
        user: str = config.NEO4J_USER,
        password: str = config.NEO4J_PASSWORD,
    ):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    # ── lifecycle ────────────────────────────────────────
    def close(self):
        self._driver.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    # ── query helpers ────────────────────────────────────
    @contextmanager
    def session(self, **kwargs):
        s = self._driver.session(**kwargs)
        try:
            yield s
        finally:
            s.close()

    def run_query(self, cypher: str, **params) -> list[dict[str, Any]]:
        """Execute a read query and return list of record dicts."""
        with self.session() as s:
            result = s.run(cypher, **params)
            return [record.data() for record in result]

    def run_write(self, cypher: str, **params) -> None:
        """Execute a write query."""
        with self.session() as s:
            s.run(cypher, **params)

    # ── schema bootstrap ─────────────────────────────────
    def bootstrap_schema(self):
        """Apply all schema layers (base + extensions)."""
        from schema.base_schema import apply_base_schema
        from schema.reliability_schema import apply_reliability_schema
        from schema.temporal_schema import apply_temporal_schema
        from schema.pattern_schema import apply_pattern_schema

        with self.session() as s:
            apply_base_schema(s)
            apply_reliability_schema(s)
            apply_temporal_schema(s)
            apply_pattern_schema(s)

    def seed(self):
        """Load seed data (idempotent MERGE operations)."""
        from schema.seed_data import seed_graph

        with self.session() as s:
            seed_graph(s)

    def seed_expanded(self) -> dict:
        """Load the expanded homeopathic knowledge graph (idempotent)."""
        from schema.expanded_seed_data import seed_expanded_graph

        with self.session() as s:
            return seed_expanded_graph(s)
