from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TicketCategory(str, Enum):
    ACCOUNT = "account"
    NETWORK = "network"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    PERMISSION = "permission"
    OTHER = "other"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3, max_length=4000)
    category: TicketCategory = TicketCategory.OTHER
    priority: TicketPriority = TicketPriority.MEDIUM
    ai_summary: str = ""
    suggested_resolution: str = ""
    source_question: str = Field(min_length=3, max_length=2000)


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    resolution_note: str | None = None


class Ticket(TicketCreate):
    id: str
    status: TicketStatus = TicketStatus.OPEN
    created_at: datetime
    updated_at: datetime
    resolution_note: str = ""


class TicketStats(BaseModel):
    total: int = 0
    by_status: dict[str, int] = Field(default_factory=dict)
    by_category: dict[str, int] = Field(default_factory=dict)
    by_priority: dict[str, int] = Field(default_factory=dict)
