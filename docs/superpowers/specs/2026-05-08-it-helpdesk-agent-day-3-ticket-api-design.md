# Enterprise IT Helpdesk Agent Day 3 Ticket API Design

## Purpose

Day 3 exposes the ticket core from Day 2 through FastAPI routes. The goal is to let IT staff and later Streamlit screens create, list, read, update, and summarize helpdesk tickets over HTTP.

Day 3 does not add Agent decision logic. Automatic ticket creation from user questions remains Day 4 scope.

## Scope

Included:

- `POST /tickets`
- `GET /tickets`
- `GET /tickets/{ticket_id}`
- `PATCH /tickets/{ticket_id}`
- `GET /tickets/stats`
- Route tests using FastAPI `TestClient`.
- Main app router registration.

Excluded:

- `POST /agent/ask`.
- LLM classification or priority inference.
- Streamlit ticket pages.
- Authentication, authorization, ownership, or approvals.
- Database migrations beyond the Day 2 SQLite table initialization.

## API Contract

### Create Ticket

```text
POST /tickets
```

Request body: `TicketCreate`.

Response body: `Ticket`.

The route delegates to `ticket_service.create_ticket`.

### List Tickets

```text
GET /tickets
```

Optional query filters:

- `status`
- `category`
- `priority`

Response body: `list[Ticket]`.

Invalid enum query values should return FastAPI's normal 422 validation response.

### Get Ticket

```text
GET /tickets/{ticket_id}
```

Response body: `Ticket`.

If the ticket does not exist, return HTTP 404 with:

```json
{"detail": "Ticket not found."}
```

### Update Ticket

```text
PATCH /tickets/{ticket_id}
```

Request body: `TicketUpdate`.

Response body: `Ticket`.

Only supplied fields are updated by the service/store layer. If the ticket does not exist, return HTTP 404 with:

```json
{"detail": "Ticket not found."}
```

### Ticket Stats

```text
GET /tickets/stats
```

Response body: `TicketStats`.

This route must be declared before `GET /tickets/{ticket_id}` so `stats` is not interpreted as a ticket ID.

## Implementation Design

Create `app/api/routes/tickets.py`.

The route module imports:

- `APIRouter`
- `HTTPException`
- ticket schemas and enums
- `ticket_service`
- `TicketNotFoundError`

It defines:

```python
router = APIRouter(prefix="/tickets", tags=["tickets"])
```

Routes should call service functions instead of constructing `TicketStore` directly. This preserves the boundary created on Day 2 and keeps SQLite out of the API layer.

Register the router in `app/main.py`:

```python
from app.api.routes.tickets import router as tickets_router
app.include_router(tickets_router)
```

## Error Handling

Pydantic/FastAPI validation handles invalid request bodies and invalid query enum values as 422.

`TicketNotFoundError` maps to HTTP 404. The API layer should not leak the internal ticket ID in the response body.

Unexpected exceptions should be left to FastAPI's default error handling.

## Testing Strategy

Add `tests/test_ticket_api.py`.

The route tests should monkeypatch `app.api.routes.tickets.ticket_service` functions. This keeps tests focused on routing, validation, serialization, and error mapping rather than SQLite behavior, which Day 2 already covers.

Required route tests:

- Create route passes `TicketCreate` to service and returns serialized ticket.
- List route passes enum filters to service.
- List route rejects invalid query enum values with 422.
- Get route returns serialized ticket.
- Get route maps `TicketNotFoundError` to 404.
- Patch route passes `TicketUpdate` to service and returns serialized ticket.
- Patch route maps `TicketNotFoundError` to 404.
- Stats route returns `TicketStats`.
- OpenAPI contains the ticket paths.

Full test verification should run all existing tests because `app/main.py` changes route registration.
