import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    """Читает обязательную переменную окружения, падает с понятной ошибкой"""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Не задана переменная окружения {name} - пропишите ее в .env")
    return value


LANGFUSE_PUBLIC_KEY = _require("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = _require("LANGFUSE_SECRET_KEY")
LANGFUSE_BASE_URL = _require("LANGFUSE_BASE_URL")
MODEL_NAME = _require("MODEL_NAME")
QWEN_API_KEY = _require("QWEN_API_KEY")
QWEN_BASE_URL = _require("QWEN_BASE_URL")
