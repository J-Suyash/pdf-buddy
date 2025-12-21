# Question Paper Search Engine - Project Specification for Claude Code

## Project Overview
Build a production-grade question paper search engine that demonstrates backend engineering excellence with AI integration. The system allows users to upload university question papers (PDFs), processes them asynchronously using LlamaCloud's extraction API, and provides semantic search capabilities through a vector database.

## Tech Stack

### Backend (Primary Focus)
- **Python 3.11+** managed with `uv`
- **FastAPI** - Async web framework
- **Celery** - Distributed task queue
- **Redis** - Message broker + caching
- **PostgreSQL** - Relational data (jobs, metadata)
- **Qdrant** - Vector database for semantic search
- **LlamaCloud SDK** - PDF extraction
- **Sentence Transformers** - Embedding generation
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **Pydantic v2** - Data validation
- **pytest** - Testing framework

### Frontend (Secondary)
- **React 18** with TypeScript
- **Vite** - Build tool
- **shadcn/ui** - Component library (NOT Tailwind directly)
- **TanStack Query** - Data fetching
- **Zustand** - State management

### DevOps
- **Docker** + **Docker Compose** - Containerization
- **Poetry/uv** - Dependency management (prefer uv)
- **Ruff** - Linting and formatting
- **pre-commit** - Git hooks

## Project Structure

```
question-paper-search/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry
│   │   ├── config.py               # Configuration management
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py
│   │   │   │   ├── upload.py       # Upload endpoints
│   │   │   │   ├── jobs.py         # Job status endpoints
│   │   │   │   ├── search.py       # Search endpoints
│   │   │   │   └── analytics.py    # Analytics endpoints
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── database.py         # PostgreSQL connection
│   │   │   ├── redis.py            # Redis connection
│   │   │   ├── qdrant.py           # Qdrant client
│   │   │   └── security.py         # Rate limiting, validation
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── job.py              # Job SQLAlchemy model
│   │   │   ├── question.py         # Question model
│   │   │   └── document.py         # Document metadata model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── job.py              # Pydantic schemas
│   │   │   ├── question.py
│   │   │   └── search.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llama_service.py    # LlamaCloud integration
│   │   │   ├── embedding_service.py # Embedding generation
│   │   │   ├── search_service.py   # Search logic
│   │   │   └── cache_service.py    # Caching layer
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py       # Celery configuration
│   │   │   ├── pdf_processor.py    # PDF processing tasks
│   │   │   └── indexing.py         # Vector indexing tasks
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── file_handler.py
│   │       ├── logger.py
│   │       └── exceptions.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py             # Pytest fixtures
│   │   ├── test_api/
│   │   │   ├── test_upload.py
│   │   │   ├── test_jobs.py
│   │   │   └── test_search.py
│   │   ├── test_services/
│   │   │   ├── test_llama_service.py
│   │   │   └── test_search_service.py
│   │   └── test_tasks/
│   │       └── test_pdf_processor.py
│   ├── scripts/
│   │   ├── test_api.py             # Manual API testing script
│   │   ├── seed_data.py            # Sample data seeding
│   │   └── benchmark.py            # Performance testing
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── pyproject.toml              # uv/poetry config
│   ├── alembic.ini
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn components
│   │   │   ├── upload/
│   │   │   ├── search/
│   │   │   └── jobs/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── App.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Implementation Phases

### Phase 1: Backend Foundation (Week 1)

#### 1.1 Project Setup
- Initialize project with `uv init`
- Setup PostgreSQL, Redis, Qdrant via Docker Compose
- Configure FastAPI with async support
- Setup SQLAlchemy 2.0 with asyncpg
- Configure Alembic for migrations
- Setup logging and configuration management

**Commands to use:**
```bash
# Initialize with uv
uv init backend
cd backend
uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic redis qdrant-client celery python-multipart
uv add --dev pytest pytest-asyncio httpx ruff

# Run services
docker-compose up -d postgres redis qdrant

# Database migrations
uv run alembic init alembic
uv run alembic revision --autogenerate -m "initial"
uv run alembic upgrade head

# Start FastAPI
uv run uvicorn app.main:app --reload
```

#### 1.2 Database Models
Create SQLAlchemy models:
- `Job`: id, status, created_at, updated_at, file_names, error_message, progress
- `Document`: id, job_id, filename, file_hash, page_count, processed_at
- `Question`: id, document_id, content, metadata (year, subject, type), qdrant_id

#### 1.3 API Endpoints - Upload Flow
```
POST /api/v1/upload
- Accept single/multiple PDF files
- Validate file types and sizes
- Generate unique job_id
- Store files temporarily
- Create Job record in PostgreSQL
- Queue Celery task
- Return job_id and status URL

