import json
import operator
import re
import uuid
from typing import TypedDict, Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langfuse.langchain import CallbackHandler
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


# ============ ИНСТРУМЕНТЫ ============

@tool
def read_file(filepath: str) -> str:
    """Читает содержимое файла по указанному пути."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"ОШИБКА: Файл '{filepath}' не найден. Проверь путь."
    except Exception as e:
        return f"ОШИБКА при чтении файла: {e}"


@tool
def count_test_cases(test_cases_json: str) -> str:
    """Считает статистику по тест-кейсам: количество каждого типа."""
    try:
        data = json.loads(test_cases_json)
        cases = data.get("test_cases", [])
        stats = {"total": len(cases)}
        for case in cases:
            t = case.get("type", "unknown")
            stats[t] = stats.get(t, 0) + 1
        return f"Статистика: {json.dumps(stats, ensure_ascii=False)}"
    except json.JSONDecodeError:
        return "ОШИБКА: Не удалось разобрать JSON для статистики."


# ============ СИСТЕМНЫЙ ПРОМПТ ============

SYSTEM_PROMPT = """Ты — опытный AI QA-инженер с 10-летним опытом в автоматизации тестирования.
Твоя задача: сгенерировать тест-кейсы по описанию фичи.

ВАЖНО: Отвечай строго на русском языке.

У тебя есть инструменты:
- read_file: прочитать описание фичи из файла
- save_test_cases: сохранить результат в файл
- count_test_cases: посчитать статистику по типам тест-кейсов

Процесс работы:
1. Если пользователь дал путь к файлу — сначала прочитай его через read_file
2. Сгенерируй тест-кейсы (обязательно включи positive, negative и edge_case сценарии)
3. Сохрани результат через save_test_cases
4. Покажи статистику через count_test_cases

Формат тест-кейсов (строго JSON):
{
  "test_cases": [
    {
      "id": 1,
      "name": "Краткое название",
      "type": "positive|negative|edge_case",
      "steps": ["шаг 1", "шаг 2"],
      "expected_result": "Что должно произойти",
      "priority": "high|medium|low"
    }
  ]
}

Правила:
- Генерируй от 5 до 10 тест-кейсов
- Обязательно покрывай негативные и граничные случаи
- Если инструмент вернул ошибку — исправь проблему и попробуй снова
"""

# ============ ГРАФ ============

tools = [read_file, count_test_cases]
llm = ChatOllama(model="qwen2.5:7b").bind_tools(tools)


class State(TypedDict):
    messages: Annotated[list, operator.add]


def agent(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


graph = StateGraph(State)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools=tools))

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")

app = graph.compile()


# ============ ИЗВЛЕЧЕНИЕ JSON ИЗ ТЕКСТА ============

def extract_json_from_text(text: str) -> dict | None:
    """Извлекает JSON-блок из текста ответа модели."""
    # Ищем блок ```json ... ```
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # Ищем любой блок { ... }
    brace_match = re.search(r'\{.*\}', text, re.DOTALL)
    if brace_match:
        json_str = brace_match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    return None


# ============ ЗАПУСК ============

def run_qa_buddy(user_request: str, session_name: str, max_iterations: int = 10):
    """Запускает агента с логированием в Langfuse."""
    langfuse_handler = CallbackHandler(
        trace_context={"trace_id": session_name}
    )

    result = app.invoke(
        {"messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_request)
        ]},
        config={
            "callbacks": [langfuse_handler],
            "recursion_limit": max_iterations
        }
    )

    # ОТЛАДКА: смотрим всю историю сообщений
    print("\n" + "=" * 60)
    print("ОТЛАДКА: все сообщения в графе")
    print("=" * 60)
    for i, msg in enumerate(result["messages"]):
        content_preview = repr(msg.content[:150]) if msg.content else "EMPTY"
        print(f"[{i}] {msg.__class__.__name__}: {content_preview}")
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            names = [tc["name"] for tc in msg.tool_calls]
            print(f"    → вызвал инструменты: {names}")

    return result["messages"][-1].content


def save_test_cases_to_file(test_cases: dict, filename: str) -> str:
    """Сохраняет тест-кейсы в файл (отдельная функция, не инструмент)."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_cases, f, indent=2, ensure_ascii=False)
        return f"УСПЕХ: Тест-кейсы сохранены в '{filename}'"
    except Exception as e:
        return f"Ошибка при сохранении: {e}"


if __name__ == "__main__":
    print("=" * 60)
    print("QA Buddy v2 — AI-агент для генерации тест-кейсов")
    print("=" * 60)

    request = (
        "Прочитай описание фичи из файла 'feature_example.txt', "
        "сгенерируй тест-кейсы и сохрани их в 'test_cases_output.json'"
    )

    print(f"\nЗапрос: {request}\n")
    print("Агент работает...\n")

    session_id = uuid.uuid4().hex
    final_answer = run_qa_buddy(request, session_name=session_id)
    print("=" * 60)
    print("ФИНАЛЬНЫЙ ОТВЕТ АГЕНТА:")
    print("=" * 60)
    print(final_answer)

    # ИЗВЛЕКАЕМ И СОХРАНЯЕМ ТЕСТ-КЕЙСЫ
    test_cases = extract_json_from_text(final_answer)
    if test_cases:
        save_message = save_test_cases_to_file(test_cases, "test_cases_output.json")
        print("\n" + save_message)
    else:
        print("Не удалось извлечь JSON из ответа агента")
        print("Проверь трассировку langfuse")

    # Даём время на отправку данных в Langfuse
    import time

    time.sleep(3)
    print("\nГотово! Проверь дашборд Langfuse и файл test_cases_output.json")
