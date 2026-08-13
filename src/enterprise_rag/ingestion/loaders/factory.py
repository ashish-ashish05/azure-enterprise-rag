from pathlib import Path

from enterprise_rag.ingestion.loaders.base import DocumentLoader
from enterprise_rag.ingestion.loaders.docx import DocxDocumentLoader
from enterprise_rag.ingestion.loaders.pdf import PdfDocumentLoader
from enterprise_rag.ingestion.loaders.xlsx import XlsxDocumentLoader


class DocumentLoaderFactory:
    """Create a document loader based on file extension."""

    _loaders: dict[str, type[DocumentLoader]] = {
        ".pdf": PdfDocumentLoader,
        ".docx": DocxDocumentLoader,
        ".xlsx": XlsxDocumentLoader,
    }

    @classmethod
    def create(cls, filename: str) -> DocumentLoader:
        extension = Path(filename).suffix.lower()

        loader_class = cls._loaders.get(extension)

        if loader_class is None:
            raise ValueError(
                f"Unsupported document type: {extension}"
            )

        return loader_class()