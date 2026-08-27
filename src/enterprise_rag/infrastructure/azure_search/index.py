from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)

from enterprise_rag.config.settings import Settings
from enterprise_rag.infrastructure.azure_search.client import (
    AzureSearchClient,
)


class AzureSearchIndexManager:
    """Create and manage the RAG search index."""

    def __init__(
        self,
        client: AzureSearchClient,
        settings: Settings,
        vector_dimensions: int,
    ) -> None:
        self._client = client
        self._settings = settings
        self._vector_dimensions = vector_dimensions

    def create_or_update_index(self) -> SearchIndex:
        index = SearchIndex(
            name=self._settings.azure_search_index_name,
            fields=[
                SimpleField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                    filterable=True,
                ),
                SearchableField(
                    name="content",
                    type=SearchFieldDataType.String,
                ),
                SimpleField(
                    name="document_id",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SimpleField(
                    name="document_family_id",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SimpleField(
                    name="source",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SimpleField(
                    name="department",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    facetable=True,
                ),
                SimpleField(
                    name="document_version",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    sortable=True,
                ),
                SimpleField(
                    name="effective_date",
                    type=SearchFieldDataType.DateTimeOffset,
                    filterable=True,
                    sortable=True,
                ),
                SimpleField(
                    name="page",
                    type=SearchFieldDataType.Int32,
                    filterable=True,
                ),
                SimpleField(
                    name="section",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SimpleField(
                    name="chunk_index",
                    type=SearchFieldDataType.Int32,
                    filterable=True,
                    sortable=True,
                ),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(
                        SearchFieldDataType.Single
                    ),
                    searchable=True,
                    vector_search_dimensions=self._vector_dimensions,
                    vector_search_profile_name="rag-vector-profile",
                ),
            ],
            vector_search=VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="rag-hnsw"
                    )
                ],
                profiles=[
                    VectorSearchProfile(
                        name="rag-vector-profile",
                        algorithm_configuration_name="rag-hnsw",
                    )
                ],
            ),
        )

        return self._client.index_client.create_or_update_index(
            index
        )