from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.utils.exceptions import ApplicationException


# Create tables on startup
@asynccontextmanager
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


# Include API routes
from app.api.v1.router import api_v1_router
app.include_router(api_v1_router)
