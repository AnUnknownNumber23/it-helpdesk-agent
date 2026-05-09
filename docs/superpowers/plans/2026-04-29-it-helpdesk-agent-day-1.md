# Enterprise IT Helpdesk Agent Day 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the standalone `projects/it-helpdesk-agent` project from `projects/rag-assistant`, update the project identity, add demo IT knowledge documents, and verify the copied baseline still works.

**Architecture:** Day 1 does not add new Agent or ticket behavior. It creates a clean independent project directory that preserves the existing FastAPI + RAG + Streamlit baseline and prepares sample IT documents for later ingestion.

**Tech Stack:** Python, FastAPI, Streamlit, pytest, Chroma, Markdown sample documents, PowerShell.

---

## File Structure

Create or modify these paths:

- Create directory: `D:\program\agent\projects\it-helpdesk-agent`
- Modify: `D:\program\agent\projects\it-helpdesk-agent\README.md`
- Modify: `D:\program\agent\projects\it-helpdesk-agent\app\core\config.py`
- Modify: `D:\program\agent\projects\it-helpdesk-agent\.env.example`
- Create: `D:\program\agent\projects\it-helpdesk-agent\sample_docs\vpn-troubleshooting.md`
- Create: `D:\program\agent\projects\it-helpdesk-agent\sample_docs\email-account-and-password.md`
- Create: `D:\program\agent\projects\it-helpdesk-agent\sample_docs\gitlab-permission-request.md`
- Create: `D:\program\agent\projects\it-helpdesk-agent\sample_docs\printer-connection-faq.md`
- Create: `D:\program\agent\projects\it-helpdesk-agent\sample_docs\office-software-installation.md`

Do not modify files under `D:\program\agent\projects\rag-assistant`.

---

### Task 1: Create Clean Project Copy

**Files:**
- Create: `D:\program\agent\projects\it-helpdesk-agent`
- Source: `D:\program\agent\projects\rag-assistant`

- [ ] **Step 1: Verify source project exists and destination does not exist**

Run:

```powershell
Test-Path D:\program\agent\projects\rag-assistant
Test-Path D:\program\agent\projects\it-helpdesk-agent
```

Expected:

```text
True
False
```

- [ ] **Step 2: Copy the source project**

Run:

```powershell
Copy-Item -Recurse -Force D:\program\agent\projects\rag-assistant D:\program\agent\projects\it-helpdesk-agent
```

Expected: command exits without error.

- [ ] **Step 3: Remove copied runtime/cache directories from the new project**

Run:

```powershell
$paths = @(
  'D:\program\agent\projects\it-helpdesk-agent\.git',
  'D:\program\agent\projects\it-helpdesk-agent\.pytest_cache',
  'D:\program\agent\projects\it-helpdesk-agent\.tmp',
  'D:\program\agent\projects\it-helpdesk-agent\__pycache__',
  'D:\program\agent\projects\it-helpdesk-agent\logs'
)
foreach ($path in $paths) {
  if (Test-Path $path) {
    Remove-Item -Recurse -Force -LiteralPath $path
  }
}
Get-ChildItem -Recurse -Directory D:\program\agent\projects\it-helpdesk-agent -Filter __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -File D:\program\agent\projects\it-helpdesk-agent -Include *.pyc | Remove-Item -Force
```

Expected: command exits without error.

- [ ] **Step 4: Confirm the new project has no copied git metadata**

Run:

```powershell
Test-Path D:\program\agent\projects\it-helpdesk-agent\.git
```

Expected:

```text
False
```

---

### Task 2: Update Project Identity

**Files:**
- Modify: `D:\program\agent\projects\it-helpdesk-agent\README.md`
- Modify: `D:\program\agent\projects\it-helpdesk-agent\app\core\config.py`
- Modify: `D:\program\agent\projects\it-helpdesk-agent\.env.example`

- [ ] **Step 1: Inspect the current copied config**

Run:

```powershell
Get-Content -Raw D:\program\agent\projects\it-helpdesk-agent\app\core\config.py
Get-Content -Raw D:\program\agent\projects\it-helpdesk-agent\.env.example
```

Expected: output shows the existing RAG assistant app name and default directories.

