#!/usr/bin/env python3
"""
Data quality cleanup script.

Fixes known issues in the Neo4j graph after initial Boericke scrape:
  1. Populate empty remedy names from index pages
  2. Re-parse & reload relationships with proper name resolution
  3. Remove duplicate relationship edges
  4. Tag seed remedies with source='seed'
  5. Clean up symptoms with very short or empty text

Usage:
    python -m data_pipeline.scripts.cleanup [--dry-run]
"""

from __future__ import annotations

import json
import os
import re
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCRAPED_FILE = DATA_DIR / "scraped_remedies.json"
PARSED_FILE = DATA_DIR / "parsed_remedies.json"


def get_driver():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD", "homeopathy_graph_2026")
    return GraphDatabase.driver(uri, auth=(user, pwd))


# ─────────────────────────────────────────────────────────
# STEP 1: Populate remedy names from index pages
# ─────────────────────────────────────────────────────────

def fetch_index_names() -> dict[str, str]:
    """
    Re-scrape index pages (lightweight — no remedy pages) to get
    abbrev → name mapping.
    """
    from data_pipeline.scrapers.boericke_scraper import BoerickeScraper

    print("  Fetching index pages for name mapping...")
    scraper = BoerickeScraper(delay_seconds=0.5)  # faster for index-only
    remedy_list = scraper.get_remedy_urls()
    mapping = {}
    for r in remedy_list:
        abbrev = r["abbrev"].lower().strip()
        name = r.get("name", "").strip()
        if name:
            # Normalize: "BELLADONNA" → "Belladonna"
            mapping[abbrev] = name.title()
    print(f"  Got names for {len(mapping)} remedies from index pages")
    return mapping


def populate_names(driver, name_map: dict[str, str], dry_run: bool = False):
    """Set remedy names in Neo4j for Boericke remedies with empty names."""
    with driver.session() as session:
        # Get current empty-name remedies
        result = session.run(
            """
            MATCH (r:Remedy)
            WHERE r.source = 'boericke' AND (r.name IS NULL OR r.name = '')
            RETURN r.abbrev AS abbrev
            """
        )
        empty = [rec["abbrev"] for rec in result]
        print(f"  Remedies needing names: {len(empty)}")

        if dry_run:
            matched = sum(1 for a in empty if a in name_map)
            print(f"  [DRY RUN] Would update {matched}/{len(empty)} names")
            return matched

        updated = 0
        batch = []
        for abbrev in empty:
            name = name_map.get(abbrev, "")
            if name:
                batch.append({"abbrev": abbrev, "name": name})

        if batch:
            session.run(
                """
                UNWIND $batch AS b
                MATCH (r:Remedy {abbrev: b.abbrev})
                SET r.name = b.name
                """,
                batch=batch,
            )
            updated = len(batch)

        print(f"  Updated {updated} remedy names")
        return updated


# ─────────────────────────────────────────────────────────
# STEP 2: Re-parse and reload relationships
# ─────────────────────────────────────────────────────────

