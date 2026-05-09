# Enterprise IT Helpdesk Agent Day 2 Ticket Core Design

## Purpose

Day 2 adds the ticket core needed by later API and Agent work. The scope is limited to the domain schema, SQLite persistence, and a small service boundary. It does not expose ticket HTTP endpoints and does not add Agent decision logic.

This keeps the project in a testable intermediate state: ticket behavior can be verified independently before Day 3 connects it to FastAPI routes.

## Scope

Included:

- Ticket Pydantic schemas and enums.
- SQLite-backed ticket storage.
- Ticket service functions for later API and Agent callers.
- Configurable database path through `TICKET_DB_PATH`.
- Unit tests for schema validation, persistence behavior, service delegation, and config default.

Excluded:

- `GET /tickets`, `POST /tickets`, `PATCH /tickets/{ticket_id}`, or stats endpoints.
- `POST /agent/ask`.
- LLM-based classification, priority inference, or automatic ticket creation.
- Authentication, authorization, approval workflows, or multi-tenant separation.

## Data Model

Ticket categories:

- `account`
- `network`
- `software`
- `hardware`
- `permission`
- `other`

Ticket priorities:

- `low`
- `medium`
- `high`

Ticket statuses:

- `open`
- `in_progress`
- `resolved`
- `closed`

`TicketCreate` is the input model for creating a ticket. It contains title, description, category, priority, AI summary, suggested resolution, and the original user question. Category defaults to `other`, priority defaults to `medium`, and AI-generated text fields default to empty strings.

`TicketUpdate` supports partial updates for status, priority, and resolution note. All fields are optional so API routes can later accept narrow PATCH payloads.

`Ticket` represents persisted data. It extends the create payload with `id`, `status`, `created_at`, `updated_at`, and `resolution_note`.

`TicketStats` returns aggregate counts:

- total ticket count
- count by status
- count by category
- count by priority

## Persistence

The storage layer uses SQLite from the Python standard library. The database path comes from `settings.ticket_db_path`, which defaults to:

```text
data/tickets.db
```

`TicketStore` owns table creation and all SQL operations. It creates the `tickets` table if it does not exist.

Stored columns:

- `id`
- `title`
- `description`
- `category`
- `priority`
- `status`
- `ai_summary`
- `suggested_resolution`
- `source_question`
- `created_at`
- `updated_at`
- `resolution_note`

Ticket IDs use a date-based sequence format:

```text
TICKET-YYYYMMDD-0001
```

The sequence is scoped to the current date by counting existing rows with the same daily prefix. This is sufficient for the local MVP and easy to inspect during demos. A future production version should replace this with a concurrency-safe sequence or database-generated identifier.

Datetimes are stored as ISO strings and converted back to `datetime` objects when rows are loaded.

## Store Interface

`TicketStore` exposes:

- `create_ticket(payload: TicketCreate) -> Ticket`
- `get_ticket(ticket_id: str) -> Ticket`
- `list_tickets(status=None, category=None, priority=None) -> list[Ticket]`
- `update_ticket(ticket_id: str, payload: TicketUpdate) -> Ticket`
- `get_stats() -> TicketStats`

Missing ticket reads and updates raise `TicketNotFoundError`. API routes added later should translate this exception into HTTP 404.

List results are sorted newest first by `created_at` and then `id`.

## Service Boundary

`app/services/ticket_service.py` is a thin wrapper over `TicketStore`. It exists so API routes and Agent code can depend on service functions instead of constructing storage directly.

Service functions accept an optional `store` argument. This keeps tests simple and allows later callers to inject a specific store without global state.

Service functions:

- `create_ticket`
- `get_ticket`
- `list_tickets`
- `update_ticket`
- `get_ticket_stats`
- `get_default_store`

`get_default_store()` builds a `TicketStore` from `settings.ticket_db_path`.

## Error Handling

Day 2 introduces one domain-specific persistence exception:

```python
TicketNotFoundError
```

It is raised when a ticket ID does not exist during read or update operations. The exception is intentionally not converted to HTTP responses yet because Day 2 has no ticket API layer.

Schema validation remains the responsibility of Pydantic models. Invalid categories, priorities, statuses, or too-short create fields fail before storage code runs.

## Testing Strategy

Tests are focused on the new boundary:

- `tests/test_ticket_schema.py` verifies enum validation, defaults, partial updates, persisted model shape, and stats defaults.
- `tests/test_ticket_store.py` verifies table initialization, ID generation, create/get/list/update, filtering, missing ticket errors, and stats aggregation.
- `tests/test_ticket_service.py` verifies service functions delegate to the injected store with the correct payloads and filters.
- `tests/test_config.py` verifies the default ticket database path is under `data`.

The full test suite should pass after Day 2 because no existing RAG or health behavior changes.

## Day 3 Handoff

Day 3 should add the ticket API routes using the service boundary from this spec:

- `POST /tickets`
- `GET /tickets`
- `GET /tickets/{ticket_id}`
- `PATCH /tickets/{ticket_id}`
- `GET /tickets/stats`

The API layer should translate:

- Pydantic validation errors into normal FastAPI 422 responses.
- `TicketNotFoundError` into HTTP 404 responses.

The Day 3 implementation should not bypass `ticket_service.py` or call SQLite directly from routes.
