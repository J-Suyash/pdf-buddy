# Backend MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Build a working semantic search engine backend that accepts PDF uploads, extracts questions via LlamaCloud, embeds them with Sentence Transformers, indexes in Qdrant, and serves semantic search results.

**Architecture:** FastAPI server with async PostgreSQL for job/question tracking, Redis for caching via Celery task queue, LlamaCloud for PDF extraction, Sentence Transformers for embeddings, and Qdrant for vector search. Minimal frontend integration—focus on robust APIs and core backend features.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.0, asyncpg, Celery, Redis, PostgreSQL, Qdrant, LlamaCloud SDK, Sentence Transformers, pytest.

**Execution Timeline:** 3-4 days of focused development for full MVP.

---

## Phase 1: Project Setup & Infrastructure

### Task 1: Initialize Backend Project with uv

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/.env.example`

**Step 1: Initialize project with uv**

```bash
cd /home/sxtr/Projects/pdf-buddy
mkdir -p backend
cd backend
uv init --name qp-search
```

Expected: Creates `pyproject.toml` with `[project]` metadata

**Step 2: Add core dependencies**

```bash
uv add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" asyncpg alembic redis qdrant-client celery python-multipart aiofiles pydantic-settings
```

**Step 3: Add dev dependencies**

```bash
uv add --dev pytest pytest-asyncio pytest-cov httpx ruff pre-commit
```

**Step 4: Create app package**

```bash
mkdir -p app
touch app/__init__.py
```

**Step 5: Create .env.example**

```bash
cat > .env.example << 'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/qp_search
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
QDRANT_HOST=localhost
QDRANT_PORT=6333
LLAMA_API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here
EOF
```

**Step 6: Copy .env.example to .env for local development**

```bash
cp .env.example .env
# User will fill in LLAMA_API_KEY manually
```

**Step 7: Verify project structure**

```bash
ls -la
# Expected: pyproject.toml, uv.lock, app/, .env, .env.example
```

---

### Task 2: Setup Docker Compose for Infrastructure

**Files:**
- Create: `docker-compose.yml` (project root)

**Step 1: Create docker-compose.yml**

```bash
cat > /home/sxtr/Projects/pdf-buddy/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: qp_search
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT_API_KEY: ${QDRANT_API_KEY:-}

volumes:
  postgres_data:
  qdrant_data:
EOF
```

**Step 2: Start infrastructure**

```bash
docker-compose up -d
```

Expected: All three services start and pass health checks

**Step 3: Verify connectivity**

```bash
# Test PostgreSQL
psql -U postgres -h localhost -d qp_search -c "SELECT 1"

# Test Redis
redis-cli ping

# Test Qdrant
curl http://localhost:6333/health
```

**Step 4: Commit**

```bash
cd /home/sxtr/Projects/pdf-buddy
git add docker-compose.yml backend/.env.example backend/.env
git commit -m "chore: setup docker compose infrastructure"
```

---

## Phase 2: Database Setup & Models

### Task 3: Configure Database Connection

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/database.py`

**Step 1: Create config.py**

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    celery_broker_url: str
    qdrant_host: str
    qdrant_port: int
    llama_api_key: str
    secret_key: str

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
```

**Step 2: Create database.py with async engine**

```python
# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=0,
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db():
    async with async_session() as session:
        yield session

from sqlalchemy.orm import declarative_base
Base = declarative_base()
```

**Step 3: Create core/__init__.py**

```python
# backend/app/core/__init__.py
from app.core.database import engine, async_session, Base, get_db

__all__ = ["engine", "async_session", "Base", "get_db"]
```

**Step 4: Update .env with your database URL (already set by docker-compose)**

**Step 5: Verify imports work**

```bash
cd backend
uv run python -c "from app.config import settings; print(f'DB: {settings.database_url}')"
```

Expected: Prints database URL without errors

**Step 6: Commit**

```bash
git add backend/app/config.py backend/app/core/
git commit -m "feat: setup async database configuration"
```

---

### Task 4: Create SQLAlchemy Models

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/job.py`
- Create: `backend/app/models/document.py`
- Create: `backend/app/models/question.py`

**Step 1: Create job.py model**

