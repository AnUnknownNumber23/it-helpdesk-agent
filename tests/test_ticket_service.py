from app.schemas.ticket import TicketCategory, TicketCreate, TicketPriority, TicketStatus, TicketUpdate
from app.services import ticket_service


class FakeStore:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def create_ticket(self, payload: TicketCreate):
        self.calls.append(("create", payload))
        return "created-ticket"

    def get_ticket(self, ticket_id: str):
        self.calls.append(("get", ticket_id))
        return "loaded-ticket"

    def list_tickets(self, **filters):
        self.calls.append(("list", filters))
        return ["ticket-a"]

    def update_ticket(self, ticket_id: str, payload: TicketUpdate):
        self.calls.append(("update", (ticket_id, payload)))
        return "updated-ticket"

    def get_stats(self):
        self.calls.append(("stats", None))
        return "ticket-stats"


def make_payload() -> TicketCreate:
    return TicketCreate(
        title="Need GitLab access",
        description="Please add me to the backend project.",
        category=TicketCategory.PERMISSION,
        priority=TicketPriority.MEDIUM,
        source_question="Can I get GitLab access?",
    )


def test_create_ticket_delegates_to_store() -> None:
    store = FakeStore()
    payload = make_payload()

    result = ticket_service.create_ticket(payload, store=store)

    assert result == "created-ticket"
    assert store.calls == [("create", payload)]


def test_get_ticket_delegates_to_store() -> None:
    store = FakeStore()

    result = ticket_service.get_ticket("TICKET-20260507-0001", store=store)

    assert result == "loaded-ticket"
    assert store.calls == [("get", "TICKET-20260507-0001")]


def test_list_tickets_delegates_filters_to_store() -> None:
    store = FakeStore()

    result = ticket_service.list_tickets(
        status=TicketStatus.OPEN,
        category=TicketCategory.PERMISSION,
        priority=TicketPriority.HIGH,
        store=store,
    )

    assert result == ["ticket-a"]
    assert store.calls == [
        (
            "list",
            {
                "status": TicketStatus.OPEN,
                "category": TicketCategory.PERMISSION,
                "priority": TicketPriority.HIGH,
            },
        )
    ]


def test_update_ticket_delegates_to_store() -> None:
    store = FakeStore()
    payload = TicketUpdate(status=TicketStatus.RESOLVED, resolution_note="Access granted.")

    result = ticket_service.update_ticket("TICKET-20260507-0001", payload, store=store)

    assert result == "updated-ticket"
    assert store.calls == [("update", ("TICKET-20260507-0001", payload))]


def test_get_ticket_stats_delegates_to_store() -> None:
    store = FakeStore()

    result = ticket_service.get_ticket_stats(store=store)

    assert result == "ticket-stats"
    assert store.calls == [("stats", None)]
