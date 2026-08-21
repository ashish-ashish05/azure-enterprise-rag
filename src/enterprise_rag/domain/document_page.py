from dataclasses import dataclass, field
@dataclass(frozen=True)
class DocumentPage:
    """A single page extracted from a document."""

    page_number: int
    content: str