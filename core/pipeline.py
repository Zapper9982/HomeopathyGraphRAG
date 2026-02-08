"""
Core Graph-RAG Pipeline — orchestrates symptom extraction,
graph-based ranking, and LLM explanation.

This is the BASE pipeline. The enhanced pipeline in
integration/enhanced_pipeline.py layers the four advanced
intelligence modules on top.
"""

from __future__ import annotations

from typing import Any

from core.graph_client import GraphClient
from core.symptom_extractor import extract_and_map, map_symptoms_to_graph
from core.remedy_ranker import rank_remedies_from_ids
from core.explainer import explain_results


def run_base_pipeline(
    graph: GraphClient,
    complaint: str | None = None,
    symptom_ids: list[str] | None = None,
) -> dict[str, Any]:
    """
    Base pipeline:
      1. Extract symptoms (LLM) or accept pre-mapped IDs
      2. Rank remedies (graph traversal)
      3. Explain results (LLM)

    Returns the full result dict.
    """
    # Step 1: symptom resolution
    if symptom_ids is None:
        if complaint is None:
            raise ValueError("Provide either complaint text or symptom_ids")
        symptom_ids = extract_and_map(graph, complaint)

    # Step 2: graph-based ranking
    ranked = rank_remedies_from_ids(graph, symptom_ids)

    result: dict[str, Any] = {
        "symptom_ids": symptom_ids,
        "ranked_remedies": ranked,
    }

    # Step 3: explanation (LLM — never invents)
    result["explanation"] = explain_results(result)

    return result
