from enterprise_rag.config.settings import Settings
from enterprise_rag.infrastructure.azure_openai.client import (
    AzureOpenAIClient,
)


class AzureOpenAIChatService:
    """Generate grounded responses using Azure OpenAI."""

    def __init__(
        self,
        client: AzureOpenAIClient,
        settings: Settings,
    ) -> None:
        self._client = client.client
        self._deployment = settings.azure_openai_chat_deployment

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Generate a response from Azure OpenAI."""

        response = self._client.chat.completions.create(
            model=self._deployment,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        message = response.choices[0].message.content

        if not message:
            raise RuntimeError(
                "Azure OpenAI returned an empty response"
            )

        return message.strip()