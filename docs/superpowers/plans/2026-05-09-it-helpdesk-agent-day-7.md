# Enterprise IT Helpdesk Agent Day 7 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close out the MVP with regression verification, small fixes if needed, and clear run/demo documentation.

**Architecture:** Keep the working backend and Streamlit app unchanged unless verification exposes a concrete issue. Treat this as a release polish day, not a feature day.

**Tech Stack:** Python, Streamlit, FastAPI, pytest, Markdown.

---

## File Structure

- Modify: `D:\program\agent\projects\it-helpdesk-agent\README.md`
- Create: `D:\program\agent\projects\it-helpdesk-agent\docs\superpowers\specs\2026-05-09-it-helpdesk-agent-day-7-release-polish-design.md`

---

### Task 1: Release Verification

- [ ] **Step 1: Run the full test suite**

```powershell
python -m pytest
```

- [ ] **Step 2: Re-run the Streamlit syntax check**

```powershell
python -m py_compile streamlit_app.py
```

- [ ] **Step 3: Inspect the current run instructions**

Confirm the README still points to the correct FastAPI and Streamlit entry points.

---

### Task 2: Documentation Polish

- [ ] **Step 1: Add a concise demo flow to the README**

Document the normal sequence for starting the backend, starting Streamlit, and exercising the five tabs.

- [ ] **Step 2: Clarify the web preview address**

Make the Streamlit URL explicit so the demo can be opened without guesswork.

---

### Task 3: Final Verification

- [ ] **Step 1: Re-run the full test suite**

```powershell
python -m pytest
```

- [ ] **Step 2: Confirm the repo has no remaining placeholder notes in the day 7 docs**

Verify the new day 7 spec and plan are complete and self-contained.
