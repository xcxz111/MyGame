import anthropic

from services.payments.ai_clients.base import AIClient

_DEFAULT_MODEL = "claude-haiku-4-5-20251001"


class ClaudeAIClient(AIClient):
    def __init__(self, api_key: str, model: str = _DEFAULT_MODEL) -> None:
        if not api_key:
            raise ValueError("Anthropic API key is required")
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def chat(self, system_prompt: str, user_content: str) -> str:
        message = await self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        return message.content[0].text if message.content else ""
