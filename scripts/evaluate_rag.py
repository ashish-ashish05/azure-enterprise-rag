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

    openai_client = AzureOpenAIClient(
        settings
    )

    embedding_service = (
        AzureOpenAIEmbeddingService(
            client=openai_client,
            settings=settings,
        )
    )

    chat_service = AzureOpenAIChatService(
        client=openai_client,
        settings=settings,
    )

    search_client = AzureSearchClient(
        settings
    )

    retriever = AzureSearchRetriever(
        search_client
    )

    rag_service = RAGService(
        embedding_service=embedding_service,
        retriever=retriever,
        chat_service=chat_service,
    )

    evaluation_cases = [
        {
            "question": "What is the expense policy?",
            "document_family_id": "ExpensePolicy",
            "expected_version": "5.1",
        },
        {
            "question": "What are the receipt requirements?",
            "document_family_id": "ExpensePolicy",
            "expected_version": "5.1",
        },
        {
            "question": (
                "How long do I have to submit an expense?"
            ),
            "document_family_id": "ExpensePolicy",
            "expected_version": "5.1",
        },
    ]

    passed = 0

    for case in evaluation_cases:
        print()
        print("=" * 60)
        print(
            f"Question: {case['question']}"
        )
        print("=" * 60)

        response = rag_service.answer(
            case["question"],
            document_family_id=(
                case["document_family_id"]
            ),
        )

        versions = {
            source.document_version
            for source in response.sources
        }

        families = {
            source.document_family_id
            for source in response.sources
        }

        if (
            case["expected_version"] in versions
            and case["document_family_id"] in families
            and response.sources
        ):
            print("PASS")
            passed += 1
        else:
            print("FAIL")

        print(
            f"Retrieved sources: "
            f"{len(response.sources)}"
        )

        print(
            f"Versions: {sorted(versions)}"
        )

        print(
            f"Families: {sorted(families)}"
        )

    print()
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(
        f"Passed: {passed}/{len(evaluation_cases)}"
    )

    if passed != len(evaluation_cases):
        raise SystemExit(1)


if __name__ == "__main__":
    main()