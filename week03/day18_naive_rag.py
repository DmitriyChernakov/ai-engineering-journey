import numpy as np
from openai import OpenAI

from config import QWEN_API_KEY, QWEN_BASE_URL, EMBEDDING_MODEL_NAME, CHAT_MODEL_NAME

RELEVANCE_THRESHOLD = 0.3

client = OpenAI(base_url=QWEN_BASE_URL, api_key=QWEN_API_KEY)

documents = [
    {
        "id": "doc1",
        "text": """
        Настройка VLAN
    
        Для создания VLAN необходимо:
        1. Открыть веб-интерфейс маршрутизатора
        2. Перейти в раздел "Switching" -> "VLAN"
        3. Нажать "Create VLAN"
        4. Указать VLAN ID (например, 100)
        5. Указать VLAN Name (необязательно)
        6. Выбрать режим работы (по умолчанию "Follow the interface status")
        7. Нажать кнопку "Create"
        """.strip(),
        "source": "VLAN_setup.md"
    },
    {
        "id": "doc2",
        "text": """
        Настройка физических интерфейсов:
    
        Для настройки физических интерфейсов необходимо:
        1. Открыть веб-интерфейс маршрутизатора
        2. Перейти в раздел "Interfaces" -> "Physical"
        3. Выбрать интерфейс из списка доступных и нажать на него (например, gigabitethernet 1/0/2)
        4. Указать IPv4 адрес в формате 0.0.0.0/0
        5. Указать Description (необязательно)
        6. В правом нижнем углу нажать кнопку "Save"
        """.strip(),
        "source": "Interface_setup.md"
    },
    {
        "id": "doc3",
        "text": """
        Настройка ACL
    
        Для настройки ACL необходимо:
        1. Открыть веб-интерфейс маршрутизатора
        2. Перейти в раздел "Shared Objects" -> "Access Lists"
        3. Нажать "Create Access List"
        4. Указать ACL Name либо оставить значение по умолчанию
        5. Нажать кнопку "Create"
        6. Добавить правило, нажав кнопку "Create Rule"
        7. Указать Rule ID в диапазоне 1-4094
        8. Нажать кнопку "Create"
        9. В правом нижнем углу нажать кнопку "Save"
        """.strip(),
        "source": "ACL_setup.md"
    },
]


def chunk_document(doc: dict) -> list[dict]:
    """Разбитие документа на чанки по абзацам"""
    paragraphs = doc["text"].split("\n\n")
    chunks = []

    for index, parag in enumerate(paragraphs):
        parag = parag.strip()
        if not parag:
            continue

        chunks.append({
            "text": parag,
            "source": doc["source"],
            "chunk_index": index,
        })
    return chunks


def embed_text(text: str) -> list[float]:
    """Получение вектора чисел"""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL_NAME,
        input=text
    )
    return response.data[0].embedding


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Косинусное сходство двух векторов"""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def retrieve(query_embedding: np.ndarray, chunks: list[dict], top_k: int = 2) -> list[dict]:
    """Нахождение top_k самых похожих чанков"""
    scored_chunks = []

    for chunk in chunks:
        simil = cosine_similarity(query_embedding, np.array(chunk["embedding"]))
        scored_chunks.append((simil, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    relevant = [(simil, chunk) for simil, chunk in scored_chunks if simil >= RELEVANCE_THRESHOLD]

    return [{"score": simil, **chunk} for simil, chunk in relevant[:top_k]]


def rag_query(question: str, chunks: list[dict]) -> str:
    """Формирование RAG-пайплайна"""
    query_embedding = np.array(embed_text(question))

    retrieved = retrieve(query_embedding, chunks, top_k=2)

    if not retrieved:
        return "Не нашел ответа в документации."

    context_parts = []
    for index, item in enumerate(retrieved, start=1):
        context_parts.append(
            f"[{index}] {item['source']} (chunk {item['chunk_index']}):\n{item['text']}"
        )

    context = "\n\n".join(context_parts)

    system_prompt = """Ты ассистент по QA-документации. Используй ТОЛЬКО предоставленный контекст.
    Если ответа нет в контексте — скажи "Не нашёл ответа в документации".
    Отвечай на русском языке, ссылаясь на источники в формате [1], [2]."""

    user_prompt = f"""Контекст:
    {context}
    
    Вопрос: {question}
    
    Ответь, ссылаясь на источники"""

    response = client.chat.completions.create(
        model=CHAT_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    print("\n[1/4] Чанкинг документов...")
    chunks = []
    for doc in documents:
        chunks.extend(chunk_document(doc))
    print(f"Создано {len(chunks)} чанков")

    print("\n[2/4] Векторизация чанков...")
    for index, chunk in enumerate(chunks, start=1):
        chunk["embedding"] = embed_text(chunk["text"])
        print(f"  Чанк {index}/{len(chunks)}: {chunk['source']} (чанк {chunk['chunk_index']})")

    test_questions = [
        "Как создать VLAN и настроить ACL?",
        "Как настроить физический интерфейс?",
        "Как приготовить борщ?",
    ]

    print("\n[3/4] Тестирование RAG-пайплайна...")
    print("=" * 60)

    for question in test_questions:
        print(f"\nВопрос: {question}")
        print("-" * 60)
        answer = rag_query(question=question, chunks=chunks)
        print(f"Ответ:\n{answer}")
        print("=" * 60)

    print("\n[4/4] Готово.")
