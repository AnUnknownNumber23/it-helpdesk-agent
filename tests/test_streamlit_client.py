from types import SimpleNamespace

from app.ui import streamlit_client


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, text="") -> None:
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def json(self):
        if isinstance(self._json_data, Exception):
            raise self._json_data
        return self._json_data


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[tuple[str, str, dict]] = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.response


def test_parse_response_payload_returns_json_for_json_body() -> None:
    response = FakeResponse(json_data={"answer": "hello"})

    payload = streamlit_client.parse_response_payload(response)

    assert payload == {"answer": "hello"}


def test_parse_response_payload_returns_text_for_non_json_body() -> None:
    response = FakeResponse(json_data=ValueError("bad json"), text="plain text")

    payload = streamlit_client.parse_response_payload(response)

    assert payload == "plain text"


def test_parse_response_payload_returns_placeholder_for_empty_text() -> None:
    response = FakeResponse(json_data=ValueError("bad json"), text=" ")

    payload = streamlit_client.parse_response_payload(response)

    assert payload == "<empty response body>"


def test_fetch_tickets_uses_tickets_endpoint_with_query_params() -> None:
    session = FakeSession(FakeResponse(json_data=[{"id": "TICKET-1"}]))

    response, payload = streamlit_client.fetch_tickets(
        api_base="http://example.test",
        params={"status": "open", "category": "network"},
        session=session,
    )

    assert response.status_code == 200
    assert payload == [{"id": "TICKET-1"}]
    assert session.calls == [
        (
            "GET",
            "http://example.test/tickets",
            {"params": {"status": "open", "category": "network"}, "timeout": 60},
        )
    ]


def test_fetch_ticket_stats_uses_stats_endpoint() -> None:
    session = FakeSession(FakeResponse(json_data={"total": 3}))

    response, payload = streamlit_client.fetch_ticket_stats(api_base="http://example.test", session=session)

    assert response.status_code == 200
    assert payload == {"total": 3}
    assert session.calls[0][1] == "http://example.test/tickets/stats"


def test_get_ticket_uses_ticket_detail_endpoint() -> None:
    session = FakeSession(FakeResponse(json_data={"id": "TICKET-1"}))

    response, payload = streamlit_client.get_ticket(
        "TICKET-1",
        api_base="http://example.test",
        session=session,
    )

    assert response.status_code == 200
    assert payload == {"id": "TICKET-1"}
    assert session.calls[0][1] == "http://example.test/tickets/TICKET-1"


def test_update_ticket_uses_patch_with_json_body() -> None:
    session = FakeSession(FakeResponse(json_data={"id": "TICKET-1"}))

    response, payload = streamlit_client.update_ticket(
        "TICKET-1",
        {"status": "resolved"},
        api_base="http://example.test",
        session=session,
    )

    assert response.status_code == 200
    assert payload == {"id": "TICKET-1"}
    assert session.calls[0][0] == "PATCH"
    assert session.calls[0][2]["json"] == {"status": "resolved"}


def test_ask_agent_posts_to_agent_endpoint() -> None:
    session = FakeSession(FakeResponse(json_data={"decision": {"action": "answer"}}))

    response, payload = streamlit_client.ask_agent(
        "Please help with VPN",
        api_base="http://example.test",
        session=session,
    )

    assert response.status_code == 200
    assert payload == {"decision": {"action": "answer"}}
    assert session.calls[0][1] == "http://example.test/agent/ask"


def test_ask_rag_posts_to_rag_endpoint() -> None:
    session = FakeSession(FakeResponse(json_data={"answer": "Use VPN steps"}))

    response, payload = streamlit_client.ask_rag(
        "What is VPN?",
        api_base="http://example.test",
        session=session,
    )

    assert response.status_code == 200
    assert payload == {"answer": "Use VPN steps"}
    assert session.calls[0][1] == "http://example.test/rag/ask"


def test_ingest_markdown_posts_file_payload() -> None:
    fake_file = SimpleNamespace(
        name="guide.md",
        getvalue=lambda: b"# Guide",
        type="text/markdown",
    )
    session = FakeSession(FakeResponse(json_data={"message": "ok"}))

    response, payload = streamlit_client.ingest_markdown(
        fake_file,
        api_base="http://example.test",
        session=session,
    )

    assert response.status_code == 200
    assert payload == {"message": "ok"}
    assert session.calls[0][1] == "http://example.test/rag/ingest"
    assert session.calls[0][2]["files"]["file"][0] == "guide.md"
