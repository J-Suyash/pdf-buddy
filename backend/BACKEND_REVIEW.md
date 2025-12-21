# Backend Review and Recommendations

## 1. Issue Resolved: API Route Mismatch

**Problem:**
The frontend was receiving 404 errors when calling `/api/v1/upload`, `/api/v1/jobs/*`, and `/api/v1/search`.
This was caused by redundant route prefixes in the backend. The routers were defining `prefix="/api/v1"`, and they were being included in `main.py` with another `prefix="/api/v1"`, resulting in paths like `/api/v1/api/v1/upload`.

**Fix Applied:**
Removed the `prefix="/api/v1"` from the individual router definitions in:
- `app/api/v1/upload.py`
- `app/api/v1/jobs.py`
- `app/api/v1/search.py`

The API endpoints should now match what the frontend expects.

## 2. Backend Overview

The backend is a robust FastAPI application designed for high performance and scalability.

- **Framework:** FastAPI (Async/Await)
- **Database:** PostgreSQL (SQLAlchemy AsyncIO)
- **Task Queue:** Celery with Redis
- **Vector Search:** Qdrant
- **Structure:** Clean separation of concerns (API, Core, Models, Schemas, Services, Tasks).

## 3. Recommendations for Improvement

### A. File Upload Handling
**Current State:**
- Files are saved to `/tmp/qp_uploads`.
- The entire file is read into memory to check the file size (`await file.read()`), which can cause memory spikes with concurrent large uploads.

**Recommendation:**
1. **Shared Storage:** In a production environment (especially with Docker/Kubernetes), `/tmp` is not shared between containers. If the API and Celery workers are in different containers, the worker won't find the file. Use a shared Docker volume or Object Storage (AWS S3, Google Cloud Storage, MinIO).
2. **Streaming:** Use `UploadFile.file` object to check size or stream the write operation to disk to avoid loading 50MB into RAM per request.
3. **Configuration:** Move `UPLOAD_DIR` and `MAX_FILE_SIZE` to `app/config.py`.

### B. Task Management
**Current State:**
- `process_pdf_task` is imported inside the route handler to avoid circular imports.

**Recommendation:**
- Refactor the application structure to allow cleaner imports, or continue using the local import pattern but ensure type checking ignores it or handles it correctly.
- Ensure the Celery worker has access to the same file system path as the API server (see Shared Storage above).

### C. Error Handling & Logging
**Current State:**
- `upload.py` catches `Exception` and raises a generic 500 error.

**Recommendation:**
- Log the full stack trace of the exception before raising the HTTP error (currently done with `str(e)`, but `logger.exception` is better).
- Create specific exception classes for different failure modes (e.g., `StorageError`, `QueueError`) to provide more helpful error messages where safe.

### D. Security
**Current State:**
- CORS allows all origins (`*`).

**Recommendation:**
- In `main.py`, configure `allow_origins` to restrict access to the specific frontend domain/port in production.

### E. Database
**Current State:**
- Migrations are handled by Alembic.

**Recommendation:**
- Ensure `alembic upgrade head` is run as part of the deployment pipeline or startup script (if safe) to keep the schema in sync.

## 4. Next Steps
1. Verify the upload functionality from the frontend.
2. Test the search and job status endpoints.
3. Consider implementing the shared storage solution if deploying to a multi-container environment.
