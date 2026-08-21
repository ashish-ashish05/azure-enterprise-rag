from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from enterprise_rag.domain.metadata import DocumentMetadata


@dataclass
class Document:
    """Normalized document representation used by the ingestion pipeline."""

    document_id: str
    source: str
    content: str
    content_type: str
    metadata: DocumentMetadata = field(
        default_factory=DocumentMetadata
    )
    created_at: datetime | None = None


@dataclass
class DocumentChunk:
    """A retrievable chunk derived from an enterprise document."""

    chunk_id: str
    document_id: str
    content: str
    source: str
    chunk_index: int
    metadata: dict[str, Any] = field(default_factory=dict)