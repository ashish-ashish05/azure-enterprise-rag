from enterprise_rag.infrastructure.azure_openai.embeddings import (
    AzureOpenAIEmbeddingService,
)
from enterprise_rag.infrastructure.azure_openai.chat import (
    AzureOpenAIChatService,
)
from enterprise_rag.infrastructure.azure_search.search import (
    AzureSearchRetriever,
)
from enterprise_rag.rag.models import (
    RAGResponse,
    SourceCitation,
)
from enterprise_rag.rag.prompt import (
    SYSTEM_PROMPT,
    build_user_prompt,
)


class RAGService:
    """Orchestrate retrieval and grounded generation."""

    def __init__(
        self,
        embedding_service: AzureOpenAIEmbeddingService,
        retriever: AzureSearchRetriever,
        chat_service: AzureOpenAIChatService,
    ) -> None:
        self._embedding_service = embedding_service
        self._retriever = retriever
        self._chat_service = chat_service

    def answer(
        self,
        question: str,
        *,
        top_k: int = 5,
        document_family_id: str | None = None,
    ) -> RAGResponse:
        """Answer a question using retrieved enterprise context."""

        if not question.strip():
            raise ValueError(
                "Question cannot be empty"
            )

        query_embedding = (
            self._embedding_service.embed_text(question)
        )

        current_version = None

        if document_family_id is not None:
            current_version = (
            self._retriever.get_current_version(
                document_family_id
            )
        )

        results = self._retriever.hybrid_search(
            query=question,
            query_embedding=query_embedding,
            top_k=top_k,
            document_family_id=document_family_id,
            document_version=current_version,
        )

        if not results:
            return RAGResponse(
                question=question,
                answer=(
                    "I don't have enough information in "
                    "the provided documents to answer "
                    "that question."
                ),
                sources=[],
                retrieved_results=[],
            )

        context = self._build_context(results)

        user_prompt = build_user_prompt(
            question=question,
            context=context,
        )

        answer = self._chat_service.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        sources = [
            SourceCitation(
                source=result.source,
                chunk_id=result.id,
                chunk_index=result.chunk_index,
                page=result.page,
            )
            for result in results
        ]

        return RAGResponse(
            question=question,
            answer=answer,
            sources=sources,
            retrieved_results=results,
        )

    @staticmethod
    def _build_context(results) -> str:
        sections: list[str] = []

        for index, result in enumerate(results, start=1):
            sections.append(
                f"""
SOURCE {index}
Document: {result.source}
Chunk: {result.chunk_index}
Page: {result.page}

Content:
{result.content}
""".strip()
            )

        return "\n\n".join(sections)