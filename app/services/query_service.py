import logging

from openai import OpenAI

from app.core.config import settings
from app.rag.retriever import retrieve_documents
from app.schemas.rag import AskResponse, Citation


logger = logging.getLogger(__name__)
DEFAULT_USER_AGENT = "curl/8.0"
MAX_CONTEXT_CHARS = 1024


def create_openai_client() -> OpenAI:
    client_options = {
        "api_key": settings.openai_api_key,
        "default_headers": {"User-Agent": DEFAULT_USER_AGENT},
    }
    if settings.openai_base_url:
        client_options["base_url"] = settings.openai_base_url
    return OpenAI(**client_options)


def generate_answer_text(prompt: str) -> str:
    if not settings.has_openai_api_key():
        logger.warning("OpenAI API key is missing or placeholder; using fallback answer.")
        return f"Placeholder answer from {settings.chat_model} for prompt: {prompt}"

    try:
        client = create_openai_client()
        response = client.responses.create(
            model=settings.chat_model,
            input=prompt,
        )
        return response.output_text or ""
    except Exception as exc:
        logger.warning("OpenAI request failed; using fallback answer. Error: %s", exc)
        return f"Placeholder answer from {settings.chat_model} for prompt: {prompt}"


def build_citations(documents) -> list[Citation]:
    citations: list[Citation] = []
    seen: set[tuple[str, str]] = set()
    for document in documents:
        source = document.metadata.get("source", "unknown")
        snippet = document.page_content
        key = (source, snippet)
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            Citation(
                source=source,
                snippet=snippet,
            )
        )
    return citations


def build_context(documents) -> str:
    entries = []
    current_chars = 0
    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "unknown")
        entry = f"{index}. Source: {source}\n{document.page_content}"
        if current_chars == 0 and len(entry) > MAX_CONTEXT_CHARS:
            entries.append(entry[:MAX_CONTEXT_CHARS])
            break
        if current_chars + len(entry) > MAX_CONTEXT_CHARS:
            break
        entries.append(entry)
        current_chars += len(entry)
    return "\n\n".join(entries)


def build_grounded_prompt(question: str, context: str) -> str:
    return (
        "Answer the question using only the context below. Cite sources when you reuse them, and if "
        "the context does not contain the answer say 'I do not know'.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )


def answer_question(question: str, top_k: int) -> AskResponse:
    documents = retrieve_documents(question, top_k)
    if not documents:
        return AskResponse(
            answer="No relevant content found in the knowledge base.",
            citations=[],
        )

    context = build_context(documents)
    prompt = build_grounded_prompt(question, context)
    return AskResponse(
        answer=generate_answer_text(prompt),
        citations=build_citations(documents),
    )
