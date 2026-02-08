"""
Confidence Estimator — computes mean scores, confidence intervals,
and ranking stability metrics from bootstrap samples.

Purely algorithmic — uses numpy/scipy for statistics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy import stats

from core.graph_client import GraphClient
from reasoning.uncertainty.bootstrap_ranker import bootstrap_rank_optimized
import config


@dataclass
class RemedyConfidence:
    remedy: str
    mean_score: float
    std_dev: float
    confidence_interval: tuple[float, float]
    rank_stability: float  # 0-1, 1 = always same rank
    n_samples: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "remedy": self.remedy,
            "mean_score": round(self.mean_score, 4),
            "std_dev": round(self.std_dev, 4),
            "confidence_interval": [
                round(self.confidence_interval[0], 4),
                round(self.confidence_interval[1], 4),
            ],
            "rank_stability": round(self.rank_stability, 4),
            "n_samples": self.n_samples,
        }


@dataclass
class UncertaintyReport:
    remedies: list[RemedyConfidence] = field(default_factory=list)
    overall_certainty: float = 0.0  # 0-1, based on top remedy's stability

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_certainty": round(self.overall_certainty, 4),
            "remedies": [r.to_dict() for r in self.remedies],
        }


def estimate_confidence(
    graph: GraphClient,
    symptom_ids: list[str],
    n_iterations: int = config.BOOTSTRAP_ITERATIONS,
    confidence_level: float = config.CONFIDENCE_LEVEL,
    seed: int | None = None,
) -> UncertaintyReport:
    """
    Run bootstrap perturbation and compute:
      - Mean score per remedy
      - Confidence interval at the given level
      - Rank stability (proportion of iterations where ranking is unchanged)

    Returns an UncertaintyReport.
    """
    if not symptom_ids:
        return UncertaintyReport()

    # ── Bootstrap sampling ───────────────────────────────
    raw_scores = bootstrap_rank_optimized(
        graph, symptom_ids,
        n_iterations=n_iterations,
        seed=seed,
    )

    if not raw_scores:
        return UncertaintyReport()

    # ── Compute statistics ───────────────────────────────
    alpha = 1 - confidence_level
    remedy_confs: list[RemedyConfidence] = []

    # Compute ranks per iteration for stability
    n_iter = max(len(v) for v in raw_scores.values())
    remedies = list(raw_scores.keys())

    # Build score matrix: [n_iter x n_remedies]
    score_matrix = np.zeros((n_iter, len(remedies)))
    for j, remedy in enumerate(remedies):
        scores = raw_scores[remedy]
        for i in range(min(n_iter, len(scores))):
            score_matrix[i, j] = scores[i]

    # Compute ranks per iteration (higher score = rank 1)
    rank_matrix = np.zeros_like(score_matrix, dtype=int)
    for i in range(n_iter):
        order = np.argsort(-score_matrix[i, :])
        for rank, j in enumerate(order):
            rank_matrix[i, j] = rank + 1

    for j, remedy in enumerate(remedies):
        scores = score_matrix[:, j]
        ranks = rank_matrix[:, j]

        mean = float(np.mean(scores))
        std = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0

        # Confidence interval via percentile bootstrap
        lower = float(np.percentile(scores, (alpha / 2) * 100))
        upper = float(np.percentile(scores, (1 - alpha / 2) * 100))

        # Rank stability: fraction of iterations with modal rank
        if len(ranks) > 0:
            modal_rank = int(stats.mode(ranks, keepdims=True).mode[0])
            stability = float(np.mean(ranks == modal_rank))
        else:
            stability = 0.0

        remedy_confs.append(
            RemedyConfidence(
                remedy=remedy,
                mean_score=mean,
                std_dev=std,
                confidence_interval=(lower, upper),
                rank_stability=stability,
                n_samples=len(scores),
            )
        )

    # Sort by mean score descending
    remedy_confs.sort(key=lambda r: r.mean_score, reverse=True)

    # Overall certainty: weighted by top remedy's stability and CI width
    top = remedy_confs[0] if remedy_confs else None
    if top:
        ci_width = top.confidence_interval[1] - top.confidence_interval[0]
        # Narrow CI + stable rank = high certainty
        overall = top.rank_stability * max(0, 1 - ci_width)
    else:
        overall = 0.0

    return UncertaintyReport(
        remedies=remedy_confs,
        overall_certainty=overall,
    )
