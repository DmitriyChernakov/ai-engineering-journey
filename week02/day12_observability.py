import operator
from typing import TypedDict, Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langfuse.langchain import CallbackHandler
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition

# 1. НАСТРОЙКА LANGFUSE
load_dotenv()


# 2. ИНСТРУМЕНТЫ (из Дня 10)
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


tools = [multiply, get_weather, read_file]

# 3. МОДЕЛЬ + bind_tools
llm = ChatOllama(model="qwen2.5:7b").bind_tools(tools)


# 4. СОСТОЯНИЕ И ГРАФ
class State(TypedDict):
    messages: Annotated[list, operator.add]


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.add_node("tools", ToolNode(tools=tools))  # готовая нода для выполнения инструментов

graph.add_edge(START, "chatbot")
graph.add_conditional_edges("chatbot", tools_condition)
graph.add_edge("tools", "chatbot")  # после инструмента возвращаемся к модели

app = graph.compile()

# 5. СОЗДАЁМ CALLBACK ДЛЯ LANGFUSE
langfuse_handler = CallbackHandler()

# 6. ТЕСТЫ С OBSERVABILITY
# Тест 1: должен вызвать multiply
print("=" * 50)
print("Тест 1: Инструмент multiply")
print("=" * 50)
r1 = app.invoke(
    {"messages": [HumanMessage(content="Сколько будет 25 * 48?")]},
    config={"callbacks": [langfuse_handler]},
)
print("Ответ:\n", r1["messages"][-1].content)

# Тест 2: должен вызвать get_weather
print("=" * 50)
print("Тест 2: Инструмент get_weather")
print("=" * 50)
r2 = app.invoke(
    {"messages": [HumanMessage(content="Какая погода в Москве?")]},
    config={"callbacks": [langfuse_handler]},
)
print("Ответ:\n", r2["messages"][-1].content)

# Тест 3: должен вызвать get_weather, но ничего не знает про город
print("=" * 50)
print("Тест 3: Инструмент get_weather, неизвестный город")
print("=" * 50)
r3 = app.invoke(
    {"messages": [HumanMessage(content="Какая погода в Мадриде?")]},
    config={"callbacks": [langfuse_handler]},
)
print("Ответ:\n", r3["messages"][-1].content)

# Тест 4: НЕ должен вызывать инструменты
print("=" * 50)
print("Тест 4: Инструмент не нужен")
print("=" * 50)
r4 = app.invoke(
    {"messages": [HumanMessage(content="Расскажи шутку")]},
    config={"callbacks": [langfuse_handler]},
)
print("Ответ:\n", r4["messages"][-1].content)

# Тест 5: должен вызвать read_file
print("=" * 50)
print("Тест 5: Инструмент read_file")
print("=" * 50)
r5 = app.invoke(
    {"messages": [HumanMessage(content="Прочитай файл test.txt")]},
    config={"callbacks": [langfuse_handler]},
)
print("Ответ:\n", r5["messages"][-1].content)

# Тест 6: должен вызвать read_file, но файл не существует
print("=" * 50)
print("Тест 6: Инструмент read_file, файл не существует")
print("=" * 50)
r6 = app.invoke(
    {"messages": [HumanMessage(content="Прочитай файл test2.txt")]},
    config={"callbacks": [langfuse_handler]},
)
print("Ответ:\n", r6["messages"][-1].content)

# Тест 7: Сложный запрос (2 инструмента)
print("=" * 50)
print("Тест 7: Сложный запрос (2 инструмента)")
print("=" * 50)
r7 = app.invoke(
    {"messages": [HumanMessage(content="Какая погода в Лондоне и сколько будет 13 * 17")]},
    config={"callbacks": [langfuse_handler]},
)
print("Ответ:\n", r7["messages"][-1].content)

import time

time.sleep(2)
