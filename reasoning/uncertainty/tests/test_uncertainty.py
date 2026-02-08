"""
Unit tests for Remedy Confidence & Uncertainty Estimation.

Uses a mock GraphClient to test the bootstrap logic
without a live Neo4j instance.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from reasoning.uncertainty.bootstrap_ranker import (
    bootstrap_rank_optimized,
)
from reasoning.uncertainty.confidence_estimator import (
    estimate_confidence,
    UncertaintyReport,
    RemedyConfidence,
)


# ── Fixtures ─────────────────────────────────────────────

MOCK_INDICATIONS = [
    {"symptom_id": "S1", "remedy": "Belladonna", "grade": 3},
    {"symptom_id": "S1", "remedy": "Bryonia", "grade": 2},
    {"symptom_id": "S2", "remedy": "Belladonna", "grade": 3},
    {"symptom_id": "S2", "remedy": "Pulsatilla", "grade": 2},
    {"symptom_id": "S3", "remedy": "Belladonna", "grade": 2},
    {"symptom_id": "S3", "remedy": "Arsenicum", "grade": 3},
    {"symptom_id": "S4", "remedy": "Arsenicum", "grade": 3},
    {"symptom_id": "S4", "remedy": "Nux Vomica", "grade": 2},
]


def _make_graph_mock() -> MagicMock:
    mock = MagicMock()
    mock.run_query.return_value = MOCK_INDICATIONS
    return mock


# ── Bootstrap Ranker Tests ───────────────────────────────

class TestBootstrapRanker:
    def test_returns_scores_for_all_remedies(self):
        graph = _make_graph_mock()
        scores = bootstrap_rank_optimized(
            graph, ["S1", "S2", "S3", "S4"],
            n_iterations=50, seed=42,
        )
        assert "Belladonna" in scores
        assert "Arsenicum" in scores
        assert len(scores["Belladonna"]) == 50

    def test_empty_symptoms_returns_empty(self):
        graph = _make_graph_mock()
        scores = bootstrap_rank_optimized(graph, [], n_iterations=10)
        assert scores == {}

    def test_single_symptom_no_drop(self):
        graph = _make_graph_mock()
        scores = bootstrap_rank_optimized(
            graph, ["S1"], n_iterations=10, seed=42,
        )
        # With a single symptom, no perturbation — all scores identical
        assert len(set(scores["Belladonna"])) == 1

    def test_deterministic_with_seed(self):
        graph = _make_graph_mock()
        s1 = bootstrap_rank_optimized(
            graph, ["S1", "S2", "S3"], n_iterations=20, seed=123,
        )
        s2 = bootstrap_rank_optimized(
            graph, ["S1", "S2", "S3"], n_iterations=20, seed=123,
        )
        assert s1 == s2


# ── Confidence Estimator Tests ───────────────────────────

class TestConfidenceEstimator:
    def test_returns_uncertainty_report(self):
        graph = _make_graph_mock()
        report = estimate_confidence(
            graph, ["S1", "S2", "S3", "S4"],
            n_iterations=100, seed=42,
        )
        assert isinstance(report, UncertaintyReport)
        assert len(report.remedies) > 0
        assert 0 <= report.overall_certainty <= 1

    def test_confidence_intervals_valid(self):
        graph = _make_graph_mock()
        report = estimate_confidence(
            graph, ["S1", "S2", "S3"],
            n_iterations=100, seed=42,
        )
        for rc in report.remedies:
            lo, hi = rc.confidence_interval
            assert lo <= rc.mean_score <= hi or abs(lo - hi) < 0.01
            assert 0 <= lo
            assert hi <= 1.0 + 0.01  # small float tolerance

    def test_report_to_dict(self):
        graph = _make_graph_mock()
        report = estimate_confidence(
            graph, ["S1", "S2"], n_iterations=50, seed=42,
        )
        d = report.to_dict()
        assert "overall_certainty" in d
        assert "remedies" in d
        assert isinstance(d["remedies"], list)
        if d["remedies"]:
            r = d["remedies"][0]
            assert "remedy" in r
            assert "mean_score" in r
            assert "confidence_interval" in r
            assert len(r["confidence_interval"]) == 2

    def test_empty_symptoms(self):
        graph = _make_graph_mock()
        report = estimate_confidence(graph, [])
        assert report.remedies == []
        assert report.overall_certainty == 0.0
