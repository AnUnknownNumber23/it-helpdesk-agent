from pathlib import Path

from langchain_core.documents.base import Document

from app.rag.loaders import load_documents
from app.rag.splitter import split_documents
from app.rag.vector_store import get_vector_store


def load_and_split_file(file_path: Path) -> list[Document]:
    documents = load_documents(file_path)
    for document in documents:
        document.metadata["source"] = str(file_path)
    return split_documents(documents)


def ingest_file(file_path: Path) -> dict[str, int | str]:
    chunks = load_and_split_file(file_path)
    store = get_vector_store()
    store.add_documents(chunks)
    return {"file": file_path.name, "chunks": len(chunks)}
