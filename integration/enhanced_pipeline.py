"""
Enhanced Pipeline — layers the four advanced intelligence modules
on top of the base Graph-RAG pipeline.

Pipeline Flow:
  ┌──────────────────────────────────────────────────────────┐
  │ 1. Symptom Extraction (LLM — structuring only)           │
  │ 2. Symptom Reliability & Contradiction Detection (graph) │
  │ 3. Graph-based Remedy Ranking (graph)                    │
  │ 4. Uncertainty Estimation via Bootstrap (algorithmic)     │
  │ 5. Temporal Evolution Reasoning (graph diff)              │
  │ 6. Rare Pattern Discovery (graph mining)                  │
  │ 7. Explanation (LLM — graph-grounded only)               │
  └──────────────────────────────────────────────────────────┘

Integration rules:
  - All intelligence layers are INDEPENDENT and OPTIONAL
  - Core ranking flow is never altered by intelligence layers
  - LLMs never invent, override, or resolve — only structure & explain
"""

from __future__ import annotations

from typing import Any

from core.graph_client import GraphClient
from core.symptom_extractor import extract_and_map
from core.remedy_ranker import rank_remedies_from_ids
from core.explainer import explain_results

from reasoning.reliability.reliability_scorer import compute_reliability
from reasoning.uncertainty.confidence_estimator import estimate_confidence
from reasoning.temporal.evolution_reasoner import (
    compute_evolution,
    suggest_next_remedy,
)
from reasoning.pattern_mining.outcome_correlator import discover_for_current_case


def run_enhanced_pipeline(
    graph: GraphClient,
    complaint: str | None = None,
    symptom_ids: list[str] | None = None,
    case_id: str | None = None,
    enable_reliability: bool = True,
    enable_uncertainty: bool = True,
    enable_temporal: bool = True,
    enable_pattern_mining: bool = True,
    bootstrap_iterations: int = 200,
    explain: bool = True,
) -> dict[str, Any]:
    """
    Full enhanced pipeline.

    Args:
        graph: Neo4j graph client
        complaint: Free-text patient complaint (used if symptom_ids not given)
        symptom_ids: Pre-mapped symptom IDs (skips LLM extraction)
        case_id: If this is a follow-up, provide case_id for temporal reasoning
        enable_*: Toggle individual intelligence layers
        bootstrap_iterations: Number of perturbation iterations for uncertainty
        explain: Whether to generate LLM explanation

    Returns:
        Full result dict with all intelligence layer outputs.
    """

    result: dict[str, Any] = {}

    # ══════════════════════════════════════════════════════
    # STEP 1: Symptom Resolution
    # ══════════════════════════════════════════════════════
    if symptom_ids is None:
        if complaint is None:
            raise ValueError("Provide either complaint text or symptom_ids")
        symptom_ids = extract_and_map(graph, complaint)

    result["symptom_ids"] = symptom_ids

    # ══════════════════════════════════════════════════════
    # STEP 2: Symptom Reliability (graph-only)
    # ══════════════════════════════════════════════════════
    if enable_reliability:
        reliability_report = compute_reliability(graph, symptom_ids)
        result["reliability"] = reliability_report.to_dict()

    # ══════════════════════════════════════════════════════
    # STEP 3: Core Remedy Ranking (graph traversal)
    # ══════════════════════════════════════════════════════
    ranked = rank_remedies_from_ids(graph, symptom_ids)
    result["ranked_remedies"] = ranked

    # ══════════════════════════════════════════════════════
    # STEP 4: Uncertainty Estimation (algorithmic)
    # ══════════════════════════════════════════════════════
    if enable_uncertainty and len(symptom_ids) >= 2:
        uncertainty_report = estimate_confidence(
            graph, symptom_ids,
            n_iterations=bootstrap_iterations,
        )
        # Merge confidence data into ranked remedies
        confidence_map = {
            rc.remedy: rc for rc in uncertainty_report.remedies
        }
        enriched_remedies = []
        for r in ranked:
            entry = dict(r)
            if r["remedy"] in confidence_map:
                rc = confidence_map[r["remedy"]]
                entry["mean_score"] = rc.mean_score
                entry["confidence_interval"] = list(rc.confidence_interval)
                entry["rank_stability"] = rc.rank_stability
            enriched_remedies.append(entry)
        result["ranked_remedies"] = enriched_remedies
        result["uncertainty"] = uncertainty_report.to_dict()

    # ══════════════════════════════════════════════════════
    # STEP 5: Temporal Evolution (graph diff)
    # ══════════════════════════════════════════════════════
    if enable_temporal and case_id:
        evolution = compute_evolution(graph, case_id)
        if evolution:
            result["temporal"] = evolution.to_dict()
            next_remedies = suggest_next_remedy(graph, case_id)
            result["temporal"]["suggested_next_remedies"] = next_remedies

    # ══════════════════════════════════════════════════════
    # STEP 6: Rare Pattern Discovery (graph mining)
    # ══════════════════════════════════════════════════════
    if enable_pattern_mining:
        pattern_report = discover_for_current_case(graph, symptom_ids)
        if pattern_report.discoveries:
            result["rare_patterns"] = [
                d.to_dict() for d in pattern_report.discoveries
            ]

    # ══════════════════════════════════════════════════════
    # STEP 7: Explanation (LLM — graph-grounded)
    # ══════════════════════════════════════════════════════
    if explain:
        result["explanation"] = explain_results(result)

    return result


