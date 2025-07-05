from typing import Optional, Literal

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

from app.core.rag import anything_llm_client
from app.core.config import settings

router = APIRouter()

class RAGQueryRequest(BaseModel):
    text: str
    # doc_type и topic больше не нужны, т.к. AnythingLLM управляет контекстом
    # внутри своего рабочего пространства (workspace)

class RAGQueryResponse(BaseModel):
    response: str
    sources: list = []

@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    """
    Отправляет запрос к AnythingLLM для получения ответа,
    обогащенного данными из базы знаний.
    """
    if not settings.ANYTHINGLLM_WORKSPACE_SLUG:
        raise HTTPException(status_code=500, detail="Не настроен `ANYTHINGLLM_WORKSPACE_SLUG` в .env")

    result = await anything_llm_client.query_workspace(
        workspace_slug=settings.ANYTHINGLLM_WORKSPACE_SLUG,
        query=request.text
    )

    if result and "error" not in result:
        text_response = result.get("textResponse", "Ответ не найден.")
        sources = result.get("sourceDocuments", [])
        return {"response": text_response, "sources": sources}
    else:
        error_detail = result.get("error", "Неизвестная ошибка от AnythingLLM")
        raise HTTPException(status_code=503, detail=error_detail) 