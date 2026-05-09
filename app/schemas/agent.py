from enum import Enum

from pydantic import BaseModel

from app.schemas.ticket import TicketCategory, TicketPriority


class AgentAction(str, Enum):
    ANSWER = "answer"
    CLARIFY = "clarify"
    CREATE_TICKET = "create_ticket"


class AgentDecision(BaseModel):
    action: AgentAction
    category: TicketCategory
    priority: TicketPriority
    summary: str
    user_message: str
    ticket_title: str = ""
    suggested_resolution: str = ""
