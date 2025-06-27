import os
from typing import List, Optional

import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.llms import LLM
from llama_index.core.vector_stores.types import ExactMatchFilter, MetadataFilters
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

# --- Глобальные переменные и инициализация ---

# Загружаем конфигурацию из переменных окружения
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000") # Внутренний порт ChromaDB
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
COLLECTION_NAME = "mind_fix_kb"

# Инициализируем LLM и модель для эмбеддингов
llm = Ollama(model=LLM_MODEL_NAME, base_url=OLLAMA_BASE_URL)
embed_model = OllamaEmbedding(model_name=LLM_MODEL_NAME, base_url=OLLAMA_BASE_URL)

Settings.llm = llm
Settings.embed_model = embed_model

# --- Инициализация RAG ---
# Убираем глобальные переменные index и query_engine отсюда
# и переносим их в управляемый контекст (lifespan)

def get_query_engine():
    """
    Инициализирует и возвращает RAG query engine.
    Эта функция будет вызываться при старте приложения.
    """
    try:
        chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = chroma_client.get_collection(COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=collection)
        
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=embed_model,
        )
        
        query_engine = index.as_query_engine(
            similarity_top_k=5,
        )
        print("RAG сервис успешно инициализирован.")
        return query_engine

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось инициализировать RAG сервис: {e}")
        print("Убедитесь, что ChromaDB запущена и база знаний была проиндексирована.")
        return None

# --- Функции для работы с RAG ---

def execute_query(query_engine, query_text: str, doc_type: Optional[str] = None, topic: Optional[str] = None):
    """
    Выполняет поиск по базе знаний с возможностью фильтрации.

    Args:
        query_engine: Активный экземпляр query_engine.
        query_text: Текст запроса.
        doc_type: Тип документа ('theory', 'practice', 'extra').
        topic: Тема документа.

    Returns:
        Ответ от LLM, основанный на найденных документах.
    """
    if not query_engine:
        return "RAG сервис не инициализирован. Проверьте лог ошибок при старте API."

    filters = []
    if doc_type:
        filters.append(ExactMatchFilter(key="type", value=doc_type))
    if topic:
        filters.append(ExactMatchFilter(key="topic", value=topic))

    if filters:
        response = query_engine.query(
            query_text, 
            vector_store_query_kwargs={"filters": MetadataFilters(filters=filters)}
        )
    else:
        response = query_engine.query(query_text)
        
    return response 