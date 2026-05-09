# Enterprise IT Helpdesk Agent

Enterprise IT Helpdesk Agent is a local IT service desk Agent MVP.

It combines FastAPI, Streamlit, RAG, SQLite, and a rule-based Agent decision layer to support knowledge-base Q&A, Agent decisions, automatic ticket creation, ticket management, and dashboard metrics.

## Features

- Upload Markdown knowledge-base documents
- Ask RAG questions with citations
- Ask the Agent to decide the next action:
  - `answer`: answer directly from the knowledge base
  - `clarify`: ask for missing details
  - `create_ticket`: create an IT support ticket
- Browse, filter, inspect, and update tickets
- View ticket dashboard metrics
- Store tickets locally in SQLite

## Project Structure

```text
app/
  api/routes/        FastAPI routes
  core/              configuration and logging
  rag/               document loading, splitting, retrieval, vector store
  schemas/           Pydantic schemas
  services/          RAG, Agent, and Ticket business logic
  storage/           SQLite ticket storage
  ui/                Streamlit API client helpers

sample_docs/         sample IT knowledge-base documents
tests/               automated tests
streamlit_app.py     Streamlit frontend
```

## Setup

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set your model configuration:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
CHAT_MODEL=gpt-5.4
```

The default embedding provider is local:

```env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

## Run Backend

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
python -m uvicorn app.main:app --reload
```

Open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## Run Frontend

Open a second terminal:

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
streamlit run streamlit_app.py --server.headless true
```

Open:

```text
http://localhost:8501
```

## Demo Flow

1. Open the `Ingest` tab and upload `sample_docs/vpn-troubleshooting.md`.
2. Open the `RAG` tab and ask:

```text
List the Windows and macOS commands for flushing DNS cache.
```

3. Open the `Agent` tab and ask:

```text
My VPN authentication keeps failing, my account may be locked, and I have retried multiple times. Please create a support ticket.
```

4. Open the `Tickets` tab and inspect the ticket created by the Agent.
5. Update the ticket status, priority, and resolution note.
6. Open the `Dashboard` tab and review ticket metrics.

## Sample Knowledge Base

The `sample_docs/` directory includes five sample IT documents:

- `vpn-troubleshooting.md`
- `email-account-and-password.md`
- `gitlab-permission-request.md`
- `printer-connection-faq.md`
- `office-software-installation.md`

## Run Tests

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
python -m pytest
```

The tests cover:

- health API
- RAG ingest and ask flows
- Agent schemas, service logic, and API
- Ticket schemas, store, service, and API
- Streamlit API client helpers

## Local Runtime Data

The following files and directories are runtime data and should not be committed:

- `.env`
- `data/chroma/`
- `data/uploads/`
- `data/tickets.db`
- `logs/`
- `__pycache__/`
- `.pytest_cache/`

They are already listed in `.gitignore`.

## Security Note

This project is a local MVP. It does not include authentication, authorization, multi-user isolation, or production hardening. Do not expose it directly to the public internet.
