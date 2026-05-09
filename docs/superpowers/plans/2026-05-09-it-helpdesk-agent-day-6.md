# Enterprise IT Helpdesk Agent Day 6 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the Streamlit demo into an operational console with ticket browsing, ticket editing, and dashboard metrics.

**Architecture:** Keep Streamlit as the thin presentation layer and move HTTP helper logic into a small reusable module. The page will continue to call the existing backend APIs and only format their results for display.

**Tech Stack:** Python, Streamlit, requests, pytest.

---

## File Structure

- Create: `D:\program\agent\projects\it-helpdesk-agent\app\ui\__init__.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\ui\streamlit_client.py`
- Modify: `D:\program\agent\projects\it-helpdesk-agent\streamlit_app.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\tests\test_streamlit_client.py`

The project directory is not a git repository, so commit steps are intentionally omitted.

---

### Task 1: Streamlit Client Helpers

**Files:**
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\ui\__init__.py`
- Create: `D:\program\agent\projects\it-helpdesk-agent\app\ui\streamlit_client.py`
- Test: `D:\program\agent\projects\it-helpdesk-agent\tests\test_streamlit_client.py`

- [ ] **Step 1: Write failing helper tests**

Add tests for response parsing and each backend call helper.

- [ ] **Step 2: Run tests to verify they fail**

```powershell
python -m pytest tests/test_streamlit_client.py -v
```

Expected: import failure for `app.ui.streamlit_client`.

- [ ] **Step 3: Implement helper functions**

Add helper functions for ingest, RAG ask, agent ask, ticket listing, ticket detail, ticket update, and stats.

- [ ] **Step 4: Run helper tests**

```powershell
python -m pytest tests/test_streamlit_client.py -v
```

Expected: pass.

---

### Task 2: Streamlit Layout

**Files:**
- Modify: `D:\program\agent\projects\it-helpdesk-agent\streamlit_app.py`

- [ ] **Step 1: Add Tickets and Dashboard tabs**

Keep the existing ingest, RAG, and Agent tabs. Add ticket browsing/editing and dashboard summaries using the helper module.

- [ ] **Step 2: Use backend helpers for ticket operations**

Call the helper functions instead of inlining new `requests` calls for the tickets/dashboard flow.

- [ ] **Step 3: Verify the script parses**

```powershell
python -m py_compile streamlit_app.py
```

Expected: no syntax errors.

---

### Task 3: Verification

- [ ] **Step 1: Run helper tests**

```powershell
python -m pytest tests/test_streamlit_client.py -v
```

- [ ] **Step 2: Run existing backend regression tests**

```powershell
python -m pytest tests/test_agent_api.py tests/test_ticket_api.py tests/test_agent_service.py tests/test_ticket_service.py tests/test_ticket_store.py -v
```

- [ ] **Step 3: Run full test suite**

```powershell
python -m pytest tests -v
```

- [ ] **Step 4: Check Day 6 docs for placeholders**

```powershell
$patterns = @('TO' + 'DO', 'TB' + 'D', 'implement' + ' later')
Select-String -Path docs/superpowers/specs/2026-05-09-it-helpdesk-agent-day-6-streamlit-tickets-dashboard-design.md,docs/superpowers/plans/2026-05-09-it-helpdesk-agent-day-6.md -Pattern $patterns
```

Expected: no output.
