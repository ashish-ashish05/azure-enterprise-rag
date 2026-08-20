from enterprise_rag.config.settings import get_settings
from enterprise_rag.infrastructure.azure_search.client import (
    AzureSearchClient,
)
from enterprise_rag.infrastructure.azure_search.index import (
    AzureSearchIndexManager,
)


def main() -> None:
    settings = get_settings()

    
    vector_dimensions = 1536

    client = AzureSearchClient(settings)

    index_manager = AzureSearchIndexManager(
        client=client,
        settings=settings,
        vector_dimensions=vector_dimensions,
    )

    index = index_manager.create_or_update_index()

    print(f"Created/updated index: {index.name}")


if __name__ == "__main__":
    main()