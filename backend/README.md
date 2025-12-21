# Question Paper Search - Backend MVP

A semantic search engine backend for university question papers built with FastAPI, PostgreSQL, Qdrant, and Celery.

## Features

✅ **PDF Upload**: Upload multiple PDF files (up to 10, 50MB each)
✅ **Job Tracking**: Track processing status and progress
✅ **Async Processing**: Celery task queue for background PDF processing
✅ **Vector Search**: Qdrant for semantic similarity search
✅ **Database**: PostgreSQL with async SQLAlchemy 2.0
✅ **Embeddings**: Sentence Transformers for question embeddings
✅ **API Documentation**: Auto-generated Swagger/ReDoc docs

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL 15 (async with asyncpg)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Task Queue**: Celery + Redis
- **Vector DB**: Qdrant
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **PDF Extraction**: LlamaCloud SDK (planned)
- **Package Manager**: uv

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── upload.py      # File upload endpoint
│   │       ├── search.py      # Semantic search endpoint
│   │       ├── jobs.py        # Job status endpoint
│   │       └── router.py      # API router
│   ├── core/
│   │   ├── database.py        # Async database setup
│   │   └── qdrant.py          # Qdrant client
│   ├── models/
│   │   ├── job.py             # Job model
│   │   ├── document.py        # Document model
│   │   └── question.py        # Question model
│   ├── schemas/
│   │   ├── job.py             # Job schemas
│   │   └── question.py        # Question schemas
│   ├── services/
│   │   ├── llama_service.py   # PDF extraction service
│   │   ├── embedding_service.py # Embedding generation
│   │   └── search_service.py  # Search service
│   ├── tasks/
│   │   ├── celery_app.py      # Celery configuration
│   │   └── pdf_processor.py   # PDF processing task
│   ├── utils/
│   │   └── exceptions.py      # Custom exceptions
│   ├── config.py              # Settings
│   └── main.py                # FastAPI app
├── alembic/                   # Database migrations
├── scripts/
│   └── test_api.py            # Manual API testing
├── pyproject.toml             # Dependencies
└── .env                       # Environment variables
```

## Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- uv package manager

### Installation

1. **Clone the repository**:
   ```bash
   cd /home/sxtr/Projects/pdf-buddy
   ```

2. **Start infrastructure services**:
   ```bash
   docker-compose up -d
   ```

   This starts:
   - PostgreSQL (port 5432)
   - Redis (port 6379)
   - Qdrant (port 6333)

3. **Install dependencies**:
   ```bash
   cd backend
   uv sync
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your LLAMA_API_KEY
   ```

5. **Run migrations**:
   ```bash
   uv run alembic upgrade head
   ```

## Running the Application

### Development Mode

**Terminal 1 - Start FastAPI server**:
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Celery worker** (when needed):
```bash
cd backend
uv run celery -A app.tasks.celery_app worker --loglevel=info
```

### Testing

**Manual API tests**:
```bash
cd backend
uv run python scripts/test_api.py
```

**Access API documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check
```bash
GET /health
```

### Upload PDFs
```bash
POST /api/v1/upload
Content-Type: multipart/form-data

files: [PDF files]
```

Response:
```json
{
  "job_id": "uuid",
  "status": "queued",
  "status_url": "/api/v1/jobs/{job_id}",
  "files": ["file1.pdf", "file2.pdf"]
}
```

### Get Job Status
```bash
GET /api/v1/jobs/{job_id}
```

Response:
```json
{
  "id": "uuid",
  "status": "processing|completed|failed",
  "progress": 50,
  "total_questions": 100,
  "processed_pages": 25,
  "error_message": null
}
```

### Search Questions
```bash
GET /api/v1/search?q=binary+search&limit=10&subject=DSA&year=2023
```

Response:
```json
{
  "query": "binary search",
  "results": [
    {
      "id": "uuid",
      "content": "Explain binary search algorithm",
      "score": 0.95,
      "subject": "DSA",
      "topic": "Searching",
      "difficulty": "medium",
      "year": 2023,
      "marks": 5
    }
  ],
  "total": 1
}
```

## Database Schema

### Jobs Table
- `id`: UUID (primary key)
- `status`: queued|processing|completed|failed
- `file_names`: Comma-separated filenames
- `progress`: 0-100
- `total_questions`: Count of extracted questions
- `error_message`: Error details if failed

### Documents Table
- `id`: UUID (primary key)
- `job_id`: Foreign key to jobs
- `filename`: Original filename
- `file_hash`: SHA-256 hash
- `page_count`: Number of pages

### Questions Table
- `id`: UUID (primary key)
- `document_id`: Foreign key to documents
- `content`: Question text
- `qdrant_id`: Vector DB point ID
- `subject`, `topic`, `difficulty`, `question_type`, `year`, `marks`: Metadata

## Development Status

### Completed (Tasks 1-16)
- ✅ Project setup with uv
- ✅ Docker Compose infrastructure
- ✅ Database configuration (async PostgreSQL)
- ✅ SQLAlchemy models
- ✅ Alembic migrations
- ✅ FastAPI application
- ✅ Pydantic schemas
- ✅ Upload API endpoint
- ✅ Celery task queue setup
- ✅ PDF processing task (stub)
- ✅ LlamaCloud service (stub)
- ✅ Embedding service
- ✅ Qdrant service
- ✅ Search service
- ✅ Search API endpoint
- ✅ Job status endpoint
- ✅ Manual test script

### TODO (Next Phase)
- ❌ Integrate LlamaCloud PDF extraction
- ❌ Implement question parsing logic
- ❌ Connect upload endpoint to Celery task
- ❌ Generate and index embeddings
- ❌ End-to-end integration testing
- ❌ Production logging and monitoring
- ❌ Error handling improvements
- ❌ Rate limiting
- ❌ Authentication/Authorization

## Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/qp_search
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
QDRANT_HOST=localhost
QDRANT_PORT=6333
LLAMA_API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here
```

## Troubleshooting

### Database connection issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
psql -U postgres -h localhost -d qp_search -c "SELECT 1"
```

### Redis connection issues
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli ping
```

### Qdrant connection issues
```bash
# Check Qdrant is running
docker-compose ps qdrant

# Test connection
curl http://localhost:6333/health
```

## License

MIT
