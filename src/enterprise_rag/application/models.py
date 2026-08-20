from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalResult:
    """A chunk returned by the retrieval layer."""

    id: str
    content: str
    document_id: str
    source: str
    chunk_index: int
    score: float | None = None
    department: str | None = None
    document_version: str | None = None
    effective_date: str | None = None
    page: int | None = None
    section: str | None = None