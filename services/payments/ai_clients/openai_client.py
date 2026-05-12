from openai import AsyncOpenAI

from services.payments.ai_clients.base import AIClient

_DEFAULT_MODEL = "gpt-4o-mini"


class OpenAIAIClient(AIClient):
    def __init__(self, api_key: str, model: str = _DEFAULT_MODEL) -> None:
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def chat(self, system_prompt: str, user_content: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or ""
