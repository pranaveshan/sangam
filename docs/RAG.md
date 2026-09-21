# SANGAM RAG System

## What it does

Retrieval-Augmented Generation over:

1. **Demo knowledge base** — playbooks/policies/cases in `backend/app/data/knowledge_base.json`
2. **Live DB entities** — challenges, projects, universities re-indexed on startup / `/api/rag/reindex`

## Pipeline (honest labels)

| Step | Method | Label |
|------|--------|-------|
| Chunking | Fixed-size text chunks with overlap | Real functionality |
| Retrieval | Local TF-IDF cosine similarity | Real functionality |
| Generation (default) | Grounded template synthesis citing sources | Real functionality (local) |
| Generation (optional) | OpenAI chat over retrieved context | Future/optional — needs `OPENAI_API_KEY` |

## API

- `GET /api/rag/status`
- `POST /api/rag/reindex`
- `POST /api/rag/query` `{ question, top_k?, domain?, prefer_llm? }`
- `GET /api/rag/suggest/{challenge_id}`
- `GET /api/rag/documents`
- `POST /api/rag/documents` — add user knowledge

Challenge submit / reanalyze also return a `rag` block.

## UI

- Header → **RAG** (`/rag`) — ask questions, browse index, add documents
- After challenge submit / on challenge detail — **RAG Assistant** panel

## Optional OpenAI

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Without the key, SANGAM stays fully offline with local grounded answers.
