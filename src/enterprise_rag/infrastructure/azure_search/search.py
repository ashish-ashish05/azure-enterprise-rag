from typing import Any

from azure.search.documents.models import VectorizedQuery

from enterprise_rag.application.models import RetrievalResult
from enterprise_rag.infrastructure.azure_search.client import (
    AzureSearchClient,
)


class AzureSearchIndexer:
    """Index document chunks in Azure AI Search."""

    def __init__(
        self,
        client: AzureSearchClient,
    ) -> None:
        self._search_client = client.search_client

    def index_chunks(
        self,
        chunks: list[Any],
        embeddings: list[list[float]],
    ) -> None:
        """Upload chunks and embeddings to Azure AI Search."""

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings"
            )

        documents = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):
            documents.append(
                {
                    "id": chunk.chunk_id,
                    "content": chunk.content,
                    "content_vector": embedding,
                    "document_id": chunk.document_id,
                    "source": chunk.source,
                    "chunk_index": chunk.chunk_index,
                    "department": chunk.metadata.get(
                        "department"
                    ),
                    "document_version": chunk.metadata.get(
                        "document_version"
                    ),
                    "effective_date": self._format_date(
                        chunk.metadata.get(
                            "effective_date"
                        )
                    ),
                    "page": chunk.metadata.get("page"),
                    "section": chunk.metadata.get("section"),
                }
            )

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
    def _format_date(value: Any) -> str | None:
        if value is None:
            return None

        if hasattr(value, "isoformat"):
            return value.isoformat()

        return str(value)


class AzureSearchRetriever:
    """Retrieve documents from Azure AI Search."""

    _SELECT_FIELDS = [
        "id",
        "content",
        "document_id",
        "source",
        "department",
        "document_version",
        "effective_date",
        "page",
        "section",
        "chunk_index",
    ]

    def __init__(
        self,
        client: AzureSearchClient,
    ) -> None:
        self._search_client = client.search_client

    def hybrid_search(
        self,
        query: str,
        query_embedding: list[float],
        *,
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        """Run keyword and vector search together."""

        if not query.strip():
            raise ValueError(
                "Search query cannot be empty"
            )

        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=top_k,
            fields="content_vector",
            kind="vector",
        )

        results = self._search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=self._SELECT_FIELDS,
            top=top_k,
        )

        return [
            self._to_result(result)
            for result in results
        ]

    @staticmethod
    def _to_result(
        result: Any,
    ) -> RetrievalResult:
        return RetrievalResult(
            id=result["id"],
            content=result["content"],
            document_id=result["document_id"],
            source=result["source"],
            chunk_index=result["chunk_index"],
            score=result.get("@search.score"),
            department=result.get("department"),
            document_version=result.get(
                "document_version"
            ),
            effective_date=result.get(
                "effective_date"
            ),
            page=result.get("page"),
            section=result.get("section"),
        )