"""
Unit tests for Temporal Case Memory & Evolution Reasoning.
"""

from __future__ import annotations

import pytest
from reasoning.temporal.evolution_reasoner import (
    _diff_snapshots,
    EvolutionReport,
    SymptomDelta,
)
from reasoning.temporal.case_memory import SnapshotData


class TestEvolutionDiff:
    def _make_snap(self, day, symptoms):
        return SnapshotData(
            snapshot_id=f"SNAP_{day}",
            day=day,
            symptoms=symptoms,
        )

    def test_detects_improvement(self):
        before = self._make_snap(0, [
            {"id": "S1", "name": "Headache", "category": "head", "intensity": 0.9},
            {"id": "S2", "name": "Red face", "category": "face", "intensity": 0.7},
        ])
        after = self._make_snap(7, [
            {"id": "S1", "name": "Headache", "category": "head", "intensity": 0.3},
            {"id": "S2", "name": "Red face", "category": "face", "intensity": 0.2},
        ])
        report = _diff_snapshots("C1", before, after)
        assert report.overall_trend == "improving"
        assert not report.suppression_detected

    def test_detects_suppression(self):
        before = self._make_snap(0, [
            {"id": "S1", "name": "Headache", "category": "head", "intensity": 0.9},
        ])
        after = self._make_snap(7, [
            {"id": "S1", "name": "Headache", "category": "head", "intensity": 0.2},
            {"id": "S3", "name": "Anxiety", "category": "mental", "intensity": 0.8},
        ])
        report = _diff_snapshots("C1", before, after)
        assert report.suppression_detected
        assert any("suppression" in i.lower() for i in report.insights)

    def test_detects_symptom_shift(self):
        before = self._make_snap(0, [
            {"id": "S1", "name": "Headache", "category": "head", "intensity": 0.8},
        ])
        after = self._make_snap(7, [
            {"id": "S2", "name": "Nausea", "category": "stomach", "intensity": 0.7},
        ])
        report = _diff_snapshots("C1", before, after)
        assert any("shift" in i.lower() for i in report.insights)

    def test_stable_case(self):
        before = self._make_snap(0, [
            {"id": "S1", "name": "Headache", "category": "head", "intensity": 0.5},
        ])
        after = self._make_snap(7, [
            {"id": "S1", "name": "Headache", "category": "head", "intensity": 0.5},
        ])
        report = _diff_snapshots("C1", before, after)
        assert report.overall_trend == "stable"

    def test_report_to_dict(self):
        before = self._make_snap(0, [
            {"id": "S1", "name": "Headache", "category": "head", "intensity": 0.9},
        ])
        after = self._make_snap(7, [
            {"id": "S1", "name": "Headache", "category": "head", "intensity": 0.3},
        ])
        report = _diff_snapshots("C1", before, after)
        d = report.to_dict()
        assert "case_id" in d
        assert "deltas" in d
        assert d["from_day"] == 0
        assert d["to_day"] == 7
