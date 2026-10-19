# QA Buddy v2 — AI-агент для генерации тест-кейсов

## Что это
CLI-инструмент, который принимает описание фичи и генерирует тест-кейсы с использованием LangGraph, инструментов и облачной LLM.

## Стек
- LangGraph (StateGraph + ToolNode)
- Qwen3.8-flash (облачный через OpenAI-совместимый API)
- Langfuse (observability)
- Python 3.14+

## Архитектура
[Схема: User Input → Agent → Tools (read_file, save) → Test Cases → Langfuse]

## Как запустить
1. Установить зависимости: `pip install -r requirements.txt`
2. Настроить `.env` (пример в `.env.example`)
3. Запустить: `python qa_buddy_v2.py`

## Результаты тестов
| Фича | Latency | Tokens | Качество |
|------|---------|-------|---------|
| Создание VLAN в веб-интерфейсе. | 186 s   | total: 12486 <br/>input: 8715 <br/>output: 3771| ⭐⭐⭐⭐ |
| Смена прошивки устройства через веб-интерфейс. | 177 s   | total: 11292<br/> input: 8077<br/> output: 3215 | ⭐⭐⭐⭐ |
| Переключение режима редактирования. Toggle Edit Mode. | 157 s   | total: 9843<br/> input: 7122<br/> output: 2721 | ⭐⭐⭐ |


## Следующие шаги
- Добавить evaluation через Ragas
- Подключить vector DB для контекста из документации