```python
# backend/app/models/job.py
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base

class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(20), default=JobStatus.QUEUED.value, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    file_names = Column(String(500), nullable=False)  # Comma-separated
    error_message = Column(Text, nullable=True)
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    total_questions = Column(Integer, default=0)
    processed_pages = Column(Integer, default=0)

    # Relationships
    documents = relationship("Document", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job {self.id}: {self.status}>"
```

**Step 2: Create document.py model**

```python
# backend/app/models/document.py
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=True)  # SHA-256
    page_count = Column(Integer, default=0)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    job = relationship("Job", back_populates="documents")
    questions = relationship("Question", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document {self.id}: {self.filename}>"
```

**Step 3: Create question.py model**

```python
# backend/app/models/question.py
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    qdrant_id = Column(Integer, nullable=True)  # Qdrant point ID

    # Metadata
    subject = Column(String(100), nullable=True)
    topic = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=True)  # easy, medium, hard
    question_type = Column(String(50), nullable=True)  # descriptive, mcq, etc
    year = Column(Integer, nullable=True)
    marks = Column(Integer, nullable=True)
    page_number = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="questions")

    def __repr__(self):
        return f"<Question {self.id}: {self.subject}>"
```

**Step 4: Create models/__init__.py**

```python
# backend/app/models/__init__.py
from app.models.job import Job, JobStatus
from app.models.document import Document
from app.models.question import Question

__all__ = ["Job", "JobStatus", "Document", "Question"]
```

**Step 5: Verify models import**

```bash
uv run python -c "from app.models import Job, Document, Question; print('Models imported successfully')"
```

Expected: No errors

**Step 6: Commit**

```bash
git add backend/app/models/
git commit -m "feat: create sqlalchemy models for jobs, documents, questions"
```

---

### Task 5: Setup Alembic for Migrations

**Files:**
- Modify: `backend/alembic/env.py`
- Create: `backend/alembic/versions/001_initial.py` (auto-generated)

**Step 1: Initialize Alembic**

```bash
cd backend
uv run alembic init alembic
```

Expected: Creates `alembic/` directory with env.py, script.py.mako, etc.

**Step 2: Configure alembic/env.py to use async**

```python
# backend/alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.core.database import Base
from app.config import settings

# this is the Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Run migrations with a connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

**Step 3: Generate initial migration**

```bash
uv run alembic revision --autogenerate -m "initial schema"
```

Expected: Creates `alembic/versions/xxx_initial_schema.py`

**Step 4: Apply migrations**

```bash
uv run alembic upgrade head
```

Expected: Creates all tables in PostgreSQL without errors

**Step 5: Verify tables created**

```bash
psql -U postgres -h localhost -d qp_search -c "\dt"
```

Expected: Lists jobs, documents, questions tables

**Step 6: Commit**

```bash
git add backend/alembic/ backend/alembic.ini
git commit -m "feat: setup alembic migrations and create initial schema"
```

---

## Phase 3: FastAPI Setup & Upload Endpoint

### Task 6: Create FastAPI Main Application

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/utils/__init__.py`
- Create: `backend/app/utils/exceptions.py`

**Step 1: Create utils/exceptions.py**

```python
# backend/app/utils/exceptions.py
class ApplicationException(Exception):
    """Base exception for application."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class ValidationException(ApplicationException):
    def __init__(self, message: str):
        super().__init__(message, 422)

class LlamaCloudException(ApplicationException):
    def __init__(self, message: str):
        super().__init__(message, 500)

class NotFound(ApplicationException):
    def __init__(self, message: str):
        super().__init__(message, 404)
```

**Step 2: Create main.py**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.utils.exceptions import ApplicationException

# Create tables on startup
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title="Question Paper Search API",
    description="Semantic search engine for university question papers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

@app.exception_handler(ApplicationException)
async def application_exception_handler(request, exc: ApplicationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "qp-search-api",
    }

# API routes will be included here
```

**Step 3: Verify FastAPI starts**

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Expected: Server starts on http://localhost:8000, /docs shows Swagger UI

**Step 4: Test health endpoint**

```bash
curl http://localhost:8000/health
```

Expected: Returns `{"status": "healthy", "service": "qp-search-api"}`

**Step 5: Stop server (Ctrl+C)**

**Step 6: Commit**

```bash
git add backend/app/main.py backend/app/utils/
git commit -m "feat: setup fastapi application with error handling"
```

---

### Task 7: Create Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/job.py`
- Create: `backend/app/schemas/question.py`

