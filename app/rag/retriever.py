from app.rag.vector_store import get_vector_store


def retrieve_documents(question: str, top_k: int):
    store = get_vector_store()
    return store.similarity_search(question, k=top_k)