def rebuild_relationships(driver, name_map: dict[str, str], dry_run: bool = False):
    """
    Re-extract relationships from scraped data, resolve target names
    to abbreviations, and reload into Neo4j.
    """
    from data_pipeline.parsers.relationship_extractor import RelationshipExtractor
    from data_pipeline.parsers.remedy_parser import ParsedRelationship

    if not SCRAPED_FILE.exists():
        print("  [SKIP] No scraped data file found")
        return 0

    with open(SCRAPED_FILE) as f:
        scraped = json.load(f)

    # Build comprehensive name→abbrev lookup
    # Include: index names, abbreviations, common variations
    lookup: dict[str, str] = {}
    for r in scraped:
        abbrev = r["abbrev"].lower().strip()
        lookup[abbrev] = abbrev

    for abbrev, name in name_map.items():
        lookup[name.lower()] = abbrev
        # First word (e.g., "belladonna" for "Belladonna")
        first = name.split()[0].lower()
        if first and len(first) > 2:
            lookup.setdefault(first, abbrev)

    # Add known abbreviations from relationship extractor
    extractor = RelationshipExtractor()
    for abbr, full in extractor.KNOWN_ABBREVIATIONS.items():
        target = full.lower()
        if target in lookup:
            lookup[abbr.lower()] = lookup[target]
        elif abbr.lower().replace(" ", "-") in lookup:
            lookup[abbr.lower()] = lookup[abbr.lower().replace(" ", "-")]

    print(f"  Name lookup: {len(lookup)} entries")

    # Re-extract relationships
    all_edges = []
    unresolved = set()

    for r in scraped:
        rel_text = r.get("relationships", "").strip()
        if not rel_text:
            continue

        abbrev = r["abbrev"].lower().strip()
        rels = extractor.extract_all(abbrev, rel_text)

        seen = set()
        for rel in rels:
            target_name = rel.target_remedy.lower().strip()

            # Resolve to abbreviation
            resolved = lookup.get(target_name)
            if not resolved:
                # Try first word
                first = target_name.split()[0] if target_name.split() else ""
                resolved = lookup.get(first)
            if not resolved:
                # Try without common suffixes
                cleaned = re.sub(r'\s+(acid|mur|carb|sulph|phos)$', '', target_name)
                resolved = lookup.get(cleaned)
            if not resolved:
                unresolved.add(rel.target_remedy)
                # Keep the full name — Neo4j will try name match
                resolved = rel.target_remedy

            # Map relation type
            type_map = {
                "antidote": "ANTIDOTES",
                "complementary": "COMPLEMENTARY",
                "incompatible": "INCOMPATIBLE",
                "compare": "CORRELATED_WITH",
                "follows_well": "FOLLOWS_WELL",
                "inimical": "INCOMPATIBLE",
            }
            edge_type = type_map.get(rel.relation_type, "CORRELATED_WITH")

            # Dedup
            key = (abbrev, resolved, edge_type)
            if key in seen:
                continue
            seen.add(key)

            all_edges.append({
                "source": abbrev,
                "target": resolved,
                "type": edge_type,
                "context": rel.context,
            })

    print(f"  Extracted {len(all_edges)} unique relationship edges")
    print(f"  Unresolved targets: {len(unresolved)}")
    if unresolved:
        samples = list(unresolved)[:10]
        print(f"    Samples: {samples}")

    if dry_run:
        by_type = {}
        for e in all_edges:
            by_type[e["type"]] = by_type.get(e["type"], 0) + 1
        print(f"  [DRY RUN] Would load: {by_type}")
        return len(all_edges)

    # Delete existing Boericke relationship edges (not INDICATES/BELONGS_TO)
    rel_types = ["ANTIDOTES", "COMPLEMENTARY", "INCOMPATIBLE",
                 "CORRELATED_WITH", "FOLLOWS_WELL"]
    with driver.session() as session:
        for rtype in rel_types:
            session.run(
                f"""
                MATCH ()-[r:{rtype}]->()
                WHERE r.source = 'boericke'
                DELETE r
                """,
            )
        print("  Deleted old Boericke relationship edges")

        # Load new edges in batches
        loaded = 0
        batch_size = 200
        for rtype in rel_types:
            type_edges = [e for e in all_edges if e["type"] == rtype]
            if not type_edges:
                continue

            for i in range(0, len(type_edges), batch_size):
                batch = type_edges[i:i + batch_size]
                params = [
                    {
                        "source": e["source"],
                        "target": e["target"],
                        "context": e["context"],
                    }
                    for e in batch
                ]
                result = session.run(
                    f"""
                    UNWIND $batch AS e
                    MATCH (a:Remedy {{abbrev: e.source}})
                    MATCH (b:Remedy)
                    WHERE b.abbrev = e.target OR b.name = e.target
                    MERGE (a)-[r:{rtype}]->(b)
                    SET r.context = e.context, r.source = 'boericke'
                    RETURN count(*) AS cnt
                    """,
                    batch=params,
                )
                loaded += result.single()["cnt"]

        print(f"  Loaded {loaded} relationship edges")
        return loaded


# ─────────────────────────────────────────────────────────
# STEP 3: Tag seed remedies
# ─────────────────────────────────────────────────────────

def tag_seed_remedies(driver, dry_run: bool = False):
    """Tag remedies without a source property as source='seed'."""
    with driver.session() as session:
        result = session.run(
            """
            MATCH (r:Remedy)
            WHERE r.source IS NULL
            RETURN count(r) AS cnt
            """
        )
        count = result.single()["cnt"]
        print(f"  Untagged remedies: {count}")

        if dry_run:
            print(f"  [DRY RUN] Would tag {count} as source='seed'")
            return count

        if count > 0:
            session.run(
                """
                MATCH (r:Remedy)
                WHERE r.source IS NULL
                SET r.source = 'seed'
                """
            )
            print(f"  Tagged {count} remedies as source='seed'")
        return count


# ─────────────────────────────────────────────────────────
# STEP 4: Also update the parsed JSON with names
# ─────────────────────────────────────────────────────────

