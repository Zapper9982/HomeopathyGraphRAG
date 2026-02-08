"""
Unit tests for the Symptom Reliability & Contradiction Engine.

Uses a mock GraphClient that returns pre-defined query results
so tests run without a Neo4j instance.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from reasoning.reliability.contradiction_detector import (
    detect_contradictions,
    find_correlated_missing,
    Contradiction,
)
from reasoning.reliability.reliability_scorer import (
    compute_reliability,
    ReliabilityReport,
)


# ── Fixtures ─────────────────────────────────────────────

def _make_graph_mock(query_responses: dict[str, list[dict]]) -> MagicMock:
    """
    Build a mock GraphClient whose run_query returns
    results keyed by a substring match on the Cypher query.
    """
    mock = MagicMock()

    def side_effect(cypher, **params):
        for key, response in query_responses.items():
            if key in cypher:
                return response
        return []

    mock.run_query.side_effect = side_effect
    return mock


# ── Contradiction Detector Tests ─────────────────────────

class TestContradictionDetector:
    def test_detects_contradictions(self):
        graph = _make_graph_mock({
            "CONTRADICTS": [
                {
                    "a_id": "SYM002", "a_name": "Worse by heat",
                    "b_id": "SYM003", "b_name": "Desire for warmth",
                    "strength": 0.9, "source": "clinical",
                }
            ]
        })

        result = detect_contradictions(graph, ["SYM002", "SYM003"])
        assert len(result) == 1
        assert isinstance(result[0], Contradiction)
        assert result[0].strength == 0.9
        assert "heat" in result[0].alert_text.lower()

    def test_no_contradictions_with_single_symptom(self):
        graph = _make_graph_mock({"CONTRADICTS": []})
        result = detect_contradictions(graph, ["SYM001"])
        assert result == []

    def test_no_contradictions_with_empty_list(self):
        graph = _make_graph_mock({"CONTRADICTS": []})
        result = detect_contradictions(graph, [])
        assert result == []

    def test_finds_correlated_missing(self):
        graph = _make_graph_mock({
            "CORRELATED_WITH": [
                {
                    "missing_id": "SYM004", "missing_name": "Dilated pupils",
                    "anchor_id": "SYM001", "anchor_name": "Throbbing headache",
                    "correlation_strength": 0.65,
                }
            ]
        })

        result = find_correlated_missing(graph, ["SYM001"])
        assert len(result) == 1
        assert result[0]["missing_name"] == "Dilated pupils"


# ── Reliability Scorer Tests ─────────────────────────────

class TestReliabilityScorer:
    def test_perfect_reliability_no_contradictions(self):
        graph = _make_graph_mock({
            "CONTRADICTS": [],
            "CORRELATED_WITH": [{"corr_count": 2}],
        })

        report = compute_reliability(graph, ["SYM001", "SYM005"])
        assert isinstance(report, ReliabilityReport)
        assert report.reliability_score > 0.9
        assert len(report.alerts) == 0

    def test_penalized_by_contradictions(self):
        graph = _make_graph_mock({
            "CONTRADICTS": [
                {
                    "a_id": "SYM002", "a_name": "Worse by heat",
                    "b_id": "SYM003", "b_name": "Desire for warmth",
                    "strength": 0.9, "source": "clinical",
                }
            ],
            "CORRELATED_WITH": [{"corr_count": 0}],
            "category": [{"cat": "modality"}],
        })

        report = compute_reliability(graph, ["SYM002", "SYM003"])
        assert report.reliability_score < 1.0
        assert len(report.alerts) >= 1
        assert report.suggestion != ""

    def test_empty_symptoms_returns_zero(self):
        graph = _make_graph_mock({})
        report = compute_reliability(graph, [])
        assert report.reliability_score == 0.0

    def test_report_to_dict(self):
        report = ReliabilityReport(
            reliability_score=0.62,
            alerts=["Test alert"],
            suggestion="Test suggestion",
        )
        d = report.to_dict()
        assert d["reliability_score"] == 0.62
        assert "Test alert" in d["alerts"]
