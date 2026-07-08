from .base_embedder import BaseEmbedder
from .openai_embedder import OPENAIEmbedder
from .bge_embedder import BGEEmbedder
from .gemini_embedder import GeminiEmbedder
from utils.config import get_settings, Settings

def get_embedder(settings: Settings = None) -> BaseEmbedder:
    """ Factory - choose embedder from config"""
    settings = settings or get_settings()

    providers = {
        "openai": lambda: OpenAIEmbedder(settings.OPENAI_EMBEDDING_MODEL),
        "bge": lambda: BGEEmbedder(settings.BGE_MODEL_NAME),
        "gemini": lambda: GeminiEmbedder(),
    }

    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider not in providers:
        raise ValueError(f"Unknown embedding provider: {provider}")

    return providers[provider]()