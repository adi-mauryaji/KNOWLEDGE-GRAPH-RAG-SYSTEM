from openai import AsyncOpenAI
from utils.config import get_settings

settings = get_settings()

class OpenAILLM:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_CHAT_MODEL

    async def complete(self, system: str, user: str, temperature: float = 0.1, max_tokens: int = 1000) -> str:
        response = await self.client.chat.completions.create(
            model = self.model,
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature = temperature,
            max_tokens = max_tokens
        )

        return response.choices[0].message.content.strip()