**Step 1: Create schemas/job.py**

```python
# backend/app/schemas/job.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.job import JobStatus

class JobResponse(BaseModel):
    id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    file_names: str
    progress: int = Field(ge=0, le=100)
    total_questions: int = 0
    processed_pages: int = 0
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class JobUploadResponse(BaseModel):
    job_id: str
    status: str
    status_url: str
    files: List[str]
```

**Step 2: Create schemas/question.py**

```python
# backend/app/schemas/question.py
from pydantic import BaseModel
from typing import Optional

class QuestionResponse(BaseModel):
    id: str
    content: str
    subject: Optional[str]
    topic: Optional[str]
    difficulty: Optional[str]
    question_type: Optional[str]
    year: Optional[int]
    marks: Optional[int]
    page_number: Optional[int]
    score: Optional[float] = None  # For search results

    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    limit: int = Field(10, ge=1, le=100)
    filters: Optional[dict] = None
```

**Step 3: Create schemas/__init__.py**

```python
# backend/app/schemas/__init__.py
from app.schemas.job import JobResponse, JobUploadResponse
from app.schemas.question import QuestionResponse, SearchQuery

__all__ = ["JobResponse", "JobUploadResponse", "QuestionResponse", "SearchQuery"]
```

**Step 4: Verify schema imports**

```bash
uv run python -c "from app.schemas import JobResponse, QuestionResponse; print('Schemas imported')"
```

Expected: No errors

**Step 5: Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: create pydantic schemas for api responses"
```

---

### Task 8: Create Upload API Endpoint

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/v1/__init__.py`
- Create: `backend/app/api/v1/upload.py`
- Create: `backend/app/api/v1/router.py`
- Modify: `backend/app/main.py`

**Step 1: Create upload.py endpoint**

```python
# backend/app/api/v1/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List
import uuid
import os

from app.core.database import get_db
from app.models import Job, Document, JobStatus
from app.schemas import JobUploadResponse
from app.utils.exceptions import ValidationException

router = APIRouter(prefix="/api/v1", tags=["upload"])

UPLOAD_DIR = "/tmp/qp_uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_TYPES = {"application/pdf"}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=JobUploadResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    db: AsyncSession = None,
):
    """
    Upload one or more PDF files for processing.
    Returns job_id and status URL.
    """
    if not files:
        raise ValidationException("No files provided")

    if len(files) > 10:
        raise ValidationException("Maximum 10 files per upload")

    # Validate files
    filenames = []
    file_paths = []

    for file in files:
        if file.content_type != "application/pdf":
            raise ValidationException(f"{file.filename} is not a PDF")

        if file.size > MAX_FILE_SIZE:
            raise ValidationException(f"{file.filename} exceeds 50MB limit")

        filenames.append(file.filename)

    try:
        # Save files temporarily
        async with AsyncSession(bind=db.bind) as session:
            for file in files:
                content = await file.read()
                file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
                with open(file_path, "wb") as f:
                    f.write(content)
                file_paths.append(file_path)

            # Create job record
            job_id = str(uuid.uuid4())
            job = Job(
                id=job_id,
                status=JobStatus.QUEUED.value,
                file_names=",".join(filenames),
                progress=0,
            )
            session.add(job)
            await session.commit()

        return JobUploadResponse(
            job_id=job_id,
            status="queued",
            status_url=f"/api/v1/jobs/{job_id}",
            files=filenames,
        )

    except Exception as e:
        # Clean up uploaded files on error
        for fpath in file_paths:
            if os.path.exists(fpath):
                os.remove(fpath)
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 2: Create router.py to include all routes**

```python
# backend/app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.upload import router as upload_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(upload_router)
```

**Step 3: Create api/__init__.py and api/v1/__init__.py**

```python
# backend/app/api/__init__.py
```

```python
# backend/app/api/v1/__init__.py
```

**Step 4: Update main.py to include router**

```python
# Add to backend/app/main.py after imports
from app.api.v1.router import api_v1_router

app.include_router(api_v1_router)
```

**Step 5: Test upload endpoint**

```bash
cd backend
uv run uvicorn app.main:app --reload &

# Create test PDF
python3 -c "
from reportlab.pdfgen import canvas
from io import BytesIO

