from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from enterprise_rag.config.settings import Settings


class BlobStorageClient:
    """Client for interacting with Azure Blob Storage."""

    def __init__(self, settings: Settings) -> None:
        credential = DefaultAzureCredential()

        self._service_client = BlobServiceClient(
            account_url=settings.azure_storage_account_url,
            credential=credential,
        )

        self._container_client = self._service_client.get_container_client(
            settings.azure_storage_container
        )

    def container_exists(self) -> bool:
        """Check whether the configured container exists."""

        return self._container_client.exists()

    def create_container(self) -> None:
        """Create the configured container if it does not exist."""

        if not self.container_exists():
            self._container_client.create_container()

    def list_blobs(self) -> list[str]:
        """Return the names of blobs in the configured container."""

        return [
            blob.name
            for blob in self._container_client.list_blobs()
        ]