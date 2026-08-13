from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Document:
    """Normalized document representation used by the ingestion pipeline."""

    document_id: str
    source: str
    content: str
    content_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None