- [ ] **Step 2: Update `config.py` app identity and storage defaults**

Replace `D:\program\agent\projects\it-helpdesk-agent\app\core\config.py` with:

```python
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Enterprise IT Helpdesk Agent"
    upload_dir: str = str(BASE_DIR / "data" / "uploads")
    chroma_dir: str = str(BASE_DIR / "data" / "chroma")
    chroma_collection: str = "it_helpdesk_knowledge"

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    chat_model: str = "gpt-5.4"
    embeddings_model: str = "text-embedding-3-small"
    embedding_provider: str = "local"
    local_embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
```

- [ ] **Step 3: Update `.env.example` for the new project**

Replace `D:\program\agent\projects\it-helpdesk-agent\.env.example` with:

```env
APP_NAME=Enterprise IT Helpdesk Agent
UPLOAD_DIR=data/uploads
CHROMA_DIR=data/chroma
CHROMA_COLLECTION=it_helpdesk_knowledge

OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
CHAT_MODEL=gpt-5.4

EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDINGS_MODEL=text-embedding-3-small
```

- [ ] **Step 4: Replace `README.md` with a Day 1 project README**

Replace `D:\program\agent\projects\it-helpdesk-agent\README.md` with:

```markdown
# Enterprise IT Helpdesk Agent

企业内部 IT 服务台 Agent。员工可以咨询账号、网络、权限、软件、硬件等 IT 问题；系统先基于知识库回答，并在后续版本中支持自动创建 IT 工单。

## 当前阶段

Day 1 基线版本包含：

- 从 `rag-assistant` 复制出的独立项目目录
- FastAPI 后端
- Streamlit 演示页面
- Markdown 文档上传和入库
- RAG 问答和 citations
- IT 场景示例知识库文档

后续阶段会继续加入：

- Agent 决策：`answer` / `clarify` / `create_ticket`
- SQLite 工单存储
- 工单 API
- 工单后台和 Dashboard

## 项目目录

```powershell
D:\program\agent\projects\it-helpdesk-agent
```

## 安装依赖

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
python -m pip install -r requirements.txt
```

## 配置 `.env`

```powershell
Copy-Item .env.example .env
```

最小配置：

```env
OPENAI_API_KEY=你的真实 key
OPENAI_BASE_URL=https://你的兼容接口/v1
```

默认 embedding 使用本地模型：

```env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

如果本地 HuggingFace 下载不稳定，可以改成 API embedding：

```env
EMBEDDING_PROVIDER=openai
EMBEDDINGS_MODEL=text-embedding-3-small
```

## 启动后端

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
python -m uvicorn app.main:app --reload
```

访问：

- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## 启动 Streamlit Demo

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
streamlit run streamlit_app.py --server.headless true
```

然后打开：

```text
http://localhost:8501
```

## 示例知识库

示例 IT 文档放在：

```text
sample_docs/
```

建议先上传这些文档进行演示：

- `vpn-troubleshooting.md`
- `email-account-and-password.md`
- `gitlab-permission-request.md`
- `printer-connection-faq.md`
- `office-software-installation.md`

## 运行测试

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
python -m pytest tests -v
```
```

- [ ] **Step 5: Verify the old project path is not mentioned in the new README**

Run:

```powershell
Select-String -Path D:\program\agent\projects\it-helpdesk-agent\README.md -Pattern 'rag-assistant'
```

Expected: only mentions `rag-assistant` as the copied source in the "当前阶段" section.

---

### Task 3: Add Demo IT Knowledge Documents

**Files:**
- Create: `D:\program\agent\projects\it-helpdesk-agent\sample_docs\vpn-troubleshooting.md`
- Create: `D:\program\agent\projects\it-helpdesk-agent\sample_docs\email-account-and-password.md`
- Create: `D:\program\agent\projects\it-helpdesk-agent\sample_docs\gitlab-permission-request.md`
- Create: `D:\program\agent\projects\it-helpdesk-agent\sample_docs\printer-connection-faq.md`
- Create: `D:\program\agent\projects\it-helpdesk-agent\sample_docs\office-software-installation.md`

- [ ] **Step 1: Create the sample docs directory**

Run:

```powershell
New-Item -ItemType Directory -Force D:\program\agent\projects\it-helpdesk-agent\sample_docs
```

Expected: directory exists.

- [ ] **Step 2: Create VPN troubleshooting document**

Create `sample_docs\vpn-troubleshooting.md` with:

```markdown
# VPN 故障排查指南

