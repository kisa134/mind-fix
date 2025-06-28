from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Модель для хранения и валидации настроек приложения,
    загружаемых из переменных окружения.
    """
    # Загружаем переменные из .env файла
    model_config = SettingsConfigDict(env_file='../../.env', env_file_encoding='utf-8', extra='ignore')

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str

    # API Backend
    BACKEND_API_URL: str = "http://backend:8000/api/v1"


# Создаем единственный экземпляр настроек,
# который будет использоваться во всем приложении.
settings = Settings() 