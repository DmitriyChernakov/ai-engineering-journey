from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.core.base.llms.types import LLMMetadata
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from config import QWEN_API_KEY, QWEN_BASE_URL, EMBEDDING_MODEL_NAME, CHAT_MODEL_NAME


class CustomOpenAI(OpenAI):
    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=204800,
            num_output=8192,
            is_chat_model=True,
            model_name=self.model,
        )


Settings.llm = CustomOpenAI(
    model=CHAT_MODEL_NAME,
    api_key=QWEN_API_KEY,
    api_base=QWEN_BASE_URL,
    temperature=0.1,
)

Settings.embed_model = OpenAIEmbedding(
    model_name=EMBEDDING_MODEL_NAME,
    api_key=QWEN_API_KEY,
    api_base=QWEN_BASE_URL,
)

documents = [
    Document(
        text="""Настройка VLAN
    
        Для создания VLAN необходимо:
        1. Открыть веб-интерфейс маршрутизатора
        2. Перейти в раздел "Switching" -> "VLAN"
        3. Нажать "Create VLAN"
        4. Указать VLAN ID (например, 100)
        5. Указать VLAN Name (необязательно)
        6. Выбрать режим работы (по умолчанию "Follow the interface status")
        7. Нажать кнопку "Create"
        """,
        metadata={"source": "VLAN_setup.md", "doc_title": "Настройка VLAN"},
    ),
    Document(
        text="""Настройка физических интерфейсов:
    
        Для настройки физических интерфейсов необходимо:
        1. Открыть веб-интерфейс маршрутизатора
        2. Перейти в раздел "Interfaces" -> "Physical"
        3. Выбрать интерфейс из списка доступных и нажать на него (например, gigabitethernet 1/0/2)
        4. Указать IPv4 адрес в формате 0.0.0.0/0
        5. Указать Description (необязательно)
        6. В правом нижнем углу нажать кнопку "Save"
        """,
        metadata={"source": "Interface_setup.md", "doc_title": "Настройка интерфейсов"},
    ),
    Document(
        text="""Настройка ACL
    
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
        """,
        metadata={"source": "ACL_setup.md", "doc_title": "Настройка ACL"},
    ),
]

index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(similarity_top_k=2)

test_questions = [
    "Как создать VLAN и настроить ACL?",
    "Как настроить физический интерфейс?",
    "Как приготовить борщ?",
]

if __name__ == "__main__":
    for question in test_questions:
        print(f"\nВопрос: {question}")
        print("-" * 60)
        response = query_engine.query(question)
        print(f"Ответ:\n{response}")
        print(f"Источники: {response.source_nodes}")
        print("=" * 60)
