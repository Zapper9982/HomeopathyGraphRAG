"""
LLM-based symptom extraction.

Takes free-text patient complaint and returns structured symptom IDs
by matching against the knowledge graph.

LLM is used ONLY to structure input — never to reason about remedies.
"""

from __future__ import annotations

import json
from typing import Any

from google import genai

import config
from core.graph_client import GraphClient


EXTRACTION_SYSTEM_PROMPT = """\
You are a clinical NLP assistant for a homeopathic decision-support system.
Given a patient complaint in natural language, extract a JSON array of symptoms.
Each element must have:
  - "name": a concise symptom phrase
  - "category": one of head, eye, face, modality, mental, thermal, sensation, stomach, onset, other

Return ONLY valid JSON (a JSON object with a "symptoms" key). Do NOT suggest remedies or diagnoses.
"""


def extract_symptoms_llm(complaint: str) -> list[dict[str, str]]:
    """Call LLM to structure free-text into symptom dicts."""
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set — cannot run LLM extraction")

    client = genai.Client(api_key=config.GEMINI_API_KEY)
    resp = client.models.generate_content(
        model=config.LLM_MODEL,
        contents=f"{EXTRACTION_SYSTEM_PROMPT}\n\nPatient complaint:\n{complaint}",
        config=genai.types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )
    raw = resp.text
    parsed = json.loads(raw)
    # Accept either {"symptoms": [...]} or [...]
    if isinstance(parsed, dict) and "symptoms" in parsed:
        return parsed["symptoms"]
    if isinstance(parsed, list):
        return parsed
    return []


def map_symptoms_to_graph(
    graph: GraphClient,
    extracted: list[dict[str, str]],
) -> list[str]:
    """
    Fuzzy-match extracted symptom names to graph Symptom nodes.
    Returns list of matched Symptom IDs.
    """
    symptom_ids: list[str] = []
    for sym in extracted:
        name = sym.get("name", "")
        # Case-insensitive CONTAINS match against the graph
        records = graph.run_query(
            """
            MATCH (s:Symptom)
            WHERE toLower(s.name) CONTAINS toLower($name)
            RETURN s.id AS id, s.name AS name
            LIMIT 1
            """,
            name=name,
        )
        if records:
            symptom_ids.append(records[0]["id"])
    return symptom_ids


def extract_and_map(
    graph: GraphClient,
    complaint: str,
) -> list[str]:
    """End-to-end: free-text → graph Symptom IDs."""
    extracted = extract_symptoms_llm(complaint)
    return map_symptoms_to_graph(graph, extracted)
