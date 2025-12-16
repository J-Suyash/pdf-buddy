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

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