## 适用范围

本文适用于员工无法连接公司 VPN、VPN 频繁断开、VPN 登录后无法访问内网系统等问题。

## 常见现象

- VPN 客户端提示认证失败。
- VPN 一直停留在连接中。
- VPN 连接成功后无法访问内网 OA、GitLab 或文件服务器。
- VPN 连接几分钟后自动断开。

## 处理步骤

1. 确认本地网络可以正常访问公网。
2. 检查 VPN 客户端版本是否为公司发布的最新版本。
3. 重新输入公司账号和密码，避免浏览器或客户端保存了旧密码。
4. 如果账号连续输错密码超过 5 次，账号可能被锁定，需要提交 IT 工单解锁。
5. 切换网络后重试，例如从 Wi-Fi 切换到手机热点。
6. 连接成功但无法访问内网系统时，执行 `ipconfig /flushdns` 后重新连接 VPN。
7. 如果问题仍然存在，请提供错误截图、客户端版本、当前网络环境和发生时间。

## 需要创建工单的情况

- 账号被锁定。
- VPN 客户端无法安装。
- 同一账号在多台设备上都无法连接。
- 涉及生产系统、财务系统或客户系统访问阻塞。
```

- [ ] **Step 3: Create email account and password document**

Create `sample_docs\email-account-and-password.md` with:

```markdown
# 邮箱账号开通和密码重置流程

## 新员工邮箱开通

新员工邮箱由 HR 入职流程触发。IT 会在员工入职日前 1 个工作日完成邮箱创建。

开通后，员工会收到临时密码。首次登录必须修改密码并绑定多因素认证。

## 忘记邮箱密码

1. 打开公司统一身份认证页面。
2. 点击“忘记密码”。
3. 使用绑定手机号或 MFA 应用完成身份验证。
4. 设置新密码。
5. 等待 5 分钟后重新登录邮箱客户端。

## 密码规则

- 长度至少 12 位。
- 必须包含大写字母、小写字母、数字和特殊字符。
- 不能使用最近 5 次使用过的密码。
- 密码有效期为 180 天。

## 需要创建工单的情况

- 手机号已更换，无法完成身份验证。
- MFA 设备丢失。
- 账号被锁定。
- 新员工入职当天仍未收到邮箱账号。
```

- [ ] **Step 4: Create GitLab permission request document**

Create `sample_docs\gitlab-permission-request.md` with:

```markdown
# GitLab 权限申请流程

## 适用范围

员工需要访问 GitLab 项目、创建代码仓库、加入项目组或提升项目权限时，使用本文流程。

## 权限级别

- Guest：只能查看基础信息。
- Reporter：可以查看代码和流水线结果。
- Developer：可以提交代码和创建分支。
- Maintainer：可以管理成员、保护分支和发布版本。

## 申请流程

1. 确认需要访问的 GitLab 项目名称或项目 URL。
2. 与直属主管确认访问目的。
3. 让项目 Owner 在 GitLab 中添加成员。
4. 如果项目 Owner 不明确，提交 IT 工单并提供项目 URL、申请权限级别和业务原因。

## 审批要求

Developer 及以上权限必须经过项目 Owner 或部门负责人确认。

生产相关仓库的 Maintainer 权限需要研发负责人审批。

## 需要创建工单的情况

- 项目 Owner 离职或无法联系。
- 无法登录 GitLab。
- 需要跨部门访问敏感仓库。
- 权限变更影响生产发布流程。
```

- [ ] **Step 5: Create printer FAQ document**

Create `sample_docs\printer-connection-faq.md` with:

```markdown
# 打印机连接问题 FAQ

## Windows 添加打印机

1. 连接公司办公网络或 VPN。
2. 打开“设置 > 蓝牙和设备 > 打印机和扫描仪”。
3. 点击“添加设备”。
4. 选择对应楼层的共享打印机。
5. 打印测试页。

