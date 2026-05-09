# Enterprise IT Helpdesk Agent Day 3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose the Day 2 ticket core through FastAPI ticket management endpoints.

**Architecture:** Add a dedicated `tickets` router that delegates to `ticket_service`. Keep SQLite inside the service/store layer and map `TicketNotFoundError` to HTTP 404 at the API boundary.

**Tech Stack:** Python, FastAPI, Pydantic, pytest, FastAPI TestClient.

---

## File Structure

- Create: `D:\program\agent\projects\it-helpdesk-agent\app\api\routes\tickets.py`
- Modify: `D:\program\agent\projects\it-helpdesk-agent\app\main.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\tests\test_ticket_api.py`

The project directory is not a git repository, so commit steps are intentionally omitted.

---

### Task 1: Ticket API Tests

**Files:**
- Create: `D:\program\agent\projects\it-helpdesk-agent\tests\test_ticket_api.py`

- [ ] **Step 1: Write failing route tests**

Add tests for create, list, invalid filters, get, missing get, patch, missing patch, stats, and OpenAPI route registration.

- [ ] **Step 2: Run tests to verify they fail**

```powershell
python -m pytest tests/test_ticket_api.py -v
```

Expected: collection or request failures because `app.api.routes.tickets` is not implemented and the router is not registered.

---

### Task 2: Ticket Router

**Files:**
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\api\routes\tickets.py`

- [ ] **Step 1: Implement `tickets.py`**

Create an `APIRouter(prefix="/tickets", tags=["tickets"])` and add:

- `POST /`
- `GET /`
- `GET /stats`
- `GET /{ticket_id}`
- `PATCH /{ticket_id}`

Use service functions and convert `TicketNotFoundError` to `HTTPException(status_code=404, detail="Ticket not found.")`.

- [ ] **Step 2: Run ticket API tests**

```powershell
python -m pytest tests/test_ticket_api.py -v
```

Expected: route tests still fail until the router is included in `app.main`.

---

### Task 3: Register Router

**Files:**
- Modify: `D:\program\agent\projects\it-helpdesk-agent\app\main.py`

- [ ] **Step 1: Include the tickets router**

Import `tickets_router` and call `app.include_router(tickets_router)`.

- [ ] **Step 2: Run ticket API tests**

```powershell
python -m pytest tests/test_ticket_api.py -v
```

Expected: all ticket API tests pass.

---

### Task 4: Full Verification

- [ ] **Step 1: Run Day 3 tests**

```powershell
python -m pytest tests/test_ticket_api.py -v
```

- [ ] **Step 2: Run ticket core regression tests**

```powershell
python -m pytest tests/test_ticket_schema.py tests/test_ticket_store.py tests/test_ticket_service.py -v
```

- [ ] **Step 3: Run full test suite**

```powershell
python -m pytest tests -v
```

- [ ] **Step 4: Check spec and plan have no placeholders**

```powershell
$patterns = @('TO' + 'DO', 'TB' + 'D', 'implement' + ' later')
Select-String -Path docs/superpowers/specs/2026-05-08-it-helpdesk-agent-day-3-ticket-api-design.md,docs/superpowers/plans/2026-05-08-it-helpdesk-agent-day-3.md -Pattern $patterns
```

Expected: no output.
