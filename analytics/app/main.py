import streamlit as st
import pandas as pd
from pathlib import Path
import json
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- Конфигурация ---
# Определяем корень проекта относительно текущего файла
PROJECT_ROOT = Path(__file__).parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "telegram_bot" / "logs"

# --- Функции для загрузки данных ---
@st.cache_data
def load_log_data(log_dir: Path) -> pd.DataFrame:
    """Загружает все interaction логи из .jsonl файлов в DataFrame."""
    all_interactions = []
    if not log_dir.exists():
        st.warning(f"Папка с логами не найдена: {log_dir}")
        return pd.DataFrame()

    log_files = sorted(log_dir.glob("interactions_*.jsonl"))
    if not log_files:
        st.info("Логи взаимодействий пока отсутствуют.")
        return pd.DataFrame()

    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    all_interactions.append(json.loads(line))
                except json.JSONDecodeError:
                    continue # Пропускаем поврежденные строки

    df = pd.DataFrame(all_interactions)
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
    return df

# --- Функции для отрисовки ---
def display_kpi_metrics(df: pd.DataFrame):
    """Отображает ключевые метрики производительности."""
    st.subheader("📊 Ключевые метрики")
    
    if df.empty:
        st.info("Нет данных для отображения метрик.")
        return

    total_messages = len(df)
    unique_users = df['user_id'].nunique()
    avg_resp_len = df['response_length'].mean()
    avg_query_len = df['query_length'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Всего сообщений", f"{total_messages}")
    col2.metric("Уникальных пользователей", f"{unique_users}")
    col3.metric("Avg. длина ответа", f"{avg_resp_len:.1f} симв.")
    col4.metric("Avg. длина запроса", f"{avg_query_len:.1f} симв.")

def display_activity_charts(df: pd.DataFrame):
    """Отображает графики активности."""
    st.subheader("📈 Активность пользователей")
    
    if df.empty or 'date' not in df.columns:
        st.info("Нет данных для построения графиков активности.")
        return
        
    # Активность по дням
    daily_activity = df.groupby('date').size().reset_index(name='messages')
    fig_daily = px.bar(daily_activity, x='date', y='messages', title='Количество сообщений по дням', text_auto=True)
    fig_daily.update_layout(xaxis_title="Дата", yaxis_title="Количество сообщений")
    st.plotly_chart(fig_daily, use_container_width=True)

def display_content_analysis(df: pd.DataFrame):
    """Отображает анализ контента запросов."""
    st.subheader("📝 Анализ контента")
    
    if df.empty:
        st.info("Нет данных для анализа контента.")
        return
        
    col1, col2 = st.columns(2)

    # Распределение типов документов
    with col1:
        doc_type_counts = df['doc_type'].fillna('N/A').value_counts()
        fig_pie = px.pie(
            doc_type_counts, 
            values=doc_type_counts.values, 
            names=doc_type_counts.index, 
            title='Распределение типов запросов'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Облако слов из запросов
    with col2:
        st.write("**Облако популярных слов в запросах**")
        all_queries = " ".join(df['query'].dropna())
        if all_queries:
            try:
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_queries)
                fig, ax = plt.subplots()
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Не удалось создать облако слов: {e}")
        else:
            st.info("Нет текста для создания облака слов.")

def display_dialogue_viewer(df: pd.DataFrame):
    """Отображает просмотрщик диалогов."""
    st.subheader("💬 Просмотр диалогов")

    if df.empty:
        st.info("Нет диалогов для просмотра.")
        return
        
    user_list = df['user_id'].unique()
    selected_user = st.selectbox("Выберите пользователя для просмотра диалога:", user_list)

    if selected_user:
        user_dialogues = df[df['user_id'] == selected_user].sort_values(by='timestamp')
        
        for _, row in user_dialogues.iterrows():
            with st.chat_message("user"):
                st.markdown(f"**Вы ({row['username']})** в {row['timestamp'].strftime('%Y-%m-%d %H:%M')}:")
                st.write(row['query'])
            
            with st.chat_message("assistant", avatar="🧠"):
                st.markdown(f"**Mind-Fix** ответил:")
                st.write(row['response'])
            st.markdown("---")

def main():
    """
    Основная функция для запуска дашборда аналитики.
    """
    st.set_page_config(page_title="Аналитика Mind-Fix", page_icon="🧠", layout="wide")
    st.title("Панель аналитики Mind-Fix")

    # Загружаем данные
    df_interactions = load_log_data(LOGS_DIR)

    # Отображаем компоненты
    display_kpi_metrics(df_interactions)
    st.markdown("---")
    display_activity_charts(df_interactions)
    st.markdown("---")
    display_content_analysis(df_interactions)
    st.markdown("---")
    display_dialogue_viewer(df_interactions)

if __name__ == "__main__":
    main() 