from langchain_openai import ChatOpenAI

from config import CHAT_MODEL_NAME, QWEN_API_KEY, QWEN_BASE_URL


def get_llm():
    """Возвращает LLM-клиент"""
    return ChatOpenAI(
        model=CHAT_MODEL_NAME,
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL,
        temperature=0,
    )
