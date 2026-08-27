from dataclasses import dataclass, field

from enterprise_rag.application.models import RetrievalResult


@dataclass(frozen=True)
class SourceCitation:
    """Citation pointing to retrieved source material."""

    source: str
    chunk_id: str
    chunk_index: int
    page: int | None = None
    document_family_id: str | None = None
    document_version: str | None = None
    effective_date: str | None = None


@dataclass(frozen=True)
class RAGResponse:
    """Grounded answer returned by the RAG pipeline."""

    question: str
    answer: str
    sources: list[SourceCitation] = field(
        default_factory=list
    )
    retrieved_results: list[RetrievalResult] = field(
        default_factory=list
    )