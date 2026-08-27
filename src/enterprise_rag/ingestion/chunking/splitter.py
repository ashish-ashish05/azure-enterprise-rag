import re
from dataclasses import asdict

from enterprise_rag.domain.models import (
    Document,
    DocumentChunk,
)


class DocumentChunker:
    """Split documents into overlapping word-based chunks."""

    def __init__(
        self,
        chunk_size: int = 700,
        chunk_overlap: int = 100,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero"
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative"
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def split(
        self,
        document: Document,
    ) -> list[DocumentChunk]:
        """Split a document into chunks.

        Page-aware documents are chunked page by page.
        Documents without page information fall back to
        whole-document chunking.
        """

        if document.pages:
            return self._split_pages(document)

        return self._split_full_document(document)

    def _split_pages(
        self,
        document: Document,
    ) -> list[DocumentChunk]:
        """Split each page independently."""

        chunks: list[DocumentChunk] = []

        global_chunk_index = 0

        for page in document.pages:
            words = self._tokenize(page.content)

            if not words:
                continue

            start = 0

            while start < len(words):
                end = min(
                    start + self._chunk_size,
                    len(words),
                )

                chunk_words = words[start:end]

                chunk_text = " ".join(chunk_words)

                chunks.append(
                    DocumentChunk(
                        chunk_id=(
                            f"{self._safe_document_id(document.document_id)}"
                            f"_chunk-{global_chunk_index}"
                        ),
                        document_id=document.document_id,
                        content=chunk_text,
                        source=document.source,
                        chunk_index=global_chunk_index,
                        metadata={
                            **asdict(document.metadata),
                            "page": page.page_number,
                            "chunk_size_words": len(chunk_words),
                        },
                    )
                )

                global_chunk_index += 1

                if end == len(words):
                    break

                start = end - self._chunk_overlap

        return chunks

    def _split_full_document(
        self,
        document: Document,
    ) -> list[DocumentChunk]:
        """Fallback for documents without page information."""

        words = self._tokenize(document.content)

        if not words:
            return []

        chunks: list[DocumentChunk] = []

        start = 0
        chunk_index = 0

        while start < len(words):
            end = min(
                start + self._chunk_size,
                len(words),
            )

            chunk_words = words[start:end]

            chunk_text = " ".join(chunk_words)

            chunks.append(
                DocumentChunk(
                    chunk_id=(
                        f"{self._safe_document_id(document.document_id)}"
                        f"_chunk-{chunk_index}"
                    ),
                    document_id=document.document_id,
                    content=chunk_text,
                    source=document.source,
                    chunk_index=chunk_index,
                    metadata={
                        **asdict(document.metadata),
                        "page": page.page_number,
                        "chunk_size_words": len(chunk_words),
                    },
                )
            )

            if end == len(words):
                break

            start = end - self._chunk_overlap
            chunk_index += 1

        return chunks

    @staticmethod
    def _safe_document_id(
        document_id: str,
    ) -> str:
        """Convert a document ID into an Azure Search-safe key."""

        return re.sub(
            r"[^A-Za-z0-9_=-]",
            "_",
            document_id,
        )

    @staticmethod
    def _tokenize(
        text: str,
    ) -> list[str]:
        return re.findall(
            r"\S+",
            text,
        )