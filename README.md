# PDF Buddy

> Chat with your PDFs — upload a document and ask questions in natural language, powered by a retrieval-augmented generation (RAG) pipeline.

PDF Buddy is a full-stack document question-answering platform. It parses uploaded PDFs, indexes their contents as vector embeddings, and answers natural-language questions by retrieving the most relevant passages and grounding responses in the source document.

## Features

- **PDF upload & parsing** — layout-aware extraction via [LlamaParse](https://github.com/run-llama/llama_parse)
- **Semantic search (RAG)** — passages embedded with `sentence-transformers` and retrieved from a [Qdrant](https://qdrant.tech/) vector store
- **Async processing** — heavy parsing/embedding jobs run on Celery workers so the API stays responsive
- **Structured extraction** — pull structured fields from documents against a defined JSON schema (`backend/extraction-schema.json`)
- **Modern SPA frontend** — React 19 + Vite UI with TanStack Query/Table and Radix components

## Architecture

```
┌──────────────┐      REST      ┌──────────────┐      enqueue     ┌──────────────┐
│  React (Vite)│ ─────────────► │   FastAPI    │ ───────────────► │ Celery worker│
│   frontend   │ ◄───────────── │   backend    │                  │ parse + embed│
└──────────────┘                └──────┬───────┘                  └──────┬───────┘
                                       │                                 │
                        ┌──────────────┼─────────────────┬──────────────┘
                        ▼              ▼                 ▼
                  ┌───────────┐  ┌───────────┐     ┌───────────┐
                  │ PostgreSQL│  │   Redis    │     │  Qdrant   │
                  │ (metadata)│  │(broker/cache)    │ (vectors) │
                  └───────────┘  └───────────┘     └───────────┘
```

**Flow:** a user uploads a PDF → FastAPI stores metadata in Postgres and enqueues a job on Redis → a Celery worker parses the document with LlamaParse, generates embeddings, and upserts them into Qdrant → questions are answered by embedding the query, retrieving the nearest passages, and returning a grounded answer.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | FastAPI, Uvicorn, async SQLAlchemy 2.0, asyncpg, Pydantic Settings |
| **Async / queue** | Celery, Redis |
| **Data & retrieval** | PostgreSQL, Alembic (migrations), Qdrant, sentence-transformers, LlamaParse |
| **Frontend** | React 19, Vite, TypeScript, Tailwind CSS, TanStack Query & Table, Radix UI, axios |
| **Tooling** | uv (Python), Bun (JS), pytest, ruff, pre-commit, Docker Compose |

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers / endpoints
│   │   ├── core/         # config, db session, Celery app
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # parsing, embedding, retrieval logic
│   │   ├── tasks/        # Celery background tasks
│   │   ├── utils/
│   │   └── main.py       # FastAPI app entrypoint (app.main:app)
│   ├── alembic/          # database migrations
│   ├── extraction-schema.json
│   └── pyproject.toml
├── frontend-react/       # React + Vite single-page app
└── docker-compose.yml    # Postgres + Redis + Qdrant
```

## Getting Started

### Prerequisites

- Python 3.10+ and [uv](https://docs.astral.sh/uv/)
- [Bun](https://bun.sh/) (or Node.js) for the frontend
- Docker + Docker Compose
- A [LlamaCloud](https://cloud.llamaindex.ai/) API key (for LlamaParse)

### 1. Start the infrastructure

```bash
docker compose up -d      # spins up PostgreSQL, Redis, and Qdrant
```

### 2. Backend

```bash
cd backend
cp .env.example .env      # then set LLAMA_API_KEY and SECRET_KEY
uv sync                   # install dependencies
uv run alembic upgrade head   # apply database migrations
uv run uvicorn app.main:app --reload   # http://localhost:8000
```

Interactive API docs are available at `http://localhost:8000/docs`.

In a separate shell, start the Celery worker (adjust the `-A` path to wherever the Celery app is defined, e.g. `app.core.celery_app`):

```bash
cd backend
uv run celery -A app.core.celery_app worker --loglevel=info
```

### 3. Frontend

```bash
cd frontend-react
bun install
bun run dev               # http://localhost:5173
```

### Environment variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Async PostgreSQL DSN (e.g. `postgresql+asyncpg://postgres:postgres@localhost:5432/qp_search`) |
| `REDIS_URL` | Redis connection URL |
| `CELERY_BROKER_URL` | Celery broker (Redis) |
| `QDRANT_HOST` / `QDRANT_PORT` | Qdrant vector DB host/port |
| `LLAMA_API_KEY` | LlamaCloud / LlamaParse API key |
| `SECRET_KEY` | App secret for signing |

## Development

```bash
# Backend tests & lint
cd backend
uv run pytest
uv run ruff check .

# Frontend lint
cd frontend-react
bun run lint
```

## License

MIT
