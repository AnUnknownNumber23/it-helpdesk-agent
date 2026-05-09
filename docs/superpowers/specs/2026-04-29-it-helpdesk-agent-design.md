# 企业 IT 服务台 Agent 设计文档

## 项目决策

新建项目目录 `projects/it-helpdesk-agent`，以当前 `projects/rag-assistant` 代码库为起点复制一份，再在新项目中扩展。

现有 `rag-assistant` 保持为干净的 RAG 基础项目。新的 `it-helpdesk-agent` 作为面向企业场景的 Agent 应用，加入 IT 支持流程、工单处理和数据看板。

## 产品目标

Enterprise IT Helpdesk Agent 是一个企业内部 IT 服务台助手。

员工可以用自然语言咨询 IT 问题。Agent 会先检索 IT 知识库，并基于检索结果返回带引用来源的回答。如果问题信息不足，Agent 会要求员工补充关键信息。如果问题需要人工介入，Agent 会自动创建 IT 工单，并为 IT 团队生成问题摘要、分类、优先级和建议处理步骤。

## 目标用户

- 需要解决内部 IT 问题的企业员工。
- 负责处理未解决问题或高风险问题的 IT 支持人员。
- 需要看到完整 Agent 工作流的项目评审者，而不只是一个单独的 RAG 演示。

## MVP 范围

MVP 包含：

- IT 知识库文档上传和入库。
- 员工问题输入。
- RAG 回答生成和 citations 返回。
- Agent 决策输出：
  - `answer`：直接回答。
  - `clarify`：要求员工补充缺失信息。
  - `create_ticket`：创建 IT 支持工单。
- 工单创建。
- 工单列表、工单详情和工单状态更新。
- 简单工单 Dashboard。
- 用于演示的 IT 知识库示例文档。

MVP 不包含：

- 用户登录和角色权限控制。
- 多租户支持。
- 飞书、钉钉、企业微信、Slack 或邮件集成。
- 通知流程。
- 审批流程。
- 复杂数据库迁移工具。
- 按用户或部门隔离知识库权限。

## 推荐工期

按每天 5 小时有效开发时间估算：

- 最快可演示版本：5 到 6 天。
- 推荐 MVP 完成周期：7 到 8 天。
- 更接近企业可部署版本，包含登录、权限和更强持久化能力：12 到 18 天。

推荐目标是完成一个 7 天 MVP。

## 按天开发计划

| 天数 | 工作内容 |
| --- | --- |
| 第 1 天 | 从 `rag-assistant` 创建 `it-helpdesk-agent`，更新项目命名，加入 IT 示例知识库文档。 |
| 第 2 天 | 新增工单 schema、ticket store 和 ticket service。 |
| 第 3 天 | 新增工单 API：创建、列表、详情、更新和统计。 |
| 第 4 天 | 新增 Agent 决策服务：分类、优先级、追问和建单判断。 |
| 第 5 天 | 改造 Streamlit 员工提问流程，展示 Agent 回答和自动建单结果。 |
| 第 6 天 | 新增 Streamlit 工单管理页和 Dashboard。 |
| 第 7 天 | 补充重点测试、修复问题、更新 README 和演示流程。 |

## 高层流程

```text
员工提问
  -> 检索相关 IT 知识库片段
  -> 生成 grounded answer 和 citations
  -> Agent 判断处理动作
      -> answer：返回答案和引用来源
      -> clarify：要求补充缺失信息
      -> create_ticket：创建工单并返回 ticket id
  -> IT 人员查看并更新工单
```

## Agent 决策模型

MVP 使用一个决策服务，不做复杂的多 Agent 系统。

决策服务接收：

- 用户原始问题。
- RAG 生成的回答。
- 检索到的 citations。
- 可用时接收检索质量信号。

返回结构化结果：

```json
{
  "action": "answer | clarify | create_ticket",
  "category": "account | network | software | hardware | permission | other",
  "priority": "low | medium | high",
  "summary": "简短问题摘要",
  "user_message": "展示给员工看的消息",
  "ticket_title": "需要建单时的工单标题",
  "suggested_resolution": "给 IT 人员看的建议处理步骤"
}
```

初始决策规则可以结合确定性规则和 LLM 结构化输出：

- 当问题缺少受影响系统、错误提示、账号、设备或期望行为时，使用 `clarify`。
- 当问题涉及账号锁定、权限申请、硬件损坏、设备更换、数据丢失或反复登录失败时，使用 `create_ticket`。
- 当 RAG 回答包含可执行步骤，并且有相关 citations 时，使用 `answer`。
- 对账号锁定、访问阻塞、安全敏感问题和关键业务系统问题提高优先级。

