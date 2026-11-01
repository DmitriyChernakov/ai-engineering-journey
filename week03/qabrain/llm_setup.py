from llama_index.core import Settings
from llama_index.core.base.llms.types import LLMMetadata
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from config import QWEN_API_KEY, QWEN_BASE_URL, EMBEDDING_MODEL_NAME, CHAT_MODEL_NAME

SYSTEM_PROMPT = (
    "Ты — QA-ассистент по документации сетевого оборудования. "
    "Отвечай только по переданному контексту, не используй сторонние знания. "
    "Ссылайся на источники по имени файла из метаданных контекста. "
    "Если ответа в контексте нет — ответь ровно: «Не нашёл ответа в документации»."
)


class CustomOpenAI(OpenAI):
    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=204800,
            num_output=8192,
            is_chat_model=True,
            model_name=self.model,
        )


def setup_models() -> None:
    """Настраивает глобальные Settings. Вызывается один раз при старте процесса."""
    Settings.llm = CustomOpenAI(
        model=CHAT_MODEL_NAME,
        api_key=QWEN_API_KEY,
        api_base=QWEN_BASE_URL,
        temperature=0.1,
        system_prompt=SYSTEM_PROMPT,
    )
    Settings.embed_model = OpenAIEmbedding(
        model_name=EMBEDDING_MODEL_NAME,
        api_key=QWEN_API_KEY,
        api_base=QWEN_BASE_URL,
    )
