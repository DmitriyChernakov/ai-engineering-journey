import operator
from typing import TypedDict, Annotated

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode


DANGEROUS_TOOL_NAMES = {"send_email"}


# 1. ИНСТРУМЕНТЫ:
@tool
def search_contacts(name: str) -> str:
    """Ищет контакт по имени. Безопасное действие."""
    contacts = {"Иван": "ivan@example.com", "Мария": "maria@example.com"}
    return contacts.get(name, f"Контакт '{name}' не найден")


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Отправляет email. ОПАСНОЕ ДЕЙСТВИЕ."""
    return f"Email отправлен на {to}: '{subject}'"


safe_tools = [search_contacts]
dangerous_tools = [send_email]
all_tools = safe_tools + dangerous_tools

# 2. МОДЕЛЬ + bind_tools
llm = ChatOllama(model="qwen2.5:7b").bind_tools(all_tools)


class State(TypedDict):
    messages: Annotated[list, operator.add]


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}



def route_tools(state: State):
    last_message = state["messages"][-1]

    if not last_message.tool_calls:
        return END

    tool_names = [tc['name'] for tc in last_message.tool_calls]
    if any(name in DANGEROUS_TOOL_NAMES for name in tool_names):
        return "dangerous_tools"
    return "safe_tools"


# 3. ГРАФ С HITL
graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.add_node("safe_tools", ToolNode(tools=safe_tools))
graph.add_node("dangerous_tools", ToolNode(tools=dangerous_tools))

graph.add_edge(START, "chatbot")
graph.add_conditional_edges(
    "chatbot",
    route_tools,
    ["safe_tools", "dangerous_tools", END]
)
graph.add_edge("safe_tools", "chatbot")
graph.add_edge("dangerous_tools", "chatbot")


memory = MemorySaver()
# Остановка только перед dangerous_tools
app = graph.compile(checkpointer=memory, interrupt_before=["dangerous_tools"])

# 4. ВИЗУАЛИЗАЦИЯ
print("\n--- Mermaid Graph Code ---")
print(app.get_graph().draw_mermaid())
print("--------------------------\n")


# 5. ТЕСТЫ
config = {"configurable": {"thread_id": "test-session-1"}}

# Тест 1: Безопасное действие (search_contacts)
print("=" * 50)
print("ТЕСТ 1: Безопасное действие (search_contacts)")
print("=" * 50)
result1 = app.invoke(
    {"messages": [HumanMessage(content="Найди контакт Ивана")]},
    config
)
print(f"Результат: {result1['messages'][-1].content}\n")

# Тест 2: Опасное действие (send_email)
print("=" * 50)
print("ТЕСТ 2: Опасное действие (send_email)")
print("=" * 50)
result2 = app.invoke(
    {"messages": [HumanMessage(content="Отправь email Ивану с темой 'Привет' и текстом 'Как дела?'")]},
    config
)
print("Агент хочет выполнить действие:")
print(f"  Tool calls: {result2['messages'][-1].tool_calls}")
print("\nПодтвердить отправку? (y/n): ", end="")

if input().lower() == "y":
    result2_final = app.invoke(None, config)  # Продолжить с чекпоинта
    print(f"Финальный результат: {result2_final['messages'][-1].content}")
else:
    print("Действие отменено.")