Response:
{
  "job_id": "uuid",
  "status": "queued",
  "status_url": "/api/v1/jobs/{job_id}",
  "files": ["file1.pdf", "file2.pdf"]
}
```

**Testing approach:**
```bash
# Create test_api.py script
uv run python scripts/test_api.py

# Or use curl
curl -X POST http://localhost:8000/api/v1/upload \
  -F "files=@sample.pdf" \
  -F "files=@sample2.pdf"
```

#### 1.4 Job Status Endpoint
```
GET /api/v1/jobs/{job_id}
- Fetch job from PostgreSQL
- Return current status with details

Response:
{
  "job_id": "uuid",
  "status": "processing",  # queued, processing, completed, failed
  "progress": 45,
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "files": [...],
  "results": {
    "total_questions": 120,
    "processed_pages": 15
  },
  "error": null
}
```

### Phase 2: LlamaCloud Integration & Task Processing (Week 1-2)

#### 2.1 Celery Setup
```python
# tasks/celery_app.py
from celery import Celery

celery_app = Celery(
    "qp_search",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
)
```

**Run Celery worker:**
```bash
uv run celery -A app.tasks.celery_app worker --loglevel=info -P threads
```

#### 2.2 LlamaCloud Service
```python
# services/llama_service.py
class LlamaCloudService:
    async def extract_from_pdf(self, pdf_path: str) -> dict:
        """
        Extract structured data from PDF using LlamaCloud API
        Returns: {
            "pages": [...],
            "questions": [...],
            "metadata": {...}
        }
        """
        # Implement LlamaCloud API calls
        # Handle rate limiting
        # Implement retry logic with exponential backoff
        pass
```

#### 2.3 PDF Processing Task
```python
# tasks/pdf_processor.py
@celery_app.task(bind=True, max_retries=3)
def process_pdf_task(self, job_id: str, file_paths: list):
    """
    1. Update job status to 'processing'
    2. For each PDF:
       a. Call LlamaCloud extraction
       b. Parse and structure questions
       c. Store in PostgreSQL
       d. Update progress
    3. Trigger embedding task
    4. Update job status to 'completed'
    """
    try:
        # Implementation
        pass
    except Exception as exc:
        # Update job with error
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

**Testing:**
Create `scripts/test_tasks.py`:
```python
from app.tasks.pdf_processor import process_pdf_task

# Test with sample PDF
result = process_pdf_task.delay("test-job-id", ["samples/test.pdf"])
print(f"Task ID: {result.id}")
print(f"Status: {result.status}")
```

#### 2.4 Question Parsing & Structuring
```python
# Use LLM to categorize extracted questions
{
    "question_text": "...",
    "subject": "Data Structures",
    "topic": "Binary Trees",
    "difficulty": "medium",
    "type": "descriptive",
    "year": 2023,
    "marks": 5
}
```

### Phase 3: Vector Search Implementation (Week 2)

#### 3.1 Embedding Service
```python
# services/embedding_service.py
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def generate_embedding(self, text: str) -> list[float]:
        """Generate 384-dim embedding"""
        return self.model.encode(text).tolist()
    
    async def batch_generate(self, texts: list[str]) -> list[list[float]]:
        """Batch processing for efficiency"""
        pass
```

#### 3.2 Qdrant Integration
```python
# core/qdrant.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(host="localhost", port=6333)
        self.collection_name = "questions"
    
    async def create_collection(self):
        """Create collection with 384-dim vectors"""
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
    
    async def index_questions(self, questions: list[dict]):
        """Batch insert questions with embeddings"""
        points = [
            PointStruct(
                id=q["id"],
                vector=q["embedding"],
                payload={
                    "question_id": q["id"],
                    "text": q["text"],
                    "subject": q["subject"],
                    "year": q["year"],
                    # ... other metadata
                }
            )
            for q in questions
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)
```

#### 3.3 Indexing Task
```python
# tasks/indexing.py
@celery_app.task
def index_questions_task(job_id: str):
    """
    1. Fetch all questions for job from PostgreSQL
    2. Generate embeddings in batches
    3. Index in Qdrant with metadata
    4. Update job status
    """
    pass
```

#### 3.4 Search API
```
GET /api/v1/search?q=binary+tree+traversal&limit=10&filters[subject]=DS&filters[year]=2023

Response:
{
    "query": "binary tree traversal",
    "results": [
        {
            "id": "uuid",
            "question": "...",
            "score": 0.87,
            "metadata": {
                "subject": "Data Structures",
                "year": 2023,
                "difficulty": "medium"
            },
            "document": {
                "filename": "DS_2023.pdf",
                "page": 3
            }
        }
    ],
    "total": 45,
    "took_ms": 23
}
```

