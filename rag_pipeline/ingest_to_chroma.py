import os
import jsonlines
from pathlib import Path

from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.storage.storage_context import StorageContext
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# --- Конфигурация ---
DATA_DIR = Path("../data")
KNOWLEDGE_BASE_FILE = DATA_DIR / "knowledge_base.jsonl"
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8001") # 8001, чтобы не конфликтовать с FastAPI
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
COLLECTION_NAME = "mind_fix_kb"

def ingest_data():
    """
    Загружает обработанные данные в ChromaDB.
    """
    if not KNOWLEDGE_BASE_FILE.exists():
        print(f"Файл {KNOWLEDGE_BASE_FILE} не найден. Сначала запустите build_knowledge_base.py")
        return

    # 1. Загружаем документы из .jsonl
    documents = []
    with jsonlines.open(KNOWLEDGE_BASE_FILE) as reader:
        for item in reader:
            doc = Document(
                text=item["text"],
                metadata={
                    "source": item["source"],
                    "type": item["type"],
                    "topic": item["topic"] or "N/A", # Chroma не любит None в метаданных
                },
            )
            documents.append(doc)
    
    if not documents:
        print("Не найдено документов для индексации.")
        return

    print(f"Загружено {len(documents)} документов для индексации.")

    # 2. Настраиваем подключение к ChromaDB
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    
    # Удаляем старую коллекцию, если она есть, для чистоты примера
    # В продакшене может понадобиться логика обновления
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
        print(f"Старая коллекция '{COLLECTION_NAME}' удалена.")
    except Exception:
        print(f"Старая коллекция '{COLLECTION_NAME}' не найдена, создаем новую.")

    collection = chroma_client.create_collection(name=COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 3. Настраиваем модель для эмбеддингов
    # Используем Ollama для локальных эмбеддингов
    embed_model = OllamaEmbedding(
        model_name=LLM_MODEL_NAME, 
        base_url=OLLAMA_BASE_URL
    )
    Settings.embed_model = embed_model
    Settings.llm = None # LLM здесь не нужен, только для эмбеддингов

    # 4. Создаем и сохраняем индекс
    print("Создание индекса... Это может занять некоторое время.")
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )
    print(f"Индекс успешно создан и сохранен в ChromaDB в коллекции '{COLLECTION_NAME}'.")

if __name__ == "__main__":
    ingest_data() 