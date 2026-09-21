"""
SANGAM Local RAG (Retrieval-Augmented Generation) — prototype.

Pipeline:
1. Index knowledge documents + optional live challenges/projects
2. Retrieve top-k chunks via bag-of-words TF-IDF cosine similarity
3. Synthesize a grounded answer that cites retrieved sources

DISCLAIMER:
- Default mode is LOCAL (no external LLM).
- Set OPENAI_API_KEY to enable optional LLM generation over retrieved context
  (still labeled honestly in API responses).
"""
from __future__ import annotations

import json
import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "at", "by",
    "is", "are", "was", "were", "be", "been", "has", "have", "had", "with",
    "from", "as", "that", "this", "these", "those", "it", "its", "into", "after",
    "can", "may", "will", "should", "their", "they", "them", "than", "then",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _tokenize(text: str) -> list[str]:
    return [
        t for t in re.findall(r"[a-z0-9]+", _normalize(text))
        if t not in STOPWORDS and len(t) > 2
    ]


def _chunk_text(text: str, chunk_size: int = 450, overlap: int = 80) -> list[str]:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        # prefer break at sentence/punctuation
        if end < len(text):
            window = text[start:end]
            for sep in [". ", "; ", ", ", " "]:
                idx = window.rfind(sep)
                if idx > chunk_size * 0.4:
                    end = start + idx + len(sep)
                    break
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


@dataclass
class KnowledgeDoc:
    id: str
    title: str
    content: str
    domain: str = "General"
    tags: list[str] = field(default_factory=list)
    source_type: str = "playbook"  # playbook | policy | case | institution | live
    provenance: str = "demo"  # demo | user | system
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    text: str
    domain: str
    tags: list[str]
    source_type: str
    provenance: str
    metadata: dict[str, Any] = field(default_factory=dict)


