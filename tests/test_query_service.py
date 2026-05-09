from app.schemas.rag import AskResponse, Citation
from app.services import query_service
from app.services.query_service import answer_question, create_openai_client, generate_answer_text
from langchain_core.documents.base import Document
from app.rag.retriever import retrieve_documents


def test_create_openai_client_sets_proxy_compatible_user_agent(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(query_service.settings, "openai_api_key", "test-key")
    monkeypatch.setattr(query_service.settings, "openai_base_url", "https://example.test/v1")
    monkeypatch.setattr(query_service, "OpenAI", FakeClient)

    create_openai_client()

    assert captured["api_key"] == "test-key"
    assert captured["base_url"] == "https://example.test/v1"
    assert captured["default_headers"] == {"User-Agent": "curl/8.0"}


def test_generate_answer_text_fallback_references_prompt_when_api_key_missing(monkeypatch) -> None:
    monkeypatch.setattr(query_service.settings, "chat_model", "demo-model")
    monkeypatch.setattr(query_service.settings, "openai_api_key", "")
    warnings: list[str] = []
    monkeypatch.setattr(
        query_service.logger,
        "warning",
        lambda message, *args: warnings.append(message % args if args else message),
    )

    prompt = "Context:\nDoc text\n\nQuestion: What is RAG?"
    result = generate_answer_text(prompt)

    assert result == "Placeholder answer from demo-model for prompt: Context:\nDoc text\n\nQuestion: What is RAG?"
    assert warnings == ["OpenAI API key is missing or placeholder; using fallback answer."]


def test_generate_answer_text_uses_placeholder_when_api_key_is_example_value(monkeypatch) -> None:
    monkeypatch.setattr(query_service.settings, "chat_model", "demo-model")
    monkeypatch.setattr(query_service.settings, "openai_api_key", "your_api_key_here")

    prompt = "Context:\nDoc text\n\nQuestion: What is RAG?"
    result = generate_answer_text(prompt)

    assert result == "Placeholder answer from demo-model for prompt: Context:\nDoc text\n\nQuestion: What is RAG?"


def test_generate_answer_text_calls_openai_responses_api(monkeypatch) -> None:
    captured_kwargs: dict[str, object] = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured_kwargs.update(kwargs)
            return type("FakeResponse", (), {"output_text": "Real model answer"})()

    class FakeClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.responses = FakeResponses()

    monkeypatch.setattr(query_service.settings, "chat_model", "demo-model")
    monkeypatch.setattr(query_service.settings, "openai_api_key", "test-key")
    monkeypatch.setattr(query_service.settings, "openai_base_url", "https://example.test/v1")
    monkeypatch.setattr(query_service, "OpenAI", FakeClient)

    prompt = "Context:\nDoc text\n\nQuestion: What is RAG?"
    result = generate_answer_text(prompt)

    assert result == "Real model answer"
    assert captured_kwargs["input"] == prompt
    assert captured_kwargs["model"] == "demo-model"


def test_generate_answer_text_falls_back_when_openai_request_fails(monkeypatch) -> None:
    class FakeResponses:
        def create(self, **kwargs):
            raise RuntimeError("upstream blocked")

    class FakeClient:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setattr(query_service.settings, "chat_model", "demo-model")
    monkeypatch.setattr(query_service.settings, "openai_api_key", "test-key")
    monkeypatch.setattr(query_service, "OpenAI", FakeClient)
    warnings: list[str] = []
    monkeypatch.setattr(
        query_service.logger,
        "warning",
        lambda message, *args: warnings.append(message % args if args else message),
    )

    prompt = "Context:\nDoc text\n\nQuestion: What is RAG?"
    result = generate_answer_text(prompt)

    assert result == "Placeholder answer from demo-model for prompt: Context:\nDoc text\n\nQuestion: What is RAG?"
    assert warnings == ["OpenAI request failed; using fallback answer. Error: upstream blocked"]


def test_answer_question_builds_grounded_prompt_from_retrieved_documents(monkeypatch) -> None:
    fake_documents = [
        Document(
            page_content="RAG retrieves relevant chunks before generation.",
            metadata={"source": "guide.md"},
        ),
        Document(
            page_content="Vector stores keep embeddings for later search.",
            metadata={"source": "vector-store.md"},
        ),
    ]
    captured_prompts: list[str] = []

    def fake_retrieve(question: str, top_k: int):
        return fake_documents

    def fake_generate(prompt: str):
        captured_prompts.append(prompt)
        return "Grounded response"

    monkeypatch.setattr(query_service, "retrieve_documents", fake_retrieve)
    monkeypatch.setattr(query_service, "generate_answer_text", fake_generate)

    result = answer_question("What is RAG?", 3)

    prompt = captured_prompts[0]
    assert prompt.splitlines()[0].startswith("Answer the question using only the context below.")
    assert "do not know" in prompt.lower()
    assert "guide.md" in captured_prompts[0]
    assert "Vector stores keep embeddings" in captured_prompts[0]
    assert "Question: What is RAG?" in captured_prompts[0]
    assert result == AskResponse(
        answer="Grounded response",
        citations=[
            Citation(source="guide.md", snippet="RAG retrieves relevant chunks before generation."),
            Citation(source="vector-store.md", snippet="Vector stores keep embeddings for later search."),
        ],
    )


def test_answer_question_returns_default_message_when_no_documents(monkeypatch) -> None:
    monkeypatch.setattr(query_service, "retrieve_documents", lambda question, top_k: [])

    def fail_if_called(prompt: str):
        raise AssertionError("generate_answer_text should not be called when there are no documents")

    monkeypatch.setattr(query_service, "generate_answer_text", fail_if_called)

    result = answer_question("What is RAG?", 3)

    assert result == AskResponse(
        answer="No relevant content found in the knowledge base.",
        citations=[],
    )


def test_build_citations_deduplicates_same_source_and_snippet() -> None:
    documents = [
        Document(
            page_content="RAG retrieves relevant chunks before generation.",
            metadata={"source": "guide.md"},
        ),
        Document(
            page_content="RAG retrieves relevant chunks before generation.",
            metadata={"source": "guide.md"},
        ),
        Document(
            page_content="Vector stores keep embeddings for later search.",
            metadata={"source": "guide.md"},
        ),
    ]

    citations = query_service.build_citations(documents)

    assert citations == [
        Citation(
            source="guide.md",
            snippet="RAG retrieves relevant chunks before generation.",
        ),
        Citation(
            source="guide.md",
            snippet="Vector stores keep embeddings for later search.",
        ),
    ]


def test_build_context_stops_adding_entries_when_exceeding_budget(monkeypatch) -> None:
    monkeypatch.setattr(query_service, "MAX_CONTEXT_CHARS", 80)
    docs = [
        Document(page_content="A" * 40, metadata={"source": "doc1.md"}),
        Document(page_content="B" * 40, metadata={"source": "doc2.md"}),
    ]

    context = query_service.build_context(docs)

    assert "doc1.md" in context
    assert "doc2.md" not in context


def test_build_context_truncates_first_entry_when_it_alone_exceeds_budget(monkeypatch) -> None:
    monkeypatch.setattr(query_service, "MAX_CONTEXT_CHARS", 20)
    doc_text = "X" * 50
    documents = [Document(page_content=doc_text, metadata={"source": "doc1.md"})]

    context = query_service.build_context(documents)

    entry = f"1. Source: doc1.md\n{doc_text}"
    assert len(context) <= 20
    assert context == entry[:20]
    assert "doc2.md" not in context


def test_retrieve_documents_calls_similarity_search(monkeypatch) -> None:
    fake_documents = [
        Document(
            page_content="RAG retrieves relevant chunks before generation.",
            metadata={"source": "guide.md"},
        )
    ]

    class FakeStore:
        def __init__(self) -> None:
            self.calls: list[tuple[str, int]] = []

        def similarity_search(self, question: str, *, k: int):
            self.calls.append((question, k))
            return fake_documents

    fake_store = FakeStore()
    monkeypatch.setattr("app.rag.retriever.get_vector_store", lambda: fake_store)

    result = retrieve_documents("What is RAG?", 3)

    assert fake_store.calls == [("What is RAG?", 3)]
    assert result == fake_documents
