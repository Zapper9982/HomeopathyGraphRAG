"""
FastAPI REST API for the Graph-RAG Clinical Decision Support System.

Endpoints:
  POST /api/consult       — Full pipeline: complaint → ranked remedies + explanation
  POST /api/symptoms      — Extract symptoms from free text (LLM)
  POST /api/rank          — Rank remedies from symptom IDs (graph only, no LLM)
  GET  /api/remedy/{abbrev} — Get remedy details + relationships
  GET  /api/search/remedies — Search remedies by name
  GET  /api/search/symptoms — Search symptoms by keyword
  GET  /api/graph/stats    — Graph statistics
  GET  /api/health         — Health check
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.graph_client import GraphClient
from core.symptom_extractor import extract_symptoms_llm, map_symptoms_to_graph
from core.remedy_ranker import rank_remedies, rank_remedies_from_ids
from core.explainer import explain_results
from integration.enhanced_pipeline import run_enhanced_pipeline

# ── Global graph client ──────────────────────────────────
_graph: GraphClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _graph
    _graph = GraphClient()
    yield
    if _graph:
        _graph.close()


app = FastAPI(
    title="Homeopathy Graph-RAG API",
    description="Clinical decision support powered by Graph-RAG with 4 intelligence layers",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response Models ──────────────────────────────

class ConsultRequest(BaseModel):
    complaint: str = Field(..., min_length=5, description="Free-text patient complaint")
    enable_reliability: bool = True
    enable_uncertainty: bool = True
    enable_pattern_mining: bool = True
    case_id: str | None = None
    explain: bool = True

class RankRequest(BaseModel):
    symptom_ids: list[str] = Field(..., min_length=1, description="List of Symptom IDs from the graph")

class SymptomsRequest(BaseModel):
    complaint: str = Field(..., min_length=5)

class SymptomResult(BaseModel):
    name: str
    category: str

class MappedSymptom(BaseModel):
    extracted_name: str
    category: str
    matched_id: str | None = None
    matched_name: str | None = None

class RemedyBrief(BaseModel):
    abbrev: str
    name: str
    common_name: str = ""
    score: float | None = None

class RemedyDetail(BaseModel):
    abbrev: str
    name: str
    common_name: str = ""
    source: str | None = None
    indications_count: int = 0
    relationships: list[dict[str, Any]] = []
    top_rubrics: list[dict[str, str]] = []


# ── Endpoints ────────────────────────────────────────────

@app.get("/api/health")
async def health():
    """Health check — verifies Neo4j connectivity."""
    try:
        _graph.run_query("RETURN 1 AS ping")
        return {"status": "ok", "neo4j": "connected"}
    except Exception as e:
        raise HTTPException(503, detail=f"Neo4j unreachable: {e}")


@app.get("/api/graph/stats")
async def graph_stats():
    """Return graph statistics."""
    nodes = {}
    for label in ["Remedy", "Rubric", "Symptom", "Case"]:
        result = _graph.run_query(f"MATCH (n:{label}) RETURN count(n) AS c")
        nodes[label] = result[0]["c"] if result else 0

    edges = {}
    for et in ["INDICATES", "BELONGS_TO", "CORRELATED_WITH", "ANTIDOTES",
               "COMPLEMENTARY", "INCOMPATIBLE", "FOLLOWS_WELL"]:
        result = _graph.run_query(f"MATCH ()-[r:{et}]->() RETURN count(r) AS c")
        edges[et] = result[0]["c"] if result else 0

    # Reachable remedies
    result = _graph.run_query("""
        MATCH (s:Symptom)-[:BELONGS_TO]->(r:Rubric)-[:INDICATES]->(rem:Remedy)
        RETURN count(DISTINCT rem) AS c
    """)
    reachable = result[0]["c"] if result else 0

    return {
        "nodes": nodes,
        "edges": edges,
        "reachable_remedies": reachable,
    }


@app.post("/api/consult")
async def consult(req: ConsultRequest):
    """Full enhanced pipeline: complaint → ranked remedies with all intelligence layers."""
    start = time.time()
    try:
        result = run_enhanced_pipeline(
            graph=_graph,
            complaint=req.complaint,
            case_id=req.case_id,
            enable_reliability=req.enable_reliability,
            enable_uncertainty=req.enable_uncertainty,
            enable_pattern_mining=req.enable_pattern_mining,
            enable_temporal=bool(req.case_id),
            explain=req.explain,
            bootstrap_iterations=100,
        )
        result["elapsed_seconds"] = round(time.time() - start, 2)
        return result
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=f"Pipeline error: {e}")


@app.post("/api/symptoms")
async def extract_symptoms(req: SymptomsRequest):
    """Extract and map symptoms from free text. Returns extracted + matched symptoms."""
    try:
        extracted = extract_symptoms_llm(req.complaint)
    except Exception as e:
        raise HTTPException(500, detail=f"LLM extraction failed: {e}")

    mapped: list[dict] = []
    for sym in extracted:
        name = sym.get("name", "")
        category = sym.get("category", "other")
        records = _graph.run_query(
            """
            MATCH (s:Symptom)
            WHERE toLower(s.name) CONTAINS toLower($name)
            RETURN s.id AS id, s.name AS name
            LIMIT 1
            """,
            name=name,
        )
        mapped.append({
            "extracted_name": name,
            "category": category,
            "matched_id": records[0]["id"] if records else None,
            "matched_name": records[0]["name"] if records else None,
        })

    return {
        "symptoms": mapped,
        "matched_count": sum(1 for m in mapped if m["matched_id"]),
        "total_extracted": len(mapped),
    }


@app.post("/api/rank")
async def rank_from_ids(req: RankRequest):
    """Rank remedies from pre-mapped symptom IDs. No LLM involved."""
    ranked = rank_remedies_from_ids(_graph, req.symptom_ids)
    return {
        "ranked_remedies": ranked[:20],
        "total": len(ranked),
    }


@app.get("/api/remedy/{abbrev}")
async def get_remedy(abbrev: str):
    """Get full remedy details including relationships and top rubrics."""
    result = _graph.run_query(
        """
        MATCH (r:Remedy {abbrev: $abbrev})
        RETURN r.abbrev AS abbrev, r.name AS name, 
               r.common_name AS common_name, r.source AS source
        """,
        abbrev=abbrev,
    )
    if not result:
        raise HTTPException(404, detail=f"Remedy '{abbrev}' not found")

    remedy = result[0]

    # Indications count
    ind = _graph.run_query(
        "MATCH (:Rubric)-[:INDICATES]->(r:Remedy {abbrev: $abbrev}) RETURN count(*) AS c",
        abbrev=abbrev,
    )
    remedy["indications_count"] = ind[0]["c"] if ind else 0

    # Relationships
    rels = _graph.run_query(
        """
        MATCH (a:Remedy {abbrev: $abbrev})-[rel]->(b:Remedy)
        RETURN type(rel) AS type, b.name AS target, b.abbrev AS target_abbrev
        UNION
        MATCH (a:Remedy)-[rel]->(b:Remedy {abbrev: $abbrev})
        RETURN type(rel) AS type, a.name AS target, a.abbrev AS target_abbrev
        """,
        abbrev=abbrev,
    )
    remedy["relationships"] = [dict(r) for r in rels]

    # Top rubrics
    rubrics = _graph.run_query(
        """
        MATCH (rub:Rubric)-[ind:INDICATES]->(r:Remedy {abbrev: $abbrev})
        RETURN rub.text AS rubric, ind.grade AS grade
        ORDER BY ind.grade DESC
        LIMIT 15
        """,
        abbrev=abbrev,
    )
    remedy["top_rubrics"] = [dict(r) for r in rubrics]

    return remedy


@app.get("/api/search/remedies")
async def search_remedies(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
):
    """Search remedies by name or abbreviation."""
    results = _graph.run_query(
        """
        MATCH (r:Remedy)
        WHERE toLower(r.name) CONTAINS toLower($q)
           OR toLower(r.abbrev) CONTAINS toLower($q)
           OR toLower(r.common_name) CONTAINS toLower($q)
        RETURN r.abbrev AS abbrev, r.name AS name, r.common_name AS common_name
        ORDER BY r.name
        LIMIT $limit
        """,
        q=q, limit=limit,
    )
    return {"results": [dict(r) for r in results], "count": len(results)}


@app.get("/api/search/symptoms")
async def search_symptoms(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
):
    """Search symptoms by keyword."""
    results = _graph.run_query(
        """
        MATCH (s:Symptom)
        WHERE toLower(s.name) CONTAINS toLower($q)
        RETURN s.id AS id, s.name AS name, s.category AS category
        LIMIT $limit
        """,
        q=q, limit=limit,
    )
    return {"results": [dict(r) for r in results], "count": len(results)}


@app.get("/api/remedy/{abbrev}/network")
async def remedy_network(abbrev: str, depth: int = Query(1, ge=1, le=3)):
    """Get remedy relationship network for visualization."""
    results = _graph.run_query(
        """
        MATCH path = (a:Remedy {abbrev: $abbrev})-[r*1..2]-(b:Remedy)
        WHERE ALL(rel IN r WHERE type(rel) IN 
            ['CORRELATED_WITH', 'ANTIDOTES', 'COMPLEMENTARY', 'INCOMPATIBLE', 'FOLLOWS_WELL'])
        UNWIND r AS rel
        WITH startNode(rel) AS src, endNode(rel) AS tgt, type(rel) AS relType
        RETURN DISTINCT src.abbrev AS source, src.name AS source_name,
               tgt.abbrev AS target, tgt.name AS target_name,
               relType AS type
        LIMIT 100
        """,
        abbrev=abbrev,
    )

    nodes = {}
    edges = []
    for r in results:
        nodes[r["source"]] = {"id": r["source"], "name": r["source_name"]}
        nodes[r["target"]] = {"id": r["target"], "name": r["target_name"]}
        edges.append({
            "source": r["source"],
            "target": r["target"],
            "type": r["type"],
        })

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
    }


# Frontend is served separately via Next.js (see /frontend)
