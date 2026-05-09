# Enterprise IT Helpdesk Agent Day 6 Streamlit Tickets And Dashboard Design

## Purpose

Day 6 turns the Streamlit demo into a usable operational console. It adds ticket browsing, ticket editing, and a dashboard while preserving the existing ingest, RAG, and Agent tabs.

This is a Streamlit-only day. The backend ticket and Agent APIs from Days 3 to 5 are reused as-is.

## Scope

Included:

- Keep the existing `Ingest`, `RAG`, and `Agent` tabs.
- Add a `Tickets` tab for list, filter, inspect, and update.
- Add a `Dashboard` tab for ticket metrics and charts.
- Add a small Streamlit API helper module to centralize backend requests.
- Add unit tests for the helper functions.

Excluded:

- New FastAPI routes.
- Authentication or role-based access control.
- Drag-and-drop boards or kanban interactions.
- Ticket deletion.
- Multi-user collaboration.

## Streamlit Layout

The page should use five tabs:

- `Ingest`
- `RAG`
- `Agent`
- `Tickets`
- `Dashboard`

The page title should continue to present the project as:

```text
Enterprise IT Helpdesk Agent
```

## Tickets Tab

The `Tickets` tab should act as a lightweight helpdesk console.

Features:

- Filter tickets by `status`, `category`, and `priority`.
- Fetch ticket list from `GET /tickets`.
- Display a compact table of tickets.
- Select a ticket to inspect details from `GET /tickets/{ticket_id}`.
- Edit `status`, `priority`, and `resolution_note`.
- Save updates with `PATCH /tickets/{ticket_id}`.

The tab should not invent new ticket fields. It should only edit fields supported by the existing API.

## Dashboard Tab

The `Dashboard` tab should summarize ticket operations using `GET /tickets/stats`.

Display:

- total ticket count
- counts by status
- counts by category
- counts by priority

Use Streamlit native charts and metrics. The dashboard should remain simple and readable.

## Helper Module

Create a small helper module for API calls and payload formatting.

Responsibilities:

- parse JSON and text responses
- call `/rag/ingest`
- call `/rag/ask`
- call `/agent/ask`
- call `/tickets`
- call `/tickets/{ticket_id}`
- call `PATCH /tickets/{ticket_id}`
- call `/tickets/stats`

This keeps `streamlit_app.py` focused on layout and interaction.

## Error Handling

The Streamlit app should keep the current style of inline status messages:

- warnings for missing inputs
- errors for backend failures
- plain JSON blocks for structured responses

When backend calls fail, show the HTTP status code and raw payload when available.

## Testing Strategy

Add tests for the helper module:

- request payload parsing
- ticket list fetch URL and query params
- ticket detail fetch URL
- ticket update request body
- dashboard stats fetch URL
- agent ask request URL

Also run a syntax check on `streamlit_app.py` after modification.

Existing backend tests should continue to pass because this day does not change API contracts.
