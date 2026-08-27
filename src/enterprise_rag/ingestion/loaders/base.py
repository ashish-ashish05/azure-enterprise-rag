from abc import ABC, abstractmethod

from enterprise_rag.domain.models import Document


class DocumentLoader(ABC):
    """Base interface for document loaders."""

    @abstractmethod
    def load(
        self,
        content: bytes,
        *,
        document_id: str,
        document_family_id: str,
        source: str,
    ) -> Document:
        """Load raw bytes into a normalized Document."""
        raise NotImplementedError