from llama_index.core import load_index_from_storage
from llama_index.core.storage.storage_context import StorageContext

from llm_setup import setup_models
from tracing import setup_tracing

setup_models()
setup_tracing()

RELEVANCE_THRESHOLD = 0.3


def load_index():
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    return load_index_from_storage(storage_context)


def ask(question: str, threshold: float = RELEVANCE_THRESHOLD):
    index = load_index()
    query_engine = index.as_query_engine(similarity_top_k=3)
    response = query_engine.query(question)

    max_score = max((node.score for node in response.source_nodes), default=0.0)
    if max_score < threshold:
        print(f"\nНе нашёл ответа в документации. (score {max_score:.2f} < {threshold})")
        return

    print("\n" + "=" * 60)
    print(response.response)
    print("-" * 60)
    print("Источники:")
    for i, node in enumerate(response.source_nodes, 1):
        print(f"  [{i}] {node.metadata.get('file_name', 'unknown')} (score: {node.score:.2f})")
    print("=" * 60)


def main():
    print("qabrain — RAG-ассистент по QA-документации")
    while True:
        question = input("❓ Вопрос: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("Пока!")
            break
        if question:
            ask(question)


if __name__ == "__main__":
    main()
