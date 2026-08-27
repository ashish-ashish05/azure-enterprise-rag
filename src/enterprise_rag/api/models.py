from dataclasses import dataclass

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request body for the RAG query endpoint."""

    question: str = Field(
        min_length=1,
        description="Question to answer from enterprise documents.",
    )
    document_family_id: str | None = None
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class SourceResponse(BaseModel):
    """Source information returned with an answer."""

    source: str
    document_family_id: str
    document_version: str | None = None
    effective_date: str | None = None
    page: int | None = None
    chunk_index: int


class QueryResponse(BaseModel):
    """RAG API response."""

    question: str
    answer: str
    sources: list[SourceResponse]