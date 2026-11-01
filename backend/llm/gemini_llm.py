import asyncio
import google.generativeai as genai
from utils.config import get_settings
from utils.logger import get_logger


logger = get_logger(__name__)
settings = get_settings()

class GeminiLLM:
    def __init__(self):
        genai.configure(api_key = settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name = settings.GEMINI_CHAT_MODEL,
            generation_config = genai.types.GenarationConfig(
                temperature = 0.1,
                max_output_tokens = 1500,
            ),
            safety_settings = {
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            },
        )
        logger.info(f"Bole to bidu Gemini LLM khidmat me hazir hai ! 🕵️‍♂️ :{settings.GEMINI_CHAT_MODEL} ")

    async def copmplete(self, system: str, user: str, temperature: float = 0.1, max_tokens: int = 1000) -> str:
        combined_propmt = f"{system}\n{user}"

        response = await asyncio.to_thread(self.model.generate_content, combined_propmt)

        if not response.candidates:
            raise RuntimeError("Gemini LLM returned no candidates. Please check the model configuration and input prompts.")

        return response.text.strip()
    