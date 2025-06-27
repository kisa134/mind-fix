import streamlit as st
import pandas as pd
# import psycopg2
# from dotenv import load_dotenv
# import os

# load_dotenv()

def main():
    """
    Основная функция для запуска дашборда аналитики.
    """
    st.set_page_config(page_title="Аналитика диалогов", page_icon="🧠")

    st.title("Аналитика диалогов")
    st.write("Добро пожаловать в панель администратора. Здесь вы можете просматривать и анализировать диалоги с пользователями.")

    # Пример подключения к БД (раскомментировать, когда будет готова)
    # try:
    #     conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    #     st.success("Успешное подключение к базе данных!")
    #     # df = pd.read_sql("SELECT * FROM dialogues", conn)
    #     # st.dataframe(df)
    #     conn.close()
    # except Exception as e:
    #     st.error(f"Ошибка подключения к БД: {e}")
    
    st.info("Подключение к базе данных будет реализовано в будущем.")


if __name__ == "__main__":
    main() 