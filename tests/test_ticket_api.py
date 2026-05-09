from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ticket import (
    Ticket,
    TicketCategory,
    TicketPriority,
    TicketStats,
    TicketStatus,
    TicketUpdate,
)
from app.storage.ticket_store import TicketNotFoundError


client = TestClient(app)


def make_ticket(**overrides) -> Ticket:
    data = {
        "id": "TICKET-20260508-0001",
        "title": "VPN login fails",
        "description": "VPN reports authentication failure.",
        "category": TicketCategory.NETWORK,
        "priority": TicketPriority.HIGH,
        "status": TicketStatus.OPEN,
        "ai_summary": "User cannot authenticate to VPN.",
        "suggested_resolution": "Check account lock status and VPN client version.",
        "source_question": "Why can't I connect to VPN?",
        "created_at": datetime(2026, 5, 8, 9, 0, 0),
        "updated_at": datetime(2026, 5, 8, 9, 0, 0),
        "resolution_note": "",
    }
    data.update(overrides)
    return Ticket(**data)


def test_create_ticket_passes_payload_to_service(monkeypatch) -> None:
    captured = []
    ticket = make_ticket()

    def fake_create_ticket(payload):
        captured.append(payload)
        return ticket

    monkeypatch.setattr("app.api.routes.tickets.ticket_service.create_ticket", fake_create_ticket)

    response = client.post(
        "/tickets",
        json={
            "title": "VPN login fails",
            "description": "VPN reports authentication failure.",
            "category": "network",
            "priority": "high",
            "ai_summary": "User cannot authenticate to VPN.",
            "suggested_resolution": "Check account lock status and VPN client version.",
            "source_question": "Why can't I connect to VPN?",
        },
    )

    assert response.status_code == 200
    assert captured[0].title == "VPN login fails"
    assert captured[0].category == TicketCategory.NETWORK
    assert response.json()["id"] == "TICKET-20260508-0001"
    assert response.json()["created_at"] == "2026-05-08T09:00:00"


def test_list_tickets_passes_filters_to_service(monkeypatch) -> None:
    captured = []
    ticket = make_ticket()

    def fake_list_tickets(**filters):
        captured.append(filters)
        return [ticket]

    monkeypatch.setattr("app.api.routes.tickets.ticket_service.list_tickets", fake_list_tickets)

    response = client.get("/tickets?status=open&category=network&priority=high")

    assert response.status_code == 200
    assert captured == [
        {
            "status": TicketStatus.OPEN,
            "category": TicketCategory.NETWORK,
            "priority": TicketPriority.HIGH,
        }
    ]
    assert response.json()[0]["id"] == "TICKET-20260508-0001"


def test_list_tickets_rejects_invalid_filter_value() -> None:
    response = client.get("/tickets?status=waiting")

    assert response.status_code == 422


def test_get_ticket_returns_ticket(monkeypatch) -> None:
    captured = []
    ticket = make_ticket()

    def fake_get_ticket(ticket_id: str):
        captured.append(ticket_id)
        return ticket

    monkeypatch.setattr("app.api.routes.tickets.ticket_service.get_ticket", fake_get_ticket)

    response = client.get("/tickets/TICKET-20260508-0001")

    assert response.status_code == 200
    assert captured == ["TICKET-20260508-0001"]
    assert response.json()["title"] == "VPN login fails"


def test_get_ticket_returns_404_when_missing(monkeypatch) -> None:
    def fake_get_ticket(ticket_id: str):
        raise TicketNotFoundError(ticket_id)

    monkeypatch.setattr("app.api.routes.tickets.ticket_service.get_ticket", fake_get_ticket)

    response = client.get("/tickets/TICKET-20260508-9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found."}


def test_update_ticket_passes_payload_to_service(monkeypatch) -> None:
    captured = []
    ticket = make_ticket(status=TicketStatus.RESOLVED, resolution_note="VPN account reset.")

    def fake_update_ticket(ticket_id: str, payload: TicketUpdate):
        captured.append((ticket_id, payload))
        return ticket

    monkeypatch.setattr("app.api.routes.tickets.ticket_service.update_ticket", fake_update_ticket)

    response = client.patch(
        "/tickets/TICKET-20260508-0001",
        json={"status": "resolved", "resolution_note": "VPN account reset."},
    )

    assert response.status_code == 200
    assert captured[0][0] == "TICKET-20260508-0001"
    assert captured[0][1].status == TicketStatus.RESOLVED
    assert captured[0][1].resolution_note == "VPN account reset."
    assert response.json()["status"] == "resolved"


def test_update_ticket_returns_404_when_missing(monkeypatch) -> None:
    def fake_update_ticket(ticket_id: str, payload: TicketUpdate):
        raise TicketNotFoundError(ticket_id)

    monkeypatch.setattr("app.api.routes.tickets.ticket_service.update_ticket", fake_update_ticket)

    response = client.patch(
        "/tickets/TICKET-20260508-9999",
        json={"status": "closed"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found."}


def test_ticket_stats_returns_service_stats(monkeypatch) -> None:
    def fake_get_ticket_stats():
        return TicketStats(
            total=2,
            by_status={"open": 1, "resolved": 1},
            by_category={"network": 2},
            by_priority={"high": 1, "medium": 1},
        )

    monkeypatch.setattr("app.api.routes.tickets.ticket_service.get_ticket_stats", fake_get_ticket_stats)

    response = client.get("/tickets/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total": 2,
        "by_status": {"open": 1, "resolved": 1},
        "by_category": {"network": 2},
        "by_priority": {"high": 1, "medium": 1},
    }


def test_openapi_includes_ticket_paths() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/tickets" in paths
    assert "/tickets/{ticket_id}" in paths
    assert "/tickets/stats" in paths
