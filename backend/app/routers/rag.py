from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Challenge, Project, University
from ..ai.rag import rag_engine, KnowledgeDoc

router = APIRouter(prefix="/api/rag", tags=["rag"])


class RagQueryRequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=5, ge=1, le=12)
    domain: Optional[str] = None
    prefer_llm: bool = True
    refresh_live_index: bool = True


class RagIndexDocRequest(BaseModel):
    id: str
    title: str
    content: str
    domain: str = "General"
    tags: list[str] = []
    source_type: str = "playbook"
    provenance: str = "user"


def _refresh_live(db: Session) -> None:
    challenges = [
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "domain": c.domain,
            "category": c.category,
            "district": c.district,
            "status": c.status,
            "community_impact": c.community_impact,
            "required_expertise": c.required_expertise,
            "is_demo": c.is_demo,
        }
        for c in db.query(Challenge).all()
    ]
    projects = [
        {
            "id": p.id,
            "name": p.name,
            "goal": p.goal,
            "proposal": p.proposal,
            "status": p.status,
            "team_name": p.team_name,
            "match_explanation": p.match_explanation,
            "is_demo": p.is_demo,
        }
        for p in db.query(Project).all()
    ]
    universities = [
        {
            "id": u.id,
            "name": u.name,
            "departments": u.departments,
            "research_areas": u.research_areas,
            "faculty_expertise": u.faculty_expertise,
            "laboratory_capabilities": u.laboratory_capabilities,
            "domains": u.domains,
            "provenance": u.provenance,
        }
        for u in db.query(University).all()
    ]
    rag_engine.upsert_live_corpus(challenges, projects, universities)


@router.get("/status")
def rag_status(db: Session = Depends(get_db)):
    if len(rag_engine.docs) == 0:
        _refresh_live(db)
    return {
        "ok": True,
        "documents_indexed": len(rag_engine.docs),
        "chunks_indexed": len(rag_engine.index.chunks),
        "retrieval_method": "local_tfidf_cosine",
        "generation_default": "local_grounded_synthesis",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "disclaimer": (
            "RAG prototype: local TF-IDF retrieval + grounded synthesis. "
            "OpenAI used only if OPENAI_API_KEY is set."
        ),
        "data_label": "DEMO knowledge base + LIVE DB entities",
    }


@router.post("/reindex")
def reindex(db: Session = Depends(get_db)):
    _refresh_live(db)
    return {
        "ok": True,
        "documents_indexed": len(rag_engine.docs),
        "chunks_indexed": len(rag_engine.index.chunks),
        "message": "Knowledge base + live challenges/projects/universities re-indexed.",
    }


@router.post("/query")
def rag_query(body: RagQueryRequest, db: Session = Depends(get_db)):
    if body.refresh_live_index or len(rag_engine.docs) == 0:
        _refresh_live(db)
    return rag_engine.query(
        question=body.question,
        top_k=body.top_k,
        domain=body.domain,
        prefer_llm=body.prefer_llm,
    )


@router.get("/suggest/{challenge_id}")
def suggest_for_challenge(challenge_id: int, db: Session = Depends(get_db)):
    c = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not c:
        raise HTTPException(404, "Challenge not found")
    if len(rag_engine.docs) == 0:
        _refresh_live(db)
    return rag_engine.suggest_for_challenge(c.title, c.description, c.domain or c.category)


@router.post("/documents")
def add_document(body: RagIndexDocRequest, db: Session = Depends(get_db)):
    """Add a user knowledge document into the RAG index (real functionality)."""
    if len(rag_engine.docs) == 0:
        _refresh_live(db)
    chunks = rag_engine.add_document(KnowledgeDoc(**body.model_dump()), rebuild=True)
    return {
        "ok": True,
        "doc_id": body.id,
        "chunks_added": chunks,
        "documents_indexed": len(rag_engine.docs),
        "provenance": body.provenance,
        "data_label": "USER-GENERATED knowledge document",
    }


@router.get("/documents")
def list_documents():
    return [
        {
            "id": d.id,
            "title": d.title,
            "domain": d.domain,
            "tags": d.tags,
            "source_type": d.source_type,
            "provenance": d.provenance,
        }
        for d in rag_engine.docs.values()
    ]