def update_parsed_json(name_map: dict[str, str]):
    """Patch names in the parsed JSON so future loads have correct names."""
    if not PARSED_FILE.exists():
        print("  [SKIP] No parsed data file")
        return

    with open(PARSED_FILE) as f:
        parsed = json.load(f)

    updated = 0
    for p in parsed:
        abbrev = p.get("abbrev", "").lower().strip()
        if not p.get("name", "").strip() and abbrev in name_map:
            p["name"] = name_map[abbrev]
            updated += 1

    with open(PARSED_FILE, "w") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)
    print(f"  Updated {updated} names in parsed JSON")


def update_scraped_json(name_map: dict[str, str]):
    """Patch names in the scraped JSON."""
    if not SCRAPED_FILE.exists():
        return

    with open(SCRAPED_FILE) as f:
        scraped = json.load(f)

    updated = 0
    for r in scraped:
        abbrev = r.get("abbrev", "").lower().strip()
        if not r.get("name", "").strip() and abbrev in name_map:
            r["name"] = name_map[abbrev]
            updated += 1

    with open(SCRAPED_FILE, "w") as f:
        json.dump(scraped, f, indent=2, ensure_ascii=False)
    print(f"  Updated {updated} names in scraped JSON")


# ─────────────────────────────────────────────────────────
# STEP 5: Report final stats
# ─────────────────────────────────────────────────────────

def report_stats(driver):
    """Print final graph statistics."""
    with driver.session() as session:
        print("\n" + "=" * 50)
        print("FINAL GRAPH STATISTICS")
        print("=" * 50)

        for label in ["Remedy", "Rubric", "Symptom"]:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) AS c")
            print(f"  {label:12s}: {result.single()['c']:,}")

        # Edge counts
        result = session.run(
            "MATCH ()-[r]->() RETURN type(r) AS t, count(r) AS c ORDER BY c DESC"
        )
        print("\n  Edges:")
        for rec in result:
            print(f"    {rec['t']:20s}: {rec['c']:,}")

        # Remedy name coverage
        result = session.run(
            """
            MATCH (r:Remedy)
            WHERE r.name IS NOT NULL AND r.name <> ''
            RETURN count(r) AS named,
                   count(r) AS total
            """
        )
        rec = result.single()
        result2 = session.run("MATCH (r:Remedy) RETURN count(r) AS total")
        total = result2.single()["total"]
        print(f"\n  Remedies with names: {rec['named']}/{total}")

        # Source breakdown
        result = session.run(
            """
            MATCH (r:Remedy)
            RETURN r.source AS source, count(r) AS cnt
            ORDER BY cnt DESC
            """
        )
        print("  By source:")
        for rec in result:
            print(f"    {str(rec['source']):12s}: {rec['cnt']}")


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Data quality cleanup")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without modifying data")
    parser.add_argument("--skip-index", action="store_true",
                        help="Skip re-fetching index pages (use cached names)")
    args = parser.parse_args()

    dry_run = args.dry_run

    driver = get_driver()

    try:
        print("=" * 50)
        print("DATA QUALITY CLEANUP")
        print("=" * 50)
        if dry_run:
            print("  *** DRY RUN MODE ***\n")

        # Step 1: Get name mapping
        print("\n[1/5] Fetching remedy names from index pages...")
        if args.skip_index:
            # Build from scraped JSON abbrevs — won't have names
            print("  [SKIP] Using cached names only")
            name_map = {}
        else:
            name_map = fetch_index_names()

        # Step 2: Populate names in Neo4j
        print("\n[2/5] Populating remedy names in Neo4j...")
        if name_map:
            populate_names(driver, name_map, dry_run=dry_run)
        else:
            print("  [SKIP] No name map available")

        # Step 3: Rebuild relationships
        print("\n[3/5] Rebuilding remedy relationships...")
        if name_map:
            rebuild_relationships(driver, name_map, dry_run=dry_run)
        else:
            print("  [SKIP] Need name map for relationship resolution")

        # Step 4: Tag seed remedies
        print("\n[4/5] Tagging seed remedies...")
        tag_seed_remedies(driver, dry_run=dry_run)

        # Step 5: Update JSON data files
        print("\n[5/5] Updating JSON data files...")
        if name_map and not dry_run:
            update_scraped_json(name_map)
            update_parsed_json(name_map)
        elif dry_run:
            print("  [DRY RUN] Would update scraped + parsed JSON files")
        else:
            print("  [SKIP] No name map")

        # Final report
        report_stats(driver)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
