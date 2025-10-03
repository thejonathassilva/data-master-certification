from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "predict-api"
    APP_VERSION: str = "0.1.0"

    # FastAPI / Uvicorn
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Mongo
    MONGO_URI: str = Field(default="mongodb://localhost:27017")
    MONGO_DB: str = Field(default="nlp")

    # MinIO
    MINIO_ENDPOINT: str = Field(default="localhost:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    MINIO_SECURE: bool = Field(default=False)
    MINIO_DEFAULT_BUCKET: str = Field(default="nlp-models")

    # Cache
    CACHE_MAX_ITEMS: int = Field(default=32)
    CACHE_TTL_SECONDS: int = Field(default=1800)
    CACHE_DIR: str = Field(default=os.path.abspath("./.model_cache"))

    PREVIEW_FORCE_CPU: bool = Field(default=True)
    RANDOM_SEED: int = Field(default=42)
    EPOCHS_TEXTCAT: int = Field(default=10)
    EPOCHS_NER: int = Field(default=8)      # não usado no preview, mas deixamos aqui
    BATCH_SIZE: int = Field(default=16)
    EARLY_STOP_PATIENCE: int = Field(default=3)
    WORK_DIR: str = Field(default="/tmp/trainer-work")

    PREVIEW_MIN_F1: float = Field(default=0.60)
    PREVIEW_MIN_LIFT: float = Field(default=0.10)
    PREVIEW_MIN_POS_CONF: float = Field(default=0.70)
    PREVIEW_MAX_NEG_CONF: float = Field(default=0.30)
    PREVIEW_MAX_FPR: float = Field(default=0.20)

    # Preview training
    PREVIEW_ITERS: int = Field(default=4)  # 3–5 recomendado

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",         # <- evita crash com variáveis que não existem no modelo
        case_sensitive=False    # <- aceita PREVIEW_FORCE_CPU e preview_force_cpu
    )

settings = Settings()
