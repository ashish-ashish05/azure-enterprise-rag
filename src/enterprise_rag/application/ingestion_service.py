from enterprise_rag.ingestion.chunking.splitter import DocumentChunker
from enterprise_rag.ingestion.pipeline import (
    DocumentIngestionPipeline,
)
from enterprise_rag.infrastructure.azure_openai.embeddings import (
    AzureOpenAIEmbeddingService,
)
from enterprise_rag.infrastructure.azure_search.search import (
    AzureSearchIndexer,
)


class IngestionService:
    """Application service for document indexing."""

    def __init__(
        self,
        ingestion_pipeline: DocumentIngestionPipeline,
        chunker: DocumentChunker,
        embedding_service: AzureOpenAIEmbeddingService,
        search_indexer: AzureSearchIndexer,
    ) -> None:
        self._ingestion_pipeline = ingestion_pipeline
        self._chunker = chunker
        self._embedding_service = embedding_service
        self._search_indexer = search_indexer

    def ingest_all(self) -> int:
        """Load, chunk, embed, and index all supported documents."""

        documents = self._ingestion_pipeline.load_all()

        total_chunks = 0

        for document in documents:
            chunks = self._chunker.split(document)

            embeddings = self._embedding_service.embed_chunks(
                chunks
            )

            self._search_indexer.index_chunks(
                chunks,
                embeddings,
            )

            total_chunks += len(chunks)

        return total_chunks