from datetime import date, datetime
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
                    "document_family_id": chunk.document_family_id,
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
    def _format_date(
        value: Any,
    ) -> str | None:
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
        department: str | None = None,
        document_version: str | None = None,
        effective_date_on_or_before: (
            date | datetime | None
        ) = None,
    ) -> list[RetrievalResult]:
        """Run hybrid search with optional metadata filters."""

        if not query.strip():
            raise ValueError(
                "Search query cannot be empty"
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero"
            )

        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=top_k,
            fields="content_vector",
            kind="vector",
        )

        filters = self._build_filter(
            department=department,
            document_version=document_version,
            effective_date_on_or_before=(
                effective_date_on_or_before
            ),
        )

        results = self._search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=self._SELECT_FIELDS,
            filter=filters,
            top=top_k,
        )

        return [
            self._to_result(result)
            for result in results
        ]

    @staticmethod
    def _build_filter(
        *,
        department: str | None,
        document_version: str | None,
        effective_date_on_or_before: (
            date | datetime | None
        ),
    ) -> str | None:
        """Build an Azure AI Search OData filter."""

        filters: list[str] = []

        if department is not None:
            escaped_department = (
                AzureSearchRetriever._escape_odata_string(
                    department
                )
            )

            filters.append(
                f"department eq '{escaped_department}'"
            )

        if document_version is not None:
            escaped_version = (
                AzureSearchRetriever._escape_odata_string(
                    document_version
                )
            )

            filters.append(
                f"document_version eq '{escaped_version}'"
            )

        if effective_date_on_or_before is not None:
            if isinstance(
                effective_date_on_or_before,
                datetime,
            ):
                value = (
                    effective_date_on_or_before.isoformat()
                )
            else:
                value = (
                    f"{effective_date_on_or_before.isoformat()}"
                    "T23:59:59Z"
                )

            filters.append(
                f"effective_date le {value}"
            )

        if not filters:
            return None

        return " and ".join(filters)

    @staticmethod
    def _escape_odata_string(
        value: str,
    ) -> str:
        """Escape a string for an OData string literal."""

        return value.replace(
            "'",
            "''",
        )

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