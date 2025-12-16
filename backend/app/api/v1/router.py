from fastapi import APIRouter
from app.api.v1.upload import router as upload_router

api_v1_router = APIRouter()
api_v1_router.include_router(upload_router, prefix="", tags=["upload"])
