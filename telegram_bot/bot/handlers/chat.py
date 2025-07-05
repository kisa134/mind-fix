import logging
import aiohttp
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from core.config import settings
from .logging import session_logger

router = Router()

logger = logging.getLogger(__name__)

class RAGClient:
    """Клиент для взаимодействия с RAG API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    async def query(self, text: str, doc_type: Optional[str] = None, topic: Optional[str] = None) -> str:
        """Отправляет запрос к RAG API и возвращает ответ."""
        url = f"{self.base_url}/api/v1/rag/query"
        
        payload = {
            "text": text,
            "doc_type": doc_type,
            "topic": topic
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "Извините, не удалось получить ответ.")
                    elif response.status == 503:
                        return "🔧 RAG-сервис временно недоступен. Попробуйте позже."
                    else:
                        logger.error(f"RAG API вернул статус {response.status}")
                        return "❌ Произошла ошибка при обработке вашего запроса."
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка соединения с RAG API: {e}")
            return "🌐 Не удалось связаться с сервисом. Проверьте подключение."
        except Exception as e:
            logger.error(f"Неожиданная ошибка при обращении к RAG API: {e}")
            return "❌ Произошла неожиданная ошибка."

# Создаем экземпляр клиента
rag_client = RAGClient(settings.BACKEND_API_URL)

@router.message(CommandStart())
async def start_command(message: Message):
    """Обработчик команды /start."""
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    
    # Логируем начало сессии
    session_logger.log_user_session(user_id, username, "start")
    
    welcome_text = """
👋 Добро пожаловать в Mind-Fix!

Я ваш ИИ-ассистент-психотерапевт, основанный на Интегративной Теории Невроза (ИТН).

🔹 Задавайте мне вопросы о психологии и психотерапии
🔹 Обсуждайте свои переживания и проблемы
🔹 Получайте рекомендации по саморазвитию

Просто напишите мне свой вопрос или опишите ситуацию, и я постараюсь помочь!

ℹ️ Доступные команды:
/help - справка
/theory - вопросы по теории
/practice - практические рекомендации
    """
    await message.answer(welcome_text)

@router.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help."""
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    
    # Логируем команду
    session_logger.log_user_session(user_id, username, "help")
    
    help_text = """
🆘 <b>Справка по использованию Mind-Fix</b>

<b>Основные команды:</b>
/start - начать работу с ботом
/help - показать эту справку
/theory - задать вопрос по теории психотерапии
/practice - получить практические рекомендации

<b>Как пользоваться:</b>
• Просто напишите ваш вопрос или опишите ситуацию
• Я проанализирую ваш запрос и дам ответ на основе ИТН
• Для более точных ответов используйте специальные команды

<b>Примеры вопросов:</b>
• "Как справиться с тревогой?"
• "Что такое невроз с точки зрения ИТН?"
• "Помогите разобраться с отношениями"

<b>Конфиденциальность:</b>
🔒 Все данные обрабатываются локально и не передаются третьим лицам.
    """
    await message.answer(help_text)

@router.message(Command("theory"))
async def theory_command(message: Message):
    """Обработчик команды /theory."""
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    
    # Логируем команду
    session_logger.log_user_session(user_id, username, "theory")
    
    await message.answer(
        "📚 <b>Режим теоретических вопросов</b>\n\n"
        "Задайте ваш вопрос о теории психотерапии, ИТН, или психологических концепциях.\n\n"
        "Например: \"Что такое базовая тревога в ИТН?\" или \"Объясните концепцию невроза\""
    )

@router.message(Command("practice"))
async def practice_command(message: Message):
    """Обработчик команды /practice."""
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    
    # Логируем команду
    session_logger.log_user_session(user_id, username, "practice")
    
    await message.answer(
        "🛠️ <b>Режим практических рекомендаций</b>\n\n"
        "Опишите вашу ситуацию или проблему, и я дам практические рекомендации.\n\n"
        "Например: \"Как работать с прокрастинацией?\" или \"Техники для снижения тревоги\""
    )

@router.message(F.text)
async def handle_text_message(message: Message):
    """Обработчик текстовых сообщений."""
    user_text = message.text
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    
    # Показываем, что бот печатает
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # Логируем запрос (без личных данных)
    logger.info(f"Получен запрос от пользователя {user_id}: {user_text[:50]}...")
    
    # Определяем тип запроса на основе контекста
    doc_type = None
    if any(word in user_text.lower() for word in ["теория", "концепция", "что такое", "объясни"]):
        doc_type = "theory"
    elif any(word in user_text.lower() for word in ["как", "помоги", "совет", "рекомендация", "техника"]):
        doc_type = "practice"
    
    # Отправляем запрос к RAG API
    response = await rag_client.query(user_text, doc_type=doc_type)
    
    # Логируем взаимодействие
    session_logger.log_interaction(user_id, username, user_text, response, doc_type)
    
    # Отправляем ответ пользователю
    try:
        await message.answer(response)
        logger.info(f"Отправлен ответ пользователю {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке ответа: {e}")
        await message.answer("❌ Произошла ошибка при отправке ответа. Попробуйте еще раз.")

@router.message()
async def handle_other_messages(message: Message):
    """Обработчик для всех остальных типов сообщений."""
    await message.answer(
        "🤖 Я понимаю только текстовые сообщения.\n\n"
        "Пожалуйста, опишите ваш вопрос или проблему текстом, и я постараюсь помочь!"
    ) 