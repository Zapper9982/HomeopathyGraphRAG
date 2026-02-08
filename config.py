"""
Graph-RAG Clinical Decision Support System for Homeopathy
Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Neo4j ──────────────────────────────────────────────
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# ── LLM (used ONLY for structuring input + explaining output) ──
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")

# ── Reasoning Tuning ──────────────────────────────────
# Symptom Reliability
CONTRADICTION_STRENGTH_THRESHOLD = 0.5  # flag if strength >= this
RELIABILITY_PENALTY_PER_CONTRADICTION = 0.15

# Uncertainty Estimation
BOOTSTRAP_ITERATIONS = 200
SYMPTOM_DROP_FRACTION = 0.2   # fraction of symptoms dropped per perturbation
CONFIDENCE_LEVEL = 0.90       # for confidence intervals

# Pattern Mining
MIN_PATTERN_FREQUENCY = 3     # minimum cases for a pattern to register
MIN_SUCCESS_RATE = 0.6        # minimum success rate to report
MAX_PATTERN_SIZE = 4          # max symptoms in a rare subgraph

# Temporal Reasoning
SUPPRESSION_MENTAL_WEIGHT = 1.5  # weight mental symptoms higher in suppression detection
IMPROVEMENT_THRESHOLD = 0.3      # fraction of symptoms resolved to count as improvement
