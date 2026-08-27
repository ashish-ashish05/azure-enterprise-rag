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


def build_rag_service() -> RAGService:
    """Build the application's RAG service."""

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

    return RAGService(
        embedding_service=embedding_service,
        retriever=retriever,
        chat_service=chat_service,
    )