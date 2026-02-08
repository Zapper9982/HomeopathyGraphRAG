"""
Boericke's Materia Medica scraper.

Scrapes from homeoint.org (public-domain text, published 1927).

Structure:
  - Index pages: http://www.homeoint.org/books/boericmm/{letter}.htm
  - Remedy pages: http://www.homeoint.org/books/boericmm/{letter}/{abbrev}.htm

Each remedy page has sections:
  Mind, Head, Face, Eyes, Ears, Nose, Mouth, Throat, Stomach, Abdomen,
  Stools, Urine, Male, Female, Respiratory, Heart, Extremities, Back,
  Skin, Fever, Sleep, Modalities, Relationship, Dose
"""

from __future__ import annotations

import re
import string
from dataclasses import dataclass, field
from typing import Optional

from bs4 import BeautifulSoup, Tag

from data_pipeline.scrapers.base_scraper import BaseScraper

BASE_URL = "http://www.homeoint.org/books/boericmm"


@dataclass
class RemedyRawData:
    """Raw scraped data for one remedy."""
    url: str
    abbrev: str
    name: str
    common_name: str = ""
    overview: str = ""
    sections: dict[str, str] = field(default_factory=dict)
    modalities: str = ""
    relationships: str = ""
    dose: str = ""


class BoerickeScraper(BaseScraper):
    """Scrape Boericke's Materia Medica from homeoint.org."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # ── index scraping ───────────────────────────────────
    def get_remedy_urls(self, letters: Optional[str] = None) -> list[dict]:
        """
        Scrape index pages and return list of
        {"abbrev": "bell", "name": "BELLADONNA", "url": "http://..."}.

        Args:
            letters: Which letters to scrape (default: all a-z).
        """
        if letters is None:
            letters = string.ascii_lowercase

        all_remedies: list[dict] = []

        for letter in letters:
            url = f"{BASE_URL}/{letter}.htm"
            print(f"  Fetching index: {letter.upper()}...", end=" ", flush=True)
            try:
                html = self.fetch(url)
            except Exception as exc:
                print(f"SKIP ({exc})")
                continue

            soup = BeautifulSoup(html, "lxml")
            remedies = self._parse_index_page(soup, letter)
            all_remedies.extend(remedies)
            print(f"{len(remedies)} remedies")

        return all_remedies

    def _parse_index_page(self, soup: BeautifulSoup, letter: str) -> list[dict]:
        """Extract remedy links from an index page."""
        results = []
        # Links can be relative (b/bac.htm) or absolute (/books/boericmm/b/bac.htm)
        pattern = re.compile(
            rf"(?:.*/?){re.escape(letter)}/([a-z0-9_-]+)\.htm",
            re.IGNORECASE,
        )
        seen = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href", "")
            match = pattern.search(href)
            if not match:
                continue
            abbrev = match.group(1).lower()
            if abbrev in seen:
                continue
            seen.add(abbrev)

            # Resolve full URL
            if href.startswith("http"):
                full_url = href
            else:
                full_url = f"{BASE_URL}/{href}"

            # Try to get full name from the link text
            name = a_tag.get_text(strip=True).upper()

            results.append({
                "abbrev": abbrev,
                "name": name,
                "url": full_url,
            })

        return results

    # ── remedy page scraping ─────────────────────────────
    def scrape_remedy(self, remedy_info: dict) -> RemedyRawData:
        """Fetch and parse a single remedy page."""
        url = remedy_info["url"]
        html = self.fetch(url)
        soup = BeautifulSoup(html, "lxml")
        return self._parse_remedy_page(soup, remedy_info)

    def _parse_remedy_page(
        self, soup: BeautifulSoup, remedy_info: dict
    ) -> RemedyRawData:
        """Parse a Boericke remedy page into structured raw data."""

        raw = RemedyRawData(
            url=remedy_info["url"],
            abbrev=remedy_info["abbrev"],
            name=remedy_info.get("name", ""),
        )

        # Find the main content area — prefer body; blockquote on this
        # site only holds the page header, not remedy content
        body = soup.body
        if body is None:
            return raw

        text = body.get_text("\n", strip=False)
        lines = text.split("\n")

        # ── Extract remedy name + common name from first lines ──
        index_name = raw.name  # preserve name from index page
        extracted_name, raw.common_name = self._extract_title(lines)
        raw.name = extracted_name if extracted_name else index_name

        # ── Split text into sections by bold headers ────────
        sections = self._split_into_sections(body)
        
        # Store body-part sections
        body_sections = {
            "mind", "head", "face", "eyes", "ears", "nose", "mouth",
            "throat", "stomach", "abdomen", "stools", "stool", "urine",
            "male", "female", "respiratory", "heart", "extremities",
            "back", "skin", "fever", "sleep", "chest",
        }

        for section_name, section_text in sections.items():
            lower = section_name.lower().strip().rstrip(".")
            if lower in body_sections:
                raw.sections[lower] = section_text.strip()
            elif lower in ("modalities", "modality"):
                raw.modalities = section_text.strip()
            elif lower in ("relationship", "relationships"):
                raw.relationships = section_text.strip()
            elif lower == "dose":
                raw.dose = section_text.strip()

        # ── Overview = everything before the first section ──
        raw.overview = self._extract_overview(body, sections)

        return raw

    def _extract_title(self, lines: list[str]) -> tuple[str, str]:
        """Extract remedy name and common name from page lines.

        The remedy name appears as an ALL-CAPS line after the header block.
        On homeoint.org pages, the name can be 30+ lines in due to empty
        lines and non-breaking spaces between the header and the title.
        """
        name = ""
        common_name = ""
        # Header noise keywords to skip
        SKIP_UPPER = {"BOERICKE", "MATERIA", "MEDICA", "HOM"}
        for line in lines[:60]:
            clean = line.strip()
            if not clean:
                continue
            upper = clean.upper()
            # Skip header lines (HOMŒOPATHIC MATERIA MEDICA, by William BOERICKE, Presented by Médi-T)
            if any(kw in upper for kw in ("BOERICKE", "MATERIA MEDICA", "MEDI-T", "MÉDI-T", "HOMOE", "HOMŒ")):
                continue
            # Skip nav links / short words (Home, [A], etc.)
            if len(clean) <= 3:
                continue
            # ALL-CAPS line that doesn't contain header noise → remedy name
            if clean.isupper() and not any(kw in upper for kw in SKIP_UPPER):
                name = clean
                continue
            # First non-uppercase line after name → common name
            if name and not common_name and not clean.startswith("("):
                # Stop if we've hit section content (sentence-like text)
                if ".--" in clean or len(clean) > 80:
                    break
                common_name = clean
                break
        return name, common_name

    def _split_into_sections(self, body: Tag) -> dict[str, str]:
        """
        Split the page body into sections using bold tags as headers.
        Boericke pages use patterns like "Mind.--" as section markers.
        """
        sections: dict[str, str] = {}
        
        # Strategy: find all text, look for "SectionName.--" pattern
        full_text = body.get_text("\n", strip=False)
        
        # Pattern: word(s) followed by .-- (Boericke section delimiter)
        section_pattern = re.compile(
            r'\n\s*([A-Z][a-z]+(?:\s+[A-Za-z]+)?)\s*\.--',
        )
        
        matches = list(section_pattern.finditer(full_text))
        
        for i, match in enumerate(matches):
            section_name = match.group(1).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
            section_text = full_text[start:end].strip()
            # Clean up the text
            section_text = re.sub(r'\s+', ' ', section_text)
            sections[section_name] = section_text
        
        return sections

    def _extract_overview(
        self, body: Tag, sections: dict[str, str]
    ) -> str:
        """Extract the overview text (before first section)."""
        full_text = body.get_text("\n", strip=False)
        
        # Find where the first section starts
        section_pattern = re.compile(
            r'\n\s*[A-Z][a-z]+(?:\s+[A-Za-z]+)?\s*\.--',
        )
        match = section_pattern.search(full_text)
        if match:
            overview = full_text[:match.start()].strip()
        else:
            overview = ""
        
        # Clean: remove header noise
        lines = overview.split("\n")
        cleaned = []
        skip_patterns = [
            "HOMŒOPATHIC", "MATERIA MEDICA", "BOERICKE", "Médi-T",
            "Presented by", "H.I.", "MAIN", "Home",
        ]
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if any(p in stripped for p in skip_patterns):
                continue
            # Skip nav links
            if stripped.startswith("[") and stripped.endswith("]"):
                continue
            cleaned.append(stripped)
        
        # Skip the title lines (first 1-2 lines are remedy name)
        if len(cleaned) > 2:
            overview_text = " ".join(cleaned[2:])
        elif cleaned:
            overview_text = " ".join(cleaned)
        else:
            overview_text = ""
        
        return re.sub(r'\s+', ' ', overview_text).strip()

    # ── bulk scraping ────────────────────────────────────
    def scrape_all(
        self,
        letters: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[RemedyRawData]:
        """
        Scrape all remedies (or a subset) from Boericke's MM.

        Args:
            letters: Which index letters to process (default: all).
            limit: Max number of remedies to scrape (for testing).
        """
        print("=" * 60)
        print("PHASE 1: Collecting remedy URLs from index pages")
        print("=" * 60)
        remedy_list = self.get_remedy_urls(letters=letters)
        print(f"\nFound {len(remedy_list)} remedies total.\n")

        if limit:
            remedy_list = remedy_list[:limit]
            print(f"  (limited to {limit} for this run)\n")

        print("=" * 60)
        print("PHASE 2: Scraping individual remedy pages")
        print("=" * 60)

        results: list[RemedyRawData] = []
        for i, info in enumerate(remedy_list, 1):
            print(f"  [{i:3d}/{len(remedy_list)}] {info['abbrev']:<15s} ", end="", flush=True)
            try:
                raw = self.scrape_remedy(info)
                sections_found = len(raw.sections)
                print(f"✓ {sections_found} sections")
                results.append(raw)
            except Exception as exc:
                print(f"✗ Error: {exc}")

        print(f"\nSuccessfully scraped {len(results)}/{len(remedy_list)} remedies.")
        return results