#### 3.5 Search Service with Caching
```python
# services/search_service.py
class SearchService:
    async def semantic_search(
        self, 
        query: str, 
        limit: int = 10,
        filters: dict = None
    ):
        """
        1. Check Redis cache
        2. Generate query embedding
        3. Search Qdrant with filters
        4. Fetch full question details from PostgreSQL
        5. Cache results
        6. Return enriched results
        """
        # Implement hybrid search (semantic + keyword)
        pass
```

**Testing search:**
```bash
# Create comprehensive test script
uv run python scripts/test_search.py

# Or curl
curl "http://localhost:8000/api/v1/search?q=explain+quicksort&limit=5"
```

### Phase 4: Advanced Features (Week 2-3)

#### 4.1 Analytics Endpoint
```
GET /api/v1/analytics

Response:
{
    "jobs": {
        "total": 234,
        "completed": 220,
        "failed": 5,
        "avg_processing_time_sec": 45.3
    },
    "questions": {
        "total": 12450,
        "by_subject": {...},
        "by_year": {...}
    },
    "search": {
        "total_queries": 5678,
        "avg_response_time_ms": 23.5,
        "popular_queries": [...]
    }
}
```

#### 4.2 Duplicate Detection
```python
# Check file hash before processing
# Detect similar questions using embeddings (cosine similarity > 0.95)
```

#### 4.3 Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/upload")
@limiter.limit("10/hour")
async def upload_files(...):
    pass
```

#### 4.4 Enhanced Search Features
- Autocomplete suggestions
- Related questions
- Question clustering by topic
- Export search results

### Phase 5: Testing & Quality (Week 3)

#### 5.1 Unit Tests
```bash
# Run all tests
uv run pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_api/test_search.py -v

# Run with markers
uv run pytest -m "not slow" -v
```

#### 5.2 Integration Tests
Test complete workflows:
- Upload → Process → Index → Search
- Error handling and retries
- Concurrent uploads

#### 5.3 Performance Testing
```python
# scripts/benchmark.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

async def benchmark_search(queries: list[str]):
    """Test search performance under load"""
    # Implement load testing
    pass

async def benchmark_upload():
    """Test upload and processing performance"""
    pass
