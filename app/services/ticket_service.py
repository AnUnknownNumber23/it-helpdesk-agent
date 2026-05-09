from app.core.config import settings
from app.schemas.ticket import (
    Ticket,
    TicketCategory,
    TicketCreate,
    TicketPriority,
    TicketStats,
    TicketStatus,
    TicketUpdate,
)
from app.storage.ticket_store import TicketStore


def get_default_store() -> TicketStore:
    return TicketStore(settings.ticket_db_path)


def create_ticket(payload: TicketCreate, *, store: TicketStore | None = None) -> Ticket:
    ticket_store = store or get_default_store()
    return ticket_store.create_ticket(payload)


def get_ticket(ticket_id: str, *, store: TicketStore | None = None) -> Ticket:
    ticket_store = store or get_default_store()
    return ticket_store.get_ticket(ticket_id)


def list_tickets(
    *,
    status: TicketStatus | None = None,
    category: TicketCategory | None = None,
    priority: TicketPriority | None = None,
    store: TicketStore | None = None,
) -> list[Ticket]:
    ticket_store = store or get_default_store()
    return ticket_store.list_tickets(status=status, category=category, priority=priority)


def update_ticket(ticket_id: str, payload: TicketUpdate, *, store: TicketStore | None = None) -> Ticket:
    ticket_store = store or get_default_store()
    return ticket_store.update_ticket(ticket_id, payload)


def get_ticket_stats(*, store: TicketStore | None = None) -> TicketStats:
    ticket_store = store or get_default_store()
    return ticket_store.get_stats()
