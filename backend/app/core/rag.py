import httpx
from typing import Optional

from .config import settings

class AnythingLLMClient:
    """
    Асинхронный клиент для взаимодействия с API AnythingLLM.
    """
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def query_workspace(self, workspace_slug: str, query: str) -> dict:
        """
        Отправляет запрос в конкретное рабочее пространство (workspace) AnythingLLM.

        Args:
            workspace_slug: URL-slug рабочего пространства.
            query: Текст запроса от пользователя.

        Returns:
            Словарь с ответом от AnythingLLM.
        """
        if not self.api_key:
            return {"error": "API ключ для AnythingLLM не предоставлен."}
        
        url = f"{self.api_url}/api/v1/workspace/{workspace_slug}/chat"
        payload = {
            "message": query,
            "mode": "chat" # Используем режим чата для получения прямого ответа
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload, timeout=120)
                response.raise_for_status() # Вызовет исключение для статусов 4xx/5xx
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Ошибка API AnythingLLM: {e.response.status_code} - {e.response.text}")
            return {"error": f"Ошибка API AnythingLLM: {e.response.status_code}"}
        except Exception as e:
            print(f"Ошибка подключения к AnythingLLM: {e}")
            return {"error": "Не удалось подключиться к сервису AnythingLLM."}

# Инициализируем клиент с настройками
anything_llm_client = AnythingLLMClient(
    api_url=settings.ANYTHINGLLM_API_URL,
    api_key=settings.ANYTHINGLLM_API_KEY
) 