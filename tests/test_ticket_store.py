import sqlite3
from pathlib import Path

import pytest

from app.schemas.ticket import TicketCategory, TicketCreate, TicketPriority, TicketStatus, TicketUpdate
from app.storage.ticket_store import TicketNotFoundError, TicketStore


def make_store(tmp_path: Path) -> TicketStore:
    return TicketStore(tmp_path / "tickets.db")


def make_ticket(**overrides) -> TicketCreate:
    data = {
        "title": "VPN login fails",
        "description": "VPN reports authentication failure for the user.",
        "category": TicketCategory.NETWORK,
        "priority": TicketPriority.HIGH,
        "ai_summary": "VPN authentication failure.",
        "suggested_resolution": "Check account lock status and VPN client version.",
        "source_question": "Why can't I connect to VPN?",
    }
    data.update(overrides)
    return TicketCreate(**data)


def test_store_initializes_tickets_table(tmp_path: Path) -> None:
    db_path = tmp_path / "tickets.db"

    TicketStore(db_path)

    with sqlite3.connect(db_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute(
                "select name from sqlite_master where type = 'table'"
            ).fetchall()
        }
    assert "tickets" in table_names


def test_create_ticket_persists_and_generates_daily_sequence_id(tmp_path: Path) -> None:
    store = make_store(tmp_path)

    first = store.create_ticket(make_ticket())
    second = store.create_ticket(make_ticket(title="GitLab access needed", category=TicketCategory.PERMISSION))

    assert first.id.startswith("TICKET-")
    assert first.id.endswith("-0001")
    assert second.id.endswith("-0002")
    assert first.status == TicketStatus.OPEN
    assert first.resolution_note == ""
    assert first.created_at == first.updated_at


def test_get_ticket_returns_persisted_ticket(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    created = store.create_ticket(make_ticket())

    loaded = store.get_ticket(created.id)

    assert loaded == created


def test_get_ticket_raises_for_missing_id(tmp_path: Path) -> None:
    store = make_store(tmp_path)

    with pytest.raises(TicketNotFoundError):
        store.get_ticket("TICKET-20990101-9999")


def test_list_tickets_orders_newest_first_and_filters(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    network = store.create_ticket(make_ticket(title="VPN issue", category=TicketCategory.NETWORK))
    permission = store.create_ticket(
        make_ticket(title="GitLab access needed", category=TicketCategory.PERMISSION, priority=TicketPriority.MEDIUM)
    )
    store.update_ticket(permission.id, TicketUpdate(status=TicketStatus.IN_PROGRESS))

    all_tickets = store.list_tickets()
    filtered = store.list_tickets(status=TicketStatus.IN_PROGRESS, category=TicketCategory.PERMISSION)

    assert [ticket.id for ticket in all_tickets] == [permission.id, network.id]
    assert [ticket.id for ticket in filtered] == [permission.id]


def test_update_ticket_changes_only_supplied_fields(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    created = store.create_ticket(make_ticket(priority=TicketPriority.LOW))

    updated = store.update_ticket(
        created.id,
        TicketUpdate(status=TicketStatus.RESOLVED, resolution_note="Reset user VPN account."),
    )

    assert updated.status == TicketStatus.RESOLVED
    assert updated.priority == TicketPriority.LOW
    assert updated.resolution_note == "Reset user VPN account."
    assert updated.updated_at > created.updated_at


def test_update_ticket_raises_for_missing_id(tmp_path: Path) -> None:
    store = make_store(tmp_path)

    with pytest.raises(TicketNotFoundError):
        store.update_ticket("TICKET-20990101-9999", TicketUpdate(status=TicketStatus.CLOSED))


def test_get_stats_counts_tickets_by_status_category_and_priority(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    open_ticket = store.create_ticket(make_ticket(category=TicketCategory.NETWORK, priority=TicketPriority.HIGH))
    store.create_ticket(make_ticket(title="Install office", category=TicketCategory.SOFTWARE, priority=TicketPriority.MEDIUM))
    store.update_ticket(open_ticket.id, TicketUpdate(status=TicketStatus.RESOLVED))

    stats = store.get_stats()

    assert stats.total == 2
    assert stats.by_status == {"open": 1, "resolved": 1}
    assert stats.by_category == {"network": 1, "software": 1}
    assert stats.by_priority == {"high": 1, "medium": 1}
