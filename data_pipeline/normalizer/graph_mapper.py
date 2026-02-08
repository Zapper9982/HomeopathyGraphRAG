"""
Graph mapper — normalise parsed remedy profiles into Neo4j-ready entities.

Maps ParsedRemedyProfile → graph nodes + edges matching the project schema:
  (:Symptom), (:Rubric), (:Remedy),
  (:Symptom)-[:BELONGS_TO]->(:Rubric),
  (:Remedy)-[:INDICATES]->(:Rubric),
  (:Remedy)-[:CONTRADICTS]->(:Remedy),
  (:Remedy)-[:CORRELATED_WITH]->(:Remedy),
  (:Remedy)-[:ANTIDOTES]->(:Remedy),
  (:Remedy)-[:COMPLEMENTARY]->(:Remedy),
  (:Remedy)-[:INCOMPATIBLE]->(:Remedy),
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Optional

from data_pipeline.parsers.remedy_parser import ParsedRemedyProfile, ParsedSymptom


# ── Graph entity dataclasses ────────────────────────────

@dataclass
class GraphSymptom:
    """A Symptom node for Neo4j."""
    id: str           # deterministic hash
    text: str
    category: str     # e.g., "mind", "head", "throat"
    source_remedy: str


@dataclass
class GraphRubric:
    """A Rubric node for Neo4j."""
    id: str
    text: str
    chapter: str      # body-part section mapped to Kent chapter


@dataclass
class GraphRemedy:
    """A Remedy node for Neo4j."""
    abbrev: str
    name: str
    common_name: str
    overview: str
    thermal_state: Optional[str] = None
    thirst: Optional[str] = None
    desires: list[str] = field(default_factory=list)
    aversions: list[str] = field(default_factory=list)
    dose: str = ""
    source_url: str = ""


@dataclass
class GraphEdge:
    """An edge between two nodes."""
    source_id: str
    target_id: str
    edge_type: str             # BELONGS_TO, INDICATES, CONTRADICTS, etc.
    properties: dict = field(default_factory=dict)


@dataclass
class GraphPayload:
    """Complete set of entities ready for Neo4j bulk load."""
    symptoms: list[GraphSymptom] = field(default_factory=list)
    rubrics: list[GraphRubric] = field(default_factory=list)
    remedies: list[GraphRemedy] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)

    def stats(self) -> dict:
        edge_counts = {}
        for e in self.edges:
            edge_counts[e.edge_type] = edge_counts.get(e.edge_type, 0) + 1
        return {
            "symptoms": len(self.symptoms),
            "rubrics": len(self.rubrics),
            "remedies": len(self.remedies),
            "edges": edge_counts,
        }


# ── Section → Kent Chapter mapping ──────────────────────
SECTION_TO_CHAPTER = {
    "mind": "Mind",
    "head": "Head",
    "face": "Face",
    "eyes": "Eyes",
    "ears": "Ears",
    "nose": "Nose",
    "mouth": "Mouth",
    "throat": "Throat",
    "stomach": "Stomach",
    "abdomen": "Abdomen",
    "stools": "Stool",
    "urine": "Urine",
    "male": "Male Genitalia",
    "female": "Female Genitalia",
    "respiratory": "Respiration",
    "heart": "Heart",
    "extremities": "Extremities",
    "back": "Back",
    "skin": "Skin",
    "fever": "Fever",
    "sleep": "Sleep",
    "generalities": "Generalities",
}


class GraphMapper:
    """Map parsed remedy profiles to graph entities."""

    def __init__(self):
        self._rubric_cache: dict[str, str] = {}   # text → rubric_id
        self._symptom_cache: dict[str, str] = {}   # text → symptom_id
        self._remedy_lookup: dict[str, str] = {}   # normalised name → abbrev

    def _build_remedy_lookup(self, profiles: list[ParsedRemedyProfile]) -> None:
        """Build a fuzzy name→abbrev lookup from all profiles."""
        for p in profiles:
            abbrev = p.abbrev.lower().strip()
            # Map abbrev to itself
            self._remedy_lookup[abbrev] = abbrev
            # Map full name
            if p.name:
                self._remedy_lookup[p.name.lower().strip()] = abbrev
                # Also map first word (common abbreviation pattern)
                first_word = p.name.split()[0].lower().strip() if p.name.split() else ""
                if first_word and len(first_word) > 2:
                    # Only set if not already taken by a more specific match
                    self._remedy_lookup.setdefault(first_word, abbrev)
            # Map common name
            if p.common_name:
                self._remedy_lookup[p.common_name.lower().strip()] = abbrev

    def _resolve_remedy(self, name: str) -> Optional[str]:
        """Resolve a remedy name/abbreviation to a known abbrev."""
        if not name:
            return None
        key = name.lower().strip()
        # Direct match
        if key in self._remedy_lookup:
            return self._remedy_lookup[key]
        # Try without trailing/leading punctuation
        cleaned = re.sub(r'[^a-z\s-]', '', key).strip()
        if cleaned in self._remedy_lookup:
            return self._remedy_lookup[cleaned]
        # Try first word only (e.g., "Calcarea Carbonica" → "calcarea")
        first = cleaned.split()[0] if cleaned.split() else ""
        if first and first in self._remedy_lookup:
            return self._remedy_lookup[first]
        return None

    def map_profile(self, profile: ParsedRemedyProfile) -> GraphPayload:
        """Map a single parsed profile to graph entities."""
        payload = GraphPayload()

        # 1. Create Remedy node
        remedy = GraphRemedy(
            abbrev=profile.abbrev,
            name=profile.name,
            common_name=profile.common_name,
            overview=profile.overview[:500],  # cap overview length
            thermal_state=profile.thermal_state,
            thirst=profile.thirst,
            desires=profile.desires,
            aversions=profile.aversions,
            dose=profile.dose,
            source_url=profile.source_url,
        )
        payload.remedies.append(remedy)

        # 2. Create Symptom + Rubric nodes from symptoms
        for sym in profile.symptoms:
            g_symptom, g_rubric, edges = self._map_symptom(sym, profile.abbrev)
            if g_symptom:
                payload.symptoms.append(g_symptom)
            if g_rubric:
                payload.rubrics.append(g_rubric)
            payload.edges.extend(edges)

        # 3. Create modality edges (as Symptom properties)
        for mod in profile.modalities:
            mod_symptom = GraphSymptom(
                id=self._make_id(f"mod_{profile.abbrev}_{mod.direction}_{mod.text}"),
                text=f"{mod.direction}: {mod.text}",
                category="modality",
                source_remedy=profile.abbrev,
            )
            payload.symptoms.append(mod_symptom)

        # 4. Create relationship edges
        for rel in profile.relationships:
            edge = self._map_relationship(profile.abbrev, rel)
            if edge:
                payload.edges.append(edge)

        return payload

    def map_all(self, profiles: list[ParsedRemedyProfile]) -> GraphPayload:
        """Map multiple profiles, deduplicating rubrics."""
        combined = GraphPayload()

        # Build name→abbrev lookup for relationship resolution
        self._build_remedy_lookup(profiles)

        for profile in profiles:
            p = self.map_profile(profile)
            combined.remedies.extend(p.remedies)
            combined.symptoms.extend(p.symptoms)
            combined.edges.extend(p.edges)

            # Deduplicate rubrics
            for rub in p.rubrics:
                if rub.id not in self._rubric_cache:
                    self._rubric_cache[rub.id] = rub.text
                    combined.rubrics.append(rub)

        return combined

    # ── internal ─────────────────────────────────────────
    def _map_symptom(
        self, sym: ParsedSymptom, remedy_abbrev: str
    ) -> tuple[Optional[GraphSymptom], Optional[GraphRubric], list[GraphEdge]]:
        """Map a parsed symptom to Symptom node, Rubric node, and edges."""
        edges: list[GraphEdge] = []

        # Build a rubric from the symptom text (generalized)
        rubric_text = self._generalize_to_rubric(sym.text, sym.section)
        chapter = SECTION_TO_CHAPTER.get(sym.section, "Generalities")
        rubric_id = self._make_id(f"rubric_{chapter}_{rubric_text}")

        rubric = GraphRubric(id=rubric_id, text=rubric_text, chapter=chapter)

        # Build symptom node
        symptom_id = self._make_id(f"sym_{remedy_abbrev}_{sym.section}_{sym.text[:80]}")
        symptom = GraphSymptom(
            id=symptom_id,
            text=sym.text,
            category=sym.section,
            source_remedy=remedy_abbrev,
        )

        # Symptom -[:BELONGS_TO]-> Rubric
        edges.append(GraphEdge(
            source_id=symptom_id,
            target_id=rubric_id,
            edge_type="BELONGS_TO",
        ))

        # Remedy -[:INDICATES]-> Rubric
        grade = 3 if sym.is_keynote else 2  # 3=keynote, 2=confirmed, 1=minor
        edges.append(GraphEdge(
            source_id=remedy_abbrev,
            target_id=rubric_id,
            edge_type="INDICATES",
            properties={"grade": grade, "source": "boericke"},
        ))

        return symptom, rubric, edges

    def _generalize_to_rubric(self, text: str, section: str) -> str:
        """
        Generalise a remedy-specific symptom into a rubric.

        E.g., "Violent headache with throbbing in temples" →
              "Headache, violent, throbbing, temples"
        """
        # Lowercase, strip excessive words
        t = text.lower().strip()
        # Remove very common filler
        fillers = ["very", "quite", "rather", "somewhat", "with"]
        for f in fillers:
            t = re.sub(rf'\b{f}\b', '', t)
        # Compact whitespace
        t = re.sub(r'\s+', ' ', t).strip()
        # Cap length
        if len(t) > 120:
            t = t[:120].rsplit(' ', 1)[0]
        return t

    def _map_relationship(
        self, source_abbrev: str, rel
    ) -> Optional[GraphEdge]:
        """Map a parsed relationship to a graph edge."""
        type_map = {
            "antidote": "ANTIDOTES",
            "complementary": "COMPLEMENTARY",
            "incompatible": "INCOMPATIBLE",
            "compare": "CORRELATED_WITH",
            "follows_well": "FOLLOWS_WELL",
            "inimical": "INCOMPATIBLE",
        }
        edge_type = type_map.get(rel.relationship_type, "CORRELATED_WITH")

        # Resolve target remedy to a known abbreviation
        target = self._resolve_remedy(rel.related_remedy)
        if not target:
            # Fall back to raw name — Neo4j loader will try name match
            target = rel.related_remedy

        return GraphEdge(
            source_id=source_abbrev,
            target_id=target,
            edge_type=edge_type,
            properties={"context": rel.notes, "source": "boericke"},
        )

    @staticmethod
    def _make_id(seed: str) -> str:
        """Create a deterministic short ID from a seed string."""
        return hashlib.sha256(seed.encode()).hexdigest()[:16]
