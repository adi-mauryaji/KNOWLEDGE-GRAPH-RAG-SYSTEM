from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .citation import Citation

class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_lenght=500,
        description="User's question",
        examples=["What is the main contribution of the papers?"]
    )
    doc_ids: Optional[list[str]]= Field(
        default=None,
        description="Filter retrieval to specific document IDs.None=search all."
    )
    top_k: int =Field(
        default=5,
        ge=1,
        le=20,
        description="Number of chunks to retrieved"
    )
    vector_weight: float =Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Weight for vector retrieval (1 - this = graph weight)"
    )
    include_graph_context: bool = Field(
        default= True,
        description="Whether to use graph retrieval"
    )

class ChatResponsse(BaseModel):
    answer: str
    Citation: list[Citation]
    query_id: str
    processing_time_ms: int
    source_used: list[str]
    chunks_retrieved: int
    timestamp: datetime = Field(default_factory=datetime.now)
    retrievel_breakdown: Optional[dict] = Field(
        default = None,
        description="How many chunks from vector vs graph"
    )

class DocumentUploadResponse(BaseModel):
    doc_id: str
    filename: str
    status: str
    chunk_created: Optional[int] = None
    entities_extracted: Optional[int] = None
    message: str ="Document id being processed"

