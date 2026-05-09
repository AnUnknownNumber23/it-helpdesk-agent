from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.ticket import (
    Ticket,
    TicketCategory,
    TicketCreate,
    TicketPriority,
    TicketStats,
    TicketStatus,
    TicketUpdate,
)


def test_ticket_create_defaults_to_medium_priority_and_other_category() -> None:
    ticket = TicketCreate(
        title="Cannot connect to VPN",
        description="VPN client reports an authentication failure.",
        source_question="VPN does not work",
    )

    assert ticket.category == TicketCategory.OTHER
    assert ticket.priority == TicketPriority.MEDIUM
    assert ticket.ai_summary == ""
    assert ticket.suggested_resolution == ""


def test_ticket_create_rejects_unknown_category() -> None:
    with pytest.raises(ValidationError):
        TicketCreate(
            title="Need repository access",
            description="Please add me to the project.",
            category="finance",
            source_question="Need GitLab access",
        )


def test_ticket_update_allows_partial_status_update() -> None:
    update = TicketUpdate(status=TicketStatus.IN_PROGRESS)

    assert update.status == TicketStatus.IN_PROGRESS
    assert update.resolution_note is None
    assert update.priority is None


def test_ticket_model_contains_persisted_fields() -> None:
    created_at = datetime(2026, 5, 7, 10, 0, 0)
    updated_at = datetime(2026, 5, 7, 10, 5, 0)

    ticket = Ticket(
        id="TICKET-20260507-0001",
        title="Printer unavailable",
        description="The floor printer is not visible.",
        category=TicketCategory.HARDWARE,
        priority=TicketPriority.LOW,
        status=TicketStatus.OPEN,
        ai_summary="Printer discovery issue.",
        suggested_resolution="Check office network and printer queue.",
        source_question="Why can't I find the printer?",
        created_at=created_at,
        updated_at=updated_at,
        resolution_note="",
    )

    assert ticket.id == "TICKET-20260507-0001"
    assert ticket.created_at == created_at
    assert ticket.updated_at == updated_at


def test_ticket_stats_defaults_to_empty_counts() -> None:
    stats = TicketStats()

    assert stats.total == 0
    assert stats.by_status == {}
    assert stats.by_category == {}
    assert stats.by_priority == {}
