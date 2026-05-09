from fastapi import APIRouter

from app.schemas.agent import AgentAction
from app.schemas.agent_api import AgentAskRequest, AgentAskResponse
from app.schemas.ticket import TicketCreate
from app.services import agent_service, query_service, ticket_service


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/ask", response_model=AgentAskResponse)
def ask_agent(request: AgentAskRequest) -> AgentAskResponse:
    rag_result = query_service.answer_question(request.question, request.top_k)
    decision = agent_service.decide_next_action(request.question, rag_result.answer, rag_result.citations)
    ticket = None

    if decision.action == AgentAction.CREATE_TICKET:
        ticket = ticket_service.create_ticket(
            TicketCreate(
                title=decision.ticket_title,
                description=decision.summary,
                category=decision.category,
                priority=decision.priority,
                ai_summary=decision.summary,
                suggested_resolution=decision.suggested_resolution,
                source_question=request.question,
            )
        )

    return AgentAskResponse(
        question=request.question,
        answer=rag_result.answer,
        citations=rag_result.citations,
        decision=decision,
        ticket=ticket,
    )
