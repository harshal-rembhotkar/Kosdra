import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    COSDATA_HOST: str = "http://127.0.0.1:8443"
    COSDATA_USER: str = "admin"
    COSDATA_PASS: str = "Admin1h"
    COLLECTION_NAME: str = "talentscout_prod"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"

settings = Settings()
