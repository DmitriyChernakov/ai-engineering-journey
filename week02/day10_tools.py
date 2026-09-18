import operator
from typing import TypedDict, Annotated

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition


# 1. ИНСТРУМЕНТЫ через декоратор @tool
@tool
def multiply(a: int, b: int) -> int:
    """Умножает два числа."""
    return a * b


@tool
def get_weather(city: str) -> str:
    """ ."""
    weather_data = {
        "москва": "Облачно, +15°C",
        "лондон": "Дождь, +12°C",
    }
    return weather_data.get(city.lower(), f"Нет данных для города: {city}")


@tool
def read_file(filepath: str) -> str:
    """Читает содержимое файла по указанному пути"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Файл '{filepath}' не найден"


@tool
def search_web(query: str) -> str:
    """Ищет информацию в интернете (заглушка)."""
    return f"Результаты поиска по запросу '{query}': Python 3.12 вышел в октябре 2023"


tools = [multiply, get_weather, read_file]

# 2. МОДЕЛЬ + bind_tools
llm = ChatOllama(model="qwen2.5:7b").bind_tools(tools)


class State(TypedDict):
    messages: Annotated[list, operator.add]


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# 3. ГРАФ С ВЕТВЛЕНИЕМ
graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.add_node("tools", ToolNode(tools=tools))  # готовая нода для выполнения инструментов

graph.add_edge(START, "chatbot")
# Если модель вернула tool_calls -> идём в нод "tools"
# Если не вернула -> идём в END
graph.add_conditional_edges("chatbot", tools_condition)
graph.add_edge("tools", "chatbot")  # после инструмента возвращаемся к модели

app = graph.compile()

# 4. ВИЗУАЛИЗАЦИЯ
print("\n--- Mermaid Graph Code ---")
print(app.get_graph().draw_mermaid())
print("--------------------------\n")

# 5. ТЕСТЫ
# Тест 1: должен вызвать multiply
print('=' * 20, " Тест 1: Инструмент multiply ", '=' * 20)
r1 = app.invoke({"messages": [HumanMessage(content="Сколько будет 25 * 48?")]})
if r1["messages"][1].tool_calls:
    print(f"Вызов инструмента {r1["messages"][1].tool_calls[0]["name"]}...\n")
else:
    print("Подходящий инструмент не найден.\n")
print("Ответ:\n", r1["messages"][-1].content)

# Тест 2: должен вызвать get_weather
print('\n', '=' * 20, " Тест 2: Инструмент get_weather ", '=' * 20)
r2 = app.invoke({"messages": [HumanMessage(content="Какая погода в Москве?")]})
if r2["messages"][1].tool_calls:
    print(f"Вызов инструмента {r2["messages"][1].tool_calls[0]["name"]}...\n")
else:
    print("Подходящий инструмент не найден.\n")
print("Ответ:\n", r2["messages"][-1].content)

# Тест 3: должен вызвать get_weather, но ничего не знает про город
print('\n', '=' * 20, " Тест 3: Инструмент get_weather, неизвестный город ", '=' * 20)
r3 = app.invoke({"messages": [HumanMessage(content="Какая погода в Мадриде?")]})
if r3["messages"][1].tool_calls:
    print(f"Вызов инструмента {r3["messages"][1].tool_calls[0]["name"]}...\n")
else:
    print("Подходящий инструмент не найден.\n")
print("Ответ:\n", r3["messages"][-1].content)

# Тест 4: НЕ должен вызывать инструменты
print('\n', '=' * 20, " Тест 4: Инструмент не нужен ", '=' * 20)
r4 = app.invoke({"messages": [HumanMessage(content="Расскажи шутку")]})
if r4["messages"][1].tool_calls:
    print(f"Вызов инструмента {r4["messages"][1].tool_calls[0]["name"]}...\n")
else:
    print("Подходящий инструмент не найден.\n")
print("Ответ:\n", r4["messages"][-1].content)

# Тест 5: должен вызвать read_file
print('\n', '=' * 20, " Тест 5: Инструмент read_file ", '=' * 20)
r5 = app.invoke({"messages": [HumanMessage(content="Прочитай файл test.txt")]})
if r5["messages"][1].tool_calls:
    print(f"Вызов инструмента {r5["messages"][1].tool_calls[0]["name"]}...\n")
else:
    print("Подходящий инструмент не найден.\n")
print("Ответ:\n", r5["messages"][-1].content)

# Тест 6: должен вызвать read_file, но файл не существует
print('\n', '=' * 20, " Тест 6: Инструмент read_file, файл не существует ", '=' * 20)
r6 = app.invoke({"messages": [HumanMessage(content="Прочитай файл test2.txt")]})
if r6["messages"][1].tool_calls:
    print(f"Вызов инструмента {r6["messages"][1].tool_calls[0]["name"]}...\n")
else:
    print("Подходящий инструмент не найден.\n")
print("Ответ:\n", r6["messages"][-1].content)

# Тест 7: попытка вызвать инструмент не из списка
print('\n', '=' * 20, " Тест 7: Попытка вызвать инструмент не из списка ", '=' * 20)
r7= app.invoke({"messages": [HumanMessage(content="Найди информацию про Python 3.12")]})
if r7["messages"][1].tool_calls:
    print(f"Вызов инструмента {r7["messages"][1].tool_calls[0]["name"]}...\n")
else:
    print("Подходящий инструмент не найден.\n")
print("Ответ:\n", r7["messages"][-1].content)
