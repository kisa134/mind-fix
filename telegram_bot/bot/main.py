import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

# from .core.config import settings
# from .handlers import common, chat

async def main() -> None:
    """
    Основная функция для запуска Telegram-бота.
    """
    # Временно используем токен напрямую для простоты
    # В будущем будет использоваться Pydantic Settings
    # bot = Bot(token=settings.telegram_bot_token, parse_mode=ParseMode.HTML)
    
    # Заглушка токена
    bot = Bot(token="YOUR_TOKEN_HERE", parse_mode=ParseMode.HTML)
    
    dp = Dispatcher()

    # Сюда будут подключаться роутеры
    # dp.include_router(common.router)
    # dp.include_router(chat.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main()) 