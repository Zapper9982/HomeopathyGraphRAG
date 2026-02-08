"""
Re-extract full remedy names from cached HTML pages.

Reads the disk cache, applies the fixed _extract_title() logic,
and updates Neo4j + JSON data files with proper full names
(e.g. "Belladonna" instead of "Bell").
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup

# ── paths ────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = ROOT / "data_pipeline" / ".cache"
DATA_DIR = ROOT / "data_pipeline" / "data"
SCRAPED_JSON = DATA_DIR / "scraped_remedies.json"
PARSED_JSON = DATA_DIR / "parsed_remedies.json"

# ── Header noise keywords ────────────────────────────────
HEADER_NOISE = ("BOERICKE", "MATERIA MEDICA", "MEDI-T", "MÉDI-T", "HOMOE", "HOMŒ")
SKIP_UPPER = {"BOERICKE", "MATERIA", "MEDICA", "HOM"}


def extract_title(lines: list[str]) -> tuple[str, str]:
    """Fixed title extraction — scans 60 lines with better filtering."""
    name = ""
    common_name = ""
    for line in lines[:60]:
        clean = line.strip()
        if not clean:
            continue
        upper = clean.upper()
        if any(kw in upper for kw in HEADER_NOISE):
            continue
        if len(clean) <= 3:
            continue
        if clean.isupper() and not any(kw in upper for kw in SKIP_UPPER):
            name = clean
            continue
        if name and not common_name and not clean.startswith("("):
            if ".--" in clean or len(clean) > 80:
                break
            common_name = clean
            break
    return name, common_name


def title_case_name(name: str) -> str:
    """Convert ALL-CAPS remedy name to proper title case.
    
    'ACONITUM NAPELLUS' → 'Aconitum Napellus'
    'NUX VOMICA' → 'Nux Vomica'
    """
    return name.strip().title()


def build_url_to_abbrev(scraped: list[dict]) -> dict[str, str]:
    """Map remedy URL → abbreviation."""
    return {r["url"]: r["abbrev"] for r in scraped if r.get("url")}


def cache_key(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def main():
    dry_run = "--dry-run" in sys.argv

    print("=" * 50)
    print("RE-EXTRACT FULL REMEDY NAMES FROM CACHE")
    print("=" * 50)
    if dry_run:
        print("  *** DRY RUN ***\n")

    # Load current scraped data
    with open(SCRAPED_JSON) as f:
        scraped = json.load(f)
    print(f"Loaded {len(scraped)} remedies from scraped JSON")

    # Build URL → cache mapping
    url_map = build_url_to_abbrev(scraped)

    # Extract names from cached pages
    extracted = {}  # abbrev → (full_name, common_name)
    missing_cache = 0
    empty_extract = 0

    for remedy in scraped:
        abbrev = remedy["abbrev"]
        url = remedy.get("url", "")
        if not url:
            continue

        html_path = CACHE_DIR / f"{cache_key(url)}.html"
        if not html_path.exists():
            missing_cache += 1
            continue

        html = html_path.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(html, "lxml")
        body = soup.body
        if not body:
            empty_extract += 1
            continue

        text = body.get_text("\n", strip=False)
        lines = text.split("\n")
        raw_name, common = extract_title(lines)

        if raw_name:
            full_name = title_case_name(raw_name)
            extracted[abbrev] = (full_name, common.strip())
        else:
            empty_extract += 1

    print(f"\nExtraction results:")
    print(f"  Full names extracted: {len(extracted)}")
    print(f"  Missing from cache:  {missing_cache}")
    print(f"  Empty extraction:    {empty_extract}")

    # Show samples
    samples = list(extracted.items())[:10]
    print(f"\n  Samples:")
    for abbrev, (name, common) in samples:
        common_str = f" ({common})" if common else ""
        print(f"    {abbrev:15s} → {name}{common_str}")

    # Check well-known remedies
    well_known = ["bell", "acon", "ars", "bry", "nux-v", "puls", "sulph", "lyc", "phos", "sep"]
    print(f"\n  Well-known remedies:")
    for abbrev in well_known:
        if abbrev in extracted:
            name, common = extracted[abbrev]
            common_str = f" ({common})" if common else ""
            print(f"    {abbrev:10s} → {name}{common_str}")
        else:
            print(f"    {abbrev:10s} → NOT FOUND")

    if dry_run:
        print("\n[DRY RUN] Would update scraped JSON, parsed JSON, and Neo4j.")
        return

    # ── Update scraped JSON ──────────────────────────────
    updated_s = 0
    for remedy in scraped:
        abbrev = remedy["abbrev"]
        if abbrev in extracted:
            name, common = extracted[abbrev]
            remedy["name"] = name
            remedy["common_name"] = common
            updated_s += 1

    with open(SCRAPED_JSON, "w") as f:
        json.dump(scraped, f, indent=2, ensure_ascii=False)
    print(f"\nUpdated {updated_s} names in scraped JSON")

    # ── Update parsed JSON ───────────────────────────────
    with open(PARSED_JSON) as f:
        parsed = json.load(f)
    updated_p = 0
    for profile in parsed:
        abbrev = profile["abbrev"]
        if abbrev in extracted:
            name, common = extracted[abbrev]
            profile["name"] = name
            if "common_name" in profile:
                profile["common_name"] = common
            updated_p += 1

    with open(PARSED_JSON, "w") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)
    print(f"Updated {updated_p} names in parsed JSON")

    # ── Update Neo4j ─────────────────────────────────────
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "homeopathy_graph_2026"),
        )
        with driver.session() as session:
            count = 0
            for abbrev, (name, common) in extracted.items():
                result = session.run(
                    """
                    MATCH (r:Remedy {abbrev: $abbrev})
                    SET r.name = $name, r.common_name = $common
                    RETURN count(r) AS c
                    """,
                    abbrev=abbrev, name=name, common=common,
                )
                count += result.single()["c"]
            print(f"Updated {count} remedy names in Neo4j")
        driver.close()
    except Exception as e:
        print(f"Neo4j update failed: {e}")

    # ── Final stats ──────────────────────────────────────
    with open(SCRAPED_JSON) as f:
        data = json.load(f)
    short = sum(1 for r in data if r.get("name", "").strip() and len(r["name"]) < 10)
    full = sum(1 for r in data if r.get("name", "").strip() and len(r["name"]) >= 10)
    empty = sum(1 for r in data if not r.get("name", "").strip())
    print(f"\nFinal name quality:")
    print(f"  Full names (>=10 chars): {full}")
    print(f"  Short names (<10 chars): {short}")
    print(f"  Empty names:             {empty}")


if __name__ == "__main__":
    main()
