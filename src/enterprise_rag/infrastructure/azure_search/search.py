from typing import Any

from enterprise_rag.domain.models import DocumentChunk
from enterprise_rag.infrastructure.azure_search.client import (
    AzureSearchClient,
)


class AzureSearchIndexer:
    """Index document chunks in Azure AI Search."""

    def __init__(self, client: AzureSearchClient) -> None:
        self._search_client = client.search_client

    def index_chunk(
        self,
        chunk: DocumentChunk,
        embedding: list[float],
    ) -> None:
        """Index one document chunk."""

        document = self._build_search_document(
            chunk=chunk,
            embedding=embedding,
        )

        result = self._search_client.upload_documents(
            documents=[document]
        )

        if not result[0].succeeded:
            raise RuntimeError(
                f"Failed to index chunk: {chunk.chunk_id}"
            )

    def index_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        """Index multiple document chunks."""

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings"
            )

        if not chunks:
            return

        documents = [
            self._build_search_document(
                chunk=chunk,
                embedding=embedding,
            )
            for chunk, embedding in zip(
                chunks,
                embeddings,
                strict=True,
            )
        ]

        results = self._search_client.upload_documents(
            documents=documents
        )

        failed = [
            result
            for result in results
            if not result.succeeded
        ]

        if failed:
            raise RuntimeError(
                f"Failed to index {len(failed)} documents"
            )

    @staticmethod
    def _build_search_document(
        chunk: DocumentChunk,
        embedding: list[float],
    ) -> dict[str, Any]:
        metadata = chunk.metadata

        return {
            "id": chunk.chunk_id,
            "content": chunk.content,
            "content_vector": embedding,
            "document_id": chunk.document_id,
            "source": chunk.source,
            "department": metadata.get("department"),
            "document_version": metadata.get(
                "document_version"
            ),
            "effective_date": metadata.get(
                "effective_date"
            ),
            "page": metadata.get("page"),
            "section": metadata.get("section"),
            "chunk_index": chunk.chunk_index,
        }