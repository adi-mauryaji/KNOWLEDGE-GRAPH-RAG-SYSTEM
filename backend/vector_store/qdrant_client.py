from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@lru_cache
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)


async def init_qdrant() -> None:
    client = get_qdrant_client()
    size = settings.get_embedding_dimension()

    if client.collection_exists(settings.COLLECTION_NAME):
        existing = client.get_collection(settings.COLLECTION_NAME).config.params.vectors.size
        if existing != size:
            raise RuntimeError(
                f"Collection '{settings.COLLECTION_NAME}' ka dimension {existing} hai, "
                f"par current embedding model {size} deta hai. "
                "Collection delete karke documents dobara upload karo."
            )
        return

    client.create_collection(
        collection_name=settings.COLLECTION_NAME,
        vectors_config=VectorParams(size=size, distance=Distance.COSINE),
    )
    logger.info(f"Created Qdrant collection: {settings.COLLECTION_NAME} (dim={size})")
