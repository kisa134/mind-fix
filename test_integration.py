#!/usr/bin/env python3
"""
Скрипт для тестирования интеграции компонентов Mind-Fix
"""

import asyncio
import aiohttp
import json
from pathlib import Path

async def test_backend_api():
    """Тестирует backend API."""
    print("🔍 Тестирование Backend API...")
    
    url = "http://localhost:8000/api/v1/rag/query"
    test_query = {
        "text": "Что такое невроз в ИТН?",
        "doc_type": "theory"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=test_query) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Backend API работает. Ответ: {data['response'][:100]}...")
                    return True
                else:
                    print(f"❌ Backend API вернул статус {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Ошибка подключения к Backend API: {e}")
        return False

def test_rag_pipeline():
    """Тестирует RAG pipeline."""
    print("🔍 Тестирование RAG Pipeline...")
    
    # Проверяем наличие векторной БД
    chroma_path = Path("rag_data/chroma_db")
    if chroma_path.exists():
        print("✅ Векторная база данных найдена")
        return True
    else:
        print("❌ Векторная база данных не найдена")
        return False

def test_data_files():
    """Тестирует наличие файлов данных."""
    print("🔍 Тестирование файлов данных...")
    
    data_path = Path("data")
    required_files = ["Адаптология.docx", "Полный ИТН (3).docx"]
    
    missing_files = []
    for file in required_files:
        if not (data_path / file).exists():
            missing_files.append(file)
    
    if not missing_files:
        print("✅ Все файлы данных найдены")
        return True
    else:
        print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False

def test_config_files():
    """Тестирует наличие конфигурационных файлов."""
    print("🔍 Тестирование конфигурации...")
    
    config_files = [
        ".env",
        "backend/app/core/config.py",
        "telegram_bot/bot/core/config.py",
        "rag_pipeline/core/config.py"
    ]
    
    missing_files = []
    for file in config_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if not missing_files:
        print("✅ Все конфигурационные файлы найдены")
        return True
    else:
        print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False

def test_docker_setup():
    """Тестирует Docker конфигурацию."""
    print("🔍 Тестирование Docker конфигурации...")
    
    docker_files = [
        "docker-compose.yml",
        "backend/Dockerfile",
        "telegram_bot/Dockerfile",
        "analytics/Dockerfile"
    ]
    
    missing_files = []
    for file in docker_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if not missing_files:
        print("✅ Все Docker файлы найдены")
        return True
    else:
        print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False

async def main():
    """Основная функция тестирования."""
    print("🚀 Запуск тестирования интеграции Mind-Fix\n")
    
    tests = [
        ("Конфигурация", test_config_files),
        ("Файлы данных", test_data_files),
        ("RAG Pipeline", test_rag_pipeline),
        ("Docker конфигурация", test_docker_setup),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
        print()
    
    # Тест Backend API (если он запущен)
    backend_result = await test_backend_api()
    results.append(("Backend API", backend_result))
    
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("="*50)
    
    for name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nИтого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Система готова к работе.")
    else:
        print("⚠️  Некоторые тесты провалены. Проверьте настройки.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main()) 