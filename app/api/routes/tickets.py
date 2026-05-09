from fastapi import APIRouter, HTTPException

from app.schemas.ticket import (
    Ticket,
    TicketCategory,
    TicketCreate,
    TicketPriority,
    TicketStats,
    TicketStatus,
    TicketUpdate,
)
from app.services import ticket_service
from app.storage.ticket_store import TicketNotFoundError


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=Ticket)
def create_ticket(request: TicketCreate) -> Ticket:
    return ticket_service.create_ticket(request)


@router.get("", response_model=list[Ticket])
def list_tickets(
    status: TicketStatus | None = None,
    category: TicketCategory | None = None,
    priority: TicketPriority | None = None,
) -> list[Ticket]:
    return ticket_service.list_tickets(status=status, category=category, priority=priority)


@router.get("/stats", response_model=TicketStats)
def get_ticket_stats() -> TicketStats:
    return ticket_service.get_ticket_stats()


@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: str) -> Ticket:
    try:
        return ticket_service.get_ticket(ticket_id)
    except TicketNotFoundError:
        raise HTTPException(status_code=404, detail="Ticket not found.")


@router.patch("/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: str, request: TicketUpdate) -> Ticket:
    try:
        return ticket_service.update_ticket(ticket_id, request)
    except TicketNotFoundError:
        raise HTTPException(status_code=404, detail="Ticket not found.")
