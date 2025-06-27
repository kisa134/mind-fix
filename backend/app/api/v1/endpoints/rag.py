from typing import Optional, Literal

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

from app.core.rag import execute_query

router = APIRouter()

class RAGQueryRequest(BaseModel):
    text: str
    doc_type: Optional[Literal["theory", "practice", "extra"]] = None
    topic: Optional[str] = None

class RAGQueryResponse(BaseModel):
    response: str
    # В будущем можно добавить источники (source_nodes)
    # sources: list = []

def get_rag_service(request: Request):
    """Зависимость для получения query_engine из состояния приложения."""
    return request.app.state.query_engine

@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest, query_engine = Depends(get_rag_service)):
    """
    Отправляет запрос к RAG-сервису для получения ответа,
    обогащенного данными из базы знаний.
    """
    if query_engine is None:
        raise HTTPException(status_code=503, detail="RAG сервис недоступен. Проверьте логи сервера.")

    try:
        result = execute_query(
            query_engine=query_engine,
            query_text=request.text,
            doc_type=request.doc_type,
            topic=request.topic,
        )
        return {"response": str(result)}
    except Exception as e:
        # Логирование ошибки здесь было бы полезно
        raise HTTPException(status_code=500, detail=str(e)) 