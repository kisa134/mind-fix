# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY ./app /app

# Запускаем Streamlit
# Указываем порт 8501, как в docker-compose.yml
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]

 