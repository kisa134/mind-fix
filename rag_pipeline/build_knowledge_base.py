import os
import json
import jsonlines
from pathlib import Path
from typing import List, Literal, Optional

from llama_index.core import Document, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.ollama import Ollama
from llama_index.readers.file import (
    DocxReader,
    PDFReader,
    MarkdownReader,
    JSONReader,
)
from pydantic import BaseModel, Field

# --- Конфигурация ---
DATA_DIR = Path("../data")
OUTPUT_FILE = DATA_DIR / "knowledge_base.jsonl"
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# --- Модели данных ---
class KnowledgeChunk(BaseModel):
    """
    Структура для хранения одного блока знаний.
    """
    type: Literal["theory", "practice", "extra"] = Field(
        ..., description="Тип контента: теория, практика или дополнительное."
    )
    topic: Optional[str] = Field(
        default=None, description="Основная тема блока, например, 'тревога' или 'прокрастинация'."
    )
    source: str = Field(..., description="Исходный файл.")
    text: str = Field(..., description="Текст блока.")

# --- Логика ---

def classify_chunk_by_keywords(text: str) -> dict:
    """
    Простая классификация по ключевым словам.
    """
    text_lower = text.lower()
    # Расширьте эти списки для более точной классификации
    practice_keywords = ["пациент:", "терапевт:", "клиент:", "случай", "кейс", "диалог"]
    theory_keywords = ["определение", "алгоритм", "теория", "концепция", "схема"]

    if any(kw in text_lower for kw in practice_keywords):
        return {"type": "practice", "topic": None}
    if any(kw in text_lower for kw in theory_keywords):
        return {"type": "theory", "topic": None}
    
    return {"type": "extra", "topic": None}


# --- Продвинутая классификация через LLM (рекомендуется) ---

# Закомментировано, чтобы не требовать запуск Ollama для базовой обработки.
# Инструкции по активации в README.md или в комментариях ниже.

# prompt = PromptTemplate(
#     "Определи тип и основную тему для следующего текстового блока. "
#     "Тип должен быть одним из: theory, practice, extra. "
#     "Тема должна быть коротким названием, например, 'тревога' или 'весы души'. "
#     "Если тему определить не удается, оставь поле пустым.\n\n"
#     "Текст: {text}\n"
# )

# program = LLMTextCompletionProgram.from_defaults(
#     output_cls=KnowledgeChunk,
#     llm=Ollama(model=LLM_MODEL_NAME, base_url=OLLAMA_BASE_URL),
#     prompt=prompt,
# )

# def classify_chunk_with_llm(text: str) -> dict:
#     """
#     Классифицирует чанк с помощью LLM.
#     Возвращает словарь, совместимый с KnowledgeChunk.
#     """
#     try:
#         result = program(text=text)
#         return result.dict()
#     except Exception as e:
#         print(f"Ошибка классификации через LLM: {e}")
#         # В случае ошибки используем запасной вариант
#         return classify_chunk_by_keywords(text)


def process_documents(use_llm_classifier: bool = False):
    """
    Основная функция для обработки всех документов в DATA_DIR.
    
    Args:
        use_llm_classifier: Использовать LLM для классификации. 
                            Требует запущенного сервиса Ollama.
    """
    # Определяем, какую функцию классификации использовать
    classifier = classify_chunk_with_llm if use_llm_classifier else classify_chunk_by_keywords

    # Настраиваем ридеры для разных типов файлов
    # SimpleDirectoryReader не подошел, т.к. нужна кастомная логика для json
    file_readers = {
        ".docx": DocxReader(),
        ".pdf": PDFReader(),
        ".md": MarkdownReader(),
        ".txt": None,  # Будем читать как обычный текст
        ".json": JSONReader(),
    }
    
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    print("Очищаем старую базу знаний (если есть)...")
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    with jsonlines.open(OUTPUT_FILE, mode='w') as writer:
        for filepath in DATA_DIR.iterdir():
            if filepath.is_file() and filepath.suffix in file_readers:
                print(f"Обработка файла: {filepath.name}...")
                
                chunks = []
                # Специальная обработка для JSON
                if filepath.suffix == ".json":
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        # Предполагаем, что result.json - это список диалогов
                        if filepath.name == "result.json" and isinstance(data, list):
                            for message in data:
                                if isinstance(message, dict) and "text" in message:
                                    chunks.append(str(message["text"])) # Приводим к строке на всякий случай
                        else:
                            # Для других JSON можно реализовать свою логику
                            # или просто извлечь весь текст
                            chunks = [json.dumps(data, ensure_ascii=False)]
                    except Exception as e:
                        print(f"Не удалось обработать JSON-файл {filepath.name}: {e}")
                        continue
                else:
                    # Обработка текстовых файлов
                    if filepath.suffix == ".txt":
                        text = filepath.read_text(encoding="utf-8")
                        docs = [Document(text=text)]
                    else:
                        docs = file_readers[filepath.suffix].load_data(filepath)
                    
                    nodes = splitter.get_nodes_from_documents(docs)
                    chunks.extend([node.text for node in nodes])
                
                # Классификация и сохранение
                for text_chunk in chunks:
                    if not text_chunk.strip():
                        continue
                    
                    classification_result = classifier(text_chunk)
                    
                    chunk_obj = KnowledgeChunk(
                        **classification_result,
                        source=filepath.name,
                        text=text_chunk,
                    )
                    writer.write(chunk_obj.dict())

if __name__ == "__main__":
    # Для использования LLM-классификатора, передайте True
    # Убедитесь, что Ollama запущена: docker-compose up ollama
    USE_LLM = False 

    print("Запуск обработки документов...")
    process_documents(use_llm_classifier=USE_LLM)
    print(f"Обработка завершена. База знаний сохранена в {OUTPUT_FILE}") 