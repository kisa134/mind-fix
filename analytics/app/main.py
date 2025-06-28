import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env
load_dotenv()

def get_db_connection():
    """Устанавливает и возвращает соединение с базой данных."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "db"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("POSTGRES_PORT", 5432)
        )
        return conn
    except psycopg2.OperationalError as e:
        st.error(f"Ошибка подключения к базе данных: {e}")
        st.info("Убедитесь, что сервис PostgreSQL запущен и переменные окружения в .env файле корректны.")
        return None

def main():
    """
    Основная функция для запуска дашборда аналитики.
    """
    st.set_page_config(page_title="Аналитика диалогов", page_icon="🧠", layout="wide")

    st.title("Аналитика диалогов")
    st.write("Добро пожаловать в панель администратора. Здесь вы можете просматривать и анализировать диалоги с пользователями.")

    conn = get_db_connection()
    if conn:
        st.success("Успешное подключение к базе данных!")
        try:
            # В будущем здесь будет запрос к таблице с диалогами
            # df = pd.read_sql("SELECT * FROM dialogues", conn)
            # st.dataframe(df)
            st.info("Отображение диалогов будет реализовано после создания соответствующей таблицы.")
        except Exception as e:
            st.error(f"Ошибка при выполнении запроса к БД: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    main() 