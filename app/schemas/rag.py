from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int = Field(default=4, ge=1, le=8)


class Citation(BaseModel):
    source: str
    snippet: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]


class IngestResponse(BaseModel):
    message: str
    file: str
    file_path: str
    chunks: int
