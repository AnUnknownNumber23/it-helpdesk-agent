from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.rag import AskResponse, Citation
from app.services import query_service


client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_endpoint_passes_question_and_top_k_to_service(monkeypatch) -> None:
    captured: list[tuple[str, int]] = []

    def fake_answer_question(question: str, top_k: int) -> AskResponse:
        captured.append((question, top_k))
        return AskResponse(
            answer="Mocked API answer",
            citations=[
                Citation(
                    source="guide.md",
                    snippet="RAG retrieves relevant chunks before generation.",
                )
            ],
        )

    monkeypatch.setattr("app.api.routes.rag.answer_question", fake_answer_question)

    response = client.post(
        "/rag/ask",
        json={"question": "What is RAG?", "top_k": 3},
    )

    assert response.status_code == 200
    assert captured == [("What is RAG?", 3)]
    assert response.json() == {
        "answer": "Mocked API answer",
        "citations": [
            {
                "source": "guide.md",
                "snippet": "RAG retrieves relevant chunks before generation.",
            }
        ],
    }


def test_ask_endpoint_rejects_too_short_question() -> None:
    response = client.post(
        "/rag/ask",
        json={"question": "hi", "top_k": 3},
    )

    assert response.status_code == 422


def test_ask_endpoint_rejects_out_of_range_top_k() -> None:
    response = client.post(
        "/rag/ask",
        json={"question": "What is RAG?", "top_k": 100},
    )

    assert response.status_code == 422


def test_ingest_endpoint_uploads_markdown_and_calls_ingest_file(monkeypatch, tmp_path) -> None:
    captured: list[Path] = []
    markdown_content = "# Guide\n\nRAG content."

    def fake_ingest_file(file_path: Path) -> dict[str, int | str]:
        captured.append(file_path)
        return {"file": file_path.name, "chunks": 8}

    monkeypatch.setattr("app.api.routes.rag.ingest_file", fake_ingest_file)
    monkeypatch.setattr(
        "app.api.routes.rag.settings",
        SimpleNamespace(upload_dir=str(tmp_path)),
        raising=False,
    )

    response = client.post(
        "/rag/ingest",
        files={"file": ("guide.md", markdown_content.encode("utf-8"), "text/markdown")},
    )

    saved_path = tmp_path / "guide.md"
    assert response.status_code == 200
    assert saved_path.read_text(encoding="utf-8") == markdown_content
    assert captured == [saved_path]
    assert response.json() == {
        "message": "Ingestion completed.",
        "file": "guide.md",
        "file_path": str(saved_path),
        "chunks": 8,
    }


def test_ingest_endpoint_returns_404_when_file_is_missing(monkeypatch, tmp_path) -> None:
    def fake_ingest_file(file_path: Path) -> None:
        raise FileNotFoundError

    monkeypatch.setattr("app.api.routes.rag.ingest_file", fake_ingest_file)
    monkeypatch.setattr(
        "app.api.routes.rag.settings",
        SimpleNamespace(upload_dir=str(tmp_path)),
        raising=False,
    )

    response = client.post(
        "/rag/ingest",
        files={"file": ("guide.md", b"# Missing", "text/markdown")},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "File not found."}


def test_ingest_endpoint_returns_400_for_directory_path(monkeypatch, tmp_path) -> None:
    def fake_ingest_file(file_path: Path) -> None:
        raise IsADirectoryError

    monkeypatch.setattr("app.api.routes.rag.ingest_file", fake_ingest_file)
    monkeypatch.setattr(
        "app.api.routes.rag.settings",
        SimpleNamespace(upload_dir=str(tmp_path)),
        raising=False,
    )

    response = client.post(
        "/rag/ingest",
        files={"file": ("guide.md", b"# Directory", "text/markdown")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file path."}


def test_ingest_endpoint_rejects_non_markdown_upload() -> None:
    response = client.post(
        "/rag/ingest",
        files={"file": ("guide.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Only .md files are supported."}


def test_ingest_endpoint_rejects_missing_file_name() -> None:
    response = client.post(
        "/rag/ingest",
        files={"dummy": ("placeholder.txt", b"not used", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Missing file name."}


def test_ingest_endpoint_returns_400_when_save_target_is_directory(monkeypatch, tmp_path) -> None:
    (tmp_path / "guide.md").mkdir()

    monkeypatch.setattr(
        "app.api.routes.rag.settings",
        SimpleNamespace(upload_dir=str(tmp_path)),
        raising=False,
    )

    response = client.post(
        "/rag/ingest",
        files={"file": ("guide.md", b"# Directory target", "text/markdown")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file path."}


def test_ingest_openapi_request_body_is_required() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    request_body = response.json()["paths"]["/rag/ingest"]["post"]["requestBody"]
    assert request_body["required"] is True