c = canvas.Canvas('/tmp/test.pdf')
c.drawString(100, 750, 'Test PDF')
c.save()
"

# Upload file
curl -X POST http://localhost:8000/api/v1/upload \
  -F "files=@/tmp/test.pdf" | jq
```

Expected: Returns job_id, status "queued", and files list

**Step 6: Verify job in database**

```bash
psql -U postgres -h localhost -d qp_search -c "SELECT id, status, file_names FROM jobs LIMIT 1"
```

Expected: Shows queued job with filename

**Step 7: Stop server (Ctrl+C)**

**Step 8: Commit**

```bash
git add backend/app/api/
git commit -m "feat: implement file upload endpoint"
```

---

## Phase 4: Celery Task Queue Setup

### Task 9: Configure Celery

**Files:**
- Create: `backend/app/tasks/__init__.py`
- Create: `backend/app/tasks/celery_app.py`

**Step 1: Create tasks/celery_app.py**

```python
# backend/app/tasks/celery_app.py
from celery import Celery
from app.config import settings

celery_app = Celery(
    "qp_search",
    broker=settings.celery_broker_url,
    backend=settings.celery_broker_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
```

**Step 2: Create tasks/__init__.py**

```python
# backend/app/tasks/__init__.py
from app.tasks.celery_app import celery_app

__all__ = ["celery_app"]
```

**Step 3: Verify Celery app loads**

```bash
uv run python -c "from app.tasks.celery_app import celery_app; print(f'Celery app: {celery_app.main}')"
```

Expected: No errors

**Step 4: Commit**

```bash
git add backend/app/tasks/
git commit -m "feat: setup celery task queue"
```

---

### Task 10: Create PDF Processing Task (Stub)

**Files:**
- Create: `backend/app/tasks/pdf_processor.py`

**Step 1: Create pdf_processor.py with stub task**

```python
# backend/app/tasks/pdf_processor.py
from app.tasks.celery_app import celery_app
from app.core.database import async_session
from app.models import Job, JobStatus
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, name="process_pdf_task")
def process_pdf_task(self, job_id: str, file_paths: list):
    """
    Process PDF files:
    1. Update job status to processing
    2. Extract text from PDF (stub for now)
    3. Store questions in database
    4. Trigger embedding task
    5. Update job status to completed
    """
    import asyncio
    from app.models import Job, JobStatus

    try:
        # Run async function
        asyncio.run(_process_pdf_async(job_id, file_paths))
        return {"status": "completed", "job_id": job_id}

    except Exception as exc:
        logger.error(f"PDF processing failed for job {job_id}: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

async def _process_pdf_async(job_id: str, file_paths: list):
    """Async helper for PDF processing."""
    async with async_session() as session:
        try:
            # Update status to processing
            from sqlalchemy import select, update
            await session.execute(
                update(Job).where(Job.id == job_id).values(status=JobStatus.PROCESSING.value)
            )
            await session.commit()

            logger.info(f"Started processing {len(file_paths)} files for job {job_id}")

            # TODO: Implement LlamaCloud extraction
            # For now, just mark as completed

            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status=JobStatus.COMPLETED.value,
                    progress=100
                )
            )
            await session.commit()

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status=JobStatus.FAILED.value,
                    error_message=str(e)
                )
            )
            await session.commit()
            raise
```

**Step 2: Verify task loads**

```bash
uv run python -c "from app.tasks.pdf_processor import process_pdf_task; print('Task loaded')"
```

Expected: No errors

**Step 3: Commit**

```bash
git add backend/app/tasks/pdf_processor.py
git commit -m "feat: create pdf processing task stub"
```

---

## Phase 5: Core Services

### Task 11: Create LlamaCloud Service

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/llama_service.py`

**Step 1: Create llama_service.py**

