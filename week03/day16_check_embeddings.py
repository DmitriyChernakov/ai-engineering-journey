from openai import OpenAI

from config import EMBEDDING_MODEL_NAME, QWEN_API_KEY, QWEN_BASE_URL


def get_client():
    """Возвращает LLM-клиент"""
    return OpenAI(
        base_url=QWEN_BASE_URL,
        api_key=QWEN_API_KEY
    )


def check_models(client: OpenAI):
    """Проверка доступных моделей"""
    print("=== Доступные модели ===")
    try:
        models = client.models.list()
        for model in models.data:
            print(f"  - {model.id}")
    except Exception as e:
        print(f"❌ Ошибка при получении списка моделей: {e}")


def check_embeddings(client: OpenAI):
    """Проверка эндпоинта embeddings"""
    print("\n=== Проверка embeddings ===")
    try:
        response = client.embeddings.create(
            input="Тестовый текст для эмбеддингов.",
            model=EMBEDDING_MODEL_NAME,
        )
        embedding = response.data[0].embedding
        print(f"✅ Эмбеддинги работают!")
        print(f"   Размерность вектора: {len(embedding)}")
        print(f"   Использованная модель: {response.model}")
        print(f"   Использовано токенов: {response.usage.total_tokens}")
        return True
    except Exception as e:
        print(f"❌ Эмбеддинги НЕ работают: {e}")
        return False


if __name__ == "__main__":
    ai_client = get_client()
    check_models(ai_client)
    check_embeddings(ai_client)
