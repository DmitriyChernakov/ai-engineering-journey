from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

from llm_setup import setup_models

setup_models()


def main():
    print("Загрузка документов...")
    documents = SimpleDirectoryReader("docs").load_data()
    print(f"Загружено {len(documents)} документов")

    print("Индексация...")
    index = VectorStoreIndex.from_documents(documents)

    print("Сохранение индекса...")
    index.storage_context.persist(persist_dir="./storage")

    print("Готово! Индекс сохранён в ./storage/")


if __name__ == "__main__":
    main()
