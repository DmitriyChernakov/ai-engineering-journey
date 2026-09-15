import operator
from typing import TypedDict, Annotated

from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

# 1. ОПРЕДЕЛЯЕМ СОСТОЯНИЕ (STATE)
class State(TypedDict):
    messages: Annotated[list, operator.add]

# Инициализируем LLM
llm = ChatOllama(model="qwen2.5:7b", temperature=0)

# 2. ОПРЕДЕЛЯЕМ НОДЫ (NODES)
def chatbot(state: State):
    """Первый нод: генерирует ответ на вопрос."""
    print("--- Нод Chatbot: Думаю... ---")
    response = llm.invoke(state["messages"])
    # Возвращаем только новое сообщение. operator.add сам добавит его в history.
    return {"messages": [response]}


def summarizer(state: State):
    """Второй нод: сокращает ответ первого."""
    print("--- Нод Summarizer: Сокращаю... ---")
    # Берем последнее сообщение (ответ чат-бота)
    last_message = state["messages"][-1].content

    prompt = f"Сократи следующий текст до одного предложения, сохранив суть и язык текста:\n\n{last_message}"

    # Вызываем LLM еще раз
    summary_response = llm.invoke([HumanMessage(content=prompt)])

    # Возвращаем как новое сообщение
    return {"messages": [AIMessage(content=f"Summary: {summary_response.content}")]}

def critic(state: State):
    """Третий нод: оценивает саммари второго."""
    print("--- Нод Critic: Оцениваю... ---")
    # Берем изначальный ответ бота и саммари
    original_message = state["messages"][-2].content
    summary_message = state["messages"][-1].content

    prompt = f"""Есть исходный текст:\n\n{original_message}\n\n
    Оцени саммари этого текста по шкале от 1 до 5:\n\n{summary_message}"""

    # Снова вызываем LLM
    rate_response = llm.invoke([HumanMessage(content=prompt)])

    # Возвращаем как новое сообщение
    return {"messages": [AIMessage(content=f"Rate: {rate_response.content}")]}


# 3. СОБИРАЕМ ГРАФ
graph_builder = StateGraph(State)

# Добавляем узлы
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("summarizer", summarizer)
graph_builder.add_node("critic", critic)

# Соединяем узлы (Edges)
# START -> chatbot -> summarizer -> critic -> END
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "summarizer")
graph_builder.add_edge("summarizer", "critic")
graph_builder.add_edge("critic", END)

# Компилируем граф
graph = graph_builder.compile()

# 4. ВИЗУАЛИЗАЦИЯ
# Выводит код для Mermaid.js
print("\n--- Mermaid Graph Code ---")
print(graph.get_graph().draw_mermaid())
print("--------------------------\n")

# 5. ЗАПУСК
print("Запускаем граф...")
initial_state = {
    "messages": [HumanMessage(content="Что такое LangGraph?")]
}

# invoke запускает исполнение от START до END
result = graph.invoke(initial_state)

print("\n--- Финальная история сообщений ---")
for msg in result["messages"]:
    print(f"[{msg.__class__.__name__}]: {msg.content}")
