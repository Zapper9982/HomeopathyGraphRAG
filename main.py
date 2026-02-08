"""
Main entry point — bootstraps the graph and runs demos.

Usage:
  python main.py seed              # Create schema + load basic seed data
  python main.py seed-expanded     # Create schema + load expanded repertory data
  python main.py demo              # Run demo with Belladonna-like acute case
  python main.py demo-arsenic      # Run demo with Arsenicum anxiety case
  python main.py demo-natmur       # Run demo with Natrum Mur grief case
  python main.py demo-contradiction # Run demo with contradictory symptoms
  python main.py demo-temporal     # Run demo with temporal case evolution
"""

from __future__ import annotations

import sys

from core.graph_client import GraphClient
from integration.enhanced_pipeline import (
    run_enhanced_pipeline,
    format_clinical_summary,
)


def cmd_seed():
    """Bootstrap schema and load basic seed data."""
    print("Connecting to Neo4j...")
    with GraphClient() as graph:
        print("Applying schema...")
        graph.bootstrap_schema()
        print("Seeding basic data...")
        graph.seed()
        print("✓ Schema and basic seed data loaded successfully.")


def cmd_seed_expanded():
    """Bootstrap schema and load the expanded homeopathic knowledge graph."""
    print("Connecting to Neo4j...")
    with GraphClient() as graph:
        print("Applying schema...")
        graph.bootstrap_schema()
        print("Loading expanded repertory data...")
        stats = graph.seed_expanded()
        print("✓ Expanded knowledge graph loaded:")
        for key, val in stats.items():
            print(f"  {key}: {val}")


def cmd_demo():
    """Run the enhanced pipeline — classic Belladonna acute case."""
    print("=" * 60)
    print("DEMO: Classic Belladonna Acute Case")
    print("  Symptoms: Throbbing headache, Red face, Dilated pupils,")
    print("            Sudden onset, Hot patient")
    print("=" * 60 + "\n")

    with GraphClient() as graph:
        result = run_enhanced_pipeline(
            graph,
            symptom_ids=[
                "SYM_HEAD_001",  # Throbbing headache
                "SYM_FACE_001",  # Red flushed face
                "SYM_EYE_001",   # Dilated pupils
                "SYM_ONSET_001", # Sudden onset
                "SYM_THER_002",  # Hot patient
            ],
            enable_reliability=True,
            enable_uncertainty=True,
            enable_temporal=False,
            enable_pattern_mining=True,
            bootstrap_iterations=200,
            explain=False,
        )
        print(format_clinical_summary(result))


def cmd_demo_arsenic():
    """Run the pipeline — classic Arsenicum Album anxiety case."""
    print("=" * 60)
    print("DEMO: Arsenicum Album Chronic Anxiety Case")
    print("  Symptoms: Anxiety about health, Restlessness, Fear of death,")
    print("            Chilly patient, Worse at night, Fastidious,")
    print("            Insomnia from anxiety")
    print("=" * 60 + "\n")

    with GraphClient() as graph:
        result = run_enhanced_pipeline(
            graph,
            symptom_ids=[
                "SYM_MIND_001",  # Anxiety about health
                "SYM_MIND_002",  # Restlessness
                "SYM_MIND_003",  # Fear of death
                "SYM_THER_001",  # Chilly patient
                "SYM_MOD_003",   # Worse at night
                "SYM_MIND_018",  # Fastidious
                "SYM_SLEEP_001", # Insomnia from anxiety
            ],
            enable_reliability=True,
            enable_uncertainty=True,
            enable_temporal=False,
            enable_pattern_mining=True,
            bootstrap_iterations=200,
            explain=False,
        )
        print(format_clinical_summary(result))


def cmd_demo_natmur():
    """Run the pipeline — Natrum Mur suppressed grief case."""
    print("=" * 60)
    print("DEMO: Natrum Muriaticum Grief Case")
    print("  Symptoms: Emotional numbness, Suppressed grief, Sun agg,")
    print("            Aversion to company, Desire for salt, Headache from sun")
    print("=" * 60 + "\n")

    with GraphClient() as graph:
        result = run_enhanced_pipeline(
            graph,
            symptom_ids=[
                "SYM_MIND_006",  # Emotional numbness
                "SYM_MIND_007",  # Grief suppressed
                "SYM_MOD_017",   # Sun aggravation
                "SYM_MIND_015",  # Aversion to company
                "SYM_STOM_009",  # Desire for salt
                "SYM_HEAD_005",  # Headache from sun
            ],
            enable_reliability=True,
            enable_uncertainty=True,
            enable_temporal=False,
            enable_pattern_mining=True,
            bootstrap_iterations=200,
            explain=False,
        )
        print(format_clinical_summary(result))


def cmd_demo_contradiction():
    """Run the pipeline with contradictory thermal symptoms."""
    print("=" * 60)
    print("DEMO: Contradictory Symptom Detection")
    print("  Symptoms: Worse by heat + Desire for warmth (contradictory!)")
    print("            + Restlessness + Throbbing headache")
    print("=" * 60 + "\n")

    with GraphClient() as graph:
        result = run_enhanced_pipeline(
            graph,
            symptom_ids=[
                "SYM_MOD_001",   # Worse by heat
                "SYM_MOD_002",   # Desire for warmth ← contradicts heat agg
                "SYM_MIND_002",  # Restlessness
                "SYM_HEAD_001",  # Throbbing headache
            ],
            enable_reliability=True,
            enable_uncertainty=True,
            enable_temporal=False,
            enable_pattern_mining=True,
            bootstrap_iterations=200,
            explain=False,
        )
        print(format_clinical_summary(result))


def cmd_demo_temporal():
    """Run the pipeline with temporal case evolution (suppression detection)."""
    print("=" * 60)
    print("DEMO: Temporal Case Evolution")
    print("  Case CASE009: Physical improved but mental worsened")
    print("  → suppression detection should trigger")
    print("=" * 60 + "\n")

    with GraphClient() as graph:
        # Current follow-up symptoms — mental aggravation after physical improvement
        result = run_enhanced_pipeline(
            graph,
            symptom_ids=[
                "SYM_MIND_002",  # Restlessness (NEW)
                "SYM_MIND_001",  # Anxiety about health (NEW)
                "SYM_SLEEP_001", # Insomnia (NEW)
            ],
            case_id="CASE009",
            enable_reliability=True,
            enable_uncertainty=True,
            enable_temporal=True,
            enable_pattern_mining=True,
            bootstrap_iterations=200,
            explain=False,
        )
        print(format_clinical_summary(result))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    dispatch = {
        "seed": cmd_seed,
        "seed-expanded": cmd_seed_expanded,
        "demo": cmd_demo,
        "demo-arsenic": cmd_demo_arsenic,
        "demo-natmur": cmd_demo_natmur,
        "demo-contradiction": cmd_demo_contradiction,
        "demo-temporal": cmd_demo_temporal,
    }

    if cmd not in dispatch:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(dispatch.keys())}")
        sys.exit(1)

    dispatch[cmd]()


if __name__ == "__main__":
    main()
