import ollama
import json
from datetime import datetime


def search_web(query: str) -> str:
    """Заглушка поиска в интернете."""
    return f"Результаты поиска по запросу '{query}': Python 3.12 вышел в октябре 2023"


def calculate(expression: str) -> str:
    """Вычисляет математическое выражение."""
    try:
        return str(eval(expression))
    except Exception:
        return "Ошибка вычисления"

def get_time() -> datetime:
    """Возвращает текущее время"""
    return datetime.now()


TOOLS = {
    "search_web": search_web,
    "calculate": calculate,
    "get_time": get_time
}

SYSTEM = """tools:
1. search_web(query) — поиск информации
2. calculate(expression) — калькулятор
3. get_time() - часы

Если нужен инструмент, ответь в JSON в формате:
{"tool": "имя_инструмента", "args": {"параметр": "значение"}}

Если инструмент не нужен, ответь в JSON в формате:
{"answer": "ответ пользователю"}"""


def run_agent(user_message: str) -> None:
    print(f"Вопрос пользователя:\n{user_message}\n")
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_message}
    ]
    response = ollama.chat(model="qwen2.5:7b", messages=messages, format="json")
    content = response.message.content
    print(f"Ответ модели:\n{content}\n")

    try:
        action = json.loads(content)
        if "tool" in action:
            tool_name = action["tool"]
            tool_args = action.get("args", {})
            print(f"[Агент выбрал инструмент: {tool_name}({tool_args})]")
            result = TOOLS[tool_name](**tool_args)
            print(f"[Результат: {result}]")

            # Второй проход: отдаём результат обратно модели
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": f"Результат: {result}. Ответь пользователю текстом."})
            tool_final = ollama.chat(model="qwen2.5:7b", messages=messages)
            print(f"\nОтвет пользователю: {tool_final.message.content}")
        else:
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": f"Перепиши ответ текстом."})
            answer_final = ollama.chat(model="qwen2.5:7b", messages=messages)
            print(f"\nОтвет пользователю: {answer_final.message.content}")
    except json.JSONDecodeError:
        print(f"\nОтвет: {content}")


if __name__ == "__main__":
    # Тест 1: Инструмент calculate
    print('=' * 60)
    print("Тест 1: Инструмент calculate")
    print('=' * 60)
    run_agent("Посчитай 900 * 600")

    # Тест 2: Инструмент search_web
    print('=' * 60)
    print("Тест 2: Инструмент search_web")
    print('=' * 60)
    run_agent("Найди информацию про Python 3.12")

    # Тест 3: Инструмент get_time
    print('=' * 60)
    print("Тест 3: Инструмент get_time")
    print('=' * 60)
    run_agent("Сколько времени?")

    # Тест 4: Инструмент не нужен
    print('=' * 60)
    print("Тест 4: Инструмент не нужен")
    print('=' * 60)
    run_agent("Привет, как дела?")

    # Тест 5: Попытка сломать инструмент calculate
    print('=' * 60)
    print("Тест 5: Попытка сломать инструмент calculate")
    print('=' * 60)
    run_agent("Подели 10 на 0")
