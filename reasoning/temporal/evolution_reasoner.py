"""
Evolution Reasoner — graph-diff between case snapshots.

Detects:
  - Symptom improvement (resolved or intensity decreased)
  - Symptom worsening (new or intensity increased)
  - Suppression pattern (physical improved but mental worsened)
  - Symptom shift (old symptoms gone, new ones appeared)

All logic is graph-based / algorithmic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.graph_client import GraphClient
from reasoning.temporal.case_memory import (
    CaseTimeline,
    SnapshotData,
    get_case_timeline,
)
import config


# ── Categories classified as "mental" vs "physical" ──────
MENTAL_CATEGORIES = {"mental"}
PHYSICAL_CATEGORIES = {"head", "eye", "face", "sensation", "stomach", "other"}


@dataclass
class SymptomDelta:
    """Change for a single symptom between two snapshots."""
    symptom_id: str
    symptom_name: str
    category: str
    old_intensity: float  # 0 if newly appeared
    new_intensity: float  # 0 if resolved
    delta: float          # new - old (negative = improvement)

    @property
    def status(self) -> str:
        if self.old_intensity == 0:
            return "NEW"
        if self.new_intensity == 0:
            return "RESOLVED"
        if self.delta < -0.2:
            return "IMPROVED"
        if self.delta > 0.2:
            return "WORSENED"
        return "STABLE"


@dataclass
class EvolutionReport:
    case_id: str
    from_day: int
    to_day: int
    deltas: list[SymptomDelta] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    suppression_detected: bool = False
    overall_trend: str = ""  # "improving", "worsening", "mixed", "stable"
    suggested_action: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "from_day": self.from_day,
            "to_day": self.to_day,
            "deltas": [
                {
                    "symptom": d.symptom_name,
                    "category": d.category,
                    "old_intensity": round(d.old_intensity, 2),
                    "new_intensity": round(d.new_intensity, 2),
                    "status": d.status,
                }
                for d in self.deltas
            ],
            "insights": self.insights,
            "suppression_detected": self.suppression_detected,
            "overall_trend": self.overall_trend,
            "suggested_action": self.suggested_action,
        }


def compute_evolution(
    graph: GraphClient,
    case_id: str,
    from_day: int | None = None,
    to_day: int | None = None,
) -> EvolutionReport | None:
    """
    Compare two snapshots of a case and compute evolution.

    If from_day / to_day not specified, uses the two most recent snapshots.
    """
    timeline = get_case_timeline(graph, case_id)
    if timeline is None or len(timeline.snapshots) < 2:
        return None

    # Select snapshots
    if from_day is not None and to_day is not None:
        snap_before = _find_snapshot(timeline, from_day)
        snap_after = _find_snapshot(timeline, to_day)
    else:
        snap_before = timeline.snapshots[-2]
        snap_after = timeline.snapshots[-1]

    if snap_before is None or snap_after is None:
        return None

    return _diff_snapshots(case_id, snap_before, snap_after)


def compute_full_trajectory(
    graph: GraphClient,
    case_id: str,
) -> list[EvolutionReport]:
    """Compute evolution between every consecutive snapshot pair."""
    timeline = get_case_timeline(graph, case_id)
    if timeline is None or len(timeline.snapshots) < 2:
        return []

    reports = []
    for i in range(len(timeline.snapshots) - 1):
        report = _diff_snapshots(
            case_id, timeline.snapshots[i], timeline.snapshots[i + 1]
        )
        reports.append(report)
    return reports


def suggest_next_remedy(
    graph: GraphClient,
    case_id: str,
) -> list[dict[str, Any]]:
    """
    Based on the evolution pattern and current symptoms,
    suggest next-step remedies via graph traversal.

    Strategy:
      - If suppression detected → look for deeper-acting remedies
        that cover the NEW mental symptoms
      - If improving → suggest waiting or same remedy
      - If worsening → re-rank on current symptom set
    """
    timeline = get_case_timeline(graph, case_id)
    if timeline is None or len(timeline.snapshots) < 2:
        return []

    evolution = _diff_snapshots(
        case_id, timeline.snapshots[-2], timeline.snapshots[-1]
    )

    current_symptoms = timeline.snapshots[-1].symptoms
    current_ids = [s["id"] for s in current_symptoms]

    if evolution.suppression_detected:
        # Focus on NEW mental symptoms
        new_mental_ids = [
            d.symptom_id for d in evolution.deltas
            if d.status == "NEW" and d.category in MENTAL_CATEGORIES
        ]
        target_ids = new_mental_ids if new_mental_ids else current_ids
    elif evolution.overall_trend == "improving":
        return [{"remedy": "Wait & Watch", "reason": "Case is improving — observe"}]
    else:
        target_ids = current_ids

    # Graph traversal for remedy ranking based on target symptoms
    from core.remedy_ranker import rank_remedies_from_ids

    ranked = rank_remedies_from_ids(graph, target_ids)
    for r in ranked:
        r["reason"] = (
            "Covers current symptom evolution"
            if not evolution.suppression_detected
            else "Covers emerging mental symptoms (anti-suppression)"
        )
    return ranked[:5]


# ── Internal helpers ─────────────────────────────────────

def _find_snapshot(
    timeline: CaseTimeline,
    day: int,
) -> SnapshotData | None:
    for s in timeline.snapshots:
        if s.day == day:
            return s
    return None


def _diff_snapshots(
    case_id: str,
    before: SnapshotData,
    after: SnapshotData,
) -> EvolutionReport:
    """Core diff logic between two snapshots."""

    before_map = {s["id"]: s for s in before.symptoms}
    after_map = {s["id"]: s for s in after.symptoms}

    all_ids = set(before_map.keys()) | set(after_map.keys())

    deltas: list[SymptomDelta] = []
    for sid in all_ids:
        b = before_map.get(sid)
        a = after_map.get(sid)
        old_int = b["intensity"] if b else 0.0
        new_int = a["intensity"] if a else 0.0
        name = (a or b)["name"]
        category = (a or b).get("category", "other")

        deltas.append(
            SymptomDelta(
                symptom_id=sid,
                symptom_name=name,
                category=category,
                old_intensity=old_int,
                new_intensity=new_int,
                delta=new_int - old_int,
            )
        )

    # ── Classify deltas ──────────────────────────────────
    mental_deltas = [d for d in deltas if d.category in MENTAL_CATEGORIES]
    physical_deltas = [d for d in deltas if d.category in PHYSICAL_CATEGORIES]

    improved = [d for d in deltas if d.status in ("IMPROVED", "RESOLVED")]
    worsened = [d for d in deltas if d.status in ("WORSENED", "NEW")]

    mental_worsened = [d for d in mental_deltas if d.status in ("WORSENED", "NEW")]
    physical_improved = [d for d in physical_deltas if d.status in ("IMPROVED", "RESOLVED")]

    # ── Suppression detection ────────────────────────────
    suppression = bool(physical_improved and mental_worsened)

    # ── Overall trend ────────────────────────────────────
    if len(improved) > len(worsened) * 2:
        trend = "improving"
    elif len(worsened) > len(improved) * 2:
        trend = "worsening"
    elif improved and worsened:
        trend = "mixed"
    else:
        trend = "stable"

    # ── Build insights ───────────────────────────────────
    insights: list[str] = []

    if improved:
        names = [d.symptom_name for d in improved]
        insights.append(f"Improved/resolved: {', '.join(names)}")

    if worsened:
        names = [d.symptom_name for d in worsened]
        insights.append(f"Worsened/new: {', '.join(names)}")

    if suppression:
        phys_names = [d.symptom_name for d in physical_improved]
        ment_names = [d.symptom_name for d in mental_worsened]
        insights.append(
            f"Physical symptoms improved ({', '.join(phys_names)}), "
            f"mental symptoms worsened ({', '.join(ment_names)}) "
            f"→ matches known suppression pattern"
        )

    # Symptom shift detection
    resolved_ids = {d.symptom_id for d in deltas if d.status == "RESOLVED"}
    new_ids = {d.symptom_id for d in deltas if d.status == "NEW"}
    if resolved_ids and new_ids:
        insights.append(
            f"Symptom shift: {len(resolved_ids)} symptoms resolved, "
            f"{len(new_ids)} new symptoms appeared"
        )

    # ── Suggested action ─────────────────────────────────
    if suppression:
        action = "Consider deeper-acting remedy targeting mental symptoms"
    elif trend == "improving":
        action = "Continue observation — wait for further improvement"
    elif trend == "worsening":
        action = "Re-evaluate remedy selection on current symptom picture"
    elif trend == "mixed":
        action = "Partial response — consider complementary remedy or potency change"
    else:
        action = "No significant change — reassess case taking"

    return EvolutionReport(
        case_id=case_id,
        from_day=before.day,
        to_day=after.day,
        deltas=deltas,
        insights=insights,
        suppression_detected=suppression,
        overall_trend=trend,
        suggested_action=action,
    )
