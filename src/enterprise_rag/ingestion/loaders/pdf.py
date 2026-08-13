from io import BytesIO

from pypdf import PdfReader

from enterprise_rag.domain.models import Document
from enterprise_rag.ingestion.loaders.base import DocumentLoader


class PdfDocumentLoader(DocumentLoader):
    """Extract text from PDF documents."""

    def load(
        self,
        content: bytes,
        *,
        document_id: str,
        source: str,
    ) -> Document:

        reader = PdfReader(BytesIO(content))

        pages: list[str] = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text.strip())

        full_text = "\n\n".join(
            page for page in pages if page
        )

        return Document(
            document_id=document_id,
            source=source,
            content=full_text,
            content_type="application/pdf",
            metadata={
                "page_count": len(reader.pages),
            },
        )