def format_clinical_summary(result: dict[str, Any]) -> str:
    """
    Produce a concise clinical summary from the pipeline result
    without LLM — for terminal / log display.
    """
    lines = [
        "╔══════════════════════════════════════════════════════════╗",
        "║   GRAPH-RAG CLINICAL DECISION SUPPORT — ENHANCED       ║",
        "╚══════════════════════════════════════════════════════════╝",
        "",
    ]

    # Symptoms
    lines.append(f"Symptoms analyzed: {len(result.get('symptom_ids', []))}")
    lines.append("")

    # Reliability
    if "reliability" in result:
        rel = result["reliability"]
        score = rel["reliability_score"]
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        lines.append(f"RELIABILITY: [{bar}] {score:.0%}")
        for alert in rel.get("alerts", []):
            lines.append(f"  ⚠  {alert}")
        if rel.get("suggestion"):
            lines.append(f"  →  {rel['suggestion']}")
        lines.append("")

    # Ranked remedies with confidence
    lines.append("REMEDY RANKINGS:")
    lines.append(f"  {'Remedy':<25s} {'Score':>8s} {'CI':>18s} {'Stability':>10s}")
    lines.append("  " + "─" * 65)
    for r in result.get("ranked_remedies", [])[:8]:
        ci = r.get("confidence_interval")
        ci_str = f"[{ci[0]:.3f}, {ci[1]:.3f}]" if ci else "—"
        stab = r.get("rank_stability")
        stab_str = f"{stab:.2f}" if stab is not None else "—"
        score = r.get("mean_score", r.get("score", 0))
        lines.append(f"  {r['remedy']:<25s} {score:>8.4f} {ci_str:>18s} {stab_str:>10s}")
    lines.append("")

    # Temporal
    if "temporal" in result:
        temp = result["temporal"]
        lines.append(f"TEMPORAL EVOLUTION (day {temp['from_day']} → {temp['to_day']}):")
        lines.append(f"  Trend: {temp['overall_trend']}")
        if temp.get("suppression_detected"):
            lines.append("  ⚠  SUPPRESSION PATTERN DETECTED")
        for insight in temp.get("insights", []):
            lines.append(f"  • {insight}")
        lines.append(f"  → {temp.get('suggested_action', '')}")
        lines.append("")

    # Rare patterns
    if "rare_patterns" in result:
        lines.append("RARE PATTERN DISCOVERIES:")
        for p in result["rare_patterns"]:
            lines.append(f"  ★ {p['description']}")
        lines.append("")

    # Uncertainty
    if "uncertainty" in result:
        uc = result["uncertainty"]
        lines.append(f"OVERALL CERTAINTY: {uc['overall_certainty']:.0%}")
        lines.append("")

    return "\n".join(lines)