class LocalVectorIndex:
    """In-memory TF-IDF-like index (pure Python, no sklearn)."""

    def __init__(self) -> None:
        self.chunks: list[Chunk] = []
        self.doc_tfs: list[Counter] = []
        self.idf: dict[str, float] = {}
        self._built = False

    def clear(self) -> None:
        self.chunks = []
        self.doc_tfs = []
        self.idf = {}
        self._built = False

    def add_chunks(self, chunks: list[Chunk]) -> None:
        self.chunks.extend(chunks)
        self._built = False

    def build(self) -> None:
        tokenized = [
            _tokenize(c.text + " " + c.title + " " + " ".join(c.tags)) for c in self.chunks
        ]
        self.doc_tfs = [Counter(toks) for toks in tokenized]
        df: Counter = Counter()
        for tf in self.doc_tfs:
            for term in tf:
                df[term] += 1
        n = max(len(self.doc_tfs), 1)
        self.idf = {t: math.log((n + 1) / (df[t] + 1)) + 1.0 for t in df}
        self._built = True

    def _tfidf(self, tf: Counter) -> dict[str, float]:
        if not tf:
            return {}
        max_f = max(tf.values())
        return {
            t: (tf[t] / max_f) * self.idf.get(t, 0.0)
            for t in tf
        }

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        keys = set(a) | set(b)
        dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def search(self, query: str, top_k: int = 5, domain: Optional[str] = None) -> list[dict[str, Any]]:
        if not self._built:
            self.build()
        if not self.chunks:
            return []
        q_tf = Counter(_tokenize(query))
        q_vec = self._tfidf(q_tf)
        scored = []
        for i, chunk in enumerate(self.chunks):
            if domain and domain.lower() not in (chunk.domain or "").lower() and domain.lower() != "all":
                # soft filter: still allow if tags overlap heavily
                if domain.lower() not in " ".join(chunk.tags).lower():
                    continue
            score = self._cosine(q_vec, self._tfidf(self.doc_tfs[i]))
            if score <= 0.01:
                continue
            scored.append({
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "title": chunk.title,
                "text": chunk.text,
                "domain": chunk.domain,
                "tags": chunk.tags,
                "source_type": chunk.source_type,
                "provenance": chunk.provenance,
                "score": round(score * 100, 1),
                "metadata": chunk.metadata,
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        # if domain filter emptied results, retry without filter
        if domain and not scored:
            return self.search(query, top_k=top_k, domain=None)
        return scored[:top_k]


def load_seed_knowledge(path: Optional[Path] = None) -> list[KnowledgeDoc]:
    base = path or Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"
    if not base.exists():
        return []
    raw = json.loads(base.read_text(encoding="utf-8"))
    docs = []
    for item in raw:
        docs.append(KnowledgeDoc(
            id=item["id"],
            title=item["title"],
            content=item["content"],
            domain=item.get("domain", "General"),
            tags=item.get("tags", []),
            source_type=item.get("source_type", "playbook"),
            provenance=item.get("provenance", "demo"),
            metadata=item.get("metadata", {}),
        ))
    return docs


class SangamRAG:
    def __init__(self) -> None:
        self.index = LocalVectorIndex()
        self.docs: dict[str, KnowledgeDoc] = {}
        self.method_label = "local_tfidf_retrieval + grounded_template_synthesis"
        self.generation_mode = "local"

    def reset_from_seed(self, extra_docs: Optional[list[KnowledgeDoc]] = None) -> int:
        self.index.clear()
        self.docs = {}
        docs = load_seed_knowledge()
        if extra_docs:
            docs.extend(extra_docs)
        for doc in docs:
            self.add_document(doc, rebuild=False)
        self.index.build()
        return len(self.docs)

    def add_document(self, doc: KnowledgeDoc, rebuild: bool = True) -> int:
        self.docs[doc.id] = doc
        parts = _chunk_text(doc.content)
        chunks = []
        for i, part in enumerate(parts):
            chunks.append(Chunk(
                chunk_id=f"{doc.id}::c{i}",
                doc_id=doc.id,
                title=doc.title,
                text=part,
                domain=doc.domain,
                tags=doc.tags,
                source_type=doc.source_type,
                provenance=doc.provenance,
                metadata=doc.metadata,
            ))
        self.index.add_chunks(chunks)
        if rebuild:
            self.index.build()
        return len(chunks)

    def upsert_live_corpus(self, challenges: list[dict], projects: list[dict], universities: list[dict]) -> None:
        """Re-index demo knowledge + live DB entities for richer retrieval."""
        extras: list[KnowledgeDoc] = []
        for c in challenges:
            extras.append(KnowledgeDoc(
                id=f"live-challenge-{c['id']}",
                title=f"Challenge: {c.get('title', '')}",
                content=(
                    f"{c.get('title','')}. {c.get('description','')}. "
                    f"Domain: {c.get('domain') or c.get('category')}. "
                    f"District: {c.get('district')}. Status: {c.get('status')}. "
                    f"Impact: {c.get('community_impact','')}. "
                    f"Expertise: {', '.join(c.get('required_expertise') or [])}."
                ),
                domain=c.get("domain") or c.get("category") or "General",
                tags=["challenge", "live", (c.get("district") or "").lower()],
                source_type="live",
                provenance="user" if not c.get("is_demo") else "demo",
                metadata={"challenge_id": c["id"], "status": c.get("status")},
            ))
        for p in projects:
            extras.append(KnowledgeDoc(
                id=f"live-project-{p['id']}",
                title=f"Project: {p.get('name', '')}",
                content=(
                    f"Project {p.get('name')}. Goal: {p.get('goal')}. "
                    f"Proposal: {p.get('proposal') or ''}. Status: {p.get('status')}. "
                    f"Team: {p.get('team_name')}. Match: {p.get('match_explanation') or ''}."
                ),
                domain="Innovation",
                tags=["project", "live", (p.get("team_name") or "").lower()],
                source_type="live",
                provenance="user" if not p.get("is_demo") else "demo",
                metadata={"project_id": p["id"]},
            ))
        for u in universities:
            extras.append(KnowledgeDoc(
                id=f"live-uni-{u['id']}",
                title=f"University: {u.get('name', '')}",
                content=(
                    f"{u.get('name')}. Departments: {', '.join(u.get('departments') or [])}. "
                    f"Research: {', '.join(u.get('research_areas') or [])}. "
                    f"Faculty: {', '.join(u.get('faculty_expertise') or [])}. "
                    f"Labs: {', '.join(u.get('laboratory_capabilities') or [])}. "
                    f"Domains: {', '.join(u.get('domains') or [])}."
                ),
                domain="Institution",
                tags=["university", "demo"],
                source_type="institution",
                provenance=u.get("provenance", "demo"),
                metadata={"university_id": u["id"]},
            ))
        self.reset_from_seed(extra_docs=extras)

    def retrieve(self, query: str, top_k: int = 5, domain: Optional[str] = None) -> list[dict[str, Any]]:
        return self.index.search(query, top_k=top_k, domain=domain)

    def _local_synthesize(self, query: str, hits: list[dict[str, Any]]) -> str:
        if not hits:
            return (
                "No sufficiently relevant knowledge chunks were retrieved for this query. "
                "Try refining the question or adding more playbooks to the knowledge base."
            )
        lines = [
            f"Grounded response for: “{query.strip()}”",
            "",
            "Based on retrieved SANGAM knowledge sources:",
        ]
        for i, h in enumerate(hits, 1):
            excerpt = h["text"]
            if len(excerpt) > 280:
                excerpt = excerpt[:277] + "..."
            lines.append(
                f"{i}. [{h['title']}] ({h['source_type']}, relevance {h['score']}%) — {excerpt}"
            )
        lines.append("")
        lines.append("Recommended next steps:")
        # Heuristic action bullets from top domains/tags
        top_tags = []
        for h in hits[:3]:
            top_tags.extend(h.get("tags") or [])
        if any("water" in t for t in top_tags) or "water" in query.lower():
            lines.append("- Prioritize water-quality evidence collection and temporary safe-water advisories.")
            lines.append("- Match Civil/Environmental Engineering + IoT teams for low-cost sensing pilots.")
        if any(t in " ".join(top_tags) for t in ["flood", "disaster"]):
            lines.append("- Coordinate with district disaster cells for consolidation of similar reports.")
        if any(h.get("source_type") == "live" for h in hits):
            lines.append("- Link this query to existing live challenges/projects already on the platform.")
        lines.append("- Validate retrieved guidance with local officials before field deployment.")
        lines.append("")
        lines.append(
            "Note: This answer was synthesized locally from retrieved chunks "
            "(not an external generative model unless OPENAI_API_KEY is configured)."
        )
        return "\n".join(lines)

    def _openai_synthesize(self, query: str, hits: list[dict[str, Any]]) -> Optional[str]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            import httpx
            context = "\n\n".join(
                f"SOURCE {i}: {h['title']} (score={h['score']})\n{h['text']}"
                for i, h in enumerate(hits, 1)
            )
            prompt = (
                "You are SANGAM's civic innovation assistant. Answer ONLY using the sources. "
                "Cite source titles. If insufficient, say so.\n\n"
                f"QUESTION: {query}\n\nSOURCES:\n{context}"
            )
            resp = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    "messages": [
                        {"role": "system", "content": "Ground answers in provided sources only."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                },
                timeout=45.0,
            )
            if resp.status_code >= 400:
                return None
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception:
            return None

    def query(
        self,
        question: str,
        top_k: int = 5,
        domain: Optional[str] = None,
        prefer_llm: bool = True,
    ) -> dict[str, Any]:
        hits = self.retrieve(question, top_k=top_k, domain=domain)
        answer = None
        mode = "local"
        if prefer_llm:
            answer = self._openai_synthesize(question, hits)
            if answer:
                mode = "openai_over_retrieved_context"
        if not answer:
            answer = self._local_synthesize(question, hits)
            mode = "local"

        return {
            "question": question,
            "answer": answer,
            "sources": hits,
            "retrieval_method": "local_tfidf_cosine",
            "generation_mode": mode,
            "disclaimer": (
                "RAG prototype: retrieval is local TF-IDF over SANGAM knowledge + live corpus. "
                "Generation is grounded template synthesis by default; OpenAI used only if API key is set."
            ),
            "data_labels": {
                "knowledge_base": "DEMO playbooks + LIVE DB entities when indexed",
                "retrieval": "REAL FUNCTIONALITY (local)",
                "generation": "LOCAL synthesis" if mode == "local" else "EXTERNAL LLM over retrieved context",
            },
            "stats": {
                "documents_indexed": len(self.docs),
                "chunks_indexed": len(self.index.chunks),
                "sources_returned": len(hits),
            },
        }

    def suggest_for_challenge(self, title: str, description: str, domain: str = "") -> dict[str, Any]:
        q = f"Solution approaches and playbooks for: {title}. {description}. Domain: {domain}"
        result = self.query(q, top_k=4, domain=domain.split("&")[0].strip() if domain else None)
        result["use_case"] = "challenge_enrichment"
        return result


# Singleton used by API
rag_engine = SangamRAG()
