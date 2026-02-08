"""
Graph-RAG Validation Suite
===========================
Comprehensive checks to verify the Graph-RAG system is working correctly.

Run:  .venv/bin/python validate_graph_rag.py

Checks:
  1. Graph health — nodes, edges, connectivity
  2. Data quality — names, relationships, symptoms
  3. Graph traversal — Symptom → Rubric → Remedy paths work
  4. Known clinical cases — well-known remedy-symptom associations rank correctly
  5. Intelligence layers — reliability, uncertainty, pattern mining
  6. End-to-end pipeline — full complaint → ranked remedies (uses LLM)
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field

from core.graph_client import GraphClient

# ── result tracking ──────────────────────────────────────

@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""
    warning: str = ""

@dataclass
class ValidationReport:
    checks: list[CheckResult] = field(default_factory=list)

    def add(self, name: str, passed: bool, detail: str = "", warning: str = ""):
        self.checks.append(CheckResult(name, passed, detail, warning))

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    @property
    def warnings(self) -> int:
        return sum(1 for c in self.checks if c.warning)

    def print_report(self):
        print("\n" + "=" * 70)
        print("  GRAPH-RAG VALIDATION REPORT")
        print("=" * 70)

        for c in self.checks:
            icon = "PASS" if c.passed else "FAIL"
            marker = "\033[32m✓\033[0m" if c.passed else "\033[31m✗\033[0m"
            print(f"\n  {marker} [{icon}] {c.name}")
            if c.detail:
                for line in c.detail.split("\n"):
                    print(f"         {line}")
            if c.warning:
                print(f"    \033[33m⚠ {c.warning}\033[0m")

        print("\n" + "─" * 70)
        total = len(self.checks)
        print(f"  Total: {total}  |  Passed: \033[32m{self.passed}\033[0m  |  "
              f"Failed: \033[31m{self.failed}\033[0m  |  Warnings: \033[33m{self.warnings}\033[0m")

        pct = (self.passed / total * 100) if total else 0
        if pct == 100:
            grade = "PERFECT"
            color = "\033[32m"
        elif pct >= 90:
            grade = "EXCELLENT"
            color = "\033[32m"
        elif pct >= 75:
            grade = "GOOD"
            color = "\033[33m"
        elif pct >= 50:
            grade = "NEEDS WORK"
            color = "\033[33m"
        else:
            grade = "CRITICAL ISSUES"
            color = "\033[31m"

        print(f"  Score: {color}{pct:.0f}% — {grade}\033[0m")
        print("=" * 70 + "\n")


# ══════════════════════════════════════════════════════════
# CHECK 1: GRAPH HEALTH
# ══════════════════════════════════════════════════════════

def check_graph_health(graph: GraphClient, report: ValidationReport):
    """Verify Neo4j is reachable and has expected node/edge counts."""
    print("\n── 1. Graph Health ──")

    # 1a. Connectivity
    try:
        result = graph.run_query("RETURN 1 AS ping")
        report.add("Neo4j connectivity", True, "Neo4j is reachable")
    except Exception as e:
        report.add("Neo4j connectivity", False, f"Cannot connect: {e}")
        return  # Can't proceed

    # 1b. Node counts
    counts = {}
    for label in ["Remedy", "Rubric", "Symptom", "Case", "CaseSnapshot"]:
        result = graph.run_query(f"MATCH (n:{label}) RETURN count(n) AS c")
        counts[label] = result[0]["c"] if result else 0

    detail = ", ".join(f"{k}: {v:,}" for k, v in counts.items())

    report.add(
        "Node counts",
        counts["Remedy"] >= 50 and counts["Rubric"] >= 100 and counts["Symptom"] >= 100,
        detail,
        warning="" if counts["Remedy"] >= 500 else f"Only {counts['Remedy']} remedies — expected 700+"
    )

    # 1c. Edge counts
    edge_types = ["INDICATES", "BELONGS_TO", "CORRELATED_WITH", "ANTIDOTES",
                  "COMPLEMENTARY", "INCOMPATIBLE"]
    edges = {}
    for et in edge_types:
        result = graph.run_query(f"MATCH ()-[r:{et}]->() RETURN count(r) AS c")
        edges[et] = result[0]["c"] if result else 0

    detail = "\n".join(f"{k:20s}: {v:,}" for k, v in edges.items())
    report.add(
        "Edge counts",
        edges["INDICATES"] >= 1000 and edges["BELONGS_TO"] >= 1000,
        detail,
        warning="" if edges["CORRELATED_WITH"] >= 500 else
        f"Only {edges['CORRELATED_WITH']} CORRELATED_WITH edges"
    )

    # 1d. Constraints
    result = graph.run_query("SHOW CONSTRAINTS")
    constraint_names = [r.get("name", "") for r in result]
    has_abbrev = any("abbrev" in str(c).lower() for c in result)
    report.add(
        "Schema constraints",
        has_abbrev,
        f"{len(result)} constraints found",
        warning="" if has_abbrev else "Missing Remedy.abbrev UNIQUE constraint"
    )


# ══════════════════════════════════════════════════════════
# CHECK 2: DATA QUALITY
# ══════════════════════════════════════════════════════════

def check_data_quality(graph: GraphClient, report: ValidationReport):
    """Verify remedy names, symptom quality, relationship coverage."""
    print("── 2. Data Quality ──")

    # 2a. Remedy names populated
    result = graph.run_query("""
        MATCH (r:Remedy)
        WITH count(r) AS total,
             sum(CASE WHEN r.name IS NOT NULL AND size(r.name) > 3 THEN 1 ELSE 0 END) AS named
        RETURN total, named
    """)
    total = result[0]["total"]
    named = result[0]["named"]
    pct = named / total * 100 if total else 0
    report.add(
        "Remedy names populated",
        pct >= 90,
        f"{named}/{total} have names ({pct:.1f}%)",
        warning="" if pct >= 95 else f"{total - named} remedies still missing proper names"
    )

    # 2b. Full names (not just abbreviations)
    result = graph.run_query("""
        MATCH (r:Remedy)
        WHERE r.name IS NOT NULL AND size(r.name) >= 10
        RETURN count(r) AS c
    """)
    full_count = result[0]["c"]
    report.add(
        "Full remedy names (not abbreviations)",
        full_count >= 500,
        f"{full_count}/{total} have full names (>=10 chars)",
        warning="" if full_count >= 600 else "Many names are still abbreviation-style"
    )

    # 2c. Common names
    result = graph.run_query("""
        MATCH (r:Remedy)
        WHERE r.common_name IS NOT NULL AND size(r.common_name) > 0
        RETURN count(r) AS c
    """)
    common = result[0]["c"]
    report.add(
        "Common names populated",
        common >= 100,
        f"{common}/{total} have common names",
    )

    # 2d. Symptoms with meaningful names
    result = graph.run_query("""
        MATCH (s:Symptom)
        WHERE size(s.name) < 5
        RETURN count(s) AS c
    """)
    short_symptoms = result[0]["c"]
    result2 = graph.run_query("MATCH (s:Symptom) RETURN count(s) AS c")
    total_syms = result2[0]["c"]
    report.add(
        "Symptom name quality",
        short_symptoms < total_syms * 0.05,
        f"{short_symptoms} symptoms with names < 5 chars (of {total_syms:,})",
    )

    # 2e. Orphan remedies (no INDICATES edges)
    result = graph.run_query("""
        MATCH (r:Remedy)
        WHERE NOT (r)<-[:INDICATES]-()
        RETURN count(r) AS c
    """)
    orphans = result[0]["c"]
    report.add(
        "Orphan remedies (no indications)",
        orphans < total * 0.20,
        f"{orphans}/{total} remedies have zero INDICATES edges",
        warning=f"{orphans} remedies unreachable by symptom search" if orphans > 50 else ""
    )

    # 2f. Source tagging
    result = graph.run_query("""
        MATCH (r:Remedy)
        RETURN r.source AS src, count(r) AS c
        ORDER BY c DESC
    """)
    detail = ", ".join(f"{r['src']}: {r['c']}" for r in result)
    has_sources = any(r["src"] is not None for r in result)
    report.add(
        "Source tagging",
        has_sources,
        detail
    )


# ══════════════════════════════════════════════════════════
# CHECK 3: GRAPH TRAVERSAL
# ══════════════════════════════════════════════════════════

def check_graph_traversal(graph: GraphClient, report: ValidationReport):
    """Verify core Symptom → Rubric → Remedy paths work."""
    print("── 3. Graph Traversal ──")

    # 3a. S→R→Rem path exists
    result = graph.run_query("""
        MATCH (s:Symptom)-[:BELONGS_TO]->(r:Rubric)-[:INDICATES]->(rem:Remedy)
        RETURN count(DISTINCT rem) AS remedies_reachable, 
               count(DISTINCT s) AS symptoms_connected,
               count(DISTINCT r) AS rubrics_used
    """)
    row = result[0]
    report.add(
        "S→R→Rem traversal",
        row["remedies_reachable"] >= 30,
        f"Reachable: {row['remedies_reachable']} remedies via "
        f"{row['symptoms_connected']:,} symptoms through {row['rubrics_used']:,} rubrics"
    )

    # 3b. Ranking works with real symptom IDs
    result = graph.run_query("""
        MATCH (s:Symptom)-[:BELONGS_TO]->(r:Rubric)-[:INDICATES]->(rem:Remedy)
        WITH s, count(DISTINCT rem) AS reach
        WHERE reach >= 2
        RETURN s.id AS id, s.name AS name, reach
        ORDER BY reach DESC
        LIMIT 3
    """)
    if result:
        test_ids = [r["id"] for r in result]
        from core.remedy_ranker import rank_remedies
        ranked = rank_remedies(graph, test_ids)
        report.add(
            "Ranker produces results",
            len(ranked) >= 2,
            f"Queried {len(test_ids)} symptoms → {len(ranked)} remedies ranked\n"
            f"Top 3: {', '.join(f'{r.name} ({r.raw_score:.3f})' for r in ranked[:3])}",
        )
    else:
        report.add("Ranker produces results", False, "No multi-remedy symptoms found")

    # 3c. Relationship edges navigable
    result = graph.run_query("""
        MATCH (a:Remedy)-[r:CORRELATED_WITH]->(b:Remedy)
        RETURN count(r) AS c
    """)
    corr = result[0]["c"]
    result2 = graph.run_query("""
        MATCH (a:Remedy)-[r:ANTIDOTES]->(b:Remedy)
        RETURN count(r) AS c
    """)
    anti = result2[0]["c"]
    report.add(
        "Remedy-to-remedy relationships",
        corr >= 100 and anti >= 20,
        f"CORRELATED_WITH: {corr}, ANTIDOTES: {anti}",
    )


# ══════════════════════════════════════════════════════════
# CHECK 4: KNOWN CLINICAL CASES
# ══════════════════════════════════════════════════════════

# Well-known homeopathic remedy-symptom associations (textbook cases)
KNOWN_CASES = [
    {
        "name": "Belladonna keynotes",
        "symptoms": ["throbbing headache", "sudden onset", "red face", "high fever"],
        "expected_top": ["Belladonna"],
        "expected_any": ["Belladonna", "Aconitum"],
    },
    {
        "name": "Arsenicum keynotes",
        "symptoms": ["burning pain", "restlessness", "anxiety", "thirst for sips"],
        "expected_top": ["Arsenicum Album"],
        "expected_any": ["Arsenicum", "Arsenicum Album"],
    },
    {
        "name": "Nux Vomica keynotes",
        "symptoms": ["irritability", "constipation", "oversensitivity", "chilly"],
        "expected_top": ["Nux Vomica"],
        "expected_any": ["Nux Vomica", "Nux-v"],
    },
    {
        "name": "Pulsatilla keynotes",
        "symptoms": ["weeping easily", "changeable symptoms", "thirstlessness", "worse warm room"],
        "expected_top": ["Pulsatilla", "Pulsatilla Pratensis"],
        "expected_any": ["Pulsatilla", "Pulsatilla Pratensis"],
    },
]


def check_known_cases(graph: GraphClient, report: ValidationReport):
    """Test whether well-known remedy associations rank correctly."""
    print("── 4. Known Clinical Cases ──")

    from core.symptom_extractor import map_symptoms_to_graph

    for case in KNOWN_CASES:
        # Manually map symptom phrases to graph
        extracted = [{"name": s, "category": "other"} for s in case["symptoms"]]
        symptom_ids = map_symptoms_to_graph(graph, extracted)

        if not symptom_ids:
            report.add(
                f"Case: {case['name']}",
                False,
                f"No symptoms matched in graph for: {case['symptoms']}",
                warning="Graph may lack these symptom keywords"
            )
            continue

        from core.remedy_ranker import rank_remedies
        ranked = rank_remedies(graph, symptom_ids)

        if not ranked:
            report.add(
                f"Case: {case['name']}",
                False,
                f"Matched {len(symptom_ids)} symptoms but 0 remedies returned",
            )
            continue

        top_5_names = [r.name for r in ranked[:5]]
        top_10_names = [r.name for r in ranked[:10]]

        # Check if expected remedy appears in top 5
        in_top5 = any(
            any(exp.lower() in name.lower() for name in top_5_names)
            for exp in case["expected_top"]
        )
        # Check if expected remedy appears anywhere in top 10
        in_top10 = any(
            any(exp.lower() in name.lower() for name in top_10_names)
            for exp in case["expected_any"]
        )

        detail = (
            f"Matched {len(symptom_ids)}/{len(case['symptoms'])} symptoms\n"
            f"Top 5: {', '.join(top_5_names)}\n"
            f"Expected in top: {case['expected_top']}"
        )

        report.add(
            f"Case: {case['name']}",
            in_top5,
            detail,
            warning="" if in_top5 else (
                "Expected remedy in top 10 but not top 5" if in_top10
                else "Expected remedy NOT found in top 10"
            ),
        )


# ══════════════════════════════════════════════════════════
# CHECK 5: INTELLIGENCE LAYERS
# ══════════════════════════════════════════════════════════

def check_intelligence_layers(graph: GraphClient, report: ValidationReport):
    """Verify each intelligence layer runs without error."""
    print("── 5. Intelligence Layers ──")

    # Find some real symptom IDs to use
    result = graph.run_query("""
        MATCH (s:Symptom)-[:BELONGS_TO]->(r:Rubric)-[:INDICATES]->(rem:Remedy)
        WITH s, count(DISTINCT rem) AS reach
        WHERE reach >= 2
        RETURN s.id AS id
        ORDER BY reach DESC
        LIMIT 5
    """)
    test_ids = [r["id"] for r in result]

    if len(test_ids) < 2:
        report.add("Intelligence layers", False, "Not enough multi-remedy symptoms to test")
        return

    # 5a. Reliability
    try:
        from reasoning.reliability.reliability_scorer import compute_reliability
        rel = compute_reliability(graph, test_ids[:3])
        report.add(
            "Reliability scorer",
            0 <= rel.reliability_score <= 1,
            f"Score: {rel.reliability_score:.2f}, Alerts: {len(rel.alerts)}",
        )
    except Exception as e:
        report.add("Reliability scorer", False, str(e))

    # 5b. Uncertainty estimation
    try:
        from reasoning.uncertainty.confidence_estimator import estimate_confidence
        uc = estimate_confidence(graph, test_ids[:3], n_iterations=50)
        report.add(
            "Uncertainty estimator",
            0 <= uc.overall_certainty <= 1,
            f"Certainty: {uc.overall_certainty:.2f}, "
            f"Remedies with CI: {len(uc.remedies)}",
        )
    except Exception as e:
        report.add("Uncertainty estimator", False, str(e))

    # 5c. Pattern mining
    try:
        from reasoning.pattern_mining.outcome_correlator import discover_for_current_case
        patterns = discover_for_current_case(graph, test_ids[:3])
        report.add(
            "Pattern mining",
            True,  # Not crashing is a pass — discoveries are bonus
            f"Discoveries: {len(patterns.discoveries)}",
        )
    except Exception as e:
        report.add("Pattern mining", False, str(e))


# ══════════════════════════════════════════════════════════
# CHECK 6: END-TO-END PIPELINE (with LLM)
# ══════════════════════════════════════════════════════════

def check_e2e_pipeline(graph: GraphClient, report: ValidationReport, skip_llm: bool = False):
    """Run the full enhanced pipeline on a test complaint."""
    print("── 6. End-to-End Pipeline ──")

    if skip_llm:
        report.add("E2E pipeline (LLM)", True, "Skipped (--no-llm flag)", warning="LLM checks skipped")
        return

    try:
        from integration.enhanced_pipeline import run_enhanced_pipeline, format_clinical_summary
        import config

        if not config.GEMINI_API_KEY:
            report.add("E2E pipeline", False, "GEMINI_API_KEY not set")
            return

        complaint = "Patient has throbbing headache, worse from light and noise, with high fever and red face"

        start = time.time()
        result = run_enhanced_pipeline(
            graph,
            complaint=complaint,
            enable_reliability=True,
            enable_uncertainty=True,
            enable_pattern_mining=True,
            enable_temporal=False,  # No case_id for this test
            explain=True,
            bootstrap_iterations=50,
        )
        elapsed = time.time() - start

        has_ranked = len(result.get("ranked_remedies", [])) > 0
        has_explanation = bool(result.get("explanation"))

        detail = (
            f"Complaint: \"{complaint[:60]}...\"\n"
            f"Symptoms mapped: {len(result.get('symptom_ids', []))}\n"
            f"Remedies ranked: {len(result.get('ranked_remedies', []))}\n"
            f"Has explanation: {has_explanation}\n"
            f"Time: {elapsed:.1f}s"
        )

        if has_ranked:
            top = result["ranked_remedies"][0]
            detail += f"\nTop remedy: {top['remedy']} (score: {top.get('score', top.get('mean_score', 0)):.4f})"

        report.add(
            "E2E pipeline",
            has_ranked,
            detail,
            warning="" if elapsed < 15 else f"Slow: {elapsed:.1f}s"
        )

        # Print the formatted clinical summary
        if has_ranked:
            summary = format_clinical_summary(result)
            print("\n" + summary)

    except Exception as e:
        report.add("E2E pipeline", False, f"Error: {e}")


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════

def main():
    skip_llm = "--no-llm" in sys.argv

    print("=" * 70)
    print("  GRAPH-RAG VALIDATION SUITE")
    print("=" * 70)
    if skip_llm:
        print("  (LLM checks skipped — use without --no-llm to include)")

    report = ValidationReport()

    try:
        graph = GraphClient()
    except Exception as e:
        print(f"\n\033[31mFATAL: Cannot connect to Neo4j: {e}\033[0m")
        print("Make sure Neo4j is running: docker start homeopathy-graph")
        sys.exit(1)

    try:
        check_graph_health(graph, report)
        check_data_quality(graph, report)
        check_graph_traversal(graph, report)
        check_known_cases(graph, report)
        check_intelligence_layers(graph, report)
        check_e2e_pipeline(graph, report, skip_llm=skip_llm)
    finally:
        graph.close()

    report.print_report()
    sys.exit(0 if report.failed == 0 else 1)


if __name__ == "__main__":
    main()
