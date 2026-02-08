#!/usr/bin/env python3
"""
run_pipeline.py — Materia Medica → Neo4j pipeline orchestrator.

Usage:
    python -m data_pipeline.run_pipeline scrape   [--letters abc] [--limit 5]
    python -m data_pipeline.run_pipeline parse     [--input scraped.json]
    python -m data_pipeline.run_pipeline load      [--input parsed.json] [--dry-run]
    python -m data_pipeline.run_pipeline full      [--letters abc] [--limit 5] [--dry-run]
    python -m data_pipeline.run_pipeline stats
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import asdict
from pathlib import Path

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

from data_pipeline.scrapers.boericke_scraper import BoerickeScraper
from data_pipeline.parsers.remedy_parser import RemedyParser
from data_pipeline.parsers.relationship_extractor import RelationshipExtractor
from data_pipeline.normalizer.graph_mapper import GraphMapper
from data_pipeline.storage.neo4j_loader import Neo4jLoader

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("pipeline")

DATA_DIR = Path(__file__).resolve().parent / "data"
SCRAPED_FILE = DATA_DIR / "scraped_remedies.json"
PARSED_FILE = DATA_DIR / "parsed_remedies.json"


# ── STEP 1: Scrape ──────────────────────────────────────

def step_scrape(letters: str | None = None, limit: int | None = None) -> list[dict]:
    """Scrape Boericke's Materia Medica from homeoint.org."""
    logger.info("=== STEP 1: SCRAPING ===")
    scraper = BoerickeScraper(delay_seconds=1.5)

    letter_list = list(letters) if letters else None
    raw_remedies = scraper.scrape_all(letters=letter_list, limit=limit)

    logger.info("Scraped %d remedies", len(raw_remedies))

    # Serialize to JSON
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    serialized = []
    for r in raw_remedies:
        serialized.append(asdict(r))

    with open(SCRAPED_FILE, "w") as f:
        json.dump(serialized, f, indent=2, ensure_ascii=False)
    logger.info("Saved scraped data to %s", SCRAPED_FILE)

    return serialized


# ── STEP 2: Parse ────────────────────────────────────────

def step_parse(input_file: Path | None = None) -> list[dict]:
    """Parse raw scraped data into structured profiles."""
    logger.info("=== STEP 2: PARSING ===")

    src = input_file or SCRAPED_FILE
    if not src.exists():
        logger.error("No scraped data found at %s. Run 'scrape' first.", src)
        sys.exit(1)

    with open(src) as f:
        raw_list = json.load(f)

    parser = RemedyParser()
    rel_extractor = RelationshipExtractor()

    parsed_profiles = []
    for raw_dict in raw_list:
        # Reconstruct a minimal object for the parser
        raw_obj = _dict_to_raw(raw_dict)
        profile = parser.parse(raw_obj)

        # Deeper relationship extraction (replaces basic parser results)
        if raw_dict.get("relationships"):
            rels = rel_extractor.extract_all(
                raw_dict["abbrev"], raw_dict["relationships"]
            )
            if rels:
                from data_pipeline.parsers.remedy_parser import ParsedRelationship
                # Replace with deeper-extracted relationships (deduplicated)
                seen = set()
                merged = []
                for r in rels:
                    key = (r.target_remedy.lower(), r.relation_type)
                    if key not in seen:
                        seen.add(key)
                        merged.append(ParsedRelationship(
                            related_remedy=r.target_remedy,
                            relationship_type=r.relation_type,
                            notes=r.context,
                        ))
                profile.relationships = merged

        parsed_profiles.append(profile)

    logger.info("Parsed %d profiles", len(parsed_profiles))
    _log_parse_summary(parsed_profiles)

    # Serialize
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    serialized = []
    for p in parsed_profiles:
        serialized.append(_profile_to_dict(p))

    with open(PARSED_FILE, "w") as f:
        json.dump(serialized, f, indent=2, ensure_ascii=False)
    logger.info("Saved parsed data to %s", PARSED_FILE)

    return serialized


# ── STEP 3: Load ─────────────────────────────────────────

def step_load(input_file: Path | None = None, dry_run: bool = False) -> None:
    """Load parsed profiles into Neo4j."""
    logger.info("=== STEP 3: LOADING INTO NEO4J ===")

    src = input_file or PARSED_FILE
    if not src.exists():
        logger.error("No parsed data found at %s. Run 'parse' first.", src)
        sys.exit(1)

    with open(src) as f:
        parsed_list = json.load(f)

    # Reconstruct profiles
    from data_pipeline.parsers.remedy_parser import (
        ParsedRemedyProfile, ParsedSymptom, ParsedModality, ParsedRelationship,
    )
    profiles = []
    for d in parsed_list:
        p = ParsedRemedyProfile(
            name=d["name"],
            abbrev=d["abbrev"],
            common_name=d.get("common_name", ""),
            overview=d.get("overview", ""),
            symptoms=[ParsedSymptom(**s) for s in d.get("symptoms", [])],
            modalities=[ParsedModality(**m) for m in d.get("modalities", [])],
            relationships=[ParsedRelationship(**r) for r in d.get("relationships", [])],
            thermal_state=d.get("thermal_state"),
            thirst=d.get("thirst"),
            desires=d.get("desires", []),
            aversions=d.get("aversions", []),
            dose=d.get("dose", ""),
            source_url=d.get("source_url", ""),
        )
        profiles.append(p)

    # Map to graph entities
    mapper = GraphMapper()
    payload = mapper.map_all(profiles)

    logger.info("Graph payload: %s", payload.stats())

    if dry_run:
        logger.info("[DRY RUN] Would load the above into Neo4j")
        return

    # Load
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "homeopathy_graph_2026")

    loader = Neo4jLoader(uri=uri, user=user, password=password)
    try:
        loader.ensure_constraints()
        stats = loader.load(payload)
        logger.info("Load result: %s", stats)
    finally:
        loader.close()


