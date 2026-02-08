"""
LLM Explainer — takes graph-derived results and produces
natural-language explanations grounded in graph evidence.

LLM NEVER invents remedies or overrides graph conclusions.
"""

from __future__ import annotations

import json
from typing import Any

from google import genai

import config


EXPLAIN_SYSTEM_PROMPT = """\
You are a clinical explanation assistant for a homeopathic decision-support system.
You receive graph-derived remedy rankings, reliability warnings, temporal insights,
confidence intervals, and rare pattern findings.

Your job is ONLY to produce a clear, structured explanation of these results
for the practitioner.

RULES:
- Do NOT invent new remedies.
- Do NOT override the ranking or scores.
- Do NOT resolve contradictions — only report them.
- Ground every statement in the provided data.
"""


def explain_results(results: dict[str, Any]) -> str:
    """
    Produce a natural-language explanation from graph-derived results.
    Falls back to a formatted summary if LLM is unavailable.
    """
    if not config.GEMINI_API_KEY:
        return _fallback_explanation(results)

    client = genai.Client(api_key=config.GEMINI_API_KEY)
    resp = client.models.generate_content(
        model=config.LLM_MODEL,
        contents=(
            f"{EXPLAIN_SYSTEM_PROMPT}\n\n"
            "Explain the following graph-derived clinical findings:\n\n"
            + json.dumps(results, indent=2, default=str)
        ),
        config=genai.types.GenerateContentConfig(
            temperature=0.3,
        ),
    )
    return resp.text


def _fallback_explanation(results: dict[str, Any]) -> str:
    """Structured text explanation without LLM."""
    lines: list[str] = ["═══ Graph-RAG Clinical Decision Report ═══\n"]

    # Remedies
    if "ranked_remedies" in results:
        lines.append("▸ REMEDY RANKING")
        for r in results["ranked_remedies"][:5]:
            ci = r.get("confidence_interval")
            ci_str = f"  CI {ci}" if ci else ""
            lines.append(f"  {r['remedy']:30s}  score={r.get('mean_score', r.get('score', '?'))}{ci_str}")
        lines.append("")

    # Reliability
    if "reliability" in results:
        rel = results["reliability"]
        lines.append(f"▸ SYMPTOM RELIABILITY: {rel.get('reliability_score', '?')}")
        for alert in rel.get("alerts", []):
            lines.append(f"  ⚠ {alert}")
        if rel.get("suggestion"):
            lines.append(f"  → {rel['suggestion']}")
        lines.append("")

    # Temporal
    if "temporal" in results:
        lines.append("▸ TEMPORAL INSIGHTS")
        for insight in results["temporal"].get("insights", []):
            lines.append(f"  • {insight}")
        lines.append("")

    # Rare patterns
    if "rare_patterns" in results:
        lines.append("▸ RARE PATTERN DISCOVERIES")
        for p in results["rare_patterns"]:
            lines.append(f"  ★ {p['description']}")
        lines.append("")

    return "\n".join(lines)
