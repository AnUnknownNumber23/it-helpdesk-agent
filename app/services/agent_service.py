from app.schemas.agent import AgentAction, AgentDecision
from app.schemas.rag import Citation
from app.schemas.ticket import TicketCategory, TicketPriority


CATEGORY_KEYWORDS: list[tuple[TicketCategory, tuple[str, ...]]] = [
    (
        TicketCategory.PERMISSION,
        ("permission", "access", "gitlab", "repository", "repo", "project", "grant"),
    ),
    (
        TicketCategory.ACCOUNT,
        ("account", "password", "login", "mfa", "locked", "unlock", "账号", "账户", "密码", "登录", "认证", "锁定", "解锁"),
    ),
    (
        TicketCategory.NETWORK,
        ("vpn", "wi-fi", "wifi", "network", "dns", "intranet", "网络", "内网"),
    ),
    (
        TicketCategory.SOFTWARE,
        ("install", "license", "software", "teams", "microsoft 365", "office"),
    ),
    (
        TicketCategory.HARDWARE,
        ("printer", "laptop", "device", "hardware", "broken", "replacement", "screen"),
    ),
]

CREATE_TICKET_KEYWORDS = (
    "account is locked",
    "locked",
    "unlock",
    "mfa device",
    "grant",
    "permission",
    "access request",
    "developer access",
    "maintainer access",
    "broken",
    "replacement",
    "data loss",
    "repeated login",
    "login failures",
    "cannot access",
    "blocked",
    "账号",
    "账户",
    "锁定",
    "解锁",
    "认证失败",
    "登录失败",
    "多次重试",
    "创建工单",
    "建单",
)

HIGH_PRIORITY_KEYWORDS = (
    "production",
    "finance",
    "customer",
    "billing",
    "business-critical",
    "critical",
    "data loss",
    "security",
)

VAGUE_QUESTIONS = (
    "it does not work",
    "does not work",
    "not working",
    "can't use it",
    "cannot use it",
    "help",
)


def decide_next_action(question: str, rag_answer: str, citations: list[Citation]) -> AgentDecision:
    normalized_question = question.strip()
    combined_text = f"{normalized_question} {rag_answer}".lower()
    category = infer_category(combined_text)

    if should_create_ticket(combined_text):
        priority = infer_priority(combined_text, default=TicketPriority.MEDIUM)
        return AgentDecision(
            action=AgentAction.CREATE_TICKET,
            category=category,
            priority=priority,
            summary=build_summary(normalized_question),
            user_message="This looks like it needs IT support, so a ticket should be created.",
            ticket_title=build_ticket_title(category, normalized_question),
            suggested_resolution=build_suggested_resolution(category, normalized_question),
        )

    if should_clarify(normalized_question, rag_answer, citations):
        return AgentDecision(
            action=AgentAction.CLARIFY,
            category=category,
            priority=TicketPriority.LOW,
            summary=build_summary(normalized_question),
            user_message=(
                "Please provide the affected system, the exact error message, what you expected to happen, "
                "and when the problem started."
            ),
        )

    return AgentDecision(
        action=AgentAction.ANSWER,
        category=category,
        priority=TicketPriority.LOW,
        summary=build_summary(normalized_question),
        user_message="Use the knowledge base answer and citations to try the recommended steps.",
    )


def infer_category(text: str) -> TicketCategory:
    for category, keywords in CATEGORY_KEYWORDS:
        if any(keyword in text for keyword in keywords):
            return category
    return TicketCategory.OTHER


def infer_priority(text: str, *, default: TicketPriority) -> TicketPriority:
    if any(keyword in text for keyword in HIGH_PRIORITY_KEYWORDS):
        return TicketPriority.HIGH
    return default


def should_create_ticket(text: str) -> bool:
    return any(keyword in text for keyword in CREATE_TICKET_KEYWORDS)


def should_clarify(question: str, rag_answer: str, citations: list[Citation]) -> bool:
    normalized_question = question.strip().lower()
    normalized_answer = rag_answer.strip().lower()
    if len(normalized_question) < 20:
        return True
    if normalized_question in VAGUE_QUESTIONS:
        return True
    return not citations and "no relevant content found" in normalized_answer


def build_summary(question: str) -> str:
    return question[:160]


def build_ticket_title(category: TicketCategory, question: str) -> str:
    if category == TicketCategory.PERMISSION and "gitlab" in question.lower():
        return "GitLab access request"
    readable_category = category.value.replace("_", " ").title()
    return f"{readable_category} support request"


def build_suggested_resolution(category: TicketCategory, question: str) -> str:
    if category == TicketCategory.ACCOUNT:
        return "Check account lock status, MFA registration, and recent authentication failures."
    if category == TicketCategory.PERMISSION:
        return "Confirm business reason and owner approval, then grant the minimum required access."
    if category == TicketCategory.HARDWARE:
        return "Inspect the hardware issue, confirm replacement need, and arrange repair or device swap."
    if category == TicketCategory.NETWORK:
        return "Check VPN or network connectivity, DNS, client version, and affected internal systems."
    if category == TicketCategory.SOFTWARE:
        return "Check Software Center availability, license assignment, disk space, and installation logs."
    return f"Review the user's report and follow standard IT support triage. Source question: {question[:80]}"
