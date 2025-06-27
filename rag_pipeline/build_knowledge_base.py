import os
import json
import jsonlines
from pathlib import Path
from typing import List, Literal, Optional

from llama_index.core import Document, Settings, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.ollama import Ollama
from pydantic import BaseModel, Field

# --- Конфигурация ---
# Определяем корень проекта относительно текущего файла
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
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


def load_all_documents(data_dir: Path) -> List[Document]:
    """
    Загружает все документы из указанной директории, используя
    SimpleDirectoryReader для стандартных форматов и ручную обработку для .json.
    """
    docs = []
    
    # Проверяем, существует ли папка data и не пуста ли она
    if not data_dir.exists():
        print(f"Папка {data_dir} не найдена. Создаю её.")
        data_dir.mkdir()
    
    if not any(data_dir.iterdir()):
        print(f"ПРЕДУПРЕЖДЕНИЕ: Папка {data_dir} пуста. Нет документов для обработки.")
        return docs

    # 1. Используем SimpleDirectoryReader для всех файлов, кроме .json
    print("Загрузка стандартных документов (docx, pdf, md, txt)...")
    reader = SimpleDirectoryReader(
        input_dir=data_dir,
        exclude=["*.json"],
        recursive=True,
    )
    docs.extend(reader.load_data(show_progress=True))
    
    # 2. Ручная обработка .json файлов
    print("Обработка JSON файлов...")
    for json_path in data_dir.rglob("*.json"):
        try:
            print(f"Обработка {json_path.name}...")
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            messages = []
            # Гибко ищем список сообщений
            if isinstance(data, dict) and "messages" in data:
                messages = data["messages"]
            elif isinstance(data, list):
                messages = data

            if messages:
                for message in messages:
                    if isinstance(message, dict) and message.get("type") == "message" and message.get("text"):
                        text_content = ""
                        raw_text = message.get("text", "")
                        if isinstance(raw_text, list):
                            for item in raw_text:
                                if isinstance(item, str):
                                    text_content += item
                                elif isinstance(item, dict) and "text" in item:
                                    text_content += item.get("text", "")
                        else:
                            text_content = str(raw_text)
                        
                        if text_content.strip():
                            docs.append(Document(
                                text=text_content, 
                                metadata={"source": json_path.name}
                            ))
            else: # Если это другой JSON, просто загружаем его как есть
                text_content = json.dumps(data, ensure_ascii=False)
                docs.append(Document(
                    text=text_content, 
                    metadata={"source": json_path.name}
                ))
        except Exception as e:
            print(f"Не удалось обработать JSON-файл {json_path.name}: {e}")

    print(f"Всего загружено документов: {len(docs)}")
    return docs


def process_documents(use_llm_classifier: bool = False):
    """
    Основная функция для обработки всех документов в DATA_DIR.
    """
    # Этот блок гарантирует, что папка будет создана, если её нет
    if not DATA_DIR.exists():
        print(f"Папка {DATA_DIR} не найдена. Создаю её.")
        DATA_DIR.mkdir()

    classifier = classify_chunk_with_llm if use_llm_classifier else classify_chunk_by_keywords
    
    # 1. Загружаем все документы
    documents = load_all_documents(DATA_DIR)
    
    # 2. Разбиваем на чанки (ноды)
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents(documents, show_progress=True)

    print("Очищаем старую базу знаний (если есть)...")
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    print(f"Начинаем обработку {len(nodes)} блоков текста...")
    with jsonlines.open(OUTPUT_FILE, mode='w') as writer:
        for node in nodes:
            text_chunk = node.get_content()
            if not text_chunk.strip():
                continue
            
            source_file = node.metadata.get("file_name") or node.metadata.get("source", "N/A")
            
            classification_result = classifier(text_chunk)
            
            chunk_obj = KnowledgeChunk(
                **classification_result,
                source=Path(source_file).name,
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