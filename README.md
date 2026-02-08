# Graph-RAG Clinical Decision Support — Enhanced

A next-generation **Graph-RAG clinical decision support system for homeopathy** that combines a Neo4j knowledge graph with four advanced intelligence layers that go **beyond what a senior human practitioner can do**.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENHANCED PIPELINE                            │
│                                                                 │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────────────┐    │
│  │ LLM      │──▸│ Graph-Based  │──▸│ LLM Explanation      │    │
│  │ Symptom  │   │ Remedy       │   │ (graph-grounded      │    │
│  │ Extract  │   │ Ranking      │   │  results only)       │    │
│  └──────────┘   └──────┬───────┘   └──────────────────────┘    │
│                        │                                        │
│        ┌───────────────┼───────────────┐                        │
│        ▼               ▼               ▼               ▼        │
│  ┌───────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │RELIABILITY│  │ UNCERTAINTY│  │  TEMPORAL   │  │  RARE    │  │
│  │Contra-    │  │ Bootstrap  │  │  Case       │  │  PATTERN │  │
│  │diction    │  │ Confidence │  │  Evolution  │  │  MINING  │  │
│  │Detection  │  │ Intervals  │  │  Reasoning  │  │  Engine  │  │
│  └───────────┘  └────────────┘  └────────────┘  └──────────┘  │
│                                                                 │
│  ALL INTELLIGENCE LAYERS ARE PURELY ALGORITHMIC / GRAPH-BASED   │
│  LLMs NEVER invent, override, or resolve — only structure      │
│  input and explain graph-derived results.                      │
└─────────────────────────────────────────────────────────────────┘
```

## What Can This System Do That A Senior Homeopath Cannot?

| Capability | Human Expert | This System |
|---|---|---|
| **Temporal Memory** | Relies on notes and recall | Graph-diff between time-indexed snapshots; detects suppression patterns across hundreds of cases |
| **Contradiction Detection** | Subjective, may miss subtle conflicts | Systematic traversal of all CONTRADICTS edges with quantified strength |
| **Uncertainty Quantification** | "I'm fairly confident" | Bootstrap perturbation over 200+ iterations → confidence intervals with rank stability scores |
| **Rare Pattern Discovery** | Limited by personal case experience | Apriori-based mining across entire case database; correlates low-frequency symptom subgraphs with outcomes |

## Project Structure

```
hackbit/
├── config.py                           # All configuration & tuning params
├── main.py                             # CLI entry point
├── requirements.txt
│
├── schema/                             # Graph schema definitions
│   ├── base_schema.py                  # Symptom, Rubric, Remedy
│   ├── reliability_schema.py           # CONTRADICTS, CORRELATED_WITH
│   ├── temporal_schema.py              # Case, CaseSnapshot
│   ├── pattern_schema.py              # Outcome nodes
│   └── seed_data.py                    # Sample knowledge graph data
│
├── core/                               # Base Graph-RAG pipeline
│   ├── graph_client.py                 # Neo4j connection wrapper
│   ├── symptom_extractor.py            # LLM-based structuring only
│   ├── remedy_ranker.py                # Graph traversal ranking
│   ├── explainer.py                    # LLM explanation (graph-grounded)
│   └── pipeline.py                     # Base pipeline orchestration
│
├── reasoning/                          # Advanced intelligence layers
│   ├── reliability/                    # Layer 1
│   │   ├── contradiction_detector.py   # CONTRADICTS edge traversal
│   │   ├── reliability_scorer.py       # Case reliability score
│   │   └── tests/
│   │
│   ├── temporal/                       # Layer 2
│   │   ├── case_memory.py              # Timeline storage & retrieval
│   │   ├── evolution_reasoner.py       # Snapshot diff & suppression detection
│   │   └── tests/
│   │
│   ├── uncertainty/                    # Layer 3
│   │   ├── bootstrap_ranker.py         # Symptom subset perturbation
│   │   ├── confidence_estimator.py     # CI computation & rank stability
│   │   └── tests/
│   │
│   └── pattern_mining/                 # Layer 4
│       ├── subgraph_miner.py           # Apriori-based symptom pattern mining
│       ├── outcome_correlator.py       # Pattern × remedy × outcome correlation
│       └── tests/
│
├── integration/
│   └── enhanced_pipeline.py            # Full pipeline wiring all 4 layers
│
└── tests/
    └── test_integration.py             # End-to-end integration tests
