import os
import jsonlines
from pathlib import Path
import sys

from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.storage.storage_context import StorageContext
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

from core.config import settings

# --- Конфигурация ---
KNOWLEDGE_BASE_FILE = settings.KNOWLEDGE_BASE_FILE
CHROMA_HOST = settings.CHROMA_HOST
CHROMA_PORT = settings.CHROMA_PORT
LLM_MODEL_NAME = settings.LLM_MODEL_NAME
OLLAMA_BASE_URL = settings.OLLAMA_BASE_URL
COLLECTION_NAME = settings.CHROMA_COLLECTION

def ingest_data():
    """
    Загружает обработанные данные в ChromaDB.
    """
    if not KNOWLEDGE_BASE_FILE.exists():
        print(f"ОШИБКА: Файл базы знаний {KNOWLEDGE_BASE_FILE} не найден.")
        print("Пожалуйста, сначала запустите скрипт: python rag_pipeline/build_knowledge_base.py")
        sys.exit(1)

    # 1. Загружаем документы из .jsonl
    documents = []
    with jsonlines.open(KNOWLEDGE_BASE_FILE) as reader:
        for item in reader:
            doc = Document(text=item["text"])
            doc.metadata={
                "source": item["source"],
                "type": item["type"],
                "topic": item["topic"] or "N/A", # Chroma не любит None в метаданных
            }
            documents.append(doc)
    
    if not documents:
        print("Не найдено документов для индексации.")
        return

    print(f"Загружено {len(documents)} документов для индексации.")

    # 2. Настраиваем подключение к ChromaDB
    try:
        chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        # Проверяем, что сервер доступен
        chroma_client.heartbeat()
        print("Успешное подключение к ChromaDB.")
    except Exception as e:
        print(f"ОШИБКА: Не удалось подключиться к ChromaDB по адресу {CHROMA_HOST}:{CHROMA_PORT}.")
        print("Убедитесь, что сервисы запущены командой: docker-compose up -d chromadb")
        print(f"Детали ошибки: {e}")
        sys.exit(1)
    
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
    try:
        embed_model = OllamaEmbedding(
            model_name=LLM_MODEL_NAME, 
            base_url=OLLAMA_BASE_URL
        )
        Settings.embed_model = embed_model
    except ImportError:
        print("ОШИБКА: Не найден пакет llama-index-embeddings-ollama.")
        print("Пожалуйста, установите его командой: pip install llama-index-embeddings-ollama")
        sys.exit(1)
    except Exception as e:
        print(f"ОШИБКА: Не удалось инициализировать модель эмбеддингов Ollama.")
        print("Убедитесь, что Ollama запущена и модель '{LLM_MODEL_NAME}' доступна.")
        print(f"Детали ошибки: {e}")
        sys.exit(1)

    # 4. Создаем и сохраняем индекс
    print("Создание индекса... Это может занять некоторое время.")
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )
    print(f"Индекс успешно создан и сохранен в ChromaDB в коллекции '{COLLECTION_NAME}'.")

if __name__ == "__main__":
    ingest_data() 