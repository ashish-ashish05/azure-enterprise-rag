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
    )

    print(f"Retrieved {len(results)} results")

    for index, result in enumerate(results, start=1):
        print()
        print(f"--- Result {index} ---")
        print(f"Score: {result.score}")
        print(f"Source: {result.source}")
        print(f"Chunk: {result.chunk_index}")
        print()
        print(result.content[:500])


if __name__ == "__main__":
    main()