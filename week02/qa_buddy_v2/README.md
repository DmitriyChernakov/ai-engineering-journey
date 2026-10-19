# QA Buddy v2 — AI-агент для генерации тест-кейсов

## Что это
AI-агент для автоматической генерации тест-кейсов из описания фичи.

## Стек
- LangGraph (StateGraph + ToolNode)
- Qwen3.8-flash (облачный через OpenAI-совместимый API)
- Langfuse (observability)
- Python 3.14+

## Как работает
Агент использует 3 инструмента:
1. `read_file` — читает описание фичи из `.txt` файла
2. `save_test_cases` — валидирует и сохраняет JSON с тест-кейсами
3. `count_test_cases` — считает статистику (positive/negative/edge_case)

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