```python
# backend/app/services/llama_service.py
from llama_cloud.client import LlamaCloud
from app.config import settings
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class LlamaCloudService:
    def __init__(self):
        self.client = LlamaCloud(api_key=settings.llama_api_key)

    async def extract_from_pdf(self, file_path: str) -> Dict:
        """
        Extract structured data from PDF using LlamaCloud API.

        Returns:
        {
            "text": "full text content",
            "pages": [...],
            "metadata": {...}
        }
        """
        try:
            logger.info(f"Extracting from PDF: {file_path}")

            # Upload file to LlamaCloud
            with open(file_path, 'rb') as f:
                file_handle = self.client.upload_file(f)

            # Extract content
            result = self.client.get_document_transform(
                file_handle.id,
                mode="markdown"
            )

            return {
                "text": result.get("markdown", ""),
                "pages": result.get("pages", []),
                "metadata": result.get("metadata", {})
            }

        except Exception as e:
            logger.error(f"LlamaCloud extraction failed: {e}")
            raise

    async def extract_questions_from_text(self, text: str) -> List[Dict]:
        """
        Parse extracted text to find questions.
        This is a simple implementation - can be enhanced with LLM later.
        """
        # Simple split by common patterns
        questions = []
        lines = text.split('\n')

        current_question = ""
        for line in lines:
            # Match question patterns (Q1., Question 1, etc.)
            if any(marker in line for marker in ["Q.", "Question ", "Ques.", "q."]):
                if current_question:
                    questions.append({
                        "content": current_question.strip(),
                        "subject": None,
                        "topic": None,
                        "difficulty": None,
                        "question_type": "unknown",
                        "year": None,
                        "marks": None,
                    })
                current_question = line
            else:
                current_question += "\n" + line

        if current_question:
            questions.append({
                "content": current_question.strip(),
                "subject": None,
                "topic": None,
                "difficulty": None,
                "question_type": "unknown",
                "year": None,
                "marks": None,
            })

        return questions

llama_service = LlamaCloudService()
```

**Step 2: Create services/__init__.py**

```python
# backend/app/services/__init__.py
from app.services.llama_service import llama_service

__all__ = ["llama_service"]
```

**Step 3: Verify service loads with API key**

```bash
uv run python -c "from app.services.llama_service import llama_service; print('LlamaCloud service loaded')"
```

Expected: No errors (API key is validated in .env)

**Step 4: Commit**

```bash
git add backend/app/services/
git commit -m "feat: create llama cloud extraction service"
```

---

### Task 12: Create Embedding Service

**Files:**
- Create: `backend/app/services/embedding_service.py`

**Step 1: Add sentence-transformers dependency**

```bash
cd backend
uv add sentence-transformers
```

**Step 2: Create embedding_service.py**

```python
# backend/app/services/embedding_service.py
from sentence_transformers import SentenceTransformer
import logging
from typing import List

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        logger.info("Loading sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate 384-dimensional embedding for text.
        """
        if not text or not text.strip():
            return [0.0] * self.embedding_dim

        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    async def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        """
        if not texts:
            return []

        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            return [[0.0] * self.embedding_dim] * len(texts)

        embeddings = self.model.encode(valid_texts, convert_to_tensor=False)
        return embeddings.tolist()

embedding_service = EmbeddingService()
```

**Step 3: Update services/__init__.py**

```python
# backend/app/services/__init__.py
from app.services.llama_service import llama_service
from app.services.embedding_service import embedding_service

__all__ = ["llama_service", "embedding_service"]
```

**Step 4: Test embedding generation**

```bash
uv run python << 'EOF'
from app.services.embedding_service import embedding_service
embedding = embedding_service.generate_embedding("What is binary search?")
print(f"Embedding dimension: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")
EOF
```

Expected: Shows 384-dimensional embedding

**Step 5: Commit**

```bash
git add backend/app/services/embedding_service.py
git commit -m "feat: create sentence transformers embedding service"
```

---

### Task 13: Create Qdrant Service

**Files:**
- Create: `backend/app/core/qdrant.py`

**Step 1: Create qdrant.py**

```python
# backend/app/core/qdrant.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            timeout=30
        )
        self.collection_name = "questions"
        self.vector_size = 384
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        try:
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except:
            logger.info(f"Creating collection '{self.collection_name}'...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

    async def index_questions(self, questions: List[Dict]) -> int:
        """
        Index questions with embeddings into Qdrant.

        Args:
            questions: List of dicts with id, vector (embedding), question_id, text, metadata

        Returns:
            Number of indexed points
        """
        if not questions:
            return 0

        points = []
        for idx, q in enumerate(questions):
            point = PointStruct(
                id=idx,  # Simple sequential ID for MVP
                vector=q.get("vector", [0.0] * self.vector_size),
                payload={
                    "question_id": q.get("question_id"),
                    "text": q.get("text", ""),
                    "subject": q.get("subject"),
                    "topic": q.get("topic"),
                    "difficulty": q.get("difficulty"),
                    "question_type": q.get("question_type"),
                    "year": q.get("year"),
                    "marks": q.get("marks"),
                    "document_id": q.get("document_id"),
                    "page_number": q.get("page_number"),
                }
            )
            points.append(point)

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Indexed {len(points)} questions into Qdrant")
            return len(points)
        except Exception as e:
            logger.error(f"Failed to index questions: {e}")
            raise

    async def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar questions using semantic similarity.
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )

            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    async def delete_collection(self):
        """Delete collection for testing/reset."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
        except:
            pass

qdrant_service = QdrantService()
```

