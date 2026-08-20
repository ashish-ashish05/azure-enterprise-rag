from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient

from enterprise_rag.config.settings import Settings


class AzureSearchClient:
    """Azure AI Search client factory."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

        if settings.azure_search_api_key:
            credential = AzureKeyCredential(
                settings.azure_search_api_key
            )
        else:
            credential = DefaultAzureCredential()

        self._index_client = SearchIndexClient(
            endpoint=settings.azure_search_endpoint,
            credential=credential,
        )

        self._search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=credential,
        )

    @property
    def index_client(self) -> SearchIndexClient:
        return self._index_client

    @property
    def search_client(self) -> SearchClient:
        return self._search_client