```

## Graph Schema

### Base Nodes & Relationships
```
(Symptom {id, name, category})
(Rubric  {id, chapter, text})
(Remedy  {name, abbrev})

(Symptom)-[:BELONGS_TO]->(Rubric)
(Rubric)-[:INDICATES {grade: 1-3}]->(Remedy)
```

### Layer 1: Reliability
```
(Symptom)-[:CONTRADICTS     {strength: 0-1, source}]->(Symptom)
(Symptom)-[:CORRELATED_WITH {strength: 0-1, source}]->(Symptom)
```

### Layer 2: Temporal
```
(Case         {id, patient_id})
(CaseSnapshot {id})
(Outcome      {type: Improved|NoChange|Worsened})

(Case)-[:HAS_SNAPSHOT {day: int}]->(CaseSnapshot)
(CaseSnapshot)-[:OBSERVED_SYMPTOM {intensity: 0-1}]->(Symptom)
(CaseSnapshot)-[:PRESCRIBED {potency}]->(Remedy)
(Case)-[:OUTCOME]->(Outcome)
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Neo4j (e.g., Docker)
docker run -d -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password neo4j:5

# 3. Bootstrap schema + seed data
python main.py seed

# 4. Run demo
python main.py demo

# 5. Run temporal evolution demo
python main.py demo-temporal

# 6. Run tests (no Neo4j needed)
pytest -v
```

## Sample Output

```
╔══════════════════════════════════════════════════════════╗
║   GRAPH-RAG CLINICAL DECISION SUPPORT — ENHANCED       ║
╚══════════════════════════════════════════════════════════╝

Symptoms analyzed: 4

RELIABILITY: [████████████████████░] 97%

REMEDY RANKINGS:
  Remedy                       Score                CI  Stability
  ─────────────────────────────────────────────────────────────────
  Belladonna                   0.9167   [0.750, 0.917]       0.92
  Aconitum Napellus            0.4167   [0.222, 0.556]       0.88

RARE PATTERN DISCOVERIES:
  ★ Rare pattern: Throbbing headache + Red flushed face
    → Belladonna (100% success, n=3 cases)

OVERALL CERTAINTY: 84%
```

## Algorithms

### Reliability Score
```
score = 1.0
for each contradiction in CONTRADICTS edges between case symptoms:
    score -= PENALTY * contradiction.strength
score += min(correlation_count * 0.03, 0.1)  # consistency bonus
score = clamp(0, 1)
```

### Uncertainty Estimation (Bootstrap)
```
for i in 1..N_ITERATIONS:
    subset = randomly_drop(symptoms, fraction=0.2)
    scores[i] = graph_rank(subset)
CI = percentile(scores, [5%, 95%])
stability = mode_rank_frequency / N_ITERATIONS
```

### Temporal Evolution
```
diff = snapshot[t2].symptoms - snapshot[t1].symptoms
if physical_improved AND mental_worsened:
    flag SUPPRESSION
trend = classify(improved_count, worsened_count)
```

### Rare Pattern Mining (Apriori)
```
for k in 2..MAX_SIZE:
    candidates = generate_from(frequent[k-1])
    count support across all cases
    filter by min_frequency
correlate with Outcome nodes for success rates
```

## Configuration

All tuning parameters are in `config.py`:

| Parameter | Default | Description |
|---|---|---|
| `CONTRADICTION_STRENGTH_THRESHOLD` | 0.5 | Min strength to flag a contradiction |
| `RELIABILITY_PENALTY_PER_CONTRADICTION` | 0.15 | Score penalty per contradiction |
| `BOOTSTRAP_ITERATIONS` | 200 | Perturbation count for uncertainty |
| `SYMPTOM_DROP_FRACTION` | 0.2 | Fraction of symptoms dropped per iteration |
| `CONFIDENCE_LEVEL` | 0.90 | Confidence interval level |
| `MIN_PATTERN_FREQUENCY` | 3 | Min cases for a pattern to register |
| `MIN_SUCCESS_RATE` | 0.6 | Min success rate to report a pattern |

## Integration Rules

1. All four intelligence layers plug into the pipeline **independently**
2. Disabling any layer does not affect the others
3. The core Graph-RAG flow (extract → rank → explain) is **never altered**
4. LLMs are restricted to:
   - Structuring free-text input into symptoms
   - Explaining graph-derived results in natural language
5. LLMs **never**: invent remedies, override rankings, or resolve contradictions