**Step 2: Update core/__init__.py**

```python
# backend/app/core/__init__.py
from app.core.database import engine, async_session, Base, get_db
from app.core.qdrant import qdrant_service

__all__ = ["engine", "async_session", "Base", "get_db", "qdrant_service"]
```

**Step 3: Test Qdrant connection**

```bash
uv run python -c "from app.core.qdrant import qdrant_service; print('Qdrant connected')"
```

Expected: No errors, Qdrant client connected

**Step 4: Commit**

```bash
git add backend/app/core/qdrant.py
git commit -m "feat: create qdrant vector database service"
```

---

## Phase 6: Search Functionality

### Task 14: Create Search Service

**Files:**
- Create: `backend/app/services/search_service.py`

**Step 1: Create search_service.py**

```python
# backend/app/services/search_service.py
from app.services.embedding_service import embedding_service
from app.core.qdrant import qdrant_service
from app.core.database import async_session
from app.models import Question
from sqlalchemy import select
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class SearchService:
    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Semantic search for questions.

        1. Generate embedding for query
        2. Search Qdrant for similar vectors
        3. Fetch full details from PostgreSQL
        4. Return results
        """
        try:
            logger.info(f"Searching for: {query}")

            # Generate query embedding
            query_embedding = embedding_service.generate_embedding(query)

            # Search in Qdrant
            qdrant_results = await qdrant_service.search(
                query_vector=query_embedding,
                limit=limit,
                filters=filters
            )

            if not qdrant_results:
                return {
                    "query": query,
                    "results": [],
                    "total": 0,
                    "took_ms": 0
                }

            # Fetch full question details from PostgreSQL
            async with async_session() as session:
                question_ids = [r["payload"]["question_id"] for r in qdrant_results]
                stmt = select(Question).where(Question.id.in_(question_ids))
                db_result = await session.execute(stmt)
                questions_map = {q.id: q for q in db_result.scalars().all()}

            # Combine results
            results = []
            for qdrant_result in qdrant_results:
                q_id = qdrant_result["payload"]["question_id"]
                question = questions_map.get(q_id)

                if question:
                    results.append({
                        "id": question.id,
                        "content": question.content,
                        "score": qdrant_result["score"],
                        "subject": question.subject,
                        "topic": question.topic,
                        "difficulty": question.difficulty,
                        "question_type": question.question_type,
                        "year": question.year,
                        "marks": question.marks,
                        "page_number": question.page_number,
                    })

            return {
                "query": query,
                "results": results,
                "total": len(results),
            }

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

search_service = SearchService()
```

**Step 2: Update services/__init__.py**

```python
# backend/app/services/__init__.py
from app.services.llama_service import llama_service
from app.services.embedding_service import embedding_service
from app.services.search_service import search_service

__all__ = ["llama_service", "embedding_service", "search_service"]
```

**Step 3: Commit**

```bash
git add backend/app/services/search_service.py
git commit -m "feat: create semantic search service"
```

---

### Task 15: Create Search API Endpoint

**Files:**
- Create: `backend/app/api/v1/search.py`
- Modify: `backend/app/api/v1/router.py`

**Step 1: Create search.py endpoint**

```python
# backend/app/api/v1/search.py
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
import logging

from app.services.search_service import search_service
from app.utils.exceptions import ValidationException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["search"])

@router.get("/search")
async def search(
    q: str = Query(..., min_length=3, max_length=500, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Number of results"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    year: Optional[int] = Query(None, description="Filter by year"),
):
    """
    Semantic search for questions.

    Returns top matching questions based on semantic similarity.
    """
    try:
        filters = {}
        if subject:
            filters["subject"] = subject
        if year:
            filters["year"] = year

        results = await search_service.semantic_search(
            query=q,
            limit=limit,
            filters=filters if filters else None
        )

        return results

    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")
```

