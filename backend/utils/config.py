from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from functools import lru_cache
from typing import Literal

class Settings(BaseSettings):
    model_config=SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        case_sensitive = True,
        etra = "ignore"
    )


#LLM Provider(Suplier mafiq boleto)

LLM_PROVIDER: Literal["openai","gemini"]="openai"
OPEN_API_KEY: str = ""
OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
GEMINI_API_KEY: str = ""
GEMINI_CHAT_MODEL: str = "gemini-1.5-flash"


# Embeddings

EMBEDDING_PROVIDER: Literal["openai","bge","gemini"]="openai"
EMBEDDING_DIMENSION: int = 1536
BGE_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"


# Qdrant

QDRANT_HOST: str = "localhost"
QDRANT_PORT: int = 6333
COLLECTION_NAME: str = "documents"


# Neo4j

NEO4J_URI: str = "bolt://localhost:7687"
NEO4J_USER: str = "neo4j"
NEO4J_PASSWORD: str = "password"


# PostgreSQL (ye optional hai boleto)

POSTGRES_URL: str = "postgresql://user:password@localhost:5432/ragdb"
USE_POSTGRES: bool = False


# Chunking

CHUNK_SIZE: int = 512
CHUNK_OVERLAP: int = 50
CHUNKING_STRATEGY: Literal["recursive","sementic","sentence"]="recursive"


# Entity Extraction

EXTRACTION_MODEL: str = "gpt-4o-mini"
SKIP_EXTRACTION: bool = False


# Retrieval

DEFAULT_TOP_K: int = 5
MIN_RELEVANCE_SCORE: float = 0.5
VECTOR_WEIGHT: float = 0.7


# Upload

UPLOAD_DIR: str = "/app/uploads"
MAX_FILE_SIZE_MB: int = 50


# App

DEBUG: bool = False
LOG_LEVEL: str = "INFO"


def get_embedding_dimension(self) -> int:
    dimensions = {
        "openai": {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        },
        "bge": {
            "BAAI/bge-small-en-v1.5": 384,  
            "BAAI/bge-base-en-v1.5": 768,
            "BAAI/bge-large-en-v1.5": 1024,
        },
        "gemini": {
            "models/embedding-001": 768,
            "models/text-embedding-004": 768,
        }
    }
    provider_dims=dimensions.get(self.EMBEDDING_PROVIDER,{})
    model_key = (
        self.OPENAI_EMBEDDING_MODEL if self.EMBEDDING_PROVIDER=="openai"
        else self.BGE_MODEL_NAME if self.EMBEDDING_PROVIDER=="bge"
        else "models/embedding-001"
    )
    return provider_dims.get(model_key,self.EMBEDDING_DIMENSION)

@lru_cache
def get_settings() -> Settings:
    return Settings()