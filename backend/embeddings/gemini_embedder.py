import google.generativeai as genai
from .base_embedder import BaseEmbedder
from utils.config import get_settings

settings = get_settings()

class GeminiEmbedder(BaseEmbedder):
    """Gemini embedding model"""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._dimension = 768

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",
            )
            embeddings.append(result["embedding"])
        return embeddings