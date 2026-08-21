from io import BytesIO

from pypdf import PdfReader

from enterprise_rag.domain.models import (
    Document,
    DocumentPage,
)
from enterprise_rag.ingestion.loaders.base import DocumentLoader


class PdfDocumentLoader(DocumentLoader):
    """Extract text from PDF documents while preserving pages."""

    def load(
        self,
        content: bytes,
        *,
        document_id: str,
        source: str,
    ) -> Document:

        reader = PdfReader(BytesIO(content))

        pages: list[DocumentPage] = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            text = page.extract_text() or ""
            text = text.strip()

            if text:
                pages.append(
                    DocumentPage(
                        page_number=page_number,
                        content=text,
                    )
                )

        full_text = "\n\n".join(
            page.content
            for page in pages
        )

        return Document(
            document_id=document_id,
            source=source,
            content=full_text,
            content_type="application/pdf",
            metadata={
                "page_count": len(reader.pages),
            },
            pages=pages,
        )