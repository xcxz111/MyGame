from services.payments.ai_clients.base import AIClient
from services.payments.ai_clients.claude_client import ClaudeAIClient
from services.payments.ai_clients.groq_client import GroqAIClient
from services.payments.ai_clients.openai_client import OpenAIAIClient
from settings import Settings


def create_ai_client(settings: Settings) -> AIClient:
    """Возвращает AI-клиента согласно `settings.ai_provider`."""
    provider = (settings.ai_provider or "").lower()
    api_key = settings.ai_api_key

    if provider == "groq":
        return GroqAIClient(api_key=api_key)
    if provider == "openai":
        return OpenAIAIClient(api_key=api_key)
    if provider == "claude":
        return ClaudeAIClient(api_key=api_key)

    raise ValueError(f"Unknown AI provider: {settings.ai_provider!r}")
