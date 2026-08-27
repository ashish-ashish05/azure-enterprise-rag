from typing import Protocol


class DocumentFamilyResolver(Protocol):
    """Resolve the document family relevant to a question."""

    def resolve(
        self,
        question: str,
        document_family_id: str | None = None,
    ) -> str | None:
        """Return the requested document family, if known."""
        ...


class ExplicitDocumentFamilyResolver:
    """Resolve a document family supplied explicitly by the caller."""

    def resolve(
        self,
        question: str,
        document_family_id: str | None = None,
    ) -> str | None:
        """Return the explicit family ID when provided."""

        if not question.strip():
            raise ValueError(
                "Question cannot be empty"
            )

        if document_family_id is None:
            return None

        family_id = document_family_id.strip()

        if not family_id:
            raise ValueError(
                "document_family_id cannot be empty"
            )

        return family_id