import re

from enterprise_rag.domain.models import Document, DocumentChunk


class DocumentChunker:
    """Split documents into overlapping word-based chunks."""

    def __init__(
        self,
        chunk_size: int = 700,
        chunk_overlap: int = 100,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def split(self, document: Document) -> list[DocumentChunk]:
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
                        **document.metadata,
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
    def _safe_document_id(document_id: str) -> str:
        """Convert a document ID into an Azure Search-safe key."""

        return re.sub(
        r"[^A-Za-z0-9_=-]",
        "_",
        document_id,
    )

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"\S+", text)