"""
Relationship extractor — deeper parsing of the Relationship section.

Handles Boericke's relationship encoding:
  Compare: Remedy1; Remedy2 (context)
  Antidotes: Rem1, Rem2
  Complementary: Rem1
  Incompatible: Rem1
  Follows well: Rem1
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ExtractedRelation:
    """A typed relationship between two remedies."""
    source_remedy: str
    target_remedy: str
    relation_type: str  # antidote, complementary, incompatible, compare, follows_well, inimical
    context: str = ""
    bidirectional: bool = False


class RelationshipExtractor:
    """
    Extract remedy-to-remedy relationships from Boericke text.

    Goes beyond simple regex — handles multi-sentence relationship blocks.
    """

    # Canonical relationship block headers
    BLOCK_PATTERNS = [
        ("compare",        re.compile(r'[Cc]ompare\s*[:\-]?\s*', re.DOTALL)),
        ("antidote",       re.compile(r'[Aa]ntidotes?\s*(?:to\s+it)?\s*[:\-]?\s*', re.DOTALL)),
        ("complementary",  re.compile(r'[Cc]omplementary\s*[:\-]?\s*', re.DOTALL)),
        ("incompatible",   re.compile(r'[Ii]ncompatible\s*[:\-]?\s*', re.DOTALL)),
        ("follows_well",   re.compile(r'[Ff]ollows\s+well\s*[:\-]?\s*', re.DOTALL)),
        ("inimical",       re.compile(r'[Ii]nimical\s*[:\-]?\s*', re.DOTALL)),
    ]

    # Common remedy abbreviations used in Boericke
    KNOWN_ABBREVIATIONS: dict[str, str] = {
        "Acon": "Aconitum Napellus",
        "Ars": "Arsenicum Album",
        "Bell": "Belladonna",
        "Bry": "Bryonia",
        "Calc": "Calcarea Carbonica",
        "Cham": "Chamomilla",
        "Chin": "China Officinalis",
        "Coff": "Coffea Cruda",
        "Gels": "Gelsemium",
        "Hep": "Hepar Sulph",
        "Ign": "Ignatia",
        "Lach": "Lachesis",
        "Lyc": "Lycopodium",
        "Merc": "Mercurius",
        "Nat mur": "Natrum Muriaticum",
        "Nit ac": "Nitricum Acidum",
        "Nux": "Nux Vomica",
        "Phos": "Phosphorus",
        "Puls": "Pulsatilla",
        "Rhus": "Rhus Tox",
        "Sep": "Sepia",
        "Sil": "Silicea",
        "Sulph": "Sulphur",
        "Thuj": "Thuja",
        "Apis": "Apis Mellifica",
        "Arg nit": "Argentum Nitricum",
        "Camph": "Camphora",
        "Opium": "Opium",
        "Caust": "Causticum",
        "Con": "Conium",
        "Dig": "Digitalis",
        "Dulc": "Dulcamara",
        "Graph": "Graphites",
        "Kali carb": "Kali Carbonicum",
        "Led": "Ledum",
        "Mag carb": "Magnesia Carbonica",
        "Nat carb": "Natrum Carbonicum",
        "Plat": "Platinum",
        "Pod": "Podophyllum",
        "Stram": "Stramonium",
        "Verat": "Veratrum Album",
        "Zinc": "Zincum Metallicum",
    }

    def extract_all(
        self, source_remedy: str, relationship_text: str
    ) -> list[ExtractedRelation]:
        """
        Extract all relationships from a remedy's Relationship section.

        Args:
            source_remedy: Name/abbreviation of the source remedy.
            relationship_text: The raw text from the Relationship section.
        """
        if not relationship_text:
            return []

        relations: list[ExtractedRelation] = []

        # Split text into typed blocks
        blocks = self._split_into_blocks(relationship_text)

        for rel_type, block_text in blocks:
            remedies = self._extract_remedies_from_block(block_text)
            for remedy_name, context in remedies:
                bidirectional = rel_type in ("complementary", "incompatible", "inimical")
                relations.append(ExtractedRelation(
                    source_remedy=source_remedy,
                    target_remedy=remedy_name,
                    relation_type=rel_type,
                    context=context,
                    bidirectional=bidirectional,
                ))

        return relations

    def normalize_remedy_name(self, name: str) -> str:
        """Expand abbreviation to full remedy name if known."""
        name = name.strip()
        # Exact match
        if name in self.KNOWN_ABBREVIATIONS:
            return self.KNOWN_ABBREVIATIONS[name]
        # Case-insensitive
        for abbrev, full in self.KNOWN_ABBREVIATIONS.items():
            if name.lower() == abbrev.lower():
                return full
        return name

    # ── internal ─────────────────────────────────────────
    def _split_into_blocks(
        self, text: str
    ) -> list[tuple[str, str]]:
        """
        Split relationship text into (type, content) blocks.

        Uses header patterns to identify where each block starts.
        """
        # Find all header positions
        headers: list[tuple[int, int, str]] = []  # (start, end, type)

        for rel_type, pattern in self.BLOCK_PATTERNS:
            for m in pattern.finditer(text):
                headers.append((m.start(), m.end(), rel_type))

        if not headers:
            # No headers found — treat entire text as "compare"
            return [("compare", text)]

        # Sort by position
        headers.sort(key=lambda x: x[0])

        blocks: list[tuple[str, str]] = []
        for i, (start, end, rel_type) in enumerate(headers):
            # Content runs from end of this header to start of next header
            if i + 1 < len(headers):
                content = text[end:headers[i + 1][0]]
            else:
                content = text[end:]
            content = content.strip().rstrip(".")
            if content:
                blocks.append((rel_type, content))

        return blocks

    def _extract_remedies_from_block(
        self, text: str
    ) -> list[tuple[str, str]]:
        """
        Extract remedy names and optional context from a block of text.

        Handles:
          "Acon; Bry; Gels"
          "Acon, Bry (headache), Gels"
          "Aconitum Napellus"
        """
        results: list[tuple[str, str]] = []

        # Split on semicolons first, then commas for shorter segments
        segments = re.split(r'[;]\s*', text)

        for seg in segments:
            seg = seg.strip()
            if not seg or len(seg) < 2:
                continue

            # Try to find remedy names separated by commas
            sub_segments = self._smart_comma_split(seg)

            for sub in sub_segments:
                sub = sub.strip()
                if not sub or len(sub) < 2:
                    continue

                # Extract name and parenthetical context
                paren_match = re.match(
                    r'([^(]+?)(?:\s*\((.+?)\))?\s*$', sub
                )
                if paren_match:
                    name = paren_match.group(1).strip()
                    context = paren_match.group(2) or ""
                else:
                    name = sub
                    context = ""

                # Validate it looks like a remedy name
                if self._looks_like_remedy(name):
                    normalized = self.normalize_remedy_name(name)
                    results.append((normalized, context.strip()))

        return results

    def _smart_comma_split(self, text: str) -> list[str]:
        """
        Split by commas but only if fragments look like remedy names.
        Keeps context phrases intact.
        """
        parts = text.split(",")
        if len(parts) <= 1:
            return [text]

        # Check if comma-separated parts look like remedy names
        possible_remedies = []
        non_remedy_parts = []

        for part in parts:
            part = part.strip()
            if self._looks_like_remedy(part.split("(")[0].strip()):
                if non_remedy_parts:
                    # Attach accumulated non-remedy text as context to last remedy
                    if possible_remedies:
                        last = possible_remedies[-1]
                        ctx = ", ".join(non_remedy_parts)
                        possible_remedies[-1] = f"{last} ({ctx})"
                    non_remedy_parts = []
                possible_remedies.append(part)
            else:
                non_remedy_parts.append(part)

        # Attach trailing non-remedy parts
        if non_remedy_parts and possible_remedies:
            last = possible_remedies[-1]
            ctx = ", ".join(non_remedy_parts)
            possible_remedies[-1] = f"{last} ({ctx})"

        return possible_remedies if possible_remedies else [text]

    def _looks_like_remedy(self, name: str) -> bool:
        """Check if a string looks like a remedy name/abbreviation."""
        if not name:
            return False
        # Must start with uppercase
        if not name[0].isupper():
            return False
        # Should be relatively short (remedy names/abbrevs)
        if len(name) > 40:
            return False
        # Should not be a common English word
        noise = {
            "The", "Also", "Compare", "Antidote", "Complementary",
            "Incompatible", "Dose", "Follows", "Similar", "Like",
            "Before", "After", "See", "Used", "Very", "Where",
            "When", "Both", "Each", "Make", "This", "That",
        }
        first_word = name.split()[0] if name.split() else name
        if first_word in noise:
            return False
        return True
