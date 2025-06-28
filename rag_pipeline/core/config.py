import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Определяем корень проекта относительно текущего файла
PROJECT_ROOT = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    """
    Модель для хранения и валидации настроек для RAG-пайплайна.
    """
    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / '.env'), env_file_encoding='utf-8', extra='ignore')

    # Пути
    DATA_DIR: Path = PROJECT_ROOT / "data"
    KNOWLEDGE_BASE_FILE: Path = DATA_DIR / "knowledge_base.jsonl"
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL_NAME: str = "llama3.1:8b"

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION: str = "mind_fix_kb"

settings = Settings()

# Логирование для проверки (кроме секретов)
print("--- RAG Pipeline Settings ---")
print(f"Project Root: {PROJECT_ROOT}")
print(f"Data Directory: {settings.DATA_DIR}")
print(f"Ollama URL: {settings.OLLAMA_BASE_URL}")
print(f"Chroma Host: {settings.CHROMA_HOST}")
print("-----------------------------") 