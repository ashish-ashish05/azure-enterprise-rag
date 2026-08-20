from enterprise_rag.config.settings import Settings
from enterprise_rag.domain.models import DocumentChunk
from enterprise_rag.infrastructure.azure_openai.client import AzureOpenAIClient


class AzureOpenAIEmbeddingService:
    """Generate embeddings using Azure OpenAI."""

    def __init__(
        self,
        client: AzureOpenAIClient,
        settings: Settings,
    ) -> None:
        self._client = client.client
        self._deployment = settings.azure_openai_embedding_deployment

    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding for one piece of text."""

        if not text.strip():
            raise ValueError("Cannot generate an embedding for empty text")

        response = self._client.embeddings.create(
            model=self._deployment,
            input=text,
        )

        return response.data[0].embedding

    def embed_chunk(self, chunk: DocumentChunk) -> list[float]:
        """Generate an embedding for a document chunk."""

        return self.embed_text(chunk.content)

    def embed_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> list[list[float]]:
        """Generate embeddings for multiple document chunks."""

        if not chunks:
            return []

        response = self._client.embeddings.create(
            model=self._deployment,
            input=[chunk.content for chunk in chunks],
        )

        ordered_embeddings = sorted(
            response.data,
            key=lambda item: item.index,
        )

        return [
            item.embedding
            for item in ordered_embeddings
        ]