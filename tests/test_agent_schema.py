import pytest
from pydantic import ValidationError

from app.schemas.agent import AgentAction, AgentDecision
from app.schemas.ticket import TicketCategory, TicketPriority


def test_agent_decision_defaults_ticket_fields_to_empty_strings() -> None:
    decision = AgentDecision(
        action=AgentAction.ANSWER,
        category=TicketCategory.NETWORK,
        priority=TicketPriority.LOW,
        summary="VPN troubleshooting guidance is available.",
        user_message="Try the VPN troubleshooting steps from the knowledge base.",
    )

    assert decision.ticket_title == ""
    assert decision.suggested_resolution == ""


def test_agent_decision_accepts_create_ticket_fields() -> None:
    decision = AgentDecision(
        action=AgentAction.CREATE_TICKET,
        category=TicketCategory.PERMISSION,
        priority=TicketPriority.MEDIUM,
        summary="User needs GitLab access.",
        user_message="I will create a ticket for IT to review the access request.",
        ticket_title="GitLab access request",
        suggested_resolution="Confirm project owner approval and grant the requested role.",
    )

    assert decision.action == AgentAction.CREATE_TICKET
    assert decision.category == TicketCategory.PERMISSION
    assert decision.priority == TicketPriority.MEDIUM
    assert decision.ticket_title == "GitLab access request"


def test_agent_decision_rejects_unknown_action() -> None:
    with pytest.raises(ValidationError):
        AgentDecision(
            action="wait",
            category=TicketCategory.OTHER,
            priority=TicketPriority.LOW,
            summary="Unknown action.",
            user_message="Unknown action.",
        )
