from enterprise_rag.config.settings import get_settings
from enterprise_rag.infrastructure.azure_openai.client import (
    AzureOpenAIClient,
)
from enterprise_rag.infrastructure.azure_openai.embeddings import (
    AzureOpenAIEmbeddingService,
)
from enterprise_rag.infrastructure.azure_openai.chat import (
    AzureOpenAIChatService,
)
from enterprise_rag.infrastructure.azure_search.client import (
    AzureSearchClient,
)
from enterprise_rag.infrastructure.azure_search.search import (
    AzureSearchRetriever,
)
from enterprise_rag.rag.service import RAGService


TEST_CASES = [
    {
        "question": "What are the employee benefits?",
        "family": "Benefits",
    },
    {
        "question": "What is the leave policy?",
        "family": "LeavePolicy",
    },
    {
        "question": "What are the password requirements?",
        "family": "PasswordPolicy",
    },
    {
        "question": "What is the travel policy?",
        "family": "TravelPolicy",
    },
    {
        "question": "What are the VPN requirements?",
        "family": "VPNGuide",
    },
    {
        "question": "What does the NDA require?",
        "family": "NDA",
    },
    {
        "question": "What are the vendor contract terms?",
        "family": "VendorContract",
    },
    {
        "question": "What are the current pricing rules?",
        "family": "Pricing2026",
    },
    {
        "question": "What is the expense policy?",
        "family": "ExpensePolicy",
    },
    {
        "question": "What are the discounts?",
        "family": "Discounts",
    },
]


def build_rag_service() -> RAGService:
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

    return RAGService(
        embedding_service=embedding_service,
        retriever=retriever,
        chat_service=chat_service,
    )


def main() -> None:
    rag_service = build_rag_service()

    passed = 0
    failed = 0

    print()
    print("=" * 70)
    print("MULTI-DOCUMENT RAG TEST")
    print("=" * 70)

    for case in TEST_CASES:
        question = case["question"]
        expected_family = case["family"]

        print()
        print("-" * 70)
        print(f"QUESTION: {question}")
        print(f"EXPECTED FAMILY: {expected_family}")
        print("-" * 70)

        try:
            response = rag_service.answer(
                question,
                document_family_id=expected_family,
            )

            families = {
                result.document_family_id
                for result in response.retrieved_results
            }

            versions = {
                result.document_version
                for result in response.retrieved_results
                if result.document_version is not None
            }

            sources = {
                result.source
                for result in response.retrieved_results
            }

            family_match = (
                expected_family in families
            )

            has_results = bool(
                response.retrieved_results
            )

            if family_match and has_results:
                print("RESULT: PASS")
                passed += 1
            else:
                print("RESULT: FAIL")
                failed += 1

            print(
                f"Retrieved results: "
                f"{len(response.retrieved_results)}"
            )

            print(
                f"Families: "
                f"{sorted(families)}"
            )

            print(
                f"Versions: "
                f"{sorted(versions)}"
            )

            print(
                f"Sources: "
                f"{sorted(sources)}"
            )

            print()
            print("ANSWER:")
            print(response.answer)

        except Exception as exc:
            failed += 1

            print("RESULT: ERROR")
            print(
                f"Reason: {exc}"
            )

    print()
    print("=" * 70)
    print("MULTI-DOCUMENT RAG SUMMARY")
    print("=" * 70)
    print(
        f"Passed: {passed}/{len(TEST_CASES)}"
    )
    print(
        f"Failed: {failed}/{len(TEST_CASES)}"
    )

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()