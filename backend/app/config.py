from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    celery_broker_url: str
    qdrant_host: str
    qdrant_port: int
    llama_api_key: str = ""  # For backward compatibility with LlamaParse
    llama_cloud_api_key: str = ""  # For LlamaExtract
    secret_key: str

    # File storage
    upload_dir: str = "/tmp/qp_uploads"
    permanent_storage_dir: str = "./storage/pdfs"  # Permanent storage for PDFs
    datalab_storage_dir: str = "./storage/datalab"  # Storage for datalab OCR output
    max_file_size_mb: int = 50

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
