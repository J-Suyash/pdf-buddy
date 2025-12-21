from fastapi import APIRouter
from app.api.v1.upload import router as upload_router
from app.api.v1.search import router as search_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.library import router as library_router
from app.api.v1.documents import router as documents_router
from app.api.v1.datalab import router as datalab_router

api_v1_router = APIRouter()
api_v1_router.include_router(upload_router, prefix="", tags=["upload"])
api_v1_router.include_router(search_router, prefix="", tags=["search"])
api_v1_router.include_router(jobs_router, prefix="", tags=["jobs"])
api_v1_router.include_router(library_router, prefix="", tags=["library"])
api_v1_router.include_router(documents_router, prefix="", tags=["documents"])
api_v1_router.include_router(datalab_router, prefix="", tags=["datalab"])
