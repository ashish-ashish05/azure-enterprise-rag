from datetime import date

from enterprise_rag.config.settings import get_settings
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
    AzureSearchRetriever,
)


def main() -> None:
    settings = get_settings()

    openai_client = AzureOpenAIClient(settings)

    embedding_service = AzureOpenAIEmbeddingService(
        client=openai_client,
        settings=settings,
    )

    search_client = AzureSearchClient(settings)

    retriever = AzureSearchRetriever(search_client)

    question = "What is the expense policy?"

    query_embedding = embedding_service.embed_text(
        question
    )

    results = retriever.hybrid_search(
        query=question,
        query_embedding=query_embedding,
        top_k=5,
        document_version="5.1",
        effective_date_on_or_before=date(
            2026,
            8,
            27,
        ),
    )

    print(
        f"Retrieved {len(results)} filtered results"
    )

    for result in results:
        print()
        print(f"Source: {result.source}")
        print(f"Version: {result.document_version}")
        print(f"Effective: {result.effective_date}")
        print(f"Page: {result.page}")
        print(f"Chunk: {result.chunk_index}")


if __name__ == "__main__":
    main()