## 后端架构

新项目保留当前 FastAPI 和 RAG 模块，并新增 Agent 与工单模块。

```text
app/
  api/routes/
    agent.py
    health.py
    rag.py
    tickets.py

  core/
    config.py
    logging.py

  rag/
    loaders.py
    retriever.py
    splitter.py
    vector_store.py

  schemas/
    agent.py
    rag.py
    ticket.py

  services/
    agent_service.py
    ingest_service.py
    query_service.py
    ticket_service.py

  storage/
    ticket_store.py
```

职责划分：

- `query_service.py`：保留 RAG 检索和回答生成能力。
- `agent_service.py`：判断 action、category、priority 和是否建议建单。
- `ticket_service.py`：创建、查询、读取和更新工单。
- `ticket_store.py`：处理工单持久化。
- `agent.py`：暴露员工侧 Agent API。
- `tickets.py`：暴露 IT 人员侧工单 API。

## 持久化选择

MVP 使用 SQLite。

原因：

- 比 JSON 文件更接近企业项目。
- 仍然足够简单，适合本地演示。
- 能干净地支持筛选、更新和 Dashboard 统计。
- 后续可以在保持 service 边界不变的情况下替换为 PostgreSQL。

## API 设计

保留现有 RAG 接口：

```text
POST /rag/ingest
POST /rag/ask
```

新增业务接口：

```text
POST /agent/ask
GET /tickets
GET /tickets/{ticket_id}
PATCH /tickets/{ticket_id}
GET /tickets/stats
```

`POST /agent/ask` 是员工侧主入口。它会执行 RAG，调用决策服务判断下一步动作，并在 action 为 `create_ticket` 时自动创建工单。

## 工单数据模型

```json
{
  "id": "TICKET-20260429-0001",
  "title": "VPN 连接失败",
  "description": "员工反馈 VPN 登录失败，并提示认证错误。",
  "category": "network",
  "priority": "medium",
  "status": "open",
  "ai_summary": "用户无法连接 VPN，问题可能与账号状态或客户端配置有关。",
  "suggested_resolution": "建议检查账号状态、VPN 客户端版本、网络连通性和认证策略。",
  "source_question": "VPN 连不上怎么办？",
  "created_at": "2026-04-29T10:00:00",
  "updated_at": "2026-04-29T10:00:00",
  "resolution_note": ""
}
```

允许的状态：

- `open`
- `in_progress`
- `resolved`
- `closed`

允许的分类：

- `account`
- `network`
- `software`
- `hardware`
- `permission`
- `other`

允许的优先级：

- `low`
- `medium`
- `high`

## Streamlit UI

MVP 继续使用 Streamlit，避免引入新的前端框架成本。

使用四个 tab：

- `Ask IT Agent`：员工提问入口、回答展示、citations 和建单结果。
- `Knowledge Base`：上传 IT 知识库文档。
- `Tickets`：工单列表、筛选、详情、状态更新和处理备注。
- `Dashboard`：总工单数、待处理工单数、已解决工单数和分类分布。

## 示例知识库

在示例数据目录下加入演示用 Markdown 文档：

- VPN 故障排查指南。
- 邮箱账号开通和密码重置流程。
- GitLab 权限申请流程。
- 打印机连接问题 FAQ。
- 常用办公软件安装指南。

这些文档可以让项目在不依赖企业私有数据的情况下，演示较真实的 IT 支持行为。

## 测试范围

补充重点测试：

- 可回答 IT 问题返回 `answer`。
- 信息不足问题返回 `clarify`。
- 需要人工支持的问题返回 `create_ticket`。
- 工单创建服务。
- 工单列表和详情 API。
- 工单状态更新 API。
- 工单统计 API。
- `/agent/ask` 自动创建工单的端到端流程。

## 完成标准

MVP 完成时应满足：

- 新的 `it-helpdesk-agent` 项目可以独立运行。
- 用户可以上传 IT 文档。
- 用户可以咨询 IT 问题，并得到带 citations 的回答。
- Agent 可以返回 `answer`、`clarify` 或 `create_ticket`。
- 对需要人工支持的问题，系统会自动创建工单。
- IT 人员可以查看和更新工单。
- Dashboard 可以展示有用的工单统计。
- README 记录安装、配置和演示流程。
