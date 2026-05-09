from pydantic import BaseModel, Field

from app.schemas.agent import AgentDecision
from app.schemas.rag import Citation
from app.schemas.ticket import Ticket


class AgentAskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int = Field(default=4, ge=1, le=8)


class AgentAskResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]
    decision: AgentDecision
    ticket: Ticket | None = None
