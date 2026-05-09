# Enterprise IT Helpdesk Agent Day 4 Agent Decision Design

## Purpose

Day 4 adds the Agent decision layer that decides what should happen after a user asks an IT question and the RAG layer returns an answer with citations.

The decision layer returns structured output with one of three actions:

- `answer`
- `clarify`
- `create_ticket`

Day 4 does not expose an Agent API route and does not automatically create tickets. Those integrations are Day 5 scope.

## Scope

Included:

- Agent Pydantic schemas.
- A deterministic `agent_service.py`.
- Rule-based category detection.
- Rule-based priority detection.
- Rule-based action selection.
- Unit tests for answer, clarify, create-ticket, category, priority, and message fields.

Excluded:

- `POST /agent/ask`.
- Calling an LLM for classification.
- Writing tickets to SQLite from the Agent flow.
- Streamlit Agent UI changes.

## Input Contract

The service function accepts:

- `question: str`
- `rag_answer: str`
- `citations: list[Citation]`

`Citation` is reused from `app.schemas.rag`.

## Output Contract

The service returns `AgentDecision`:

```json
{
  "action": "answer | clarify | create_ticket",
  "category": "account | network | software | hardware | permission | other",
  "priority": "low | medium | high",
  "summary": "Short internal issue summary",
  "user_message": "Message shown to the employee",
  "ticket_title": "Ticket title when action is create_ticket",
  "suggested_resolution": "Suggested IT handling steps"
}
```

Categories and priorities reuse the Day 2 ticket enums so later ticket creation can pass values directly into `TicketCreate`.

## Decision Rules

`create_ticket` wins over other actions when the question contains signals that usually require IT staff intervention:

- account locked
- password or MFA device cannot be recovered by self-service
- permission or GitLab access requests
- hardware damage or replacement
- repeated login failure
- data loss
- production, finance, customer, or business-critical system access blocked

`clarify` is returned when the question lacks enough operational detail. Examples:

- very short generic question
- no affected system
- no error message
- no expected behavior
- no citations and a RAG fallback answer

`answer` is returned when there are citations and the RAG answer contains usable guidance, and no create-ticket rule is triggered.

## Category Rules

Category is inferred from keywords:

- account: account, password, login, MFA, locked
- network: VPN, Wi-Fi, network, DNS, intranet
- software: install, license, software, Teams, Microsoft 365
- hardware: printer, laptop, device, hardware, broken
- permission: permission, access, GitLab, repository, project
- other: fallback

## Priority Rules

Priority is `high` when the question mentions:

- production system
- finance system
- customer system
- business-critical outage
- data loss
- security-sensitive access issue

Priority is `medium` for create-ticket issues that do not match high-priority signals.

Priority is `low` for normal answer or clarify decisions.

## Testing Strategy

Add:

- `tests/test_agent_schema.py`
- `tests/test_agent_service.py`

Schema tests verify enum validation and default optional fields.

Service tests verify:

- actionable cited RAG answer returns `answer`
- vague question returns `clarify`
- account locked returns `create_ticket`
- permission request returns `create_ticket`
- critical production issue is high priority
- category detection maps common IT language correctly
- generated user message, ticket title, and suggested resolution are populated

Full suite verification should pass because Day 4 does not modify existing API behavior.
