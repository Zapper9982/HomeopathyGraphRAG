"""
Remedy parser — convert raw scraped Boericke data into structured profiles.

Extracts:
  - Individual symptoms per body-part section
  - Modalities (worse/better)
  - Relationships (antidotes, complementary, incompatible, compare)
  - Remedy characteristics (thermal state, thirst, desires/aversions)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedSymptom:
    """A single parsed symptom from a body-part section."""
    text: str
    section: str            # e.g., "mind", "head", "throat"
    modifiers: list[str] = field(default_factory=list)  # worse/better info
    is_keynote: bool = False  # strong/distinctive?


@dataclass
class ParsedModality:
    """A parsed modality (aggravation or amelioration)."""
    text: str
    direction: str   # "worse" or "better"


@dataclass
class ParsedRelationship:
    """A parsed remedy relationship."""
    related_remedy: str
    relationship_type: str  # "antidote", "complementary", "incompatible", "compare"
    notes: str = ""


@dataclass
class ParsedRemedyProfile:
    """Complete parsed profile for one remedy."""
    name: str
    abbrev: str
    common_name: str
    overview: str
    symptoms: list[ParsedSymptom] = field(default_factory=list)
    modalities: list[ParsedModality] = field(default_factory=list)
    relationships: list[ParsedRelationship] = field(default_factory=list)
    thermal_state: Optional[str] = None  # "hot", "cold", "ambithermal"
    thirst: Optional[str] = None  # "thirsty", "thirstless", "sips"
    desires: list[str] = field(default_factory=list)
    aversions: list[str] = field(default_factory=list)
    dose: str = ""
    source_url: str = ""


class RemedyParser:
    """Parse raw Boericke data into structured remedy profiles."""

    # ── section parsing ──────────────────────────────────
    SENTENCE_SPLIT = re.compile(r'(?<=[.;])\s+')

    # Keywords that indicate keynote symptoms (in Boericke, typically
    # descriptive phrases that are unique to a remedy)
    KEYNOTE_INDICATORS = [
        "characteristic", "peculiar", "marked", "great", "violent",
        "especially", "extremely",
    ]

    def parse(self, raw) -> ParsedRemedyProfile:
        """
        Parse a RemedyRawData into a ParsedRemedyProfile.

        Args:
            raw: A RemedyRawData instance from the scraper.
        """
        profile = ParsedRemedyProfile(
            name=self._clean_name(raw.name),
            abbrev=raw.abbrev,
            common_name=raw.common_name,
            overview=raw.overview,
            source_url=raw.url,
        )

        # Parse body-part sections into symptoms
        for section_name, section_text in raw.sections.items():
            symptoms = self._parse_section_symptoms(section_name, section_text)
            profile.symptoms.extend(symptoms)

        # Parse modalities
        if raw.modalities:
            profile.modalities = self._parse_modalities(raw.modalities)

        # Parse relationships
        if raw.relationships:
            profile.relationships = self._parse_relationships(raw.relationships)

        # Extract thermal state, thirst, desires/aversions from parsed data
        self._extract_characteristics(profile)

        # Store dose
        profile.dose = raw.dose

        return profile

    # ── name cleaning ────────────────────────────────────
    def _clean_name(self, raw_name: str) -> str:
        """Clean remedy name: 'BELLADONNA' -> 'Belladonna'."""
        if not raw_name:
            return ""
        # Handle names like "ACONITUM NAPELLUS"
        parts = raw_name.strip().split()
        cleaned = []
        for part in parts:
            if part.isupper() and len(part) > 1:
                cleaned.append(part.capitalize())
            else:
                cleaned.append(part)
        return " ".join(cleaned)

    # ── section → symptoms ───────────────────────────────
    def _parse_section_symptoms(
        self, section: str, text: str
    ) -> list[ParsedSymptom]:
        """Split a section's text into individual symptom entries."""
        if not text:
            return []

        # Boericke uses sentences/clauses separated by periods or semicolons
        fragments = self.SENTENCE_SPLIT.split(text)

        symptoms = []
        for frag in fragments:
            frag = frag.strip().rstrip(".")
            if not frag or len(frag) < 5:
                continue

            # Skip non-symptom fragments
            if self._is_noise(frag):
                continue

            modifiers = self._extract_modifiers(frag)
            is_keynote = any(
                kw in frag.lower() for kw in self.KEYNOTE_INDICATORS
            )

            symptoms.append(ParsedSymptom(
                text=frag,
                section=section,
                modifiers=modifiers,
                is_keynote=is_keynote,
            ))

        return symptoms

    def _is_noise(self, text: str) -> bool:
        """Filter out non-symptom text fragments."""
        lower = text.lower()
        noise_patterns = [
            "copyright", "médi-t", "boericke",
            "compare:", "antidote", "complementary",
            "dose:", "potency",
        ]
        return any(p in lower for p in noise_patterns)

    def _extract_modifiers(self, text: str) -> list[str]:
        """Extract worse/better modifiers from symptom text."""
        modifiers = []

        # Pattern: "worse <condition>" or "better <condition>"
        worse_match = re.findall(
            r'(?:worse|agg(?:ravat)?|<)\s+(.+?)(?:[;,.]|$)', text, re.IGNORECASE
        )
        for m in worse_match:
            modifiers.append(f"worse: {m.strip()}")

        better_match = re.findall(
            r'(?:better|amel(?:iorat)?|>)\s+(.+?)(?:[;,.]|$)', text, re.IGNORECASE
        )
        for m in better_match:
            modifiers.append(f"better: {m.strip()}")

        return modifiers

    # ── modalities ───────────────────────────────────────
    def _parse_modalities(self, text: str) -> list[ParsedModality]:
        """Parse the Modalities section into structured modalities."""
        modalities = []

        # Boericke format: "Worse, touch, jar, noise. Better, semi-erect."
        worse_match = re.search(
            r'[Ww]orse[,:\s]+(.+?)(?:\.\s*[Bb]etter|$)', text, re.DOTALL
        )
        better_match = re.search(
            r'[Bb]etter[,:\s]+(.+?)(?:\.\s*$|\.\s*[A-Z]|$)', text, re.DOTALL
        )

        if worse_match:
            items = self._split_modality_items(worse_match.group(1))
            for item in items:
                modalities.append(ParsedModality(text=item, direction="worse"))

        if better_match:
            items = self._split_modality_items(better_match.group(1))
            for item in items:
                modalities.append(ParsedModality(text=item, direction="better"))

        return modalities

    def _split_modality_items(self, text: str) -> list[str]:
        """Split 'touch, jar, noise, after noon' into individual items."""
        items = re.split(r'[,;]\s*', text)
        result = []
        for item in items:
            cleaned = item.strip().rstrip(".")
            if cleaned and len(cleaned) > 1:
                result.append(cleaned)
        return result

    # ── relationships ────────────────────────────────────
    RELATIONSHIP_PATTERNS = {
        "antidote": re.compile(
            r'[Aa]ntidotes?\s*(?:to\s+\w+)?\s*[:\s]+(.+?)(?:\.|$)',
            re.DOTALL,
        ),
        "complementary": re.compile(
            r'[Cc]omplementary\s*[:\s]+(.+?)(?:\.|$)',
            re.DOTALL,
        ),
        "incompatible": re.compile(
            r'[Ii]ncompatible\s*[:\s]+(.+?)(?:\.|$)',
            re.DOTALL,
        ),
        "compare": re.compile(
            r'[Cc]ompare\s*[:\s]+(.+?)(?:Antidote|Complementary|Incompatible|Dose|$)',
            re.DOTALL,
        ),
    }

    def _parse_relationships(self, text: str) -> list[ParsedRelationship]:
        """Parse the Relationship section into structured data."""
        relationships = []

        for rel_type, pattern in self.RELATIONSHIP_PATTERNS.items():
            match = pattern.search(text)
            if not match:
                continue
            raw = match.group(1).strip()
            # Split by semicolons or remedy abbreviations
            remedies = self._extract_remedy_names(raw)
            for remedy_name, notes in remedies:
                relationships.append(ParsedRelationship(
                    related_remedy=remedy_name,
                    relationship_type=rel_type,
                    notes=notes,
                ))

        return relationships

    def _extract_remedy_names(self, text: str) -> list[tuple[str, str]]:
        """
        Extract remedy names from relationship text.
        Returns list of (remedy_name, notes).
        """
        results = []

        # Split on semicolons first (each might be a separate remedy)
        segments = re.split(r'[;]\s*', text)

        for seg in segments:
            seg = seg.strip()
            if not seg or len(seg) < 2:
                continue

            # Try to extract remedy name — typically first word(s) before parenthesis
            # E.g., "Camph; Coff; Opium; Acon" or "Calc (contains lime)"
            name_match = re.match(
                r'([A-Z][a-z]+(?:\s+[a-z]+)?(?:\s+[A-Z][a-z]+)*)',
                seg,
            )
            if name_match:
                name = name_match.group(1).strip()
                notes = seg[name_match.end():].strip().strip("().- ")
                results.append((name, notes))

        return results

    # ── thermal & thirst extraction ──────────────────────
    THERMAL_COLD_KEYWORDS = [
        "chilly", "cold", "aversion to cold", "worse cold",
        "desire for warmth", "wraps up",
    ]
    THERMAL_HOT_KEYWORDS = [
        "hot patient", "warm-blooded", "worse heat", "desire for cold",
        "throws off covers", "aversion to heat",
    ]
    THIRST_KEYWORDS = {
        "thirsty": ["great thirst", "thirst for", "drinks large"],
        "thirstless": ["thirstless", "no thirst", "absence of thirst"],
        "sips": ["sips", "small quantities", "little and often"],
    }

    def _extract_characteristics(self, profile: ParsedRemedyProfile) -> None:
        """Extract thermal state, thirst, desires/aversions from profile."""
        all_text = profile.overview.lower()
        for sym in profile.symptoms:
            all_text += " " + sym.text.lower()
        for mod in profile.modalities:
            all_text += " " + mod.text.lower()

        # Thermal state
        cold_score = sum(1 for kw in self.THERMAL_COLD_KEYWORDS if kw in all_text)
        hot_score = sum(1 for kw in self.THERMAL_HOT_KEYWORDS if kw in all_text)
        if cold_score > hot_score:
            profile.thermal_state = "cold"
        elif hot_score > cold_score:
            profile.thermal_state = "hot"
        else:
            profile.thermal_state = "ambithermal"

        # Thirst
        for thirst_type, keywords in self.THIRST_KEYWORDS.items():
            if any(kw in all_text for kw in keywords):
                profile.thirst = thirst_type
                break

        # Desires and aversions from stomach section
        desire_pattern = re.compile(
            r'(?:desire|craving|wants|longs)\s+(?:for\s+)?(.+?)(?:[;,.]|$)',
            re.IGNORECASE,
        )
        aversion_pattern = re.compile(
            r'(?:aversion|averse)\s+(?:to\s+)?(.+?)(?:[;,.]|$)',
            re.IGNORECASE,
        )

        stomach_text = ""
        for sym in profile.symptoms:
            if sym.section == "stomach":
                stomach_text += " " + sym.text

        for m in desire_pattern.finditer(stomach_text):
            profile.desires.append(m.group(1).strip())
        for m in aversion_pattern.finditer(stomach_text):
            profile.aversions.append(m.group(1).strip())
