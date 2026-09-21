"""SANGAM AI package — local services + classical NLP + RAG."""
from .engine import (
    build_full_analysis,
    classify_challenge,
    compute_priority,
    find_similar_challenges,
    match_universities,
    METHOD_DISCLAIMER,
)
from .rag import rag_engine, SangamRAG
from .llm_service import llm_service, LLMService
from .embedding_service import embedding_service, EmbeddingService
from .speech_service import speech_service, SpeechService
from .translation_service import translation_service, TranslationService

__all__ = [
    "build_full_analysis",
    "classify_challenge",
    "compute_priority",
    "find_similar_challenges",
    "match_universities",
    "METHOD_DISCLAIMER",
    "rag_engine",
    "SangamRAG",
    "llm_service",
    "LLMService",
    "embedding_service",
    "EmbeddingService",
    "speech_service",
    "SpeechService",
    "translation_service",
    "TranslationService",
]
