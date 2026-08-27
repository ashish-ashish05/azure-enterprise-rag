from enterprise_rag.config.settings import get_settings
from enterprise_rag.infrastructure.azure_search.client import (
    AzureSearchClient,
)
from enterprise_rag.infrastructure.azure_search.search import (
    AzureSearchRetriever,
)


def main() -> None:
    settings = get_settings()

    search_client = AzureSearchClient(settings)

    retriever = AzureSearchRetriever(
        search_client
    )

    family_id = "ExpensePolicy"

    version = retriever.get_current_version(
        family_id
    )

    print(
        f"Document family: {family_id}"
    )

    print(
        f"Current version: {version}"
    )


if __name__ == "__main__":
    main()