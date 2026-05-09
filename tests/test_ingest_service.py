from pathlib import Path
from unittest.mock import Mock

import pytest
from langchain_core.documents.base import Document

from app.rag.loaders import load_documents
from app.rag.vector_store import get_embeddings
from app.services.ingest_service import ingest_file, load_and_split_file


def test_load_and_split_file_populates_source_metadata(tmp_path: Path) -> None:
    file_path = tmp_path / "guide.md"
    body = "你好" + "甲" * 650
    file_path.write_text(body, encoding="utf-8")

    chunks = load_and_split_file(file_path)

    assert len(chunks) == 2
    assert chunks[0].page_content.startswith("你好")
    assert all(chunk.metadata["source"] == str(file_path) for chunk in chunks)
    assert len(chunks[0].page_content) == 500
    assert len(chunks[1].page_content) == 252

    assert chunks[0].page_content[-100:] == chunks[1].page_content[:100]


def test_load_documents_uses_utf8(tmp_path: Path, monkeypatch) -> None:
    file_path = tmp_path / "guide.md"
    file_path.write_text("content", encoding="utf-8")

    captured: list[tuple[str, str]] = []

    class FakeTextLoader:
        def __init__(self, path: str, encoding: str = "utf-8"):
            captured.append((path, encoding))

        def load(self):
            return []

    monkeypatch.setattr("app.rag.loaders.TextLoader", FakeTextLoader)

    load_documents(file_path)

    assert captured == [(str(file_path), "utf-8")]


def test_ingest_file_uses_chunks_and_store(tmp_path: Path, monkeypatch) -> None:
    file_path = tmp_path / "guide.md"
    file_path.write_text("content", encoding="utf-8")

    fake_chunks = [
        Document(page_content="chunked", metadata={"source": str(file_path)})
    ]

    monkeypatch.setattr(
        "app.services.ingest_service.load_and_split_file",
        Mock(return_value=fake_chunks),
    )

    fake_store = Mock()
    fake_store.add_documents = Mock()
    fake_store_factory = Mock(return_value=fake_store)
    monkeypatch.setattr(
        "app.services.ingest_service.get_vector_store",
        fake_store_factory,
    )

    result = ingest_file(file_path)

    fake_store.add_documents.assert_called_once_with(fake_chunks)
    fake_store_factory.assert_called_once()
    assert result["chunks"] == len(fake_chunks)


def test_get_embeddings_requires_api_key(monkeypatch) -> None:
    from app.rag import vector_store as vs

    class FakeSettings:
        def __init__(self) -> None:
            self.embedding_provider = "openai"
            self.openai_api_key = ""
            self.openai_base_url = ""
            self.embeddings_model = "text-embedding-3-small"
            self.local_embedding_model = (
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )

        def has_openai_api_key(self) -> bool:
            return False

        def uses_openai_embeddings(self) -> bool:
            return True

    monkeypatch.setattr(vs, "settings", FakeSettings())

    with pytest.raises(ValueError, match="Embeddings require a real"):
        get_embeddings()


def test_get_embeddings_uses_settings(monkeypatch) -> None:
    from app.rag import vector_store as vs

    captured = {}

    class FakeEmbeddings:
        def __init__(self, *, model, base_url, api_key):
            captured["model"] = model
            captured["base_url"] = base_url
            captured["api_key"] = api_key

    class FakeSettings:
        def __init__(self) -> None:
            self.embedding_provider = "openai"
            self.openai_api_key = "real-key"
            self.openai_base_url = "https://api.example"
            self.embeddings_model = "text-embedding-3-small"
            self.local_embedding_model = (
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )

        def has_openai_api_key(self) -> bool:
            return True

        def uses_openai_embeddings(self) -> bool:
            return True

    monkeypatch.setattr(vs, "OpenAIEmbeddings", FakeEmbeddings)
    monkeypatch.setattr(vs, "settings", FakeSettings())

    embeddings = get_embeddings()

    assert isinstance(embeddings, FakeEmbeddings)
    assert captured == {
        "model": "text-embedding-3-small",
        "base_url": "https://api.example",
        "api_key": "real-key",
    }


def test_get_embeddings_uses_local_provider(monkeypatch) -> None:
    from app.rag import vector_store as vs

    captured = {}

    class FakeEmbeddings:
        def __init__(self, *, model_name):
            captured["model_name"] = model_name

    class FakeSettings:
        def __init__(self) -> None:
            self.embedding_provider = "local"
            self.openai_api_key = ""
            self.openai_base_url = ""
            self.embeddings_model = "text-embedding-3-small"
            self.local_embedding_model = (
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )

        def has_openai_api_key(self) -> bool:
            return False

        def uses_openai_embeddings(self) -> bool:
            return False

    monkeypatch.setattr(vs, "HuggingFaceEmbeddings", FakeEmbeddings)
    monkeypatch.setattr(vs, "settings", FakeSettings())

    embeddings = get_embeddings()

    assert isinstance(embeddings, FakeEmbeddings)
    assert captured == {
        "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    }


def test_get_embeddings_caches_local_provider(monkeypatch) -> None:
    from app.rag import vector_store as vs

    captured = {"calls": 0}

    class FakeEmbeddings:
        def __init__(self, *, model_name):
            captured["calls"] += 1
            self.model_name = model_name

    class FakeSettings:
        def __init__(self) -> None:
            self.embedding_provider = "local"
            self.openai_api_key = ""
            self.openai_base_url = ""
            self.embeddings_model = "text-embedding-3-small"
            self.local_embedding_model = (
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )

        def has_openai_api_key(self) -> bool:
            return False

        def uses_openai_embeddings(self) -> bool:
            return False

    monkeypatch.setattr(vs, "HuggingFaceEmbeddings", FakeEmbeddings)
    monkeypatch.setattr(vs, "settings", FakeSettings())

    if hasattr(vs, "_LOCAL_EMBEDDINGS_CACHE"):
        vs._LOCAL_EMBEDDINGS_CACHE.clear()

    first = get_embeddings()
    second = get_embeddings()

    assert first is second
    assert captured["calls"] == 1


def test_get_embeddings_rejects_unknown_provider(monkeypatch) -> None:
    from app.rag import vector_store as vs

    class FakeSettings:
        def __init__(self) -> None:
            self.embedding_provider = "invalid"
            self.openai_api_key = ""
            self.openai_base_url = ""
            self.embeddings_model = "text-embedding-3-small"
            self.local_embedding_model = (
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )

        def has_openai_api_key(self) -> bool:
            return False

        def uses_openai_embeddings(self) -> bool:
            return False

    monkeypatch.setattr(vs, "settings", FakeSettings())

    with pytest.raises(ValueError, match="Unsupported embedding provider"):
        get_embeddings()

