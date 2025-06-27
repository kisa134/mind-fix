from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.api.v1.endpoints.rag import router as rag_router
from app.core.rag import get_query_engine

# Контекст Lifespan для управления RAG сервисом
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код здесь выполняется перед запуском приложения
    print("Инициализация RAG сервиса...")
    app.state.query_engine = get_query_engine()
    yield
    # Код здесь выполняется после остановки приложения
    print("RAG сервис остановлен.")
    app.state.query_engine = None

app = FastAPI(
    title="Mind-Fix API",
    description="API для проекта ИИ-психотерапевта Mind-Fix",
    version="0.1.0",
    lifespan=lifespan
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