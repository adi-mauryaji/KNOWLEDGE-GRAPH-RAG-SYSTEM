from abc import ABC, abstractmethod
import numpy as np

class BaseEmbedder(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """" Embed single text """
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """ Embed batch of texts """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """ Vector dimension """
        pass

    def cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """ Compute cosine similarity between two vectors """
        a = np.array(vec1)
        b = np.array(vec2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))