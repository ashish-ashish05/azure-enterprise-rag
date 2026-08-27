from pathlib import Path

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

    openai_client = AzureOpenAIClient(settings)

    embedding_service = AzureOpenAIEmbeddingService(
        client=openai_client,
        settings=settings,
    )

    search_client = AzureSearchClient(settings)

    indexer = AzureSearchIndexer(
        search_client
    )

    metadata_extractor = DocumentMetadataExtractor()

    chunker = DocumentChunker(
        chunk_size=700,
        chunk_overlap=100,
    )

    total_documents = 0
    total_chunks = 0

    for blob_name in blob_names:
        print()
        print("=" * 60)
        print(f"Indexing: {blob_name}")
        print("=" * 60)

        try:
            content = blob_storage.download_blob(
                blob_name
            )

            document_family_id = Path(
                blob_name
            ).stem

            print(
                f"Document family: "
                f"{document_family_id}"
            )

            loader = DocumentLoaderFactory.create(
                blob_name
            )

            document = loader.load(
                content,
                document_id=blob_name,
                source=blob_name,
                document_family_id=document_family_id,
            )

            print(
                f"Extracted "
                f"{len(document.content.split())} words"
            )

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

            chunks: list[DocumentChunk] = (
                chunker.split(document)
            )

            print(
                f"Created {len(chunks)} chunks"
            )

            if not chunks:
                print(
                    "Skipping document because it "
                    "contains no extractable content."
                )
                continue

            embeddings = (
                embedding_service.embed_chunks(
                    chunks
                )
            )

            print(
                f"Generated {len(embeddings)} embeddings"
            )

            deleted_count = (
                indexer.delete_chunks_for_document(
                    document.document_id
                )
            )

            print(
                f"Deleted {deleted_count} existing chunks"
            )

            indexed_count = (
                indexer.index_chunks(
                    chunks,
                    embeddings,
                )
            )

            print(
                f"Indexed {indexed_count} chunks"
            )

            total_documents += 1
            total_chunks += indexed_count

        except Exception as exc:
            print(
                f"FAILED: {blob_name}"
            )
            print(
                f"Reason: {exc}"
            )

    print()
    print("=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)
    print(
        f"Documents indexed: {total_documents}"
    )
    print(
        f"Chunks indexed: {total_chunks}"
    )


if __name__ == "__main__":
    main()