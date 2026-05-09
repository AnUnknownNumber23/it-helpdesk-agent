from app.schemas.agent import AgentAction
from app.schemas.rag import Citation
from app.schemas.ticket import TicketCategory, TicketPriority
from app.services.agent_service import decide_next_action


def citation(source: str = "vpn-troubleshooting.md") -> Citation:
    return Citation(source=source, snippet="Follow the documented troubleshooting steps.")


def test_decision_answers_when_cited_rag_answer_has_guidance() -> None:
    decision = decide_next_action(
        question="How do I fix VPN DNS issues?",
        rag_answer="Run ipconfig /flushdns and reconnect to VPN.",
        citations=[citation()],
    )

    assert decision.action == AgentAction.ANSWER
    assert decision.category == TicketCategory.NETWORK
    assert decision.priority == TicketPriority.LOW
    assert "knowledge base" in decision.user_message.lower()
    assert decision.ticket_title == ""


def test_decision_clarifies_when_question_is_too_vague() -> None:
    decision = decide_next_action(
        question="It does not work",
        rag_answer="No relevant content found in the knowledge base.",
        citations=[],
    )

    assert decision.action == AgentAction.CLARIFY
    assert decision.category == TicketCategory.OTHER
    assert decision.priority == TicketPriority.LOW
    assert "system" in decision.user_message.lower()
    assert "error" in decision.user_message.lower()


def test_decision_creates_ticket_for_locked_account() -> None:
    decision = decide_next_action(
        question="My account is locked after repeated login failures.",
        rag_answer="You need IT to unlock the account.",
        citations=[citation("email-account-and-password.md")],
    )

    assert decision.action == AgentAction.CREATE_TICKET
    assert decision.category == TicketCategory.ACCOUNT
    assert decision.priority == TicketPriority.MEDIUM
    assert "account" in decision.ticket_title.lower()
    assert decision.suggested_resolution


def test_decision_creates_ticket_for_chinese_locked_vpn_account_request() -> None:
    decision = decide_next_action(
        question="我的 VPN 一直认证失败，账号也可能被锁定了，已经多次重试还是不行，请帮我创建工单。",
        rag_answer="账号锁定需要 IT 支持人员处理。",
        citations=[citation()],
    )

    assert decision.action == AgentAction.CREATE_TICKET
    assert decision.category == TicketCategory.ACCOUNT
    assert decision.priority == TicketPriority.MEDIUM
    assert decision.ticket_title


def test_decision_creates_ticket_for_permission_request() -> None:
    decision = decide_next_action(
        question="Please grant me Developer access to the GitLab backend project.",
        rag_answer="Project owner approval is required.",
        citations=[citation("gitlab-permission-request.md")],
    )

    assert decision.action == AgentAction.CREATE_TICKET
    assert decision.category == TicketCategory.PERMISSION
    assert decision.priority == TicketPriority.MEDIUM
    assert "GitLab" in decision.ticket_title


def test_decision_marks_production_access_block_as_high_priority() -> None:
    decision = decide_next_action(
        question="I cannot access the production finance system and customer billing is blocked.",
        rag_answer="Production system access issues require IT support.",
        citations=[citation()],
    )

    assert decision.action == AgentAction.CREATE_TICKET
    assert decision.category == TicketCategory.PERMISSION
    assert decision.priority == TicketPriority.HIGH
    assert "production" in decision.summary.lower()


def test_decision_detects_software_category_for_install_issue() -> None:
    decision = decide_next_action(
        question="Microsoft 365 install fails with error code 30015.",
        rag_answer="Open Software Center and retry the installation.",
        citations=[citation("office-software-installation.md")],
    )

    assert decision.action == AgentAction.ANSWER
    assert decision.category == TicketCategory.SOFTWARE


def test_decision_creates_ticket_for_hardware_damage() -> None:
    decision = decide_next_action(
        question="My laptop screen is broken and needs replacement.",
        rag_answer="Hardware replacement requires IT support.",
        citations=[],
    )

    assert decision.action == AgentAction.CREATE_TICKET
    assert decision.category == TicketCategory.HARDWARE
    assert decision.priority == TicketPriority.MEDIUM
    assert "hardware" in decision.suggested_resolution.lower()
