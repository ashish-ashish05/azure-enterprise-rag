from enterprise_rag.config.settings import get_settings
from enterprise_rag.infrastructure.azure_openai.client import AzureOpenAIClient
from enterprise_rag.infrastructure.azure_openai.embeddings import (
    AzureOpenAIEmbeddingService,
)


def main() -> None:
    settings = get_settings()

    client = AzureOpenAIClient(settings)

    embedding_service = AzureOpenAIEmbeddingService(
        client=client,
        settings=settings,
    )

    vector = embedding_service.embed_text(
        "Enterprise RAG test document."
    )

    print(f"Embedding dimensions: {len(vector)}")
    print(f"First five values: {vector[:5]}")


if __name__ == "__main__":
    main()