## macOS 添加打印机

1. 连接公司办公网络或 VPN。
2. 打开“系统设置 > 打印机与扫描仪”。
3. 点击添加打印机。
4. 选择支持 AirPrint 或公司打印服务的设备。
5. 打印测试页。

## 常见问题

- 搜不到打印机：确认是否连接公司办公网络。
- 打印任务卡住：取消队列后重新提交。
- 提示驱动错误：卸载旧驱动并重新添加打印机。
- 打印乱码：确认文档格式，优先使用 PDF 打印。

## 需要创建工单的情况

- 同楼层多人无法使用同一台打印机。
- 打印机显示硬件错误。
- 打印机缺纸、缺墨或卡纸后无法恢复。
- 员工电脑没有安装打印服务权限。
```

- [ ] **Step 6: Create office software installation document**

Create `sample_docs\office-software-installation.md` with:

```markdown
# 常用办公软件安装指南

## 标准软件清单

公司标准办公软件包括：

- Microsoft 365
- Teams
- 企业 VPN 客户端
- 浏览器安全插件
- PDF 阅读器
- 终端安全客户端

## 安装流程

1. 打开公司软件中心。
2. 搜索需要安装的软件名称。
3. 点击安装并等待软件中心完成部署。
4. 安装完成后重启应用。
5. 如果软件需要授权，使用公司账号登录激活。

## 无法安装的处理方式

- 确认电脑已连接公司网络或 VPN。
- 确认终端安全客户端在线。
- 重启软件中心后再次尝试。
- 检查磁盘空间是否大于 5GB。

## 需要创建工单的情况

- 软件中心无法打开。
- 安装失败并出现错误码。
- 需要安装不在标准清单中的软件。
- 软件授权失败或提示许可证不足。
```

- [ ] **Step 7: Verify all sample documents exist**

Run:

```powershell
Get-ChildItem D:\program\agent\projects\it-helpdesk-agent\sample_docs -Filter *.md | Select-Object Name
```

Expected output contains exactly:

```text
vpn-troubleshooting.md
email-account-and-password.md
gitlab-permission-request.md
printer-connection-faq.md
office-software-installation.md
```

---

### Task 4: Verify Baseline Tests

**Files:**
- Existing tests under `D:\program\agent\projects\it-helpdesk-agent\tests`

- [ ] **Step 1: Run existing test suite in the new project**

Run:

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
python -m pytest tests -v
```

Expected: all existing tests pass. If local embedding downloads are triggered unexpectedly, run the smaller baseline set:

```powershell
python -m pytest tests/test_config.py tests/test_health_api.py tests/test_logging.py -v
```

Expected: selected baseline tests pass.

- [ ] **Step 2: Run a smoke import for FastAPI app title**

Run:

```powershell
cd D:\program\agent\projects\it-helpdesk-agent
python -c "from app.main import app; print(app.title)"
```

Expected:

```text
Enterprise IT Helpdesk Agent
```

- [ ] **Step 3: Confirm `rag-assistant` remains untouched**

Run:

```powershell
git -C D:\program\agent\projects\rag-assistant status --short
```

Expected: no output.

---

### Task 5: Day 1 Completion Check

**Files:**
- Inspect: `D:\program\agent\projects\it-helpdesk-agent`

- [ ] **Step 1: Confirm Day 1 deliverables**

Run:

```powershell
Test-Path D:\program\agent\projects\it-helpdesk-agent
Test-Path D:\program\agent\projects\it-helpdesk-agent\README.md
Test-Path D:\program\agent\projects\it-helpdesk-agent\sample_docs\vpn-troubleshooting.md
Test-Path D:\program\agent\projects\it-helpdesk-agent\app\core\config.py
```

Expected:

```text
True
True
True
True
```

- [ ] **Step 2: Summarize verification results**

Record in the final response:

```text
Created project: D:\program\agent\projects\it-helpdesk-agent
Updated project identity: Enterprise IT Helpdesk Agent
Added sample docs: 5
Baseline tests: pass or list failing command and failure reason
rag-assistant status: clean
```
