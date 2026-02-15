# Multi PDF RAG System

Contextual Q&A across multiple PDFs with reliable citations. Backend powered by FastAPI, LangChain, Qdrant, and Gemini; frontend built with Next.js.

**Tech Stack**

- **Backend:** FastAPI, Pydantic, LangChain, Qdrant, Google Generative AI Embeddings, Uvicorn
- **Frontend:** Next.js 14, React 18, TypeScript
- **Infra/Deps:** Python 3.13+, Node.js 18+, Docker (for Qdrant)

## Overview

- Ingest multiple PDFs, split them into metadata‑rich chunks, embed with Gemini `text-embedding-004`, and store in Qdrant.
- Run similarity search to retrieve relevant chunks and generate answers with `gemini-2.5-flash`, grounded in the retrieved context.
- Preserve `source` (filename) and `page_label` (page number) metadata for citation. The UI displays citations when provided.

## Architecture

- **PDF Ingestion:** Parse each page, extract text, attach metadata: `source`, `page_label`.
- **Chunking:** LangChain `CharacterTextSplitter` produces overlapping chunks for better recall.
- **Embedding:** `GoogleGenerativeAIEmbeddings` (`models/text-embedding-004`) using `GOOGLE_API_KEY`.
- **Vector Store:** `QdrantVectorStore` backed by Qdrant over `QDRANT_URL` and `QDRANT_COLLECTION`.
- **Retrieval:** `similarity_search` returns top chunks with metadata.
- **Generation:** Prompt `gemini-2.5-flash` via OpenAI SDK against Google Generative Language API (`GEMINI_API_KEY`) with a strict system prompt that confines answers to retrieved context.

Key implementation points:

- Chunking on `Document` objects retains metadata through the pipeline for accurate citations.
- The server holds vector stores per session (`session_id`) so the browser never uploads embeddings or vectors.

## Backend API

- POST `/process-pdfs`

  - Form‑Data: `files`: one or more PDF files.
  - Behavior: extracts per‑page text, builds `Document` chunks with metadata, embeds, creates a Qdrant vector store, and stores it server‑side under a new `session_id`.
  - Response (JSON):
    - `message`: string
    - `session_id`: string
    - `files`: string[]

- POST `/ask-question`
  - JSON body:
    - `session_id`: string
    - `user_query`: string
  - Behavior: runs `similarity_search` on the session’s vector store, crafts a context block (including page and source), and calls Gemini for an answer grounded in that context.
  - Response (JSON):
    - `answer`: string
    - `sources`?: `[{ source: string; page_label: number }]` (optional; UI displays if provided)

## Environment Variables

Place a `.env` file in `backend/` with:

- `GOOGLE_API_KEY`: for embeddings (`text-embedding-004`).
- `GEMINI_API_KEY`: for chat generation (`gemini-2.5-flash` via Google Generative Language API).
- `QDRANT_URL`: default `http://localhost:6333`.
- `QDRANT_COLLECTION`: default `MultiPDFChat`.

Frontend environment (`frontend/.env.local`):

- `NEXT_PUBLIC_API_BASE_URL`: default `http://localhost:8000`.

## Data Pipeline Details

- `get_pdf_documents()` and server ingestion: extract per‑page text and attach metadata: `source` (filename) and `page_label` (1‑based page index).
- `get_text_chunks()`: LangChain `CharacterTextSplitter` with `chunk_size=1000`, `chunk_overlap=200` preserves metadata.
- `create_vector_store()`: `QdrantVectorStore.from_documents(...)` persists embeddings to Qdrant.
- `answer_question()`: builds a strict `SYSTEM_PROMPT` and calls Gemini via OpenAI SDK (`base_url=https://generativelanguage.googleapis.com/v1beta/openai/`).
- Citations: the UI can render `sources` (`source`, `page_label`) if the backend includes them in the response. Metadata is carried through retrieval; adding `sources` to the response is a straightforward enhancement.

## Validation & Safety

- Upload validation: rejects non‑PDFs/unreadable files with 400 errors.
- Request validation: `AskQuestionRequest` enforces `session_id` and `user_query`.
- Session isolation: per‑session vector stores in memory on the server (`VECTOR_STORES[session_id]`).
- Grounded answers: the system prompt instructs to answer only from retrieved context; answers are constrained and include guidance to reference pages.