# ── STEP 4: Stats ────────────────────────────────────────

def step_stats() -> None:
    """Print statistics about scraped/parsed data and Neo4j state."""
    logger.info("=== DATA PIPELINE STATS ===")

    if SCRAPED_FILE.exists():
        with open(SCRAPED_FILE) as f:
            scraped = json.load(f)
        logger.info("Scraped remedies: %d", len(scraped))
    else:
        logger.info("No scraped data found")

    if PARSED_FILE.exists():
        with open(PARSED_FILE) as f:
            parsed = json.load(f)
        total_symptoms = sum(len(p.get("symptoms", [])) for p in parsed)
        total_modalities = sum(len(p.get("modalities", [])) for p in parsed)
        total_rels = sum(len(p.get("relationships", [])) for p in parsed)
        logger.info(
            "Parsed: %d profiles, %d symptoms, %d modalities, %d relationships",
            len(parsed), total_symptoms, total_modalities, total_rels,
        )
    else:
        logger.info("No parsed data found")

    # Neo4j counts
    try:
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "homeopathy_graph_2026")
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            for label in ["Remedy", "Rubric", "Symptom"]:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) AS c")
                c = result.single()["c"]
                logger.info("Neo4j %s nodes: %d", label, c)
            # Count edges
            result = session.run(
                "MATCH ()-[r]->() RETURN type(r) AS t, count(r) AS c ORDER BY c DESC"
            )
            for rec in result:
                logger.info("Neo4j edge [:%s]: %d", rec["t"], rec["c"])
        driver.close()
    except Exception as exc:
        logger.warning("Could not query Neo4j: %s", exc)


# ── helpers ──────────────────────────────────────────────

class _RawProxy:
    """Minimal proxy to make a dict look like RemedyRawData for the parser."""
    def __init__(self, d: dict):
        self.url = d.get("url", "")
        self.abbrev = d.get("abbrev", "")
        self.name = d.get("name", "")
        self.common_name = d.get("common_name", "")
        self.overview = d.get("overview", "")
        self.sections = d.get("sections", {})
        self.modalities = d.get("modalities", "")
        self.relationships = d.get("relationships", "")
        self.dose = d.get("dose", "")


def _dict_to_raw(d: dict):
    return _RawProxy(d)


def _profile_to_dict(profile) -> dict:
    """Serialize a ParsedRemedyProfile to a JSON-safe dict."""
    return {
        "name": profile.name,
        "abbrev": profile.abbrev,
        "common_name": profile.common_name,
        "overview": profile.overview,
        "symptoms": [
            {"text": s.text, "section": s.section,
             "modifiers": s.modifiers, "is_keynote": s.is_keynote}
            for s in profile.symptoms
        ],
        "modalities": [
            {"text": m.text, "direction": m.direction}
            for m in profile.modalities
        ],
        "relationships": [
            {"related_remedy": r.related_remedy,
             "relationship_type": r.relationship_type,
             "notes": getattr(r, "notes", "")}
            for r in profile.relationships
            if r is not None
        ],
        "thermal_state": profile.thermal_state,
        "thirst": profile.thirst,
        "desires": profile.desires,
        "aversions": profile.aversions,
        "dose": profile.dose,
        "source_url": profile.source_url,
    }


def _log_parse_summary(profiles) -> None:
    total_symptoms = sum(len(p.symptoms) for p in profiles)
    total_mods = sum(len(p.modalities) for p in profiles)
    total_rels = sum(len(p.relationships) for p in profiles)
    thermal = {"hot": 0, "cold": 0, "ambithermal": 0}
    for p in profiles:
        if p.thermal_state in thermal:
            thermal[p.thermal_state] += 1
    logger.info(
        "Summary: %d profiles | %d symptoms | %d modalities | %d relationships",
        len(profiles), total_symptoms, total_mods, total_rels,
    )
    logger.info("Thermal: %s", thermal)


# ── CLI ──────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Materia Medica → Neo4j data pipeline"
    )
    parser.add_argument(
        "command",
        choices=["scrape", "parse", "load", "full", "stats"],
        help="Pipeline step to run",
    )
    parser.add_argument("--letters", type=str, default=None,
                        help="Limit scraping to these letters (e.g., 'ab')")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max remedies to scrape per letter")
    parser.add_argument("--input", type=str, default=None,
                        help="Input file path (overrides default)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't write to Neo4j")

    args = parser.parse_args()
    input_path = Path(args.input) if args.input else None

    t0 = time.time()

    if args.command == "scrape":
        step_scrape(letters=args.letters, limit=args.limit)

    elif args.command == "parse":
        step_parse(input_file=input_path)

    elif args.command == "load":
        step_load(input_file=input_path, dry_run=args.dry_run)

    elif args.command == "full":
        step_scrape(letters=args.letters, limit=args.limit)
        step_parse()
        step_load(dry_run=args.dry_run)

    elif args.command == "stats":
        step_stats()

    elapsed = time.time() - t0
    logger.info("Pipeline finished in %.1fs", elapsed)


if __name__ == "__main__":
    main()
