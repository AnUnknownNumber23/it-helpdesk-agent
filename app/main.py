from fastapi import FastAPI

from app.api.routes.agent import router as agent_router
from app.api.routes.health import router as health_router
from app.api.routes.rag import router as rag_router
from app.api.routes.tickets import router as tickets_router
from app.core.config import settings
from app.core.logging import configure_logging


configure_logging()
app = FastAPI(title=settings.app_name)
app.include_router(agent_router)
app.include_router(health_router)
app.include_router(rag_router)
app.include_router(tickets_router)
