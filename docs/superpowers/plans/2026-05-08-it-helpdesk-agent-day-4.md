# Enterprise IT Helpdesk Agent Day 4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the deterministic Agent decision layer that returns `answer`, `clarify`, or `create_ticket` after RAG answers an IT question.

**Architecture:** Add focused Agent schemas and a pure service function. The service reuses ticket category and priority enums, uses deterministic rules, and does not call external APIs or write tickets yet.

**Tech Stack:** Python, Pydantic, pytest.

---

## File Structure

- Create: `D:\program\agent\projects\it-helpdesk-agent\app\schemas\agent.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\services\agent_service.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\tests\test_agent_schema.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\tests\test_agent_service.py`

The project directory is not a git repository, so commit steps are intentionally omitted.

---

### Task 1: Agent Schema

**Files:**
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\schemas\agent.py`
- Test: `D:\program\agent\projects\it-helpdesk-agent\tests\test_agent_schema.py`

- [ ] **Step 1: Write failing schema tests**

Add tests for `AgentAction`, `AgentDecision`, enum validation, and default empty ticket fields.

- [ ] **Step 2: Run tests to verify they fail**

```powershell
python -m pytest tests/test_agent_schema.py -v
```

Expected: import failure for `app.schemas.agent`.

- [ ] **Step 3: Implement schema**

Create `AgentAction` and `AgentDecision`. Reuse `TicketCategory` and `TicketPriority`.

- [ ] **Step 4: Run schema tests**

```powershell
python -m pytest tests/test_agent_schema.py -v
```

Expected: pass.

---

### Task 2: Agent Service

**Files:**
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\services\agent_service.py`
- Test: `D:\program\agent\projects\it-helpdesk-agent\tests\test_agent_service.py`

- [ ] **Step 1: Write failing service tests**

Add tests for `answer`, `clarify`, `create_ticket`, category inference, priority inference, and populated messages.

- [ ] **Step 2: Run tests to verify they fail**

```powershell
python -m pytest tests/test_agent_service.py -v
```

Expected: import failure for `app.services.agent_service`.

- [ ] **Step 3: Implement deterministic service**

Create `decide_next_action(question, rag_answer, citations) -> AgentDecision`.

- [ ] **Step 4: Run service tests**

```powershell
python -m pytest tests/test_agent_service.py -v
```

Expected: pass.

---

### Task 3: Verification

- [ ] **Step 1: Run Day 4 tests**

```powershell
python -m pytest tests/test_agent_schema.py tests/test_agent_service.py -v
```

- [ ] **Step 2: Run existing ticket and API regression tests**

```powershell
python -m pytest tests/test_ticket_schema.py tests/test_ticket_store.py tests/test_ticket_service.py tests/test_ticket_api.py -v
```

- [ ] **Step 3: Run full test suite**

```powershell
python -m pytest tests -v
```

- [ ] **Step 4: Check Day 4 docs for placeholders**

```powershell
$patterns = @('TO' + 'DO', 'TB' + 'D', 'implement' + ' later')
Select-String -Path docs/superpowers/specs/2026-05-08-it-helpdesk-agent-day-4-agent-decision-design.md,docs/superpowers/plans/2026-05-08-it-helpdesk-agent-day-4.md -Pattern $patterns
```

Expected: no output.
