import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import settings
from handlers import chat

async def main() -> None:
    """
    Основная функция для запуска Telegram-бота.
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        logging.critical("ОШИБКА: Не задана переменная окружения TELEGRAM_BOT_TOKEN!")
        sys.exit(1)

    # Задаем свойства по умолчанию для бота, включая parse_mode
    default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
    
    # Используем токен из настроек и передаем свойства
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, default=default_properties)
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(chat.router)
    
    logging.info("Telegram-бот запущен и готов к работе.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    # Выводим информацию о загруженных настройках (без секретов)
    logging.info(f"Загружен URL бэкенда: {settings.BACKEND_API_URL}")
    asyncio.run(main()) 