```

#### 5.4 API Documentation
```python
# main.py - FastAPI auto-generates OpenAPI docs
app = FastAPI(
    title="Question Paper Search API",
    description="Semantic search engine for university question papers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

Access: `http://localhost:8000/docs`

### Phase 6: Frontend Integration (Week 4)

#### 6.1 Setup React + shadcn
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install

# Add shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input textarea
npx shadcn-ui@latest add dialog dropdown-menu tabs
npx shadcn-ui@latest add progress badge alert
```

#### 6.2 Core Components
- `UploadZone`: Drag-drop PDF upload with progress
- `JobStatusCard`: Real-time job status with progress bar
- `SearchBar`: Search input with filters
- `QuestionCard`: Display search results
- `AnalyticsDashboard`: Charts and metrics

#### 6.3 State Management
Use Zustand for:
- Active jobs tracking
- Search state
- User preferences

#### 6.4 Real-time Updates
Implement Server-Sent Events or WebSocket for job status updates

### Phase 7: Production Ready (Week 4)

#### 7.1 Docker Compose
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: qp_search
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  backend:
    build: ./backend
    command: uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - qdrant
    environment:
      - DATABASE_URL=postgresql+asyncpg://admin:secret@postgres/qp_search
      - REDIS_URL=redis://redis:6379
      - QDRANT_HOST=qdrant

  celery_worker:
    build: ./backend
    command: uv run celery -A app.tasks.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
      - qdrant

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
  qdrant_data:
```

#### 7.2 Configuration Management
```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    qdrant_host: str
    qdrant_port: int = 6333
    llama_api_key: str
    secret_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### 7.3 Logging & Monitoring
```python
# utils/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger("qp_search")
    logger.setLevel(logging.INFO)
    
    handler = RotatingFileHandler(
        "logs/app.log", 
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

#### 7.4 Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_db(),
        "redis": await check_redis(),
        "qdrant": await check_qdrant(),
        "celery": await check_celery_workers()
    }
```

## Testing Strategy

### Manual Testing Scripts
Never use `python3 -c "..."`. Always create proper test files:

```python
# scripts/test_api.py
import asyncio
import httpx
from pathlib import Path

async def test_upload():
    async with httpx.AsyncClient() as client:
        files = {
            'files': ('test.pdf', open('samples/test.pdf', 'rb'), 'application/pdf')
        }
        response = await client.post(
            'http://localhost:8000/api/v1/upload',
            files=files
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()

async def test_job_status(job_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'http://localhost:8000/api/v1/jobs/{job_id}'
        )
        print(f"Job Status: {response.json()}")

async def test_search(query: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'http://localhost:8000/api/v1/search',
            params={'q': query, 'limit': 10}
        )
        print(f"Search Results: {response.json()}")

async def main():
    # Test upload
    result = await test_upload()
    job_id = result['job_id']
    
    # Wait and check status
    await asyncio.sleep(2)
    await test_job_status(job_id)
    
    # Test search (after processing completes)
    await asyncio.sleep(10)
    await test_search("binary tree")

if __name__ == "__main__":
    asyncio.run(main())
```

Run: `uv run python scripts/test_api.py`

### curl Testing Examples
```bash
# Upload
curl -X POST http://localhost:8000/api/v1/upload \
  -F "files=@samples/test.pdf" \
  -v

# Job Status
curl http://localhost:8000/api/v1/jobs/JOB_ID_HERE | jq

# Search
curl "http://localhost:8000/api/v1/search?q=sorting+algorithms&limit=5" | jq

# Analytics
curl http://localhost:8000/api/v1/analytics | jq
```

### Automated Tests
```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test categories
uv run pytest tests/test_api/ -v
uv run pytest tests/test_services/ -v
uv run pytest tests/test_tasks/ -v

# Run with markers
uv run pytest -m "integration" -v
uv run pytest -m "unit" -v
```

## Key Implementation Notes

### 1. Always Use uv
```bash
# Install dependencies
uv add package-name

# Run scripts
uv run python script.py
uv run uvicorn app.main:app
uv run celery -A app.tasks.celery_app worker

# Run tests
uv run pytest

# Format code
uv run ruff check .
uv run ruff format .
```

### 2. Error Handling Pattern
```python
from app.utils.exceptions import (
    LlamaCloudException,
    EmbeddingException,
    SearchException
)

@router.post("/upload")
async def upload_files(...):
    try:
        # Implementation
        pass
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 3. Async Best Practices
```python
# Use async/await consistently
async def process_documents(docs: list[Document]):
    tasks = [process_single_doc(doc) for doc in docs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# Use async context managers
async with aiofiles.open('file.txt', 'r') as f:
    content = await f.read()
```

### 4. Database Operations
```python
# Always use async sessions
async with AsyncSession(engine) as session:
    async with session.begin():
        result = await session.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
```

### 5. Testing Database Operations
```python
# conftest.py
@pytest.fixture
async def db_session():
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()

# test file
async def test_create_job(db_session):
    job = Job(id="test-id", status="queued")
    db_session.add(job)
    await db_session.commit()
    
    result = await db_session.execute(select(Job).where(Job.id == "test-id"))
    assert result.scalar_one().status == "queued"
```

## Success Metrics

Your resume project should demonstrate:

✅ **Backend Architecture**: FastAPI, async patterns, task queues, microservices design
✅ **AI Integration**: LLM API usage, embeddings, vector search
✅ **Database Design**: PostgreSQL with proper relationships, vector database usage
✅ **Testing**: Comprehensive unit and integration tests with >80% coverage
✅ **Production Ready**: Docker, logging, monitoring, error handling
✅ **Code Quality**: Type hints, documentation, linting, formatting
✅ **Performance**: Caching, batch processing, efficient queries
✅ **API Design**: RESTful, versioned, well-documented

## Documentation Deliverables

1. **README.md**: Architecture overview, setup instructions, API usage
2. **API_DOCS.md**: Detailed endpoint documentation with examples
3. **ARCHITECTURE.md**: System design, data flow, scaling considerations
4. **DEPLOYMENT.md**: Docker setup, environment variables, production checklist

## Resume Talking Points

- "Built a production-grade semantic search engine processing 1000+ question papers"
- "Implemented async task orchestration with Celery handling 100+ concurrent PDF extractions"
- "Integrated LLM APIs with retry logic and rate limiting for 99.9% reliability"
- "Designed vector search system using Qdrant achieving <50ms query latency"
- "Achieved 85%+ test coverage with pytest for all critical paths"
- "Containerized multi-service application with Docker Compose"
- "Implemented hybrid search combining semantic similarity and metadata filtering"

## Getting Started Commands

```bash
# Clone and setup
git clone <repo>
cd question-paper-search

# Start infrastructure
docker-compose up -d postgres redis qdrant

# Setup backend
cd backend
uv sync
uv run alembic upgrade head

# Start backend
uv run uvicorn app.main:app --reload

# Start Celery worker (separate terminal)
uv run celery -A app.tasks.celery_app worker --loglevel=info

# Run tests
uv run pytest tests/ -v

# Setup frontend
cd ../frontend
npm install
npm run dev
```

Access:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Qdrant Dashboard: http://localhost:6333/dashboard

Now you're ready to build! Focus on backend first, test thoroughly, and iterate.