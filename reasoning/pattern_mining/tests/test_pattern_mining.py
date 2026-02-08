"""
Unit tests for Rare Pattern Discovery Engine.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from reasoning.pattern_mining.subgraph_miner import (
    mine_symptom_subgraphs,
    find_patterns_matching,
    SymptomPattern,
    _generate_candidates,
)
from reasoning.pattern_mining.outcome_correlator import (
    discover_rare_patterns,
    RarePatternReport,
    PatternOutcome,
)


# ── Subgraph Miner Tests ────────────────────────────────

class TestSubgraphMiner:
    def test_generate_candidates_k2(self):
        freq = {
            frozenset(["A"]): 5,
            frozenset(["B"]): 4,
            frozenset(["C"]): 3,
        }
        cands = _generate_candidates(freq, 2)
        # All pairs should be generated
        assert len(cands) == 3

    def test_generate_candidates_k3_prunes(self):
        # Only {A,B}, {A,C}, {B,C} are frequent — {A,B,C} is valid
        freq = {
            frozenset(["A", "B"]): 3,
            frozenset(["A", "C"]): 3,
            frozenset(["B", "C"]): 3,
        }
        cands = _generate_candidates(freq, 3)
        assert frozenset(["A", "B", "C"]) in cands

    def test_find_patterns_matching(self):
        p1 = SymptomPattern(
            symptom_ids=frozenset(["S1", "S2"]),
            symptom_names=["Headache", "Red face"],
            frequency=5, total_cases=20, support=0.25,
        )
        p2 = SymptomPattern(
            symptom_ids=frozenset(["S3", "S4"]),
            symptom_names=["Anxiety", "Chilly"],
            frequency=3, total_cases=20, support=0.15,
        )
        matched = find_patterns_matching([p1, p2], ["S1", "S2", "S5"])
        assert len(matched) == 1
        assert matched[0].symptom_ids == frozenset(["S1", "S2"])

    def test_mine_from_mock_graph(self):
        mock = MagicMock()

        # First call: case symptom sets
        # Second call: symptom names
        call_count = [0]

        def side_effect(cypher, **params):
            call_count[0] += 1
            if "collect" in cypher:
                return [
                    {"case_id": "C1", "symptom_ids": ["S1", "S2", "S3"]},
                    {"case_id": "C2", "symptom_ids": ["S1", "S2"]},
                    {"case_id": "C3", "symptom_ids": ["S1", "S2", "S4"]},
                    {"case_id": "C4", "symptom_ids": ["S1", "S3"]},
                ]
            else:
                return [
                    {"id": "S1", "name": "Sym1"},
                    {"id": "S2", "name": "Sym2"},
                    {"id": "S3", "name": "Sym3"},
                    {"id": "S4", "name": "Sym4"},
                ]

        mock.run_query.side_effect = side_effect

        patterns = mine_symptom_subgraphs(mock, min_frequency=2, max_pattern_size=3)
        # S1+S2 should appear in C1, C2, C3 → freq=3
        s1s2 = [p for p in patterns if p.symptom_ids == frozenset(["S1", "S2"])]
        assert len(s1s2) >= 1
        assert s1s2[0].frequency >= 3


# ── Outcome Correlator Tests ─────────────────────────────

class TestOutcomeCorrelator:
    def test_report_structure(self):
        report = RarePatternReport(discoveries=[])
        d = report.to_dict()
        assert "rare_patterns" in d
        assert isinstance(d["rare_patterns"], list)

    def test_pattern_outcome_to_dict(self):
        p = SymptomPattern(
            symptom_ids=frozenset(["S1", "S2"]),
            symptom_names=["Sun aggravation", "Emotional numbness"],
            frequency=4, total_cases=20, support=0.2,
        )
        po = PatternOutcome(
            pattern=p,
            remedy="Natrum Mur",
            success_count=3,
            total_count=4,
            success_rate=0.75,
            description="Rare pattern detected: Sun agg + Emotional numbness → Natrum Mur",
        )
        d = po.to_dict()
        assert d["remedy"] == "Natrum Mur"
        assert d["success_rate"] == 0.75
        assert d["total_count"] == 4
