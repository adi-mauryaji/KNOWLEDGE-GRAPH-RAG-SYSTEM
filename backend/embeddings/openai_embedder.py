from openai import OpenAI
from .base_embedder import BaseEmbedder
from utils.config import get_settings
from utils.logger import get_logger
import time

logger = get_logger(__name__)
settings = get_settings()

class OpenAIEmbedder(BaseEmbedder):
    def __init__(self, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model
        self._dimension = 1536 if "small" in model else 3072  

    @property
    def dimension(self) -> int:
        return self._dimension
    
    def embed_text(self, text: str) -> list[float]:
        """ Single text embedding """
        return self.embed_batch([text])[0]
    
    def embed_batch(self, texts: list[str], max_retries: int = 3) -> list[list[float]]:
        """ Batch embedding - more effecient + cheaper """
        texts = [t.replace("\n", " ").strip() for t in texts]
        texts = [t[:8000] for t in texts] 

        for attempt in range(max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts,
                    encoding_format="float"
                )
                return [item.embedding for item in response.data]
            
            except Exception as e:
                if attempt == max_retries -1:
                    raise
                wait_time = 2 ** attempt 
                logger.warning(f"Embeddding attempt {attempt+1} failed. Waiting {wait_time}s...")
                time.sleep(wait_time)
