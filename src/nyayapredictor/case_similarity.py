"""Case similarity engine using semantic + feature matching."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from src.common.models import DisputeCase


@dataclass
class CaseSimilarityEngine:
    """Retrieve similar precedents for a dispute case."""

    precedents_path: str
    embedding_model: str = "all-MiniLM-L6-v2"
    precedents: List[Dict] = field(init=False)
    embedder: Optional[object] = field(init=False, default=None)
    embeddings: Optional[np.ndarray] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self.precedents = self._load_precedents(self.precedents_path)
        self.embedder = self._load_embedder()
        self.embeddings = self._compute_embeddings()

    @staticmethod
    def _load_precedents(path: str) -> List[Dict]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return payload if isinstance(payload, list) else []

    def _load_embedder(self) -> Optional[object]:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            return SentenceTransformer(self.embedding_model)
        except Exception:
            return None

    def _compute_embeddings(self) -> Optional[np.ndarray]:
        if not self.precedents:
            return None
        texts = [row.get("summary", "") for row in self.precedents]
        if self.embedder:
            try:
                return np.asarray(self.embedder.encode(texts, show_progress_bar=False))
            except Exception:
                return None
        return None

    @staticmethod
    def _cosine(a: np.ndarray, b: np.ndarray) -> float:
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    @staticmethod
    def _token_similarity(text_a: str, text_b: str) -> float:
        tokens_a = set(text_a.lower().split())
        tokens_b = set(text_b.lower().split())
        if not tokens_a or not tokens_b:
            return 0.0
        return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)

    @staticmethod
    def _feature_similarity(dispute: DisputeCase, precedent: Dict) -> float:
        amount = float(precedent.get("dispute_amount", 0.0))
        amount_ratio = 1.0 - min(1.0, abs(dispute.total_claim - amount) / max(dispute.total_claim, 1.0))
        overdue_ratio = 1.0 - min(
            1.0,
            abs(max((inv.days_overdue for inv in dispute.invoices), default=0) - float(precedent.get("days_overdue", 0)))
            / 365.0,
        )
        buyer_match = 1.0 if dispute.buyer.buyer_type == precedent.get("buyer_type") else 0.0
        state_match = 1.0 if dispute.mse.state == precedent.get("state") else 0.0
        sector_match = 1.0 if dispute.mse.major_activity in str(precedent.get("mse_sector", "")) else 0.0
        return float(np.clip(0.35 * amount_ratio + 0.2 * overdue_ratio + 0.2 * buyer_match + 0.15 * state_match + 0.1 * sector_match, 0, 1))

    def find_similar_cases(self, dispute: DisputeCase, top_k: int = 5) -> List[Dict]:
        """Find top-k similar cases by weighted semantic and feature similarity."""
        if not self.precedents:
            return []

        query_text = dispute.dispute_description or ""
        if self.embedder and self.embeddings is not None:
            query_vector = np.asarray(self.embedder.encode([query_text], show_progress_bar=False))[0]
        else:
            query_vector = None

        scored = []
        for idx, case in enumerate(self.precedents):
            if query_vector is not None and self.embeddings is not None:
                semantic = self._cosine(query_vector, self.embeddings[idx])
            else:
                semantic = self._token_similarity(query_text, case.get("summary", ""))
            feature = self._feature_similarity(dispute, case)
            total_score = 0.4 * semantic + 0.6 * feature
            scored.append((total_score, case))

        scored.sort(key=lambda x: x[0], reverse=True)
        result = []
        for score, case in scored[:top_k]:
            result.append(
                {
                    "case_id": case.get("case_id"),
                    "summary": case.get("summary"),
                    "outcome": case.get("outcome"),
                    "recovery_percentage": case.get("recovery_percentage"),
                    "resolution_days": case.get("resolution_days"),
                    "similarity_score": round(score, 4),
                    "learning": (
                        "Prior outcomes suggest documentation strength and agreement terms directly improve recovery."
                    ),
                }
            )
        return result

    def get_precedent_insight(self, similar_cases: List[Dict]) -> str:
        """Generate concise precedent insight from retrieved similar cases."""
        if not similar_cases:
            return "No sufficiently similar precedents available for this dispute."
        recoveries = [float(c.get("recovery_percentage", 0.0)) for c in similar_cases]
        avg_recovery = sum(recoveries) / max(len(recoveries), 1)
        above_80 = sum(1 for v in recoveries if v >= 80)
        return (
            f"In {above_80} of {len(similar_cases)} similar cases, recovery was at least 80%. "
            f"Average recovery across matches is {avg_recovery:.1f}%."
        )
