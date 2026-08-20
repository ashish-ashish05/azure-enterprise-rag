from enterprise_rag.config.settings import get_settings
from enterprise_rag.infrastructure.azure_openai.chat import (
    AzureOpenAIChatService,
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
    AzureSearchRetriever,
)
from enterprise_rag.rag.service import RAGService


def main() -> None:
    settings = get_settings()

    openai_client = AzureOpenAIClient(settings)

    embedding_service = AzureOpenAIEmbeddingService(
        client=openai_client,
        settings=settings,
    )

    chat_service = AzureOpenAIChatService(
        client=openai_client,
        settings=settings,
    )

    search_client = AzureSearchClient(settings)

    retriever = AzureSearchRetriever(search_client)

    rag_service = RAGService(
        embedding_service=embedding_service,
        retriever=retriever,
        chat_service=chat_service,
    )

    question = "What is the expense policy?"

    response = rag_service.answer(
        question,
        top_k=5,
    )

    print()
    print("QUESTION")
    print(response.question)

    print()
    print("ANSWER")
    print(response.answer)

    print()
    print("SOURCES")

    for source in response.sources:
        print(
            f"- {source.source} "
            f"(chunk {source.chunk_index})"
        )


if __name__ == "__main__":
    main()