import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    COSDATA_HOST: str = "http://127.0.0.1:8443"
    COSDATA_USER: str = "admin"
    COSDATA_PASS: str = "Admin1h"
    COLLECTION_NAME: str = "kosdra_prod"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    # Search defaults and feature flags
    DEFAULT_TOP_K: int = 15
    DEFAULT_FUSION_K: float = 60.0
    RELAX_ON_EMPTY: bool = False
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()