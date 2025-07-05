from fastapi import FastAPI
from app.api.v1.endpoints.rag import router as rag_router

# Контекст Lifespan больше не нужен, т.к. клиент AnythingLLM
# не требует сложной инициализации при старте.

app = FastAPI(
    title="Mind-Fix API",
    description="API для проекта ИИ-психотерапевта Mind-Fix",
    version="0.1.0",
    # lifespan=lifespan # Убрали
)

@app.get("/")
async def read_root():
    """
    Корневой эндпоинт для проверки работоспособности API.
    """
    return {"status": "API is running"}

# Подключаем роутеры
app.include_router(rag_router, prefix="/api/v1/rag", tags=["RAG"])

# В будущем здесь будут подключаться роутеры
# from .api.v1.endpoints import chat
# app.include_router(chat.router, prefix="/api/v1") 