# Enterprise IT Helpdesk Agent Day 5 Agent API Design

## Purpose

Day 5 exposes the Agent decision flow through FastAPI and connects it to the Streamlit demo. It turns a user question into a single response that can answer, clarify, or create a helpdesk ticket.

This is the first end-to-end employee-facing Agent workflow. It does not add authentication, permissions, dashboards, or multi-step conversations.

## Scope

Included:

- `POST /agent/ask`
- Agent API request and response schemas.
- Integration of `query_service`, `agent_service`, and `ticket_service`.
- Optional ticket creation when the decision is `create_ticket`.
- Streamlit Agent tab that calls the new API.
- Unit and API tests for the Agent flow.

Excluded:

- Login, authorization, or role-based access control.
- Multi-turn Agent memory.
- Streamlit ticket management screens.
- Dashboard charts.
- Any change to the existing `/rag/*` or `/tickets/*` contracts.

## API Contract

### Ask Agent

```text
POST /agent/ask
```

Request body:

```json
{
  "question": "string",
  "top_k": 4
}
```

Response body:

```json
{
  "question": "string",
  "answer": "string",
  "citations": [],
  "decision": {
    "action": "answer | clarify | create_ticket",
    "category": "account | network | software | hardware | permission | other",
    "priority": "low | medium | high",
    "summary": "string",
    "user_message": "string",
    "ticket_title": "string",
    "suggested_resolution": "string"
  },
  "ticket": null
}
```

If `decision.action` is `create_ticket`, the `ticket` field contains the created `Ticket`. Otherwise it is `null`.

## Data Flow

1. Validate the question with the existing `AskRequest` model.
2. Call `query_service.answer_question(question, top_k)`.
3. Call `agent_service.decide_next_action(question, rag_answer, citations)`.
4. If the decision is `create_ticket`, build a `TicketCreate` from the decision and call `ticket_service.create_ticket`.
5. Return a combined response containing the original question, RAG answer, citations, decision, and optional ticket.

This keeps RAG, decisioning, and persistence as separate layers while still giving the UI one endpoint to call.

## Error Handling

- Validation errors remain FastAPI 422 responses.
- No relevant RAG answer does not raise an error; it can still flow into `clarify`.
- Unexpected service errors should use FastAPI defaults during Day 5. The route should only explicitly convert known persistence errors if they appear during ticket creation.

If ticket creation is triggered and the persistence layer raises `TicketNotFoundError` or a similar storage error, the route should surface a 500 or domain-appropriate HTTP error only if the failure is expected and mapped explicitly.

## Streamlit Changes

Replace the current two-section demo with an Agent-oriented interface that keeps the ingest area and adds an Agent question tab.

The new UI should:

- keep Markdown ingest
- keep basic RAG ask flow for direct knowledge-base testing
- add an Agent ask section
- show the Agent decision and optional ticket result

This preserves the existing demo while making the Agent workflow visible.

## Testing Strategy

Add:

- `tests/test_agent_api.py`

Tests should verify:

- request validation
- response serialization
- ticket creation when `create_ticket`
- no ticket when `answer` or `clarify`
- OpenAPI includes `/agent/ask`
- Streamlit calls the new API path

Existing ticket, agent decision, RAG, and health tests should continue to pass.
