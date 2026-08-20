from typing import Any

from enterprise_rag.application.models import RetrievalResult

from azure.search.documents.models import VectorizedQuery

from enterprise_rag.infrastructure.azure_search.client import (
    AzureSearchClient,
)


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
            raise ValueError("Search query cannot be empty")

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
    def _to_result(result: Any) -> RetrievalResult:
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