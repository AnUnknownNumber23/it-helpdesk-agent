# Enterprise IT Helpdesk Agent Day 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the ticket domain model, SQLite ticket store, and ticket service used by later API and Agent work.

**Architecture:** Day 2 introduces a small ticket module without exposing HTTP endpoints yet. Pydantic schemas define the contract, `TicketStore` owns SQLite persistence, and `ticket_service.py` provides the application-facing functions that later routes and agent decisions will call.

**Tech Stack:** Python, Pydantic, SQLite standard library, pytest.

---

## File Structure

- Modify: `D:\program\agent\projects\it-helpdesk-agent\app\core\config.py`
- Modify: `D:\program\agent\projects\it-helpdesk-agent\.env.example`
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\schemas\ticket.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\storage\__init__.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\storage\ticket_store.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\services\ticket_service.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\tests\test_ticket_schema.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\tests\test_ticket_store.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\tests\test_ticket_service.py`

The project directory is not a git repository, so commit steps are intentionally omitted.

---

### Task 1: Ticket Schema

**Files:**
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\schemas\ticket.py`
- Test: `D:\program\agent\projects\it-helpdesk-agent\tests\test_ticket_schema.py`

- [ ] **Step 1: Write failing schema tests**

Define tests for enum validation, create payload defaults, update payload optionality, and stored ticket timestamps.

- [ ] **Step 2: Verify tests fail**

Run:

```powershell
python -m pytest tests/test_ticket_schema.py -v
```

Expected: import failure for `app.schemas.ticket`.

- [ ] **Step 3: Implement ticket schemas**

Add `TicketCategory`, `TicketPriority`, `TicketStatus`, `TicketCreate`, `TicketUpdate`, `Ticket`, and `TicketStats`.

- [ ] **Step 4: Verify tests pass**

Run:

```powershell
python -m pytest tests/test_ticket_schema.py -v
```

Expected: pass.

---

### Task 2: Ticket Store

**Files:**
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\storage\__init__.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\storage\ticket_store.py`
- Test: `D:\program\agent\projects\it-helpdesk-agent\tests\test_ticket_store.py`

- [ ] **Step 1: Write failing store tests**

Define tests for table initialization, ticket id generation, create/get/list/update, filtering, validation of missing records, and stats.

- [ ] **Step 2: Verify tests fail**

Run:

```powershell
python -m pytest tests/test_ticket_store.py -v
```

Expected: import failure for `app.storage.ticket_store`.

- [ ] **Step 3: Implement SQLite store**

Use `sqlite3`, `row_factory`, ISO datetime strings, and the ticket schemas for all public return values.

- [ ] **Step 4: Verify tests pass**

Run:

```powershell
python -m pytest tests/test_ticket_store.py -v
```

Expected: pass.

---

### Task 3: Ticket Service And Config

**Files:**
- Modify: `D:\program\agent\projects\it-helpdesk-agent\app\core\config.py`
- Modify: `D:\program\agent\projects\it-helpdesk-agent\.env.example`
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\services\ticket_service.py`
- Test: `D:\program\agent\projects\it-helpdesk-agent\tests\test_config.py`
- Test: `D:\program\agent\projects\it-helpdesk-agent\tests\test_ticket_service.py`

- [ ] **Step 1: Write failing config and service tests**

Define tests for `ticket_db_path` default and service methods delegating to a store.

- [ ] **Step 2: Verify tests fail**

Run:

```powershell
python -m pytest tests/test_config.py tests/test_ticket_service.py -v
```

Expected: config assertion failure and import failure for `app.services.ticket_service`.

- [ ] **Step 3: Implement config and service wrapper**

Add `ticket_db_path` to settings and `.env.example`. Add default store factory plus create/get/list/update/stats functions.

- [ ] **Step 4: Verify tests pass**

Run:

```powershell
python -m pytest tests/test_config.py tests/test_ticket_service.py -v
```

Expected: pass.

---

### Task 4: Full Verification

- [ ] **Step 1: Run ticket-focused tests**

```powershell
python -m pytest tests/test_ticket_schema.py tests/test_ticket_store.py tests/test_ticket_service.py -v
```

- [ ] **Step 2: Run baseline safe tests**

```powershell
python -m pytest tests/test_config.py tests/test_health_api.py tests/test_logging.py -v
```

- [ ] **Step 3: Run full test suite if dependencies are available**

```powershell
python -m pytest tests -v
```

- [ ] **Step 4: Record results**

Summarize created files, passing commands, and any skipped verification in the final response.
