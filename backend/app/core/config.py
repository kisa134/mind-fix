import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Модель для хранения и валидации настроек backend-приложения.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # PostgreSQL Database
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "mind_fix_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    LLM_MODEL_NAME: str = "llama3.1:8b"

    # ChromaDB
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000 # Внутренний порт ChromaDB
    CHROMA_COLLECTION: str = "mind_fix_kb"

    # Redis
    REDIS_HOST: str = "redis_cache"
    REDIS_PORT: int = 6379


settings = Settings() 