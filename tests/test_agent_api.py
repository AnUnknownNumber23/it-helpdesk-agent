from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.agent import AgentAction, AgentDecision
from app.schemas.rag import AskResponse, Citation
from app.schemas.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus


client = TestClient(app)


def make_decision(action: AgentAction, **overrides) -> AgentDecision:
    data = {
        "action": action,
        "category": TicketCategory.NETWORK,
        "priority": TicketPriority.LOW,
        "summary": "VPN question.",
        "user_message": "Use the knowledge base answer.",
        "ticket_title": "",
        "suggested_resolution": "",
    }
    data.update(overrides)
    return AgentDecision(**data)


def make_ticket() -> Ticket:
    return Ticket(
        id="TICKET-20260509-0001",
        title="GitLab access request",
        description="Please grant Developer access to the backend project.",
        category=TicketCategory.PERMISSION,
        priority=TicketPriority.MEDIUM,
        status=TicketStatus.OPEN,
        ai_summary="User needs GitLab access.",
        suggested_resolution="Confirm project owner approval and grant the requested role.",
        source_question="Please grant me Developer access to the GitLab backend project.",
        created_at=datetime(2026, 5, 9, 9, 0, 0),
        updated_at=datetime(2026, 5, 9, 9, 0, 0),
        resolution_note="",
    )


def test_agent_ask_returns_answer_without_ticket(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.routes.agent.query_service.answer_question",
        lambda question, top_k: AskResponse(
            answer="Run the VPN troubleshooting steps.",
            citations=[Citation(source="vpn-troubleshooting.md", snippet="Check DNS and reconnect.")],
        ),
    )
    monkeypatch.setattr(
        "app.api.routes.agent.agent_service.decide_next_action",
        lambda question, rag_answer, citations: make_decision(
            AgentAction.ANSWER,
            category=TicketCategory.NETWORK,
            priority=TicketPriority.LOW,
        ),
    )

    response = client.post("/agent/ask", json={"question": "How do I fix VPN DNS issues?", "top_k": 4})

    assert response.status_code == 200
    payload = response.json()
    assert payload["question"] == "How do I fix VPN DNS issues?"
    assert payload["answer"] == "Run the VPN troubleshooting steps."
    assert payload["decision"]["action"] == "answer"
    assert payload["ticket"] is None


def test_agent_ask_creates_ticket_when_decision_requests_it(monkeypatch) -> None:
    captured = []
    ticket = make_ticket()

    monkeypatch.setattr(
        "app.api.routes.agent.query_service.answer_question",
        lambda question, top_k: AskResponse(
            answer="Project owner approval is required.",
            citations=[Citation(source="gitlab-permission-request.md", snippet="Owner approval is required.")],
        ),
    )
    monkeypatch.setattr(
        "app.api.routes.agent.agent_service.decide_next_action",
        lambda question, rag_answer, citations: make_decision(
            AgentAction.CREATE_TICKET,
            category=TicketCategory.PERMISSION,
            priority=TicketPriority.MEDIUM,
            summary="GitLab access request.",
            user_message="I will create a ticket for IT to review the access request.",
            ticket_title="GitLab access request",
            suggested_resolution="Confirm project owner approval and grant the requested role.",
        ),
    )
    monkeypatch.setattr(
        "app.api.routes.agent.ticket_service.create_ticket",
        lambda payload: captured.append(payload) or ticket,
    )

    response = client.post(
        "/agent/ask",
        json={"question": "Please grant me Developer access to the GitLab backend project.", "top_k": 4},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"]["action"] == "create_ticket"
    assert payload["ticket"]["id"] == "TICKET-20260509-0001"
    assert captured[0].title == "GitLab access request"


def test_agent_ask_returns_clarify_without_ticket(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.routes.agent.query_service.answer_question",
        lambda question, top_k: AskResponse(answer="No relevant content found in the knowledge base.", citations=[]),
    )
    monkeypatch.setattr(
        "app.api.routes.agent.agent_service.decide_next_action",
        lambda question, rag_answer, citations: make_decision(
            AgentAction.CLARIFY,
            category=TicketCategory.OTHER,
            priority=TicketPriority.LOW,
            user_message="Please provide the affected system, the exact error message, what you expected to happen, and when the problem started.",
        ),
    )

    response = client.post("/agent/ask", json={"question": "It does not work", "top_k": 4})

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"]["action"] == "clarify"
    assert payload["ticket"] is None
    assert "error message" in payload["decision"]["user_message"]


def test_agent_ask_rejects_short_question() -> None:
    response = client.post("/agent/ask", json={"question": "hi", "top_k": 4})

    assert response.status_code == 422


def test_agent_openapi_includes_route() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/agent/ask" in response.json()["paths"]
