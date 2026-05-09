# Enterprise IT Helpdesk Agent Day 1 Bootstrap Design

## Purpose

Day 1 creates `it-helpdesk-agent` as a standalone project derived from the existing `rag-assistant` baseline. The goal is to preserve the working FastAPI, RAG, Streamlit, and pytest foundation while changing the project identity to an enterprise IT helpdesk assistant.

Day 1 intentionally does not add ticket storage, ticket APIs, Agent decision logic, authentication, dashboard views, or new workflows. It prepares a clean base for those later days.

## Scope

Included:

- Create `D:\program\agent\projects\it-helpdesk-agent` from `D:\program\agent\projects\rag-assistant`.
- Remove copied runtime and repository metadata from the new project.
- Rename the app identity to `Enterprise IT Helpdesk Agent`.
- Point default runtime directories at the new project.
- Keep the existing RAG ingestion and question-answering behavior.
- Keep the existing Streamlit demo entry point.
- Add IT helpdesk sample documents for manual ingestion demos.
- Verify the copied baseline still runs and passes tests.

Excluded:

- Ticket schema, store, service, or APIs.
- Agent classification or automatic ticket creation.
- Streamlit ticket management UI.
- Dashboard charts.
- Authentication or role-based access control.
- Any changes under `D:\program\agent\projects\rag-assistant`.

## Project Identity

The copied project should present itself as:

```text
Enterprise IT Helpdesk Agent
```

The FastAPI app title comes from `settings.app_name`, so the value must be set in `app/core/config.py` and mirrored in `.env.example` through `APP_NAME`.

The project should use its own storage defaults instead of reusing paths from `rag-assistant`:

- uploads: `data/uploads`
- vector store: `data/chroma`
- Chroma collection: `it_helpdesk_knowledge`
- logs: `logs/app.log`

Day 2 later adds ticket database configuration.

## Baseline Behavior

The baseline keeps the existing RAG application behavior:

- `POST /rag/ingest` uploads and ingests Markdown documents.
- `POST /rag/ask` retrieves relevant chunks and generates a grounded answer with citations.
- `GET /health` returns the health check response.
- `streamlit_app.py` remains the local demo UI.

Day 1 should not change the public RAG contract. Existing tests should continue to pass after the copy and rename.

## Sample Documents

Day 1 adds five Markdown documents under `sample_docs/`:

- `vpn-troubleshooting.md`
- `email-account-and-password.md`
- `gitlab-permission-request.md`
- `printer-connection-faq.md`
- `office-software-installation.md`

These files are demo knowledge-base inputs. They are not automatically ingested. The user can upload them through the existing RAG ingestion flow to demonstrate IT helpdesk answers.

The documents should cover common IT categories that later map naturally to ticket categories:

- network and VPN
- account and password
- permissions
- hardware and printer support
- software installation

## Cleanup Rules

The new project must not keep copied repository metadata or runtime caches from the source project.

Remove from `it-helpdesk-agent` when present:

- `.git`
- `.pytest_cache`
- `.tmp`
- `__pycache__`
- `*.pyc`
- copied logs

The source project `rag-assistant` must not be modified as part of Day 1.

## Documentation

The Day 1 README should describe:

- the project identity
- how to install dependencies
- how to create `.env`
- how to run FastAPI
- how to run Streamlit
- where sample documents live
- how to run tests

The README should not describe Day 2+ features as already available. Future ticket, Agent, and dashboard work can be listed as later scope only.

## Verification

Day 1 is complete when:

- `D:\program\agent\projects\it-helpdesk-agent` exists.
- `app/core/config.py` uses `Enterprise IT Helpdesk Agent`.
- `.env.example` contains the new app name and IT Chroma collection.
- `sample_docs/` contains the five IT Markdown files.
- FastAPI imports with the expected title.
- Baseline tests pass.
- `rag-assistant` remains clean.

Recommended verification commands:

```powershell
python -m pytest tests -v
python -c "from app.main import app; print(app.title)"
git -C D:\program\agent\projects\rag-assistant status --short
```

Expected app title:

```text
Enterprise IT Helpdesk Agent
```
