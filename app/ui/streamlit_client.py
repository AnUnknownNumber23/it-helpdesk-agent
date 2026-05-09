import requests


API_BASE = "http://127.0.0.1:8000"
DEFAULT_TIMEOUT = 60


def parse_response_payload(response):
    try:
        return response.json()
    except ValueError:
        raw_text = response.text.strip()
        return raw_text or "<empty response body>"


def _request(method, path, *, api_base=API_BASE, session=requests, timeout=DEFAULT_TIMEOUT, **kwargs):
    response = session.request(method, f"{api_base}{path}", timeout=timeout, **kwargs)
    return response, parse_response_payload(response)


def ingest_markdown(uploaded_file, *, api_base=API_BASE, session=requests, timeout=DEFAULT_TIMEOUT):
    return _request(
        "POST",
        "/rag/ingest",
        api_base=api_base,
        session=session,
        timeout=timeout,
        files={
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type or "text/markdown",
            )
        },
    )


def ask_rag(question: str, *, top_k: int = 4, api_base=API_BASE, session=requests, timeout=DEFAULT_TIMEOUT):
    return _request(
        "POST",
        "/rag/ask",
        api_base=api_base,
        session=session,
        timeout=timeout,
        json={"question": question, "top_k": top_k},
    )


def ask_agent(question: str, *, top_k: int = 4, api_base=API_BASE, session=requests, timeout=DEFAULT_TIMEOUT):
    return _request(
        "POST",
        "/agent/ask",
        api_base=api_base,
        session=session,
        timeout=timeout,
        json={"question": question, "top_k": top_k},
    )


def fetch_tickets(*, params=None, api_base=API_BASE, session=requests, timeout=DEFAULT_TIMEOUT):
    return _request(
        "GET",
        "/tickets",
        api_base=api_base,
        session=session,
        timeout=timeout,
        params=params or {},
    )


def get_ticket(ticket_id: str, *, api_base=API_BASE, session=requests, timeout=DEFAULT_TIMEOUT):
    return _request(
        "GET",
        f"/tickets/{ticket_id}",
        api_base=api_base,
        session=session,
        timeout=timeout,
    )


def update_ticket(ticket_id: str, payload, *, api_base=API_BASE, session=requests, timeout=DEFAULT_TIMEOUT):
    return _request(
        "PATCH",
        f"/tickets/{ticket_id}",
        api_base=api_base,
        session=session,
        timeout=timeout,
        json=payload,
    )


def fetch_ticket_stats(*, api_base=API_BASE, session=requests, timeout=DEFAULT_TIMEOUT):
    return _request(
        "GET",
        "/tickets/stats",
        api_base=api_base,
        session=session,
        timeout=timeout,
    )
