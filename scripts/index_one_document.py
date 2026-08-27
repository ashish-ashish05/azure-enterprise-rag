from enterprise_rag.config.settings import get_settings
from enterprise_rag.domain.models import DocumentChunk
from enterprise_rag.ingestion.chunking.splitter import DocumentChunker
from enterprise_rag.ingestion.loaders.factory import (
    DocumentLoaderFactory,
)
from enterprise_rag.ingestion.metadata.extractor import (
    DocumentMetadataExtractor,
)
from enterprise_rag.infrastructure.azure_openai.client import (
    AzureOpenAIClient,
)
from enterprise_rag.infrastructure.azure_openai.embeddings import (
    AzureOpenAIEmbeddingService,
)
from enterprise_rag.infrastructure.azure_search.client import (
    AzureSearchClient,
)
from enterprise_rag.infrastructure.azure_search.search import (
    AzureSearchIndexer,
)
from enterprise_rag.infrastructure.azure_storage.blob import (
    BlobStorageClient,
)


def main() -> None:
    settings = get_settings()

    blob_storage = BlobStorageClient(settings)

    blob_names = blob_storage.list_blobs()

    if not blob_names:
        raise RuntimeError(
            "No documents found in the Azure Blob container."
        )

    blob_name = blob_names[0]

    print(f"Indexing: {blob_name}")

    content = blob_storage.download_blob(blob_name)

    loader = DocumentLoaderFactory.create(blob_name)

    document = loader.load(
        content,
        document_id=blob_name,
        source=blob_name,
    )

    print(
        f"Extracted {len(document.content.split())} words"
    )

    metadata_extractor = DocumentMetadataExtractor()

    metadata = metadata_extractor.extract(
        document.content
    )

    document.metadata = metadata

    print(
        f"Document version: "
        f"{metadata.document_version}"
    )

    print(
        f"Effective date: "
        f"{metadata.effective_date}"
    )

    print(
        f"Policy owner: "
        f"{metadata.policy_owner}"
    )

    chunker = DocumentChunker(
        chunk_size=700,
        chunk_overlap=100,
    )

    chunks: list[DocumentChunk] = chunker.split(
        document
    )

    print(f"Created {len(chunks)} chunks")

    openai_client = AzureOpenAIClient(settings)

    embedding_service = AzureOpenAIEmbeddingService(
        client=openai_client,
        settings=settings,
    )

    embeddings = embedding_service.embed_chunks(
        chunks
    )

    print(
        f"Generated {len(embeddings)} embeddings"
    )

    search_client = AzureSearchClient(settings)

    indexer = AzureSearchIndexer(search_client)

    indexer.index_chunks(
        chunks,
        embeddings,
    )

    print(
        f"Indexed {len(chunks)} chunks into "
        f"{settings.azure_search_index_name}"
    )


if __name__ == "__main__":
    main()