**Step 2: Update router.py to include search**

```python
# backend/app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.upload import router as upload_router
from app.api.v1.search import router as search_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(upload_router)
api_v1_router.include_router(search_router)
```

**Step 3: Commit**

```bash
git add backend/app/api/v1/search.py
git commit -m "feat: create search api endpoint"
```

---

### Task 16: Create Job Status Endpoint

**Files:**
- Create: `backend/app/api/v1/jobs.py`
- Modify: `backend/app/api/v1/router.py`

**Step 1: Create jobs.py endpoint**

```python
# backend/app/api/v1/jobs.py
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import async_session
from app.models import Job
from app.schemas import JobResponse
from app.utils.exceptions import NotFound

router = APIRouter(prefix="/api/v1", tags=["jobs"])

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """
    Get the current status of a PDF processing job.
    """
    async with async_session() as session:
        stmt = select(Job).where(Job.id == job_id)
        result = await session.execute(stmt)
        job = result.scalar_one_or_none()

        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        return job
```

**Step 2: Update router.py**

```python
# backend/app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.upload import router as upload_router
from app.api.v1.search import router as search_router
from app.api.v1.jobs import router as jobs_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(upload_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(jobs_router)
```

**Step 3: Commit**

```bash
git add backend/app/api/v1/jobs.py
git commit -m "feat: create job status endpoint"
```

---

## Phase 7: Testing

### Task 17: Create Pytest Fixtures and Basic Tests

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_api/__init__.py`
- Create: `backend/tests/test_api/test_upload.py`

**Step 1: Create tests/conftest.py with fixtures**

```python
# backend/tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from httpx import AsyncClient

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create test database and tables."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestingSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def client(test_db):
    """Create test HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

**Step 2: Create test directories**

```bash
mkdir -p backend/tests/test_api
touch backend/tests/__init__.py
touch backend/tests/test_api/__init__.py
```

**Step 3: Create test_upload.py**

```python
# backend/tests/test_api/test_upload.py
import pytest
from io import BytesIO
from pathlib import Path

@pytest.mark.asyncio
async def test_upload_single_pdf(client):
    """Test uploading a single PDF file."""
    # Create a minimal test PDF
    from reportlab.pdfgen import canvas

    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(100, 750, 'Test Question Paper')
    c.save()
    pdf_buffer.seek(0)

    files = {
        'files': ('test.pdf', pdf_buffer, 'application/pdf')
    }

    response = await client.post('/api/v1/upload', files=files)

    assert response.status_code == 200
    data = response.json()

    assert 'job_id' in data
    assert data['status'] == 'queued'
    assert data['files'] == ['test.pdf']
    assert 'status_url' in data

@pytest.mark.asyncio
async def test_upload_no_files(client):
    """Test uploading with no files."""
    response = await client.post('/api/v1/upload', files={})

    # Should return 422 or similar validation error
    assert response.status_code != 200

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get('/health')

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
```

**Step 4: Run tests**

```bash
cd backend
uv run pytest tests/ -v
```

Expected: All tests pass (or minimal failures for now)

**Step 5: Commit**

```bash
git add backend/tests/
git commit -m "feat: add pytest fixtures and basic api tests"
```

---

## Phase 8: Integration & Manual Testing

### Task 18: Create Manual API Test Script

**Files:**
- Create: `backend/scripts/__init__.py`
- Create: `backend/scripts/test_api.py`

**Step 1: Create scripts directory**

```bash
mkdir -p backend/scripts
touch backend/scripts/__init__.py
```

**Step 2: Create test_api.py**

```python
# backend/scripts/test_api.py
import asyncio
import httpx
import time
from pathlib import Path
from reportlab.pdfgen import canvas
from io import BytesIO

API_BASE = "http://localhost:8000"

async def create_test_pdf(filename: str = "test.pdf") -> Path:
    """Create a test PDF file."""
    pdf_path = Path(f"/tmp/{filename}")

    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(100, 750, 'Test Question Paper')
    c.drawString(50, 700, 'Q1. What is binary search?')
    c.drawString(50, 650, 'Q2. Explain quicksort algorithm')
    c.drawString(50, 600, 'Q3. What is dynamic programming?')
    c.save()
    pdf_buffer.seek(0)

    with open(pdf_path, 'wb') as f:
        f.write(pdf_buffer.read())

    print(f"✓ Created test PDF: {pdf_path}")
    return pdf_path

async def test_health():
    """Test health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/health")
        print(f"✓ Health check: {response.status_code}")
        return response.json()

