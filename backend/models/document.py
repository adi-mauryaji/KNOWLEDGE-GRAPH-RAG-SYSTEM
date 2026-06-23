from pydantic import BaseModel, Field
from typing import Optional, Literal 
from datetime import datetime
import uuid

class DocumentMetadata(BaseModel):
    """YE STORE HOGA postgreSQL me YA KISI ME BHI JISME HUMEIN STORE KARNA HAI"""
    doc_id: str = Field(default_factory=Lambda:str(uuid.uuid4()))
    filename: str
    file_hash: str                          #MD5 for duplicate detection-> mtlb yeh humein ye batayega ki file duplicate hai ya nahi
    file_size_bytes: int
    total_pages: int
    total_chunks: int=0
    entities_extracted: int = 0
    relationships_extracted: int = 0
    status: Literal["processing", "completed", "failed"] = "processing"
    error_message: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None

class Chunk(BaseModel):
        """YE HOGA CHUNK KA MODEL JISME HUMEIN CHUNK KA DATA STORE KARNA HAI"""
        chunk_id: str = Field(default_factory=Lambda:str(uuid.uuid4()))
        doc_id: str
        chunk_index: int
        text: str
        page_number: int = 0
        chunk_index: int = 0
        chunk_total: int = 0
        filename: str
        token_count: Optional[int] = None

class RetievedChunk(BaseModel):
    """YE HOGA RETRIEVED CHUNK KA MODEL JISME HUMEIN RETRIEVED CHUNK KA DATA STORE KARNA HAI"""
    chunk_id: str
    doc_id: str
    text: str
    filename: str
    page_number: int = 0
    score: float
    final_score: float = 0.0
    source: Literal["vector", "graph", "hybrid"]= "vector"

    def to_context_line(self, index: int) -> str:
        """YE HOGA CONTEXT LINE KA FUNCTION JISME HUMEIN CONTEXT LINE KA DATA STORE KARNA HAI"""
        return (
             f"[{index}] Source: {self.filename} | Page: {self.page_number} | Score: {self.score:.3f}\n"
                f"{self.text}"
        )






