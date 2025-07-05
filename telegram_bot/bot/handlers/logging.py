import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class UserSessionLogger:
    """Класс для логирования пользовательских сессий."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
    def log_interaction(self, user_id: int, username: str, query: str, response: str, doc_type: Optional[str] = None):
        """Логирует взаимодействие пользователя с ботом."""
        timestamp = datetime.now().isoformat()
        
        interaction_data = {
            "timestamp": timestamp,
            "user_id": user_id,
            "username": username,
            "query": query,
            "response": response,
            "doc_type": doc_type,
            "query_length": len(query),
            "response_length": len(response)
        }
        
        # Логируем в файл по дням
        log_file = self.log_dir / f"interactions_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(interaction_data, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Ошибка при записи лога взаимодействия: {e}")
    
    def log_user_session(self, user_id: int, username: str, action: str):
        """Логирует начало/конец пользовательской сессии."""
        timestamp = datetime.now().isoformat()
        
        session_data = {
            "timestamp": timestamp,
            "user_id": user_id,
            "username": username,
            "action": action  # "start", "end", "command"
        }
        
        log_file = self.log_dir / f"sessions_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(session_data, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Ошибка при записи лога сессии: {e}")

# Глобальный экземпляр логгера
session_logger = UserSessionLogger() 