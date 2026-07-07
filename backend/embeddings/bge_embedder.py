from sentence_transformers import SentenceTransformer
from .base_embedder import BaseEmbedder

class BGEEmbedder(BaseEmbedder):
    """ Locate krne ke liye BGE embeddings ko sentence transformers ke help se"""
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()
        print(f"💚 BGE model loaded: {model_name} (dim={self._dimension})")

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> list[float]:
        return self.model.encode(text, normalise_embedding=True).tolist()
     
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """ BGE works best with instructions prefix for retrieval"""
        instruction = "Represent this sentence for searching relevant passages: "
        prefixed = [instruction + t for t in texts]

        embeddings  = self.model.encode(
            prefixed,
            normalised_embeddings=True,
            batch_size=32,
            show_progress_bar=len(texts) > 100
        )
        return embeddings.tolist()