"""
Integration test — runs the full enhanced pipeline
against a mock graph to verify end-to-end wiring.

Does NOT require a live Neo4j instance.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from integration.enhanced_pipeline import (
    run_enhanced_pipeline,
    format_clinical_summary,
)


# ── Mock Fixtures ────────────────────────────────────────

def _build_mock_graph():
    """
    Build a mock GraphClient that returns realistic data
    for the full pipeline test.
    """
    mock = MagicMock()

    # Map Cypher patterns to responses
    responses = {
        # Remedy ranking: Symptom → Rubric → Remedy
        "INDICATES": [
            {"remedy": "Belladonna", "grade": 3, "rubric": "Head; throbbing", "symptom_id": "SYM001"},
            {"remedy": "Belladonna", "grade": 3, "rubric": "Face; red", "symptom_id": "SYM005"},
            {"remedy": "Aconitum", "grade": 2, "rubric": "Face; red", "symptom_id": "SYM005"},
            {"remedy": "Belladonna", "grade": 2, "rubric": "Sudden onset", "symptom_id": "SYM006"},
            {"remedy": "Aconitum", "grade": 3, "rubric": "Sudden onset", "symptom_id": "SYM006"},
        ],
        # Contradiction check
        "CONTRADICTS": [],
        # Correlation check
        "CORRELATED_WITH": [{"corr_count": 1}],
        # Bootstrap: pre-fetch indication map
        "BELONGS_TO": [
            {"symptom_id": "SYM001", "remedy": "Belladonna", "grade": 3},
            {"symptom_id": "SYM005", "remedy": "Belladonna", "grade": 3},
            {"symptom_id": "SYM005", "remedy": "Aconitum", "grade": 2},
            {"symptom_id": "SYM006", "remedy": "Belladonna", "grade": 2},
            {"symptom_id": "SYM006", "remedy": "Aconitum", "grade": 3},
        ],
        # Case symptom sets for pattern mining
        "collect": [
            {"case_id": "C1", "symptom_ids": ["SYM001", "SYM005", "SYM006"]},
            {"case_id": "C2", "symptom_ids": ["SYM001", "SYM005"]},
            {"case_id": "C3", "symptom_ids": ["SYM001", "SYM005", "SYM007"]},
        ],
        # Symptom names
        "s.name": [
            {"id": "SYM001", "name": "Throbbing headache"},
            {"id": "SYM005", "name": "Red flushed face"},
            {"id": "SYM006", "name": "Sudden onset"},
            {"id": "SYM007", "name": "Restlessness"},
        ],
        # Pattern outcome correlation
        "OUTCOME": [
            {"case_id": "C1", "remedy": "Belladonna", "outcome": "Improved"},
            {"case_id": "C2", "remedy": "Belladonna", "outcome": "Improved"},
        ],
    }

    def side_effect(cypher, **params):
        # Check more specific patterns first to avoid ambiguous matches
        # (e.g., outcome query also contains "collect")
        if "OUTCOME" in cypher and "PRESCRIBED" in cypher:
            return responses["OUTCOME"]
        for key, response in responses.items():
            if key in cypher:
                return response
        return []

    mock.run_query.side_effect = side_effect
    return mock


# ── Tests ────────────────────────────────────────────────

class TestEnhancedPipeline:
    def test_full_pipeline_no_llm(self):
        """Run full pipeline with pre-mapped symptom IDs and no LLM."""
        graph = _build_mock_graph()
        result = run_enhanced_pipeline(
            graph,
            symptom_ids=["SYM001", "SYM005", "SYM006"],
            enable_reliability=True,
            enable_uncertainty=True,
            enable_temporal=False,  # no case_id → skip temporal
            enable_pattern_mining=True,
            bootstrap_iterations=50,
            explain=False,  # skip LLM
        )

        # Core results present
        assert "symptom_ids" in result
        assert "ranked_remedies" in result
        assert len(result["ranked_remedies"]) > 0

        # Reliability present
        assert "reliability" in result
        assert "reliability_score" in result["reliability"]

        # Uncertainty present
        assert "uncertainty" in result

        # Top remedy should have confidence interval
        top = result["ranked_remedies"][0]
        assert "confidence_interval" in top
        assert len(top["confidence_interval"]) == 2

    def test_format_summary(self):
        """Test that format_clinical_summary produces readable output."""
        graph = _build_mock_graph()
        result = run_enhanced_pipeline(
            graph,
            symptom_ids=["SYM001", "SYM005", "SYM006"],
            bootstrap_iterations=30,
            explain=False,
        )
        summary = format_clinical_summary(result)
        assert "RELIABILITY" in summary
        assert "REMEDY RANKINGS" in summary
        assert "CERTAINTY" in summary

    def test_pipeline_with_single_symptom(self):
        """Single symptom should still work (uncertainty skipped)."""
        graph = _build_mock_graph()
        result = run_enhanced_pipeline(
            graph,
            symptom_ids=["SYM001"],
            bootstrap_iterations=20,
            explain=False,
        )
        assert "ranked_remedies" in result
        # Uncertainty skipped for fewer than 2 symptoms
        assert "uncertainty" not in result

    def test_pipeline_raises_without_input(self):
        graph = _build_mock_graph()
        with pytest.raises(ValueError):
            run_enhanced_pipeline(graph)
