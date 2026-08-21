from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DocumentMetadata:
    """Structured metadata associated with a document."""

    department: str | None = None
    document_version: str | None = None
    effective_date: date | None = None
    policy_owner: str | None = None