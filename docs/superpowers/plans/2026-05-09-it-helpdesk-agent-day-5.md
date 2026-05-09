# Enterprise IT Helpdesk Agent Day 5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose the Agent workflow through `/agent/ask` and update the Streamlit demo to use it.

**Architecture:** Add a dedicated Agent API route that composes the existing RAG, decision, and ticket layers. Keep the Streamlit UI thin and make it call the API instead of duplicating decision logic in the browser.

**Tech Stack:** Python, FastAPI, Pydantic, Streamlit, requests, pytest.

---

## File Structure

- Create: `D:\program\agent\projects\it-helpdesk-agent\app\schemas\agent_api.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\api\routes\agent.py`
- Modify: `D:\program\agent\projects\it-helpdesk-agent\app\main.py`
- Modify: `D:\program\agent\projects\it-helpdesk-agent\streamlit_app.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\tests\test_agent_api.py`

The project directory is not a git repository, so commit steps are intentionally omitted.

---

### Task 1: Agent API Schemas

**Files:**
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\schemas\agent_api.py`
- Test: `D:\program\agent\projects\it-helpdesk-agent\tests\test_agent_api.py`

- [ ] **Step 1: Write failing API schema tests**

Add tests for request validation and combined response shape.

- [ ] **Step 2: Run tests to verify they fail**

```powershell
python -m pytest tests/test_agent_api.py -v
```

Expected: import failure for `app.schemas.agent_api`.

- [ ] **Step 3: Implement API schemas**

Create `AgentAskRequest` and `AgentAskResponse`.

- [ ] **Step 4: Run schema tests**

```powershell
python -m pytest tests/test_agent_api.py -v
```

Expected: route-level failures until the API route exists.

---

### Task 2: Agent Route

**Files:**
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\api\routes\agent.py`
- Modify: `D:\program\agent\projects\it-helpdesk-agent\app\main.py`

- [ ] **Step 1: Implement `/agent/ask`**

Compose:

- `query_service.answer_question`
- `agent_service.decide_next_action`
- `ticket_service.create_ticket`

Return the combined `AgentAskResponse`.

- [ ] **Step 2: Register the router**

Import and include the new router in `app/main.py`.

- [ ] **Step 3: Run Agent API tests**

```powershell
python -m pytest tests/test_agent_api.py -v
```

Expected: route tests pass.

---

### Task 3: Streamlit Agent UI

**Files:**
- Modify: `D:\program\agent\projects\it-helpdesk-agent\streamlit_app.py`

- [ ] **Step 1: Add an Agent section**

Keep ingest and direct RAG ask flows, and add an Agent ask form that calls `/agent/ask`.

- [ ] **Step 2: Show decision and ticket output**

Render answer, clarify prompt, or created ticket details based on the response.

- [ ] **Step 3: Verify the script still parses**

Run:

```powershell
python -m py_compile streamlit_app.py
```

Expected: no syntax errors.

---

### Task 4: Full Verification

- [ ] **Step 1: Run Agent API tests**

```powershell
python -m pytest tests/test_agent_api.py -v
```

- [ ] **Step 2: Run regression tests**

```powershell
python -m pytest tests/test_agent_schema.py tests/test_agent_service.py tests/test_ticket_api.py tests/test_ticket_store.py tests/test_ticket_service.py -v
```

- [ ] **Step 3: Run full test suite**

```powershell
python -m pytest tests -v
```

- [ ] **Step 4: Check docs for placeholders**

```powershell
$patterns = @('TO' + 'DO', 'TB' + 'D', 'implement' + ' later')
Select-String -Path docs/superpowers/specs/2026-05-09-it-helpdesk-agent-day-5-agent-api-design.md,docs/superpowers/plans/2026-05-09-it-helpdesk-agent-day-5.md -Pattern $patterns
```

Expected: no output.