async def test_upload(pdf_path: Path):
    """Test file upload."""
    async with httpx.AsyncClient() as client:
        with open(pdf_path, 'rb') as f:
            files = {'files': ('test.pdf', f, 'application/pdf')}
            response = await client.post(f"{API_BASE}/api/v1/upload", files=files)

        print(f"✓ Upload: {response.status_code}")
        data = response.json()
        print(f"  Job ID: {data['job_id']}")
        print(f"  Status: {data['status']}")
        return data['job_id']

async def test_job_status(job_id: str):
    """Test job status endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/api/v1/jobs/{job_id}")
        print(f"✓ Job status: {response.status_code}")
        data = response.json()
        print(f"  Status: {data['status']}")
        print(f"  Progress: {data['progress']}%")
        return data

async def test_search(query: str):
    """Test search endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE}/api/v1/search",
            params={'q': query, 'limit': 5}
        )
        print(f"✓ Search: {response.status_code}")
        data = response.json()
        print(f"  Query: {data['query']}")
        print(f"  Results: {data['total']}")
        return data

async def main():
    print("=" * 50)
    print("Question Paper Search - API Test Script")
    print("=" * 50)

    try:
        # Test health
        await test_health()

        # Create test PDF
        pdf_path = await create_test_pdf()

        # Test upload
        job_id = await test_upload(pdf_path)

        # Test job status
        await test_job_status(job_id)

        # Wait for processing (in real scenario)
        print("\n⏳ Waiting for processing (3 seconds)...")
        await asyncio.sleep(3)

        # Test search
        await test_search("binary search")

        print("\n✓ All tests completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Step 3: Install reportlab for PDF creation**

```bash
cd backend
uv add reportlab
```

**Step 4: Start services and test**

```bash
# Terminal 1: Start FastAPI
cd backend
uv run uvicorn app.main:app --reload

# Terminal 2: Run test script
cd backend
uv run python scripts/test_api.py
```

Expected: All tests pass and show successful API calls

**Step 5: Commit**

```bash
git add backend/scripts/
git commit -m "feat: add manual api testing script"
```

---

## Summary & Next Steps

### What You Have Now:

✅ **Project Setup**: uv, pyproject.toml, Docker Compose infrastructure
✅ **Database**: PostgreSQL with SQLAlchemy async ORM, Alembic migrations
✅ **FastAPI Server**: Main app, error handling, health check
✅ **File Upload**: POST /api/v1/upload endpoint with validation
✅ **Job Tracking**: Job status endpoint with database persistence
✅ **Celery Queue**: Task queue setup (ready for processing)
✅ **Vector Search**: Qdrant integration, search endpoint
✅ **Services**: LlamaCloud, Embeddings, Search services
✅ **Testing**: Pytest fixtures, basic test coverage, manual test script

### What's NOT Yet Integrated (for next phase):

- ❌ PDF processing task → LlamaCloud extraction
- ❌ Question parsing and storage
- ❌ Embedding generation and indexing
- ❌ Celery task triggering from upload endpoint
- ❌ End-to-end integration test
- ❌ Production readiness (logging, monitoring, error handling)

### Running the MVP:

```bash
# Terminal 1: Start services
docker-compose up -d

# Terminal 2: Start FastAPI
cd backend && uv run uvicorn app.main:app --reload

# Terminal 3: (when needed) Start Celery worker
cd backend && uv run celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 4: Run manual tests
cd backend && uv run python scripts/test_api.py
```

### Git Status:

All code is committed with logical, small commit messages following TDD patterns.

---

**Plan complete and saved to `/home/sxtr/Projects/pdf-buddy/docs/plans/2025-12-16-backend-mvp.md`.**

## Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration with code quality gates

**2. Parallel Session (separate)** - Open new session with executing-plans skill, batch execution with checkpoints

**Which approach would you prefer?**