from abc import ABC, abstractmethod


class AIClient(ABC):
    """Абстрактный AI-клиент: chat(system, user) -> raw response text."""

    @abstractmethod
    async def chat(self, system_prompt: str, user_content: str) -> str: ...
