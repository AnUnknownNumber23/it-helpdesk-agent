from app.core.config import settings

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:  # pragma: no cover - exercised only when optional dep is missing
    HuggingFaceEmbeddings = None

_LOCAL_EMBEDDINGS_CACHE = {}


def get_embeddings():
    provider = settings.embedding_provider.strip().lower()

    if provider == "local":
        if HuggingFaceEmbeddings is None:
            raise ImportError(
                "Local embeddings require langchain-huggingface and sentence-transformers."
            )
        model_name = settings.local_embedding_model
        if model_name not in _LOCAL_EMBEDDINGS_CACHE:
            _LOCAL_EMBEDDINGS_CACHE[model_name] = HuggingFaceEmbeddings(
                model_name=model_name
            )
        return _LOCAL_EMBEDDINGS_CACHE[model_name]

    if settings.uses_openai_embeddings():
        if not settings.has_openai_api_key():
            raise ValueError("Embeddings require a real OpenAI-compatible API key.")
        return OpenAIEmbeddings(
            model=settings.embeddings_model,
            base_url=settings.openai_base_url or None,
            api_key=settings.openai_api_key,
        )

    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name="rag_assistant",
        persist_directory=settings.vector_store_dir,
        embedding_function=get_embeddings(),
    )
