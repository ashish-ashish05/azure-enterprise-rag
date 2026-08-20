from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

from enterprise_rag.config.settings import Settings


class AzureOpenAIClient:
    """Client for Microsoft Foundry's OpenAI-compatible API."""

    def __init__(self, settings: Settings) -> None:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default",
        )

        endpoint = settings.azure_openai_endpoint.rstrip("/")

        self._client = OpenAI(
            base_url=f"{endpoint}/openai/v1/",
            api_key=token_provider,
        )

    @property
    def client(self) -> OpenAI:
        """Return the configured OpenAI client."""

        return self._client