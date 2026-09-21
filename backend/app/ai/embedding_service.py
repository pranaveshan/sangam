"""Embedding service — local hashing / bag-of-words vectors (upgrade path ready)."""
from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from typing import Any

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "at", "by",
    "is", "are", "was", "were", "be", "been", "has", "have", "had", "with",
    "from", "as", "that", "this", "these", "those", "it", "its", "into", "after",
}

DIM = 256


def _tokenize(text: str) -> list[str]:
    return [
        t for t in re.findall(r"[a-zA-Z0-9\u0900-\u097F\u0C00-\u0C7F]+", (text or "").lower())
        if t not in STOPWORDS and len(t) > 1
    ]


class EmbeddingService:
    """Local sparse-hash embedding. Never invents semantic meaning beyond token overlap."""

    def __init__(self, dim: int = DIM):
        self.dim = dim
        self.provider = "local_hashing_bow"

    def embed(self, text: str) -> list[float]:
        tokens = _tokenize(text)
        vec = [0.0] * self.dim
        if not tokens:
            return vec
        counts = Counter(tokens)
        for tok, cnt in counts.items():
            h = int(hashlib.sha256(tok.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign * float(cnt)
        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [round(v / norm, 6) for v in vec]

    def cosine(self, a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        return float(sum(x * y for x, y in zip(a, b)))

    def similarity(self, text_a: str, text_b: str) -> float:
        return self.cosine(self.embed(text_a), self.embed(text_b))

    def find_similar(
        self,
        query_text: str,
        candidates: list[dict[str, Any]],
        threshold: float = 0.35,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        q = self.embed(query_text)
        results = []
        for item in candidates:
            doc = f"{item.get('title', '')} {item.get('description', '')} {item.get('location', '')}"
            emb = item.get("embedding") or self.embed(doc)
            sim = self.cosine(q, emb)
            if sim < threshold:
                continue
            results.append({
                **{k: item[k] for k in item if k != "embedding"},
                "similarity": round(sim * 100, 1),
                "embedding_method": self.provider,
            })
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]


embedding_service = EmbeddingService()
