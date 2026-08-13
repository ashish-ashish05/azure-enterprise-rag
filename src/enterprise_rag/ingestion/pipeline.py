from pathlib import PurePosixPath

from enterprise_rag.domain.models import Document
from enterprise_rag.ingestion.loaders.factory import DocumentLoaderFactory
from enterprise_rag.infrastructure.azure_storage.blob import BlobStorageClient


class DocumentIngestionPipeline:
    """Load documents from Azure Blob Storage."""

    def __init__(
        self,
        blob_storage: BlobStorageClient,
    ) -> None:
        self._blob_storage = blob_storage

    def load_all(self) -> list[Document]:
        documents: list[Document] = []

        for blob_name in self._blob_storage.list_blobs():
            filename = PurePosixPath(blob_name).name

            loader = DocumentLoaderFactory.create(filename)

            content = self._blob_storage.download_blob(blob_name)

            document = loader.load(
                content,
                document_id=blob_name,
                source=blob_name,
            )

            documents.append(document)

        return documents