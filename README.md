# Enterprise IT Helpdesk Agent

企业 IT Helpdesk Agent 是 Day 1 阶段的新项目骨架，用于把现有 RAG 能力迁移为企业 IT 知识库问答助手。

## 当前阶段

- 项目目录：`D:\program\agent\projects\it-helpdesk-agent`
- 初始代码从 `D:\program\agent\projects\rag-assistant` 复制而来
- Day 1 目标：完成项目身份、默认配置、启动路径和基础验证命令更新

## 环境准备

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

默认使用本地 embedding：

```env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

如需调用 OpenAI 兼容接口，请在 `.env` 中填写：

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
CHAT_MODEL=gpt-5.4
```

## 启动后端

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
python -m uvicorn app.main:app --reload
```

访问：

- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## 启动 Streamlit

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
streamlit run streamlit_app.py --server.headless true
```

访问：

```text
http://localhost:8501
```

## sample_docs

Day 1 已加入 `sample_docs` 目录，可用于手动上传验证 IT 知识库 RAG 问答：

- `vpn-troubleshooting.md`
- `email-account-and-password.md`
- `gitlab-permission-request.md`
- `printer-connection-faq.md`
- `office-software-installation.md`

## 运行测试

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
python -m pytest
```

## Demo flow

1. Start the backend:

```powershell
python -m uvicorn app.main:app --reload
```

2. Start the Streamlit app:

```powershell
streamlit run streamlit_app.py --server.headless true
```

3. Open the Streamlit app:

```text
http://localhost:8501
```

4. Walk through the tabs:

- Ingest a Markdown file.
- Ask a RAG question.
- Ask the Agent a support question.
- Review and update tickets.
- Check the dashboard metrics.
